from __future__ import annotations

import hashlib
import json
import random
import statistics
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
    "monte_carlo_v1": {
        "method_id": "monte_carlo_v1",
        "name": "Monte Carlo v1",
        "type": SimulationType.MONTE_CARLO.value,
        "inputs_required": ["alternative_id", "objective_id", "parameter_name", "parameter_distribution"],
        "outputs": ["mean", "std_dev", "min", "max", "percentiles", "samples_count", "convergence_check"],
        "description": "Muestrea una distribución declarada sobre un parámetro de una alternativa con semilla fija.",
        "method_version": "1.0",
    },
}


def list_methods() -> list[dict[str, Any]]:
    return [dict(method) for method in METHODS.values()]


def canonical_hash(inputs: dict[str, Any], outputs: dict[str, Any], seed: int | None = None) -> str:
    value: dict[str, Any] = {"inputs": inputs, "outputs": outputs}
    if seed is not None:
        value["seed"] = seed
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * percentile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def _monte_carlo(inputs: dict[str, Any], project: Any) -> tuple[SimulationState, dict[str, Any]]:
    alternative = project.alternatives.get(str(inputs.get("alternative_id")))
    objective = project.objectives.get(str(inputs.get("objective_id")))
    if alternative is None or objective is None:
        return SimulationState.INSUFFICIENT, {"missing_inputs": ["alternative_id" if alternative is None else "objective_id"]}
    parameter_name = str(inputs.get("parameter_name", ""))
    if parameter_name not in alternative.parameters:
        raise ValueError("PARAMETER_NOT_FOUND")
    distribution = inputs.get("parameter_distribution")
    if not isinstance(distribution, dict):
        raise ValueError("INVALID_DISTRIBUTION")
    distribution_type = str(distribution.get("type", "")).upper()
    parameters = distribution.get("parameters", {})
    if not isinstance(parameters, dict) or distribution_type not in {"NORMAL", "UNIFORM", "TRIANGULAR"}:
        raise ValueError("INVALID_DISTRIBUTION")
    try:
        iterations = int(inputs.get("iterations", 1000))
    except (TypeError, ValueError) as exc:
        raise ValueError("INVALID_INPUTS") from exc
    if iterations < 1 or iterations > 10000:
        raise ValueError("INVALID_INPUTS")
    seed = int(inputs.get("seed", 20260916))
    rng = random.Random(seed)
    try:
        if distribution_type == "NORMAL":
            mean = float(parameters["mean"])
            standard_deviation = float(parameters["std_dev"])
            if standard_deviation < 0:
                raise ValueError
            samples = [rng.gauss(mean, standard_deviation) for _ in range(iterations)]
        elif distribution_type == "UNIFORM":
            low, high = float(parameters["low"]), float(parameters["high"])
            if low > high:
                raise ValueError
            samples = [rng.uniform(low, high) for _ in range(iterations)]
        else:
            low = float(parameters["low"])
            mode = float(parameters["mode"])
            high = float(parameters["high"])
            if not low <= mode <= high:
                raise ValueError
            samples = [rng.triangular(low, high, mode) for _ in range(iterations)]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("INVALID_INPUTS") from exc
    output = {
        "mean": statistics.fmean(samples),
        "std_dev": statistics.pstdev(samples),
        "min": min(samples),
        "max": max(samples),
        "percentiles": {"p10": _percentile(samples, 0.10), "p50": _percentile(samples, 0.50), "p90": _percentile(samples, 0.90)},
        "samples_count": len(samples),
        "convergence_check": len(samples) >= 100,
        "seed": seed,
        "parameter_name": parameter_name,
        "objective_id": objective.objective_id,
        "alternative_id": alternative.alternative_id,
        "provenance": "SICL monte_carlo_v1",
    }
    return SimulationState.EXECUTED, output


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
    if method == "monte_carlo_v1":
        return _monte_carlo(inputs, project)
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
