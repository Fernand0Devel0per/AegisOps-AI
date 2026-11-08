"""Protótipo de estudo local; não integra a API nem fornece ferramentas externas."""

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, Literal

from fastapi.encoders import jsonable_encoder

from aegisops import colibri
from aegisops.api import _domain_problem, _explanation
from aegisops.contracts import Incident, InvalidIncident, validate_incident
from aegisops.explanation import (
    InvalidExplanation,
    Sentence,
    canonical_sentences,
    verify_selection,
)
from aegisops.triage import TriageResult, triage_incident

Stage = Literal["triagem", "selecao", "verificacao", "fim"]
Selector = Callable[[tuple[Sentence, ...]], Awaitable[object]]
MAX_STEPS = 3


@dataclass(slots=True)
class State:
    stage: Stage = "triagem"
    transitions: list[str] = field(default_factory=list)
    triage: TriageResult | None = None
    incident: Incident | None = None
    sentences: tuple[Sentence, ...] = ()
    selection: object = None
    status_code: int = 200
    response: dict[str, Any] = field(default_factory=dict)
    selector_calls: int = 0


def _finish(state: State, status: int, response: dict[str, Any]) -> None:
    state.selection = None
    state.incident = None
    state.sentences = ()
    state.status_code = status
    state.response = response
    state.stage = "fim"
    state.transitions.append("fim")


def _fallback(state: State, explanation_state: str, limitation: str) -> None:
    assert state.triage is not None
    _finish(
        state,
        200,
        {
            "triage": jsonable_encoder(state.triage),
            "explanation": _explanation(explanation_state, limitation),
        },
    )


def _triage(state: State, data: object) -> None:
    try:
        result = triage_incident(data)
    except InvalidIncident as exc:
        error = _domain_problem(exc)
        _finish(state, error.status_code, json.loads(bytes(error.body)))
        return
    state.triage = result
    if result.state == "insuficiente":
        _fallback(state, "nao_solicitada", "")
        state.response["explanation"] = _explanation("nao_solicitada")
    elif len(result.observations) > colibri.MAX_OBSERVATIONS:
        _fallback(
            state, "indisponivel", "Explicação excede limite local de observações."
        )
    else:
        state.incident = validate_incident(data)
        state.sentences = canonical_sentences(result)
        state.stage = "selecao"


async def _select(state: State, selector: Selector) -> None:
    state.selector_calls += 1
    try:
        state.selection = await selector(state.sentences)
    except colibri.ModelUnavailable:
        _fallback(
            state,
            "indisponivel",
            "Explicação local indisponível; triagem determinística preservada.",
        )
    except colibri.ModelRejected:
        _fallback(
            state,
            "rejeitada",
            "Explicação local rejeitada; triagem determinística preservada.",
        )
    else:
        state.stage = "verificacao"


def _verify(state: State) -> None:
    assert state.triage is not None and state.incident is not None
    try:
        verified = verify_selection(
            state.selection, state.sentences, state.incident, state.triage
        )
    except InvalidExplanation:
        _fallback(
            state,
            "rejeitada",
            "Explicação local rejeitada; triagem determinística preservada.",
        )
        return
    _finish(
        state,
        200,
        {
            "triage": jsonable_encoder(state.triage),
            "explanation": {
                "state": "verificada",
                "text": " ".join(item.text for item in verified),
                "sentences": jsonable_encoder(verified),
                "limitations": [],
            },
        },
    )


async def experiment(
    data: object, selector: Selector, *, step_limit: int = MAX_STEPS
) -> State:
    """Executa no máximo três etapas, apenas em memória, usando seletor confiável de teste."""
    if type(step_limit) is not int or not 1 <= step_limit <= MAX_STEPS:
        raise ValueError("Limite inválido")
    state = State()
    for _ in range(step_limit):
        state.transitions.append(state.stage)
        try:
            if state.stage == "triagem":
                _triage(state, data)
            elif state.stage == "selecao":
                await _select(state, selector)
            elif state.stage == "verificacao":
                _verify(state)
        except Exception:  # noqa: BLE001 -- equivalente sanitizado à fronteira HTTP do estudo.
            _finish(state, 500, {"code": "erro_interno"})
        if state.stage == "fim":
            return state
    _finish(state, 500, {"code": "limite_workflow"})
    return state
