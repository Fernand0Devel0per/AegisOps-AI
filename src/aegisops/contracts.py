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
            if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
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

    def signal(self, value: object, index: int, window: Period | None) -> Signal:
        path = f"signals[{index}]"
        obj = self.obj(value, path)
        identifier = self.identifier(obj, "id", f"{path}.id")
        metric = self.text(obj, "metric", f"{path}.metric")
        unit = self.text(obj, "unit", f"{path}.unit")
        aggregation = self.text(obj, "aggregation", f"{path}.aggregation")
        source = self.text(obj, "source", f"{path}.source")
        if metric and metric not in _UNITS:
            self.error(f"{path}.metric", "metrica_desconhecida")
        if metric in _UNITS and unit and unit != _UNITS[metric]:
            self.error(f"{path}.unit", "unidade_incompativel")
        raw_value = obj.get("value")
        numeric: Decimal | None = None
        if type(raw_value) not in (int, float):
            self.error(f"{path}.value", "numero_finito_esperado")
        else:
            try:
                numeric = (
                    Decimal(raw_value)
                    if isinstance(raw_value, int)
                    else Decimal(str(raw_value))
                )
                if not numeric.is_finite():
                    raise InvalidOperation
            except InvalidOperation, ValueError, OverflowError:
                self.error(f"{path}.value", "numero_finito_esperado")
                numeric = None
        if numeric is not None and (
            numeric < 0 or (metric != "http_request_duration_p95" and numeric > 100)
        ):
            self.error(f"{path}.value", "valor_fora_intervalo")
        period = self.period(obj.get("period"), f"{path}.period", 5)
        if (
            period is not None
            and window is not None
            and (period.start < window.start or period.end > window.end)
        ):
            self.error(f"{path}.period", "periodo_fora_janela")
        numerator = obj.get("numerator")
        denominator = obj.get("denominator")
        if metric == "http_5xx_rate":
            valid_num = type(numerator) is int and numerator >= 0
            valid_den = type(denominator) is int and denominator > 0
            if not valid_num:
                self.error(f"{path}.numerator", "contagem_invalida")
            if not valid_den:
                self.error(f"{path}.denominator", "contagem_invalida")
            if (
                type(numerator) is int
                and type(denominator) is int
                and valid_num
                and valid_den
            ):
                if numerator > denominator:
                    self.error(f"{path}.numerator", "contagem_invalida")
                elif numeric is not None:
                    # Exact rational arithmetic keeps the tolerance independent of decimal context.
                    observed = Fraction(numeric)
                    expected = Fraction(numerator * 100, denominator)
                    if abs(observed - expected) > Fraction(1, 1_000_000):
                        self.error(f"{path}.value", "taxa_inconsistente")
        else:
            numerator = None
            denominator = None
        # Invalid placeholders are never returned: the caller raises if errors exist.
        return Signal(
            identifier,
            metric,
            cast(int | float, raw_value) if numeric is not None else 0,
            unit,
            aggregation,
            period
            or Period(
                datetime.min.replace(tzinfo=UTC), datetime.min.replace(tzinfo=UTC)
            ),
            source,
            numerator if type(numerator) is int else None,
            denominator if type(denominator) is int else None,
        )


def validate_incident(data: object) -> Incident:
    """Valida objeto decodificado; erros são estáveis e nenhum resultado parcial é devolvido."""
    v = _Validator()
    obj = v.obj(data, "$")
    identifier = v.identifier(obj, "id", "id")
    service = v.text(obj, "service", "service")
    environment = v.text(obj, "environment", "environment")
    if obj.get("synthetic") is not True:
        v.error("synthetic", "sintetico_obrigatorio")
    window = v.period(obj.get("window"), "window", 10)
    signals = tuple(
        v.signal(item, i, window)
        for i, item in enumerate(v.items(obj.get("signals"), "signals"))
    )
    evidence_list = v.items(obj.get("evidence"), "evidence")
    evidence: list[Evidence] = []
    for i, item in enumerate(evidence_list):
        path = f"evidence[{i}]"
        entry = v.obj(item, path)
        evidence.append(
            Evidence(
                v.identifier(entry, "id", f"{path}.id"),
                v.text(entry, "signal_id", f"{path}.signal_id"),
                v.text(entry, "summary", f"{path}.summary"),
            )
        )
    signal_ids = {signal.id for signal in signals if signal.id}
    linked: set[str] = set()
    for i, item in enumerate(evidence):
        if item.signal_id and item.signal_id not in signal_ids:
            v.error(f"evidence[{i}].signal_id", "sinal_inexistente")
        elif item.signal_id:
            linked.add(item.signal_id)
    for i, signal in enumerate(signals):
        if signal.id and signal.id not in linked:
            v.error(f"signals[{i}].id", "sinal_sem_evidencia")
    if v.errors:
        raise InvalidIncident(tuple(v.errors))
    assert window is not None
    return Incident(identifier, service, environment, window, signals, tuple(evidence))
