from __future__ import annotations

from sicl.agents import EconomicAgent, StructuralAgent
from sicl.cli import CLI
from sicl.domain import Assumption, Constraint, Fact, Objective, Project
from sicl.repository import SQLiteRepository
from sicl.v11 import Alternative


def test_structural_agent_penalizes_masonry_above_six_floors():
    project = Project("P", "Project")
    project.objectives["S"] = Objective("S", "P", "SAFETY", "MAXIMIZE", "80")
    alternative = Alternative("A", "P", "A", parameters={"FLOORS": "8", "STRUCTURE": "Mampostería"})
    evaluation = StructuralAgent().evaluate(alternative, project)
    assert evaluation.value == 70.0
    assert evaluation.source == "EXPERT_SYSTEM"


def test_structural_agent_requires_piles_on_soft_soil():
    project = Project("P", "Project")
    project.objectives["S"] = Objective("S", "P", "SAFETY", "MAXIMIZE", "80")
    project.facts["F"] = Fact("F", "P", "SOIL_TYPE=Blando", "SITE_INTELLIGENCE_API")
    alternative = Alternative("A", "P", "A", parameters={"FLOORS": "4", "STRUCTURE": "Concreto", "FOUNDATION_TYPE": "Zapata"})
    assert StructuralAgent().evaluate(alternative, project).value == 60.0


def test_structural_agent_accepts_piles_on_soft_soil():
    project = Project("P", "Project")
    project.objectives["S"] = Objective("S", "P", "SAFETY", "MAXIMIZE", "80")
    project.facts["F"] = Fact("F", "P", "SOIL_TYPE=Blando", "SITE_INTELLIGENCE_API")
    alternative = Alternative("A", "P", "A", parameters={"FOUNDATION_TYPE": "Pilotes"})
    assert StructuralAgent().evaluate(alternative, project).value == 100.0


def test_economic_agent_marks_over_budget_negative():
    project = Project("P", "Project")
    project.objectives["C"] = Objective("C", "P", "ESTIMATED_COST", "MINIMIZE", "0")
    project.assumptions["A"] = Assumption("A", "P", "AREA=2000 COST_PER_M2=1200", "ESTIMATION")
    project.constraints["B"] = Constraint("B", "P", "BUDGET", "<=", "500000", "USD")
    alternative = Alternative("A", "P", "A", parameters={"FLOORS": "8"})
    evaluation = EconomicAgent().evaluate(alternative, project)
    assert evaluation.value == -1.0
    assert evaluation.source == "EXPERT_SYSTEM"


def test_economic_agent_calculates_cost_under_budget():
    project = Project("P", "Project")
    project.objectives["C"] = Objective("C", "P", "ESTIMATED_COST", "MINIMIZE", "0")
    project.assumptions["A"] = Assumption("A", "P", "AREA=1000 COST_PER_M2=100", "ESTIMATION")
    project.constraints["B"] = Constraint("B", "P", "BUDGET", "<=", "500000", "USD")
    alternative = Alternative("A", "P", "A", parameters={"FLOORS": "2"})
    assert EconomicAgent().evaluate(alternative, project).value == 200000.0


def test_debate_returns_all_three_agents_and_is_read_only():
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute("/PROJECT CREATE DEB-001 Debate")
    cli.execute("/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80")
    cli.execute("/OBJECTIVE SET SAFETY MAXIMIZE 80")
    cli.execute("/OBJECTIVE SET ESTIMATED_COST MINIMIZE 0")
    cli.execute("/FACT SET Temperatura calida API")
    cli.execute("/FACT SET SOIL_TYPE=Blando API")
    cli.execute("/ASSUMPTION SET AREA=1000 COST_PER_M2=100 ESTIMATION")
    cli.execute("/CONSTRAINT SET BUDGET <= 500000 USD")
    cli.execute("/ALTERNATIVE CREATE CONVENCIONAL_A")
    cli.execute("/ALTERNATIVE SET CONVENCIONAL_A facade vidrio simple")
    cli.execute("/ALTERNATIVE SET CONVENCIONAL_A FLOORS 8")
    cli.execute("/ALTERNATIVE SET CONVENCIONAL_A STRUCTURE Mampostería")
    before_events = len(repo.events("DEB-001"))
    result = cli.execute("/DEBATE CONVENCIONAL_A")
    text = result["data"]["text"]
    assert result["code"] == "OK"
    assert "Agente Bioclimatic" in text
    assert "Agente Structural" in text
    assert "Agente Economic" in text
    assert "VEREDICTO DEL DEBATE" in text
    assert "DECISION CREADA: NO" in text
    assert len(repo.events("DEB-001")) == before_events


def test_debate_does_not_create_decision():
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute("/PROJECT CREATE DEB-002 Debate")
    cli.execute("/ALTERNATIVE CREATE A")
    result = cli.execute("/DEBATE A")
    assert result["code"] == "OK"
    assert cli.execute("/STATUS")["data"]["decisions"] == {}


def test_all_structural_and_economic_evaluations_are_expert_system():
    project = Project("P", "Project")
    project.objectives["S"] = Objective("S", "P", "SAFETY", "MAXIMIZE", "80")
    project.objectives["C"] = Objective("C", "P", "ESTIMATED_COST", "MINIMIZE", "0")
    project.assumptions["A"] = Assumption("A", "P", "AREA=100 COST_PER_M2=10", "ESTIMATION")
    alternative = Alternative("A", "P", "A", parameters={"FLOORS": "1"})
    assert StructuralAgent().evaluate(alternative, project).source == "EXPERT_SYSTEM"
    assert EconomicAgent().evaluate(alternative, project).source == "EXPERT_SYSTEM"


def test_debate_reports_missing_agent_inputs_without_mutation():
    repo = SQLiteRepository()
    cli = CLI(repo)
    cli.execute("/PROJECT CREATE DEB-003 Debate")
    cli.execute("/ALTERNATIVE CREATE A")
    before = len(repo.events("DEB-003"))
    text = cli.execute("/DEBATE A")["data"]["text"]
    assert "requiere datos" in text
    assert len(repo.events("DEB-003")) == before
