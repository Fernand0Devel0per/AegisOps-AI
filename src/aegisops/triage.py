"""Triagem local de sinais sintéticos já sujeitos ao contrato de entrada."""

from dataclasses import dataclass
from typing import Literal

from aegisops.contracts import Incident, Period, Signal, validate_incident

Level = Literal["normal", "media", "alta"]

# Os limites são exemplos sintéticos aceitos, não política operacional.
_THRESHOLDS: dict[str, tuple[int, int]] = {
    "http_request_duration_p95": (500, 1500),
    "http_5xx_rate": (5, 10),
    "cpu_utilization": (95, 99),
    "memory_utilization": (90, 95),
}
_LEVEL_ORDER: dict[Level, int] = {"normal": 0, "media": 1, "alta": 2}


@dataclass(frozen=True, slots=True)
class Observation:
    signal_id: str
    metric: str
    value: int | float
    unit: str
    period: Period
    level: Level
    evidence_id: str


@dataclass(frozen=True, slots=True)
class TriageResult:
    incident_id: str
    state: Literal["classificado", "insuficiente"]
    severity: Level | None
    observations: tuple[Observation, ...]
    limitations: tuple[str, ...]
    explanation_state: Literal["nao_solicitada"] = "nao_solicitada"


def _signal_level(signal: Signal) -> Level:
    medium, high = _THRESHOLDS[signal.metric]
    if signal.value >= high:
        return "alta"
    if signal.value >= medium:
        return "media"
    return "normal"


def _selected_evidence(incident: Incident) -> dict[str, str]:
    selected: dict[str, str] = {}
    for evidence in incident.evidence:
        previous = selected.get(evidence.signal_id)
        if previous is None or evidence.id < previous:
            selected[evidence.signal_id] = evidence.id
    return selected


def _observations(incident: Incident) -> tuple[Observation, ...]:
    selected = _selected_evidence(incident)
    return tuple(
        Observation(
            signal_id=signal.id,
            metric=signal.metric,
            value=signal.value,
            unit=signal.unit,
            period=signal.period,
            level=_signal_level(signal),
            evidence_id=selected[signal.id],
        )
        for signal in incident.signals
    )


def _missing_metrics(incident: Incident) -> tuple[str, ...]:
    present = {signal.metric for signal in incident.signals}
    missing = tuple(
        f"Métrica ausente: {metric}" for metric in _THRESHOLDS if metric not in present
    )
    if missing:
        return (*missing, "Classificação parcial não demonstra ausência de degradação.")
    return ()


def triage_incident(data: object) -> TriageResult:
    """Valida a entrada e calcula observações; InvalidIncident não é interceptada."""
    incident = validate_incident(data)
    if not incident.signals:
        return TriageResult(
            incident_id=incident.id,
            state="insuficiente",
            severity=None,
            observations=(),
            limitations=("Ausência de sinais.",),
        )
    observations = _observations(incident)
    severity: Level = max(
        (item.level for item in observations), key=_LEVEL_ORDER.__getitem__
    )
    return TriageResult(
        incident_id=incident.id,
        state="classificado",
        severity=severity,
        observations=observations,
        limitations=_missing_metrics(incident),
    )
