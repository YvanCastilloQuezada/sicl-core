from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from api.main import create_app


def client(tmp_path: Path) -> TestClient:
    os.environ["SICL_DB_PATH"] = str(tmp_path / "location.sqlite")
    os.environ["SICL_CORE_SERVICE_TOKEN"] = "test-token"
    return TestClient(create_app())


def headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}


def create_project(c: TestClient, project_id: str) -> None:
    response = c.post("/v1/projects", headers=headers(), json={"project_id": project_id, "name": "Educational example", "spatial_scope": "parcela_sitio"})
    assert response.status_code == 200, response.text


def point() -> dict:
    return {"type": "Point", "coordinates": [-79.028, -8.111]}


def test_candidate_requires_explicit_confirmation(tmp_path: Path) -> None:
    c = client(tmp_path)
    project_id = f"LOC-CANDIDATE-{uuid4().hex[:10]}"
    create_project(c, project_id)
    response = c.post(f"/v1/projects/{project_id}/locations", headers=headers(), json={"geometry": point(), "confirm": False})
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "HUMAN_CONFIRMATION_REQUIRED"


def test_confirmed_point_persists_and_reloads(tmp_path: Path) -> None:
    c = client(tmp_path)
    project_id = f"LOC-PERSIST-{uuid4().hex[:10]}"
    create_project(c, project_id)
    response = c.post(f"/v1/projects/{project_id}/locations", headers=headers(), json={"geometry": point(), "place_label": "Trujillo candidate", "actor_id": "architect-1", "authority": "owner-1", "confirm": True})
    assert response.status_code == 200, response.text
    location = response.json()["data"]["location"]
    assert location["status"] == "CONFIRMED"
    assert location["geometry"]["coordinates"] == [-79.028, -8.111]
    current = c.get(f"/v1/projects/{project_id}/locations/current", headers=headers())
    assert current.status_code == 200
    assert current.json()["data"]["location"]["location_id"] == location["location_id"]
    missing = c.get(f"/v1/projects/{project_id}/missing-data?spatial_scope=parcela_sitio", headers=headers())
    assert missing.status_code == 200
    payload = missing.json()["data"]
    assert payload["location_present"] is True
    assert next(item for item in payload["variables"] if item["canonical_variable_id"] == "SITE_COORDINATE_REFERENCE")["state"] == "PRESENT"
    assert payload["capabilities"][0]["state"] == "AVAILABLE"


def test_invalid_coordinates_and_scope_are_rejected(tmp_path: Path) -> None:
    c = client(tmp_path)
    project_id = f"LOC-INVALID-{uuid4().hex[:10]}"
    create_project(c, project_id)
    invalid = c.post(f"/v1/projects/{project_id}/locations", headers=headers(), json={"geometry": {"type": "Point", "coordinates": [250, 1]}, "confirm": True})
    assert invalid.status_code == 422
    bad_scope = c.get(f"/v1/projects/{project_id}/missing-data?spatial_scope=not-a-scope", headers=headers())
    assert bad_scope.status_code == 400


def test_history_contains_confirmation_event(tmp_path: Path) -> None:
    c = client(tmp_path)
    project_id = f"LOC-HISTORY-{uuid4().hex[:10]}"
    create_project(c, project_id)
    c.post(f"/v1/projects/{project_id}/locations", headers=headers(), json={"geometry": point(), "confirm": True})
    history = c.get(f"/v1/projects/{project_id}/history", headers=headers())
    assert any(event["type"] == "SPATIAL_LOCATION_CONFIRMED" for event in history.json()["data"]["events"])
