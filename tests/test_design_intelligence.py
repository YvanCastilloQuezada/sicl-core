from __future__ import annotations

from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.cli import CLI
from sicl.repository import SQLiteRepository
from sicl.design_principles import PRINCIPLES


def configured_client(tmp_path, monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    repo = SQLiteRepository(tmp_path / "design.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    return repo, TestClient(app)


def test_http_catalog_returns_fifteen_sourced_principles(tmp_path, monkeypatch):
    repo, client = configured_client(tmp_path, monkeypatch)
    try:
        response = client.get("/v1/design/principles")
        assert response.status_code == 200
        body = response.json()
        assert body["contract_version"] == "1.0"
        principles = body["data"]["principles"]
        assert len(principles) == 15
        assert all(item["source"] != "PENDING_REFERENCE" for item in principles)
        assert all(item["source"] for item in principles)
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_http_get_single_principle_and_not_found(tmp_path, monkeypatch):
    repo, client = configured_client(tmp_path, monkeypatch)
    try:
        response = client.get("/v1/design/principles/P-01")
        missing = client.get("/v1/design/principles/P-99")
        assert response.status_code == 200
        assert response.json()["data"]["principle"]["category"] == "PROPORCION"
        assert missing.status_code == 404
        assert missing.json()["detail"]["code"] == "PRINCIPLE_NOT_FOUND"
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_http_category_filter_is_read_only(tmp_path, monkeypatch):
    repo, client = configured_client(tmp_path, monkeypatch)
    try:
        response = client.get("/v1/design/principles?category=LUZ")
        assert response.status_code == 200
        principles = response.json()["data"]["principles"]
        assert len(principles) == 1
        assert principles[0]["principle_id"] == "P-09"
        assert response.json()["project_id"] is None
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_cli_design_commands_are_read_only(tmp_path):
    repo = SQLiteRepository(tmp_path / "cli.sqlite")
    try:
        cli = CLI(repo)
        listed = cli.execute("/DESIGN PRINCIPLES")
        single = cli.execute("/DESIGN PRINCIPLE P-12")
        missing = cli.execute("/DESIGN PRINCIPLE P-99")
        assert len(listed["data"]["principles"]) == 15
        assert single["data"]["principle"]["name"] == "Lleno-vacío"
        assert missing["code"] == "PRINCIPLE_NOT_FOUND"
        assert repo.list_projects() == []
        assert repo.events() == []
    finally:
        repo.close()


def test_catalog_has_expected_ids_categories_and_sources():
    assert [item.principle_id for item in PRINCIPLES] == [f"P-{index:02d}" for index in range(1, 16)]
    assert all(item.category.value for item in PRINCIPLES)
    assert all(item.source != "PENDING_REFERENCE" for item in PRINCIPLES)


def test_design_principles_do_not_create_decision_or_recommendation(tmp_path):
    repo = SQLiteRepository(tmp_path / "invariants.sqlite")
    try:
        cli = CLI(repo)
        cli.execute('/PROJECT CREATE P-DESIGN "Design"')
        before = len(repo.events("P-DESIGN"))
        cli.execute("/DESIGN PRINCIPLES")
        cli.execute("/DESIGN PRINCIPLE P-01")
        project = repo.get_project("P-DESIGN")
        assert project.decisions == {}
        assert project.recommendations == {}
        assert len(repo.events("P-DESIGN")) == before
    finally:
        repo.close()
