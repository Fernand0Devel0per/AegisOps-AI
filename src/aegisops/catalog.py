"""Catálogo sintético fixo, validado integralmente antes de servir consultas."""

import json
from importlib.resources import files

from aegisops.contracts import Incident, validate_incident

_RESOURCE_NAMES = (
    "inc-001-latencia.json",
    "inc-002-erros-5xx.json",
    "inc-003-saturacao.json",
)


def _read_resource(name: str) -> str:
    return files("aegisops").joinpath("data", "incidents", name).read_text("utf-8")


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Chave JSON duplicada no catálogo")
        result[key] = value
    return result


def load_catalog() -> dict[str, Incident]:
    """Carrega apenas recursos do pacote e rejeita catálogo parcial ou duplicado."""
    catalog: dict[str, Incident] = {}
    for name in _RESOURCE_NAMES:
        data = json.loads(_read_resource(name), object_pairs_hook=_unique_object)
        incident = validate_incident(data)
        if incident.id in catalog:
            raise ValueError("ID duplicado no catálogo")
        catalog[incident.id] = incident
    return catalog
