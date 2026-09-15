from __future__ import annotations

from pathlib import Path

import pytest

from sicl.cli import CLI
from sicl.repository import SQLiteRepository


def test_vertical_slice_create_fact_objective_constraint_save_close_open_history(tmp_path: Path):
    db_path = tmp_path / "sicl.sqlite"
    repo = SQLiteRepository(db_path)
    cli = CLI(repo, actor="Wilfredo")

    assert cli.execute('/PROJECT CREATE UPAO-001 "Plaza Center"')["code"] == "OK"
    assert cli.execute('/FACT SET "El terreno tiene 2000 m2" "Ficha del proyecto"')["code"] == "OK"
    assert cli.execute('/OBJECTIVE SET rentabilidad MAXIMIZE "alta"')["code"] == "OK"
    assert cli.execute('/CONSTRAINT SET presupuesto "<=" "500000" PEN')["code"] == "OK"
    assert cli.execute('/STAGE SET ACTIVE')["code"] == "OK"

    state = cli.execute('/PROJECT SHOW')["data"]
    assert state["project_id"] == "UPAO-001"
    assert len(state["facts"]) == 1
    assert len(state["objectives"]) == 1
    assert len(state["constraints"]) == 1
    assert next(iter(state["constraints"].values()))["hard"] is True

    assert cli.execute('/STAGE SET CLOSED')["code"] == "OK"
    assert cli.execute('/OBJECTIVE SET area MAXIMIZE 1000')["code"] == "INVALID_STATE"
    assert cli.execute('/EXIT')["code"] == "OK"

    reopened = CLI(repo, actor="Wilfredo")
    assert reopened.execute('/PROJECT OPEN UPAO-001')["code"] == "OK"
    recovered = reopened.execute('/STATUS')["data"]
    assert recovered["stage"] == "CLOSED"
    assert len(recovered["facts"]) == 1
    assert len(recovered["objectives"]) == 1
    assert len(recovered["constraints"]) == 1

    events = reopened.execute('/HISTORY')["data"]["events"]
    assert [e["type"] for e in events] == [
        "PROJECT_CREATED", "FACT_SET", "OBJECTIVE_SET", "CONSTRAINT_SET", "STAGE_SET", "STAGE_SET"
    ]
    assert all(e["actor"] == "Wilfredo" for e in events)
    assert all(e["source"] == "USER_COMMAND" for e in events)
    repo.close()


def test_fact_and_assumption_are_distinct_and_decision_is_human(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "sicl.sqlite")
    cli = CLI(repo, actor="Architect")
    cli.execute('/PROJECT CREATE P-1 "Test"')
    cli.execute('/FACT SET "Observed datum" "Survey"')
    cli.execute('/ASSUMPTION SET "Demand remains stable" "Scenario premise"')
    cli.execute('/DECISION RECORD "Proceed with option A" "Architect" "PRODUCT_OWNER"')

    state = cli.execute('/STATUS')["data"]
    assert len(state["facts"]) == 1
    assert len(state["assumptions"]) == 1
    decision = next(iter(state["decisions"].values()))
    assert decision["actor"] == "Architect"
    assert decision["authority"] == "PRODUCT_OWNER"
    assert [e["type"] for e in cli.execute('/HISTORY')["data"]["events"]] == [
        "PROJECT_CREATED", "FACT_SET", "ASSUMPTION_SET", "DECISION_RECORDED"
    ]
    repo.close()


def test_append_only_events_and_validation(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "sicl.sqlite")
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE P-1 "Test"')
    before = repo.events("P-1")
    assert cli.execute('/OBJECTIVE SET cost DEFAULT 10')["code"] == "INVALID_ARGUMENT"
    assert cli.execute('/UNKNOWN COMMAND')["code"] == "UNKNOWN_COMMAND"
    after = repo.events("P-1")
    assert len(before) == len(after) == 1
    assert after[0].id == before[0].id
    with pytest.raises(Exception, match="append-only"):
        repo.conn.execute("UPDATE events SET type='TAMPERED' WHERE id=1")
    with pytest.raises(Exception, match="append-only"):
        repo.conn.execute("DELETE FROM events WHERE id=1")
    repo.close()


def test_vertical_slice_upao_001(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "upao.sqlite")
    cli = CLI(repo, actor="Yvan")
    assert cli.execute('/PROJECT CREATE UPAO-001 "Plaza Center"')["code"] == "OK"
    assert cli.execute('/FACT SET "SITE_AREA=2000" CATASTRO')["code"] == "OK"
    assert cli.execute('/ASSUMPTION SET "OCCUPANCY=80%" ESTIMACION')["code"] == "OK"
    assert cli.execute('/OBJECTIVE SET CLIMATE MAXIMIZE 80')["code"] == "OK"
    assert cli.execute('/CONSTRAINT SET HEIGHT "<=" 6 FLOORS')["code"] == "OK"
    assert cli.execute('/ROLE ADD ARCHITECT Yvan')["code"] == "OK"
    assert cli.execute('/EXIT')["code"] == "OK"

    reopened = CLI(repo, actor="Yvan")
    assert reopened.execute('/PROJECT OPEN UPAO-001')["code"] == "OK"
    state = reopened.execute('/STATUS')["data"]
    fact = next(iter(state["facts"].values()))
    assumption = next(iter(state["assumptions"].values()))
    objective = next(iter(state["objectives"].values()))
    constraint = next(iter(state["constraints"].values()))
    role = next(iter(state["roles"].values()))
    assert fact["statement"] == "SITE_AREA=2000" and fact["source"] == "CATASTRO"
    assert assumption["statement"] == "OCCUPANCY=80%" and assumption["basis"] == "ESTIMACION"
    assert fact["fact_id"] != assumption["assumption_id"]
    assert objective["key"] == "CLIMATE" and objective["direction"] == "MAXIMIZE" and objective["value"] == "80"
    assert constraint["key"] == "HEIGHT" and constraint["operator"] == "<=" and constraint["value"] == "6"
    assert constraint["unit"] == "FLOORS" and constraint["hard"] is True
    assert role["name"] == "ARCHITECT" and role["actor"] == "Yvan"
    events = reopened.execute('/HISTORY')["data"]["events"]
    assert len(events) == 6
    assert [event["type"] for event in events] == [
        "PROJECT_CREATED", "FACT_SET", "ASSUMPTION_SET", "OBJECTIVE_SET", "CONSTRAINT_SET", "ROLE_ADDED"
    ]
    repo.close()


