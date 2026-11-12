#!/usr/bin/env python3
"""Testes proporcionais da política de offsets, limites e erros, com dados sintéticos."""

import hashlib
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


chunk = load("chunk_worker")
worker = load("worker")


class ChunkTests(unittest.TestCase):
    def test_fixed_offsets_and_overlap(self):
        text = "x" * 1201
        spans = chunk.fixed(text)
        self.assertEqual(spans, [(0, 600), (500, 1100), (1000, 1201)])
        self.assertTrue(all(len(text[a:b]) <= 600 for a, b in spans))

    def test_fixed_exact_boundary_does_not_add_duplicate(self):
        self.assertEqual(chunk.fixed("x" * 600), [(0, 600)])

    def test_structural_preserves_lines_and_offsets(self):
        page = {
            "tables": [],
            "text": "primeira linha\nsegunda linha",
            "lines": [
                {"text": "primeira linha", "bbox": [0, 0, 10, 1]},
                {"text": "segunda linha", "bbox": [0, 2, 10, 3]},
            ],
        }
        self.assertEqual(chunk.structural(page), [(0, len(page["text"]))])

    def test_structural_fails_closed_on_missing_units(self):
        page = {
            "tables": [],
            "text": "linha segredo",
            "lines": [{"text": "linha", "bbox": [0, 0, 1, 1]}],
        }
        with self.assertRaises(ValueError):
            chunk.structural(page)

    def test_structural_divides_long_unit_deterministically(self):
        page = {
            "tables": [],
            "text": "x" * 1201,
            "lines": [{"text": "x" * 1201, "bbox": [0, 0, 1, 1]}],
        }
        self.assertEqual(chunk.structural(page), [(0, 600), (600, 1200), (1200, 1201)])

    def test_table_rows_stay_together_when_they_fit(self):
        first = "x" * 590
        rows = ["header", "row one", "row two"]
        text = first + "\n" + "\n".join(rows)
        lines = [{"text": first, "bbox": [0, 0, 1, 1]}] + [
            {"text": row, "bbox": [1, i, 9, i + 0.5]} for i, row in enumerate(rows, 2)
        ]
        page = {"text": text, "lines": lines, "tables": [{"bbox": [0, 1.5, 10, 6]}]}
        spans = chunk.structural(page)
        self.assertEqual(len(spans), 2)
        self.assertEqual(text[spans[1][0] : spans[1][1]], "\n".join(rows))

    def test_frozen_output_hashes_and_chunk_provenance(self):
        output = ROOT / "output"
        for name in ("extraction-freeze.json", "chunk-freeze.json"):
            index = json.loads((output / name).read_text())
            self.assertTrue(index["files"])
            for relative, digest in index["files"].items():
                self.assertEqual(
                    hashlib.sha256((output / relative).read_bytes()).hexdigest(), digest
                )
        for path in (output / "chunks").glob("*/*/*.json"):
            doc = json.loads(path.read_text())
            source = json.loads(
                (output / "extractions" / doc["extractor"] / path.name).read_text()
            )
            pages = {p["page"]: p["text"] for p in source["pages"]}
            self.assertLessEqual(len(doc["chunks"]), 200)
            for c in doc["chunks"]:
                self.assertEqual(c["text"], pages[c["page"]][c["start"] : c["end"]])
                self.assertLessEqual(len(c["text"]), 600)

    def test_recorded_code_and_protocol_hashes(self):
        inventory = json.loads((ROOT / "output/dependency-inventory.json").read_text())
        for name, expected in inventory["files_sha256"].items():
            self.assertEqual(
                hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected
            )

    def test_isolation_failures_are_recorded(self):
        report = json.loads((ROOT / "output/failure-probes.json").read_text())
        self.assertEqual(report["failure"]["status"], "failed")
        self.assertEqual(report["failure"]["returncode"], 7)
        self.assertEqual(report["timeout"]["status"], "timeout")
        self.assertGreaterEqual(report["timeout"]["wall_seconds"], 30)

    def test_native_table_and_no_false_section_metadata(self):
        output = ROOT / "output"
        extracted = json.loads(
            (output / "extractions/pdfplumber/RD-02.json").read_text()
        )
        rows = extracted["pages"][0]["tables"][0]["rows"]
        self.assertEqual(rows[0], ["Fila", "Limite de alerta", "Idade máxima"])
        self.assertEqual(rows[1], ["Vega", "120 mensagens", "8 minutos"])
        self.assertEqual(rows[2], ["Lyra", "75 mensagens", "15 minutos"])
        for path in (output / "chunks").glob("*/*/*.json"):
            for part in json.loads(path.read_text())["chunks"]:
                self.assertIsNone(part["section"])
                self.assertEqual(part["section_status"], "not_extracted")

    def test_chunk_limit_rejects_excess(self):
        source = {
            "document_id": "RD-X",
            "extractor": "test",
            "pages": [{"page": 1, "text": "x" * 100601}],
        }
        fake_fs = SimpleNamespace(f_blocks=1, f_frsize=4096)
        with (
            patch("builtins.open", return_value=io.StringIO(json.dumps(source))),
            patch.object(chunk.sys, "argv", ["chunk_worker", "fixed"]),
            patch.object(chunk.os, "statvfs", return_value=fake_fs),
            patch.object(chunk.os, "sched_getaffinity", return_value={0}),
            patch.object(chunk.socket, "if_nameindex", return_value=[(1, "lo")]),
            self.assertRaisesRegex(ValueError, "Limite de chunks excedido"),
        ):
            chunk.main()

    def test_text_cap_rejects_overflow(self):
        with self.assertRaises(ValueError):
            worker.read_limited([sys.executable, "-c", 'print("x"*1000)'], 100)


if __name__ == "__main__":
    unittest.main()
