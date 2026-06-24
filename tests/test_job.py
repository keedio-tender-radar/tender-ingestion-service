from tender_ingestion.connectors.placsp_connector import PlacspConnector
from tender_ingestion.connectors.ted_connector import TedConnector
from tender_ingestion.jobs.daily_ingestion_job import (
    FilterConfig,
    Source,
    run_ingestion,
)
from tender_ingestion.normalizers import placsp_normalizer, ted_normalizer

CFG = FilterConfig(
    cpv_preferred=["72", "48"],
    cpv_excluded=["45", "90"],
    keywords_positive=["datos", "integración", "inteligencia artificial", "api"],
    keywords_negative=["obra", "construcción", "mobiliario"],
)


class FakeApi:
    def __init__(self):
        self.published = []

    def publish(self, payload):
        self.published.append(payload)
        return {"id": payload.source_id}


def _sources(monkeypatch, placsp_atom, ted_json) -> list[Source]:
    placsp = PlacspConnector("x")
    monkeypatch.setattr(placsp, "fetch_raw", lambda: placsp_atom)
    ted = TedConnector("x")
    monkeypatch.setattr(ted, "fetch_raw", lambda: ted_json)
    return [
        Source(placsp, placsp_normalizer.normalize),
        Source(ted, ted_normalizer.normalize),
    ]


def test_full_ingestion_filters_and_publishes(monkeypatch, placsp_atom, ted_json):
    api = FakeApi()
    result = run_ingestion(_sources(monkeypatch, placsp_atom, ted_json), api, CFG)

    assert result.fetched == 4
    # Relevantes: plataforma de datos (PLACSP) + integración/IA (TED)
    assert result.published == 2
    assert result.relevant == 2
    # Filtradas: obra civil (CPV 45) + mobiliario (CPV 39 sin match / keyword negativa)
    assert result.filtered_out == 2
    assert result.errors == []

    ids = {p.source_id for p in api.published}
    assert ids == {"PLACSP-2026-000184", "430921-2026"}


def test_connector_error_is_isolated(monkeypatch, ted_json):
    bad = PlacspConnector("x")
    monkeypatch.setattr(bad, "fetch_raw", lambda: (_ for _ in ()).throw(RuntimeError("down")))
    ted = TedConnector("x")
    monkeypatch.setattr(ted, "fetch_raw", lambda: ted_json)

    api = FakeApi()
    result = run_ingestion(
        [Source(bad, placsp_normalizer.normalize), Source(ted, ted_normalizer.normalize)],
        api,
        CFG,
    )
    # El conector caído no impide procesar el otro.
    assert any("placsp" in e for e in result.errors)
    assert result.published == 1


def test_duplicates_counted(monkeypatch, ted_json):
    # Mismo feed TED en dos fuentes → la segunda copia es duplicada.
    ted1 = TedConnector("x")
    monkeypatch.setattr(ted1, "fetch_raw", lambda: ted_json)
    ted2 = TedConnector("y")
    monkeypatch.setattr(ted2, "fetch_raw", lambda: ted_json)

    api = FakeApi()
    result = run_ingestion(
        [Source(ted1, ted_normalizer.normalize), Source(ted2, ted_normalizer.normalize)],
        api,
        CFG,
    )
    assert result.duplicates == 2  # las 2 entradas del segundo feed
    assert result.published == 1  # solo la relevante del primero
