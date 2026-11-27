from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.deps import get_repository, get_copilot_session_repository
from api.main import app
from sicl.repository import SQLiteRepository
from sicl.copilot_session_repository import CopilotSessionRepository


@pytest.fixture
def copilot_client(tmp_path, monkeypatch):
    monkeypatch.setenv("SICL_CORE_SERVICE_TOKEN", "copilot-test-token")
    canonical = SQLiteRepository(tmp_path / "canonical.sqlite", check_same_thread=False)
    conversation = CopilotSessionRepository(tmp_path / "conversations.sqlite")
    app.dependency_overrides[get_repository] = lambda: canonical
    app.dependency_overrides[get_copilot_session_repository] = lambda: conversation
    client = TestClient(app)
    created = client.post("/projects", json={"project_id": "CP02-P1", "name": "CP02 test"})
    assert created.status_code == 200
    yield client, canonical, conversation
    conversation.close()
    canonical.close()
    app.dependency_overrides.clear()


def auth():
    return {"Authorization": "Bearer copilot-test-token"}


def test_api_create_session_and_append_message(copilot_client):
    client, _, store = copilot_client
    response = client.post("/v1/copilot/sessions", headers=auth(), json={
        "session_id": "sess-1", "project_id": "CP02-P1", "actor_id": "architect-1",
        "channel": "FIELD", "title": "Site inspection",
    })
    assert response.status_code == 201
    assert response.json()["session_id"] == "sess-1"

    msg = {"message_id": "msg-1", "role": "architect", "content": "Observed crack",
           "attachments": ["photo-1"], "metadata": {"surface": "FIELD"},
           "idempotency_key": "msg-key-1"}
    posted = client.post("/v1/copilot/sessions/sess-1/messages?actor_id=architect-1",
                         headers=auth(), json=msg)
    assert posted.status_code == 201
    assert posted.json()["sequence"] == 1

    history = client.get("/v1/copilot/sessions/sess-1/messages?actor_id=architect-1", headers=auth())
    assert history.status_code == 200
    assert history.json()["messages"][0]["content"] == "Observed crack"
    assert history.json()["messages"][0]["attachments"] == ["photo-1"]


def test_api_authentication_is_fail_closed(copilot_client, monkeypatch):
    client, _, _ = copilot_client
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    response = client.post("/v1/copilot/sessions", json={
        "project_id": "CP02-P1", "actor_id": "architect-1"
    })
    assert response.status_code == 503
    monkeypatch.setenv("SICL_CORE_SERVICE_TOKEN", "copilot-test-token")
    response = client.post("/v1/copilot/sessions", headers={"Authorization": "Bearer wrong"}, json={
        "project_id": "CP02-P1", "actor_id": "architect-1"
    })
    assert response.status_code == 401


def test_api_session_actor_scope_returns_not_found_for_other_actor(copilot_client):
    client, _, _ = copilot_client
    client.post("/v1/copilot/sessions", headers=auth(), json={
        "session_id": "sess-scope", "project_id": "CP02-P1", "actor_id": "owner-a"
    })
    response = client.get("/v1/copilot/sessions/sess-scope/messages?actor_id=owner-b", headers=auth())
    assert response.status_code == 404


def test_duplicate_api_message_is_idempotent(copilot_client):
    client, _, _ = copilot_client
    client.post("/v1/copilot/sessions", headers=auth(), json={
        "session_id": "sess-idem", "project_id": "CP02-P1", "actor_id": "architect-1"
    })
    msg = {"message_id": "m1", "role": "architect", "content": "hello",
            "idempotency_key": "key-1"}
    path = "/v1/copilot/sessions/sess-idem/messages?actor_id=architect-1"
    first = client.post(path, headers=auth(), json=msg)
    second = client.post(path, headers=auth(), json=msg)
    assert first.status_code == 201 and second.status_code == 201
    assert second.json()["code"] == "DUPLICATE"
    assert len(client.get(path.replace("/messages", "/messages"), headers=auth()).json()["messages"]) == 1


def test_api_rejects_unknown_project_and_invalid_channel(copilot_client):
    client, _, _ = copilot_client
    bad_project = client.post("/v1/copilot/sessions", headers=auth(), json={
        "project_id": "missing-project", "actor_id": "a"
    })
    assert bad_project.status_code == 404
    bad_channel = client.post("/v1/copilot/sessions", headers=auth(), json={
        "project_id": "CP02-P1", "actor_id": "a", "channel": "ADMIN"
    })
    assert bad_channel.status_code == 422
