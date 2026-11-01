"""Frases sintéticas canônicas e verificação independente de uma seleção."""

from dataclasses import dataclass

from aegisops.contracts import Incident, Signal
from aegisops.triage import Observation, TriageResult


@dataclass(frozen=True, slots=True)
class Sentence:
    id: str
    text: str
    signal_id: str
    evidence_id: str


class InvalidExplanation(ValueError):
    """Seleção ou referências não atendem à política de explicação."""


def _observation_text(item: Observation, index: int) -> str:
    return (
        f"Sinal {index}: {item.metric} = {item.value} {item.unit}, "
        f"de {item.period.start.isoformat()} até {item.period.end.isoformat()} "
        f"(fim exclusivo); nível {item.level}."
    )


def canonical_sentences(result: TriageResult) -> tuple[Sentence, ...]:
    """Gera somente afirmações derivadas do resultado determinístico classificado."""
    if result.state != "classificado" or result.severity is None:
        raise ValueError("Explicação exige resultado classificado")
    maximum = next(
        (index, item)
        for index, item in enumerate(result.observations, start=1)
        if item.level == result.severity
    )
    max_index, max_item = maximum
    return (
        Sentence(
            "S-MAX",
            f"Severidade máxima {result.severity}, determinada pelo sinal {max_index}.",
            max_item.signal_id,
            max_item.evidence_id,
        ),
        *(
            Sentence(
                f"S-{index:03d}",
                _observation_text(item, index),
                item.signal_id,
                item.evidence_id,
            )
            for index, item in enumerate(result.observations, start=1)
        ),
    )


def _selection_ids(selection: object) -> list[str]:
    if not isinstance(selection, dict) or set(selection) != {"sentence_ids"}:
        raise InvalidExplanation("Estrutura inválida")
    ids = selection["sentence_ids"]
    if not isinstance(ids, list) or not ids or any(not isinstance(x, str) for x in ids):
        raise InvalidExplanation("Lista inválida")
    if len(set(ids)) != len(ids) or "S-MAX" not in ids:
        raise InvalidExplanation("Seleção duplicada ou sem severidade máxima")
    return ids


def verify_selection(
    selection: object,
    sentences: tuple[Sentence, ...],
    incident: Incident,
    result: TriageResult,
) -> tuple[Sentence, ...]:
    """Rejeita seleção inválida ou referência não vinculada ao sinal descrito."""
    ids = _selection_ids(selection)
    if result.state != "classificado" or sentences != canonical_sentences(result):
        raise InvalidExplanation("Catálogo de frases inválido")
    by_id = {sentence.id: sentence for sentence in sentences}
    if len(by_id) != len(sentences) or any(item not in by_id for item in ids):
        raise InvalidExplanation("ID de frase inválido")
    links = {(evidence.id, evidence.signal_id) for evidence in incident.evidence}
    signals = {signal.id: signal for signal in incident.signals}
    observations = {item.signal_id: item for item in result.observations}
    chosen = tuple(by_id[item] for item in ids)
    if result.incident_id != incident.id or any(
        sentence.signal_id not in signals
        or sentence.signal_id not in observations
        or (sentence.evidence_id, sentence.signal_id) not in links
        or not _matches_observation(
            signals[sentence.signal_id], observations[sentence.signal_id]
        )
        for sentence in chosen
    ):
        raise InvalidExplanation("Referência inválida")
    return chosen


def _matches_observation(signal: Signal, observation: Observation) -> bool:
    return (
        signal.id == observation.signal_id
        and signal.metric == observation.metric
        and signal.value == observation.value
        and signal.unit == observation.unit
        and signal.period == observation.period
    )
