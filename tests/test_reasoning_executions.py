from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.repository import SQLiteRepository


@pytest.fixture(autouse=True)
def clear_service_token(monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)


@pytest.fixture
def ctx(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "reasoning.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    client = TestClient(app)
    client.post("/v1/projects", json={"project_id": "R-P", "name": "Reasoning"})
    yield client, repo
    repo.close()
    app.dependency_overrides.clear()


def body(kind="PROJECT_BRAIN", status="HYPOTHESIS", execution_id="EX-1", payload=None, fingerprint=None, actor="arki"):
    return {
        "execution_id": execution_id,
        "kind": kind,
        "fingerprint": fingerprint or ("a" * 64),
        "input_fingerprint": "b" * 64,
        "payload": payload if payload is not None else {"result": "bounded"},
        "epistemic_status": status,
        "human_authority_ref": None,
        "source_refs": [],
        "actor": actor,
        "created_at": "2026-09-29T12:00:00Z",
    }


@pytest.mark.parametrize(("kind", "status"), [
    ("PROJECT_BRAIN", "FACT"),
    ("D6_2", "UNKNOWN"),
    ("D6_3", "HYPOTHESIS"),
    ("DEVELOPER_PROPOSAL", "HYPOTHESIS"),
    ("DEVELOPER_PROPOSAL", "PROPOSAL"),
])
def test_records_allowed_reasoning_kinds(ctx, kind, status):
    client, _ = ctx
    response = client.post("/v1/projects/R-P/reasoning-executions", json=body(kind, status))
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "RECORDED"


def test_rejects_unknown_kind(ctx):
    client, _ = ctx
    assert client.post("/v1/projects/R-P/reasoning-executions", json=body("OTHER")).status_code == 422


def test_rejects_unknown_project(ctx):
    client, _ = ctx
    assert client.post("/v1/projects/MISSING/reasoning-executions", json=body()).status_code == 404


@pytest.mark.parametrize("fingerprint", ["x" * 64, "A" * 64, "a" * 63])
def test_rejects_malformed_fingerprint(ctx, fingerprint):
    client, _ = ctx
    assert client.post("/v1/projects/R-P/reasoning-executions", json=body(fingerprint=fingerprint)).status_code == 422


@pytest.mark.parametrize(("kind", "status"), [
    ("D6_3", "FACT"),
    ("DEVELOPER_PROPOSAL", "FACT"),
    ("PROJECT_BRAIN", "PROPOSAL"),
    ("D6_2", "PROPOSAL"),
])
def test_rejects_incompatible_epistemic_status(ctx, kind, status):
    client, _ = ctx
    assert client.post("/v1/projects/R-P/reasoning-executions", json=body(kind, status)).status_code == 422


def test_persists_exact_reasoning_event_and_history(ctx):
    client, repo = ctx
    request = body()
    response = client.post("/v1/projects/R-P/reasoning-executions", json=request)
    event = repo.events("R-P")[-1]
    assert event.type == "REASONING_EXECUTION_RECORDED"
    assert event.source == "ARKI_REASONING"
    assert event.payload == {"execution": request}
    history = client.get("/v1/projects/R-P/history").json()["data"]["events"]
    assert history[-1]["id"] == event.id


def test_does_not_increment_project_version_or_change_snapshot(ctx):
    client, repo = ctx
    before = repo.get_project("R-P")
    before_version = before.version
    before_snapshot = client.get("/v1/projects/R-P/snapshot").json()["data"]["snapshot"]
    response = client.post("/v1/projects/R-P/reasoning-executions", json=body())
    after = repo.get_project("R-P")
    after_snapshot = client.get("/v1/projects/R-P/snapshot").json()["data"]["snapshot"]
    assert response.json()["observed_version"] == before_version
    assert after.version == before_version
    assert after_snapshot == before_snapshot


def test_idempotent_same_execution_returns_same_event(ctx):
    client, repo = ctx
    request = body()
    first = client.post("/v1/projects/R-P/reasoning-executions", json=request)
    second = client.post("/v1/projects/R-P/reasoning-executions", json=request)
    assert second.status_code == 200
    assert second.json()["data"]["event_id"] == first.json()["data"]["event_id"]
    assert len([e for e in repo.events("R-P") if e.type == "REASONING_EXECUTION_RECORDED"]) == 1


def test_conflict_same_execution_different_content(ctx):
    client, _ = ctx
    assert client.post("/v1/projects/R-P/reasoning-executions", json=body()).status_code == 200
    changed = body(payload={"result": "different"})
    assert client.post("/v1/projects/R-P/reasoning-executions", json=changed).status_code == 409


def test_rejects_forbidden_d2_commit_key(ctx):
    client, _ = ctx
    response = client.post("/v1/projects/R-P/reasoning-executions", json=body(payload={"d2_commit": True}))
    assert response.status_code == 400


def test_allows_free_text_that_mentions_d2(ctx):
    client, _ = ctx
    response = client.post("/v1/projects/R-P/reasoning-executions", json=body(payload={"note": "D-2 remains unchanged"}))
    assert response.status_code == 200


def test_event_store_remains_append_only(ctx):
    client, repo = ctx
    response = client.post("/v1/projects/R-P/reasoning-executions", json=body())
    event_id = response.json()["data"]["event_id"]
    with pytest.raises(Exception):
        repo.conn.execute("UPDATE events SET actor='x' WHERE id=?", (event_id,))
    repo.conn.rollback()
    with pytest.raises(Exception):
        repo.conn.execute("DELETE FROM events WHERE id=?", (event_id,))
    repo.conn.rollback()
