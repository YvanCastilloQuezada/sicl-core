from pathlib import Path

from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.repository import SQLiteRepository


def client_for(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "api.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    return TestClient(app), repo


def teardown():
    app.dependency_overrides.clear()


def test_health(tmp_path: Path):
    client, repo = client_for(tmp_path)
    assert client.get("/health").json() == {"status": "ok", "service": "sicl-core-api"}
    repo.close(); teardown()


def test_cors_configured(tmp_path: Path):
    client, repo = client_for(tmp_path)
    response = client.options("/projects", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    repo.close(); teardown()


def test_create_project(tmp_path: Path):
    client, repo = client_for(tmp_path)
    response = client.post("/projects", json={"project_id": "P-API", "name": "API Project"})
    assert response.status_code == 201
    assert response.json()["data"]["project_id"] == "P-API"
    repo.close(); teardown()


def test_list_projects(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/projects", json={"project_id": "P-LIST", "name": "List"})
    response = client.get("/projects")
    assert response.status_code == 200
    assert response.json()["data"]["projects"][0]["project_id"] == "P-LIST"
    repo.close(); teardown()


def test_get_project(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/projects", json={"project_id": "P-GET", "name": "Get"})
    response = client.get("/projects/P-GET")
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Get"
    repo.close(); teardown()


def test_missing_project_404(tmp_path: Path):
    client, repo = client_for(tmp_path)
    assert client.get("/projects/MISSING").status_code == 404
    repo.close(); teardown()


def test_update_stage(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/projects", json={"project_id": "P-UPDATE", "name": "Update"})
    response = client.put("/projects/P-UPDATE", json={"stage": "ACTIVE"})
    assert response.status_code == 200
    assert response.json()["data"]["stage"] == "ACTIVE"
    repo.close(); teardown()


def test_logical_delete_closes_project(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/projects", json={"project_id": "P-CLOSE", "name": "Close"})
    response = client.delete("/projects/P-CLOSE")
    assert response.status_code == 200
    assert response.json()["data"]["stage"] == "CLOSED"
    assert len(repo.events("P-CLOSE")) == 2
    repo.close(); teardown()


def test_generic_command(tmp_path: Path):
    client, repo = client_for(tmp_path)
    client.post("/projects", json={"project_id": "P-CMD", "name": "Command"})
    response = client.post("/commands", json={"command": "/OBJECTIVE SET CLIMATE MAXIMIZE 80", "actor": "architect"})
    assert response.status_code == 200
    assert response.json()["data"]["key"] == "CLIMATE"
    repo.close(); teardown()


def test_invalid_command_returns_400(tmp_path: Path):
    client, repo = client_for(tmp_path)
    response = client.post("/commands", json={"command": "/UNKNOWN COMMAND"})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "UNKNOWN_COMMAND"
    repo.close(); teardown()
