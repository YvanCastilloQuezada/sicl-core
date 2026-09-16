from __future__ import annotations

from dataclasses import asdict

from .domain import ScenarioBranch, ScenarioEvolution, TemporalCycle


def cycle_to_dict(cycle: TemporalCycle) -> dict:
    value = asdict(cycle)
    value["horizon"] = cycle.horizon.value
    value["state"] = cycle.state.value
    value["start_date"] = cycle.start_date.isoformat()
    value["end_date"] = cycle.end_date.isoformat() if cycle.end_date else None
    value["created_at"] = cycle.created_at.isoformat()
    return value


def scenario_to_dict(branch: ScenarioBranch) -> dict:
    value = asdict(branch)
    value["state"] = branch.state.value
    value["selected_at"] = branch.selected_at.isoformat() if branch.selected_at else None
    value["created_at"] = branch.created_at.isoformat()
    return value


def evolution_to_dict(evolution: ScenarioEvolution) -> dict:
    value = asdict(evolution)
    value["state"] = evolution.state.value
    value["applied_at"] = evolution.applied_at.isoformat() if evolution.applied_at else None
    return value
