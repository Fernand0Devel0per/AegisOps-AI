"""Verifica a métrica multirrelevante e a separação de falhas técnicas."""

import json
import runpy
import subprocess
import sys
from pathlib import Path

MEASURE = runpy.run_path(
    str(Path(__file__).resolve().parents[2] / "datasets/evaluation/measure.py")
)


def test_recall_counts_distinct_relevant_not_hit_rate() -> None:
    recall = MEASURE["recall_at"]
    assert recall(["A", "A", "X", "B"], {"A", "B"}, 3) == 0.5
    assert recall(["A", "A", "X", "B"], {"A", "B"}, 5) == 1.0
    assert recall([], {"A"}, 5) == 0.0


def test_technical_failure_is_not_absence_abstention() -> None:
    metric = MEASURE["metric"]
    base = {
        "absence": True,
        "ids": [],
        "unjudged": 0,
        "negative": 0,
        "recall_3": 0,
        "recall_5": 0,
        "rr": 0,
    }
    result = metric([{**base, "error": "CorpusError"}, {**base, "error": None}])
    assert result["technical_failures"] == 1
    assert result["absence_denominator"] == 1
    assert result["absence_abstentions"] == 1


def test_evaluate_query_tracks_first_relevant_and_judgment_categories() -> None:
    evaluate_query = MEASURE["evaluate_query"]
    query = {
        "id": "Q-example",
        "group": "incident",
        "language": "en",
        "absence": False,
        "relevant": [{"id": "A"}, {"id": "B"}],
        "negative": [{"id": "N"}],
        "unjudged": ["U"],
    }
    outcome = {"ids": ["N", "U", "B", "A"], "error": None}

    result = evaluate_query(query, outcome)

    assert result["first"] == 3
    assert result["rr"] == 1 / 3
    assert result["recall_3"] == 0.5
    assert result["recall_5"] == 1.0
    assert result["negative"] == 1
    assert result["unjudged"] == 1


def test_worker_reports_invalid_query_separately_from_abstention(
    tmp_path: Path,
) -> None:
    worker = (
        Path(__file__).resolve().parents[2] / "datasets/evaluation/retrieval_worker.py"
    )
    process = subprocess.run(
        [sys.executable, str(worker)],
        input=json.dumps(["unmatcheduniqueterm98765", ""]),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    abstention, invalid_query = [
        json.loads(line) for line in process.stdout.splitlines()
    ]
    assert abstention == {"ids": [], "error": None}
    assert invalid_query == {"ids": [], "error": "InvalidQuery"}
