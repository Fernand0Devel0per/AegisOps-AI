"""Verifica se o pacote distribuído foi instalado no ambiente de teste."""

import sys
from importlib.metadata import version
from pathlib import Path

import aegisops


def test_package_is_installed_in_active_environment() -> None:
    assert version("aegisops-ai") == "0.0.0"
    assert aegisops.__file__ is not None
    assert Path(aegisops.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
