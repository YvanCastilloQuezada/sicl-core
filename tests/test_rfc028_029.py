from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from sicl.copilot import OllamaCopilot
from sicl.gis import ingest_geojson


def feature():
    return {"type": "Feature", "id": "PE-TRU-001", "properties": {"district": "Trujillo"}, "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]}}


def test_geojson_parcel_is_parcela_sitio_and_review_required():
    item = ingest_geojson(feature(), "P-001", "https://example.gob.pe/ogc/parcels", jurisdiction="PE-TRUJILLO")
    assert item.spatial_scope.value == "parcela_sitio"
    assert item.review_state == "HUMAN_REVIEW_REQUIRED"
    assert item.response_hash.startswith("sha256:")


def test_geojson_requires_parcel_identifier():
    payload = feature()
    del payload["id"]
    payload["properties"] = {}
    with pytest.raises(ValueError, match="parcel_id"):
        ingest_geojson(payload, "P-001", "https://example.gob.pe/ogc/parcels")


def test_ollama_is_preview_only():
    response = {"choices": [{"message": {"content": json.dumps({"command": "/PROJECT CREATE P-001 Vivienda", "explanation": "Crea un proyecto", "confidence": 0.9})}}]}
    class FakeResponse:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return json.dumps(response).encode()
    with patch("urllib.request.urlopen", return_value=FakeResponse()):
        intent = OllamaCopilot("http://localhost:11434").translate_preview("crea una vivienda")
    assert intent.command.startswith("/")
    assert intent.executed is False
    assert intent.decision_created is False


def test_ollama_not_configured():
    with pytest.raises(RuntimeError, match="COPILOT_NOT_CONFIGURED"):
        OllamaCopilot("").translate_preview("crea un proyecto")
