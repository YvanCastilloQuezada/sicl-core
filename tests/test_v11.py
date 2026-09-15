from pathlib import Path

import pytest

from sicl.cli import CLI
from sicl.repository import SQLiteRepository


def seed_project(cli: CLI) -> None:
    assert cli.execute('/PROJECT CREATE V11 "UPAO v1.1"')["code"] == "OK"
    assert cli.execute('/OBJECTIVE SET CLIMATE MAXIMIZE 80')["code"] == "OK"


def test_alternative_creation(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "alternative.sqlite")
    cli = CLI(repo)
    seed_project(cli)
    assert cli.execute('/ALTERNATIVE CREATE OPCION_A')["code"] == "OK"
    state = cli.execute('/STATUS')["data"]
    alternative = next(iter(state["alternatives"].values()))
    assert alternative["name"] == "OPCION_A"
    assert alternative["status"] == "GENERATED"
    repo.close()


def test_evaluation_against_objective(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "evaluation.sqlite")
    cli = CLI(repo)
    seed_project(cli)
    cli.execute('/ALTERNATIVE CREATE OPCION_A')
    result = cli.execute('/EVALUATE OPCION_A CLIMATE 85')
    assert result["code"] == "OK"
    evaluation = next(iter(cli.execute('/STATUS')["data"]["evaluations"].values()))
    assert evaluation["value"] == 85.0
    assert evaluation["source"] == "USER_INPUT"
    repo.close()


def test_comparison_tradeoffs(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "comparison.sqlite")
    cli = CLI(repo)
    seed_project(cli)
    cli.execute('/ALTERNATIVE CREATE OPCION_A')
    cli.execute('/ALTERNATIVE CREATE OPCION_B')
    cli.execute('/EVALUATE OPCION_A CLIMATE 85')
    cli.execute('/EVALUATE OPCION_B CLIMATE 90')
    result = cli.execute('/COMPARE OPCION_A OPCION_B')
    assert result["code"] == "OK"
    comparison = next(iter(cli.execute('/STATUS')["data"]["comparisons"].values()))
    assert len(comparison["alternative_ids"]) == 2
    assert len(comparison["evaluations"]) == 2
    assert cli.execute('/COMPARE OPCION_A')["code"] == "INVALID_ARGUMENT"
    repo.close()


def test_recommendation_separated_from_decision(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "recommendation.sqlite")
    cli = CLI(repo)
    seed_project(cli)
    cli.execute('/ALTERNATIVE CREATE OPCION_A')
    cli.execute('/ALTERNATIVE CREATE OPCION_B')
    cli.execute('/EVALUATE OPCION_A CLIMATE 85')
    cli.execute('/EVALUATE OPCION_B CLIMATE 90')
    cli.execute('/COMPARE OPCION_A OPCION_B')
    result = cli.execute('/RECOMMEND')
    assert result["code"] == "OK"
    state = cli.execute('/STATUS')["data"]
    recommendation = next(iter(state["recommendations"].values()))
    assert recommendation["status"] == "PENDING_APPROVAL"
    assert state["decisions"] == {}
    repo.close()


def test_recommendation_requires_human_approval(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "approval.sqlite")
    cli = CLI(repo)
    seed_project(cli)
    cli.execute('/ALTERNATIVE CREATE OPCION_A')
    cli.execute('/ALTERNATIVE CREATE OPCION_B')
    cli.execute('/EVALUATE OPCION_A CLIMATE 85')
    cli.execute('/EVALUATE OPCION_B CLIMATE 90')
    cli.execute('/COMPARE OPCION_A OPCION_B')
    cli.execute('/RECOMMEND')
    state = cli.execute('/STATUS')["data"]
    recommendation = next(iter(state["recommendations"].values()))
    assert recommendation["status"] != "APPROVED"
    assert state["decisions"] == {}
    assert cli.execute('/DECISION RECORD "Select OPCION_B" Architect PRODUCT_OWNER')["code"] == "OK"
    repo.close()


def test_evaluation_uses_facts_and_assumptions(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "sources.sqlite")
    cli = CLI(repo)
    seed_project(cli)
    cli.execute('/FACT SET "SITE_AREA=2000" CATASTRO')
    cli.execute('/ASSUMPTION SET "OCCUPANCY=80%" ESTIMACION')
    cli.execute('/ALTERNATIVE CREATE OPCION_A')
    assert cli.execute('/EVALUATE OPCION_A CLIMATE 85 "" 0.9 FACT')["code"] == "OK"
    assert cli.execute('/EVALUATE OPCION_A CLIMATE 80 "" 0.8 ASSUMPTION')["code"] == "OK"
    sources = {e["source"] for e in cli.execute('/STATUS')["data"]["evaluations"].values()}
    assert sources == {"FACT", "ASSUMPTION"}
    repo.close()
