"""Calcula resultados a partir de rankings congelados e revisão semântica separada."""

import hashlib
import json
import statistics
from pathlib import Path

import judge

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
OUT = ROOT / "output"
OLD = REPO / "datasets/rich-document-experiment/output"
CORPUS = REPO / "datasets/rich-documents"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference(hit, configuration, provenance, available):
    ref = provenance[configuration][hit["id"]]
    pdf = CORPUS / "documents" / (ref["document_id"] + ".pdf")
    chunk = REPO / ref["chunk_file"]
    mode = "poppler" if configuration == "B1" else "pdfplumber"
    source = read(OLD / "extractions" / mode / (ref["document_id"] + ".json"))
    page = next(p["text"] for p in source["pages"] if p["page"] == ref["page"])
    text = hit["text"]
    start = ref["start"]
    end = start + len(available)
    valid = (
        sha(pdf) == ref["pdf_sha256"]
        and sha(chunk) == ref["chunk_file_sha256"]
        and page[start : ref["end"]] == text
        and text.startswith(available)
        and ref["end"] - start == len(text)
    )
    return {
        "chunk_id": hit["id"],
        "score": hit["score"],
        "document_id": ref["document_id"],
        "document_version": ref["document_version"],
        "pdf_sha256": ref["pdf_sha256"],
        "page": ref["page"],
        "section": None,
        "section_status": "not_extracted",
        "span_in_extraction": [start, end],
        "chunk_full_span": [start, ref["end"]],
        "visible_characters": len(available),
        "truncated": len(available) < len(text),
        "resolvable": valid,
    }


def covered(evidence, ref, visible):
    return (
        evidence["eligible"]
        and evidence["document_id"] == ref["document_id"]
        and evidence["page"] == ref["page"]
        and all(text in visible for text in evidence["required_text"])
    )


def evaluate_row(row, case, provenance, kind):
    if kind == "raw":
        items = [{"id": x["id"], "text": x["text"]} for x in row["hits"]]
    else:
        items = row["context"]["chunks"]
    hitmap = {x["id"]: x for x in row["hits"]}
    citations = []
    anchor_positions = {}
    for rank, item in enumerate(items, 1):
        hit = hitmap[item["id"]]
        ref = reference(hit, row["configuration"], provenance, item["text"])
        if not ref["resolvable"]:
            raise ValueError("Citação não resolvível: " + item["id"])
        if case["status"] == "answerable":
            found = [
                e["occurrence"]
                for e in case["evidence"]
                if covered(e, ref, item["text"])
            ]
            relevant_location = any(
                e["document_id"] == ref["document_id"] and e["page"] == ref["page"]
                for e in case["evidence"]
            )
            for number in found:
                anchor_positions.setdefault(number, rank)
            ref["semantic_status"] = (
                "supports_anchor"
                if found
                else "insufficient"
                if relevant_location
                else "unjudged"
            )
            ref["supported_occurrences"] = found
            ref["justification"] = (
                case["reason"]
                if relevant_location
                else "Trecho não julgado para esta consulta; não é automaticamente negativo."
            )
        else:
            ref["semantic_status"] = (
                "related_insufficient"
                if ref["document_id"] == case["related_document"]
                else "unjudged"
            )
            ref["supported_occurrences"] = []
            ref["justification"] = (
                case["reason"]
                if ref["semantic_status"] == "related_insufficient"
                else "Trecho não julgado para esta consulta."
            )
        citations.append(ref)
    record = {
        "configuration": row["configuration"],
        "question_id": row["question_id"],
        "k": row["k"],
        "view": kind,
        "state": row["state"],
        "ranking": [{"id": h["id"], "score": h["score"]} for h in row["hits"]],
        "citations": citations,
    }
    if case["status"] == "answerable":
        total = len(case["evidence"])
        covered_ids = sorted(anchor_positions)
        missing = [x for x in range(1, total + 1) if x not in anchor_positions]
        first = min(anchor_positions.values()) if anchor_positions else None
        relation = case["relation_preserved_in_extraction"]
        record.update(
            {
                "status": "answerable",
                "expected_answer": case["expected_answer"],
                "anchor_coverage": len(covered_ids),
                "anchor_total": total,
                "covered_occurrences": covered_ids,
                "missing_occurrences": missing,
                "recall": len(covered_ids) / total,
                "first_relevant_rank": first,
                "reciprocal_rank": 1 / first if first else 0.0,
                "fully_sufficient": len(covered_ids) == total and relation,
                "partial": 0 < len(covered_ids) < total
                or (len(covered_ids) == total and not relation),
                "relation_preserved": relation,
                "justification": case["reason"],
            }
        )
    else:
        record.update(
            {
                "status": "absent",
                "related_insufficient_returns": sum(
                    x["semantic_status"] == "related_insufficient" for x in citations
                ),
                "absence_scope": "RICH-01 v1.0.0 completo",
                "justification": case["reason"],
            }
        )
    return record


