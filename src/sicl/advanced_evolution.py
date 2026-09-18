from __future__ import annotations

from dataclasses import asdict
from math import sqrt
from typing import Any

from .gdi import apply_design_operation, design_dna
from .hierarchical_design import derive_hierarchical_state
from .spatial_generator import UPAO001SpatialGenerator
from .spatial_evaluation import spatial_metrics
from .v11 import Alternative

INTENSITIES = tuple(range(0, 101, 10))
MUTABLE = {"footprint_ratio", "courtyard_ratio", "mass_separation", "floors"}


def _alt(value: dict[str, Any]) -> Alternative:
    return Alternative(**value)


def _vector(value: dict[str, Any]) -> dict[str, float]:
    source = value.get("alternative", value)
    p = source.get("parameters", {}) if isinstance(source, dict) else {}
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


DIRECTIONS = {"MORE_OPEN", "MORE_COMPACT", "MORE_COURTYARD", "MORE_ARTICULATED", "MORE_SEPARATED", "LOWER_HEIGHT", "HIGHER_DENSITY"}


def _direction_specs(direction: str) -> list[tuple[str, dict[str, Any]]]:
    direction = direction.upper()
    if direction not in DIRECTIONS:
        raise ValueError("UNSUPPORTED_EXPLORATION_DIRECTION")
    return {
        "MORE_OPEN": [("CREATE_COURTYARD", {"courtyard_ratio": 0.20}), ("CREATE_COURTYARD", {"courtyard_ratio": 0.30}), ("MODIFY_OPEN_SPACE", {"footprint_ratio": 0.30}), ("SET_GAP", {"distance": 6.0}), ("SET_GAP", {"distance": 8.0}), ("SET_GAP", {"distance": 10.0})],
        "MORE_COMPACT": [("SCALE", {"footprint_ratio": 0.60}), ("SCALE", {"footprint_ratio": 0.58})],
        "MORE_COURTYARD": [("CREATE_COURTYARD", {"courtyard_ratio": 0.25}), ("CREATE_COURTYARD", {"courtyard_ratio": 0.31}), ("CREATE_COURTYARD", {"courtyard_ratio": 0.31})],
        "MORE_ARTICULATED": [("ARTICULATE", {"mass_separation": 4.0}), ("ARTICULATE", {"mass_separation": 8.0})],
        "MORE_SEPARATED": [("SET_GAP", {"distance": 6.0}), ("SET_GAP", {"distance": 10.0})],
        "LOWER_HEIGHT": [("CHANGE_HEIGHT", {"floors": 3}), ("CHANGE_HEIGHT", {"floors": 4})],
        "HIGHER_DENSITY": [("CHANGE_HEIGHT", {"floors": 6}), ("SCALE", {"footprint_ratio": 0.55})],
    }[direction]


