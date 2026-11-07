"""Recorte offline descritivo: seleção restrita de observações estruturadas.

Não interpreta texto livre, documentos ou perguntas abertas e não verifica semântica geral.
"""

import asyncio
import re
from dataclasses import dataclass
from typing import Literal, Protocol

from aegisops.contracts import Incident, Signal, validate_incident
from aegisops.triage import TriageResult, triage_incident

PROMPT_VERSION = "descriptive-selection-v1"
MAX_SIGNALS = 16
TIMEOUT_SECONDS = 1.0
_METRICS = frozenset(
    {
        "http_request_duration_p95",
        "http_5xx_rate",
        "cpu_utilization",
        "memory_utilization",
    }
)
_SAFE_ID = re.compile(r"[A-Za-z0-9_-]{1,80}\Z", re.ASCII)


class ProviderUnavailable(Exception):
    """O provedor não está disponível."""


class Provider(Protocol):
    async def select(self, prompt_version: str, ids: tuple[str, ...]) -> object: ...


class MockProvider:
    """Seleciona todos os IDs em memória, sem rede ou credenciais."""

    async def select(self, prompt_version: str, ids: tuple[str, ...]) -> object:
        return {"evidence_ids": list(ids)}


@dataclass(frozen=True, slots=True)
class Fact:
    text: str
    references: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Analysis:
    state: Literal[
        "aceita", "rejeitada", "timeout", "indisponivel", "insuficiente", "abstencao"
    ]
    triage: TriageResult
    facts: tuple[Fact, ...]
    limitations: tuple[str, ...]


def _fallback(
    state: Literal["rejeitada", "timeout", "indisponivel", "insuficiente", "abstencao"],
    triage: TriageResult,
    limitation: str,
) -> Analysis:
    return Analysis(state, triage, (), (limitation,))


def _context(incident: Incident, metric: str) -> tuple[tuple[Signal, str], ...]:
    links = {
        e.signal_id: e.id
        for e in sorted(incident.evidence, key=lambda e: e.id, reverse=True)
    }
    return tuple(
        (signal, links[signal.id])
        for signal in incident.signals
        if signal.metric == metric and signal.id in links
    )


def _valid_selection(
    selection: object, context: tuple[tuple[Signal, str], ...], incident: Incident
) -> bool:
    if not isinstance(selection, dict) or set(selection) != {"evidence_ids"}:
        return False
    ids = selection["evidence_ids"]
    expected = tuple(ref for _, ref in context)
    if not isinstance(ids, list) or len(ids) != len(expected):
        return False
    if any(not isinstance(ref, str) for ref in ids):
        return False
    links = {(e.id, e.signal_id) for e in incident.evidence}
    return (
        len(ids) == len(expected)
        and len(set(ids)) == len(ids)
        and set(ids) == set(expected)
        and all(
            _SAFE_ID.fullmatch(ref) and (ref, signal.id) in links
            for signal, ref in context
        )
    )


def _fact(signal: Signal, reference: str) -> Fact:
    count = (
        ""
        if signal.numerator is None
        else f" ({signal.numerator} de {signal.denominator})"
    )
    return Fact(
        f"{signal.metric}: {signal.value} {signal.unit}{count}; "
        f"de {signal.period.start.isoformat()} até {signal.period.end.isoformat()} (fim exclusivo).",
        (reference,),
    )


def _comparison(context: tuple[tuple[Signal, str], ...]) -> tuple[Fact, ...]:
    if len(context) != 2:
        return ()
    ordered = sorted(context, key=lambda item: item[0].period.start)
    (first, first_ref), (second, second_ref) = ordered
    if (
        first.unit != second.unit
        or first.aggregation != second.aggregation
        or first.period.end > second.period.start
    ):
        return ()
    direction = (
        "aumentou"
        if second.value > first.value
        else "diminuiu"
        if second.value < first.value
        else "permaneceu igual"
    )
    return (
        Fact(
            f"A métrica {direction} entre os períodos indicados.",
            (first_ref, second_ref),
        ),
    )


async def analyze(
    data: object, metric: str, provider: Provider, *, causal_question: bool = False
) -> Analysis:
    """Analisa uma métrica explícita; entrada inválida conserva a exceção do contrato existente."""
    incident = validate_incident(data)
    triage = triage_incident(data)
    if metric not in _METRICS:
        return _fallback(
            "abstencao", triage, "Pergunta fora do recorte estruturado disponível."
        )
    if not incident.signals:
        return _fallback(
            "insuficiente", triage, "Não há sinais disponíveis para responder."
        )
    if len(incident.signals) > MAX_SIGNALS:
        return _fallback(
            "indisponivel", triage, "Quantidade de sinais excede o limite."
        )
    context = _context(incident, metric)
    if not context:
        return _fallback(
            "abstencao", triage, "Não há sinal disponível para a métrica solicitada."
        )
    if any(not _SAFE_ID.fullmatch(ref) for _, ref in context):
        return _fallback("rejeitada", triage, "Referência fora do formato permitido.")
    try:
        async with asyncio.timeout(TIMEOUT_SECONDS):
            selection = await provider.select(
                PROMPT_VERSION, tuple(ref for _, ref in context)
            )
    except TimeoutError:
        return _fallback("timeout", triage, "Tempo de espera do provedor excedido.")
    except ProviderUnavailable:
        return _fallback("indisponivel", triage, "Provedor indisponível.")
    if not _valid_selection(selection, context, incident):
        return _fallback(
            "rejeitada",
            triage,
            "Seleção ou referências inválidas; resposta integral rejeitada.",
        )
    facts = tuple(_fact(signal, ref) for signal, ref in context) + _comparison(context)
    limitation = (
        "Observações não estabelecem causa; apoio semântico geral não foi verificado."
    )
    if causal_question:
        limitation = (
            "A causa não pode ser determinada a partir destas observações. "
            + limitation
        )
    return Analysis("aceita", triage, facts, (limitation,))
