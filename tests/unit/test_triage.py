"""Exemplos sintéticos e fronteiras públicas da triagem local."""

import copy
import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest

from aegisops.contracts import InvalidIncident
from aegisops.triage import triage_incident

DATASETS = Path(__file__).resolve().parents[2] / "datasets" / "incidents"


def fixture(name: str) -> dict[str, Any]:
    return json.loads((DATASETS / name).read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def one_signal(metric: str, value: float, unit: str) -> dict[str, Any]:
    data = fixture("inc-001-latencia.json")
    signal = data["signals"][0]
    signal.update(id="signal", metric=metric, value=value, unit=unit)
    if metric == "http_5xx_rate":
        # Denominador grande representa exatamente as casas decimais dos testes.
        signal.update(numerator=round(value * 10_000_000), denominator=1_000_000_000)
    data["signals"] = [signal]
    data["evidence"] = [{"id": "evidence", "signal_id": "signal", "summary": "dado"}]
    return data


@pytest.mark.parametrize(
    ("name", "severity", "levels"),
    [
        ("inc-001-latencia.json", "media", ["normal", "media", "normal"]),
        ("inc-002-erros-5xx.json", "alta", ["normal", "alta", "normal"]),
        ("inc-003-saturacao.json", "alta", ["normal", "alta", "media"]),
    ],
)
def test_fixtures_are_reproducible_with_resolvable_evidence(
    name: str, severity: str, levels: list[str]
) -> None:
    data = fixture(name)
    result = triage_incident(data)
    assert result == triage_incident(copy.deepcopy(data))
    assert result.state == "classificado"
    assert result.severity == severity == data["expected"]["severity"]
    assert [item.level for item in result.observations] == levels
    assert [item.evidence_id for item in result.observations] == data["expected"][
        "evidence_ids"
    ]
    evidence = {item["id"]: item for item in data["evidence"]}
    for observation, signal in zip(result.observations, data["signals"], strict=True):
        assert (
            evidence[observation.evidence_id]["signal_id"]
            == observation.signal_id
            == signal["id"]
        )
        assert (observation.metric, observation.value, observation.unit) == (
            signal["metric"],
            signal["value"],
            signal["unit"],
        )
        assert observation.period.start.isoformat() == signal["period"][
            "start"
        ].replace("Z", "+00:00")
        assert observation.period.end.isoformat() == signal["period"]["end"].replace(
            "Z", "+00:00"
        )
    assert result.explanation_state == "nao_solicitada"
    assert "causa" not in str(asdict(result)).lower()
    assert "hipotese" not in asdict(result)


@pytest.mark.parametrize(
    ("metric", "unit", "medium", "high"),
    [
        ("http_request_duration_p95", "ms", 500, 1500),
        ("http_5xx_rate", "percent", 5, 10),
        ("cpu_utilization", "percent", 95, 99),
        ("memory_utilization", "percent", 90, 95),
    ],
)
def test_threshold_boundaries(metric: str, unit: str, medium: int, high: int) -> None:
    for value, level in [
        (medium - 0.0000001, "normal"),
        (float(medium), "media"),
        (medium + 0.0000001, "media"),
        (high - 0.0000001, "media"),
        (float(high), "alta"),
        (high + 0.0000001, "alta"),
    ]:
        result = triage_incident(one_signal(metric, value, unit))
        assert result.severity == result.observations[0].level == level


def test_multiple_evidence_selects_lexicographic_minimum_regardless_of_order() -> None:
    data = fixture("inc-002-erros-5xx.json")
    data["evidence"].extend(
        [
            {
                "id": "A-EVIDENCE",
                "signal_id": data["signals"][1]["id"],
                "summary": "outro",
            },
            {
                "id": "Z-EVIDENCE",
                "signal_id": data["signals"][1]["id"],
                "summary": "outro",
            },
        ]
    )
    result = triage_incident(data)
    data["evidence"].reverse()
    assert triage_incident(data) == result
    assert result.observations[1].evidence_id == "A-EVIDENCE"
    assert result.severity == "alta"


def test_partial_and_complete_metric_limitations() -> None:
    data = one_signal("memory_utilization", 60, "percent")
    result = triage_incident(data)
    assert result.severity == "normal"
    assert result.limitations == (
        "Métrica ausente: http_request_duration_p95",
        "Métrica ausente: http_5xx_rate",
        "Métrica ausente: cpu_utilization",
        "Classificação parcial não demonstra ausência de degradação.",
    )
    other = fixture("inc-001-latencia.json")
    data["signals"].extend(other["signals"])
    data["evidence"].extend(other["evidence"])
    cpu = one_signal("cpu_utilization", 99, "percent")
    cpu["signals"][0]["id"] = "cpu"
    cpu["evidence"][0].update(id="cpu-evidence", signal_id="cpu")
    data["signals"].extend(cpu["signals"])
    data["evidence"].extend(cpu["evidence"])
    result = triage_incident(data)
    assert result.severity == "alta"
    assert result.limitations == ()


def test_empty_is_insufficient_but_invalid_input_takes_precedence() -> None:
    data = fixture("inc-001-latencia.json")
    data["signals"] = []
    data["evidence"] = []
    result = triage_incident(data)
    assert result.state == "insuficiente"
    assert result.severity is None
    assert result.observations == ()
    assert result.limitations == ("Ausência de sinais.",)
    assert result.explanation_state == "nao_solicitada"
    data["service"] = " "
    with pytest.raises(InvalidIncident) as error:
        triage_incident(data)
    assert error.value.state == "entrada_invalida"
    assert any(item.path == "service" for item in error.value.errors)
    assert not hasattr(error.value, "severity")
    assert not hasattr(error.value, "observations")
    assert not hasattr(error.value, "explanation_state")


@pytest.mark.parametrize(
    ("mutation", "path"),
    [
        (lambda d: d["signals"][0].update(unit="percent"), "signals[0].unit"),
        (lambda d: d["signals"][0].update(metric="unknown"), "signals[0].metric"),
        (lambda d: d["signals"][0].update(value=math.nan), "signals[0].value"),
        (lambda d: d["signals"][0].update(value=-1), "signals[0].value"),
        (
            lambda d: d["signals"][0]["period"].update(
                start="2026-10-01T09:59:00Z", end="2026-10-01T10:04:00Z"
            ),
            "signals[0].period",
        ),
        (
            lambda d: d["signals"][0]["period"].update(end="2026-10-01T10:04:00Z"),
            "signals[0].period",
        ),
        (lambda d: d["window"].update(end="2026-10-01T10:11:00Z"), "window"),
        (
            lambda d: d["evidence"][0].update(signal_id="missing"),
            "evidence[0].signal_id",
        ),
        (lambda d: d["evidence"].pop(0), "signals[0].id"),
        (lambda d: d["evidence"][0].update(id=d["id"]), "evidence[0].id"),
    ],
)
def test_invalid_entries_propagate_field_details(mutation: Any, path: str) -> None:
    data = fixture("inc-001-latencia.json")
    mutation(data)
    with pytest.raises(InvalidIncident) as error:
        triage_incident(data)
    assert error.value.state == "entrada_invalida"
    assert any(item.path == path for item in error.value.errors)


@pytest.mark.parametrize(
    ("field", "value", "path"),
    [
        ("denominator", 0, "signals[0].denominator"),
        ("numerator", 1001, "signals[0].numerator"),
        ("value", 9, "signals[0].value"),
    ],
)
def test_inconsistent_5xx_is_invalid(field: str, value: int, path: str) -> None:
    data = fixture("inc-002-erros-5xx.json")
    data["signals"][0][field] = value
    with pytest.raises(InvalidIncident) as error:
        triage_incident(data)
    assert any(item.path == path for item in error.value.errors)


def test_overlapping_periods_within_window_are_independent() -> None:
    data = fixture("inc-003-saturacao.json")
    data["signals"][1]["period"] = {
        "start": "2026-10-01T10:02:00Z",
        "end": "2026-10-01T10:07:00Z",
    }
    result = triage_incident(data)
    assert result.severity == "alta"
    assert [item.level for item in result.observations] == ["normal", "alta", "media"]


@pytest.mark.parametrize(
    ("metric", "unit"),
    [
        ("http_request_duration_p95", "ms"),
        ("http_5xx_rate", "percent"),
        ("cpu_utilization", "percent"),
        ("memory_utilization", "percent"),
    ],
)
def test_each_metric_rejects_incompatible_unit(metric: str, unit: str) -> None:
    data = one_signal(metric, 0, unit)
    data["signals"][0]["unit"] = "percent" if unit == "ms" else "ms"
    with pytest.raises(InvalidIncident) as error:
        triage_incident(data)
    assert any(item.path == "signals[0].unit" for item in error.value.errors)


def test_5xx_tolerance_preserves_input_value_for_classification() -> None:
    data = one_signal("http_5xx_rate", 5.0, "percent")
    data["signals"][0].update(numerator=5, denominator=100, value=4.999999)
    assert triage_incident(data).severity == "normal"
    data["signals"][0]["value"] = 4.9999989
    with pytest.raises(InvalidIncident) as error:
        triage_incident(data)
    assert any(item.code == "taxa_inconsistente" for item in error.value.errors)


def test_end_beyond_incident_window_is_invalid() -> None:
    data = one_signal("memory_utilization", 95, "percent")
    data["signals"][0]["period"] = {
        "start": "2026-10-01T10:05:01Z",
        "end": "2026-10-01T10:10:01Z",
    }
    with pytest.raises(InvalidIncident) as error:
        triage_incident(data)
    assert any(item.code == "periodo_fora_janela" for item in error.value.errors)


def test_result_is_read_only_and_does_not_modify_input() -> None:
    data = fixture("inc-003-saturacao.json")
    original = copy.deepcopy(data)
    result = triage_incident(data)
    assert data == original
    with pytest.raises(AttributeError):
        result.observations[0].value = 42  # type: ignore[misc]
