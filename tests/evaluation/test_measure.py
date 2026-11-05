"""Verifica a métrica multirrelevante e a separação de falhas técnicas."""

import runpy
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
