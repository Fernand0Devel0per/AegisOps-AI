"""Consulta local de incidentes sintéticos, sem operações de escrita."""

import logging
from collections.abc import AsyncGenerator, Awaitable, Callable, Mapping
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.responses import Response

from aegisops import colibri
from aegisops.catalog import load_catalog
from aegisops.contracts import InvalidIncident, validate_incident
from aegisops.explanation import (
    InvalidExplanation,
    canonical_sentences,
    verify_selection,
)
from aegisops.triage import triage_incident


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: UP043
    app.state.catalog = load_catalog()
    yield
    app.state.catalog = None


app = FastAPI(lifespan=lifespan, openapi_url=None)
logger = logging.getLogger(__name__)


def problem(
    status: int,
    code: str,
    title: str,
    detail: str,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        media_type="application/problem+json",
        headers=headers,
        content={
            "type": "about:blank",
            "title": title,
            "status": status,
            "detail": detail,
            "code": code,
        },
    )


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
    if exc.status_code == 404:
        return problem(
            404, "nao_encontrado", "Não encontrado", "Recurso não encontrado."
        )
    if exc.status_code == 405:
        return problem(
            405,
            "metodo_nao_permitido",
            "Método não permitido",
            "Método não permitido.",
            exc.headers,
        )
    return problem(
        exc.status_code, "erro_http", "Erro HTTP", "A requisição falhou.", exc.headers
    )


@app.exception_handler(RequestValidationError)
async def validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return problem(400, "entrada_invalida", "Entrada inválida", "Parâmetro inválido.")


@app.middleware("http")
async def internal_errors(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    try:
        return await call_next(request)
    except Exception:  # noqa: BLE001 -- fronteira HTTP deve sanitizar falhas inesperadas.
        logger.error("Falha interna ao atender requisição")
        return problem(
            500, "erro_interno", "Erro interno", "Não foi possível atender à consulta."
        )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/incidents/{incident_id:path}")
def incident(incident_id: str, request: Request) -> Any:
    if not incident_id.strip():
        return problem(400, "entrada_invalida", "Entrada inválida", "ID inválido.")
    item = request.app.state.catalog.get(incident_id)
    if item is None:
        return problem(
            404,
            "incidente_nao_encontrado",
            "Não encontrado",
            "Incidente não encontrado.",
        )
    return jsonable_encoder(item)


MAX_INCIDENT_BYTES = 256 * 1024


def _explanation(state: str, limitation: str | None = None) -> dict[str, Any]:
    return {
        "state": state,
        "text": None,
        "sentences": [],
        "limitations": [limitation] if limitation else [],
    }


def _domain_problem(exc: InvalidIncident) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        media_type="application/problem+json",
        content={
            "type": "about:blank",
            "title": "Entrada inválida",
            "status": 422,
            "detail": "Incidente inválido.",
            "code": "entrada_invalida",
            "errors": [{"path": item.path, "code": item.code} for item in exc.errors],
        },
    )


async def _incident_body(request: Request) -> bytes | None:
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > MAX_INCIDENT_BYTES:
            return None
        body.extend(chunk)
    return bytes(body)


@app.post("/v1/investigations")
async def investigate(request: Request) -> Any:
    body = await _incident_body(request)
    if body is None:
        return problem(
            413,
            "corpo_excedido",
            "Corpo excedido",
            "Corpo da requisição excede o limite.",
        )
    try:
        data = colibri.parse_json(body)
    except ValueError, UnicodeDecodeError, RecursionError:
        return problem(400, "json_invalido", "JSON inválido", "Corpo JSON inválido.")
    try:
        result = triage_incident(data)
    except InvalidIncident as exc:
        return _domain_problem(exc)
    response: dict[str, Any] = {
        "triage": jsonable_encoder(result),
        "explanation": _explanation("nao_solicitada"),
    }
    if result.state == "insuficiente":
        return response
    if len(result.observations) > colibri.MAX_OBSERVATIONS:
        response["explanation"] = _explanation(
            "indisponivel", "Explicação excede limite local de observações."
        )
        return response
    incident = validate_incident(data)
    sentences = canonical_sentences(result)
    try:
        selection = await colibri.select_sentences(sentences)
        verified = verify_selection(selection, sentences, incident, result)
    except colibri.ModelUnavailable:
        response["explanation"] = _explanation(
            "indisponivel",
            "Explicação local indisponível; triagem determinística preservada.",
        )
        return response
    except colibri.ModelRejected, InvalidExplanation:
        response["explanation"] = _explanation(
            "rejeitada",
            "Explicação local rejeitada; triagem determinística preservada.",
        )
        return response
    response["explanation"] = {
        "state": "verificada",
        "text": " ".join(item.text for item in verified),
        "sentences": jsonable_encoder(verified),
        "limitations": [],
    }
    return response
