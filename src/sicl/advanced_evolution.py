from __future__ import annotations

from dataclasses import asdict
from math import sqrt
from typing import Any

from .gdi import apply_design_operation, design_dna
from .hierarchical_design import derive_hierarchical_state, propagate_space_geometry_change
from .spatial_generator import UPAO001SpatialGenerator
from .spatial_evaluation import spatial_metrics
from .v11 import Alternative

INTENSITIES = tuple(range(0, 101, 10))
MUTABLE = {"footprint_ratio", "courtyard_ratio", "mass_separation", "floors"}
NEAR_DUPLICATE_AGGREGATE_TOLERANCE = 0.02  # PROPOSED / REQUIRES VALIDATION; computational, not quality.


def _alt(value: dict[str, Any]) -> Alternative:
    return Alternative(**value)


def _vector(value: dict[str, Any]) -> dict[str, float]:
    source = value.get("alternative", value)
    p = source.get("parameters", {}) if isinstance(source, dict) else {}
    return {key: float(p[key]) for key in MUTABLE if key in p and isinstance(p[key], (int, float))}


def _comparison_source(value: dict[str, Any]) -> dict[str, Any]:
    return value.get("alternative", value) if isinstance(value.get("alternative", value), dict) else value


def _bbox(geometry: dict[str, Any] | None) -> tuple[float, float, float, float] | None:
    if not isinstance(geometry, dict):
        return None
    coords = geometry.get("coordinates", [])
    points: list[tuple[float, float]] = []
    def collect(node: Any) -> None:
        if isinstance(node, (list, tuple)) and len(node) >= 2 and all(isinstance(item, (int, float)) for item in node[:2]):
            points.append((float(node[0]), float(node[1])))
        elif isinstance(node, (list, tuple)):
            for item in node: collect(item)
    collect(coords)
    if not points: return None
    xs, ys = zip(*points)
    return min(xs), min(ys), max(xs), max(ys)


def _bbox_area(box: tuple[float, float, float, float] | None) -> float:
    return max(0.0, (box[2] - box[0]) * (box[3] - box[1])) if box else 0.0


def _bbox_iou(left: tuple[float, float, float, float] | None, right: tuple[float, float, float, float] | None) -> float | None:
    if not left or not right: return None
    ix = max(0.0, min(left[2], right[2]) - max(left[0], right[0]))
    iy = max(0.0, min(left[3], right[3]) - max(left[1], right[1]))
    intersection = ix * iy
    union = _bbox_area(left) + _bbox_area(right) - intersection
    return intersection / union if union else 1.0


def _geometry_summary(value: dict[str, Any]) -> dict[str, Any] | None:
    representation = value.get("representation")
    if not isinstance(representation, dict): return None
    elements = representation.get("elements", [])
    footprints = [item for item in elements if str(item.get("element_type", "")).upper() == "BUILDINGFOOTPRINT"]
    masses = [item for item in elements if str(item.get("element_type", "")).upper() == "BUILDINGMASS"]
    footprint = _bbox(footprints[0].get("geometry")) if footprints else None
    mass_boxes = [_bbox(item.get("geometry")) for item in masses]
    mass_boxes = [box for box in mass_boxes if box]
    heights = [float(item.get("metadata", {}).get("height", 0.0)) for item in masses if isinstance(item.get("metadata", {}).get("height", 0.0), (int, float))]
    return {"footprint_bbox": footprint, "footprint_area": _bbox_area(footprint), "mass_count": len(masses), "mass_boxes": mass_boxes, "height": max(heights, default=0.0), "mass_area": sum(_bbox_area(box) for box in mass_boxes)}


def _metric_summary(value: dict[str, Any]) -> dict[str, float]:
    metrics = value.get("metrics", {})
    return {key: float(metrics[key]) for key in ("site_area", "footprint_area", "gross_massing_area", "open_site_area") if isinstance(metrics.get(key), (int, float))}


def _relationship_signature(value: dict[str, Any]) -> set[tuple[str, str, str]] | None:
    state = value.get("hierarchical_state")
    if not isinstance(state, dict): return None
    result = set()
    for item in state.get("dependencies", []):
        result.add(("DEPENDENCY", "", str(item.get("type"))))
    for item in state.get("relationships", []):
        result.add(("PROGRAM", "", str(item.get("relationship_type", item.get("type")))))
    return result


def _hierarchy_signature(value: dict[str, Any]) -> dict[str, int] | None:
    state = value.get("hierarchical_state")
    if not isinstance(state, dict): return None
    return {kind: sum(1 for node in state.get("nodes", []) if node.get("kind") == kind) for kind in ("SITE", "BUILDING", "MASS", "SPACE")}


