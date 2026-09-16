from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.repository import SQLiteRepository


@pytest.fixture(autouse=True)
def clear_service_token(monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)


def client_for(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "v1.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    return TestClient(app), repo


def close(repo: SQLiteRepository) -> None:
    repo.close()
    app.dependency_overrides.clear()


def test_v1_health_and_envelope(tmp_path: Path):
    client, repo = client_for(tmp_path)
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"contract_version": "1.0", "status": "OK", "service": "sicl-core-api"}
    close(repo)


def test_v1_project_snapshot_and_history(tmp_path: Path):
    client, repo = client_for(tmp_path)
    created = client.post("/v1/projects", json={"project_id": "V1-P", "name": "Canonical"})
    assert created.status_code == 200
    body = created.json()
    assert body["contract_version"] == "1.0"
    assert body["project_id"] == "V1-P"
    assert body["observed_version"] == 1
    snapshot = client.get("/v1/projects/V1-P/snapshot").json()
    assert snapshot["data"]["snapshot"]["project_id"] == "V1-P"
    history = client.get("/v1/projects/V1-P/history").json()
    assert len(history["data"]["events"]) == 1
    close(repo)


def test_v1_project_scoped_command_has_observed_version(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-C", "name": "Command"})
    response = client.post("/v1/projects/V1-C/commands", json={"command": "/OBJECTIVE SET CLIMATE MAXIMIZE 80", "actor": "architect"})
    assert response.status_code == 200
    assert response.json()["observed_version"] == 2
    assert response.json()["data"]["key"] == "CLIMATE"
    close(repo)


def test_v1_preference_is_separate_and_emits_event(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-PREF", "name": "Preference"})
    response = client.post("/v1/projects/V1-PREF/preferences", json={"statement": "Prefer low operational energy", "actor": "owner"})
    assert response.status_code == 200
    preference = response.json()["data"]["preference"]
    assert preference["statement"] == "Prefer low operational energy"
    assert "preferences" in response.json()["data"] or preference["preference_id"].startswith("PREF-")
    events = client.get("/v1/projects/V1-PREF/history").json()["data"]["events"]
    assert events[-1]["type"] == "PREFERENCE_RECORDED"
    close(repo)


def test_v1_human_review_then_decision(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-D", "name": "Decision"})
    review = client.post("/v1/projects/V1-D/human-reviews", json={"actor": "Yvan", "timestamp": "2026-09-15T20:00:00Z", "review": "Reviewed recommendation", "reason": "Architecture review", "authority": "PRODUCT_OWNER"})
    assert review.status_code == 200
    decision = client.post("/v1/projects/V1-D/decisions", json={"statement": "Proceed", "actor": "Yvan", "authority": "PRODUCT_OWNER"})
    assert decision.status_code == 200
    assert decision.json()["data"]["decision"]["actor"] == "Yvan"
    close(repo)


def test_v1_decision_without_review_is_semantic_error(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-NO-REVIEW", "name": "Decision"})
    response = client.post("/v1/projects/V1-NO-REVIEW/decisions", json={"statement": "Proceed", "actor": "Yvan", "authority": "PRODUCT_OWNER"})
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "HUMAN_REVIEW_REQUIRED"
    close(repo)


def test_v1_read_only_debate_does_not_create_decision(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/v1/projects", json={"project_id": "V1-DEBATE", "name": "Debate"})
    client.post("/v1/projects/V1-DEBATE/commands", json={"command": "/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80"})
    alternative = client.post("/v1/projects/V1-DEBATE/commands", json={"command": "/ALTERNATIVE CREATE CONVENCIONAL_A"}).json()["data"]["alternative_id"]
    response = client.post("/v1/projects/V1-DEBATE/debate", json={"alternative_id": alternative})
    assert response.status_code == 200
    assert response.json()["data"]["decision_created"] is False
    close(repo)


def test_v1_auth_rejects_invalid_token(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SICL_CORE_SERVICE_TOKEN", "secret-for-test")
    client, repo = client_for(tmp_path)
    assert client.get("/v1/health").status_code == 401
    assert client.get("/v1/health", headers={"Authorization": "Bearer secret-for-test"}).status_code == 200
    close(repo)
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN")


def test_legacy_endpoints_remain_available(tmp_path: Path):
    client, repo = client_for(tmp_path)
    response = client.post("/projects", json={"project_id": "LEGACY", "name": "Legacy"})
    assert response.status_code == 201
    assert client.get("/projects/LEGACY").status_code == 200
    close(repo)
