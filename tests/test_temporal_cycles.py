from __future__ import annotations

import sqlite3

import pytest
from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.cli import CLI
from sicl.repository import SQLiteRepository


def setup_project(repo: SQLiteRepository) -> CLI:
    cli = CLI(repo, actor="owner")
    assert cli.execute('/PROJECT CREATE TEMP-1 "Temporal project"')["status"] == "OK"
    return cli


def test_create_supported_horizons(tmp_path):
    repo = SQLiteRepository(tmp_path / "cycles.sqlite")
    cli = setup_project(repo)
    for year in ("2030", "2040", "2050"):
        assert cli.execute(f"/CYCLE CREATE C-{year} {year} 2026-01-01")["status"] == "OK"
    cycles = cli.execute('/CYCLE LIST')["data"]["cycles"]
    assert [item["horizon"] for item in cycles] == ["2030", "2040", "2050"]


def test_custom_cycle_and_persistence(tmp_path):
    path = tmp_path / "persist.sqlite"
    repo = SQLiteRepository(path)
    cli = setup_project(repo)
    cli.execute('/CYCLE CREATE C-CUSTOM CUSTOM 2026-01-01')
    repo.close()
    reopened = SQLiteRepository(path)
    cycle = reopened.get_cycle("TEMP-1", "C-CUSTOM")
    assert cycle is not None
    assert cycle.horizon.value == "CUSTOM"
    assert cycle.start_date.isoformat() == "2026-01-01"


def test_scenarios_branch_from_same_cycle_without_overwrite(tmp_path):
    repo = SQLiteRepository(tmp_path / "branches.sqlite")
    cli = setup_project(repo)
    cli.execute('/CYCLE CREATE C-2030 2030 2026-01-01')
    cli.execute('/SCENARIO CREATE S-A C-2030 "Adaptive growth"')
    cli.execute('/SCENARIO CREATE S-B C-2030 "Conservative growth"')
    scenarios = cli.execute('/SCENARIO LIST')["data"]["scenarios"]
    assert {item["branch_id"] for item in scenarios} == {"S-A", "S-B"}
    assert all(item["state"] == "PROPOSED" for item in scenarios)


def test_scenario_selection_requires_actor_and_human_review(tmp_path):
    repo = SQLiteRepository(tmp_path / "selection.sqlite")
    cli = setup_project(repo)
    cli.execute('/CYCLE CREATE C-2030 2030 2026-01-01')
    cli.execute('/SCENARIO CREATE S-A C-2030 "Adaptive"')
    cli.execute('/ACTOR ADD A-DEC ARCHITECT Architect DECISIONAL')
    blocked = cli.execute('/SCENARIO SELECT S-A A-DEC BOARD')
    assert blocked["code"] == "HUMAN_REVIEW_REQUIRED"
    cli.execute('/HUMAN REVIEW A-DEC 2026-09-15T00:00:00Z "Reviewed" "Scenario review" BOARD')
    selected = cli.execute('/SCENARIO SELECT S-A A-DEC BOARD')
    assert selected["data"]["scenario"]["state"] == "SELECTED"
    assert selected["data"]["scenario"]["selected_by"] == "A-DEC"


def test_selection_is_versioned_append_only_and_past_cycle_unchanged(tmp_path):
    repo = SQLiteRepository(tmp_path / "append.sqlite")
    cli = setup_project(repo)
    cli.execute('/CYCLE CREATE C-2030 2030 2026-01-01')
    cli.execute('/SCENARIO CREATE S-A C-2030 "Adaptive"')
    cli.execute('/ACTOR ADD A-DEC ARCHITECT Architect DECISIONAL')
    cli.execute('/HUMAN REVIEW A-DEC 2026-09-15T00:00:00Z "Reviewed" "Scenario review" BOARD')
    cli.execute('/SCENARIO SELECT S-A A-DEC BOARD')
    assert repo.get_cycle("TEMP-1", "C-2030").state.value == "DRAFT"
    assert repo.conn.execute("SELECT COUNT(*) FROM scenario_branches WHERE branch_id='S-A'").fetchone()[0] == 2
    with pytest.raises(sqlite3.IntegrityError):
        repo.conn.execute("DELETE FROM temporal_cycles WHERE cycle_id='C-2030'")


def test_http_temporal_endpoints(tmp_path, monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    repo = SQLiteRepository(tmp_path / "http.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    try:
        client = TestClient(app)
        assert client.post('/v1/projects', json={"project_id": "HTTP-T", "name": "Temporal HTTP"}).status_code == 200
        cycle = client.post('/v1/projects/HTTP-T/cycles', json={"cycle_id": "C-2040", "horizon": "2040", "start_date": "2026-01-01", "assumptions": ["stable demand"]})
        assert cycle.status_code == 200
        scenario = client.post('/v1/projects/HTTP-T/scenarios', json={"branch_id": "S-1", "parent_cycle_id": "C-2040", "scenario_name": "Base", "conditions": {"growth": "medium"}})
        assert scenario.status_code == 200
        assert len(client.get('/v1/projects/HTTP-T/cycles').json()["data"]["cycles"]) == 1
        assert len(client.get('/v1/projects/HTTP-T/scenarios').json()["data"]["scenarios"]) == 1
    finally:
        app.dependency_overrides.clear()
