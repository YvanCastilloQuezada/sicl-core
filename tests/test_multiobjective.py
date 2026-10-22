from __future__ import annotations

import sqlite3

from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.cli import CLI
from sicl.repository import SQLiteRepository


def setup_project(repo: SQLiteRepository) -> tuple[CLI, str, str, str]:
    cli = CLI(repo, actor="tester")
    cli.execute('/PROJECT CREATE P-MOBJ "Multiobjective"')
    objective_a = cli.execute('/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80')["data"]["objective_id"]
    objective_b = cli.execute('/OBJECTIVE SET CONSTRUCTION_COST MINIMIZE 80')["data"]["objective_id"]
    alt_a = cli.execute('/ALTERNATIVE CREATE Alpha')["data"]["alternative_id"]
    alt_b = cli.execute('/ALTERNATIVE CREATE Beta')["data"]["alternative_id"]
    cli.execute('/EVALUATE ALPHA ENERGY_SAVINGS 90 ENERGY_SAVINGS 1 USER_INPUT')
    cli.execute('/EVALUATE ALPHA CONSTRUCTION_COST 80 USD 1 USER_INPUT')
    cli.execute('/EVALUATE BETA ENERGY_SAVINGS 70 ENERGY_SAVINGS 1 USER_INPUT')
    cli.execute('/EVALUATE BETA CONSTRUCTION_COST 100 USD 1 USER_INPUT')
    return cli, objective_a, objective_b, alt_a


def test_cli_pareto_persists_expected_result(tmp_path):
    repo = SQLiteRepository(tmp_path / "pareto.sqlite")
    try:
        cli, objective_a, objective_b, _ = setup_project(repo)
        result = cli.execute(f'/MULTIOBJECTIVE PARETO ENERGY_SAVINGS CONSTRUCTION_COST')
        assert result["code"] == "OK"
        record = result["data"]["multiobjective"]
        assert record["method"] == "pareto_front_v1"
        assert record["state"] == "EXECUTED"
        assert len(record["pareto_front"]) == 1
        assert len(record["dominated"]) == 1
        assert result["data"]["decision_created"] is False
        assert result["data"]["recommendation_created"] is False
        assert record["objectives"] == ["ENERGY_SAVINGS", "CONSTRUCTION_COST"]
    finally:
        repo.close()


def test_cli_tradeoffs_has_matrix_and_list_show(tmp_path):
    repo = SQLiteRepository(tmp_path / "tradeoffs.sqlite")
    try:
        cli, _, _, _ = setup_project(repo)
        result = cli.execute('/MULTIOBJECTIVE TRADEOFFS ENERGY_SAVINGS CONSTRUCTION_COST')
        record = result["data"]["multiobjective"]
        assert record["method"] == "tradeoff_matrix_v1"
        assert "matrix" in record["tradeoffs"]
        result_id = record["multiobjective_id"]
        assert cli.execute('/MULTIOBJECTIVE LIST')["data"]["multiobjectives"]
        assert cli.execute(f'/MULTIOBJECTIVE SHOW {result_id}')["data"]["multiobjective"]["multiobjective_id"] == result_id
    finally:
        repo.close()


def test_incomplete_result_and_objective_errors(tmp_path):
    repo = SQLiteRepository(tmp_path / "incomplete.sqlite")
    try:
        cli = CLI(repo)
        cli.execute('/PROJECT CREATE P-INCOMPLETE "Incomplete"')
        cli.execute('/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80')
        cli.execute('/OBJECTIVE SET CONSTRUCTION_COST MINIMIZE 80')
        cli.execute('/ALTERNATIVE CREATE Alpha')
        result = cli.execute('/MULTIOBJECTIVE PARETO ENERGY_SAVINGS CONSTRUCTION_COST')
        assert result["code"] == "OK"
        assert result["data"]["multiobjective"]["state"] == "INSUFFICIENT"
        assert result["data"]["multiobjective"]["incomplete"]
        assert cli.execute('/MULTIOBJECTIVE PARETO ENERGY_SAVINGS')["code"] == "INVALID_ARGUMENT"
        assert cli.execute('/MULTIOBJECTIVE PARETO UNKNOWN CONSTRUCTION_COST')["code"] == "OBJECTIVE_NOT_FOUND"
    finally:
        repo.close()


def test_objective_direction_is_required(tmp_path):
    repo = SQLiteRepository(tmp_path / "direction.sqlite")
    try:
        cli = CLI(repo)
        cli.execute('/PROJECT CREATE P-DIRECTION "Direction"')
        cli.execute('/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80')
        cli.execute('/OBJECTIVE SET CONSTRUCTION_COST MINIMIZE 80')
        repo.conn.execute("UPDATE objectives SET direction='' WHERE key='ENERGY_SAVINGS'")
        repo.conn.commit()
        result = cli.execute('/MULTIOBJECTIVE PARETO ENERGY_SAVINGS CONSTRUCTION_COST')
        assert result["code"] == "OBJECTIVE_DIRECTION_REQUIRED"
    finally:
        repo.close()


def test_multiobjective_survives_restart_and_is_append_only(tmp_path):
    path = tmp_path / "restart.sqlite"
    repo = SQLiteRepository(path)
    cli, _, _, _ = setup_project(repo)
    result = cli.execute('/MULTIOBJECTIVE PARETO ENERGY_SAVINGS CONSTRUCTION_COST')
    result_id = result["data"]["multiobjective"]["multiobjective_id"]
    repo.close()
    reopened = SQLiteRepository(path)
    try:
        restored = reopened.get_multiobjective_result("P-MOBJ", result_id)
        assert restored is not None
        assert restored.multiobjective_id == result_id
        try:
            reopened.conn.execute("UPDATE multiobjective_results SET method='changed'")
            raise AssertionError("UPDATE should fail")
        except sqlite3.IntegrityError:
            pass
        try:
            reopened.conn.execute("DELETE FROM multiobjective_results")
            raise AssertionError("DELETE should fail")
        except sqlite3.IntegrityError:
            pass
    finally:
        reopened.close()


def test_http_multiobjective_endpoints(tmp_path, monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    repo = SQLiteRepository(tmp_path / "http.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    try:
        cli, _, _, _ = setup_project(repo)
        created = TestClient(app).post('/v1/projects/P-MOBJ/multiobjective/pareto', json={"objectives": ["ENERGY_SAVINGS", "CONSTRUCTION_COST"]})
        assert created.status_code == 200
        body = created.json()
        result_id = body["data"]["multiobjective"]["multiobjective_id"]
        assert body["contract_version"] == "1.0"
        tradeoffs = TestClient(app).post('/v1/projects/P-MOBJ/multiobjective/tradeoffs', json={"objectives": ["ENERGY_SAVINGS", "CONSTRUCTION_COST"]})
        assert tradeoffs.status_code == 200
        listed = TestClient(app).get('/v1/projects/P-MOBJ/multiobjective')
        assert listed.status_code == 200
        assert len(listed.json()["data"]["multiobjectives"]) == 2
        individual = TestClient(app).get(f'/v1/projects/P-MOBJ/multiobjective/{result_id}')
        assert individual.status_code == 200
        assert individual.json()["project_id"] == "P-MOBJ"
    finally:
        app.dependency_overrides.clear()
        repo.close()
