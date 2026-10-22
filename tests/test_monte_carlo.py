from __future__ import annotations

import hashlib
import json
import shlex

from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.cli import CLI
from sicl.repository import SQLiteRepository


def setup_cli(tmp_path):
    repo = SQLiteRepository(tmp_path / "mc.sqlite")
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE P-MC "Monte Carlo"')
    objective_id = cli.execute('/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80')["data"]["objective_id"]
    alternative = cli.execute('/ALTERNATIVE CREATE Alpha')['data']
    alternative_id = alternative['alternative_id']
    cli.execute('/ALTERNATIVE SET Alpha height 10')
    return repo, cli, objective_id, alternative_id


def test_monte_carlo_is_reproducible_and_hash_includes_seed(tmp_path):
    repo, cli, objective_id, alternative_id = setup_cli(tmp_path)
    try:
        payload = {"alternative_id": alternative_id, "objective_id": objective_id, "parameter_name": "height", "parameter_distribution": {"type": "NORMAL", "parameters": {"mean": 10, "std_dev": 1}}, "iterations": 1000, "seed": 20260916}
        encoded = shlex.quote(json.dumps(payload, sort_keys=True))
        first = cli.execute(f"/SIMULATE RUN MONTE_CARLO monte_carlo_v1 {encoded}")["data"]["simulation"]
        second = cli.execute(f"/SIMULATE RUN MONTE_CARLO monte_carlo_v1 {encoded}")["data"]["simulation"]
        assert first["outputs"] == second["outputs"]
        assert first["outputs"]["samples_count"] == 1000
        assert first["outputs"]["convergence_check"] is True
        canonical = json.dumps({"inputs": first["inputs"], "outputs": first["outputs"], "seed": 20260916}, sort_keys=True, separators=(",", ":"), default=str)
        assert first["evidence_hash"] == hashlib.sha256(canonical.encode()).hexdigest()
    finally:
        repo.close()


def test_monte_carlo_cli_short_form_and_distributions(tmp_path):
    repo, cli, objective_id, alternative_id = setup_cli(tmp_path)
    try:
        command = f'/SIMULATE MONTE_CARLO {alternative_id} {objective_id} height {shlex.quote(json.dumps({"type": "UNIFORM", "parameters": {"low": 1, "high": 3}}))} 10'
        result = cli.execute(command)
        assert result["code"] == "OK"
        assert result["data"]["simulation"]["outputs"]["samples_count"] == 10
    finally:
        repo.close()


def test_monte_carlo_rejects_unknown_parameter_and_invalid_distribution(tmp_path):
    repo, cli, objective_id, alternative_id = setup_cli(tmp_path)
    try:
        missing = cli.execute(f'/SIMULATE RUN MONTE_CARLO monte_carlo_v1 {shlex.quote(json.dumps({"alternative_id": alternative_id, "objective_id": objective_id, "parameter_name": "unknown", "parameter_distribution": {"type": "NORMAL", "parameters": {"mean": 1, "std_dev": 1}}}))}')
        invalid = cli.execute(f'/SIMULATE RUN MONTE_CARLO monte_carlo_v1 {shlex.quote(json.dumps({"alternative_id": alternative_id, "objective_id": objective_id, "parameter_name": "height", "parameter_distribution": {"type": "EXPONENTIAL", "parameters": {}}}))}')
        assert missing["code"] == "PARAMETER_NOT_FOUND"
        assert invalid["code"] == "INVALID_DISTRIBUTION"
    finally:
        repo.close()


