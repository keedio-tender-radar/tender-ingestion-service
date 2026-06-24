from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def placsp_atom() -> str:
    return (FIXTURES / "placsp.atom").read_text(encoding="utf-8")


@pytest.fixture
def ted_json() -> str:
    return (FIXTURES / "ted.json").read_text(encoding="utf-8")
