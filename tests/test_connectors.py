import pytest

from tender_ingestion.connectors.placsp_connector import PlacspAccessError, PlacspConnector
from tender_ingestion.connectors.ted_connector import TedConnector

_PLACSP_ERROR_PAGE = (
    '<html><head><meta http-equiv="refresh" content="5;url=http://contrataciondelestado.es"></head>'
    "<body><h2>Su certificado no está autorizado a acceder a la Plataforma.</h2>"
    "<p>Se ha producido un error de acceso. Redireccionando...</p></body></html>"
)


def test_placsp_rejects_non_atom_access_error():
    with pytest.raises(PlacspAccessError) as exc:
        PlacspConnector("x").parse(_PLACSP_ERROR_PAGE)
    assert "acceso no autorizado" in str(exc.value)


def test_placsp_rejects_plain_html():
    with pytest.raises(PlacspAccessError):
        PlacspConnector("x").parse("<html><body>algo</body></html>")


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
