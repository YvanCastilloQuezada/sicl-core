from __future__ import annotations

import json
import shlex
import sqlite3

import pytest

from sicl.cli import CLI
from sicl.repository import SQLiteRepository


def setup_project(tmp_path):
    repo = SQLiteRepository(tmp_path / "extended-generation.sqlite")
    cli = CLI(repo, actor="architect")
    assert cli.execute('/PROJECT CREATE GEN-EXT "Extended Generation"')["code"] == "OK"
    assert cli.execute('/PROJECT OPEN GEN-EXT')["code"] == "OK"
    objective = cli.execute('/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80')["data"]["objective_id"]
    alternative = cli.execute('/ALTERNATIVE CREATE BASELINE')["data"]["alternative_id"]
    cli.execute('/ALTERNATIVE SET BASELINE HEIGHT 6')
    return cli, repo, objective, alternative


def evolutionary_command(alternative, objective, **overrides):
    inputs = {
        "base_alternatives": [alternative],
        "objectives": [objective],
        "population_size": 6,
        "generations": 3,
        "mutation_rate": 0.2,
        "crossover_rate": 0.7,
        "seed": 42,
    }
    inputs.update(overrides)
    return f"/GENERATE DESIGN evolutionary_v1 {shlex.quote(json.dumps(inputs, sort_keys=True))}"


def test_evolutionary_generates_population_and_outputs(tmp_path):
    cli, repo, objective, alternative = setup_project(tmp_path)
    try:
        result = cli.execute(evolutionary_command(alternative, objective))
        assert result["code"] == "OK"
        generation = result["data"]["generation"]
        assert generation["method"] == "RULE_BASED"
        assert generation["state"] == "GENERATED"
        assert len(generation["outputs"]["final_population"]) == 6
        assert len(generation["outputs"]["best_candidates"]) == 3
        assert len(generation["outputs"]["generation_log"]) == 3
        assert generation["outputs"]["seed"] == 42
        assert result["data"]["decision_created"] is False
        assert result["data"]["recommendation_created"] is False
    finally:
        repo.close()


def test_evolutionary_is_deterministic_for_same_seed(tmp_path):
    cli, repo, objective, alternative = setup_project(tmp_path)
    try:
        first = cli.execute(evolutionary_command(alternative, objective, seed=99))["data"]["generation"]
        second = cli.execute(evolutionary_command(alternative, objective, seed=99))["data"]["generation"]
        assert first["outputs"] == second["outputs"]
    finally:
        repo.close()


@pytest.mark.parametrize("overrides", [{"population_size": 101}, {"generations": 51}, {"mutation_rate": 1.1}, {"crossover_rate": -0.1}])
def test_evolutionary_rejects_invalid_parameters(tmp_path, overrides):
    cli, repo, objective, alternative = setup_project(tmp_path)
    try:
        result = cli.execute(evolutionary_command(alternative, objective, **overrides))
        assert result["code"] == "INVALID_INPUTS"
    finally:
        repo.close()


def test_llm_assisted_is_defined_but_not_configured(tmp_path):
    cli, repo, objective, alternative = setup_project(tmp_path)
    try:
        payload = {"context": "A project", "objectives": [objective], "constraints": [], "num_candidates": 3}
        result = cli.execute(f"/GENERATE DESIGN llm_assisted_v1 {shlex.quote(json.dumps(payload))}")
        assert result["code"] == "LLM_NOT_CONFIGURED"
        assert not repo.list_generations("GEN-EXT")
    finally:
        repo.close()


def test_catalog_marks_advanced_methods_correctly(tmp_path):
    cli, repo, _, _ = setup_project(tmp_path)
    try:
        catalog = {item["name"]: item for item in cli.execute('/GENERATE METHODS')["data"]["methods"]}
        assert len(catalog) == 4
        assert catalog["evolutionary_v1"]["status"] == "ACTIVE"
        assert catalog["evolutionary_v1"]["active"] is True
        assert catalog["llm_assisted_v1"]["status"] == "DEFINED_NOT_CONFIGURED"
        assert catalog["llm_assisted_v1"]["active"] is False
    finally:
        repo.close()


def test_evolutionary_persists_and_is_append_only(tmp_path):
    cli, repo, objective, alternative = setup_project(tmp_path)
    generation_id = cli.execute(evolutionary_command(alternative, objective))["data"]["generation"]["generation_id"]
    db = repo.path
    repo.close()
    reopened = SQLiteRepository(db)
    try:
        loaded = reopened.get_generation("GEN-EXT", generation_id)
        assert loaded is not None
        assert len(loaded.candidates) == 6
        with pytest.raises(sqlite3.IntegrityError):
            reopened.conn.execute(f"UPDATE generated_alternatives SET rationale='tampered' WHERE generation_id='{generation_id}'")
        with pytest.raises(sqlite3.IntegrityError):
            reopened.conn.execute(f"DELETE FROM generated_alternatives WHERE generation_id='{generation_id}'")
    finally:
        reopened.close()


def test_evolutionary_does_not_create_decision_or_recommendation(tmp_path):
    cli, repo, objective, alternative = setup_project(tmp_path)
    try:
        cli.execute(evolutionary_command(alternative, objective))
        project = repo.get_project("GEN-EXT")
        assert project is not None
        assert project.decisions == {}
        assert project.recommendations == {}
    finally:
        repo.close()
