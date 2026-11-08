"""Análise estruturada interna com orientações curadas e fontes verificadas.

Os textos curados são dados fixos; não interpreta documentos ou perguntas livres.
"""

import asyncio
import re
from dataclasses import dataclass
from typing import Literal

from aegisops.contracts import Incident, Period, Signal, validate_incident
from aegisops.descriptive import Provider, ProviderUnavailable
from aegisops.retrieval import CorpusError, Passage, _load_passages
from aegisops.triage import TriageResult, triage_incident

PROTOCOL_VERSION = "curated-selection-v1"
MAX_SIGNALS = 16
MAX_DOCUMENTS = 3
TIMEOUT_SECONDS = 1.0
_SAFE_ID = re.compile(r"[A-Za-z0-9_-]{1,80}\Z", re.ASCII)

# Paráfrases fixas dos trechos C1, não geradas a partir de conteúdo externo em tempo de execução.
_GUIDANCE = {
    "DU-5XX": (
        "O runbook orienta examinar a abrangência dos erros por endpoint ou região "
        "se essas observações estiverem disponíveis."
    ),
    "BK-CPU": (
        "O runbook orienta distinguir pico de padrão sustentado quando houver série temporal; "
        "utilização de CPU não estabelece throttling."
    ),
    "BK-MEM": (
        "O runbook orienta examinar abrangência e histórico de memória; duas médias "
        "não comprovam tendência contínua, vazamento ou evento iminente de falta de memória."
    ),
}

_CURATED_HASHES = {
    "DU-5XX": "de5cc367e13397e983c8ce084b08fcac6d1283eec1a26c841fd527b5a74470bf",
    "BK-CPU": "f2f4e71939d31252ea425e443228d7a0db710fd5ce966a99ab1d68ac208ebd8a",
    "BK-MEM": "e91a2a0a709c5f5c0811c6ef724cd563f23a18935182844870d29173eae5bbc1",
}


@dataclass(frozen=True, slots=True)
class Observation:
    incident_id: str
    signal_id: str
    evidence_id: str
    metric: str
    value: int | float
    unit: str
    period: Period
    numerator: int | None
    denominator: int | None


@dataclass(frozen=True, slots=True)
class Comparison:
    metric: str
    direction: Literal["aumentou", "diminuiu", "igual"]
    before_evidence_id: str
    after_evidence_id: str


@dataclass(frozen=True, slots=True)
class Guidance:
    document_id: str
    text: str
    path: str
    corpus_version: str
    sha256: str
    source_url: str
    source_version: str


@dataclass(frozen=True, slots=True)
class CuratedAnalysis:
    state: Literal[
        "aceita", "rejeitada", "timeout", "indisponivel", "insuficiente", "abstencao"
    ]
    triage: TriageResult
    observations: tuple[Observation, ...]
    comparisons: tuple[Comparison, ...]
    guidance: tuple[Guidance, ...]
    limitations: tuple[str, ...]


def _fallback(
    state: Literal["rejeitada", "timeout", "indisponivel", "insuficiente", "abstencao"],
    triage: TriageResult,
    limitation: str,
) -> CuratedAnalysis:
    return CuratedAnalysis(state, triage, (), (), (), (limitation,))


def _valid_request(evidence_ids: object, document_ids: object) -> bool:
    if not isinstance(evidence_ids, tuple) or not isinstance(document_ids, tuple):
        return False
    if len(evidence_ids) > MAX_SIGNALS or len(document_ids) > MAX_DOCUMENTS:
        return False
    refs = (*evidence_ids, *document_ids)
    if any(not isinstance(ref, str) or not _SAFE_ID.fullmatch(ref) for ref in refs):
        return False
    return len(set(refs)) == len(refs)


def _bounded_incident(incident: Incident) -> bool:
    return (
        len(incident.signals) <= MAX_SIGNALS
        and len(incident.evidence) <= 64
        and bool(_SAFE_ID.fullmatch(incident.id))
        and all(
            _SAFE_ID.fullmatch(signal.id)
            and len(signal.aggregation) <= 256
            and abs(signal.value) <= 10**15
            and (signal.numerator is None or signal.numerator <= 10**15)
            and (signal.denominator is None or signal.denominator <= 10**15)
            for signal in incident.signals
        )
    )


def _context(
    incident: Incident, evidence_ids: tuple[str, ...]
) -> tuple[tuple[Signal, str], ...] | None:
    signals = {signal.id: signal for signal in incident.signals}
    evidence = {item.id: item.signal_id for item in incident.evidence}
    if any(ref not in evidence or evidence[ref] not in signals for ref in evidence_ids):
        return None
    return tuple((signals[evidence[ref]], ref) for ref in evidence_ids)


