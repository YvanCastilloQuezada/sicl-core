from __future__ import annotations

import hashlib
import json

from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.cli import CLI
from sicl.repository import SQLiteRepository
from sicl.simulation import METHODS


def setup_project(client: TestClient) -> tuple[str, str, str]:
    assert client.post("/v1/projects", json={"project_id": "P-SIM", "name": "Simulation"}).status_code == 200
    objective = client.post("/v1/projects/P-SIM/commands", json={"command": "/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80"}).json()["data"]
    alternative = client.post("/v1/projects/P-SIM/commands", json={"command": "/ALTERNATIVE CREATE Alpha"}).json()["data"]
    return objective["objective_id"], alternative["alternative_id"], "P-SIM"


def configured_client(tmp_path, monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    repo = SQLiteRepository(tmp_path / "simulation.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    return repo, TestClient(app)


def test_methods_catalog_has_all_implemented_methods(tmp_path):
    repo = SQLiteRepository(tmp_path / "catalog.sqlite")
    try:
        result = CLI(repo).execute("/SIMULATE METHODS")
        assert result["code"] == "OK"
        assert {method["method_id"] for method in result["data"]["methods"]} == {"deterministic_basic_v1", "sensitivity_linear_v1", "monte_carlo_v1"}
        assert all("inputs_required" in method and "outputs" in method for method in result["data"]["methods"])
    finally:
        repo.close()


def test_cli_deterministic_simulation_executes_and_hashes_inputs_outputs(tmp_path):
    repo = SQLiteRepository(tmp_path / "cli.sqlite")
    try:
        cli = CLI(repo)
        cli.execute('/PROJECT CREATE P-CLI "Simulation"')
        objective = cli.execute('/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80')["data"]["objective_id"]
        alternative = cli.execute('/ALTERNATIVE CREATE Alpha')["data"]["alternative_id"]
        result = cli.execute(f"/SIMULATE RUN DETERMINISTIC deterministic_basic_v1 '{json.dumps({'alternative_id': alternative, 'objective_id': objective, 'parameter_value': 82})}'")
        simulation = result["data"]["simulation"]
        assert simulation["state"] == "EXECUTED"
        assert simulation["outputs"]["objective_value"] == 82.0
        assert simulation["outputs"]["delta"] == 2.0
        expected = json.dumps({"inputs": simulation["inputs"], "outputs": simulation["outputs"]}, sort_keys=True, separators=(",", ":"), default=str)
        assert simulation["evidence_hash"] == hashlib.sha256(expected.encode()).hexdigest()
        assert result["data"]["decision_created"] is False
        assert result["data"]["recommendation_created"] is False
    finally:
        repo.close()


def test_cli_missing_inputs_is_insufficient(tmp_path):
    repo = SQLiteRepository(tmp_path / "insufficient.sqlite")
    try:
        cli = CLI(repo)
        cli.execute('/PROJECT CREATE P-INS "Simulation"')
        result = cli.execute('/SIMULATE RUN DETERMINISTIC deterministic_basic_v1 {}')
        assert result["code"] == "OK"
        assert result["data"]["simulation"]["state"] == "INSUFFICIENT"
        assert "alternative_id" in result["data"]["simulation"]["outputs"]["missing_inputs"]
    finally:
        repo.close()


def test_cli_unknown_method_and_type_mismatch(tmp_path):
    repo = SQLiteRepository(tmp_path / "errors.sqlite")
    try:
        cli = CLI(repo)
        cli.execute('/PROJECT CREATE P-ERR "Simulation"')
        assert cli.execute('/SIMULATE RUN DETERMINISTIC no_such_method {}')["code"] == "METHOD_NOT_FOUND"
        assert cli.execute('/SIMULATE RUN MONTE_CARLO deterministic_basic_v1 {}')["code"] == "METHOD_TYPE_MISMATCH"
    finally:
        repo.close()


def test_cli_sensitivity_simulation_and_list_show(tmp_path):
    repo = SQLiteRepository(tmp_path / "sensitivity.sqlite")
    try:
        cli = CLI(repo)
        cli.execute('/PROJECT CREATE P-SENS "Simulation"')
        objective = cli.execute('/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80')["data"]["objective_id"]
        alternative = cli.execute('/ALTERNATIVE CREATE Alpha')["data"]["alternative_id"]
        result = cli.execute(f"/SIMULATE RUN SENSITIVITY sensitivity_linear_v1 '{json.dumps({'alternative_id': alternative, 'objective_id': objective, 'parameter': 'height', 'range': [1, 3]})}'")
        sid = result["data"]["simulation"]["simulation_id"]
        assert result["data"]["simulation"]["state"] == "EXECUTED"
        assert cli.execute('/SIMULATE LIST')["data"]["simulations"]
        assert cli.execute(f'/SIMULATE SHOW {sid}')["data"]["simulation"]["simulation_id"] == sid
    finally:
        repo.close()


def test_http_create_list_get_and_methods(tmp_path, monkeypatch):
    repo, client = configured_client(tmp_path, monkeypatch)
    try:
        objective_id, alternative_id, project_id = setup_project(client)
        payload = {"simulation_type": "DETERMINISTIC", "method": "deterministic_basic_v1", "inputs": {"alternative_id": alternative_id, "objective_id": objective_id, "parameter_value": 82}}
        created = client.post(f"/v1/projects/{project_id}/simulations", json=payload)
        assert created.status_code == 200
        assert created.json()["contract_version"] == "1.0"
        simulation = created.json()["data"]["simulation"]
        assert simulation["state"] == "EXECUTED"
        listed = client.get(f"/v1/projects/{project_id}/simulations")
        individual = client.get(f"/v1/projects/{project_id}/simulations/{simulation['simulation_id']}")
        methods = client.get("/v1/simulations/methods")
        assert len(listed.json()["data"]["simulations"]) == 1
        assert individual.json()["data"]["simulation"]["simulation_id"] == simulation["simulation_id"]
        assert len(methods.json()["data"]["methods"]) == 3
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_http_unknown_method_is_404(tmp_path, monkeypatch):
    repo, client = configured_client(tmp_path, monkeypatch)
    try:
        _, alternative_id, project_id = setup_project(client)
        response = client.post(f"/v1/projects/{project_id}/simulations", json={"simulation_type": "DETERMINISTIC", "method": "missing", "inputs": {"alternative_id": alternative_id}})
        assert response.status_code == 404
        assert response.json()["detail"]["code"] == "METHOD_NOT_FOUND"
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_http_incomplete_inputs_422_and_type_mismatch_409(tmp_path, monkeypatch):
    repo, client = configured_client(tmp_path, monkeypatch)
    try:
        _, alternative_id, project_id = setup_project(client)
        incomplete = client.post(f"/v1/projects/{project_id}/simulations", json={"simulation_type": "DETERMINISTIC", "method": "deterministic_basic_v1", "inputs": {"alternative_id": alternative_id}})
        mismatch = client.post(f"/v1/projects/{project_id}/simulations", json={"simulation_type": "MONTE_CARLO", "method": "deterministic_basic_v1", "inputs": {}})
        assert incomplete.status_code == 422
        assert incomplete.json()["detail"]["code"] == "INSUFFICIENT_INPUTS"
        assert mismatch.status_code == 409
        assert mismatch.json()["detail"]["code"] == "METHOD_TYPE_MISMATCH"
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_simulation_does_not_create_recommendation_or_decision(tmp_path, monkeypatch):
    repo, client = configured_client(tmp_path, monkeypatch)
    try:
        objective_id, alternative_id, project_id = setup_project(client)
        client.post(f"/v1/projects/{project_id}/simulations", json={"simulation_type": "DETERMINISTIC", "method": "deterministic_basic_v1", "inputs": {"alternative_id": alternative_id, "objective_id": objective_id, "parameter_value": 82}})
        snapshot = client.get(f"/v1/projects/{project_id}/snapshot").json()["data"]["snapshot"]
        assert snapshot["recommendations"] == {}
        assert snapshot["decisions"] == {}
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_simulation_persists_after_restart(tmp_path, monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    db = tmp_path / "restart.sqlite"
    repo = SQLiteRepository(db, check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    with TestClient(app) as client:
        objective_id, alternative_id, project_id = setup_project(client)
        client.post(f"/v1/projects/{project_id}/simulations", json={"simulation_type": "DETERMINISTIC", "method": "deterministic_basic_v1", "inputs": {"alternative_id": alternative_id, "objective_id": objective_id, "parameter_value": 82}})
    repo.close()
    restarted = SQLiteRepository(db, check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: restarted
    try:
        with TestClient(app) as client:
            assert len(client.get(f"/v1/projects/{project_id}/simulations").json()["data"]["simulations"]) == 1
    finally:
        app.dependency_overrides.clear()
        restarted.close()


def test_simulation_is_append_only(tmp_path):
    repo = SQLiteRepository(tmp_path / "append.sqlite")
    try:
        cli = CLI(repo)
        cli.execute('/PROJECT CREATE P-APP "Simulation"')
        result = cli.execute('/SIMULATE RUN DETERMINISTIC deterministic_basic_v1 {}')
        sid = result["data"]["simulation"]["simulation_id"]
        for statement in (f"UPDATE simulations SET state='FAILED' WHERE simulation_id='{sid}'", f"DELETE FROM simulations WHERE simulation_id='{sid}'"):
            try:
                repo.conn.execute(statement)
                assert False, "Simulation must be append-only"
            except Exception as exc:
                assert "append-only" in str(exc)
    finally:
        repo.close()
