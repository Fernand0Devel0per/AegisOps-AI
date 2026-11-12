"""Testes proporcionais do adaptador lexical e do corte de contexto."""

import unittest

import adapter


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            {"id": "B", "text": "Ação ação CPU"},
            {"id": "A", "text": "acao cpu"},
        ]
        self.index = adapter.build(self.records, adapter.digest(self.records))

    def test_nfkd_casefold_and_tokens(self):
        self.assertEqual(
            adapter.tokens("AÇÂO ação Straße ﬃ"), {"acao", "strasse", "ffi"}
        )

    def test_score_is_distinct_and_ties_are_sorted(self):
        result = adapter.search(self.index, "ACAO ação cpu", 2)
        self.assertEqual(
            [(x["id"], x["score"]) for x in result["hits"]], [("A", 2), ("B", 2)]
        )

    def test_invalid_queries_and_k(self):
        for query, k in [
            ("", 1),
            ("---", 1),
            (None, 1),
            ("x" * 4097, 1),
            ("cpu", 0),
            ("cpu", 6),
            ("cpu", True),
        ]:
            with (
                self.subTest(query=query, k=k),
                self.assertRaises(adapter.InvalidQuery),
            ):
                adapter.search(self.index, query, k)

    def test_abstention(self):
        self.assertEqual(
            adapter.search(self.index, "zzzzsemtermo", 5),
            {"state": "abstained", "hits": []},
        )

    def test_corrupt_hash_and_duplicate(self):
        with self.assertRaises(adapter.CorpusError):
            adapter.build(self.records, "0" * 64)
        records = [self.records[0], self.records[0]]
        with self.assertRaises(adapter.CorpusError):
            adapter.build(records, adapter.digest(records))

    def test_budget_counts_header_and_unicode(self):
        hits = [{"id": "X", "score": 1, "text": "açãoç"}]
        result = adapter.apply_budget(hits, 8)
        self.assertEqual(result["used"], 8)
        self.assertEqual(result["chunks"][0]["text"], "ação")
        self.assertTrue(result["chunks"][0]["truncated"])

    def test_budget_exact_boundary_and_header(self):
        hits = [
            {"id": "A", "score": 1, "text": "1234"},
            {"id": "B", "score": 1, "text": "xyz"},
        ]
        result = adapter.apply_budget(hits, 8)
        self.assertEqual(result["used"], 8)
        self.assertEqual(len(result["chunks"]), 1)
        self.assertFalse(result["chunks"][0]["truncated"])

    def test_budget_rejects_invalid_limit(self):
        with self.assertRaises(ValueError):
            adapter.apply_budget([], True)


class FrozenEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import json
        from pathlib import Path

        import evaluate
        import judge

        cls.evaluate = evaluate
        cls.root = Path(__file__).resolve().parent / "output"
        judge.verify_rankings()
        cls.ranking = json.loads((cls.root / "rankings.json").read_text())
        cls.evaluation = json.loads((cls.root / "evaluation.json").read_text())

    def test_executed_code_hashes_and_equivalence(self):
        import hashlib
        import json

        root = self.root.parent
        env = json.loads((self.root / "environment.json").read_text())
        for key, filename in (
            ("protocol_sha256", "protocol.md"),
            ("adapter_sha256", "adapter.py"),
            ("worker_sha256", "ranker_worker.py"),
            ("controller_sha256", "run.py"),
        ):
            self.assertEqual(
                hashlib.sha256((root / filename).read_bytes()).hexdigest(), env[key]
            )
        equivalence = json.loads((self.root / "equivalence-c1.json").read_text())
        self.assertEqual(equivalence["result"]["status"], "pass")
        self.assertEqual(
            hashlib.sha256(
                (self.root / "equivalence-c1.json").read_bytes()
            ).hexdigest(),
            env["equivalence_sha256"],
        )

    def test_all_rankings_and_budget_integrity(self):
        self.assertEqual(len(self.ranking), 52)
        for row in self.ranking:
            self.assertLessEqual(len(row["hits"]), row["k"])
            self.assertLessEqual(row["context"]["used"], 1800)
            self.assertEqual(
                row["context"]["used"],
                sum(
                    len(c["header"]) + len(c["text"]) for c in row["context"]["chunks"]
                ),
            )
            self.assertTrue(
                all(c["header"] == f"[{c['id']}]\n" for c in row["context"]["chunks"])
            )

    def test_top3_is_prefix_of_top5(self):
        for cfg in ("B1", "C1"):
            for q in (f"Q{i:02}" for i in range(1, 14)):
                low = next(
                    x
                    for x in self.ranking
                    if x["configuration"] == cfg
                    and x["question_id"] == q
                    and x["k"] == 3
                )
                high = next(
                    x
                    for x in self.ranking
                    if x["configuration"] == cfg
                    and x["question_id"] == q
                    and x["k"] == 5
                )
                self.assertEqual(low["hits"], high["hits"][:3])

    def test_truncation_does_not_cover_cut_anchor(self):
        evidence = {
            "eligible": True,
            "document_id": "RD-01",
            "page": 1,
            "required_text": ["Título", "valor completo"],
        }
        ref = {"document_id": "RD-01", "page": 1}
        self.assertFalse(self.evaluate.covered(evidence, ref, "Título: valor comp"))
        self.assertTrue(self.evaluate.covered(evidence, ref, "Título: valor completo"))
        evidence["eligible"] = False
        self.assertFalse(self.evaluate.covered(evidence, ref, "Título: valor completo"))

    def test_cross_page_coverage_and_unjudged(self):
        rows = self.evaluation["individual"]
        for cfg in ("B1", "C1"):
            low = next(
                x
                for x in rows
                if x["configuration"] == cfg
                and x["question_id"] == "Q10"
                and x["k"] == 3
                and x["view"] == "raw"
            )
            high = next(
                x
                for x in rows
                if x["configuration"] == cfg
                and x["question_id"] == "Q10"
                and x["k"] == 5
                and x["view"] == "raw"
            )
            self.assertEqual(low["anchor_coverage"], 1)
            self.assertFalse(low["fully_sufficient"])
            self.assertEqual(high["anchor_coverage"], 2)
            self.assertTrue(high["fully_sufficient"])
            self.assertEqual(
                {
                    c["page"]
                    for c in high["citations"]
                    if c["semantic_status"] == "supports_anchor"
                },
                {1, 2},
            )
            self.assertIn("unjudged", {c["semantic_status"] for c in high["citations"]})

    def test_citations_are_resolvable_and_evidence_distinct(self):
        rows = self.evaluation["individual"]
        self.assertEqual(len(rows), 104)
        self.assertTrue(all(c["resolvable"] for row in rows for c in row["citations"]))
        for cfg in ("B1", "C1"):
            for q in ("Q12", "Q13"):
                row = next(
                    x
                    for x in rows
                    if x["configuration"] == cfg
                    and x["question_id"] == q
                    and x["k"] == 5
                    and x["view"] == "raw"
                )
                self.assertEqual(row["status"], "absent")
                self.assertEqual(row["related_insufficient_returns"], 1)
                self.assertTrue(
                    any(c["semantic_status"] == "unjudged" for c in row["citations"])
                )


if __name__ == "__main__":
    unittest.main()