def test_events_append_only(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "events.sqlite")
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE P-APPEND "Append Only"')
    cli.execute('/FACT SET datum source')
    original = repo.events("P-APPEND")
    with pytest.raises(Exception, match="append-only"):
        repo.conn.execute("UPDATE events SET payload='tampered' WHERE id=?", (original[0].id,))
    with pytest.raises(Exception, match="append-only"):
        repo.conn.execute("DELETE FROM events WHERE id=?", (original[0].id,))
    assert [event.id for event in repo.events("P-APPEND")] == [event.id for event in original]
    repo.close()


def test_decision_requires_actor_and_authority(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "decision.sqlite")
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE P-DECISION "Decision"')
    assert cli.execute('/DECISION RECORD "Proceed"')["code"] == "INVALID_ARGUMENT"
    assert cli.execute('/DECISION RECORD "Proceed" Architect')["code"] == "INVALID_ARGUMENT"
    assert cli.execute('/DECISION RECORD "Proceed" Architect PRODUCT_OWNER')["code"] == "OK"
    decision = next(iter(cli.execute('/STATUS')["data"]["decisions"].values()))
    assert decision["actor"] == "Architect" and decision["authority"] == "PRODUCT_OWNER"
    repo.close()


def test_constraint_hard_only(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "constraints.sqlite")
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE P-CONSTRAINT "Hard Constraints"')
    assert cli.execute('/CONSTRAINT SET budget "<=" 500000 PEN SOFT')["code"] == "INVALID_ARGUMENT"
    assert cli.execute('/CONSTRAINT SET budget "<=" 500000 PEN')["code"] == "OK"
    constraints = cli.execute('/STATUS')["data"]["constraints"].values()
    assert all(constraint["hard"] is True for constraint in constraints)
    repo.close()


def test_closed_project_no_mutations(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "closed.sqlite")
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE P-CLOSED "Closed"')
    assert cli.execute('/STAGE SET CLOSED')["code"] == "OK"
    assert cli.execute('/OBJECTIVE SET cost MINIMIZE 10')["code"] == "INVALID_STATE"
    assert cli.execute('/CONSTRAINT SET height "<=" 6 FLOORS')["code"] == "INVALID_STATE"
    assert len(repo.events("P-CLOSED")) == 2
    repo.close()


def test_history_temporal_ordering(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "history.sqlite")
    cli = CLI(repo)
    cli.execute('/PROJECT CREATE P-HISTORY "History"')
    cli.execute('/STAGE SET ACTIVE')
    cli.execute('/FACT SET one source')
    cli.execute('/OBJECTIVE SET climate MAXIMIZE 80')
    cli.execute('/ROLE ADD ARCHITECT Yvan')
    events = cli.execute('/HISTORY')["data"]["events"]
    assert len(events) == 5
    assert [event["id"] for event in events] == sorted(event["id"] for event in events)
    assert [event["type"] for event in events] == [
        "PROJECT_CREATED", "STAGE_SET", "FACT_SET", "OBJECTIVE_SET", "ROLE_ADDED"
    ]
    repo.close()


def test_event_has_source(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "source.sqlite")
    cli = CLI(repo, actor="Architect")
    cli.execute('/PROJECT CREATE P-SOURCE "Source"')
    cli.execute('/FACT SET datum survey')
    events = repo.events("P-SOURCE")
    assert len(events) == 2
    assert all(event.source and event.source == "USER_COMMAND" for event in events)
    assert all(event.actor == "Architect" for event in events)
    repo.close()


def test_events_accumulate_not_replace(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "accumulate.sqlite")
    cli = CLI(repo, actor="Architect")
    cli.execute('/PROJECT CREATE P-ACCUMULATE "Accumulate"')
    cli.execute('/STAGE SET ACTIVE')
    cli.execute('/FACT SET datum survey')
    project = repo.get_project("P-ACCUMULATE")
    assert project is not None
    before = repo.events("P-ACCUMULATE")
    repo.save(project)
    repo.save(project)
    after = repo.events("P-ACCUMULATE")
    assert len(after) == 3
    assert [event.id for event in after] == [event.id for event in before]
    assert [event["type"] for event in cli.execute('/HISTORY')["data"]["events"]] == [
        "PROJECT_CREATED", "STAGE_SET", "FACT_SET"
    ]
    repo.close()
