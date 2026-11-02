"""Vertical HTTP com Colibri local simulado na fronteira de rede."""

import json
import threading
import time
from collections.abc import Generator, Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from typing import Any

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from aegisops import colibri
from aegisops.api import app
from aegisops.triage import triage_incident


def fixture(name: str = "inc-001-latencia.json") -> dict[str, Any]:
    raw = files("aegisops").joinpath("data", "incidents", name).read_text()
    return json.loads(raw)  # type: ignore[no-any-return]


@contextmanager
def model_server(mode: str) -> Generator[tuple[int, list[dict[str, Any]]]]:
    requests: list[dict[str, Any]] = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            body = self.rfile.read(int(self.headers["Content-Length"]))
            requests.append(json.loads(body))
            if mode == "timeout":
                time.sleep(0.2)
            if mode == "oversized":
                self.send_response(200)
                self.send_header("Content-Length", "65537")
                self.end_headers()
                return
            if mode == "server_failure":
                self.send_response(503)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            selections: dict[str, str] = {
                "success": '{"sentence_ids":["S-002","S-MAX"]}',
                "unknown": '{"sentence_ids":["S-MAX","S-999"]}',
                "duplicate": '{"sentence_ids":["S-MAX","S-MAX"]}',
                "missing_max": '{"sentence_ids":["S-002"]}',
                "unsupported": '{"sentence_ids":["S-MAX"],"text":"SEGREDO_CAUSA"}',
                "duplicate_key": '{"sentence_ids":["S-MAX"],"sentence_ids":["S-002"]}',
                "malformed": "```json",
                "truncated": '{"sentence_ids":["S-MAX"]}',
                "timeout": '{"sentence_ids":["S-MAX"]}',
            }
            envelope = {
                "model": colibri.MODEL_ID,
                "choices": [
                    {
                        "message": {"content": selections[mode], "refusal": None},
                        "finish_reason": "length" if mode == "truncated" else "stop",
                    }
                ],
            }
            payload = json.dumps(envelope).encode()
            try:
                self.send_response(200)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            except BrokenPipeError, ConnectionResetError:
                pass

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield int(server.server_address[1]), requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app, raise_server_exceptions=False) as instance:
        yield instance