def _operation_controls(operation_type: str, controls: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    affected = {
        "CREATE_COURTYARD": {"courtyard_ratio", "footprint_ratio"},
        "RESIZE_COURTYARD": {"courtyard_ratio", "footprint_ratio"},
        "MODIFY_OPEN_SPACE": {"footprint_ratio"},
        "SCALE": {"footprint_ratio"},
        "SET_GAP": {"mass_separation"},
        "ARTICULATE": {"mass_separation"},
        "CHANGE_HEIGHT": {"floors"},
    }.get(operation_type, set())
    return {key: rule for key, rule in controls.items() if key in affected or str(rule.get("mode", "FREE")).upper() == "LOCK"}


def bounded_diverse_exploration(parent: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    """Generate transient bounded candidates and select structural representatives."""
    direction = str(payload.get("direction", "MORE_OPEN")).upper()
    budget = str(payload.get("budget", "STANDARD")).upper()
    budget_limit = {"QUICK": 6, "STANDARD": 10, "DEEP": 14}.get(budget, 6)
    controls = dict(payload.get("controls", {}))
    if payload.get("human_confirmed") is not True:
        raise ValueError("HUMAN_CONFIRMATION_REQUIRED")
    base = _alt(parent["alternative"] if "alternative" in parent else parent)
    specs = (_direction_specs(direction) * ((budget_limit // len(_direction_specs(direction))) + 1))[:budget_limit]
    generator = UPAO001SpatialGenerator()
    internal: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for index, (operation_type, parameters) in enumerate(specs):
        try:
            child, operation = apply_design_operation(base, operation_type, parameters, _operation_controls(operation_type, controls), payload.get("intent_refs", []), payload.get("knowledge_refs", []))
            representation = generator.generate(child)
            dna = design_dna(child)
            hierarchical_state = derive_hierarchical_state(asdict(child), representation.to_dict(), payload.get("space_layout"), downstream_state="RECOMPUTED")
            record = {"alternative": asdict(child), "operation": asdict(operation), "representation": representation.to_dict(), "hierarchical_state": hierarchical_state, "metrics": spatial_metrics(representation, generator), "design_dna": dna, "parent_alternative_id": base.alternative_id, "direction": direction, "candidate_index": index, "traceable": True, "representative": False, "representative_reason": None, "automatic_winner": False, "recommendation_created": False, "decision_created": False}
            record["design_contribution_trace"] = {"parent_alternative_id": base.alternative_id, "exploration_request": {"direction": direction, "budget": budget, "controls": controls, "human_confirmed": True}, "operation_sequence": [asdict(operation)], "target_spatial_scope": payload.get("target_spatial_scope", "edificacion"), "candidate_alternative_id": child.alternative_id, "knowledge_refs": list(payload.get("knowledge_refs", [])), "intent_refs": list(payload.get("intent_refs", [])), "expected_effect": "Explore a bounded spatial direction; no performance claim.", "observed_effect": {"metrics": record["metrics"], "hierarchical_state": record["hierarchical_state"], "design_dna": dna}, "uncertainty": ["Synthetic geometry; real-world performance remains unknown."]}
            duplicate = next((item for item in internal if item["alternative"]["parameters"] == record["alternative"]["parameters"]), None)
            if duplicate:
                rejected.append({"candidate_index": index, "status": "EXACT_DUPLICATE", "duplicate_of": duplicate["alternative"]["alternative_id"]})
                continue
            near = next((item for item in internal if design_distance(item, record)["distance"] < 0.02), None)
            if near:
                rejected.append({"candidate_index": index, "status": "NEAR_DUPLICATE", "near_duplicate_of": near["alternative"]["alternative_id"], "distance": design_distance(near, record)})
                continue
            internal.append(record)
        except (ValueError, Exception) as exc:
            rejected.append({"candidate_index": index, "status": "REJECTED", "reason": str(exc)})
    representatives: list[dict[str, Any]] = []
    families: dict[str, list[str]] = {}
    for item in internal:
        family = item["design_dna"]["composition_family"]
        families.setdefault(family, []).append(item["alternative"]["alternative_id"])
        if family not in {candidate["design_dna"]["composition_family"] for candidate in representatives}:
            item["representative"] = True
            item["representative_reason"] = "family coverage"
            item["design_contribution_trace"]["representative_reason"] = "family coverage"
            item["design_contribution_trace"]["family"] = family
            representatives.append(item)
    for item in sorted(internal, key=lambda value: value["alternative"]["alternative_id"]):
        if len(representatives) >= 5:
            break
        if item in representatives:
            continue
        nearest = min((design_distance(item, selected)["distance"] for selected in representatives), default=0.0)
        if nearest >= 0.05:
            item["representative"] = True
            item["representative_reason"] = "structural distance coverage"
            item["distance_from_representatives"] = nearest
            item["design_contribution_trace"]["representative_reason"] = "structural distance coverage"
            item["design_contribution_trace"]["distance_from_representatives"] = nearest
            item["design_contribution_trace"]["family"] = item["design_dna"]["composition_family"]
            representatives.append(item)
    status = "OK" if representatives else "NO_VALID_CANDIDATES"
    if len(representatives) < 2 and internal:
        status = "INSUFFICIENT_DIVERSITY_WITHIN_CURRENT_BOUNDS"
    return {"status": status, "request": {"project_id": base.project_id, "parent_alternative_id": base.alternative_id, "direction": direction, "budget": budget, "controls": controls, "human_confirmed": True, "authorized_operations": sorted({item["operation"]["operation_type"] for item in internal})}, "internal_candidate_count": len(specs), "valid_candidate_count": len(internal), "rejected_candidates": rejected, "candidates": internal, "representatives": representatives, "presented_count": len(representatives), "design_families": families, "automatic_winner": False, "recommendation_created": False, "decision_created": False, "provenance": "P6 bounded deterministic exploration over existing GDI operations"}


__all__ = ["DIRECTIONS", "bounded_diverse_exploration", "DesignOperation", "advanced_evolution", "cross_branch", "design_distance", "design_dna", "directed_mutation", "extreme_exploration", "inheritance_profile", "search_by_example"]
