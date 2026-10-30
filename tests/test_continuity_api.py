from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.repository import SQLiteRepository


@pytest.fixture
def continuity_client(tmp_path, monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    repo = SQLiteRepository(tmp_path / "continuity.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    client = TestClient(app)
    created = client.post("/v1/projects", json={"project_id": "MEMORY-P1", "name": "Continuity"})
    assert created.status_code == 200
    yield client, repo
    repo.close()
    app.dependency_overrides.clear()


def _event(event_id="evt-001", idempotency_key="idem-001"):
    return {
        "event_id": event_id,
        "event_type": "DECISION_RECORDED",
        "workstream_id": "MEMORY",
        "occurred_at": "2026-10-30T12:00:00Z",
        "actor": "OWNER",
        "authority_ref": "OWNER_CONFIRMED",
        "source_system": "CHATGPT",
        "source_sha": None,
        "evidence_refs": ["https://github.com/example/evidence"],
        "payload": {"decision": "Use Core as canonical event store"},
        "idempotency_key": idempotency_key,
        "correlation_id": "session-001",
    }


def test_continuity_fails_closed_when_service_token_is_not_configured(
    continuity_client, monkeypatch
):
    client, _ = continuity_client
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    response = client.post("/v1/projects/MEMORY-P1/continuity/events", json=_event())
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "CONTINUITY_AUTH_NOT_CONFIGURED"


def test_continuity_rejects_missing_or_invalid_token(continuity_client, monkeypatch):
    client, _ = continuity_client
    monkeypatch.setenv("SICL_CORE_SERVICE_TOKEN", "test-secret")
    url = "/v1/projects/MEMORY-P1/continuity/events"
    assert client.post(url, json=_event()).status_code == 401
    assert client.post(url, json=_event(), headers={"Authorization": "Bearer wrong"}).status_code == 401


def test_continuity_append_is_idempotent_and_recoverable(continuity_client, monkeypatch):
    client, repo = continuity_client
    monkeypatch.setenv("SICL_CORE_SERVICE_TOKEN", "test-secret")
    headers = {"Authorization": "Bearer test-secret"}
    url = "/v1/projects/MEMORY-P1/continuity/events"

    first = client.post(url, json=_event(), headers=headers)
    retry = client.post(url, json=_event(), headers=headers)
    assert first.status_code == 200
    assert first.json()["code"] == "RECORDED"
    assert retry.status_code == 200
    assert retry.json()["code"] == "DUPLICATE"
    assert retry.json()["event_sequence"] == first.json()["event_sequence"]
    assert len([e for e in repo.events("MEMORY-P1") if e.type == "CONTINUITY_DECISION_RECORDED"]) == 1

    history = client.get(
        "/v1/projects/MEMORY-P1/continuity/events?after_id=0",
        headers=headers,
    )
    assert history.status_code == 200
    assert len(history.json()["events"]) == 1
    assert history.json()["events"][0]["event"]["event_id"] == "evt-001"

    checkpoint = client.get("/v1/projects/MEMORY-P1/continuity/checkpoint", headers=headers)
    assert checkpoint.status_code == 200
    assert checkpoint.json()["event_count"] == 1
    assert checkpoint.json()["last_event_id"] == first.json()["event_sequence"]


def test_continuity_idempotency_key_conflict_does_not_append(continuity_client, monkeypatch):
    client, repo = continuity_client
    monkeypatch.setenv("SICL_CORE_SERVICE_TOKEN", "test-secret")
    headers = {"Authorization": "Bearer test-secret"}
    url = "/v1/projects/MEMORY-P1/continuity/events"
    assert client.post(url, json=_event(), headers=headers).status_code == 200

    changed = _event(event_id="evt-002", idempotency_key="idem-001")
    changed["payload"] = {"decision": "Different content"}
    response = client.post(url, json=changed, headers=headers)
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "CONTINUITY_IDEMPOTENCY_CONFLICT"
    assert len([e for e in repo.events("MEMORY-P1") if e.type.startswith("CONTINUITY_")]) == 1


def test_continuity_rejects_unknown_event_type(continuity_client, monkeypatch):
    client, _ = continuity_client
    monkeypatch.setenv("SICL_CORE_SERVICE_TOKEN", "test-secret")
    body = _event()
    body["event_type"] = "AUTO_APPROVE"
    response = client.post(
        "/v1/projects/MEMORY-P1/continuity/events",
        json=body,
        headers={"Authorization": "Bearer test-secret"},
    )
    assert response.status_code == 422


def test_continuity_event_id_conflict_does_not_append(continuity_client, monkeypatch):
    client, repo = continuity_client
    monkeypatch.setenv("SICL_CORE_SERVICE_TOKEN", "test-secret")
    headers = {"Authorization": "Bearer test-secret"}
    url = "/v1/projects/MEMORY-P1/continuity/events"
    assert client.post(url, json=_event(), headers=headers).status_code == 200

    changed = _event(event_id="evt-001", idempotency_key="idem-002")
    changed["payload"] = {"decision": "Different content"}
    response = client.post(url, json=changed, headers=headers)
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "CONTINUITY_IDEMPOTENCY_CONFLICT"
    assert len([e for e in repo.events("MEMORY-P1") if e.type.startswith("CONTINUITY_")]) == 1


def test_continuity_rejects_oversized_payload_without_append(continuity_client, monkeypatch):
    client, repo = continuity_client
    monkeypatch.setenv("SICL_CORE_SERVICE_TOKEN", "test-secret")
    body = _event()
    body["payload"] = {"large": "x" * 260_000}
    response = client.post(
        "/v1/projects/MEMORY-P1/continuity/events",
        json=body,
        headers={"Authorization": "Bearer test-secret"},
    )
    assert response.status_code == 413
    assert response.json()["detail"]["code"] == "CONTINUITY_EVENT_TOO_LARGE"
    assert len([e for e in repo.events("MEMORY-P1") if e.type.startswith("CONTINUITY_")]) == 0


def test_continuity_rejects_unknown_project(continuity_client, monkeypatch):
    client, _ = continuity_client
    monkeypatch.setenv("SICL_CORE_SERVICE_TOKEN", "test-secret")
    response = client.post(
        "/v1/projects/DOES-NOT-EXIST/continuity/events",
        json=_event(),
        headers={"Authorization": "Bearer test-secret"},
    )
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "PROJECT_NOT_FOUND"


def test_continuity_key_index_is_append_only(continuity_client, monkeypatch):
    client, repo = continuity_client
    monkeypatch.setenv("SICL_CORE_SERVICE_TOKEN", "test-secret")
    response = client.post(
        "/v1/projects/MEMORY-P1/continuity/events",
        json=_event(),
        headers={"Authorization": "Bearer test-secret"},
    )
    assert response.status_code == 200
    with pytest.raises(Exception, match="append-only"):
        repo.conn.execute(
            "UPDATE continuity_event_keys SET sha256=? WHERE project_id=? AND event_id=?",
            ("0" * 64, "MEMORY-P1", "evt-001"),
        )
    with pytest.raises(Exception, match="append-only"):
        repo.conn.execute(
            "DELETE FROM continuity_event_keys WHERE project_id=? AND event_id=?",
            ("MEMORY-P1", "evt-001"),
        )