@pytest.mark.parametrize(
    "name",
    ["inc-001-latencia.json", "inc-002-erros-5xx.json", "inc-003-saturacao.json"],
)
def test_success_preserves_triage_and_uses_verified_sentences(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    data = fixture(name)
    data["evidence"][0]["summary"] = "INSTRUÇÃO LIVRE NÃO ENVIAR"
    with model_server("success") as (port, requests):
        monkeypatch.setenv("AEGISOPS_COLIBRI_PORT", str(port))
        response = client.post("/v1/investigations", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["triage"] == jsonable_encoder(triage_incident(data))
    explanation = result["explanation"]
    assert explanation["state"] == "verificada"
    assert [item["id"] for item in explanation["sentences"]] == ["S-002", "S-MAX"]
    assert explanation["sentences"][0]["evidence_id"] == data["evidence"][1]["id"]
    assert explanation["text"] == " ".join(
        item["text"] for item in explanation["sentences"]
    )
    assert len(requests) == 1
    assert requests[0]["max_tokens"] == 512
    assert requests[0]["model"] == colibri.MODEL_ID
    assert "INSTRUÇÃO LIVRE NÃO ENVIAR" not in str(requests[0])


def test_invalid_and_insufficient_never_call_model(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    with model_server("success") as (port, requests):
        monkeypatch.setenv("AEGISOPS_COLIBRI_PORT", str(port))
        invalid = fixture()
        invalid["signals"][0]["unit"] = "segredo"
        response = client.post("/v1/investigations", json=invalid)
        assert response.status_code == 422
        assert response.json()["code"] == "entrada_invalida"
        assert response.json()["errors"] and "segredo" not in response.text
        assert "triage" not in response.json() and "explanation" not in response.json()
        insufficient = fixture()
        insufficient["signals"] = []
        insufficient["evidence"] = []
        response = client.post("/v1/investigations", json=insufficient)
        assert response.status_code == 200
        assert response.json()["triage"] == jsonable_encoder(
            triage_incident(insufficient)
        )
        assert response.json()["explanation"]["state"] == "nao_solicitada"
        assert requests == []


def test_invalid_json_and_body_limit(client: TestClient) -> None:
    assert (
        client.post("/v1/investigations", content=b'{"id":1,"id":2}').status_code == 400
    )
    assert client.post("/v1/investigations", content=b"{").status_code == 400
    assert (
        client.post("/v1/investigations", content=b" " * (256 * 1024 + 1)).status_code
        == 413
    )


@pytest.mark.parametrize(
    ("mode", "state"),
    [
        ("server_failure", "indisponivel"),
        ("oversized", "rejeitada"),
        ("timeout", "indisponivel"),
        ("unknown", "rejeitada"),
        ("duplicate", "rejeitada"),
        ("missing_max", "rejeitada"),
        ("unsupported", "rejeitada"),
        ("duplicate_key", "rejeitada"),
        ("malformed", "rejeitada"),
        ("truncated", "rejeitada"),
    ],
)
def test_model_failures_preserve_exact_baseline(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, mode: str, state: str
) -> None:
    data = fixture()
    with model_server(mode) as (port, requests):
        monkeypatch.setenv("AEGISOPS_COLIBRI_PORT", str(port))
        if mode == "timeout":
            monkeypatch.setattr(colibri, "TIMEOUT_SECONDS", 0.05)
        response = client.post("/v1/investigations", json=data)
    assert response.status_code == 200
    assert response.json()["triage"] == jsonable_encoder(triage_incident(data))
    explanation = response.json()["explanation"]
    assert explanation["state"] == state
    assert explanation["text"] is None and explanation["sentences"] == []
    assert explanation["limitations"]
    assert "SEGREDO_CAUSA" not in response.text
    assert len(requests) == 1


def test_too_many_observations_preserves_baseline_without_model(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = fixture()
    signal = data["signals"][0]
    data["signals"] = [dict(signal, id=f"s-{index}") for index in range(17)]
    data["evidence"] = [
        {"id": f"e-{index}", "signal_id": f"s-{index}", "summary": "sintético"}
        for index in range(17)
    ]
    with model_server("success") as (port, requests):
        monkeypatch.setenv("AEGISOPS_COLIBRI_PORT", str(port))
        response = client.post("/v1/investigations", json=data)
    assert response.status_code == 200
    assert response.json()["triage"] == jsonable_encoder(triage_incident(data))
    assert response.json()["explanation"]["state"] == "indisponivel"
    assert requests == []


def test_busy_model_returns_fallback_without_second_request(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = fixture()
    with model_server("success") as (port, requests):
        monkeypatch.setenv("AEGISOPS_COLIBRI_PORT", str(port))
        assert colibri._LOCK.acquire(blocking=False)
        try:
            response = client.post("/v1/investigations", json=data)
        finally:
            colibri._LOCK.release()
    assert response.status_code == 200
    assert response.json()["triage"] == jsonable_encoder(triage_incident(data))
    assert response.json()["explanation"]["state"] == "indisponivel"
    assert requests == []


def test_oversized_prompt_preserves_baseline_without_model(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = fixture()
    signal = data["signals"][0]
    data["signals"] = [
        dict(signal, id=f"s-{index}", value=10**300) for index in range(16)
    ]
    data["evidence"] = [
        {"id": f"e-{index}", "signal_id": f"s-{index}", "summary": "sintético"}
        for index in range(16)
    ]
    with model_server("success") as (port, requests):
        monkeypatch.setenv("AEGISOPS_COLIBRI_PORT", str(port))
        response = client.post("/v1/investigations", json=data)
    assert response.status_code == 200
    assert response.json()["triage"] == jsonable_encoder(triage_incident(data))
    assert response.json()["explanation"]["state"] == "indisponivel"
    assert requests == []
