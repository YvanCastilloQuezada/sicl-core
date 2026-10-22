from __future__ import annotations

from sicl.cli import CLI
from sicl.optimization import GenerativeOptimizer, tradeoff_matrix
from sicl.repository import SQLiteRepository
from sicl.v11 import Alternative, Evaluation


def test_optimizer_reduces_floors_for_over_budget():
    alternative = Alternative("A", "P", "CONVENCIONAL_A", parameters={"FLOORS": "8"})
    proposals = GenerativeOptimizer().generate(alternative, [Evaluation("E", "A", "COST", -1, source="EXPERT_SYSTEM")])
    assert len(proposals) == 1
    assert proposals[0].status == "PROPOSED"
    assert proposals[0].source == "GENERATIVE_OPTIMIZER"
    assert proposals[0].parameters["FLOORS"] == "7"


def test_optimizer_changes_facade_for_poor_energy():
    alternative = Alternative("A", "P", "CONVENCIONAL_A", parameters={"facade": "vidrio simple"})
    proposals = GenerativeOptimizer().generate(alternative, [Evaluation("E", "A", "ENERGY", 60, source="EXPERT_SYSTEM")])
    assert proposals[0].parameters["facade"] == "doble piel"
    assert proposals[0].status == "PROPOSED"


def test_generate_command_records_proposed_alternative_and_event():
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute("/PROJECT CREATE GEN-001 Generated")
    cli.execute("/ALTERNATIVE CREATE CONVENCIONAL_A")
    cli.execute("/ALTERNATIVE SET CONVENCIONAL_A FLOORS 8")
    cli.execute("/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80")
    cli.execute("/EVALUATE CONVENCIONAL_A ENERGY_SAVINGS 60 score 0.8 EXPERT_SYSTEM")
    before = len(repo.events("GEN-001"))
    result = cli.execute("/GENERATE CONVENCIONAL_A ENERGY_SAVINGS,CONSTRUCTION_COST")
    generated = result["data"]["generated"]
    assert result["code"] == "OK"
    assert generated and generated[0]["status"] == "PROPOSED"
    assert generated[0]["source"] == "GENERATIVE_OPTIMIZER"
    assert len(repo.events("GEN-001")) == before + len(generated)
    assert all(event.type == "ALTERNATIVE_GENERATED" for event in repo.events("GEN-001")[before:])


def test_generate_does_not_create_decision_or_recommendation():
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute("/PROJECT CREATE GEN-002 Generated")
    cli.execute("/ALTERNATIVE CREATE A")
    cli.execute("/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80")
    cli.execute("/EVALUATE A ENERGY_SAVINGS 60")
    result = cli.execute("/GENERATE A ENERGY_SAVINGS")
    assert result["data"]["decision_created"] is False
    assert result["data"]["recommendation_created"] is False
    assert cli.execute("/STATUS")["data"]["decisions"] == {}


def test_tradeoff_matrix_shows_deltas_and_pareto_marker():
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute("/PROJECT CREATE MAT-001 Matrix")
    cli.execute("/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80")
    cli.execute("/OBJECTIVE SET CONSTRUCTION_COST MINIMIZE 100")
    cli.execute("/ALTERNATIVE CREATE A")
    cli.execute("/ALTERNATIVE CREATE B")
    cli.execute("/EVALUATE A ENERGY_SAVINGS 50")
    cli.execute("/EVALUATE A CONSTRUCTION_COST 100")
    cli.execute("/EVALUATE B ENERGY_SAVINGS 75")
    cli.execute("/EVALUATE B CONSTRUCTION_COST 115")
    text = cli.execute("/TRADEOFF_MATRIX ENERGY_SAVINGS CONSTRUCTION_COST")["data"]["text"]
    assert "TRADE-OFF MATRIX" in text
    assert "B vs A" in text
    assert "delta" in text
    assert "Pareto front" in text
    assert "B" in text


def test_tradeoff_matrix_function_includes_incomplete_alternatives():
    text = tradeoff_matrix(
        [Alternative("A", "P", "A"), Alternative("B", "P", "B")],
        [Evaluation("E", "A", "O", 10)],
        [type("Objective", (), {"key": "O", "objective_id": "O", "direction": "MAXIMIZE"})()],
    )
    assert "A" in text and "B" in text
