import math

from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.repository import SQLiteRepository
from sicl.spatial_registration import derive_registration_transform


def payload(project_id="P-REG"):
    return {
        "actor": "architect",
        "source_frame": {"id": "PROJECT_LOCAL", "type": "PROJECT_LOCAL"},
        "target_frame": {"id": "FIELD_LOCAL", "type": "TARGET_LOCAL"},
        "control_correspondences": [
            {"id": "CONTROL_A", "project_point": {"x": 0, "y": 0}, "target_point": {"x": 10, "y": 20}},
            {"id": "CONTROL_B", "project_point": {"x": 10, "y": 0}, "target_point": {"x": 10, "y": 30}},
        ],
        "registration_method": "MANUAL_TWO_POINT",
        "units": "m",
        "coordinate_systems": {"source": "PROJECT_LOCAL", "target": "FIELD_LOCAL"},
        "site_side_confirmation": {"confirmed": True, "side": "NORTH", "actor": "architect"},
        "uncertainty": {"state": "UNKNOWN"},
    }


def test_transform_is_deterministic_and_rejects_degenerate_baselines():
    first = derive_registration_transform(payload()["control_correspondences"])
    second = derive_registration_transform(payload()["control_correspondences"])
    assert first == second
    assert first["scale"] == 1
    assert math.isclose(first["rotation_degrees"], 90.0)
    assert first["translation"] == {"x": 10.0, "y": 20.0}
    bad = payload()["control_correspondences"]
    bad[1]["project_point"] = {"x": 0, "y": 0}
    try:
        derive_registration_transform(bad)
    except ValueError as exc:
        assert str(exc) == "DEGENERATE_CONTROL_BASELINE"
    else:
        raise AssertionError("degenerate baseline must be rejected")


def test_http_registration_lifecycle_persists_and_is_project_scoped(tmp_path, monkeypatch):
    repo = SQLiteRepository(tmp_path / "registration.sqlite", check_same_thread=False)
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    app.dependency_overrides[get_repository] = lambda: repo
    try:
        with TestClient(app) as client:
            assert client.post("/v1/projects", json={"project_id": "P-REG", "name": "Registration"}).status_code == 200
            assert client.post("/v1/projects", json={"project_id": "P-OTHER", "name": "Other"}).status_code == 200
            proposed = client.post("/v1/projects/P-REG/spatial-registrations", json=payload())
            assert proposed.status_code == 200
            registration = proposed.json()["data"]["registration"]
            assert registration["status"] == "DRAFT"
            assert proposed.json()["data"]["decision_created"] is False
            confirmed = client.post(f"/v1/projects/P-REG/spatial-registrations/{registration['registration_id']}/transition", json={"actor": "architect", "action": "CONFIRM"})
            assert confirmed.status_code == 200
            locked = client.post(f"/v1/projects/P-REG/spatial-registrations/{registration['registration_id']}/transition", json={"actor": "architect", "action": "LOCK"})
            assert locked.status_code == 200
            assert locked.json()["data"]["registration"]["status"] == "LOCKED"
            listed = client.get("/v1/projects/P-REG/spatial-registrations")
            assert listed.status_code == 200
            assert listed.json()["data"]["registrations"][0]["status"] == "LOCKED"
            assert client.get("/v1/projects/P-OTHER/spatial-registrations").json()["data"]["registrations"] == []
            assert [event.type for event in repo.events("P-REG") if event.type.startswith("REGISTRATION_")] == ["REGISTRATION_PROPOSED", "REGISTRATION_CONFIRMED", "REGISTRATION_LOCKED"]
    finally:
        app.dependency_overrides.clear()
        repo.close()
