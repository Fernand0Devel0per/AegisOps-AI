"""Adaptador lexical experimental; recebe exclusivamente IDs e textos de unidades."""

import hashlib
import json
import unicodedata


class InvalidQuery(ValueError):
    """Consulta ou k inválido."""


class CorpusError(RuntimeError):
    """Unidades inválidas ou hash divergente."""


def tokens(text):
    normalized = unicodedata.normalize("NFKD", text)
    stripped = "".join(
        c for c in normalized if not unicodedata.category(c).startswith("M")
    )
    words = []
    current = ""
    for char in stripped.casefold():
        if char.isalnum():
            current += char
        elif current:
            words.append(current)
            current = ""
    if current:
        words.append(current)
    return set(words)


def digest(records):
    data = json.dumps(
        records, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def build(records, expected_hash):
    if not isinstance(records, list) or not records or len(records) > 200:
        raise CorpusError("Lista de unidades inválida")
    if digest(records) != expected_hash:
        raise CorpusError("Hash das unidades divergente")
    if any(
        not isinstance(x, dict)
        or set(x) != {"id", "text"}
        or not isinstance(x["id"], str)
        or not x["id"]
        or not isinstance(x["text"], str)
        or not x["text"]
        for x in records
    ):
        raise CorpusError("Unidade inválida")
    if len({x["id"] for x in records}) != len(records):
        raise CorpusError("ID duplicado")
    return [
        {"id": x["id"], "text": x["text"], "terms": sorted(tokens(x["text"]))}
        for x in records
    ]


def search(index, query, k=5):
    if not isinstance(query, str) or len(query) > 4096 or not tokens(query):
        raise InvalidQuery("Consulta inválida")
    if type(k) is not int or not 1 <= k <= 5:
        raise InvalidQuery("k inválido")
    terms = tokens(query)
    hits = []
    for row in index:
        score = len(terms & set(row["terms"]))
        if score:
            hits.append({"id": row["id"], "score": score, "text": row["text"]})
    hits.sort(key=lambda item: (-item["score"], item["id"]))
    hits = hits[:k]
    return {"state": "returned" if hits else "abstained", "hits": hits}


def apply_budget(hits, limit=1800):
    if type(limit) is not int or limit < 0:
        raise ValueError("Orçamento inválido")
    context = []
    used = 0
    for hit in hits:
        header = f"[{hit['id']}]\n"
        if used + len(header) > limit:
            break
        available = limit - used - len(header)
        text = hit["text"][:available]
        used += len(header) + len(text)
        context.append(
            {
                "id": hit["id"],
                "header": header,
                "text": text,
                "start": 0,
                "end": len(text),
                "truncated": len(text) < len(hit["text"]),
            }
        )
        if len(text) < len(hit["text"]):
            break
    return {"budget": limit, "used": used, "chunks": context}
