from __future__ import annotations

import hashlib
import itertools
import json
from datetime import datetime, timezone
from typing import Any

from .domain import GeneratedAlternative, GenerationMethod, GenerationState


SUPPORTED_METHODS = {
    "parametric_grid_v1": GenerationMethod.PARAMETRIC,
    "pattern_variation_v1": GenerationMethod.PATTERN_BASED,
}


def _hash_payload(inputs: dict[str, Any], candidates: list[dict[str, Any]]) -> str:
    payload = json.dumps({"inputs": inputs, "candidates": candidates}, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def list_generation_methods() -> list[dict[str, Any]]:
    return [
        {"name": "parametric_grid_v1", "method": GenerationMethod.PARAMETRIC.value, "active": True, "required_inputs": ["parameters"]},
        {"name": "pattern_variation_v1", "method": GenerationMethod.PATTERN_BASED.value, "active": True, "required_inputs": ["pattern", "variations"]},
        {"name": "llm_assisted_v1", "method": GenerationMethod.HYBRID.value, "active": False, "required_inputs": ["provider_contract"]},
        {"name": "evolutionary_v1", "method": GenerationMethod.RULE_BASED.value, "active": False, "required_inputs": ["population", "fitness_contract"]},
    ]


def _values(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict) and "values" in value and isinstance(value["values"], list):
        return value["values"]
    if isinstance(value, dict) and {"min", "max"} <= set(value):
        step = value.get("step", 1)
        if not isinstance(step, (int, float)) or step <= 0:
            return []
        current, result = value["min"], []
        while current <= value["max"]:
            result.append(current)
            current += step
        return result
    return [value]


def generate_parametric(inputs: dict[str, Any]) -> tuple[list[dict[str, Any]], str, GenerationState]:
    parameters = inputs.get("parameters")
    if not isinstance(parameters, dict) or not parameters:
        return [], "parameters must be a non-empty object", GenerationState.INSUFFICIENT
    keys = sorted(parameters)
    values = [_values(parameters[key]) for key in keys]
    if any(not options for options in values):
        return [], "each parameter must declare at least one value", GenerationState.INSUFFICIENT
    candidates = [{key: value for key, value in zip(keys, combination)} for combination in itertools.product(*values)]
    return candidates, "Cartesian product of explicitly declared parameter values.", GenerationState.GENERATED


def generate_pattern(inputs: dict[str, Any]) -> tuple[list[dict[str, Any]], str, GenerationState]:
    pattern = inputs.get("pattern")
    variations = inputs.get("variations")
    if not isinstance(pattern, dict) or not pattern or not isinstance(variations, dict) or not variations:
        return [], "pattern and variations must be non-empty objects", GenerationState.INSUFFICIENT
    keys = sorted(variations)
    values = [_values(variations[key]) for key in keys]
    if any(not options for options in values):
        return [], "each variation must declare at least one value", GenerationState.INSUFFICIENT
    candidates = []
    for combination in itertools.product(*values):
        candidate = dict(pattern)
        candidate.update({key: value for key, value in zip(keys, combination)})
        candidates.append(candidate)
    return candidates, "Explicit variations applied to the declared reference pattern.", GenerationState.GENERATED


def generate_candidates(project_id: str, method_name: str, inputs: dict[str, Any], generation_id: str, generator: str = "SICL_DESIGN_GENERATOR") -> GeneratedAlternative:
    normalized = method_name.strip().lower()
    if normalized not in SUPPORTED_METHODS:
        raise ValueError("METHOD_NOT_FOUND")
    method = SUPPORTED_METHODS[normalized]
    if method is GenerationMethod.PARAMETRIC:
        candidates, rationale, state = generate_parametric(inputs)
    else:
        candidates, rationale, state = generate_pattern(inputs)
    return GeneratedAlternative(
        generation_id=generation_id,
        project_id=project_id,
        generator=generator,
        generator_version="1.0",
        method=method,
        inputs=inputs,
        candidates=candidates,
        rationale=rationale,
        state=state,
        generation_hash=_hash_payload(inputs, candidates),
        created_at=datetime.now(timezone.utc),
    )


def generation_to_dict(generation: GeneratedAlternative) -> dict[str, Any]:
    return {
        "generation_id": generation.generation_id,
        "project_id": generation.project_id,
        "generator": generation.generator,
        "generator_version": generation.generator_version,
        "method": generation.method.value,
        "inputs": generation.inputs,
        "candidates": generation.candidates,
        "rationale": generation.rationale,
        "state": generation.state.value,
        "generation_hash": generation.generation_hash,
        "created_at": generation.created_at.isoformat(),
        "version": generation.version,
    }


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def hash_candidate(candidate: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(candidate, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()
