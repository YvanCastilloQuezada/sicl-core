from __future__ import annotations

from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.repository import SQLiteRepository


def setup_project(client: TestClient) -> None:
    assert client.post("/v1/projects", json={"project_id": "P-RFC5", "name": "RFC5"}).status_code == 200
    assert client.post("/v1/projects/P-RFC5/commands", json={"command": "/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80"}).status_code == 200
    assert client.post("/v1/projects/P-RFC5/commands", json={"command": "/ALTERNATIVE CREATE Alpha"}).status_code == 200
    assert client.post("/v1/projects/P-RFC5/commands", json={"command": "/ALTERNATIVE CREATE Beta"}).status_code == 200


def client_for(tmp_path, monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    repo = SQLiteRepository(tmp_path / "rfc5.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    return repo, TestClient(app)


def test_post_evaluation_valid_and_get_list_and_filter(tmp_path, monkeypatch):
    repo, client = client_for(tmp_path, monkeypatch)
    try:
        setup_project(client)
        response = client.post("/v1/projects/P-RFC5/evaluations", json={"alternative": "Alpha", "objective": "ENERGY_SAVINGS", "value": 82, "unit": "%", "confidence": "0.8", "source": "USER_INPUT"})
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == "OK"
        assert body["data"]["evaluation"]["value"] == 82
        listed = client.get("/v1/projects/P-RFC5/evaluations")
        filtered = client.get("/v1/projects/P-RFC5/evaluations?alternative=Alpha")
        assert listed.status_code == filtered.status_code == 200
        assert len(listed.json()["data"]["evaluations"]) == 1
        assert len(filtered.json()["data"]["evaluations"]) == 1
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_evaluation_missing_field_returns_400(tmp_path, monkeypatch):
    repo, client = client_for(tmp_path, monkeypatch)
    try:
        setup_project(client)
        response = client.post("/v1/projects/P-RFC5/evaluations", json={"alternative": "Alpha", "value": 1})
        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_ARGUMENT"
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_evaluation_missing_alternative_returns_404(tmp_path, monkeypatch):
    repo, client = client_for(tmp_path, monkeypatch)
    try:
        setup_project(client)
        response = client.post("/v1/projects/P-RFC5/evaluations", json={"alternative": "Missing", "objective": "ENERGY_SAVINGS", "value": 1})
        assert response.status_code == 404
        assert response.json()["detail"]["code"] == "ALTERNATIVE_NOT_FOUND"
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_evaluation_duplicate_returns_409(tmp_path, monkeypatch):
    repo, client = client_for(tmp_path, monkeypatch)
    try:
        setup_project(client)
        payload = {"alternative": "Alpha", "objective": "ENERGY_SAVINGS", "value": 82}
        assert client.post("/v1/projects/P-RFC5/evaluations", json=payload).status_code == 200
        duplicate = client.post("/v1/projects/P-RFC5/evaluations", json=payload)
        assert duplicate.status_code == 409
        assert duplicate.json()["detail"]["code"] == "CONFLICT"
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_post_comparison_valid_and_get_list(tmp_path, monkeypatch):
    repo, client = client_for(tmp_path, monkeypatch)
    try:
        setup_project(client)
        response = client.post("/v1/projects/P-RFC5/comparisons", json={"alternatives": ["Alpha", "Beta"], "objectives": ["ENERGY_SAVINGS"]})
        assert response.status_code == 200
        assert response.json()["data"]["comparison"]["alternative_ids"]
        listed = client.get("/v1/projects/P-RFC5/comparisons")
        assert listed.status_code == 200
        assert len(listed.json()["data"]["comparisons"]) == 1
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_comparison_requires_two_existing_distinct_alternatives(tmp_path, monkeypatch):
    repo, client = client_for(tmp_path, monkeypatch)
    try:
        setup_project(client)
        too_short = client.post("/v1/projects/P-RFC5/comparisons", json={"alternatives": ["Alpha"]})
        missing = client.post("/v1/projects/P-RFC5/comparisons", json={"alternatives": ["Alpha", "Missing"]})
        duplicate_name = client.post("/v1/projects/P-RFC5/comparisons", json={"alternatives": ["Alpha", "Alpha"]})
        assert too_short.status_code == 400
        assert missing.status_code == 404
        assert duplicate_name.status_code == 400
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_evaluation_and_comparison_do_not_create_recommendation_or_decision(tmp_path, monkeypatch):
    repo, client = client_for(tmp_path, monkeypatch)
    try:
        setup_project(client)
        client.post("/v1/projects/P-RFC5/evaluations", json={"alternative": "Alpha", "objective": "ENERGY_SAVINGS", "value": 82})
        client.post("/v1/projects/P-RFC5/comparisons", json={"alternatives": ["Alpha", "Beta"]})
        snapshot = client.get("/v1/projects/P-RFC5/snapshot").json()["data"]["snapshot"]
        assert snapshot["recommendations"] == {}
        assert snapshot["decisions"] == {}
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_evaluation_and_comparison_persist_after_restart(tmp_path, monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    db = tmp_path / "restart.sqlite"
    repo = SQLiteRepository(db, check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    with TestClient(app) as client:
        setup_project(client)
        client.post("/v1/projects/P-RFC5/evaluations", json={"alternative": "Alpha", "objective": "ENERGY_SAVINGS", "value": 82})
        client.post("/v1/projects/P-RFC5/comparisons", json={"alternatives": ["Alpha", "Beta"]})
    repo.close()
    restarted = SQLiteRepository(db, check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: restarted
    try:
        with TestClient(app) as client:
            assert len(client.get("/v1/projects/P-RFC5/evaluations").json()["data"]["evaluations"]) == 1
            assert len(client.get("/v1/projects/P-RFC5/comparisons").json()["data"]["comparisons"]) == 1
    finally:
        app.dependency_overrides.clear()
        restarted.close()


def test_evaluations_and_comparisons_are_append_only(tmp_path, monkeypatch):
    repo, client = client_for(tmp_path, monkeypatch)
    try:
        setup_project(client)
        client.post("/v1/projects/P-RFC5/evaluations", json={"alternative": "Alpha", "objective": "ENERGY_SAVINGS", "value": 82})
        client.post("/v1/projects/P-RFC5/comparisons", json={"alternatives": ["Alpha", "Beta"]})
        evaluation_id = next(iter(repo.get_project("P-RFC5").evaluations))
        comparison_id = next(iter(repo.get_project("P-RFC5").comparisons))
        for statement in (
            f"UPDATE evaluations SET value=0 WHERE id='{evaluation_id}'",
            f"DELETE FROM evaluations WHERE id='{evaluation_id}'",
            f"UPDATE comparisons SET version=2 WHERE id='{comparison_id}'",
            f"DELETE FROM comparisons WHERE id='{comparison_id}'",
        ):
            try:
                repo.conn.execute(statement)
                assert False, f"append-only trigger did not reject: {statement}"
            except Exception as exc:
                assert "append-only" in str(exc)
    finally:
        app.dependency_overrides.clear()
        repo.close()
