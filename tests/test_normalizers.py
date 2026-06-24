from datetime import date, datetime

from tender_ingestion.connectors.placsp_connector import PlacspConnector
from tender_ingestion.connectors.ted_connector import TedConnector
from tender_ingestion.normalizers import common_normalizer as cn
from tender_ingestion.normalizers import placsp_normalizer, ted_normalizer


def test_placsp_normalize(placsp_atom):
    raw = PlacspConnector("x").parse(placsp_atom)[0]
    p = placsp_normalizer.normalize(raw)
    assert p.source == "placsp"
    assert p.source_id == "PLACSP-2026-000184"
    assert p.budget_amount == 620000.0
    assert p.cpv == ["72300000"]
    assert p.deadline == datetime(2026, 7, 15, 0, 0)
    assert p.publication_date == date(2026, 6, 20)


def test_ted_normalize(ted_json):
    raw = TedConnector("x").parse(ted_json)[0]
    p = ted_normalizer.normalize(raw)
    assert p.source == "ted"
    assert p.source_id == "430921-2026"
    assert p.budget_amount == 280000.0
    assert p.cpv == ["72200000"]  # dedupe del normalizador
    assert p.publication_date == date(2026, 6, 24)
    assert p.deadline is None  # TED v3 no expone plazo a nivel de nota


def test_to_float_european_format():
    assert cn.to_float("1.234.567,89") == 1234567.89
    assert cn.to_float("280000") == 280000.0
    assert cn.to_float("620.000,00 €") == 620000.0
    assert cn.to_float(None) is None


def test_clean_cpv():
    assert cn.clean_cpv(["72300000", "72300000", "abc45000000"]) == ["72300000", "45000000"]
