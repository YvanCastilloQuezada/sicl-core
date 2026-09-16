from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class SimulationType(str, Enum):
    DETERMINISTIC = "DETERMINISTIC"
    MONTE_CARLO = "MONTE_CARLO"
    SCENARIO = "SCENARIO"
    SENSITIVITY = "SENSITIVITY"


class SimulationState(str, Enum):
    PLANNED = "PLANNED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    INSUFFICIENT = "INSUFFICIENT"


@dataclass(frozen=True)
class Simulation:
    simulation_id: str
    project_id: str
    simulation_type: SimulationType
    method: str
    method_version: str
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    state: SimulationState
    started_at: datetime
    finished_at: datetime | None
    evidence_hash: str
    version: int = 1


METHODS: dict[str, dict[str, Any]] = {
    "deterministic_basic_v1": {
        "method_id": "deterministic_basic_v1",
        "name": "Deterministic Basic v1",
        "type": SimulationType.DETERMINISTIC.value,
        "inputs_required": ["alternative_id", "objective_id", "parameter_value"],
        "outputs": ["objective_value", "delta"],
        "description": "Calcula un valor objetivo y su delta de forma determinista sobre una alternativa.",
        "method_version": "1.0",
    },
    "sensitivity_linear_v1": {
        "method_id": "sensitivity_linear_v1",
        "name": "Sensitivity Linear v1",
        "type": SimulationType.SENSITIVITY.value,
        "inputs_required": ["alternative_id", "objective_id", "parameter", "range"],
        "outputs": ["sensitivity_coefficient", "samples"],
        "description": "Evalúa una variación lineal sobre un parámetro dentro de un rango.",
        "method_version": "1.0",
    },
}


def list_methods() -> list[dict[str, Any]]:
    return [dict(method) for method in METHODS.values()]


def canonical_hash(inputs: dict[str, Any], outputs: dict[str, Any]) -> str:
    payload = json.dumps({"inputs": inputs, "outputs": outputs}, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def execute_method(simulation_type: SimulationType, method: str, inputs: dict[str, Any], project: Any) -> tuple[SimulationState, dict[str, Any]]:
    definition = METHODS.get(method)
    if definition is None:
        raise KeyError("METHOD_NOT_FOUND")
    if definition["type"] != simulation_type.value:
        raise ValueError("METHOD_TYPE_MISMATCH")
    missing = [key for key in definition["inputs_required"] if key not in inputs]
    if missing:
        return SimulationState.INSUFFICIENT, {"missing_inputs": missing}
    if method == "deterministic_basic_v1":
        alternative = project.alternatives.get(str(inputs["alternative_id"]))
        objective = project.objectives.get(str(inputs["objective_id"]))
        if alternative is None or objective is None:
            return SimulationState.INSUFFICIENT, {"missing_inputs": ["alternative_id" if alternative is None else "objective_id"]}
        parameter_value = float(inputs["parameter_value"])
        try:
            target = float(objective.value)
        except (TypeError, ValueError):
            target = 0.0
        return SimulationState.EXECUTED, {"objective_value": parameter_value, "delta": parameter_value - target, "feasibility": True, "provenance": "SICL deterministic_basic_v1"}
    if method == "sensitivity_linear_v1":
        if str(inputs["alternative_id"]) not in project.alternatives or str(inputs["objective_id"]) not in project.objectives:
            return SimulationState.INSUFFICIENT, {"missing_inputs": ["alternative_id or objective_id"]}
        values = inputs["range"]
        if not isinstance(values, list) or len(values) != 2:
            return SimulationState.INSUFFICIENT, {"missing_inputs": ["range with two numeric values"]}
        start, end = float(values[0]), float(values[1])
        coefficient = (end - start) / 2.0
        samples = [{"parameter": start, "value": start}, {"parameter": end, "value": end}]
        return SimulationState.EXECUTED, {"sensitivity_coefficient": coefficient, "samples": samples, "feasibility": True, "provenance": "SICL sensitivity_linear_v1"}
    raise KeyError("METHOD_NOT_FOUND")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def simulation_to_dict(simulation: Simulation) -> dict[str, Any]:
    value = asdict(simulation)
    value["simulation_type"] = simulation.simulation_type.value
    value["state"] = simulation.state.value
    value["started_at"] = simulation.started_at.isoformat()
    value["finished_at"] = simulation.finished_at.isoformat() if simulation.finished_at else None
    return value
