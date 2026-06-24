"""Conector TED (Tenders Electronic Daily, UE).

La API de TED devuelve notices en JSON. Este parser acepta la forma `{"notices": [...]}` y
mapea los campos habituales de forma defensiva (los nombres exactos varían por versión de la
API; se cubren varios alias).
"""

from __future__ import annotations

import json

from .base_connector import BaseConnector


def _pick(d: dict, *keys: str):
    for k in keys:
        if k in d and d[k] not in (None, "", []):
            return d[k]
    return None


def _as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)]


class TedConnector(BaseConnector):
    name = "ted"

    def parse(self, raw: str) -> list[dict]:
        data = json.loads(raw)
        notices = data.get("notices") or data.get("results") or []
        results: list[dict] = []
        for n in notices:
            results.append(
                {
                    "source_id": str(_pick(n, "publication-number", "ND", "id") or ""),
                    "title": str(_pick(n, "title", "TI") or "").strip(),
                    "summary": _pick(n, "description", "summary"),
                    "url": _pick(n, "links_self", "uri", "url"),
                    "cpv": _as_list(_pick(n, "classification-cpv", "cpv", "PC")),
                    "budget_amount": _pick(n, "total-value", "value", "amount"),
                    "deadline": _pick(n, "deadline-receipt-tender", "deadline", "DT"),
                    "buyer": _pick(n, "buyer-name", "organisation", "AA"),
                }
            )
        return results
