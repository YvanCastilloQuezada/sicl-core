from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .design_intent import interpret_intent

MODALITIES = {"LANGUAGE", "SKETCH", "REFERENCE_IMAGE", "GRAPHICAL_SELECTION", "DIRECT_MANIPULATION"}

@dataclass(frozen=True)
class MultimodalCandidate:
    input_id: str
    project_id: str
    modality: str
    interpretation: str
    candidate_intent: dict[str, Any]
    operation: dict[str, Any] | None
    status: str
    human_confirmation_required: bool
    decision_created: bool
    provenance: dict[str, Any]


def interpret_multimodal_input(project_id: str, modality: str, payload: dict[str, Any], *, input_id: str = "MMI-LOCAL") -> dict[str, Any]:
    mode = modality.upper().strip()
    if mode not in MODALITIES:
        raise ValueError("UNSUPPORTED_MODALITY")
    provenance = {"source": "USER_PROVIDED_MULTIMODAL_INPUT", "modality": mode, "input_id": input_id, "project_id": project_id}
    operation = None
    if mode == "LANGUAGE":
        text = str(payload.get("text", "")).strip()
        if not text:
            raise ValueError("LANGUAGE_INPUT_REQUIRED")
        candidate = interpret_intent(text, project_id=project_id)
        interpretation = text
        candidate_intent = candidate
    elif mode == "SKETCH":
        hint = str(payload.get("semantic_hint", "")).strip()
        primitives = payload.get("primitives") or []
        if not primitives and not hint:
            raise ValueError("SKETCH_PRIMITIVE_OR_HINT_REQUIRED")
        interpretation = hint or "Bounded graphical primitives require semantic interpretation"
        candidate_intent = {"kind": "SPATIAL_INTENT", "statement": interpretation, "primitives": primitives, "confidence": "MEDIUM"}
    elif mode == "REFERENCE_IMAGE":
        annotation = str(payload.get("annotation", "")).strip()
        if not annotation:
            raise ValueError("REFERENCE_IMAGE_ANNOTATION_REQUIRED")
        interpretation = annotation
        candidate_intent = {"kind": "REFERENCE_CHARACTERISTIC", "statement": annotation, "confidence": "USER_IDENTIFIED"}
    elif mode == "GRAPHICAL_SELECTION":
        target = str(payload.get("target_id", "")).strip()
        action = str(payload.get("action", "")).upper().strip()
        if not target or action not in {"KEEP_THIS", "CHANGE_THAT"}:
            raise ValueError("GRAPHICAL_SELECTION_REQUIRES_TARGET_AND_SUPPORTED_ACTION")
        interpretation = f"{action} on {target}"
        candidate_intent = {"kind": "SELECTED_ELEMENT_INTENT", "target_id": target, "action": action}
        operation = {"operation_type": action, "target_id": target}
    else:
        target = str(payload.get("target_id", "")).strip()
        operation_type = str(payload.get("operation", "")).upper().strip()
        if not target or operation_type not in {"MOVE", "RESIZE", "ROTATE", "SCALE"}:
            raise ValueError("DIRECT_MANIPULATION_REQUIRES_SUPPORTED_TARGET_AND_OPERATION")
        interpretation = f"{operation_type} on {target}"
        candidate_intent = {"kind": "DIRECT_MANIPULATION", "target_id": target, "operation": operation_type, "preview": payload.get("preview")}
        operation = {"operation_type": operation_type, "target_id": target, "preview": payload.get("preview")}
    result = asdict(MultimodalCandidate(input_id, project_id, mode, interpretation, candidate_intent, operation, "CANDIDATE_REQUIRES_CONFIRMATION", True, False, provenance))
    return result


def confirm_multimodal_candidate(candidate: dict[str, Any], actor: str) -> dict[str, Any]:
    if not actor.strip() or actor.upper() == "SYSTEM":
        raise ValueError("HUMAN_AUTHORITY_REQUIRED")
    adopted = dict(candidate)
    adopted.update({"status": "HUMAN_CONFIRMED", "actor": actor, "decision_created": False, "human_confirmation_required": False, "provenance": {**candidate.get("provenance", {}), "confirmation": "HUMAN_CONFIRMATION"}})
    return adopted
