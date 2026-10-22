from __future__ import annotations

import json
from pathlib import Path

from sicl.cli import CLI
from sicl.repository import SQLiteRepository


def cli_for(tmp_path: Path) -> CLI:
    return CLI(SQLiteRepository(tmp_path / "feasibility.sqlite"), actor="architect")


def test_project_variable_and_feasible_front_are_explicit(tmp_path: Path) -> None:
    cli = cli_for(tmp_path)
    assert cli.execute('/PROJECT CREATE P-FEAS "Feasibility" edificacion proyecto')["code"] == "OK"
    assert cli.execute('/CONSTRAINT SET INVESTMENT <= 100 USD')["code"] == "OK"
    variable = cli.execute('/VARIABLE ADD V-1 INVESTMENT CONSTRAINT 90 architect PROJECT_OWNER USD edificacion')
    assert variable["code"] == "OK"
    assert variable["data"]["variable"]["variable_type"] == "CONSTRAINT"
    assert cli.execute('/VARIABLE ADD V-2 investment PARAMETER 80 architect PROJECT_OWNER USD edificacion')["code"] == "CONFLICT"
    assert cli.execute('/FEASIBILITY CHECK ALT-A \'{"INVESTMENT":90}\'')["data"]["feasibility"]["state"] == "FEASIBLE"
    assert cli.execute('/FEASIBILITY CHECK ALT-B \'{"INVESTMENT":120}\'')["data"]["feasibility"]["state"] == "INFEASIBLE"
    front = cli.execute('/MULTIOBJECTIVE FEASIBLE_PARETO \'["ALT-A","ALT-B"]\'')
    assert front["data"]["feasible_pareto_front"] == ["ALT-A"]


def test_variable_and_feasibility_events_survive_reload(tmp_path: Path) -> None:
    path = tmp_path / "persistent.sqlite"
    cli = CLI(SQLiteRepository(path), actor="architect")
    cli.execute('/PROJECT CREATE P-PERSIST "Persistent" edificacion proyecto')
    cli.execute('/CONSTRAINT SET INVESTMENT <= 100 USD')
    cli.execute('/VARIABLE ADD V-1 INVESTMENT CONSTRAINT 90 architect PROJECT_OWNER USD edificacion')
    cli.execute('/FEASIBILITY CHECK ALT-A \'{"INVESTMENT":90}\'')
    reopened = CLI(SQLiteRepository(path), actor="architect")
    assert reopened.execute('/PROJECT OPEN P-PERSIST')["code"] == "OK"
    assert reopened.execute('/VARIABLE LIST')["data"]["variables"][0]["variable_id"] == "V-1"
    assert reopened.execute('/FEASIBILITY CHECK ALT-A \'{"INVESTMENT":90}\'')["data"]["feasibility"]["state"] == "FEASIBLE"
