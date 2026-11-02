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


def _port() -> int:
    value = os.environ.get("AEGISOPS_COLIBRI_PORT", "18999")
    if (
        len(value) > 5
        or not value.isascii()
        or not value.isdecimal()
        or not 1 <= int(value) <= 65535
    ):
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


def _content_length(headers: bytes) -> int:
    try:
        lines = headers.decode("iso-8859-1").split("\r\n")
        parts = lines[0].split(" ", 2)
        if len(parts) < 2 or not parts[0].startswith("HTTP/"):
            raise ValueError
        status = int(parts[1])
        if status != 200:
            raise ModelUnavailable("Servidor não respondeu com sucesso")
        fields: dict[str, str] = {}
        for line in lines[1:]:
            if not line:
                continue
            key, value = line.split(":", 1)
            key = key.strip().lower()
            if key in fields:
                raise ValueError
            fields[key] = value.strip()
        if "transfer-encoding" in fields:
            raise ValueError
        length_text = fields["content-length"]
        if not length_text.isascii() or not length_text.isdecimal():
            raise ValueError
        length = int(length_text)
        if length > MAX_RESPONSE_BYTES:
            raise ValueError
        return length
    except (KeyError, ValueError, OverflowError) as exc:
        raise ModelRejected("Resposta HTTP inválida") from exc


def _selection(body: bytes) -> object:
    try:
        envelope = parse_json(body)
        if not isinstance(envelope, dict) or envelope.get("model") != MODEL_ID:
            raise ValueError
        choices = envelope.get("choices")
        if not isinstance(choices, list) or len(choices) != 1:
            raise ValueError
        choice = choices[0]
        if not isinstance(choice, dict) or choice.get("finish_reason") != "stop":
            raise ValueError
        message = choice.get("message")
        if not isinstance(message, dict) or message.get("refusal") is not None:
            raise ValueError
        content = message.get("content")
        if not isinstance(content, str):
            raise TypeError
        return parse_json(content)
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


async def select_sentences(sentences: tuple[Sentence, ...]) -> object:
    """Solicita IDs sem enviar campos livres e com limite absoluto de tempo e volume."""
    if len(sentences) - 1 > MAX_OBSERVATIONS:
        raise ModelUnavailable("Quantidade de observações excede o limite local")
    prompt = _prompt(sentences)
    if len(prompt.encode("utf-8")) > MAX_PROMPT_BYTES:
        raise ModelUnavailable("Prompt excede o limite local")
    if not _LOCK.acquire(blocking=False):
        raise ModelUnavailable("Explicação ocupada")
    try:
        try:
            async with asyncio.timeout(TIMEOUT_SECONDS):
                response = await _exchange(_request(prompt), _port())
        except (OSError, TimeoutError, asyncio.IncompleteReadError) as exc:
            raise ModelUnavailable("Servidor local indisponível ou expirado") from exc
        except asyncio.LimitOverrunError as exc:
            raise ModelRejected("Cabeçalho excede o limite") from exc
        return _selection(response)
    finally:
        _LOCK.release()
