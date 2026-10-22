from __future__ import annotations

import hashlib
import itertools
import json
import random
from datetime import datetime, timezone
from typing import Any

from .domain import GeneratedAlternative, GenerationMethod, GenerationState


SUPPORTED_METHODS = {
    "parametric_grid_v1": GenerationMethod.PARAMETRIC,
    "pattern_variation_v1": GenerationMethod.PATTERN_BASED,
    "evolutionary_v1": GenerationMethod.RULE_BASED,
    "llm_assisted_v1": GenerationMethod.HYBRID,
}


def _hash_payload(inputs: dict[str, Any], candidates: list[dict[str, Any]]) -> str:
    payload = json.dumps({"inputs": inputs, "candidates": candidates}, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def list_generation_methods() -> list[dict[str, Any]]:
    return [
        {"name": "parametric_grid_v1", "method": GenerationMethod.PARAMETRIC.value, "active": True, "status": "ACTIVE", "required_inputs": ["parameters"]},
        {"name": "pattern_variation_v1", "method": GenerationMethod.PATTERN_BASED.value, "active": True, "status": "ACTIVE", "required_inputs": ["pattern", "variations"]},
        {"name": "evolutionary_v1", "method": GenerationMethod.RULE_BASED.value, "active": True, "status": "ACTIVE", "required_inputs": ["base_alternatives", "objectives"]},
        {"name": "llm_assisted_v1", "method": GenerationMethod.HYBRID.value, "active": False, "status": "DEFINED_NOT_CONFIGURED", "required_inputs": ["context", "objectives", "constraints", "num_candidates"]},
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


def _numeric_mutation(value: Any, rng: random.Random, mutation_rate: float) -> Any:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or rng.random() > mutation_rate:
        return value
    delta = rng.choice((-1, 1)) * max(abs(float(value)) * 0.05, 0.01)
    mutated = float(value) + delta
    return int(round(mutated)) if isinstance(value, int) else round(mutated, 6)


def generate_evolutionary(inputs: dict[str, Any], project: Any) -> tuple[list[dict[str, Any]], str, GenerationState, dict[str, Any]]:
    base_ids = inputs.get("base_alternatives")
    objective_ids = inputs.get("objectives")
    if not isinstance(base_ids, list) or not base_ids or not isinstance(objective_ids, list) or not objective_ids:
        return [], "base_alternatives and objectives must be non-empty lists", GenerationState.INSUFFICIENT, {}
    alternatives = [project.alternatives.get(str(item)) for item in base_ids]
    objectives = [project.objectives.get(str(item)) for item in objective_ids]
    if any(item is None for item in alternatives) or any(item is None for item in objectives):
        return [], "all base alternatives and objectives must exist", GenerationState.INSUFFICIENT, {}
    try:
        population_size = int(inputs.get("population_size", 20))
        generations = int(inputs.get("generations", 10))
        mutation_rate = float(inputs.get("mutation_rate", 0.1))
        crossover_rate = float(inputs.get("crossover_rate", 0.7))
        seed = int(inputs.get("seed", 20260916))
    except (TypeError, ValueError) as exc:
        raise ValueError("INVALID_INPUTS") from exc
    if not 1 <= population_size <= 100 or not 1 <= generations <= 50 or not 0 <= mutation_rate <= 1 or not 0 <= crossover_rate <= 1:
        raise ValueError("INVALID_INPUTS")
    rng = random.Random(seed)
    templates = [{"base_alternative_id": item.alternative_id, "parameters": dict(item.parameters)} for item in alternatives]

    def candidate(index: int, template: dict[str, Any]) -> dict[str, Any]:
        parameters = {key: _numeric_mutation(value, rng, mutation_rate) for key, value in template["parameters"].items()}
        return {"candidate_id": f"EVO-{index:04d}", "base_alternative_id": template["base_alternative_id"], "parameters": parameters}

    population = [candidate(index, templates[index % len(templates)]) for index in range(population_size)]
    generation_log: list[dict[str, Any]] = []
    for generation_number in range(generations):
        ranked = sorted(population, key=hash_candidate)
        unique = len({hash_candidate(item) for item in population})
        generation_log.append({"generation": generation_number + 1, "population_size": len(population), "unique_candidates": unique})
        elites = ranked[: max(1, population_size // 2)]
        next_population = [dict(item, parameters=dict(item["parameters"])) for item in elites]
        while len(next_population) < population_size:
            left = elites[rng.randrange(len(elites))]
            child = dict(left, candidate_id=f"EVO-{generation_number + 1:02d}-{len(next_population):04d}", parameters=dict(left["parameters"]))
            if len(elites) > 1 and rng.random() <= crossover_rate:
                right = elites[rng.randrange(len(elites))]
                keys = sorted(set(child["parameters"]) | set(right["parameters"]))
                child["parameters"] = {key: (child["parameters"].get(key, right["parameters"].get(key)) if rng.random() < 0.5 else right["parameters"].get(key, child["parameters"].get(key))) for key in keys}
            child["parameters"] = {key: _numeric_mutation(value, rng, mutation_rate) for key, value in child["parameters"].items()}
            next_population.append(child)
        population = next_population
    final_population = sorted(population, key=hash_candidate)
    best_count = min(3, len(final_population))
    outputs = {
        "final_population": final_population,
        "best_candidates": final_population[:best_count],
        "generation_log": generation_log,
        "convergence": len({hash_candidate(item) for item in final_population}) == 1,
        "seed": seed,
        "objective_ids": [item.objective_id for item in objectives],
    }
    return final_population, "Deterministic candidate evolution. Ranking is a stable ordering for inspection, not a decision or recommendation.", GenerationState.GENERATED, outputs


def generate_candidates(project_id: str, method_name: str, inputs: dict[str, Any], generation_id: str, generator: str = "SICL_DESIGN_GENERATOR", project: Any = None) -> GeneratedAlternative:
    normalized = method_name.strip().lower()
    if normalized not in SUPPORTED_METHODS:
        raise ValueError("METHOD_NOT_FOUND")
    method = SUPPORTED_METHODS[normalized]
    outputs: dict[str, Any] = {}
    stored_inputs = dict(inputs)
    if normalized == "llm_assisted_v1":
        raise ValueError("LLM_NOT_CONFIGURED")
    if method is GenerationMethod.PARAMETRIC:
        candidates, rationale, state = generate_parametric(inputs)
    elif method is GenerationMethod.PATTERN_BASED:
        candidates, rationale, state = generate_pattern(inputs)
    else:
        candidates, rationale, state, outputs = generate_evolutionary(inputs, project)
    if outputs:
        stored_inputs["_outputs"] = outputs
    return GeneratedAlternative(
        generation_id=generation_id,
        project_id=project_id,
        generator=generator,
        generator_version="1.1",
        method=method,
        inputs=stored_inputs,
        candidates=candidates,
        rationale=rationale,
        state=state,
        generation_hash=_hash_payload(stored_inputs, candidates),
        created_at=datetime.now(timezone.utc),
    )


def generation_to_dict(generation: GeneratedAlternative) -> dict[str, Any]:
    inputs = dict(generation.inputs)
    outputs = inputs.pop("_outputs", {})
    return {
        "generation_id": generation.generation_id,
        "project_id": generation.project_id,
        "generator": generation.generator,
        "generator_version": generation.generator_version,
        "method": generation.method.value,
        "inputs": inputs,
        "outputs": outputs,
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


__all__ = ["SUPPORTED_METHODS", "generate_candidates", "generation_to_dict", "list_generation_methods", "hash_candidate"]
