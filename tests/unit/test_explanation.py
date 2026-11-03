"""Avaliação controlada da política de frases anterior à integração de LLM."""

import json
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from aegisops.contracts import Incident, validate_incident
from aegisops.explanation import (
    InvalidExplanation,
    canonical_sentences,
    verify_selection,
)
from aegisops.triage import TriageResult, triage_incident


@pytest.fixture
def context() -> tuple[dict[str, Any], Incident, TriageResult]:
    data = json.loads(Path("datasets/incidents/inc-001-latencia.json").read_text())
    return data, validate_incident(data), triage_incident(data)


def test_sentences_are_grounded_in_observations(
    context: tuple[dict[str, Any], Incident, TriageResult],
) -> None:
    _, incident, result = context
    sentences = canonical_sentences(result)
    assert sentences[0].text == "Severidade máxima media, determinada pelo sinal 2."
    assert sentences[0].signal_id == "SIG-001-02"
    assert sentences[0].evidence_id == "EVD-001-02"
    assert "http_request_duration_p95 = 900 ms" in sentences[2].text
    assert "2026-10-01T10:05:00+00:00" in sentences[2].text
    selected = verify_selection(
        {"sentence_ids": ["S-002", "S-MAX"]}, sentences, incident, result
    )
    assert [sentence.id for sentence in selected] == ["S-002", "S-MAX"]
    assert all("causa" not in sentence.text.lower() for sentence in selected)


@pytest.mark.parametrize(
    "response",
    [
        None,
        "não é JSON",
        {},
        {"sentence_ids": []},
        {"sentence_ids": [1]},
        {"sentence_ids": ["S-MAX", "S-MAX"]},
        {"sentence_ids": ["S-999", "S-MAX"]},
        {"sentence_ids": ["S-001"]},
        {"sentence_ids": ["S-MAX"], "text": "causa raiz"},
    ],
)
def test_rejects_malformed_or_unsupported_selection(
    context: tuple[dict[str, Any], Incident, TriageResult], response: object
) -> None:
    _, incident, result = context
    with pytest.raises(InvalidExplanation):
        verify_selection(response, canonical_sentences(result), incident, result)


@pytest.mark.parametrize("evidence_id", ["EVD-INEXISTENTE", "EVD-001-01"])
def test_rejects_nonexistent_or_mismatched_evidence(
    context: tuple[dict[str, Any], Incident, TriageResult], evidence_id: str
) -> None:
    _, incident, result = context
    sentences = canonical_sentences(result)
    tampered = (replace(sentences[0], evidence_id=evidence_id), *sentences[1:])
    with pytest.raises(InvalidExplanation):
        verify_selection({"sentence_ids": ["S-MAX"]}, tampered, incident, result)


def test_no_canonical_explanation_for_insufficient_data(
    context: tuple[dict[str, Any], Incident, TriageResult],
) -> None:
    data, _, _ = context
    data["signals"] = []
    data["evidence"] = []
    result = triage_incident(data)
    assert result.state == "insuficiente"
    with pytest.raises(ValueError):
        canonical_sentences(result)


@pytest.mark.parametrize(
    ("name", "severity", "expected"),
    [
        (
            "inc-001-latencia.json",
            "media",
            ("http_request_duration_p95", 900, "ms", "media", "EVD-001-02"),
        ),
        (
            "inc-002-erros-5xx.json",
            "alta",
            ("http_5xx_rate", 20.0, "percent", "alta", "EVD-002-02"),
        ),
        (
            "inc-003-saturacao.json",
            "alta",
            ("memory_utilization", 97, "percent", "alta", "EVD-003-02"),
        ),
    ],
)
def test_maximum_sentence_matches_known_fixture(
    name: str, severity: str, expected: tuple[str, int | float, str, str, str]
) -> None:
    data = json.loads((Path("datasets/incidents") / name).read_text(encoding="utf-8"))
    incident = validate_incident(data)
    result = triage_incident(data)
    sentences = canonical_sentences(result)
    metric, value, unit, level, evidence_id = expected
    assert result.severity == severity
    assert (
        sentences[0].text == f"Severidade máxima {severity}, determinada pelo sinal 2."
    )
    assert sentences[0].evidence_id == evidence_id
    assert f"{metric} = {value} {unit}" in sentences[2].text
    assert f"nível {level}" in sentences[2].text
    assert verify_selection(
        {"sentence_ids": ["S-MAX", "S-002"]}, sentences, incident, result
    )


def test_rejects_forged_claim_and_missing_evidence_in_source(
    context: tuple[dict[str, Any], Incident, TriageResult],
) -> None:
    _, incident, result = context
    sentences = canonical_sentences(result)
    forged = (replace(sentences[0], text="Causa raiz confirmada."), *sentences[1:])
    with pytest.raises(InvalidExplanation):
        verify_selection({"sentence_ids": ["S-MAX"]}, forged, incident, result)
    missing = replace(
        incident, evidence=tuple(e for e in incident.evidence if e.id != "EVD-001-02")
    )
    with pytest.raises(InvalidExplanation):
        verify_selection({"sentence_ids": ["S-MAX"]}, sentences, missing, result)


def test_rejects_observation_that_does_not_match_source(
    context: tuple[dict[str, Any], Incident, TriageResult],
) -> None:
    _, incident, result = context
    signals = list(incident.signals)
    signals[1] = replace(signals[1], value=123)
    altered = replace(incident, signals=tuple(signals))
    with pytest.raises(InvalidExplanation):
        verify_selection(
            {"sentence_ids": ["S-MAX"]}, canonical_sentences(result), altered, result
        )


@pytest.mark.parametrize(
    "alteration",
    ["incident", "missing_signal", "evidence_link", "metric", "unit", "period"],
)
def test_rejects_unrelated_or_inconsistent_source(
    context: tuple[dict[str, Any], Incident, TriageResult], alteration: str
) -> None:
    _, incident, result = context
    signals = list(incident.signals)
    evidence = list(incident.evidence)
    if alteration == "incident":
        incident = replace(incident, id="outro-incidente")
    elif alteration == "missing_signal":
        incident = replace(incident, signals=tuple(signals[:1] + signals[2:]))
    elif alteration == "evidence_link":
        evidence[1] = replace(evidence[1], signal_id=signals[0].id)
        incident = replace(incident, evidence=tuple(evidence))
    else:
        signal = signals[1]
        if alteration == "metric":
            signal = replace(signal, metric="outra_metrica")
        elif alteration == "unit":
            signal = replace(signal, unit="outra_unidade")
        else:
            signal = replace(
                signal,
                period=replace(
                    signal.period, start=signal.period.start + timedelta(seconds=1)
                ),
            )
        signals[1] = signal
        incident = replace(incident, signals=tuple(signals))
    with pytest.raises(InvalidExplanation, match="Referência inválida"):
        verify_selection(
            {"sentence_ids": ["S-MAX"]}, canonical_sentences(result), incident, result
        )
