from __future__ import annotations

from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.cli import CLI
from sicl.domain import ScaleRelationType, SpatialScope
from sicl.repository import SQLiteRepository


def test_scale_hierarchy_is_explicit():
    cli = CLI(SQLiteRepository())
    assert cli.execute('/SCALE PARENT ciudad_distrito')['data']['parent'] == 'provincia_metropoli'
    assert cli.execute('/SCALE CHILDREN ciudad_distrito')['data']['children'] == ['barrio_sector']
    assert cli.execute('/SCALE PARENT pais')['data']['parent'] is None


def test_relation_requires_ancestor_scope_and_persists():
    repo = SQLiteRepository()
    cli = CLI(repo, actor='architect')
    assert cli.execute('/PROJECT CREATE CITY "City" ciudad_distrito')['code'] == 'OK'
    assert cli.execute('/PROJECT CREATE SITE "Site" parcela_sitio')['code'] == 'OK'
    result = cli.execute('/SCALE RELATE CITY SITE CONTAINS "contains site"')
    assert result['code'] == 'OK'
    relation = repo.list_scale_relations('SITE')[0]
    assert relation.relation_type is ScaleRelationType.CONTAINS
    assert relation.created_by == 'architect'
    assert repo.events('CITY')[-1].type == 'SCALE_RELATION_CREATED'


def test_contains_relation_rejects_incompatible_scopes():
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE A "A" edificio')
    cli.execute('/PROJECT CREATE B "B" ciudad_distrito')
    result = cli.execute('/SCALE RELATE A B CONTAINS')
    assert result['code'] == 'INVALID_SCOPE_RELATION'
    assert repo.list_scale_relations('A') == []


def test_objective_import_requires_relation_and_keeps_provenance():
    repo = SQLiteRepository()
    cli = CLI(repo, actor='architect')
    cli.execute('/PROJECT CREATE CITY "City" ciudad_distrito')
    source = CLI(repo, actor='architect')
    source.execute('/PROJECT OPEN CITY')
    objective = source.execute('/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80')['data']
    cli.execute('/PROJECT CREATE SITE "Site" parcela_sitio')
    blocked = cli.execute(f"/PROJECT IMPORT OBJECTIVE CITY {objective['objective_id']}")
    assert blocked['code'] == 'SCALE_RELATION_REQUIRED'
    cli.execute('/SCALE RELATE CITY SITE CONTAINS')
    imported = cli.execute(f"/PROJECT IMPORT OBJECTIVE CITY {objective['objective_id']}")
    assert imported['code'] == 'OK'
    assert imported['data']['source_parent_objective_id'] == objective['objective_id']
    assert repo.events('SITE')[-1].type == 'OBJECTIVE_IMPORTED'


def test_relation_survives_reload(tmp_path):
    path = tmp_path / 'relations.sqlite'
    first = SQLiteRepository(path)
    cli = CLI(first)
    cli.execute('/PROJECT CREATE REGION "Region" region')
    cli.execute('/PROJECT CREATE CITY "City" ciudad_distrito')
    cli.execute('/SCALE RELATE REGION CITY CONTAINS')
    first.close()
    second = SQLiteRepository(path)
    relation = second.list_scale_relations('CITY')[0]
    assert relation.parent_project_id == 'REGION'
    assert second.get_project('CITY').scale_relations[relation.relation_id].relation_type is ScaleRelationType.CONTAINS


def test_http_scales_and_relation_and_import(tmp_path, monkeypatch):
    monkeypatch.delenv('SICL_CORE_SERVICE_TOKEN', raising=False)
    repo = SQLiteRepository(tmp_path / 'api.sqlite', check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    try:
        with TestClient(app) as client:
            assert client.get('/v1/scales').status_code == 200
            assert client.post('/projects', json={'project_id': 'REGION', 'name': 'Region', 'spatial_scope': 'region'}).status_code == 201
            assert client.post('/projects', json={'project_id': 'CITY', 'name': 'City', 'spatial_scope': 'ciudad_distrito'}).status_code == 201
            objective = client.post('/v1/projects/REGION/commands', json={'command': '/OBJECTIVE SET CLIMATE MAXIMIZE 80'}).json()
            oid = objective['data']['objective_id']
            created = client.post('/v1/projects/CITY/scale-relations', json={'parent_project_id': 'REGION', 'child_project_id': 'CITY', 'relation_type': 'CONTAINS'}).json()
            assert created['code'] == 'OK'
            imported = client.post('/v1/projects/CITY/import-objective', json={'source_project_id': 'REGION', 'objective_id': oid}).json()
            assert imported['code'] == 'OK'
            assert imported['data']['objective']['source_parent_objective_id'] == oid
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_scale_relation_is_append_only():
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE REGION "Region" region')
    cli.execute('/PROJECT CREATE CITY "City" ciudad_distrito')
    cli.execute('/SCALE RELATE REGION CITY CONTAINS')
    relation_id = repo.list_scale_relations('CITY')[0].relation_id
    try:
        repo.conn.execute('UPDATE scale_relations SET description=? WHERE relation_id=?', ('x', relation_id))
        raise AssertionError('update should fail')
    except Exception as exc:
        assert 'append-only' in str(exc)
    try:
        repo.conn.execute('DELETE FROM scale_relations WHERE relation_id=?', (relation_id,))
        raise AssertionError('delete should fail')
    except Exception as exc:
        assert 'append-only' in str(exc)


def test_project_scale_scope_is_persisted():
    repo = SQLiteRepository()
    result = CLI(repo).execute('/PROJECT CREATE BUILDING "Building" edificio escenario_2030')
    assert result['code'] == 'OK'
    project = repo.get_project('BUILDING')
    assert project.spatial_scope is SpatialScope.EDIFICIO
    assert project.temporal_scope.value == 'escenario_2030'


def test_unknown_scale_command_returns_controlled_error():
    result = CLI(SQLiteRepository()).execute('/SCALE PARENT unknown')
    assert result['code'] == 'INVALID_SCOPE'


def test_relation_duplicate_is_rejected():
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE REGION "Region" region')
    cli.execute('/PROJECT CREATE CITY "City" ciudad_distrito')
    assert cli.execute('/SCALE RELATE REGION CITY CONTAINS')['code'] == 'OK'
    assert cli.execute('/SCALE RELATE REGION CITY CONTAINS')['code'] == 'CONFLICT'