def _space_geometry_distance(left: dict[str, Any], right: dict[str, Any]) -> float | None:
    left_nodes = [node for node in left.get("nodes", []) if node.get("kind") == "SPACE"]
    right_nodes = [node for node in right.get("nodes", []) if node.get("kind") == "SPACE"]
    if not left_nodes or not right_nodes or len(left_nodes) != len(right_nodes): return None
    distances = []
    for left_node, right_node in zip(left_nodes, right_nodes):
        lb, rb = _bbox(left_node.get("geometry")), _bbox(right_node.get("geometry"))
        if not lb or not rb: return None
        left_center = ((lb[0] + lb[2]) / 2.0, (lb[1] + lb[3]) / 2.0)
        right_center = ((rb[0] + rb[2]) / 2.0, (rb[1] + rb[3]) / 2.0)
        distances.append(sqrt((left_center[0] - right_center[0]) ** 2 + (left_center[1] - right_center[1]) ** 2) / max(1.0, _bbox_area(lb) ** 0.5, _bbox_area(rb) ** 0.5))
    return round(sum(distances) / len(distances), 4)


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
    parameter_components = {}
    for key in keys:
        denominator = 1.0 if key in {"footprint_ratio", "courtyard_ratio"} else max(1.0, abs(a.get(key, 0.0)), abs(b.get(key, 0.0)))
        parameter_components[key] = round(abs(a.get(key, 0.0) - b.get(key, 0.0)) / denominator, 4)
    parameter_distance = round(sum(parameter_components.values()) / max(1, len(parameter_components)), 4)
    left_geo, right_geo = _geometry_summary(left), _geometry_summary(right)
    geometry_details: dict[str, Any] = {"status": "UNKNOWN"}
    geometry_distance: float | None = None
    if left_geo and right_geo:
        iou = _bbox_iou(left_geo["footprint_bbox"], right_geo["footprint_bbox"])
        area_diff = abs(left_geo["footprint_area"] - right_geo["footprint_area"]) / max(1.0, left_geo["footprint_area"], right_geo["footprint_area"])
        count_diff = abs(left_geo["mass_count"] - right_geo["mass_count"]) / max(1, left_geo["mass_count"], right_geo["mass_count"])
        height_diff = abs(left_geo["height"] - right_geo["height"]) / max(1.0, left_geo["height"], right_geo["height"])
        geometry_distance = round(sum((area_diff, 1.0 - (iou if iou is not None else 0.0), count_diff, height_diff)) / 4.0, 4)
        geometry_details = {"status": "AVAILABLE", "footprint_area_difference": round(area_diff, 4), "footprint_bbox_iou": round(iou, 4) if iou is not None else None, "mass_count_difference": round(count_diff, 4), "height_difference": round(height_diff, 4), "normalization": "observed project geometry domain; computational tolerance only"}
    left_metrics, right_metrics = _metric_summary(left), _metric_summary(right)
    metric_keys = sorted(set(left_metrics) | set(right_metrics))
    metric_components = {key: round(abs(left_metrics.get(key, 0.0) - right_metrics.get(key, 0.0)) / max(1.0, abs(left_metrics.get(key, 0.0)), abs(right_metrics.get(key, 0.0))), 4) for key in metric_keys}
    metric_distance = round(sum(metric_components.values()) / max(1, len(metric_components)), 4) if metric_keys else None
    left_rel, right_rel = _relationship_signature(left), _relationship_signature(right)
    relationship_distance = None if left_rel is None or right_rel is None else round(len(left_rel.symmetric_difference(right_rel)) / max(1, len(left_rel | right_rel)), 4)
    left_h, right_h = _hierarchy_signature(left), _hierarchy_signature(right)
    left_state, right_state = left.get("hierarchical_state"), right.get("hierarchical_state")
    space_geometry_distance = _space_geometry_distance(left_state, right_state) if isinstance(left_state, dict) and isinstance(right_state, dict) else None
    hierarchy_count_distance = None if left_h is None or right_h is None else round(sum(abs(left_h[k] - right_h[k]) for k in left_h) / max(1, sum(max(left_h[k], right_h[k]) for k in left_h)), 4)
    hierarchy_values = [value for value in (hierarchy_count_distance, space_geometry_distance) if value is not None]
    hierarchy_distance = round(sum(hierarchy_values) / len(hierarchy_values), 4) if hierarchy_values else None
    available = [value for value in (parameter_distance, geometry_distance, metric_distance, relationship_distance, hierarchy_distance) if value is not None]
    aggregate = round(sum(available) / max(1, len(available)), 4)
    same_state = parameter_distance == 0 and (geometry_distance in (None, 0.0)) and (metric_distance in (None, 0.0)) and (relationship_distance in (None, 0.0)) and (hierarchy_distance in (None, 0.0))
    classification = "EXACT_DUPLICATE" if same_state else ("NEAR_DUPLICATE" if aggregate < NEAR_DUPLICATE_AGGREGATE_TOLERANCE else "MEANINGFULLY_DISTINCT")
    return {"left": _comparison_source(left).get("alternative_id"), "right": _comparison_source(right).get("alternative_id"), "distance": aggregate, "classification": classification, "components": {"parameter_distance": parameter_distance, "geometry_distance": geometry_distance, "metric_distance": metric_distance, "relationship_distance": relationship_distance, "hierarchical_distance": hierarchy_distance}, "component_details": {"parameter": parameter_components, "geometry": geometry_details, "metrics": metric_components, "relationships": "AVAILABLE" if relationship_distance is not None else "UNKNOWN", "hierarchy": {"count_distance": hierarchy_count_distance, "space_geometry_distance": space_geometry_distance} if hierarchy_distance is not None else "UNKNOWN"}, "is_quality_score": False, "explanation": "Explainable design difference; distance is not quality. Unsupported components remain UNKNOWN."}


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
    parent_representation = generator.generate(base).to_dict()
    parent_hierarchical_state = derive_hierarchical_state(asdict(base), parent_representation, payload.get("space_layout"), downstream_state="PRESERVED")
    internal: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for index, (operation_type, parameters) in enumerate(specs):
        try:
            child, operation = apply_design_operation(base, operation_type, parameters, _operation_controls(operation_type, controls), payload.get("intent_refs", []), payload.get("knowledge_refs", []))
            representation = generator.generate(child)
            dna = design_dna(child)
            hierarchical_state = derive_hierarchical_state(asdict(child), representation.to_dict(), payload.get("space_layout"), downstream_state="RECOMPUTED")
            changed_mass = next((node for node in hierarchical_state["nodes"] if node["kind"] == "MASS"), None)
            propagation = propagate_space_geometry_change(parent_hierarchical_state, hierarchical_state, changed_mass["id"], parameters) if changed_mass else {"status": "UNKNOWN", "unknown": ["No mass node is currently represented."]}
            record = {"alternative": asdict(child), "operation": asdict(operation), "representation": representation.to_dict(), "hierarchical_state": hierarchical_state, "space_propagation": propagation, "metrics": spatial_metrics(representation, generator), "design_dna": dna, "parent_alternative_id": base.alternative_id, "direction": direction, "candidate_index": index, "traceable": True, "representative": False, "representative_reason": None, "automatic_winner": False, "recommendation_created": False, "decision_created": False}
            record["design_contribution_trace"] = {"parent_alternative_id": base.alternative_id, "exploration_request": {"direction": direction, "budget": budget, "controls": controls, "human_confirmed": True}, "operation_sequence": [asdict(operation)], "target_spatial_scope": payload.get("target_spatial_scope", "edificacion"), "candidate_alternative_id": child.alternative_id, "knowledge_refs": list(payload.get("knowledge_refs", [])), "intent_refs": list(payload.get("intent_refs", [])), "expected_effect": "Explore a bounded spatial direction; no performance claim.", "observed_effect": {"metrics": record["metrics"], "hierarchical_state": record["hierarchical_state"], "design_dna": dna}, "uncertainty": ["Synthetic geometry; real-world performance remains unknown."]}
            comparison = next(((item, design_distance(item, record)) for item in internal if design_distance(item, record)["classification"] == "EXACT_DUPLICATE"), None)
            if comparison:
                duplicate, evidence = comparison
                rejected.append({"candidate_index": index, "status": "EXACT_DUPLICATE", "duplicate_of": duplicate["alternative"]["alternative_id"], "evidence": evidence})
                continue
            near = next(((item, design_distance(item, record)) for item in internal if design_distance(item, record)["classification"] == "NEAR_DUPLICATE"), None)
            if near:
                near_item, evidence = near
                rejected.append({"candidate_index": index, "status": "NEAR_DUPLICATE", "near_duplicate_of": near_item["alternative"]["alternative_id"], "distance": evidence})
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
        comparisons = [design_distance(item, selected) for selected in representatives]
        distinct_from_all = all(comparison["classification"] == "MEANINGFULLY_DISTINCT" for comparison in comparisons)
        nearest = min((comparison["distance"] for comparison in comparisons), default=0.0)
        if distinct_from_all:
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
    clusters = [{"cluster_id": f"CLUSTER-{index + 1}", "representative_id": item["alternative"]["alternative_id"], "member_ids": [item["alternative"]["alternative_id"]], "classification": "MEANINGFULLY_DISTINCT", "evidence": "No near-duplicate members retained in this cluster."} for index, item in enumerate(representatives)]
    return {"status": status, "request": {"project_id": base.project_id, "parent_alternative_id": base.alternative_id, "direction": direction, "budget": budget, "controls": controls, "human_confirmed": True, "authorized_operations": sorted({item["operation"]["operation_type"] for item in internal})}, "internal_candidate_count": len(specs), "valid_candidate_count": len(internal), "rejected_candidates": rejected, "candidates": internal, "representatives": representatives, "presented_count": len(representatives), "design_families": families, "near_duplicate_clusters": clusters, "near_duplicate_tolerance": {"aggregate": NEAR_DUPLICATE_AGGREGATE_TOLERANCE, "classification": "PROPOSED / REQUIRES_VALIDATION", "meaning": "computational tolerance only; not architectural significance or quality"}, "automatic_winner": False, "recommendation_created": False, "decision_created": False, "provenance": "P6 bounded deterministic exploration over existing GDI operations"}


__all__ = ["DIRECTIONS", "bounded_diverse_exploration", "DesignOperation", "advanced_evolution", "cross_branch", "design_distance", "design_dna", "directed_mutation", "extreme_exploration", "inheritance_profile", "search_by_example"]
