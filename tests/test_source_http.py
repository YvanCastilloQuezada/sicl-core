from __future__ import annotations

from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.repository import SQLiteRepository


def setup_client(tmp_path, monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    repo = SQLiteRepository(tmp_path / "test.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    return repo, TestClient(app)


def teardown(repo):
    app.dependency_overrides.clear()
    repo.close()


def project(client, project_id="P-SOURCE"):
    response = client.post("/v1/projects", json={"project_id": project_id, "name": "Source project"})
    assert response.status_code == 200


def source(source_id="SRC-1", source_type="OFFICIAL", title="Official source", url=None):
    return {"source_id": source_id, "source_type": source_type, "title": title, "url": url}


def test_create_list_get_source(tmp_path, monkeypatch):
    repo, client = setup_client(tmp_path, monkeypatch)
    try:
        project(client)
        created = client.post("/v1/projects/P-SOURCE/sources", json=source(url="https://example.test"))
        assert created.status_code == 200
        body = created.json()
        assert body["contract_version"] == "1.0"
        assert body["code"] == "OK"
        item = body["data"]["source"]
        assert item == {"source_id": "SRC-1", "project_id": "P-SOURCE", "source_type": "OFFICIAL", "title": "Official source", "url": "https://example.test", "version": 1}
        assert client.get("/v1/projects/P-SOURCE/sources").json()["data"]["sources"] == [item]
        assert client.get("/v1/projects/P-SOURCE/sources/SRC-1").json()["data"]["source"] == item
    finally:
        teardown(repo)


def test_source_optional_url_and_supported_types(tmp_path, monkeypatch):
    repo, client = setup_client(tmp_path, monkeypatch)
    try:
        project(client, "P-TYPES")
        for index, source_type in enumerate(("OFFICIAL", "SECONDARY", "USER_PROVIDED", "UNKNOWN")):
            response = client.post("/v1/projects/P-TYPES/sources", json=source(f"SRC-{index}", source_type, source_type))
            assert response.status_code == 200
            assert response.json()["data"]["source"]["url"] is None
    finally:
        teardown(repo)


def test_duplicate_source_is_rejected_without_mutation(tmp_path, monkeypatch):
    repo, client = setup_client(tmp_path, monkeypatch)
    try:
        project(client, "P-DUP")
        item = source("SRC-DUP")
        assert client.post("/v1/projects/P-DUP/sources", json=item).status_code == 200
        version = repo.get_project("P-DUP").version
        events = len(repo.events("P-DUP"))
        response = client.post("/v1/projects/P-DUP/sources", json=item)
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "SOURCE_ALREADY_EXISTS"
        assert repo.get_project("P-DUP").version == version
        assert len(repo.events("P-DUP")) == events
    finally:
        teardown(repo)


def test_invalid_source_type_is_rejected_and_not_persisted(tmp_path, monkeypatch):
    repo, client = setup_client(tmp_path, monkeypatch)
    try:
        project(client, "P-INVALID")
        response = client.post("/v1/projects/P-INVALID/sources", json=source("SRC-BAD", "NOT_A_TYPE"))
        assert response.status_code == 422
        assert response.json()["detail"]["code"] == "INVALID_SOURCE_TYPE"
        assert client.get("/v1/projects/P-INVALID/sources").json()["data"]["sources"] == []
    finally:
        teardown(repo)


def test_missing_project_and_source_errors(tmp_path, monkeypatch):
    repo, client = setup_client(tmp_path, monkeypatch)
    try:
        assert client.get("/v1/projects/MISSING/sources").json()["detail"]["code"] == "PROJECT_NOT_FOUND"
        project(client, "P-MISSING-SOURCE")
        response = client.get("/v1/projects/P-MISSING-SOURCE/sources/NOPE")
        assert response.status_code == 404
        assert response.json()["detail"]["code"] == "SOURCE_NOT_FOUND"
    finally:
        teardown(repo)


def test_source_persists_after_restart(tmp_path, monkeypatch):
    repo, client = setup_client(tmp_path, monkeypatch)
    db = tmp_path / "test.sqlite"
    try:
        project(client, "P-RESTART")
        assert client.post("/v1/projects/P-RESTART/sources", json=source("SRC-R")).status_code == 200
    finally:
        teardown(repo)
    reopened = SQLiteRepository(db, check_same_thread=False)
    try:
        loaded = reopened.get_project("P-RESTART")
        assert loaded is not None
        assert loaded.sources["SRC-R"].title == "Official source"
    finally:
        reopened.close()


def test_evidence_can_reference_http_source(tmp_path, monkeypatch):
    repo, client = setup_client(tmp_path, monkeypatch)
    try:
        project(client, "P-EVIDENCE")
        assert client.post("/v1/projects/P-EVIDENCE/sources", json=source("SRC-E")).status_code == 200
        response = client.post("/v1/projects/P-EVIDENCE/evidence", json={"evidence_id": "E-1", "statement": "Recorded", "evidence_type": "DOCUMENT", "source_id": "SRC-E"})
        assert response.status_code == 200
        assert response.json()["data"]["evidence"]["source_id"] == "SRC-E"
    finally:
        teardown(repo)


def test_source_is_project_scoped(tmp_path, monkeypatch):
    repo, client = setup_client(tmp_path, monkeypatch)
    try:
        project(client, "P-A")
        project(client, "P-B")
        item = source("SRC-SAME")
        assert client.post("/v1/projects/P-A/sources", json=item).status_code == 200
        assert client.post("/v1/projects/P-B/sources", json=item).status_code == 200
        assert client.get("/v1/projects/P-A/sources/SRC-SAME").json()["data"]["source"]["project_id"] == "P-A"
        assert client.get("/v1/projects/P-B/sources/SRC-SAME").json()["data"]["source"]["project_id"] == "P-B"
    finally:
        teardown(repo)


def test_source_event_append_only_and_complete(tmp_path, monkeypatch):
    repo, client = setup_client(tmp_path, monkeypatch)
    try:
        project(client, "P-EVENT")
        before = len(repo.events("P-EVENT"))
        client.post("/v1/projects/P-EVENT/sources", json=source("SRC-EV", "SECONDARY", "Event source", "https://event.test"))
        events = repo.events("P-EVENT")
        assert len(events) == before + 1
        event = events[-1]
        assert event.type == "SOURCE_ADDED"
        assert event.actor == "api"
        assert event.source
        assert event.payload["source_id"] == "SRC-EV"
        assert event.payload["title"] == "Event source"
    finally:
        teardown(repo)


def test_source_create_does_not_create_decision_or_recommendation(tmp_path, monkeypatch):
    repo, client = setup_client(tmp_path, monkeypatch)
    try:
        project(client, "P-INVARIANT")
        client.post("/v1/projects/P-INVARIANT/sources", json=source("SRC-I"))
        state = repo.get_project("P-INVARIANT")
        assert state.sources
        assert not state.recommendations
        assert not state.decisions
        assert not state.human_reviews
    finally:
        teardown(repo)


