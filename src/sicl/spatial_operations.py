"""Formal, reversible architectural operations over existing GDI alternatives.

This is an operational projection over Alternative + DesignOperation + existing
spatial generation. It deliberately does not introduce a new canonical entity.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .gdi import DesignOperation, apply_design_operation, design_dna
from .spatial_evaluation import spatial_metrics
from .spatial_generator import UPAO001SpatialGenerator, generate_upao001_alternatives
from .v11 import Alternative

OPERATION_CAPABILITIES: dict[str, dict[str, Any]] = {
    "MOVE_MASS": {"status": "PARTIAL", "implementation": "requires positional geometry parameter not yet canonical"},
    "ROTATE_MASS": {"status": "PARTIAL", "implementation": "orientation is retained but generator rotation is not yet canonical"},
    "SCALE_MASS": {"status": "AVAILABLE", "implementation": "existing GDI SCALE / footprint_ratio"},
    "SPLIT_MASS": {"status": "AVAILABLE", "implementation": "existing GDI SPLIT / articulated multi-mass"},
    "SET_GAP": {"status": "AVAILABLE", "implementation": "existing articulated mass_separation"},
    "CHANGE_HEIGHT": {"status": "AVAILABLE", "implementation": "existing GDI CHANGE_HEIGHT / floors"},
    "CREATE_COURTYARD": {"status": "AVAILABLE", "implementation": "existing courtyard geometry"},
    "MODIFY_COURTYARD": {"status": "AVAILABLE", "implementation": "existing RESIZE_COURTYARD / courtyard_ratio"},
    "ADD_MASS": {"status": "NOT_CURRENTLY_SUPPORTED", "implementation": "no canonical add-mass model"},
    "REMOVE_MASS": {"status": "NOT_CURRENTLY_SUPPORTED", "implementation": "no canonical remove-mass model"},
    "MERGE_MASSES": {"status": "NOT_CURRENTLY_SUPPORTED", "implementation": "no canonical merge model"},
    "OFFSET_MASS": {"status": "NOT_CURRENTLY_SUPPORTED", "implementation": "no canonical positional offset model"},
    "STEP_MASS": {"status": "NOT_CURRENTLY_SUPPORTED", "implementation": "no canonical stepped mass model"},
    "ARTICULATE_MASS": {"status": "AVAILABLE", "implementation": "existing GDI ARTICULATE"},
}

_OPERATION_MAP = {
    "SCALE_MASS": "SCALE",
    "SPLIT_MASS": "SPLIT",
    "SET_GAP": "SET_GAP",
    "CHANGE_HEIGHT": "CHANGE_HEIGHT",
    "CREATE_COURTYARD": "CREATE_COURTYARD",
    "MODIFY_COURTYARD": "RESIZE_COURTYARD",
    "ARTICULATE_MASS": "ARTICULATE",
}


def operation_capabilities() -> dict[str, dict[str, Any]]:
    return {key: dict(value) for key, value in OPERATION_CAPABILITIES.items()}


def _base(alternative_id: str) -> Alternative:
    for item in generate_upao001_alternatives():
        if item.alternative_id == alternative_id:
            return item
    raise ValueError("BASE_ALTERNATIVE_NOT_FOUND")


def _mass_targets(alternative: Alternative) -> list[str]:
    representation = UPAO001SpatialGenerator().generate(alternative)
    return [item.id for item in representation.elements if item.element_type == "BuildingMass"]


def propose_operation(
    alternative: Alternative,
    operation_type: str,
    parameters: dict[str, Any] | None = None,
    *,
    intent_linkage: list[str] | None = None,
    knowledge_linkage: list[str] | None = None,
    controls: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    operation = operation_type.upper()
    capability = OPERATION_CAPABILITIES.get(operation)
    if capability is None:
        raise ValueError(f"UNSUPPORTED_DESIGN_OPERATION:{operation}")
    if capability["status"] != "AVAILABLE":
        raise ValueError(f"OPERATION_NOT_AVAILABLE:{operation}")
    params = dict(parameters or {})
    target = str(params.pop("target", "MASS_01"))
    if target not in {"MASS_01", "MASS_02", "ALL_MASSES"} and not target.startswith("SR-"):
        raise ValueError("INVALID_OPERATION_TARGET")
    mapped = _OPERATION_MAP[operation]
    child, executed = apply_design_operation(
        alternative,
        mapped,
        params,
        controls or {},
        intent_linkage or [],
        knowledge_linkage or [],
    )
    representation = UPAO001SpatialGenerator().generate(child)
    metrics_before = spatial_metrics(UPAO001SpatialGenerator().generate(alternative), UPAO001SpatialGenerator())
    metrics_after = spatial_metrics(representation, UPAO001SpatialGenerator())
    target_ids = _mass_targets(alternative)
    return {
        "operation": {**asdict(executed), "operation_type": operation, "target": target, "target_element_ids": target_ids, "execution_status": "PREVIEW", "reversible": True, "inverse_operation": {"operation_type": operation, "source_alternative_id": child.alternative_id, "restoration": "BRANCH_OR_REPLAY"}},
        "parent": asdict(alternative),
        "proposed_child": asdict(child),
        "before_representation": UPAO001SpatialGenerator().generate(alternative).to_dict(),
        "after_representation": representation.to_dict(),
        "metrics_before": metrics_before,
        "metrics_after": metrics_after,
        "metric_deltas": {key: metrics_after[key] - metrics_before[key] for key in metrics_after if isinstance(metrics_after[key], (int, float)) and isinstance(metrics_before.get(key), (int, float))},
        "design_dna_before": design_dna(alternative),
        "design_dna_after": design_dna(child),
        "status": "PREVIEW",
        "human_confirmation_required": True,
        "decision_created": False,
        "recommendation_created": False,
    }


def execute_operation(
    alternative: Alternative,
    operation_type: str,
    parameters: dict[str, Any] | None = None,
    *,
    intent_linkage: list[str] | None = None,
    knowledge_linkage: list[str] | None = None,
    controls: dict[str, dict[str, Any]] | None = None,
    human_confirmed: bool = False,
) -> dict[str, Any]:
    if not human_confirmed:
        raise ValueError("HUMAN_CONFIRMATION_REQUIRED")
    result = propose_operation(alternative, operation_type, parameters, intent_linkage=intent_linkage, knowledge_linkage=knowledge_linkage, controls=controls)
    result["operation"]["execution_status"] = "EXECUTED"
    result["status"] = "EXECUTED"
    result["proposed_child"]["source"] = "SPATIAL_OPERATION_P0"
    return result


def execute_sequence(alternative: Alternative, operations: list[dict[str, Any]], *, human_confirmed: bool = False) -> dict[str, Any]:
    if not human_confirmed:
        raise ValueError("HUMAN_CONFIRMATION_REQUIRED")
    current = alternative
    steps: list[dict[str, Any]] = []
    for index, spec in enumerate(operations, start=1):
        result = execute_operation(current, str(spec.get("operation_type", "")), dict(spec.get("parameters", {})), intent_linkage=spec.get("intent_linkage", []), knowledge_linkage=spec.get("knowledge_linkage", []), controls=spec.get("controls", {}), human_confirmed=True)
        result["operation"]["sequence_order"] = index
        steps.append(result)
        current = Alternative(**result["proposed_child"])
    return {"parent_alternative_id": alternative.alternative_id, "child_alternative": asdict(current), "steps": steps, "operation_history": [step["operation"] for step in steps], "status": "EXECUTED", "reversible": True, "reversal": "BRANCH_OR_REPLAY_FROM_PARENT", "automatic_winner": False, "recommendation_created": False, "decision_created": False}


__all__ = ["OPERATION_CAPABILITIES", "operation_capabilities", "propose_operation", "execute_operation", "execute_sequence"]
