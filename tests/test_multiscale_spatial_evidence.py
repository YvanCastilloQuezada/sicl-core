from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.multiscale_spatial_evidence import PROFILE, evidence_view, scale_relevance, surface_conflicts, validate_observation
from sicl.repository import SQLiteRepository


def test_all_eleven_scopes_use_canonical_values_and_scale_guidance():
    assert set(PROFILE) == {"pais", "macro_region", "region", "provincia_metropoli", "distrito_ciudad", "zona_barrio_sector", "parcela_sitio", "edificacion", "sistema", "espacio", "objeto"}
    assert scale_relevance("edificacion", "floor_count") == "RELEVANT"
    assert scale_relevance("distrito_ciudad", "MANUAL_OBSERVATION") == "POSSIBLE"


def test_qualifiers_units_and_unknowns_are_explicit():
    result = validate_observation({"spatial_scope": "parcela_sitio", "observation_type": "street_width", "value": 18, "unit": "m", "qualifier": "APPROXIMATE", "epistemic_state": "USER_OBSERVED"})
    assert result["qualifier"] == "APPROXIMATE"
    assert result["unit"] == "m"
    assert validate_observation({"spatial_scope": "objeto", "observation_type": "existing_object", "qualifier": "UNKNOWN", "epistemic_state": "UNKNOWN"})["epistemic_state"] == "UNKNOWN"


def test_conflicts_are_surfaced_without_source_ranking():
    records = [
        {"evidence_id": "E1", "spatial_scope": "edificacion", "observation_type": "floor_count", "value": 5},
        {"evidence_id": "E2", "spatial_scope": "edificacion", "observation_type": "floor_count", "value": 4},
    ]
    conflict = surface_conflicts(records)[0]
    assert conflict["state"] == "EVIDENCE_CONFLICT / REQUIRES_HUMAN_REVIEW"
    assert conflict["resolution"] == "NONE"


def test_http_multiscale_evidence_and_review_do_not_create_decision(tmp_path, monkeypatch):
    repo = SQLiteRepository(tmp_path / "multiscale-evidence.sqlite", check_same_thread=False)
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    app.dependency_overrides[get_repository] = lambda: repo
    try:
        with TestClient(app) as client:
            assert client.post("/v1/projects", json={"project_id": "P-MSE", "name": "Synthetic Evidence"}).status_code == 200
            base = {"actor": "architect", "spatial_scope": "edificacion", "observation_type": "floor_count", "value": 5, "unit": "floors", "qualifier": "EXACT", "epistemic_state": "USER_OBSERVED", "statement": "Neighboring building observed at five floors", "evidence_id": "E-MSE-1"}
            created = client.post("/v1/projects/P-MSE/spatial-evidence", json=base)
            assert created.status_code == 200
            photo = {**base, "evidence_id": "E-MSE-2", "value": 4, "source_kind": "EXTERNAL_SOURCE", "epistemic_state": "EXTERNAL_SOURCE", "photo_reference": "photo://synthetic", "observation_point": {"latitude": -8.1, "longitude": -79.0, "crs": "EPSG:4326"}, "spatial_scope": "distrito_ciudad"}
            assert client.post("/v1/projects/P-MSE/spatial-evidence", json=photo).status_code == 200
            listed = client.get("/v1/projects/P-MSE/spatial-evidence?spatial_scope=edificacion")
            assert listed.status_code == 200
            assert len(listed.json()["data"]["evidence"]) == 1
            assert listed.json()["data"]["decision_created"] is False
            reviewed = client.post("/v1/projects/P-MSE/spatial-evidence/E-MSE-1/review", json={"actor": "architect", "authority": "project_owner", "status": "APPROVED", "review": "Confirmed in field notes", "reason": "Human review"})
            assert reviewed.status_code == 200
            rejected = client.post("/v1/projects/P-MSE/spatial-evidence/E-MSE-2/review", json={"actor": "architect", "authority": "project_owner", "status": "REJECTED", "review": "Not accepted", "reason": "Insufficient provenance"})
            assert rejected.status_code == 200
            summary = client.get("/v1/projects/P-MSE/spatial-evidence/multiscale")
            assert summary.status_code == 200
            assert summary.json()["data"]["decision_created"] is False
            assert summary.json()["data"]["scopes"]["edificacion"][0]["human_review_state"] == "HUMAN_CONFIRMED"
            assert summary.json()["data"]["scopes"]["distrito_ciudad"][0]["human_review_state"] == "REJECTED"
            assert repo.events("P-MSE")[-1].type == "SPATIAL_EVIDENCE_REVIEWED"
    finally:
        app.dependency_overrides.clear()
        repo.close()
