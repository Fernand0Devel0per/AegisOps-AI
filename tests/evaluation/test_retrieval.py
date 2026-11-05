"""Contratos da busca local e dos recursos instalados."""

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

from aegisops import retrieval
from aegisops.retrieval import CorpusError, InvalidQuery, Passage, retrieve


def passage(identifier: str, text: str) -> Passage:
    return Passage(identifier, "path", "version", "hash", "source", "version", text, 0)


def test_ranking_distinct_terms_ties_normalization_and_limits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        retrieval,
        "_load_passages",
        lambda: (
            passage("B", "CPU cpu memória"),
            passage("A", "cpu memoria"),
            passage("C", "cpu"),
        ),
    )
    result = retrieve("CPU CPU MEMÓRIA", 2)
    assert [(p.id, p.score) for p in result.passages] == [("A", 2), ("B", 2)]
    assert result.state == "returned"
    assert [p.id for p in retrieve("cpu", 5).passages] == ["A", "B", "C"]
    assert retrieve("unmatchedtoken").state == "abstained"
    assert retrieve("unmatchedtoken").passages == ()


@pytest.mark.parametrize(
    "query,k", [("", 5), ("!!!", 5), ("x" * 4097, 5), ("x", 0), ("x", 6), ("x", True)]
)
def test_invalid_input(query: str, k: int) -> None:
    with pytest.raises(InvalidQuery):
        retrieve(query, k)


def test_all_citations_resolve_and_hash_matches() -> None:
    for p in retrieval._load_passages():
        data = retrieval._read_resource(p.path.rsplit("/", 1)[-1])
        assert hashlib.sha256(data).hexdigest() == p.sha256
        assert p.corpus_version == retrieval.CORPUS_VERSION
        assert p.source_url and p.source_version and p.text in data.decode()


@pytest.mark.parametrize("failure", ["missing", "altered", "source", "version"])
def test_bad_or_missing_data_is_not_abstention(
    monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    original = retrieval._read_resource
    if failure == "missing":

        def broken(name: str) -> bytes:
            raise FileNotFoundError(name)

        monkeypatch.setattr(retrieval, "_read_resource", broken)
    elif failure == "altered":
        monkeypatch.setattr(
            retrieval, "_read_resource", lambda name: original(name) + b"altered"
        )
    else:
        units = list(retrieval._UNITS)
        item = list(units[0])
        item[3 if failure == "source" else 4] = "incorrect"
        units[0] = (item[0], item[1], item[2], item[3], item[4], item[5])
        monkeypatch.setattr(retrieval, "_UNITS", tuple(units))
    with pytest.raises(CorpusError):
        retrieve("unmatchedtoken")


def test_installed_resources_from_other_directory(tmp_path: Path) -> None:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from aegisops.retrieval import retrieve; assert retrieve('cpu').passages",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
