from __future__ import annotations

import sqlite3

from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.cli import CLI
from sicl.domain import SpatialScope, TemporalScope
from sicl.repository import SQLiteRepository


def test_project_defaults_to_undeclared_spatial_and_project_temporal():
    repo = SQLiteRepository()
    result = CLI(repo).execute('/PROJECT CREATE P-001 "Test"')
    assert result["code"] == "OK"
    project = repo.get_project("P-001")
    assert project.spatial_scope is None
    assert project.temporal_scope is TemporalScope.PROYECTO


def test_project_create_with_valid_scopes_persists():
    repo = SQLiteRepository()
    result = CLI(repo).execute('/PROJECT CREATE P-002 "Building" edificacion escenario_2030')
    assert result["code"] == "OK"
    project = repo.get_project("P-002")
    assert project.spatial_scope is SpatialScope.EDIFICACION
    assert project.temporal_scope is TemporalScope.ESCENARIO_2030


def test_project_create_invalid_scope_returns_invalid_scope():
    repo = SQLiteRepository()
    result = CLI(repo).execute('/PROJECT CREATE P-003 "Invalid" planeta')
    assert result["code"] == "INVALID_SCOPE"
    assert repo.get_project("P-003") is None


def test_project_set_scope_emits_append_only_event():
    repo = SQLiteRepository()
    cli = CLI(repo, actor="architect")
    assert cli.execute('/PROJECT CREATE P-004 "Scope"')["code"] == "OK"
    result = cli.execute('/PROJECT SET SCOPE parcela_sitio mediano_plazo')
    assert result["code"] == "OK"
    project = repo.get_project("P-004")
    assert project.spatial_scope is SpatialScope.PARCELA_SITIO
    assert project.temporal_scope is TemporalScope.MEDIANO_PLAZO
    event = repo.events("P-004")[-1]
    assert event.type == "SCOPE_CHANGED"
    assert event.actor == "architect"
    assert event.payload["spatial_scope"] == "parcela_sitio"


def test_project_set_scope_invalid_returns_invalid_scope_without_mutation():
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE P-INVALID-SET "Scope"')
    result = cli.execute('/PROJECT SET SCOPE universo')
    assert result["code"] == "INVALID_SCOPE"
    project = repo.get_project("P-INVALID-SET")
    assert project.spatial_scope is None
    assert len(repo.events("P-INVALID-SET")) == 1


def test_project_scope_survives_reload(tmp_path):
    db = tmp_path / "scope.sqlite"
    first = SQLiteRepository(db)
    cli = CLI(first)
    cli.execute('/PROJECT CREATE P-005 "Persistent" distrito_ciudad largo_plazo')
    first.close()
    second = SQLiteRepository(db)
    project = second.get_project("P-005")
    assert project.spatial_scope is SpatialScope.DISTRITO_CIUDAD
    assert project.temporal_scope is TemporalScope.LARGO_PLAZO


def test_existing_projects_migrate_without_scope(tmp_path):
    db_path = tmp_path / "legacy.sqlite"
    db = sqlite3.connect(db_path)
    db.executescript("CREATE TABLE projects (project_id TEXT PRIMARY KEY, name TEXT NOT NULL, stage TEXT NOT NULL, version INTEGER NOT NULL);")
    db.execute("INSERT INTO projects VALUES ('LEGACY', 'Legacy', 'DRAFT', 1)")
    db.commit()
    db.close()
    repo = SQLiteRepository(db_path)
    legacy = repo.get_project("LEGACY")
    assert legacy.spatial_scope is None
    assert legacy.temporal_scope is TemporalScope.PROYECTO


def test_api_create_and_get_expose_scopes(tmp_path):
    repo = SQLiteRepository(tmp_path / "api.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    try:
        with TestClient(app) as client:
            response = client.post("/projects", json={"project_id": "API-001", "name": "API", "spatial_scope": "region", "temporal_scope": "escenario_2040"})
            assert response.status_code == 201
            assert response.json()["data"]["spatial_scope"] == "region"
            fetched = client.get("/projects/API-001")
            assert fetched.status_code == 200
            assert fetched.json()["data"]["spatial_scope"] == "region"
            assert fetched.json()["data"]["temporal_scope"] == "escenario_2040"
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_api_invalid_scope_returns_bad_request(tmp_path):
    repo = SQLiteRepository(tmp_path / "api-invalid.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    try:
        with TestClient(app) as client:
            response = client.post("/projects", json={"project_id": "API-002", "name": "API", "spatial_scope": "unknown"})
            assert response.status_code == 400
            assert response.json()["detail"]["code"] == "INVALID_SCOPE"
    finally:
        app.dependency_overrides.clear()
        repo.close()



def test_rfc019_exposes_eleven_canonical_scopes_and_labels():
    expected = [
        "pais", "macro_region", "region", "provincia_metropoli",
        "distrito_ciudad", "zona_barrio_sector", "parcela_sitio",
        "edificacion", "sistema", "espacio", "objeto",
    ]
    assert [scope.value for scope in SpatialScope] == expected
    assert SpatialScope.MACRO_REGION.label == "Macro-región"
    assert SpatialScope.SISTEMA.label == "Sistema"


def test_rfc019_parent_child_chain_has_eleven_scopes():
    from sicl.multiscale import SCALE_ORDER, children_scopes, parent_scope

    assert len(SCALE_ORDER) == 11
    assert parent_scope("macro_region") is SpatialScope.PAIS
    assert children_scopes("pais") == [SpatialScope.MACRO_REGION]
    assert parent_scope("sistema") is SpatialScope.EDIFICACION
    assert children_scopes("sistema") == [SpatialScope.ESPACIO]
    assert parent_scope("objeto") is SpatialScope.ESPACIO


def test_rfc019_new_scopes_support_ancestor_relations():
    from sicl.multiscale import is_ancestor

    assert is_ancestor("pais", "sistema")
    assert is_ancestor("edificacion", "objeto")
    assert not is_ancestor("sistema", "edificacion")
