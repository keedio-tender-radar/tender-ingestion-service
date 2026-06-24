from tender_ingestion.filters import cpv_filter, keyword_filter
from tender_ingestion.filters.duplicate_filter import DuplicateFilter
from tender_ingestion.types import TenderPayload

PREF = ["72", "48"]
EXCL = ["45", "90"]
POS = ["datos", "integración", "api"]
NEG = ["obra", "construcción", "mobiliario"]


def _p(**kw) -> TenderPayload:
    base = {"source": "placsp", "source_id": "1", "title": "t"}
    base.update(kw)
    return TenderPayload(**base)


def test_cpv_preferred_match():
    assert cpv_filter.passes(_p(cpv=["72300000"]), PREF, EXCL) is True


def test_cpv_excluded():
    assert cpv_filter.passes(_p(cpv=["45000000"]), PREF, EXCL) is False


def test_cpv_no_match_when_preferred_required():
    assert cpv_filter.passes(_p(cpv=["50000000"]), PREF, EXCL) is False


def test_cpv_empty_is_neutral():
    assert cpv_filter.passes(_p(cpv=[]), PREF, EXCL) is True


def test_keyword_positive():
    assert keyword_filter.passes(_p(title="Plataforma de datos"), POS, NEG) is True


def test_keyword_negative_only_rejected():
    assert keyword_filter.passes(_p(title="Obra civil de construcción"), POS, NEG) is False


def test_keyword_neutral_rejected():
    assert keyword_filter.passes(_p(title="Servicio genérico"), POS, NEG) is False


def test_duplicate_filter():
    dedupe = DuplicateFilter()
    p = _p(source_id="A")
    assert dedupe.is_new(p) is True
    assert dedupe.is_new(p) is False
    assert dedupe.is_new(_p(source_id="B")) is True
