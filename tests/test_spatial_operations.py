import pytest

from sicl.spatial_generator import generate_upao001_alternatives, UPAO001SpatialGenerator
from sicl.spatial_operations import execute_operation, execute_sequence, operation_capabilities, propose_operation


def test_operation_capabilities_classify_supported_and_deferred_operations():
    capabilities = operation_capabilities()
    assert capabilities["CREATE_COURTYARD"]["status"] == "AVAILABLE"
    assert capabilities["SET_GAP"]["status"] == "AVAILABLE"
    assert capabilities["MOVE_MASS"]["status"] == "PARTIAL"
    assert capabilities["ADD_MASS"]["status"] == "NOT_CURRENTLY_SUPPORTED"


def test_preview_requires_available_operation_and_exposes_target_ids():
    base = generate_upao001_alternatives()[0]
    preview = propose_operation(base, "CREATE_COURTYARD", {"courtyard_ratio": 0.30}, intent_linkage=["INT-1"], knowledge_linkage=["ITEM-1"])
    assert preview["status"] == "PREVIEW"
    assert preview["operation"]["target_element_ids"]
    assert preview["operation"]["execution_status"] == "PREVIEW"
    assert preview["decision_created"] is False


def test_execute_requires_human_confirmation_and_preserves_geometry_lineage():
    base = generate_upao001_alternatives()[0]
    with pytest.raises(ValueError, match="HUMAN_CONFIRMATION_REQUIRED"):
        execute_operation(base, "SCALE_MASS", {"footprint_ratio": 0.50})
    result = execute_operation(base, "SCALE_MASS", {"footprint_ratio": 0.50}, human_confirmed=True)
    assert result["status"] == "EXECUTED"
    assert result["proposed_child"]["alternative_id"] != base.alternative_id
    assert result["operation"]["parent_alternative_id"] == base.alternative_id
    assert result["metrics_after"]["footprint_area"] != result["metrics_before"]["footprint_area"]


def test_three_operation_sequences_are_deterministic_and_reversible_by_branching():
    base = generate_upao001_alternatives()[0]
    operations = [
        {"operation_type": "CREATE_COURTYARD", "parameters": {"courtyard_ratio": 0.25}},
        {"operation_type": "SET_GAP", "parameters": {"distance": 6.0}},
        {"operation_type": "CHANGE_HEIGHT", "parameters": {"floors": 3}},
    ]
    sequence = execute_sequence(base, operations, human_confirmed=True)
    assert sequence["status"] == "EXECUTED"
    assert len(sequence["steps"]) == 3
    assert [step["operation"]["sequence_order"] for step in sequence["steps"]] == [1, 2, 3]
    assert sequence["reversible"] is True
    preserved = execute_sequence(base, operations[:2], human_confirmed=True)
    assert preserved["child_alternative"]["alternative_id"] != sequence["child_alternative"]["alternative_id"]
    assert sequence["parent_alternative_id"] == base.alternative_id


def test_keep_change_controls_preserve_locked_values_and_bound_ranges():
    base = generate_upao001_alternatives()[0]
    with pytest.raises(ValueError, match="LOCKED_PARAMETER_CHANGED"):
        propose_operation(base, "CHANGE_HEIGHT", {"floors": 3}, controls={"floors": {"mode": "LOCK", "value": 5}})
    bounded = propose_operation(base, "CHANGE_HEIGHT", {"floors": 4}, controls={"floors": {"mode": "RANGE", "min": 3, "max": 4}})
    assert bounded["proposed_child"]["parameters"]["floors"] == 4


def test_materially_distinct_operation_families_have_distinct_spatial_metrics():
    base = generate_upao001_alternatives()[0]
    generator = UPAO001SpatialGenerator()
    courtyard = execute_operation(base, "CREATE_COURTYARD", {"courtyard_ratio": 0.30}, human_confirmed=True)
    articulated = execute_operation(base, "SPLIT_MASS", {"mass_separation": 8.0}, human_confirmed=True)
    assert courtyard["proposed_child"]["parameters"]["strategy"] == "courtyard"
    assert articulated["proposed_child"]["parameters"]["strategy"] == "articulated"
    assert courtyard["proposed_child"]["alternative_id"] != articulated["proposed_child"]["alternative_id"]
    assert courtyard["metrics_after"]["gross_massing_area"] != articulated["metrics_after"]["gross_massing_area"]
    assert len([e for e in generator.generate(__import__('sicl.v11', fromlist=['Alternative']).Alternative(**courtyard['proposed_child'])).elements if e.element_type == 'BuildingMass']) != len([e for e in generator.generate(__import__('sicl.v11', fromlist=['Alternative']).Alternative(**articulated['proposed_child'])).elements if e.element_type == 'BuildingMass'])
