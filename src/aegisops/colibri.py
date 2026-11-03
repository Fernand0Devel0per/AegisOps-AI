"""Consulta restrita ao Colibri local; o modelo nunca decide fatos da triagem."""

import asyncio
import json
import os
import threading
from typing import Any

from aegisops.explanation import Sentence

MODEL_ID = "qwen3-coder-30b-a3b-colibri"
TIMEOUT_SECONDS = 300.0
MAX_RESPONSE_BYTES = 65_536
MAX_PROMPT_BYTES = 4_096
MAX_OBSERVATIONS = 16
_LOCK = threading.Lock()


class ModelUnavailable(Exception):
    """Servidor indisponível, ocupado ou expirado."""


class ModelRejected(Exception):
    """Resposta de servidor ou modelo fora do contrato."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Chave JSON duplicada")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("Número JSON inválido")


def parse_json(data: str | bytes) -> Any:
    """Decodifica JSON estrito sem chaves duplicadas ou números não finitos."""
    return json.loads(
        data, object_pairs_hook=_unique_object, parse_constant=_reject_constant
    )


def _valid_port(value: str) -> bool:
    return (
        len(value) <= 5
        and value.isascii()
        and value.isdecimal()
        and 1 <= int(value) <= 65535
    )


def _port() -> int:
    value = os.environ.get("AEGISOPS_COLIBRI_PORT", "18999")
    if not _valid_port(value):
        raise ModelUnavailable("Configuração local inválida")
    return int(value)


def _prompt(sentences: tuple[Sentence, ...]) -> str:
    lines = " ".join(f"{sentence.id}: {sentence.text}" for sentence in sentences)
    return (
        "Selecione e ordene IDs das frases abaixo para explicar o incidente. "
        "Inclua obrigatoriamente S-MAX. Retorne somente um objeto JSON com a chave "
        "sentence_ids e uma lista de IDs, sem texto extra e sem IDs repetidos. " + lines
    )


def _request(prompt: str) -> bytes:
    data = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "max_tokens": 512,
        "temperature": 0,
    }
    body = json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")
    return (
        b"POST /v1/chat/completions HTTP/1.1\r\n"
        b"Host: 127.0.0.1\r\nContent-Type: application/json\r\n"
        b"Connection: close\r\nContent-Length: "
        + str(len(body)).encode("ascii")
        + b"\r\n\r\n"
        + body
    )


def _require_successful_status(status_line: str) -> None:
    parts = status_line.split(" ", 2)
    if len(parts) < 2 or not parts[0].startswith("HTTP/"):
        raise ValueError
    if int(parts[1]) != 200:
        raise ModelUnavailable("Servidor não respondeu com sucesso")


def _header_fields(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in lines:
        if not line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        if key in fields:
            raise ValueError
        fields[key] = value.strip()
    return fields


def _bounded_content_length(fields: dict[str, str]) -> int:
    if "transfer-encoding" in fields:
        raise ValueError
    length_text = fields["content-length"]
    if not length_text.isascii() or not length_text.isdecimal():
        raise ValueError
    length = int(length_text)
    if length > MAX_RESPONSE_BYTES:
        raise ValueError
    return length


def _content_length(headers: bytes) -> int:
    try:
        lines = headers.decode("iso-8859-1").split("\r\n")
        _require_successful_status(lines[0])
        return _bounded_content_length(_header_fields(lines[1:]))
    except (KeyError, ValueError, OverflowError) as exc:
        raise ModelRejected("Resposta HTTP inválida") from exc


def _completed_choice(envelope: Any) -> dict[str, Any]:
    if not isinstance(envelope, dict) or envelope.get("model") != MODEL_ID:
        raise ValueError
    choices = envelope.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        raise ValueError
    choice = choices[0]
    if not isinstance(choice, dict) or choice.get("finish_reason") != "stop":
        raise ValueError
    return choice


def _message_content(choice: dict[str, Any]) -> str:
    message = choice.get("message")
    if not isinstance(message, dict) or message.get("refusal") is not None:
        raise ValueError
    content = message.get("content")
    if not isinstance(content, str):
        raise TypeError
    return content


def _selection(body: bytes) -> object:
    try:
        choice = _completed_choice(parse_json(body))
        return parse_json(_message_content(choice))
    except (ValueError, TypeError, UnicodeDecodeError, RecursionError) as exc:
        raise ModelRejected("Resposta estruturada inválida") from exc


async def _exchange(request: bytes, port: int) -> bytes:
    reader, writer = await asyncio.open_connection("127.0.0.1", port, limit=8192)
    try:
        writer.write(request)
        await writer.drain()
        headers = await reader.readuntil(b"\r\n\r\n")
        length = _content_length(headers)
        return await reader.readexactly(length)
    finally:
        writer.close()
        await writer.wait_closed()


def _bounded_prompt(sentences: tuple[Sentence, ...]) -> str:
    if len(sentences) - 1 > MAX_OBSERVATIONS:
        raise ModelUnavailable("Quantidade de observações excede o limite local")
    prompt = _prompt(sentences)
    if len(prompt.encode("utf-8")) > MAX_PROMPT_BYTES:
        raise ModelUnavailable("Prompt excede o limite local")
    return prompt


async def _exchange_with_deadline(prompt: str) -> bytes:
    try:
        async with asyncio.timeout(TIMEOUT_SECONDS):
            return await _exchange(_request(prompt), _port())
    except (OSError, TimeoutError, asyncio.IncompleteReadError) as exc:
        raise ModelUnavailable("Servidor local indisponível ou expirado") from exc
    except asyncio.LimitOverrunError as exc:
        raise ModelRejected("Cabeçalho excede o limite") from exc


async def select_sentences(sentences: tuple[Sentence, ...]) -> object:
    """Solicita IDs sem enviar campos livres e com limite absoluto de tempo e volume."""
    prompt = _bounded_prompt(sentences)
    if not _LOCK.acquire(blocking=False):
        raise ModelUnavailable("Explicação ocupada")
    try:
        return _selection(await _exchange_with_deadline(prompt))
    finally:
        _LOCK.release()
