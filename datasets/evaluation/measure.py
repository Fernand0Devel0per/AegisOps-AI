"""Avaliação exploratória congelada; executa o pacote instalado em processo isolado."""

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUERY_HASH = "cfbb5f70cb669cacff739c4317c3fce7c5818386267dbe5f35d93888d2612f8b"
MANIFEST_HASH = "63fadc27c030b0647db84d63fa1fc7b93b31af069638af2560e7fdecffa34b30"
QUERY_PATH = ROOT / "datasets/evaluation/queries.yaml"
MANIFEST_PATH = ROOT / "datasets/runbooks/manifest.yaml"
VALIDATOR_PATH = ROOT / "datasets/evaluation/validate.py"
WORKER_PATH = ROOT / "datasets/evaluation/retrieval_worker.py"
INSTALLED_PYTHON = ROOT / ".venv/bin/python"


def validate_frozen_hash(path: Path, expected_hash: str) -> None:
    actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual_hash != expected_hash:
        raise ValueError(f"Arquivo congelado alterado: {path.name}")


def validate_frozen() -> dict:
    # PyYAML é uma dependência do ambiente documental, não do pacote de aplicação.
    import yaml

    validate_frozen_hash(QUERY_PATH, QUERY_HASH)
    validate_frozen_hash(MANIFEST_PATH, MANIFEST_HASH)
    subprocess.run(["python3", str(VALIDATOR_PATH)], check=True, capture_output=True)

    dataset = yaml.safe_load(QUERY_PATH.read_text())
    if dataset["split"] != "nao_atribuido":
        raise ValueError("Partição inesperada")
    return dataset


def recall_at(ids: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    returned_relevant = set(ids[:k]) & relevant
    return len(returned_relevant) / len(relevant)


def metric(rows: list[dict]) -> dict:
    successful_rows = [row for row in rows if not row["error"]]
    positive_rows = [row for row in successful_rows if not row["absence"]]
    absence_rows = [row for row in successful_rows if row["absence"]]
    technical_failures = sum(bool(row["error"]) for row in rows)

    result = {
        "queries": len(rows),
        "technical_failures": technical_failures,
        "positive_denominator": len(positive_rows),
        "absence_denominator": len(absence_rows),
        "unjudged_at_5": sum(row["unjudged"] for row in successful_rows),
        "negative_at_5": sum(row["negative"] for row in successful_rows),
    }
    for limit in (3, 5):
        recall_field = f"recall_{limit}"
        result[f"recall_sum_{limit}"] = sum(row[recall_field] for row in positive_rows)

    result["reciprocal_rank_sum_5"] = sum(row["rr"] for row in positive_rows)
    result["positive_abstentions"] = sum(not row["ids"] for row in positive_rows)
    result["absence_returns"] = sum(bool(row["ids"]) for row in absence_rows)
    result["absence_abstentions"] = sum(not row["ids"] for row in absence_rows)
    return result


def run_retrieval(queries: list[dict]) -> list[dict]:
    query_texts = [query["text"] for query in queries]
    command = [str(INSTALLED_PYTHON), str(WORKER_PATH)]
    process = subprocess.run(
        command,
        input=json.dumps(query_texts),
        text=True,
        capture_output=True,
        check=True,
        cwd="/tmp",
    )
    outcomes = [json.loads(line) for line in process.stdout.splitlines()]
    if len(outcomes) != len(queries):
        raise ValueError("Quantidade de respostas incompatível")
    return outcomes


def first_relevant_position(ids: list[str], relevant_ids: set[str]) -> int | None:
    positions = [
        position
        for position, identifier in enumerate(ids, 1)
        if identifier in relevant_ids
    ]
    return min(positions) if positions else None


def evaluate_query(query: dict, outcome: dict) -> dict:
    returned_ids = outcome["ids"]
    relevant_ids = {item["id"] for item in query["relevant"]}
    negative_ids = {item["id"] for item in query["negative"]}
    unjudged_ids = set(query["unjudged"])
    first_relevant = first_relevant_position(returned_ids, relevant_ids)
    reciprocal_rank = 1 / first_relevant if first_relevant else 0
    returned_id_set = set(returned_ids)

    return {
        "id": query["id"],
        "group": query["group"],
        "language": query["language"],
        "absence": query["absence"],
        "ids": returned_ids,
        "error": outcome["error"],
        "first": first_relevant,
        "rr": reciprocal_rank,
        "recall_3": recall_at(returned_ids, relevant_ids, 3),
        "recall_5": recall_at(returned_ids, relevant_ids, 5),
        "unjudged": len(returned_id_set & unjudged_ids),
        "negative": len(returned_id_set & negative_ids),
    }


def evaluate_queries(queries: list[dict], outcomes: list[dict]) -> list[dict]:
    return [
        evaluate_query(query, outcome)
        for query, outcome in zip(queries, outcomes, strict=True)
    ]


def summarize_results(rows: list[dict]) -> dict:
    group_names = sorted({row["group"] for row in rows})
    groups = {
        group: metric([row for row in rows if row["group"] == group])
        for group in group_names
    }
    languages = {
        language: metric([row for row in rows if row["language"] == language])
        for language in ("pt-BR", "en")
    }
    return {
        "overall": metric(rows),
        "languages": languages,
        "groups": groups,
        "queries": rows,
    }


def main() -> None:
    dataset = validate_frozen()
    queries = dataset["queries"]
    outcomes = run_retrieval(queries)
    rows = evaluate_queries(queries, outcomes)
    results = summarize_results(rows)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
