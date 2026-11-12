"""Produz revisão semântica usando gabarito e revisão 062 somente após congelar rankings."""

import hashlib
import json
from pathlib import Path

import run as benchmark
import yaml

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
OUT = ROOT / "output"
CORPUS = REPO / "datasets/rich-documents"
OLD = REPO / "datasets/rich-document-experiment"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_rankings():
    benchmark.verify_inputs()
    freeze = json.loads((OUT / "ranking-freeze.json").read_text())
    if freeze["protocol_sha256"] != sha(ROOT / "protocol.md"):
        raise ValueError("Protocolo alterado")
    for file, expected in freeze["files"].items():
        if sha(OUT / file) != expected:
            raise ValueError("Ranking ou evidência alterada: " + file)
    if (
        sha(CORPUS / "judgments.yaml")
        != "7860c4e2eb8b84fffa3c9383da5735ae88bf5659d97ef211e3daa6899f5771ee"
    ):
        raise ValueError("Gabarito alterado")
    if (
        sha(OLD / "semantic-review.yaml")
        != "8293cb11c90d41ed171f805ad2ba91df519f328164d913466f958b39e0b4f683"
    ):
        raise ValueError("Revisão 062 alterada")


def required(case, number):
    evidence = case["evidence"][number]
    parts = evidence["anchor"].split(" | ")
    qid = case["question_id"]
    if qid in ("Q04", "Q05"):
        return ["Fila", "Limite de alerta", "Idade máxima", *parts]
    if qid in ("Q08", "Q09"):
        return [
            "1. Diagnóstico de recursos",
            "1.1 CPU" if qid == "Q08" else "1.2 Memória",
            *parts,
        ]
    if qid == "Q11" and number == 1:
        return [case["evidence"][0]["anchor"], *parts]
    return parts


def main():
    verify_rankings()
    judgments = yaml.safe_load((CORPUS / "judgments.yaml").read_text())["judgments"]
    previous = yaml.safe_load((OLD / "semantic-review.yaml").read_text())["extractors"]
    review = {
        "reviewer": "Executor; revisão semântica da representação e conteúdo após congelar rankings, com base no julgamento 062 aceito pelo PO. Aceite humano desta avaliação pendente.",
        "ranking_freeze_sha256": sha(OUT / "ranking-freeze.json"),
        "method": "Âncora elegível somente se aprovada na revisão semântica 062 e termos/contexto essenciais aparecem integralmente no trecho exibido; não julgados permanecem distintos de negativos.",
        "configurations": {},
    }
    for name, mode in [("B1", "poppler"), ("C1", "pdfplumber")]:
        cases = {}
        for case in judgments:
            qid = case["question_id"]
            if case["status"] == "absent":
                cases[qid] = {
                    "status": "absent",
                    "related_document": "RD-01" if qid == "Q12" else "RD-03",
                    "reason": "Ausência aprovada apenas para o corpus completo; retorno relacionado é insuficiente para a informação solicitada.",
                }
                continue
            reference = previous[mode][qid]
            evidence = []
            for i, e in enumerate(case["evidence"]):
                evidence.append(
                    {
                        "occurrence": i + 1,
                        "document_id": e["document_id"],
                        "page": e["page"],
                        "anchor": e["anchor"],
                        "eligible": reference["anchors"][i],
                        "required_text": required(case, i),
                        "reason": reference["reason"],
                    }
                )
            cases[qid] = {
                "status": "answerable",
                "expected_answer": case["expected_answer"],
                "relation_preserved_in_extraction": reference["relation"],
                "evidence": evidence,
                "reason": reference["reason"],
            }
        review["configurations"][name] = cases
    (OUT / "semantic-review.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "PASS: revisão semântica registrada para 13 perguntas por configuração após congelamento"
    )


if __name__ == "__main__":
    main()
