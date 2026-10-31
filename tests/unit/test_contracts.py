import copy
import json
from pathlib import Path
from typing import Any

import pytest

from aegisops.contracts import InvalidIncident, validate_incident

FIXTURES = Path(__file__).resolve().parents[2] / "datasets" / "incidents"


def fixture(name: str = "inc-001-latencia.json") -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def errors(data: object) -> set[tuple[str, str]]:
    with pytest.raises(InvalidIncident) as exc:
        validate_incident(data)
    assert exc.value.state == "entrada_invalida"
    return {(item.path, item.code) for item in exc.value.errors}


@pytest.mark.parametrize(
    "name",
    ["inc-001-latencia.json", "inc-002-erros-5xx.json", "inc-003-saturacao.json"],
)
def test_fixtures_accepted_without_migration(name: str) -> None:
    data = fixture(name)
    incident = validate_incident(data)
    assert incident.id == data["id"]
    assert len(incident.signals) == len(data["signals"])
    assert {e.signal_id for e in incident.evidence} == {s.id for s in incident.signals}
    assert incident.window.start.utcoffset().total_seconds() == 0  # type: ignore[union-attr]


def test_empty_and_overlapping_periods_with_multiple_evidence() -> None:
    data = fixture()
    data["signals"] = []
    data["evidence"] = []
    assert validate_incident(data).signals == ()
    data = fixture()
    data["signals"][1]["period"] = copy.deepcopy(data["signals"][0]["period"])
    data["evidence"].append(
        {"id": "extra", "signal_id": data["signals"][0]["id"], "summary": "outra"}
    )
    assert len(validate_incident(data).evidence) == 4


@pytest.mark.parametrize("value", [None, True, "1", float("nan"), float("inf"), -1])
def test_invalid_latency(value: object) -> None:
    data = fixture()
    data["signals"][0]["value"] = value
    assert any(path == "signals[0].value" for path, _ in errors(data))


@pytest.mark.parametrize("value", [0, 100])
def test_percent_boundaries(value: int) -> None:
    data = fixture("inc-003-saturacao.json")
    data["signals"][0]["value"] = value
    assert validate_incident(data).signals[0].value == value


@pytest.mark.parametrize("value", [-0.01, 100.01])
def test_percent_outside_range(value: float) -> None:
    data = fixture("inc-003-saturacao.json")
    data["signals"][0]["value"] = value
    assert ("signals[0].value", "valor_fora_intervalo") in errors(data)


@pytest.mark.parametrize(
    ("value", "valid"),
    [(0.500001, True), (0.50000101, False), (0.499999, True), (0.49999899, False)],
)
def test_rate_absolute_tolerance(value: float, valid: bool) -> None:
    data = fixture()
    data["signals"][2]["value"] = value
    if valid:
        validate_incident(data)
    else:
        assert ("signals[2].value", "taxa_inconsistente") in errors(data)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("denominator", 0),
        ("denominator", True),
        ("denominator", 1.0),
        ("numerator", -1),
        ("numerator", 1001),
        ("numerator", False),
        ("numerator", None),
    ],
)
def test_invalid_rate_counts(field: str, value: object) -> None:
    data = fixture()
    data["signals"][2][field] = value
    assert (f"signals[2].{field}", "contagem_invalida") in errors(data)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("metric", "unknown", "metrica_desconhecida"),
        ("unit", "percent", "unidade_incompativel"),
        ("source", "  ", "texto_obrigatorio"),
        ("aggregation", None, "texto_obrigatorio"),
        ("id", "", "texto_obrigatorio"),
    ],
)
def test_signal_fields(field: str, value: object, code: str) -> None:
    data = fixture()
    data["signals"][0][field] = value
    assert (f"signals[0].{field}", code) in errors(data)


@pytest.mark.parametrize(
    ("target", "field", "value", "path", "code"),
    [
        ("window", "end", "2026-10-01T10:09:59Z", "window", "duracao_invalida"),
        (
            "window",
            "start",
            "2026-10-01T10:00:00",
            "window.start",
            "timestamp_utc_invalido",
        ),
        (
            "window",
            "start",
            "2026-10-01T10:00:00+01:00",
            "window.start",
            "timestamp_utc_invalido",
        ),
        ("window", "start", "not-a-date", "window.start", "timestamp_utc_invalido"),
        (
            "period",
            "end",
            "2026-10-01T10:04:59Z",
            "signals[0].period",
            "duracao_invalida",
        ),
        (
            "period",
            "start",
            "2026-10-01T09:59:00Z",
            "signals[0].period",
            "duracao_invalida",
        ),
    ],
)
def test_invalid_time(
    target: str, field: str, value: str, path: str, code: str
) -> None:
    data = fixture()
    entry = data["window"] if target == "window" else data["signals"][0]["period"]
    entry[field] = value
    assert (path, code) in errors(data)


