"""Compara a rota existente com protótipo isolado usando seletores simulados."""

import asyncio
import json
import runpy
from collections.abc import Awaitable, Callable
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from aegisops import api, colibri
from aegisops.api import app
from aegisops.explanation import Sentence, canonical_sentences
from aegisops.triage import TriageResult

experiment: Any = runpy.run_path("scripts/workflow_050.py")["experiment"]


def fixture() -> dict[str, Any]:
    return json.loads(Path("datasets/incidents/inc-001-latencia.json").read_text())  # type: ignore[no-any-return]


def input_for(scenario: str) -> dict[str, Any]:
    data = fixture()
    if scenario == "invalid":
        data["signals"][0]["unit"] = "invalid"
    elif scenario == "insufficient":
        data["signals"] = []
        data["evidence"] = []
    elif scenario == "too_many":
        signal = data["signals"][0]
        data["signals"] = [dict(signal, id=f"s-{index}") for index in range(17)]
        data["evidence"] = [
            {"id": f"e-{index}", "signal_id": f"s-{index}", "summary": "fixture"}
            for index in range(17)
        ]
    return data


def selector_for(
    scenario: str, calls: list[str]
) -> Callable[[tuple[Sentence, ...]], Awaitable[object]]:
    async def select(sentences: tuple[Sentence, ...]) -> object:
        calls.append(scenario)
        if scenario in {"timeout", "unavailable"}:
            raise colibri.ModelUnavailable("simulado")
        if scenario == "intermediate":
            raise colibri.ModelRejected("simulado")
        if scenario == "internal":
            raise RuntimeError("detalhe não deve ser exposto")
        if scenario == "invalid_reference":
            return {"sentence_ids": ["S-MAX", "S-999"]}
        if scenario == "free_text":
            return {"sentence_ids": ["S-MAX"], "text": "causa inventada"}
        return {"sentence_ids": ["S-002", "S-MAX"]}

    return select


@pytest.mark.parametrize(
    ("scenario", "status", "explanation"),
    [
        ("success", 200, "verificada"),
        ("invalid", 422, None),
        ("insufficient", 200, "nao_solicitada"),
        ("timeout", 200, "indisponivel"),
        ("unavailable", 200, "indisponivel"),
        ("intermediate", 200, "rejeitada"),
        ("invalid_reference", 200, "rejeitada"),
        ("free_text", 200, "rejeitada"),
        ("too_many", 200, "indisponivel"),
        ("internal", 500, None),
    ],
)
def test_same_scenarios_against_real_route(
    monkeypatch: pytest.MonkeyPatch, scenario: str, status: int, explanation: str | None
) -> None:
    data = input_for(scenario)
    route_calls: list[str] = []
    experiment_calls: list[str] = []
    monkeypatch.setattr(
        colibri, "select_sentences", selector_for(scenario, route_calls)
    )
    with TestClient(app, raise_server_exceptions=False) as client:
        route = client.post("/v1/investigations", json=deepcopy(data))
    state = asyncio.run(
        experiment(deepcopy(data), selector_for(scenario, experiment_calls))
    )
    assert route.status_code == state.status_code == status
    if status == 500:
        assert route.json()["code"] == state.response["code"] == "erro_interno"
        assert "detalhe" not in route.text and "detalhe" not in repr(state.response)
    else:
        assert route.json() == state.response
    if explanation is not None:
        assert state.response["explanation"]["state"] == explanation
    assert route_calls == experiment_calls
    assert state.selector_calls == len(experiment_calls) <= 1
    assert state.stage == "fim" and state.transitions[-1] == "fim"
    assert state.selection is None and state.incident is None and not state.sentences
    assert len(state.transitions) <= 4
    if scenario in {"invalid", "insufficient", "too_many"}:
        assert not route_calls
    if scenario == "success":
        assert state.transitions == ["triagem", "selecao", "verificacao", "fim"]
    if scenario in {
        "timeout",
        "unavailable",
        "intermediate",
        "invalid_reference",
        "free_text",
    }:
        assert state.response["triage"]["severity"] == "media"
        assert state.response["explanation"]["text"] is None


def test_step_limit_fails_closed_without_running_selector() -> None:
    calls: list[str] = []
    state = asyncio.run(
        experiment(fixture(), selector_for("success", calls), step_limit=1)
    )
    assert state.response == {"code": "limite_workflow"} and state.status_code == 500
    assert state.transitions == ["triagem", "fim"] and not calls
    for limit in (0, 4, True):
        with pytest.raises(ValueError):
            asyncio.run(
                experiment(fixture(), selector_for("success", calls), step_limit=limit)
            )


def test_forged_evidence_is_rejected_independently(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forged(result: TriageResult) -> tuple[Sentence, ...]:
        sentences = canonical_sentences(result)
        return (replace(sentences[0], evidence_id="EVD-INEXISTENTE"), *sentences[1:])

    data = fixture()
    monkeypatch.setattr(api, "canonical_sentences", forged)
    monkeypatch.setitem(experiment.__globals__, "canonical_sentences", forged)
    monkeypatch.setattr(colibri, "select_sentences", selector_for("success", []))
    with TestClient(app, raise_server_exceptions=False) as client:
        route = client.post("/v1/investigations", json=data)
    state = asyncio.run(experiment(data, selector_for("success", [])))
    assert route.status_code == state.status_code == 200
    assert route.json() == state.response
    assert state.response["explanation"]["state"] == "rejeitada"
    assert state.response["explanation"]["text"] is None