def summaries(rows):
    result = {}
    for cfg in ("B1", "C1"):
        result[cfg] = {}
        for k in (3, 5):
            result[cfg][str(k)] = {}
            for view in ("raw", "budget"):
                selected = [
                    x
                    for x in rows
                    if x["configuration"] == cfg and x["k"] == k and x["view"] == view
                ]
                positives = [x for x in selected if x["status"] == "answerable"]
                absent = [x for x in selected if x["status"] == "absent"]
                citations = [c for x in selected for c in x["citations"]]
                judged = [
                    c for c in citations if c["semantic_status"] not in ("unjudged",)
                ]
                supported = [
                    c for c in judged if c["semantic_status"] == "supports_anchor"
                ]
                q10 = next(x for x in positives if x["question_id"] == "Q10")
                result[cfg][str(k)][view] = {
                    "positive_n": len(positives),
                    "positive_total": 11,
                    "recall_sum": sum(x["recall"] for x in positives),
                    "recall_mean": sum(x["recall"] for x in positives) / len(positives),
                    "mrr_sum": sum(x["reciprocal_rank"] for x in positives),
                    "mrr_mean": sum(x["reciprocal_rank"] for x in positives)
                    / len(positives),
                    "anchors_covered": sum(x["anchor_coverage"] for x in positives),
                    "anchors_total": 15,
                    "fully_sufficient": sum(x["fully_sufficient"] for x in positives),
                    "partial": sum(x["partial"] for x in positives),
                    "multi_anchor_full": sum(
                        x["fully_sufficient"]
                        for x in positives
                        if x["anchor_total"] > 1
                    ),
                    "multi_anchor_total": sum(x["anchor_total"] > 1 for x in positives),
                    "positive_abstentions": sum(
                        x["state"] == "abstained" for x in positives
                    ),
                    "absent_total": len(absent),
                    "absent_returned": sum(x["state"] == "returned" for x in absent),
                    "absent_abstained": sum(x["state"] == "abstained" for x in absent),
                    "absent_related_insufficient_queries": sum(
                        x["related_insufficient_returns"] > 0 for x in absent
                    ),
                    "citations_total": len(citations),
                    "citations_resolvable": sum(c["resolvable"] for c in citations),
                    "citations_judged": len(judged),
                    "citations_supporting_anchor": len(supported),
                    "citations_unjudged": len(citations) - len(judged),
                    "q10_covered": q10["anchor_coverage"],
                    "q10_total": q10["anchor_total"],
                    "q10_complete": q10["fully_sufficient"],
                }
    return result


def performance():
    rows = read(OUT / "measurements.json")
    out = {}
    for cfg in ("B1", "C1"):
        out[cfg] = {}
        for stage, cutoff in (
            ("index", None),
            ("query", None),
            ("query", 3),
            ("query", 5),
        ):
            group = [
                x
                for x in rows
                if x["configuration"] == cfg
                and x["stage"] == stage
                and x["phase"] == "measured"
                and (cutoff is None or x.get("k") == cutoff)
            ]
            if not group or any(x["status"] != "ok" for x in group):
                raise ValueError("Medição incompleta")
            label = stage if cutoff is None else f"{stage}_k{cutoff}"
            out[cfg][label] = {
                "n": len(group),
                "wall_mean_seconds": statistics.mean(x["wall_seconds"] for x in group),
                "wall_min_seconds": min(x["wall_seconds"] for x in group),
                "wall_max_seconds": max(x["wall_seconds"] for x in group),
                "cpu_mean_seconds": statistics.mean(x["cpu_seconds"] for x in group),
                "memory_peak_max_bytes": max(x["memory_peak_bytes"] for x in group),
                "operation_mean_seconds": statistics.mean(
                    x["operation_seconds"] for x in group
                ),
            }
    return out


def main():
    judge.verify_rankings()
    review = read(OUT / "semantic-review.json")
    if review["ranking_freeze_sha256"] != sha(OUT / "ranking-freeze.json"):
        raise ValueError("Revisão não corresponde ao ranking congelado")
    provenance = read(OUT / "provenance.json")
    rankings = read(OUT / "rankings.json")
    measurements = read(OUT / "measurements.json")
    if len(rankings) != 52 or len(measurements) != 216:
        raise ValueError("Rankings ou medições incompletos")
    failures = sum(item["status"] != "ok" for item in measurements)
    rows = []
    for row in rankings:
        case = review["configurations"][row["configuration"]][row["question_id"]]
        for kind in ("raw", "budget"):
            rows.append(evaluate_row(row, case, provenance, kind))
    result = {
        "review": "Autorrevisão semântica do executor baseada na STORY-062; aceite do PO pendente.",
        "ranking_freeze_sha256": sha(OUT / "ranking-freeze.json"),
        "semantic_review_sha256": sha(OUT / "semantic-review.json"),
        "summaries": summaries(rows),
        "individual": rows,
        "performance": performance(),
        "technical_failures": failures,
    }
    (OUT / "evaluation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for cfg, byk in result["summaries"].items():
        for k, views in byk.items():
            m = views["raw"]
            print(
                cfg,
                "k",
                k,
                "Recall",
                m["recall_sum"],
                "/11",
                "MRR",
                m["mrr_sum"],
                "/11",
                "full",
                m["fully_sufficient"],
                "/11",
                "citações",
                m["citations_resolvable"],
                "/",
                m["citations_total"],
            )


if __name__ == "__main__":
    main()