def test_period_outside_window_and_utc_offset() -> None:
    data = fixture()
    data["signals"][0]["period"] = {
        "start": "2026-10-01T09:59:00+00:00",
        "end": "2026-10-01T10:04:00+00:00",
    }
    assert ("signals[0].period", "periodo_fora_janela") in errors(data)
    data["signals"][0]["period"] = {
        "start": "2026-10-01T10:00:00+00:00",
        "end": "2026-10-01T10:05:00+00:00",
    }
    validate_incident(data)


def test_ids_and_references() -> None:
    data = fixture()
    data["signals"][1]["id"] = data["id"]
    data["evidence"][0]["id"] = data["signals"][0]["id"]
    data["evidence"][2]["signal_id"] = "missing"
    result = errors(data)
    assert ("signals[1].id", "id_duplicado") in result
    assert ("evidence[0].id", "id_duplicado") in result
    assert ("evidence[2].signal_id", "sinal_inexistente") in result
    assert ("signals[2].id", "sinal_sem_evidencia") in result


def test_missing_evidence_and_orphan_with_no_signals() -> None:
    data = fixture()
    data["evidence"] = []
    assert ("signals[0].id", "sinal_sem_evidencia") in errors(data)
    data = fixture()
    data["signals"] = []
    assert ("evidence[0].signal_id", "sinal_inexistente") in errors(data)


def test_inconsistent_empty_input_has_deterministic_errors_without_payload() -> None:
    data = fixture()
    data["signals"] = []
    data["evidence"] = []
    data["service"] = " "
    data["window"]["start"] = "secret invalid value"
    with pytest.raises(InvalidIncident) as first:
        validate_incident(data)
    with pytest.raises(InvalidIncident) as second:
        validate_incident(data)
    assert first.value.errors == second.value.errors
    assert {e.path for e in first.value.errors} == {"service", "window.start"}
    assert "secret" not in str(first.value) + repr(first.value.errors)


@pytest.mark.parametrize(
    "data", [None, [], "incident", {"signals": {}, "evidence": None}]
)
def test_malformed_top_level(data: object) -> None:
    assert errors(data)


def test_required_fields_and_synthetic_flag() -> None:
    data = fixture()
    del data["id"]
    data["synthetic"] = 1
    data["environment"] = " "
    data["evidence"][0]["summary"] = ""
    result = errors(data)
    assert ("id", "texto_obrigatorio") in result
    assert ("synthetic", "sintetico_obrigatorio") in result
    assert ("environment", "texto_obrigatorio") in result
    assert ("evidence[0].summary", "texto_obrigatorio") in result


def test_large_counts_and_decimal_rate() -> None:
    data = fixture()
    data["signals"][2]["numerator"] = 10**5000
    data["signals"][2]["denominator"] = 2 * 10**5000
    data["signals"][2]["value"] = 50
    assert validate_incident(data).signals[2].value == 50
    data["signals"][2]["value"] = 50.000002
    assert ("signals[2].value", "taxa_inconsistente") in errors(data)


def test_models_are_immutable_and_fixture_metadata_is_not_trusted() -> None:
    from dataclasses import FrozenInstanceError

    data = fixture()
    data["expected"] = {"severity": "alta", "evidence_ids": ["nonexistent"]}
    incident = validate_incident(data)
    assert not hasattr(incident, "expected")
    with pytest.raises(FrozenInstanceError):
        incident.id = "another"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        incident.signals[0].value = 999  # type: ignore[misc]


def test_duplicate_evidence_id_and_invalid_evidence_shape() -> None:
    data = fixture()
    data["evidence"][1]["id"] = data["evidence"][0]["id"]
    data["evidence"][2] = None
    result = errors(data)
    assert ("evidence[1].id", "id_duplicado") in result
    assert ("evidence[2]", "objeto_esperado") in result


def test_rate_validation_does_not_depend_on_decimal_context() -> None:
    from decimal import Inexact, localcontext

    data = fixture()
    data["signals"][2]["value"] = 0.500001
    with localcontext() as context:
        context.prec = 2
        context.traps[Inexact] = True
        validate_incident(data)
