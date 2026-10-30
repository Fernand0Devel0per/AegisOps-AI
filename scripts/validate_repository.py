#!/usr/bin/env python3
"""Validate the repository's documentary contracts; no application runtime."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import unquote

try:
    import yaml
except ImportError:
    sys.exit("PyYAML ausente; consulte doc/standards/validation.md.")

ROOT = Path(__file__).resolve().parents[1]
PLAN_HASH = "9a22c8fff517e28556e7b32cb1bd35ffe5b7306f48ad90f1f74644d22c5cc078"
STATES = {
    "story": {"backlog", "ready", "in_progress", "blocked", "in_review", "done"},
    "epic": {"backlog", "ready", "in_progress", "blocked", "in_review", "done"},
    "spec": {"draft", "ready", "superseded"},
    "activity": {"pending", "in_progress", "blocked", "in_review", "completed", "cancelled"},
    "handoff": {"completed", "partial", "blocked"},
}
REQUIRED = {
    "story": "id title epic description objective context priority status dependencies scope acceptance_criteria technical_constraints deliverables validation references definition_of_done",
    "epic": "id title source_phase objective status priority dependencies scope exit_criteria stories references",
    "spec": "id story_id title status problem_statement proposed_solution architecture interfaces data_contracts dependencies security_considerations observability error_handling implementation_steps test_strategy acceptance_mapping open_questions related_adrs",
    "activity": "id story_id spec_id title objective status agent inputs expected_outputs constraints execution_steps validation dependencies handoff_required",
    "handoff": "id activity_id story_id spec_id source_agent target_agent status summary completed_work changed_files decisions_made validation known_issues pending_work next_steps related_adrs",
}
LIST_FIELDS = {
    "story": "dependencies acceptance_criteria technical_constraints deliverables references definition_of_done",
    "epic": "dependencies scope exit_criteria stories references",
    "spec": "interfaces data_contracts dependencies security_considerations observability error_handling implementation_steps test_strategy acceptance_mapping open_questions related_adrs",
    "activity": "inputs expected_outputs constraints execution_steps dependencies",
    "handoff": "completed_work changed_files decisions_made known_issues pending_work next_steps related_adrs",
}
PREFIX = {"story": "STORY", "epic": "EPIC", "spec": "SPEC", "activity": "ACT", "handoff": "HANDOFF"}
FOLDERS = {"story": "roadmap/stories", "epic": "roadmap/epics", "spec": "agents/specs", "activity": "agents/activities", "handoff": "agents/handoffs"}


class Invalid(ValueError):
    """An invalid documentary contract."""


def require(condition, message):
    if not condition:
        raise Invalid(message)


class UniqueLoader(yaml.SafeLoader):
    """Safe YAML that also rejects silent key replacement."""


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        require(isinstance(key, str), "Chave YAML deve ser texto.")
        require(key not in result, f"Chave YAML duplicada: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def parse_yaml(source):
    require(not any(isinstance(t, (yaml.tokens.AliasToken, yaml.tokens.AnchorToken)) for t in yaml.scan(source)), "Aliases/anchors YAML não são permitidos.")
    data = yaml.load(source, Loader=UniqueLoader)
    require(isinstance(data, dict), "Documento YAML deve ser um mapa.")
    return data


def list_at(data, key, label):
    require(isinstance(data.get(key), list), f"{label}: {key} deve ser lista.")


def fields_at(data, fields, label):
    require(isinstance(data, dict), f"{label}: esperado mapa.")
    for field in fields.split():
        require(field in data, f"{label}: campo ausente {field}.")


def contract(kind, data, label, template=False):
    fields_at(data, REQUIRED[kind], label)
    require(re.fullmatch(PREFIX[kind] + r"-\d{3,}", str(data["id"])), f"{label}: ID inválido.")
    require(data["status"] in STATES[kind], f"{label}: estado inválido.")
    for key in LIST_FIELDS[kind].split():
        list_at(data, key, label)
    if kind in {"story", "epic"}:
        require(data["priority"] in {"high", "medium", "low"}, f"{label}: prioridade inválida.")
    if kind == "story":
        fields_at(data["scope"], "included excluded", label)
        for key in ("included", "excluded"):
            list_at(data["scope"], key, label)
        fields_at(data["validation"], "automated_tests manual_checks", label)
        for key in ("automated_tests", "manual_checks"):
            list_at(data["validation"], key, label)
        ids = []
        for ac in data["acceptance_criteria"]:
            fields_at(ac, "id criterion", label)
            require(ac["criterion"], f"{label}: critério vazio.")
            ids.append(ac["id"])
        require(len(ids) == len(set(ids)), f"{label}: critérios repetidos.")
        if not template:
            require(ids and data["scope"]["included"] and data["definition_of_done"], f"{label}: escopo/aceite/DoD vazio.")
    if kind == "spec":
        fields_at(data["architecture"], "components interactions data_flow", label)
        for key in ("components", "interactions", "data_flow"):
            list_at(data["architecture"], key, label)
    if kind == "activity":
        fields_at(data["agent"], "role responsibility", label)
        fields_at(data["validation"], "commands expected_results", label)
        for key in ("commands", "expected_results"):
            list_at(data["validation"], key, label)
        require(data["handoff_required"] is True, f"{label}: handoff obrigatório.")
    if kind == "handoff":
        fields_at(data["validation"], "executed passed failed not_executed", label)
        for key in ("executed", "passed", "failed", "not_executed"):
            list_at(data["validation"], key, label)
        if data["status"] == "completed" and not template:
            require(data["validation"]["executed"] and data["validation"]["passed"], f"{label}: sem evidência de validação.")
            require(not data["validation"]["failed"], f"{label}: validação falha não resolvida.")


def ac_mapping(story, spec):
    expected = {ac["id"] for ac in story["acceptance_criteria"]}
    actual = []
    for item in spec["acceptance_mapping"]:
        fields_at(item, "criterion_id validation evidence", spec["id"])
        require(item["validation"] and item["evidence"], f"{spec['id']}: mapeamento incompleto.")
        actual.append(item["criterion_id"])
    require(expected == set(actual) and len(actual) == len(set(actual)), f"{spec['id']}: AC sem mapeamento ou referência de AC inválida.")


def same_catalog(entry, entity, keys):
    for key in keys:
        require(entry.get(key) == entity.get(key), f"{entity['id']}: índice divergente em {key}.")


def acyclic(entities):
    active, visited = set(), set()

    def visit(identifier):
        require(identifier in entities, f"Dependência inexistente: {identifier}")
        require(identifier not in active, f"Ciclo de dependências em {identifier}")
        if identifier in visited:
            return
        active.add(identifier)
        for dependency in entities[identifier]["dependencies"]:
            visit(dependency)
        active.remove(identifier)
        visited.add(identifier)

    for identifier in entities:
        visit(identifier)


def existing(path, label):
    require(isinstance(path, str) and path, f"{label}: caminho inválido.")
    target = (ROOT / path).resolve()
    require(target.is_relative_to(ROOT), f"{label}: caminho fora do repositório.")
    require(target.exists(), f"{label}: referência inexistente {path}")


def self_test():
    cases = [
        lambda: parse_yaml("id: A\nid: B\n"),
        lambda: acyclic({"A": {"dependencies": ["B"]}, "B": {"dependencies": ["A"]}}),
        lambda: same_catalog({"status": "done"}, {"id": "X", "status": "ready"}, ["status"]),
        lambda: ac_mapping({"acceptance_criteria": [{"id": "AC-01"}]}, {"id": "SPEC-X", "acceptance_mapping": []}),
    ]
    for case in cases:
        try:
            case()
        except Invalid:
            continue
        raise Invalid("Self-test aceitou entrada inválida.")
    require(parse_yaml("id: A\nitems: []\n") == {"id": "A", "items": []}, "Self-test rejeitou entrada válida.")
    print("PASS self-test: 4 entradas inválidas rejeitadas e 1 válida aceita.")


def validate():
    documents = {}
    for folder in ("roadmap", "agents"):
        for path in sorted((ROOT / folder).rglob("*.yaml")):
            try:
                documents[path.relative_to(ROOT).as_posix()] = parse_yaml(path.read_text(encoding="utf-8"))
            except (Invalid, yaml.YAMLError) as exc:
                raise Invalid(f"{path.relative_to(ROOT)}: {exc}") from exc
    entities = {kind: {} for kind in FOLDERS}
    for kind, folder in FOLDERS.items():
        for path, data in documents.items():
            if path.startswith(folder + "/"):
                contract(kind, data, path)
                require(Path(path).stem == data["id"], f"{path}: nome não corresponde ao ID.")
                require(data["id"] not in entities[kind], f"{path}: ID repetido.")
                entities[kind][data["id"]] = data
    for kind, path in {
        "story": "roadmap/templates/story.template.yaml",
        "spec": "agents/templates/spec.template.yaml",
        "activity": "agents/templates/activity.template.yaml",
        "handoff": "agents/templates/handoff.template.yaml",
    }.items():
        require(path in documents, f"Template ausente: {path}")
        contract(kind, documents[path], path, template=True)
    index = documents["roadmap/index.yaml"]
    fields_at(index, "schema_version updated_at source current_phase next_story next_activity epics stories milestones", "index")
    existing(index["source"], "index.source")
    for kind, catalog in (("story", "stories"), ("epic", "epics")):
        ids = [item["id"] for item in index[catalog]]
        require(len(ids) == len(set(ids)) and set(ids) == set(entities[kind]), f"index: catálogo {catalog} incompleto ou repetido.")
        for entry in index[catalog]:
            require(entry["path"] == f"{FOLDERS[kind]}/{entry['id']}.yaml", f"index: path inválido para {entry['id']}")
            same_catalog(entry, entities[kind][entry["id"]], ["title", "status", "priority", "dependencies"] + (["epic"] if kind == "story" else []))
        acyclic(entities[kind])
    acyclic(entities["activity"])
    for kind in entities:
        for identifier, data in entities[kind].items():
            for field in ("references", "related_adrs", "inputs"):
                for path in data.get(field, []):
                    existing(path, f"{identifier}.{field}")
    for epic in entities["epic"].values():
        expected = {s["id"] for s in entities["story"].values() if s["epic"] == epic["id"]}
        require(set(epic["stories"]) == expected, f"{epic['id']}: lista de histórias divergente.")
    for story in entities["story"].values():
        require(story["epic"] in entities["epic"], f"{story['id']}: épico inexistente.")
        if story["status"] in {"ready", "in_progress", "in_review", "done"}:
            require(all(entities["story"][dep]["status"] == "done" for dep in story["dependencies"]), f"{story['id']}: dependência não concluída.")
            require(not story.get("refinement_required", False), f"{story['id']}: falta refinamento.")
            specs = {s["id"] for s in entities["spec"].values() if s["story_id"] == story["id"] and s["status"] == "ready"}
            require(specs, f"{story['id']}: sem spec pronta.")
            require(any(a["story_id"] == story["id"] and a["spec_id"] in specs and a["status"] != "cancelled" for a in entities["activity"].values()), f"{story['id']}: sem atividade preparada.")
        if story["status"] == "done":
            require(any(h["story_id"] == story["id"] and h["status"] == "completed" for h in entities["handoff"].values()), f"{story['id']}: sem handoff concluído.")
            for path in story["deliverables"]:
                existing(path, story["id"])
    for spec in entities["spec"].values():
        require(spec["story_id"] in entities["story"], f"{spec['id']}: história inexistente.")
        if spec["status"] == "ready":
            ac_mapping(entities["story"][spec["story_id"]], spec)
        for path in spec["dependencies"]:
            existing(path, spec["id"])
    for activity in entities["activity"].values():
        require(activity["story_id"] in entities["story"] and activity["spec_id"] in entities["spec"], f"{activity['id']}: vínculo inexistente.")
        require(entities["spec"][activity["spec_id"]]["story_id"] == activity["story_id"], f"{activity['id']}: spec de outra história.")
        if activity["status"] == "completed":
            require(any(h["activity_id"] == activity["id"] and h["status"] == "completed" for h in entities["handoff"].values()), f"{activity['id']}: sem handoff concluído.")
            for path in activity["expected_outputs"]:
                existing(path, activity["id"])
    for handoff in entities["handoff"].values():
        require(handoff["activity_id"] in entities["activity"], f"{handoff['id']}: atividade inexistente.")
        activity = entities["activity"][handoff["activity_id"]]
        same_catalog(handoff, activity, ["story_id", "spec_id"])
        for change in handoff["changed_files"]:
            fields_at(change, "path reason", handoff["id"])
            require(change["reason"], f"{handoff['id']}: alteração sem motivo.")
            existing(change["path"], handoff["id"])
        for result in handoff["validation"]["passed"]:
            fields_at(result, "check evidence", handoff["id"])
            existing(result["evidence"], handoff["id"])
    require(index["next_story"] in entities["story"] and index["next_activity"] in entities["activity"], "index: próximo contrato inexistente.")
    require(entities["activity"][index["next_activity"]]["story_id"] == index["next_story"], "index: próxima atividade de outra história.")
    for milestone in index["milestones"]:
        require(all(s in entities["story"] for s in milestone["required_stories"]), "Marco com história inexistente.")
    md_files = sorted(ROOT.rglob("*.md"))
    for path in md_files:
        if ".git" in path.relative_to(ROOT).parts:
            continue
        text = path.read_text(encoding="utf-8")
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", link):
                continue
            target = unquote(link.strip("<> ").split("#", 1)[0])
            if target:
                resolved = (path.parent / target).resolve()
                require(resolved.is_relative_to(ROOT) and resolved.exists(), f"{path.relative_to(ROOT)}: link quebrado {link}")
    require(hashlib.sha256((ROOT / "AegisOps_AI_Plano_do_Zero.md").read_bytes()).hexdigest() == PLAN_HASH, "Plano original foi alterado.")
    print(f"PASS: {len(documents)} YAML, {len(entities['epic'])} épicos, {len(entities['story'])} histórias, {len(md_files)} Markdown.")
    print("PASS: templates, campos, estados, catálogo, dependências, vínculos, ACs, evidências, links locais e hash do plano.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Check validator rejection of representative invalid inputs.")
    args = parser.parse_args()
    try:
        self_test() if args.self_test else validate()
    except (Invalid, yaml.YAMLError, KeyError, TypeError, OSError) as exc:
        sys.exit(f"FAIL: {exc}")
