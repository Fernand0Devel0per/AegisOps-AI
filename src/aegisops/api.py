"""Consulta local de incidentes sintéticos, sem operações de escrita."""

import logging
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.responses import Response

from aegisops.catalog import load_catalog


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
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
