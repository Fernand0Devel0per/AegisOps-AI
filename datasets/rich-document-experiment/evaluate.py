#!/usr/bin/env python3
"""Reproduz cálculo a partir de julgamentos semânticos registrados pelo executor."""

import hashlib
import json
import statistics
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
CORPUS = ROOT.parent / "rich-documents"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(s):
    return " ".join(s.split())


def main():
    # Never read judgments until both extraction and chunk outputs exist and pass their frozen hashes.
    for freeze in ("extraction-freeze.json", "chunk-freeze.json"):
        for path, expected in read(OUT / freeze)["files"].items():
            if sha(OUT / path) != expected:
                raise ValueError("Saída congelada alterada: " + path)
    approved = "7860c4e2eb8b84fffa3c9383da5735ae88bf5659d97ef211e3daa6899f5771ee"
    if sha(CORPUS / "judgments.yaml") != approved:
        raise ValueError("Gabaritos alterados")
    cases = yaml.safe_load((CORPUS / "judgments.yaml").read_text(encoding="utf-8"))[
        "judgments"
    ]
    cases = [q for q in cases if q["status"] == "answerable"]
    review = yaml.safe_load((ROOT / "semantic-review.yaml").read_text(encoding="utf-8"))
    metrics = {}
    for mode in ("poppler", "pdfplumber"):
        records = review["extractors"][mode]
        occurrences = 0
        positives = 0
        single = 0
        details = []
        for case in cases:
            qid = case["question_id"]
            doc = case["evidence"][0]["document_id"]
            docout = read(OUT / "extractions" / mode / (doc + ".json"))
            flags = records[qid]["anchors"]
            assert len(flags) == len(case["evidence"])
            for evidence, flag in zip(case["evidence"], flags):
                text = next(
                    p["text"] for p in docout["pages"] if p["page"] == evidence["page"]
                )
                parts = evidence["anchor"].split(" | ")
                # Indicator checks tokens only; the semantic flag comes from the executor's review.
                if not all(normalize(part) in normalize(text) for part in parts):
                    raise ValueError(
                        f"{mode} {qid}: trecho não encontrado para conferir"
                    )
            occurrences += sum(flags)
            ok = all(flags) and records[qid]["relation"]
            positives += ok
            samepage = (
                len({(e["document_id"], e["page"]) for e in case["evidence"]}) == 1
            )
            single += ok and samepage
            details.append(
                {
                    "question_id": qid,
                    "document_id": doc,
                    "anchors_preserved": flags,
                    "relation_preserved": records[qid]["relation"],
                    "question_preserved": ok,
                    "single_page": samepage,
                    "reason": records[qid]["reason"],
                }
            )
        metrics[mode] = {
            "occurrences_preserved": occurrences,
            "occurrences_total": 15,
            "questions_preserved": positives,
            "questions_total": 11,
            "single_chunk_eligible": single,
            "single_chunk_total": 11,
            "questions": details,
        }
    for mode, strategy in (
        ("poppler", "fixed"),
        ("pdfplumber", "fixed"),
        ("pdfplumber", "structural"),
    ):
        filenames = sorted((OUT / "chunks" / mode / strategy).glob("*.json"))
        count = 0
        lengths = []
        overlapping = 0
        for path in filenames:
            chunk = read(path)
            doc = read(OUT / "extractions" / mode / path.name)
            bypage = {p["page"]: p["text"] for p in doc["pages"]}
            previous = {}
            for entry in chunk["chunks"]:
                text = bypage[entry["page"]]
                assert (
                    entry["text"] == text[entry["start"] : entry["end"]]
                    and len(entry["text"]) <= 600
                )
                overlap = max(0, previous.get(entry["page"], 0) - entry["start"])
                overlapping += overlap
                previous[entry["page"]] = entry["end"]
                lengths.append(len(entry["text"]))
                count += 1
            # In this corpus each page has one full chunk; no semantic judgments are extrapolated otherwise.
            assert all(
                sum(
                    1
                    for c in chunk["chunks"]
                    if c["page"] == p["page"] and c["text"] == p["text"]
                )
                == 1
                for p in doc["pages"]
            )
        metrics[mode + "/" + strategy] = {
            "documents": len(filenames),
            "chunks": count,
            "lengths": lengths,
            "overlap_characters": overlapping,
            "single_chunk_questions": metrics[mode]["single_chunk_eligible"],
            "multi_chunk_questions": metrics[mode]["questions_preserved"],
            "questions": [
                {
                    "question_id": q["question_id"],
                    "anchors_preserved": q["anchors_preserved"],
                    "union_sufficient": q["question_preserved"],
                    "single_chunk_sufficient": q["question_preserved"]
                    and q["single_page"],
                }
                for q in metrics[mode]["questions"]
            ],
            "notes": "Todos os chunks preservam o texto integral da sua página; relações semânticas herdadas da avaliação de extração.",
        }
    timings = read(OUT / "measurements.json")
    summary = {}
    for mode in (
        "poppler",
        "poppler_layout",
        "pdfplumber",
        "poppler/fixed",
        "pdfplumber/fixed",
        "pdfplumber/structural",
    ):
        rows = [
            r
            for r in timings
            if r.get("configuration") == mode
            and r.get("phase") == "measured"
            and r["status"] == "ok"
        ]
        summary[mode] = {
            "n": len(rows),
            "wall_mean_seconds": statistics.mean(x["wall_seconds"] for x in rows),
            "cpu_mean_seconds": statistics.mean(x["cpu_seconds"] for x in rows),
            "memory_peak_max_bytes": max(x["memory_peak_bytes"] for x in rows),
            "worker_operation_mean_seconds": statistics.mean(
                x["worker_timing"].get("extraction", x["worker_timing"].get("chunking"))
                for x in rows
            ),
            "worker_initialization_partial_mean_seconds": statistics.mean(
                x["worker_timing"]["worker_initialization"] for x in rows
            ),
        }
    result = {
        "reviewer": "autorrevisão semântica do executor; não é aceite humano",
        "metrics": metrics,
        "relations": review["relations"],
        "resources": summary,
    }
    (OUT / "evaluation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for mode in ("poppler", "pdfplumber"):
        print(
            mode,
            metrics[mode]["occurrences_preserved"],
            "/15",
            metrics[mode]["questions_preserved"],
            "/11",
            "single",
            metrics[mode]["single_chunk_eligible"],
            "/11",
        )
    for mode in ("poppler/fixed", "pdfplumber/fixed", "pdfplumber/structural"):
        print(
            mode,
            metrics[mode]["chunks"],
            "chunks; caracteres sobrepostos",
            metrics[mode]["overlap_characters"],
        )


if __name__ == "__main__":
    main()
