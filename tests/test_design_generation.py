from __future__ import annotations

import json
import shlex
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.cli import CLI
from sicl.repository import SQLiteRepository


@pytest.fixture(autouse=True)
def clear_service_token(monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)


def cli_for(tmp_path: Path, project_id: str = "GEN-P"):
    repo = SQLiteRepository(tmp_path / "generation.sqlite")
    cli = CLI(repo, actor="architect")
    assert cli.execute(f'/PROJECT CREATE "{project_id}" "Generation"')["code"] == "OK"
    assert cli.execute(f"/PROJECT OPEN {project_id}")["code"] == "OK"
    return cli, repo


def client_for(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "api-generation.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    return TestClient(app), repo


def close(repo: SQLiteRepository):
    repo.close()
    app.dependency_overrides.clear()


def test_parametric_grid_generates_declared_cartesian_candidates(tmp_path: Path):
    cli, repo = cli_for(tmp_path)
    inputs = {"parameters": {"HEIGHT": [3, 6], "ORIENTATION": ["N", "S"]}}
    result = cli.execute(f"/GENERATE DESIGN parametric_grid_v1 {shlex.quote(json.dumps(inputs))}")
    assert result["code"] == "OK"
    generation = result["data"]["generation"]
    assert generation["method"] == "PARAMETRIC"
    assert generation["state"] == "GENERATED"
    assert len(generation["candidates"]) == 4
    assert generation["generation_hash"]
    repo.close()


def test_pattern_variation_generates_without_hidden_filtering(tmp_path: Path):
    cli, repo = cli_for(tmp_path)
    inputs = {"pattern": {"FLOORS": 2, "STRUCTURE": "Mampostería"}, "variations": {"FLOORS": [2, 4], "COURTYARD": [False, True]}}
    result = cli.execute(f"/GENERATE DESIGN pattern_variation_v1 {shlex.quote(json.dumps(inputs))}")
    candidates = result["data"]["generation"]["candidates"]
    assert result["code"] == "OK"
    assert len(candidates) == 4
    assert {candidate["FLOORS"] for candidate in candidates} == {2, 4}
    assert {candidate["COURTYARD"] for candidate in candidates} == {False, True}
    repo.close()


def test_generation_missing_inputs_is_insufficient(tmp_path: Path):
    cli, repo = cli_for(tmp_path)
    result = cli.execute(f"/GENERATE DESIGN parametric_grid_v1 {shlex.quote('{}')}")
    assert result["code"] == "OK"
    assert result["data"]["generation"]["state"] == "INSUFFICIENT"
    repo.close()


def test_unknown_generation_method_is_rejected(tmp_path: Path):
    cli, repo = cli_for(tmp_path)
    result = cli.execute(f"/GENERATE DESIGN llm_assisted_v1 {shlex.quote(json.dumps({'parameters': {'X': [1]}}))}")
    assert result["code"] == "METHOD_NOT_FOUND"
    repo.close()


def test_promotion_requires_human_actor_and_authority_and_creates_alternative_only(tmp_path: Path):
    cli, repo = cli_for(tmp_path)
    result = cli.execute(f"/GENERATE DESIGN parametric_grid_v1 {shlex.quote(json.dumps({'parameters': {'FLOORS': [2]}}))}")
    generation_id = result["data"]["generation"]["generation_id"]
    rejected = cli.execute(f"/ALTERNATIVE PROMOTE {generation_id} 0 architect")
    assert rejected["code"] == "INVALID_ARGUMENT"
    promoted = cli.execute(f"/ALTERNATIVE PROMOTE {generation_id} 0 architect PRODUCT_OWNER")
    assert promoted["code"] == "OK"
    alternative = promoted["data"]["alternative"]
    assert alternative["source"] == "DESIGN_GENERATION"
    project = repo.get_project("GEN-P")
    assert project and len(project.alternatives) == 1
    assert not project.decisions
    assert not project.recommendations
    repo.close()


def test_generation_persists_and_lists(tmp_path: Path):
    db = tmp_path / "persist.sqlite"
    repo = SQLiteRepository(db)
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE PERSIST "Persist"')
    cli.execute('/PROJECT OPEN PERSIST')
    created = cli.execute(f"/GENERATE DESIGN pattern_variation_v1 {shlex.quote(json.dumps({'pattern': {'MASS': 'A'}, 'variations': {'MASS': ['A', 'B']}}))}")
    generation_id = created["data"]["generation"]["generation_id"]
    repo.close()
    reopened = SQLiteRepository(db)
    loaded = reopened.get_generation("PERSIST", generation_id)
    assert loaded is not None
    assert loaded.candidates == [{"MASS": "A"}, {"MASS": "B"}]
    reopened.close()


def test_generation_tables_are_append_only(tmp_path: Path):
    cli, repo = cli_for(tmp_path)
    cli.execute(f"/GENERATE DESIGN parametric_grid_v1 {shlex.quote(json.dumps({'parameters': {'X': [1]}}))}")
    with pytest.raises(sqlite3.IntegrityError):
        repo.conn.execute("UPDATE generated_alternatives SET rationale='tampered'")
    with pytest.raises(sqlite3.IntegrityError):
        repo.conn.execute("DELETE FROM generated_alternatives")
    repo.close()


def test_cli_generation_catalog_and_listing(tmp_path: Path):
    cli, repo = cli_for(tmp_path)
    methods = cli.execute("/GENERATE METHODS")["data"]["methods"]
    assert {item["name"] for item in methods} >= {"parametric_grid_v1", "pattern_variation_v1"}
    created = cli.execute(f"/GENERATE DESIGN parametric_grid_v1 {shlex.quote(json.dumps({'parameters': {'X': [1]}}))}")
    generation_id = created["data"]["generation"]["generation_id"]
    assert cli.execute("/GENERATE LIST")["data"]["generations"][0]["generation_id"] == generation_id
    assert cli.execute(f"/GENERATE SHOW {generation_id}")["data"]["generation"]["generation_id"] == generation_id
    repo.close()


def test_http_generation_endpoints_and_promotion(tmp_path: Path):
    client, repo = client_for(tmp_path)
    created = client.post("/v1/projects", json={"project_id": "HTTP-GEN", "name": "HTTP Generation"})
    assert created.status_code == 200
    response = client.post("/v1/projects/HTTP-GEN/generations", json={"method": "parametric_grid_v1", "inputs": {"parameters": {"WIDTH": [10, 20]}}})
    assert response.status_code == 200
    generation_id = response.json()["data"]["generation"]["generation_id"]
    assert len(response.json()["data"]["generation"]["candidates"]) == 2
    assert client.get("/v1/generations/methods").status_code == 200
    assert client.get(f"/v1/projects/HTTP-GEN/generations/{generation_id}").status_code == 200
    promoted = client.post(f"/v1/projects/HTTP-GEN/generations/{generation_id}/promote", json={"candidate_index": 0, "actor": "Yvan", "authority": "PRODUCT_OWNER"})
    assert promoted.status_code == 200
    assert promoted.json()["data"]["alternative"]["source"] == "DESIGN_GENERATION"
    close(repo)
