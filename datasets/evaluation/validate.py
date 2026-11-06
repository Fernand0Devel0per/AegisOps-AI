"""Validate the frozen corpus and reviewed judgments without running retrieval."""

from __future__ import annotations

import copy
import hashlib
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
TRANSLATION_PAIRS = (
    ("Q01", "Q02"),
    ("Q03", "Q04"),
    ("Q05", "Q07"),
    ("Q06", "Q08"),
    ("Q09", "Q10"),
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_unit_files(unit: dict) -> str:
    unit_path = ROOT / unit["path"]
    license_path = ROOT / unit["license_path"]
    require(
        unit_path.is_file() and license_path.is_file(), "Arquivo ou licença inexistente"
    )
    require(
        digest(unit_path.read_bytes()) == unit["sha256"], "Hash da unidade divergente"
    )
    require(
        digest(license_path.read_bytes()) == unit["license_sha256"],
        "Hash da licença divergente",
    )
    return unit_path.read_text(encoding="utf-8")


def validate_unit_provenance(unit: dict, text: str) -> None:
    provenance_fields = (
        unit["id"],
        unit["version"],
        unit["source_url"],
        unit["source_sha256"],
    )
    has_provenance = all(str(field) in text for field in provenance_fields)
    require(has_provenance, "Proveniência incompleta")

    has_sections = all(str(section) in text for section in unit["sections"])
    require(has_sections, "Seção ausente na unidade")

    required_markers = ("## Excerpt", "Modification:", "Attribution:")
    has_metadata = all(marker in text for marker in required_markers)
    require(has_metadata, "Metadados incompletos")


def validate_units(manifest: dict) -> list[str]:
    units = manifest["units"]
    unit_ids = [unit["id"] for unit in units]
    require(
        len(unit_ids) == len(set(unit_ids)) and bool(unit_ids),
        "IDs de unidades duplicados ou ausentes",
    )
    unit_paths = [unit["path"] for unit in units]
    require(len(unit_paths) == len(set(unit_paths)), "Caminhos de unidades duplicados")
    require(manifest["status"] == "revisado_po", "Corpus sem revisão registrada")

    for unit in units:
        accepted = unit["review"] == "aceito_po_resposta_conjunta_2026-11-04"
        require(accepted, "Unidade sem aceite registrado")
        unit_text = validate_unit_files(unit)
        validate_unit_provenance(unit, unit_text)
    return unit_ids


def validate_corpus_version(manifest: dict, dataset: dict) -> str:
    units_by_path = sorted(manifest["units"], key=lambda unit: unit["path"])
    canonical_lines = (f"{unit['sha256']}  {unit['path']}\n" for unit in units_by_path)
    canonical_corpus = "".join(canonical_lines)
    corpus_hash = digest(canonical_corpus.encode("utf-8"))

    hashes_match = manifest["corpus_sha256"] == corpus_hash == dataset["corpus_sha256"]
    require(hashes_match, "Hash do corpus divergente")
    require(
        manifest["corpus_version"] == dataset["corpus_version"],
        "Versão do corpus divergente",
    )
    return corpus_hash


def validate_judgments(query: dict, unit_ids: list[str]) -> None:
    relevant_ids = [item["id"] for item in query["relevant"]]
    negative_ids = [item["id"] for item in query["negative"]]
    unjudged_ids = query["unjudged"]
    judged_and_unjudged = relevant_ids + negative_ids + unjudged_ids
    ids_are_unique = len(judged_and_unjudged) == len(set(judged_and_unjudged))
    ids_cover_corpus = set(judged_and_unjudged) == set(unit_ids)
    require(
        ids_are_unique and ids_cover_corpus,
        "Julgamentos duplicados ou referências inválidas",
    )

    judgments = query["relevant"] + query["negative"]
    require(
        all(item.get("rationale") for item in judgments), "Julgamento sem justificativa"
    )
    require(
        query["absence"] == (not relevant_ids), "Ausência incompatível com relevantes"
    )
    require(
        not query["absence"] or not unjudged_ids,
        "Ausência exige julgamento de todas as unidades",
    )


def validate_review(query: dict) -> None:
    review = query["review"]
    require(review["status"] == "aceito_po", "Revisão humana não aceita")
    has_reviewer_and_date = review["po"] == "Product Owner" and bool(
        review.get("po_date")
    )
    require(has_reviewer_and_date, "Revisor ou data ausente")


def validate_query_context(query: dict, manifest: dict, corpus_hash: str) -> None:
    valid_language_and_text = query["language"] in ("pt-BR", "en") and bool(
        query["text"]
    )
    require(valid_language_and_text, "Idioma ou texto inválido")
    correct_corpus = (
        query["corpus_version"] == manifest["corpus_version"]
        and query["corpus_sha256"] == corpus_hash
    )
    require(correct_corpus, "Consulta de outra versão")
    if query["fixture"] is not None:
        fixture_path = ROOT / query["fixture"]
        require(fixture_path.is_file(), "Fixture inexistente")


def validate_translation_pairs(queries: list[dict]) -> None:
    judgment_fields = ("relevant", "negative", "unjudged", "absence")
    for first_id, second_id in TRANSLATION_PAIRS:
        pair = [query for query in queries if query["id"] in (first_id, second_id)]
        same_group = len(pair) == 2 and pair[0]["group"] == pair[1]["group"]
        require(same_group, "Grupo de tradução inconsistente")
        languages = {query["language"] for query in pair}
        require(languages == {"pt-BR", "en"}, "Par de idiomas inconsistente")
        same_judgments = all(
            pair[0][field] == pair[1][field] for field in judgment_fields
        )
        require(same_judgments, "Rótulos de tradução divergentes")


def validate_queries(
    dataset: dict, manifest: dict, corpus_hash: str, unit_ids: list[str]
) -> None:
    query_ids = set()
    groups_by_incident: dict = {}
    for query in dataset["queries"]:
        require(query["id"] not in query_ids, "Consulta duplicada")
        query_ids.add(query["id"])
        validate_query_context(query, manifest, corpus_hash)
        if query["fixture"] is not None:
            groups_by_incident.setdefault(query["incident_id"], set()).add(
                query["group"]
            )
        validate_judgments(query, unit_ids)
        validate_review(query)

    incident_groups_are_unique = all(
        len(groups) == 1 for groups in groups_by_incident.values()
    )
    require(incident_groups_are_unique, "Variantes do incidente em grupos distintos")
    validate_translation_pairs(dataset["queries"])
    require(dataset["split"] == "nao_atribuido", "Partição não revisada")


def check(manifest: dict, dataset: dict) -> None:
    unit_ids = validate_units(manifest)
    corpus_hash = validate_corpus_version(manifest, dataset)
    validate_queries(dataset, manifest, corpus_hash, unit_ids)


def assert_dataset_mutation_rejected(manifest: dict, dataset: dict, change) -> None:
    candidate = copy.deepcopy(dataset)
    change(candidate)
    try:
        check(manifest, candidate)
    except ValueError, KeyError:
        return
    raise AssertionError("Entrada inválida aceita")


def add_duplicate_query(dataset: dict) -> None:
    first_query = dataset["queries"][0]
    dataset["queries"].append(copy.deepcopy(first_query))


def add_relevant_as_negative(dataset: dict) -> None:
    first_query = dataset["queries"][0]
    first_relevant = first_query["relevant"][0]
    first_query["negative"].append(copy.deepcopy(first_relevant))


def leave_absence_unjudged(dataset: dict) -> None:
    absence_query = dataset["queries"][8]
    removed_negative = absence_query["negative"].pop()
    absence_query.update(absence=True, unjudged=[removed_negative["id"]])


def assert_unreviewed_unit_rejected(manifest: dict, dataset: dict) -> None:
    candidate_manifest = copy.deepcopy(manifest)
    candidate_manifest["units"][0]["review"] = "pendente_po"
    try:
        check(candidate_manifest, dataset)
    except ValueError:
        return
    raise AssertionError("Unidade sem aceite foi aceita")


def add_unknown_unjudged_id(dataset: dict) -> None:
    dataset["queries"][0]["unjudged"].append("ID-INEXISTENTE")


def change_incident_group(dataset: dict) -> None:
    dataset["queries"][6]["group"] = "outro-grupo"


def change_corpus_hash(dataset: dict) -> None:
    dataset["corpus_sha256"] = "0" * 64


def remove_fixture(dataset: dict) -> None:
    dataset["queries"][0]["fixture"] = "datasets/incidents/inexistente.json"


def remove_review_acceptance(dataset: dict) -> None:
    dataset["queries"][0]["review"]["status"] = "proposta_pendente_po"


def remove_review_date(dataset: dict) -> None:
    dataset["queries"][0]["review"]["po_date"] = ""


def self_test(manifest: dict, dataset: dict) -> None:
    mutations = (
        add_duplicate_query,
        add_relevant_as_negative,
        add_unknown_unjudged_id,
        leave_absence_unjudged,
        change_incident_group,
        change_corpus_hash,
        remove_fixture,
        remove_review_acceptance,
        remove_review_date,
    )
    for mutation in mutations:
        assert_dataset_mutation_rejected(manifest, dataset, mutation)
    assert_unreviewed_unit_rejected(manifest, dataset)
    print("PASS: 10 mutações inválidas rejeitadas")


def main() -> None:
    manifest_path = ROOT / "datasets/runbooks/manifest.yaml"
    dataset_path = ROOT / "datasets/evaluation/queries.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    dataset = yaml.safe_load(dataset_path.read_text())
    check(manifest, dataset)
    print(
        f"PASS: {len(manifest['units'])} unidades, {len(dataset['queries'])} consultas, hashes e grupos"
    )
    if sys.argv[1:] == ["--self-test"]:
        self_test(manifest, dataset)
    elif sys.argv[1:]:
        raise SystemExit("Uso: validate.py [--self-test]")


if __name__ == "__main__":
    main()
