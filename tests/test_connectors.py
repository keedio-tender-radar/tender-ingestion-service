from tender_ingestion.connectors.placsp_connector import PlacspConnector
from tender_ingestion.connectors.ted_connector import TedConnector


def test_placsp_parse(placsp_atom):
    rows = PlacspConnector("x").parse(placsp_atom)
    assert len(rows) == 2
    first = rows[0]
    assert first["source_id"] == "PLACSP-2026-000184"
    assert first["title"].startswith("Plataforma de datos")
    assert first["cpv"] == ["72300000"]
    assert first["budget_amount"] == "620.000,00"
    assert first["deadline"] == "2026-07-15"
    assert first["buyer"] == "Servicio de Salud de la Comunidad"
    assert first["url"].endswith("PLACSP-2026-000184")


def test_ted_parse(ted_json):
    rows = TedConnector("x").parse(ted_json)
    assert len(rows) == 2
    assert rows[0]["source_id"] == "2026-OJS-000123"
    assert rows[0]["cpv"] == ["72200000"]
    assert rows[0]["budget_amount"] == 280000


def test_connector_fetch_uses_fetch_raw(monkeypatch, ted_json):
    conn = TedConnector("x")
    monkeypatch.setattr(conn, "fetch_raw", lambda: ted_json)
    rows = conn.fetch()
    assert len(rows) == 2
