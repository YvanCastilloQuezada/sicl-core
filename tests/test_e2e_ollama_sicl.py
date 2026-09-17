from __future__ import annotations

import json
import os
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.repository import SQLiteRepository


def test_ollama_to_sicl_e2e_is_preview_only():
    repo = SQLiteRepository(":memory:", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    client = TestClient(app)
    try:
        created = client.post("/projects", json={"project_id": "E2E-OLLAMA-001", "name": "Ollama E2E", "actor": "e2e"})
        assert created.status_code == 201

        ollama_response = {
            "choices": [{"message": {"content": json.dumps({
                "command": "/PROJECT OPEN E2E-OLLAMA-001",
                "explanation": "Abre el proyecto solicitado.",
                "confidence": 0.98,
            })}}]
        }

        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return json.dumps(ollama_response).encode()

        with patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://ollama.test"}, clear=False), patch("urllib.request.urlopen", return_value=FakeResponse()):
            translated = client.post("/v1/copilot/translate", json={"text": "abre el proyecto E2E-OLLAMA-001"})

        assert translated.status_code == 200
        body = translated.json()
        intent = body["data"]["intent"]
        assert intent["command"] == "/PROJECT OPEN E2E-OLLAMA-001"
        assert intent["status"] == "PREVIEW_ONLY"
        assert intent["executed"] is False
        assert body["data"]["decision_created"] is False
        assert repo.get_project("E2E-OLLAMA-001") is not None
        assert repo.get_project("E2E-OLLAMA-001") is not None
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_gis_snapshot_survives_e2e_request_and_token_is_not_returned():
    repo = SQLiteRepository(":memory:", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    client = TestClient(app)
    try:
        client.post("/projects", json={"project_id": "E2E-GIS-001", "name": "GIS E2E", "actor": "e2e"})
        response = client.post("/v1/projects/E2E-GIS-001/gis/parcel-snapshots", json={
            "feature": {"type": "Feature", "id": "PARCEL-001", "properties": {"district": "Trujillo"}, "geometry": {"type": "Point", "coordinates": [0, 0]}},
            "source_url": "https://example.test/ogc/parcels",
            "jurisdiction": "PE-TRUJILLO",
        })
        assert response.status_code == 200
        listed = client.get("/v1/projects/E2E-GIS-001/gis/parcel-snapshots")
        assert listed.status_code == 200
        assert listed.json()["data"]["snapshots"][0]["parcel_id"] == "PARCEL-001"
        assert "SICL_CORE_SERVICE_TOKEN" not in response.text
    finally:
        app.dependency_overrides.clear()
        repo.close()