def test_monte_carlo_http_endpoint(tmp_path, monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    repo = SQLiteRepository(tmp_path / "mc-http.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    try:
        with TestClient(app) as client:
            client.post("/v1/projects", json={"project_id": "P-MC-HTTP", "name": "Monte Carlo"})
            objective = client.post("/v1/projects/P-MC-HTTP/commands", json={"command": "/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80"}).json()["data"]["objective_id"]
            alternative = client.post("/v1/projects/P-MC-HTTP/commands", json={"command": "/ALTERNATIVE CREATE Alpha"}).json()["data"]["alternative_id"]
            client.post("/v1/projects/P-MC-HTTP/commands", json={"command": "/ALTERNATIVE SET Alpha height 10"})
            response = client.post("/v1/projects/P-MC-HTTP/simulations", json={"simulation_type": "MONTE_CARLO", "method": "monte_carlo_v1", "inputs": {"alternative_id": alternative, "objective_id": objective, "parameter_name": "height", "parameter_distribution": {"type": "TRIANGULAR", "parameters": {"low": 8, "mode": 10, "high": 12}}, "iterations": 100}})
            assert response.status_code == 200
            assert response.json()["data"]["simulation"]["outputs"]["samples_count"] == 100
    finally:
        app.dependency_overrides.clear()
        repo.close()


def test_monte_carlo_rejects_iteration_limit(tmp_path):
    repo, cli, objective_id, alternative_id = setup_cli(tmp_path)
    try:
        result = cli.execute(f'/SIMULATE RUN MONTE_CARLO monte_carlo_v1 {shlex.quote(json.dumps({"alternative_id": alternative_id, "objective_id": objective_id, "parameter_name": "height", "parameter_distribution": {"type": "NORMAL", "parameters": {"mean": 1, "std_dev": 1}}, "iterations": 10001}))}')
        assert result["code"] == "INVALID_INPUTS"
    finally:
        repo.close()


def test_monte_carlo_does_not_create_decision_or_recommendation(tmp_path):
    repo, cli, objective_id, alternative_id = setup_cli(tmp_path)
    try:
        cli.execute(f'/SIMULATE RUN MONTE_CARLO monte_carlo_v1 {shlex.quote(json.dumps({"alternative_id": alternative_id, "objective_id": objective_id, "parameter_name": "height", "parameter_distribution": {"type": "NORMAL", "parameters": {"mean": 1, "std_dev": 1}}}))}')
        snapshot = repo.get_project("P-MC").__dict__
        assert snapshot["decisions"] == {}
        assert snapshot["recommendations"] == {}
    finally:
        repo.close()


def test_monte_carlo_seed_is_recorded_in_output(tmp_path):
    repo, cli, objective_id, alternative_id = setup_cli(tmp_path)
    try:
        result = cli.execute(f'/SIMULATE RUN MONTE_CARLO monte_carlo_v1 {shlex.quote(json.dumps({"alternative_id": alternative_id, "objective_id": objective_id, "parameter_name": "height", "parameter_distribution": {"type": "NORMAL", "parameters": {"mean": 1, "std_dev": 1}}}))}')
        assert result["data"]["simulation"]["outputs"]["seed"] == 20260916
    finally:
        repo.close()


def test_monte_carlo_persists_after_reload(tmp_path):
    repo, cli, objective_id, alternative_id = setup_cli(tmp_path)
    db = tmp_path / "mc.sqlite"
    try:
        cli.execute(f'/SIMULATE RUN MONTE_CARLO monte_carlo_v1 {shlex.quote(json.dumps({"alternative_id": alternative_id, "objective_id": objective_id, "parameter_name": "height", "parameter_distribution": {"type": "NORMAL", "parameters": {"mean": 1, "std_dev": 1}}, "iterations": 10}))}')
    finally:
        repo.close()
    restarted = SQLiteRepository(db)
    try:
        assert len(restarted.list_simulations("P-MC")) == 1
    finally:
        restarted.close()


def test_monte_carlo_sources_are_not_decisions(tmp_path):
    repo, cli, objective_id, alternative_id = setup_cli(tmp_path)
    try:
        result = cli.execute(f'/SIMULATE RUN MONTE_CARLO monte_carlo_v1 {shlex.quote(json.dumps({"alternative_id": alternative_id, "objective_id": objective_id, "parameter_name": "height", "parameter_distribution": {"type": "UNIFORM", "parameters": {"low": 1, "high": 2}}, "iterations": 5}))}')
        assert result["data"]["simulation"]["state"] == "EXECUTED"
        assert result["data"]["decision_created"] is False
        assert result["data"]["recommendation_created"] is False
    finally:
        repo.close()
