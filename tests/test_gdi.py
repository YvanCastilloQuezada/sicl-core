import pytest

from sicl.gdi import apply_design_operation, explore_design_space, evolve_from_candidate, multi_agent_challenge, multiobjective_search
from sicl.spatial_generator import generate_upao001_alternatives


def test_design_operation_supports_distinct_composition_operations():
    base = generate_upao001_alternatives()[0]
    child, operation = apply_design_operation(base, "COURTYARD", {}, {}, ["INT-1"], ["ITEM-1"])
    assert child.parameters["strategy"] == "courtyard"
    assert operation.operation_type == "COURTYARD"
    assert child.alternative_id != base.alternative_id


def test_lock_and_range_controls_are_enforced():
    base = generate_upao001_alternatives()[0]
    with pytest.raises(ValueError, match="LOCKED_PARAMETER_CHANGED"):
        apply_design_operation(base, "CHANGE_HEIGHT", {"floors": 3}, {"floors": {"mode": "LOCK", "value": 5}}, [], [])
    child, _ = apply_design_operation(base, "CHANGE_HEIGHT", {"floors": 4}, {"floors": {"mode": "RANGE", "min": 3, "max": 4}}, [], [])
    assert child.parameters["floors"] == 4


def test_bounded_exploration_preserves_diversity_and_no_winner():
    adopted = {"adoption": "HUMAN_CONFIRMED", "adopted_intents": [{"intent_id": "INT-1"}]}
    result = explore_design_space("UPAO-001-A", adopted, {"links": [{"knowledge_item_id": "ITEM-1"}]}, {"budget": "STANDARD", "controls": {}})
    assert len(result["candidates"]) == 5
    assert result["diversity_preserved"] is True
    assert result["automatic_winner"] is False
    assert all(item["traceable"] for item in result["candidates"])


def test_multi_agent_challenge_preserves_disagreement():
    result = multi_agent_challenge({"alternative": {"alternative_id": "UPAO-001-A"}, "design_dna": {"composition_family": "COMPACT"}})
    assert len(result["perspectives"]) == 5
    assert result["disagreement_preserved"] is True
    assert result["winner"] is None


def test_evolution_and_multiobjective_map_keep_design_primary():
    adopted = {"adoption": "HUMAN_CONFIRMED", "adopted_intents": [{"intent_id": "INT-1"}]}
    exploration = explore_design_space("UPAO-001-A", adopted, {"links": []}, {"budget": "QUICK", "controls": {}})
    evolved = evolve_from_candidate(exploration["candidates"][0], "CHANGE_THAT", {"parameters": {"floors": 3}, "controls": {}})
    assert evolved["parent_alternative_id"] == exploration["candidates"][0]["alternative"]["alternative_id"]
    mapped = multiobjective_search(exploration)
    assert mapped["points"]
    assert mapped["pareto_front"]
    assert mapped["automatic_winner"] is False
