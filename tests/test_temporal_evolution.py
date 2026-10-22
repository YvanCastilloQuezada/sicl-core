from __future__ import annotations

import sqlite3

import pytest
from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.cli import CLI
from sicl.repository import SQLiteRepository


def setup(repo: SQLiteRepository) -> CLI:
    cli = CLI(repo, actor="owner")
    assert cli.execute('/PROJECT CREATE EVO-1 "Temporal evolution"')["code"] == "OK"
    assert cli.execute('/PROJECT OPEN EVO-1')["code"] == "OK"
    assert cli.execute('/CYCLE CREATE C-2030 2030 2026-01-01')["code"] == "OK"
    assert cli.execute('/CYCLE CREATE C-2040 2040 2026-01-01')["code"] == "OK"
    assert cli.execute('/SCENARIO CREATE S-A C-2030 "Adaptive"')["code"] == "OK"
    return cli


def create_evolution(cli: CLI):
    return cli.execute('/EVOLUTION CREATE EV-1 S-A C-2030 C-2040')


def test_create_add_apply_evolution_requires_human_authority(tmp_path):
    repo = SQLiteRepository(tmp_path / "evolution.sqlite")
    cli = setup(repo)
    assert create_evolution(cli)["code"] == "OK"
    assert cli.execute('/EVOLUTION ADD CHANGE EV-1 FAR 6.0')["code"] == "OK"
    assert cli.execute('/EVOLUTION ADD TRIGGER EV-1 demand increased')["code"] == "OK"
    blocked = cli.execute('/EVOLUTION APPLY EV-1 "" ""')
    assert blocked["code"] == "HUMAN_AUTHORITY_REQUIRED"
    applied = cli.execute('/EVOLUTION APPLY EV-1 Yvan PRODUCT_OWNER')
    assert applied["code"] == "OK"
    assert applied["data"]["evolution"]["state"] == "APPLIED"
    assert applied["data"]["decision_created"] is False
    assert applied["data"]["recommendation_created"] is False
    repo.close()


def test_evolution_does_not_modify_previous_cycle_or_scenario(tmp_path):
    repo = SQLiteRepository(tmp_path / "past.sqlite")
    cli = setup(repo)
    before_cycle = repo.get_cycle("EVO-1", "C-2030")
    before_scenario = repo.get_scenario("EVO-1", "S-A")
    create_evolution(cli)
    cli.execute('/EVOLUTION ADD CHANGE EV-1 FAR 6.0')
    cli.execute('/EVOLUTION APPLY EV-1 Yvan PRODUCT_OWNER')
    after_cycle = repo.get_cycle("EVO-1", "C-2030")
    after_scenario = repo.get_scenario("EVO-1", "S-A")
    assert before_cycle == after_cycle
    assert before_scenario == after_scenario
    assert repo.get_project("EVO-1").decisions == {}
    assert repo.get_project("EVO-1").recommendations == {}
    repo.close()


def test_evolution_persists_and_history_has_versions(tmp_path):
    path = tmp_path / "persist.sqlite"
    repo = SQLiteRepository(path)
    cli = setup(repo)
    create_evolution(cli)
    cli.execute('/EVOLUTION ADD CHANGE EV-1 FAR 6.0')
    repo.close()
    reopened = SQLiteRepository(path)
    loaded = reopened.get_scenario_evolution("EVO-1", "EV-1")
    assert loaded is not None
    assert loaded.changes == [{"key": "FAR", "value": "6.0"}]
    assert loaded.version == 2
    assert reopened.conn.execute("SELECT COUNT(*) FROM scenario_evolutions WHERE evolution_id='EV-1'").fetchone()[0] == 2
    reopened.close()


def test_evolution_table_is_append_only(tmp_path):
    repo = SQLiteRepository(tmp_path / "append.sqlite")
    cli = setup(repo)
    create_evolution(cli)
    with pytest.raises(sqlite3.IntegrityError):
        repo.conn.execute("UPDATE scenario_evolutions SET state='REJECTED'")
    with pytest.raises(sqlite3.IntegrityError):
        repo.conn.execute("DELETE FROM scenario_evolutions")
    repo.close()


def test_evolution_http_endpoints(tmp_path, monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    repo = SQLiteRepository(tmp_path / "http.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    try:
        client = TestClient(app)
        assert client.post('/v1/projects', json={"project_id": "HTTP-EVO", "name": "HTTP evolution"}).status_code == 200
        assert client.post('/v1/projects/HTTP-EVO/cycles', json={"cycle_id": "C-2030", "horizon": "2030", "start_date": "2026-01-01"}).status_code == 200
        assert client.post('/v1/projects/HTTP-EVO/cycles', json={"cycle_id": "C-2040", "horizon": "2040", "start_date": "2026-01-01"}).status_code == 200
        assert client.post('/v1/projects/HTTP-EVO/scenarios', json={"branch_id": "S-A", "parent_cycle_id": "C-2030", "scenario_name": "Adaptive"}).status_code == 200
        created = client.post('/v1/projects/HTTP-EVO/scenario-evolutions', json={"evolution_id": "EV-1", "scenario_id": "S-A", "from_cycle_id": "C-2030", "to_cycle_id": "C-2040"})
        assert created.status_code == 200
        assert client.get('/v1/projects/HTTP-EVO/scenario-evolutions').json()["data"]["evolutions"][0]["state"] == "PROPOSED"
        assert client.get('/v1/projects/HTTP-EVO/scenario-evolutions/EV-1').status_code == 200
        applied = client.post('/v1/scenario-evolutions/EV-1/apply', json={"actor": "Yvan", "authority": "PRODUCT_OWNER"})
        assert applied.status_code == 200
        assert applied.json()["data"]["evolution"]["state"] == "APPLIED"
    finally:
        app.dependency_overrides.clear()
        repo.close()
