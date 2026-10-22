from __future__ import annotations

import json
import os

from fastapi.testclient import TestClient

from api.main import create_app


def test_upao001_spatial_representation_transport_is_read_only() -> None:
    client = TestClient(create_app())
    headers = {"Authorization": f"Bearer {os.getenv('SICL_CORE_SERVICE_TOKEN', '')}"}
    response = client.get("/v1/projects/UPAO-001/spatial-representations", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["read_only"] is True
    assert data["provenance"] == "SYNTHETIC / EDUCATIONAL / MODEL PROJECT"
    assert len(data["representations"]) == 3
    assert {item["alternative_id"] for item in data["representations"]} == {
        "UPAO-001-A", "UPAO-001-B", "UPAO-001-C"
    }
    assert all(item["spatial_scope"] == "edificacion" for item in data["representations"])
    assert all(item["elements"] for item in data["representations"])
    assert set(data["metrics"]) == {"UPAO-001-A", "UPAO-001-B", "UPAO-001-C"}
    assert len({json.dumps(item["elements"], sort_keys=True) for item in data["representations"]}) == 3


def test_upao001_spatial_representation_transport_selects_one_alternative() -> None:
    client = TestClient(create_app())
    headers = {"Authorization": f"Bearer {os.getenv('SICL_CORE_SERVICE_TOKEN', '')}"}
    response = client.get("/v1/projects/UPAO-001/spatial-representations?alternative=UPAO-001-B", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert [item["alternative_id"] for item in data["representations"]] == ["UPAO-001-B"]


def test_unknown_project_is_not_silently_fabricated() -> None:
    client = TestClient(create_app())
    headers = {"Authorization": f"Bearer {os.getenv('SICL_CORE_SERVICE_TOKEN', '')}"}
    response = client.get("/v1/projects/UNKNOWN/spatial-representations", headers=headers)
    assert response.status_code == 404
    assert "PROJECT_NOT_FOUND" in str(response.json())
