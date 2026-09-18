import pytest

from sicl.multimodal import confirm_multimodal_candidate, interpret_multimodal_input


def test_language_and_sketch_converge_to_candidate_intent():
    language = interpret_multimodal_input("UPAO-001", "LANGUAGE", {"text": "Conserva el patio"}, input_id="L1")
    sketch = interpret_multimodal_input("UPAO-001", "SKETCH", {"semantic_hint": "PRESERVE_REGION", "primitives": [{"type": "closed_region", "points": [[0, 0], [1, 1]]}]}, input_id="S1")
    assert language["status"] == "CANDIDATE_REQUIRES_CONFIRMATION"
    assert sketch["candidate_intent"]["kind"] == "SPATIAL_INTENT"
    assert language["decision_created"] is False
    assert sketch["provenance"]["modality"] == "SKETCH"


def test_reference_image_requires_human_annotation_and_confirmation():
    with pytest.raises(ValueError, match="REFERENCE_IMAGE_ANNOTATION_REQUIRED"):
        interpret_multimodal_input("UPAO-001", "REFERENCE_IMAGE", {"image_ref": "local://image"})
    candidate = interpret_multimodal_input("UPAO-001", "REFERENCE_IMAGE", {"image_ref": "local://image", "annotation": "organización alrededor de un patio"})
    adopted = confirm_multimodal_candidate(candidate, "architect-1")
    assert adopted["status"] == "HUMAN_CONFIRMED"
    assert adopted["decision_created"] is False


def test_selection_and_manipulation_map_only_to_supported_operations():
    selected = interpret_multimodal_input("UPAO-001", "GRAPHICAL_SELECTION", {"target_id": "SpatialZone:1", "action": "CHANGE_THAT"})
    moved = interpret_multimodal_input("UPAO-001", "DIRECT_MANIPULATION", {"target_id": "SpatialZone:1", "operation": "MOVE", "preview": {"dx": 1}})
    assert selected["operation"]["operation_type"] == "CHANGE_THAT"
    assert moved["operation"]["operation_type"] == "MOVE"
    with pytest.raises(ValueError, match="HUMAN_AUTHORITY_REQUIRED"):
        confirm_multimodal_candidate(moved, "SYSTEM")
