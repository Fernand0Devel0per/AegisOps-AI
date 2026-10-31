"""Testes HTTP contra o pacote instalado e seu catálogo distribuído."""

import json
from importlib.resources import files
from typing import Any
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from aegisops import catalog
from aegisops.api import app
from aegisops.contracts import validate_incident


@pytest.fixture
def client() -> Any:
    with TestClient(app, raise_server_exceptions=False) as instance:
        yield instance


def assert_problem(response: Any, status: int, code: str) -> None:
    assert response.status_code == status
    assert response.headers["content-type"] == "application/problem+json"
    assert isinstance(response.json()["title"], str) and response.json()["title"]
    assert isinstance(response.json()["detail"], str) and response.json()["detail"]
    assert response.json() == {
        "type": "about:blank",
        "title": response.json()["title"],
        "status": status,
        "detail": response.json()["detail"],
        "code": code,
    }


@pytest.mark.parametrize(
    "name",
    ["inc-001-latencia.json", "inc-002-erros-5xx.json", "inc-003-saturacao.json"],
)
def test_installed_catalog_incidents(client: TestClient, name: str) -> None:
    data = json.loads(files("aegisops").joinpath("data", "incidents", name).read_text())
    response = client.get(f"/v1/incidents/{data['id']}")
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == data["id"]
    assert result["synthetic"] is True
    assert len(result["signals"]) == len(data["signals"])
    assert len(result["evidence"]) == len(data["evidence"])
    assert "expected" not in result and "limitations" not in result
    assert result["window"]["start"].startswith("2026-10-01")


def test_health_after_startup(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_nonexistent_and_invalid_ids(client: TestClient) -> None:
    assert_problem(client.get("/v1/incidents/ausente"), 404, "incidente_nao_encontrado")
    assert_problem(client.get("/v1/incidents/%20%20"), 400, "entrada_invalida")
    assert_problem(client.get("/v1/incidents/"), 400, "entrada_invalida")


def test_ids_are_exact_and_not_arbitrarily_limited(client: TestClient) -> None:
    raw = files("aegisops").joinpath("data", "incidents", "inc-001-latencia.json")
    for identifier in ("a", "x" * 4096, " serviço/Ω ", "../catalog.json"):
        data = json.loads(raw.read_text())
        data["id"] = identifier
        app.state.catalog[identifier] = validate_incident(data)
        response = client.get("/v1/incidents/" + quote(identifier, safe=""))
        assert response.status_code == 200
        assert response.json()["id"] == identifier
    assert_problem(client.get("/v1/incidents/%20a%20"), 404, "incidente_nao_encontrado")


def test_traversal_never_reads_client_paths(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(name: str) -> str:
        raise AssertionError("Requisição não pode ler arquivos")

    monkeypatch.setattr(catalog, "_read_resource", forbidden)
    response = client.get("/v1/incidents/..%2F..%2Fetc%2Fpasswd")
    assert_problem(response, 404, "incidente_nao_encontrado")
    assert "root:" not in response.text


def test_other_http_errors_are_structured(client: TestClient) -> None:
    assert_problem(client.get("/inexistente"), 404, "nao_encontrado")
    response = client.post("/health")
    assert_problem(response, 405, "metodo_nao_permitido")
    assert response.headers["allow"] == "GET"


def test_internal_error_is_sanitized(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    class BrokenCatalog:
        def get(self, identifier: str) -> None:
            raise RuntimeError("SEGREDO_INTERNO")

    app.state.catalog = BrokenCatalog()
    response = client.get("/v1/incidents/consulta")
    assert_problem(response, 500, "erro_interno")
    assert "SEGREDO_INTERNO" not in response.text
    assert "SEGREDO_INTERNO" not in caplog.text


@pytest.mark.parametrize(
    "failure", ["missing", "json", "duplicate_key", "invalid", "duplicate_id"]
)
def test_startup_failure_prevents_requests(
    monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    original = catalog._read_resource

    def read(name: str) -> str:
        if failure == "missing":
            raise FileNotFoundError("ausente")
        if failure == "json":
            return "{"
        if failure == "duplicate_key":
            return '{"id":"a", "id":"b"}'
        if failure == "invalid":
            return "{}"
        return original("inc-001-latencia.json")

    monkeypatch.setattr(catalog, "_read_resource", read)
    with pytest.raises((FileNotFoundError, ValueError)), TestClient(app):
        pytest.fail("Inicialização inválida aceitou requisições")
