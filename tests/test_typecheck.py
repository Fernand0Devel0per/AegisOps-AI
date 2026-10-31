"""Protege a configuração de erro para anotações deprecadas do typeshed."""

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("annotation", "expected_exit"),
    [("AsyncIterator[None]", 1), ("AsyncGenerator[None, None]", 0)],
)
def test_async_context_manager_deprecation(
    tmp_path: Path, annotation: str, expected_exit: int
) -> None:
    source = tmp_path / "sample.py"
    source.write_text(
        "from collections.abc import AsyncGenerator, AsyncIterator\n"
        "from contextlib import asynccontextmanager\n\n"
        "@asynccontextmanager\n"
        f"async def example() -> {annotation}:\n"
        "    yield\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "pyright", "--project", str(PROJECT), str(source)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == expected_exit, result.stdout + result.stderr
    if expected_exit:
        assert "reportDeprecated" in result.stdout
        assert "asynccontextmanager" in result.stdout
    else:
        assert "reportDeprecated" not in result.stdout
