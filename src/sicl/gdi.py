from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Iterable

from .spatial_evaluation import spatial_metrics
from .spatial_generator import UPAO001SpatialGenerator, generate_upao001_alternatives
from .v11 import Alternative


SUPPORTED_OPERATIONS = {
    "COMPACT", "COURTYARD", "MULTI_BLOCK", "ARTICULATED",
    "CREATE_COURTYARD", "RESIZE_COURTYARD", "MODIFY_OPEN_SPACE",
    "CHANGE_HEIGHT", "SCALE", "SPLIT", "ARTICULATE",
}
BUDGETS = {"QUICK": 3, "STANDARD": 5, "DEEP": 6}


@dataclass(frozen=True)
class DesignOperation:
    operation_id: str
    operation_type: str
    target: str
    parameters: dict[str, Any]
    parent_alternative_id: str
    intent_linkage: list[str]
    knowledge_linkage: list[str]
    constraint_state: str
    provenance: dict[str, Any]
    status: str = "AUTHORIZED"
    reversible: bool = True


def _digest(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()[:12]


def _controls(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    controls = payload.get("controls", {})
    return controls if isinstance(controls, dict) else {}


def _assert_controls(parameters: dict[str, Any], controls: dict[str, dict[str, Any]]) -> None:
    for name, rule in controls.items():
        if not isinstance(rule, dict):
            continue
        mode = str(rule.get("mode", "FREE")).upper()
        value = parameters.get(name)
        if mode == "LOCK" and value != rule.get("value", value):
            raise ValueError(f"LOCKED_PARAMETER_CHANGED:{name}")
        if mode == "RANGE" and value is not None:
            low, high = float(rule.get("min", value)), float(rule.get("max", value))
            if not low <= float(value) <= high:
                raise ValueError(f"PARAMETER_OUT_OF_RANGE:{name}")
        if mode not in {"LOCK", "FREE", "RANGE"}:
            raise ValueError(f"INVALID_CONTROL_MODE:{name}")


def _base(alternative_id: str) -> Alternative:
    for item in generate_upao001_alternatives():
        if item.alternative_id == alternative_id:
            return item
    raise ValueError("BASE_ALTERNATIVE_NOT_FOUND")


def apply_design_operation(base: Alternative, operation_type: str, parameters: dict[str, Any], controls: dict[str, dict[str, Any]], intent_linkage: list[str], knowledge_linkage: list[str]) -> tuple[Alternative, DesignOperation]:
    operation = operation_type.upper()
    if operation not in SUPPORTED_OPERATIONS:
        raise ValueError(f"UNSUPPORTED_DESIGN_OPERATION:{operation}")
    next_parameters = dict(base.parameters)
    if operation in {"COMPACT", "SCALE"}:
        next_parameters["strategy"] = "compact"
        next_parameters["footprint_ratio"] = float(parameters.get("footprint_ratio", min(0.70, float(next_parameters.get("footprint_ratio", 0.42)) + 0.06)))
    elif operation in {"COURTYARD", "CREATE_COURTYARD", "RESIZE_COURTYARD"}:
        next_parameters["strategy"] = "courtyard"
        next_parameters["courtyard_ratio"] = float(parameters.get("courtyard_ratio", 0.30))
        next_parameters["footprint_ratio"] = float(parameters.get("footprint_ratio", 0.48))
    elif operation in {"MULTI_BLOCK", "SPLIT"}:
        next_parameters["strategy"] = "articulated"
        next_parameters["mass_separation"] = float(parameters.get("mass_separation", 6.0))
        next_parameters["footprint_ratio"] = float(parameters.get("footprint_ratio", 0.36))
    elif operation == "ARTICULATE":
        next_parameters["strategy"] = "articulated"
        next_parameters["mass_separation"] = float(parameters.get("mass_separation", 4.0))
    elif operation == "MODIFY_OPEN_SPACE":
        next_parameters["footprint_ratio"] = float(parameters.get("footprint_ratio", 0.30))
    elif operation == "CHANGE_HEIGHT":
        next_parameters["floors"] = int(parameters.get("floors", max(1, int(next_parameters.get("floors", 4)) - 1)))
    _assert_controls(next_parameters, controls)
    operation_id = f"OP-{_digest({'base': base.alternative_id, 'type': operation, 'parameters': next_parameters})}"
    op = DesignOperation(operation_id, operation, "SPATIAL_MASSING", parameters, base.alternative_id, intent_linkage, knowledge_linkage, "UNKNOWN_UNLESS_EXPLICITLY_SUPPLIED", {"method": "GDI_P1_DETERMINISTIC", "classification": ["SYNTHETIC", "EDUCATIONAL"]})
    child_id = f"{base.alternative_id}-GDI-{_digest(asdict(op))[:8]}"
    child = Alternative(child_id, base.project_id, operation, "Architect-guided derived alternative", next_parameters, "GENERATED", 1, "GDI_P1_OPERATION")
    return child, op


def design_dna(alternative: Alternative) -> dict[str, Any]:
    p = alternative.parameters
    return {"alternative_id": alternative.alternative_id, "composition_family": str(p.get("strategy", "unknown")).upper(), "mass_count": 2 if p.get("strategy") == "articulated" else 1, "orientation": "UNSPECIFIED", "courtyard_proportion": p.get("courtyard_ratio", 0.0), "height_profile": p.get("floors"), "footprint_ratio": p.get("footprint_ratio"), "articulation": p.get("strategy") == "articulated", "mass_distribution": p.get("mass_separation", 0.0)}


def explore_design_space(base_alternative_id: str, adopted_intent: dict[str, Any], knowledge: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    budget_name = str(payload.get("budget", "QUICK")).upper()
    count = BUDGETS.get(budget_name, BUDGETS["QUICK"])
    controls = _controls(payload)
    intent_ids = [item.get("intent_id") for item in adopted_intent.get("adopted_intents", [])]
    knowledge_ids = [link.get("knowledge_item_id", link.get("pattern_id")) for link in knowledge.get("links", [])]
    base = _base(base_alternative_id)
    operations = ["COMPACT", "COURTYARD", "MULTI_BLOCK", "ARTICULATED", "CHANGE_HEIGHT", "MODIFY_OPEN_SPACE"][:count]
    candidates: list[dict[str, Any]] = []
    families: dict[str, list[str]] = {}
    generator = UPAO001SpatialGenerator()
    for operation_type in operations:
        try:
            child, operation = apply_design_operation(base, operation_type, {}, controls, intent_ids, knowledge_ids)
            representation = generator.generate(child)
            metrics = spatial_metrics(representation, generator)
            record = {"alternative": asdict(child), "operation": asdict(operation), "representation": representation.to_dict(), "metrics": metrics, "design_dna": design_dna(child), "parent_alternative_id": base.alternative_id, "traceable": True, "validated": False, "recommendation_created": False, "decision_created": False}
            candidates.append(record)
            families.setdefault(record["design_dna"]["composition_family"], []).append(child.alternative_id)
        except ValueError:
            continue
    return {"budget": budget_name, "base_alternative_id": base.alternative_id, "candidates": candidates, "design_families": families, "diversity_preserved": len({item["design_dna"]["composition_family"] for item in candidates}) > 1, "automatic_winner": False, "unknown_constraint_is_not_pass": True, "provenance": "GDI-P1 bounded deterministic exploration"}


def evolve_from_candidate(candidate: dict[str, Any], action: str, payload: dict[str, Any]) -> dict[str, Any]:
    alternative = Alternative(**candidate["alternative"])
    operation_type = "CHANGE_HEIGHT" if action == "CHANGE_THAT" else "ARTICULATE"
    child, operation = apply_design_operation(alternative, operation_type, payload.get("parameters", {}), payload.get("controls", {}), candidate["operation"].get("intent_linkage", []), candidate["operation"].get("knowledge_linkage", []))
    return {"alternative": asdict(child), "operation": asdict(operation), "parent_alternative_id": alternative.alternative_id, "design_dna": design_dna(child), "decision_created": False}


def multi_agent_challenge(alternative: dict[str, Any], knowledge: dict[str, Any] | None = None) -> dict[str, Any]:
    dna = alternative.get("design_dna", {})
    family = dna.get("composition_family", "UNKNOWN")
    return {"alternative_id": alternative.get("alternative", {}).get("alternative_id", alternative.get("alternative_id")), "perspectives": [{"role": "GENERALIST_DESIGN", "stance": "PROPOSE", "observation": f"{family} offers a coherent spatial direction; compare against alternatives."}, {"role": "BIOCLIMATIC_DESIGN", "stance": "CHALLENGE", "observation": "Solar/shadow implications require supported environmental evidence; no performance claim is made."}, {"role": "URBAN_SITE", "stance": "EVALUATE", "observation": "Site relationship remains synthetic and should be reviewed at the applicable scale."}, {"role": "DEVELOPER_AREA_EFFICIENCY", "stance": "EVALUATE", "observation": "Area metrics are descriptive; no cost or profitability is inferred."}, {"role": "BEAUTY_HARMONY", "stance": "PROPOSE", "observation": "Massing distinction is visible; aesthetic judgment remains human."}], "disagreement_preserved": True, "winner": None, "recommendation_created": False, "decision_created": False}


def multiobjective_search(exploration: dict[str, Any]) -> dict[str, Any]:
    candidates = exploration.get("candidates", [])
    points = [{"alternative_id": item["alternative"]["alternative_id"], "x": item["metrics"].get("gross_massing_area"), "y": item["metrics"].get("open_site_area"), "design_dna": item["design_dna"], "representation": item["representation"], "provenance": "S2 deterministic spatial metrics"} for item in candidates]
    frontier = []
    for point in points:
        dominated = any(other is not point and other["x"] >= point["x"] and other["y"] >= point["y"] and (other["x"] > point["x"] or other["y"] > point["y"]) for other in points)
        if not dominated:
            frontier.append(point["alternative_id"])
    return {"objectives": [{"id": "GROSS_MASSING_AREA", "direction": "MAXIMIZE", "unit": "m²"}, {"id": "OPEN_SITE_AREA", "direction": "MAXIMIZE", "unit": "m²"}], "points": points, "pareto_front": frontier, "automatic_winner": False, "recommendation_created": False, "decision_created": False, "design_primary": True, "data_secondary": True}


__all__ = ["DesignOperation", "SUPPORTED_OPERATIONS", "BUDGETS", "apply_design_operation", "design_dna", "explore_design_space", "evolve_from_candidate", "multi_agent_challenge", "multiobjective_search"]
