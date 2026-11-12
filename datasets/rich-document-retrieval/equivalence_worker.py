"""Compara adaptador com o pacote C1 original, dentro do sandbox."""

import json
from unittest.mock import patch

import adapter

from aegisops import retrieval as original


def signature_original(query, k):
    try:
        result = original.retrieve(query, k)
        return {
            "state": result.state,
            "hits": [(p.id, p.score) for p in result.passages],
        }
    except (original.InvalidQuery, original.CorpusError) as exc:
        return {"error": type(exc).__name__}


def signature_adapter(index, query, k):
    try:
        result = adapter.search(index, query, k)
        return {
            "state": result["state"],
            "hits": [(p["id"], p["score"]) for p in result["hits"]],
        }
    except (adapter.InvalidQuery, adapter.CorpusError) as exc:
        return {"error": type(exc).__name__}


def main():
    passages = original._load_passages()
    records = [{"id": p.id, "text": p.text} for p in passages]
    index = adapter.build(records, adapter.digest(records))
    with open("/c1queries.json", encoding="utf-8") as stream:
        queries = json.load(stream)
    cases = [
        (q, k)
        for q in queries
        + [
            "AÇÚCAR ÇÃO",
            "Straße ﬃ",
            "zzzzsemcoincidencia883733",
            "１２３ abc",
            "É é e\u0301",
        ]
        for k in (1, 2, 3, 4, 5)
    ]
    cases += [
        (q, k)
        for q, k in [
            ("", 1),
            ("---", 1),
            (None, 1),
            ("x" * 4097, 1),
            ("cpu", 0),
            ("cpu", 6),
            ("cpu", True),
        ]
    ]
    for query, k in cases:
        a = signature_original(query, k)
        b = signature_adapter(index, query, k)
        if a != b:
            raise AssertionError(f"Divergência: {query!r} k={k}: {a} != {b}")
    # The original retrieval algorithm is exercised with controlled passages for explicit ties.
    tie = [
        original.Passage(
            id=x,
            path=x,
            corpus_version="x",
            sha256="x",
            source_url="x",
            source_version="x",
            text="cpu",
            score=0,
        )
        for x in ("Z", "A", "B")
    ]
    tie_records = [{"id": p.id, "text": p.text} for p in tie]
    with patch.object(original, "_load_passages", return_value=tuple(tie)):
        a = signature_original("cpu", 2)
    b = signature_adapter(
        adapter.build(tie_records, adapter.digest(tie_records)), "cpu", 2
    )
    if a != b or [x[0] for x in b["hits"]] != ["A", "B"]:
        raise AssertionError("Empate divergente")
    with patch.object(original, "_read_resource", return_value=b"corrompido"):
        try:
            original._load_passages()
        except original.CorpusError:
            original_integrity = True
        else:
            original_integrity = False
    try:
        adapter.build(records, "0" * 64)
    except adapter.CorpusError:
        adapter_integrity = True
    else:
        adapter_integrity = False
    if not original_integrity or not adapter_integrity:
        raise AssertionError("Falha de integridade não rejeitada")
    print(
        json.dumps(
            {
                "status": "pass",
                "c1_queries": len(queries),
                "c1_comparisons": len(queries) * 5,
                "additional_cases": len(cases) - len(queries) * 5,
                "tie": "pass",
                "original_corpus_integrity": "pass",
                "adapter_integrity": "pass",
                "results": "IDs, scores, ordem, cortes e estados equivalentes",
                "network_namespace": __import__("os").stat("/proc/self/ns/net").st_ino,
            }
        )
    )


if __name__ == "__main__":
    main()
