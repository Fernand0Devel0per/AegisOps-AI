"""Contratos locais para incidentes sintéticos; não fazem triagem."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from typing import Any, cast


@dataclass(frozen=True, slots=True)
class InputError:
    path: str
    code: str


class InvalidIncident(ValueError):
    """Entrada inválida; os detalhes não incluem os valores recebidos."""

    state = "entrada_invalida"

    def __init__(self, errors: tuple[InputError, ...]) -> None:
        self.errors = errors
        super().__init__("entrada_invalida")


@dataclass(frozen=True, slots=True)
class Period:
    start: datetime
    end: datetime


@dataclass(frozen=True, slots=True)
class Signal:
    id: str
    metric: str
    value: int | float
    unit: str
    aggregation: str
    period: Period
    source: str
    numerator: int | None = None
    denominator: int | None = None


@dataclass(frozen=True, slots=True)
class Evidence:
    id: str
    signal_id: str
    summary: str


@dataclass(frozen=True, slots=True)
class Incident:
    id: str
    service: str
    environment: str
    window: Period
    signals: tuple[Signal, ...]
    evidence: tuple[Evidence, ...]
    synthetic: bool = True


_UNITS = {
    "http_request_duration_p95": "ms",
    "http_5xx_rate": "percent",
    "cpu_utilization": "percent",
    "memory_utilization": "percent",
}


class _Validator:
    def __init__(self) -> None:
        self.errors: list[InputError] = []
        self.ids: set[str] = set()

    def incident(self, data: object) -> Incident:
        obj = self.obj(data, "$")
        identifier = self.identifier(obj, "id", "id")
        service = self.text(obj, "service", "service")
        environment = self.text(obj, "environment", "environment")
        self.validate_synthetic(obj)
        window = self.period(obj.get("window"), "window", 10)
        signals = self.signals(obj.get("signals"), window)
        evidence = self.evidence(obj.get("evidence"))
        self.validate_references(signals, evidence)
        self.raise_if_invalid()
        assert window is not None
        return Incident(identifier, service, environment, window, signals, evidence)

    def validate_synthetic(self, obj: dict[str, Any]) -> None:
        if obj.get("synthetic") is not True:
            self.error("synthetic", "sintetico_obrigatorio")

    def raise_if_invalid(self) -> None:
        if self.errors:
            raise InvalidIncident(tuple(self.errors))

    def error(self, path: str, code: str) -> None:
        self.errors.append(InputError(path, code))

    def obj(self, value: object, path: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            self.error(path, "objeto_esperado")
            return {}
        return value

    def text(self, obj: dict[str, Any], key: str, path: str) -> str:
        value = obj.get(key)
        if not isinstance(value, str) or not value.strip():
            self.error(path, "texto_obrigatorio")
            return ""
        return value

    def identifier(self, obj: dict[str, Any], key: str, path: str) -> str:
        value = self.text(obj, key, path)
        if value:
            if value in self.ids:
                self.error(path, "id_duplicado")
            self.ids.add(value)
        return value

    def timestamp(self, value: object, path: str) -> datetime | None:
        if not isinstance(value, str):
            self.error(path, "timestamp_utc_invalido")
            return None
        try:
            parsed = datetime.fromisoformat(value)
            if not _is_utc(parsed):
                raise ValueError
            return parsed.astimezone(UTC)
        except ValueError, OverflowError:
            self.error(path, "timestamp_utc_invalido")
            return None

    def period(self, value: object, path: str, minutes: int) -> Period | None:
        obj = self.obj(value, path)
        start = self.timestamp(obj.get("start"), f"{path}.start")
        end = self.timestamp(obj.get("end"), f"{path}.end")
        if start is None or end is None:
            return None
        if end - start != timedelta(minutes=minutes):
            self.error(path, "duracao_invalida")
            return None
        return Period(start, end)

    def items(self, value: object, path: str) -> list[Any]:
        if not isinstance(value, list):
            self.error(path, "lista_esperada")
            return []
        return value

    def signals(self, value: object, window: Period | None) -> tuple[Signal, ...]:
        signals = []
        for index, item in enumerate(self.items(value, "signals")):
            signals.append(self.signal(item, index, window))
        return tuple(signals)

    def signal(self, value: object, index: int, window: Period | None) -> Signal:
        path = f"signals[{index}]"
        obj = self.obj(value, path)
        identifier = self.identifier(obj, "id", f"{path}.id")
        metric = self.text(obj, "metric", f"{path}.metric")
        unit = self.text(obj, "unit", f"{path}.unit")
        aggregation = self.text(obj, "aggregation", f"{path}.aggregation")
        source = self.text(obj, "source", f"{path}.source")
        self.validate_metric_and_unit(metric, unit, path)
        numeric = self.signal_value(obj.get("value"), metric, path)
        period = self.signal_period(obj.get("period"), window, path)
        numerator, denominator = self.rate_counts(obj, metric, numeric, path)
        return Signal(
            id=identifier,
            metric=metric,
            value=cast(int | float, obj["value"]) if numeric is not None else 0,
            unit=unit,
            aggregation=aggregation,
            period=period or _placeholder_period(),
            source=source,
            numerator=numerator,
            denominator=denominator,
        )

    def validate_metric_and_unit(self, metric: str, unit: str, path: str) -> None:
        if metric and metric not in _UNITS:
            self.error(f"{path}.metric", "metrica_desconhecida")
        if _has_incompatible_unit(metric, unit):
            self.error(f"{path}.unit", "unidade_incompativel")

    def signal_value(self, value: object, metric: str, path: str) -> Decimal | None:
        numeric = _finite_decimal(value)
        if numeric is None:
            self.error(f"{path}.value", "numero_finito_esperado")
        elif _is_outside_metric_range(numeric, metric):
            self.error(f"{path}.value", "valor_fora_intervalo")
        return numeric

    def signal_period(
        self, value: object, window: Period | None, path: str
    ) -> Period | None:
        period = self.period(value, f"{path}.period", 5)
        if _is_outside_window(period, window):
            self.error(f"{path}.period", "periodo_fora_janela")
        return period

    def rate_counts(
        self, obj: dict[str, Any], metric: str, value: Decimal | None, path: str
    ) -> tuple[int | None, int | None]:
        if metric != "http_5xx_rate":
            return None, None
        numerator = obj.get("numerator")
        denominator = obj.get("denominator")
        self.validate_rate_counts(numerator, denominator, value, path)
        return (
            numerator if type(numerator) is int else None,
            denominator if type(denominator) is int else None,
        )

    def validate_rate_counts(
        self, numerator: object, denominator: object, value: Decimal | None, path: str
    ) -> None:
        valid_numerator = _is_nonnegative_integer(numerator)
        valid_denominator = _is_positive_integer(denominator)
        if not valid_numerator:
            self.error(f"{path}.numerator", "contagem_invalida")
        if not valid_denominator:
            self.error(f"{path}.denominator", "contagem_invalida")
        if not valid_numerator or not valid_denominator:
            return
        # The predicates above exclude bool as well as non-integers.
        numerator = cast(int, numerator)
        denominator = cast(int, denominator)
        if numerator > denominator:
            self.error(f"{path}.numerator", "contagem_invalida")
        elif value is not None and _is_inconsistent_rate(value, numerator, denominator):
            self.error(f"{path}.value", "taxa_inconsistente")

    def evidence(self, value: object) -> tuple[Evidence, ...]:
        evidence = []
        for index, item in enumerate(self.items(value, "evidence")):
            evidence.append(self.evidence_item(item, index))
        return tuple(evidence)

    def evidence_item(self, value: object, index: int) -> Evidence:
        path = f"evidence[{index}]"
        obj = self.obj(value, path)
        return Evidence(
            id=self.identifier(obj, "id", f"{path}.id"),
            signal_id=self.text(obj, "signal_id", f"{path}.signal_id"),
            summary=self.text(obj, "summary", f"{path}.summary"),
        )

    def validate_references(
        self, signals: tuple[Signal, ...], evidence: tuple[Evidence, ...]
    ) -> None:
        signal_ids = {signal.id for signal in signals if signal.id}
        linked = self.validate_evidence_links(evidence, signal_ids)
        self.validate_signals_have_evidence(signals, linked)

    def validate_evidence_links(
        self, evidence: tuple[Evidence, ...], signal_ids: set[str]
    ) -> set[str]:
        linked: set[str] = set()
        for index, item in enumerate(evidence):
            if item.signal_id and item.signal_id not in signal_ids:
                self.error(f"evidence[{index}].signal_id", "sinal_inexistente")
            elif item.signal_id:
                linked.add(item.signal_id)
        return linked

    def validate_signals_have_evidence(
        self, signals: tuple[Signal, ...], linked: set[str]
    ) -> None:
        for index, signal in enumerate(signals):
            if signal.id and signal.id not in linked:
                self.error(f"signals[{index}].id", "sinal_sem_evidencia")


def _is_utc(value: datetime) -> bool:
    return value.tzinfo is not None and value.utcoffset() == timedelta(0)


def _has_incompatible_unit(metric: str, unit: str) -> bool:
    return metric in _UNITS and bool(unit) and unit != _UNITS[metric]


def _finite_decimal(value: object) -> Decimal | None:
    if type(value) not in (int, float):
        return None
    try:
        numeric = Decimal(value) if isinstance(value, int) else Decimal(str(value))
        return numeric if numeric.is_finite() else None
    except InvalidOperation, ValueError, OverflowError:
        return None


def _is_outside_metric_range(value: Decimal, metric: str) -> bool:
    return value < 0 or (metric != "http_request_duration_p95" and value > 100)


def _is_outside_window(period: Period | None, window: Period | None) -> bool:
    if period is None or window is None:
        return False
    return period.start < window.start or period.end > window.end


def _is_nonnegative_integer(value: object) -> bool:
    return type(value) is int and value >= 0


def _is_positive_integer(value: object) -> bool:
    return type(value) is int and value > 0


def _is_inconsistent_rate(value: Decimal, numerator: int, denominator: int) -> bool:
    observed = Fraction(value)
    expected = Fraction(numerator * 100, denominator)
    return abs(observed - expected) > Fraction(1, 1_000_000)


def _placeholder_period() -> Period:
    # Invalid signals are never returned; this preserves reference checks after a bad period.
    instant = datetime.min.replace(tzinfo=UTC)
    return Period(instant, instant)


def validate_incident(data: object) -> Incident:
    """Valida objeto decodificado; erros são estáveis e nenhum resultado parcial é devolvido."""
    return _Validator().incident(data)