def _valid_selection(selection: object, expected: tuple[str, ...]) -> bool:
    if not isinstance(selection, dict) or set(selection) != {"evidence_ids"}:
        return False
    ids = selection["evidence_ids"]
    if not isinstance(ids, list) or len(ids) != len(expected):
        return False
    if any(not isinstance(ref, str) or not _SAFE_ID.fullmatch(ref) for ref in ids):
        return False
    return len(set(ids)) == len(ids) and set(ids) == set(expected)


def _observation(incident: Incident, signal: Signal, ref: str) -> Observation:
    return Observation(
        incident.id,
        signal.id,
        ref,
        signal.metric,
        signal.value,
        signal.unit,
        signal.period,
        signal.numerator,
        signal.denominator,
    )


def _comparisons(context: tuple[tuple[Signal, str], ...]) -> tuple[Comparison, ...]:
    results = []
    for metric in sorted({signal.metric for signal, _ in context}):
        group = sorted(
            ((signal, ref) for signal, ref in context if signal.metric == metric),
            key=lambda item: item[0].period.start,
        )
        if len(group) != 2:
            continue
        (first, first_ref), (second, second_ref) = group
        if (
            first.unit != second.unit
            or first.aggregation != second.aggregation
            or first.period.end > second.period.start
        ):
            continue
        direction: Literal["aumentou", "diminuiu", "igual"] = (
            "aumentou"
            if second.value > first.value
            else "diminuiu"
            if second.value < first.value
            else "igual"
        )
        results.append(Comparison(metric, direction, first_ref, second_ref))
    return tuple(results)


def _guidance(
    document_ids: tuple[str, ...], passages: tuple[Passage, ...]
) -> tuple[Guidance, ...]:
    by_id = {item.id: item for item in passages}
    return tuple(
        Guidance(
            ref,
            _GUIDANCE[ref],
            by_id[ref].path,
            by_id[ref].corpus_version,
            by_id[ref].sha256,
            by_id[ref].source_url,
            by_id[ref].source_version,
        )
        for ref in document_ids
    )


async def analyze_curated(
    data: object,
    evidence_ids: tuple[str, ...],
    document_ids: tuple[str, ...],
    provider: Provider,
    *,
    causal_question: bool = False,
) -> CuratedAnalysis:
    """Analisa contexto explicitamente selecionado; não é uma interface HTTP."""
    incident = validate_incident(data)
    triage = triage_incident(data)
    if not _valid_request(evidence_ids, document_ids):
        return _fallback("rejeitada", triage, "Contexto solicitado inválido.")
    if not _bounded_incident(incident):
        return _fallback(
            "indisponivel", triage, "Entrada excede os limites do catálogo."
        )
    context = _context(incident, evidence_ids)
    if context is None or any(ref not in _GUIDANCE for ref in document_ids):
        return _fallback(
            "rejeitada", triage, "Referência inexistente ou fora do catálogo."
        )
    if not evidence_ids and not document_ids:
        state: Literal["insuficiente", "abstencao"] = (
            "insuficiente" if not incident.signals else "abstencao"
        )
        return _fallback(
            state, triage, "Nenhuma evidência ou orientação foi selecionada."
        )
    try:
        passages = _load_passages() if document_ids else ()
        by_id = {item.id: item for item in passages}
        if any(
            ref not in by_id or by_id[ref].sha256 != _CURATED_HASHES[ref]
            for ref in document_ids
        ):
            raise CorpusError("Versão curada divergente")
    except CorpusError:
        return _fallback(
            "indisponivel", triage, "Corpus documental indisponível ou inválido."
        )
    expected = (*evidence_ids, *document_ids)
    try:
        async with asyncio.timeout(TIMEOUT_SECONDS):
            selection = await provider.select(PROTOCOL_VERSION, expected)
    except TimeoutError:
        return _fallback("timeout", triage, "Tempo de espera do provedor excedido.")
    except ProviderUnavailable:
        return _fallback("indisponivel", triage, "Provedor indisponível.")
    if not _valid_selection(selection, expected):
        return _fallback(
            "rejeitada", triage, "Seleção inválida; resposta integral rejeitada."
        )
    limitations: tuple[str, ...] = (
        "Os sinais são dados recebidos, não comprovação independente de sua veracidade.",
        "Orientação documental não é observação do incidente; IDs não provam apoio semântico geral.",
        "Causa não é determinada pelas observações disponíveis.",
    )
    if "DU-5XX" in document_ids:
        limitations += (
            "O contexto estruturado não informa dados por endpoint ou região.",
        )
    if causal_question:
        limitations += ("Não há dados para estabelecer a causa solicitada.",)
    return CuratedAnalysis(
        "aceita",
        triage,
        tuple(_observation(incident, signal, ref) for signal, ref in context),
        _comparisons(context),
        _guidance(document_ids, passages),
        limitations,
    )
