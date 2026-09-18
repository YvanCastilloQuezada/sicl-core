from __future__ import annotations

from dataclasses import asdict
from math import sqrt
from typing import Any

from .gdi import apply_design_operation, design_dna
from .spatial_generator import UPAO001SpatialGenerator
from .spatial_evaluation import spatial_metrics
from .v11 import Alternative

INTENSITIES = tuple(range(0, 101, 10))
MUTABLE = {"footprint_ratio", "courtyard_ratio", "mass_separation", "floors"}

def _alt(value: dict[str, Any]) -> Alternative:
    return Alternative(**value)

def _vector(value: dict[str, Any]) -> dict[str, float]:
    p = value.get("parameters", {})
    return {key: float(p[key]) for key in MUTABLE if key in p and isinstance(p[key], (int, float))}

def inheritance_profile(parent: dict[str, Any], inherit: list[str] | None = None, mutable: list[str] | None = None, bounds: dict[str, dict[str, float]] | None = None) -> dict[str, Any]:
    dna = parent.get("design_dna") or design_dna(_alt(parent["alternative"] if "alternative" in parent else parent))
    selected = inherit or ["strategy"]
    mutable_keys = mutable or ["footprint_ratio", "courtyard_ratio", "mass_separation", "floors"]
    return {"inherit": selected, "mutable": mutable_keys, "bounded": bounds or {}, "free": [key for key in mutable_keys if key not in (bounds or {})], "design_dna": dna, "controls": {key: {"mode": "RANGE", "min": value.get("min"), "max": value.get("max")} for key, value in (bounds or {}).items()}}

def _apply_bounds(params: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    next_params = dict(params)
    for key, bounds in profile.get("bounded", {}).items():
        if key in next_params:
            next_params[key] = max(float(bounds["min"]), min(float(bounds["max"]), float(next_params[key])))
    return next_params

def directed_mutation(parent: dict[str, Any], profile: dict[str, Any], target: str, intensity: int) -> dict[str, Any]:
    if target not in MUTABLE:
        raise ValueError("UNSUPPORTED_MUTATION_TARGET")
    if intensity not in INTENSITIES:
        raise ValueError("INVALID_MUTATION_INTENSITY")
    base = _alt(parent["alternative"] if "alternative" in parent else parent)
    params = dict(base.parameters)
    current = float(params.get(target, 0))
    if target == "footprint_ratio":
        desired = 0.30 if str(params.get("strategy")) == "courtyard" else 0.60
    elif target == "courtyard_ratio":
        desired = 0.45
    elif target == "mass_separation":
        desired = 10.0
    else:
        desired = max(1, int(params.get(target, 4)) + 2)
    params[target] = current + (desired - current) * (intensity / 100)
    params = _apply_bounds(params, profile)
    operation_type = "CHANGE_HEIGHT" if target == "floors" else ("MODIFY_OPEN_SPACE" if target == "footprint_ratio" else ("RESIZE_COURTYARD" if target == "courtyard_ratio" else "ARTICULATE"))
    child, operation = apply_design_operation(base, operation_type, params, {}, [], [])
    return {"alternative": asdict(child), "operation": asdict(operation), "parent_alternative_id": base.alternative_id, "inheritance": profile, "mutation": {"target": target, "intensity": intensity, "bounds": profile.get("bounded", {})}, "design_dna": design_dna(child), "provenance": "GDI-P6 deterministic directed mutation", "decision_created": False}

def design_distance(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    a, b = _vector(left), _vector(right)
    keys = sorted(set(a) | set(b))
    components = {key: round(abs(a.get(key, 0.0) - b.get(key, 0.0)), 4) for key in keys}
    raw = sqrt(sum(value * value for value in components.values()))
    normalized = round(raw / max(1.0, len(keys)), 4)
    return {"left": left.get("alternative_id") or left.get("alternative", {}).get("alternative_id"), "right": right.get("alternative_id") or right.get("alternative", {}).get("alternative_id"), "distance": normalized, "components": components, "is_quality_score": False, "explanation": "Parameter difference only; distance is not quality."}

def cross_branch(parent_a: dict[str, Any], parent_b: dict[str, Any], inherit_a: list[str], inherit_b: list[str]) -> dict[str, Any]:
    dna_a, dna_b = parent_a.get("design_dna", {}), parent_b.get("design_dna", {})
    conflicts = []
    if "strategy" in inherit_a and "strategy" in inherit_b and dna_a.get("composition_family") != dna_b.get("composition_family"):
        conflicts.append("strategy")
    if conflicts:
        return {"status": "CONFLICT", "conflicts": conflicts, "auto_conflict_decision": False, "decision_created": False}
    merged = dict(parent_a["alternative"].get("parameters", {}))
    for key in inherit_b:
        if key in parent_b["alternative"].get("parameters", {}): merged[key] = parent_b["alternative"]["parameters"][key]
    return {"status": "COMPATIBLE", "candidate_parameters": merged, "parents": [parent_a["alternative"]["alternative_id"], parent_b["alternative"]["alternative_id"]], "decision_created": False}

def search_by_example(seed: dict[str, Any], candidates: list[dict[str, Any]], mode: str = "SIMILAR") -> dict[str, Any]:
    mode = mode.upper()
    if mode not in {"SIMILAR", "DIVERSE", "BALANCED"}: raise ValueError("INVALID_SEARCH_MODE")
    ranked = sorted((dict(item, distance=design_distance(seed, item)) for item in candidates), key=lambda item: item["distance"]["distance"], reverse=mode == "DIVERSE")
    return {"seed": seed.get("alternative_id") or seed.get("alternative", {}).get("alternative_id"), "mode": mode, "candidates": ranked[:5], "seed_is_preference": False, "decision_created": False}

def extreme_exploration(parent: dict[str, Any], direction: str) -> dict[str, Any]:
    direction = direction.upper()
    if direction not in {"MORE_COMPACT", "MORE_OPEN_SPACE", "GREATER_SEPARATION", "HIGHER_AREA_EFFICIENCY"}: raise ValueError("UNSUPPORTED_EXTREME")
    target, intensity = ("footprint_ratio", 100) if direction == "MORE_COMPACT" else (("footprint_ratio", 0) if direction == "MORE_OPEN_SPACE" else (("mass_separation", 100) if direction == "GREATER_SEPARATION" else ("footprint_ratio", 80)))
    profile = inheritance_profile(parent, inherit=["strategy"], mutable=[target], bounds={})
    return dict(directed_mutation(parent, profile, target, intensity), exploration_mode="EXTREME", extreme=direction, automatic_winner=False)

def advanced_evolution(parent: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    mode = str(payload.get("mode", "MUTATE")).upper()
    profile = inheritance_profile(parent, payload.get("inherit"), payload.get("mutable"), payload.get("bounds"))
    if mode == "MUTATE": return directed_mutation(parent, profile, str(payload.get("target", "footprint_ratio")), int(payload.get("intensity", 40)))
    if mode == "EXTREME": return extreme_exploration(parent, str(payload.get("direction", "MORE_COMPACT")))
    if mode == "SERENDIPITY": return dict(directed_mutation(parent, profile, "mass_separation", 70), exploration_mode="SERENDIPITY", automatic_winner=False)
    raise ValueError("UNSUPPORTED_ADVANCED_EVOLUTION_MODE")
