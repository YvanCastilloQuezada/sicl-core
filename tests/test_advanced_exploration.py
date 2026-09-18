import pytest

from sicl.advanced_evolution import bounded_diverse_exploration, design_distance
from sicl.spatial_generator import generate_upao001_alternatives


def _request():
    return {
        "direction": "MORE_OPEN",
        "budget": "STANDARD",
        "human_confirmed": True,
        "controls": {
            "floors": {"mode": "LOCK", "value": 5},
            "courtyard_ratio": {"mode": "RANGE", "min": 0.20, "max": 0.35},
            "mass_separation": {"mode": "RANGE", "min": 4.0, "max": 10.0},
        },
        "intent_refs": ["INT-OPEN"],
        "knowledge_refs": ["ITEM-APL-001"],
    }


def test_bounded_exploration_requires_human_confirmation():
    base = {"alternative": generate_upao001_alternatives()[0].__dict__}
    with pytest.raises(ValueError, match="HUMAN_CONFIRMATION_REQUIRED"):
        bounded_diverse_exploration(base, {"direction": "MORE_OPEN"})


def test_bounded_exploration_preserves_bounds_and_selects_families():
    base = {"alternative": generate_upao001_alternatives()[0].__dict__}
    result = bounded_diverse_exploration(base, _request())
    assert result["status"] == "OK"
    assert result["internal_candidate_count"] == 10
    assert result["presented_count"] >= 2
    assert len(result["design_families"]) >= 2
    assert result["automatic_winner"] is False
    assert result["recommendation_created"] is False
    assert result["decision_created"] is False
    for candidate in result["candidates"]:
        assert candidate["alternative"]["parameters"]["floors"] == 5
        if "courtyard_ratio" in candidate["alternative"]["parameters"] and candidate["alternative"]["parameters"]["strategy"] == "courtyard":
            assert 0.20 <= candidate["alternative"]["parameters"]["courtyard_ratio"] <= 0.35


def test_duplicate_control_is_reported_naturally_and_distance_is_explainable():
    base = {"alternative": generate_upao001_alternatives()[0].__dict__}
    result = bounded_diverse_exploration(base, {**_request(), "direction": "MORE_COURTYARD", "budget": "STANDARD"})
    assert any(item["status"] in {"EXACT_DUPLICATE", "NEAR_DUPLICATE"} for item in result["rejected_candidates"])
    reps = result["representatives"]
    assert len(reps) >= 1
    if len(reps) > 1:
        distance = design_distance(reps[0], reps[1])
        assert distance["is_quality_score"] is False
        assert "components" in distance


def test_determinism_and_second_generation_branch():
    base = {"alternative": generate_upao001_alternatives()[0].__dict__}
    first = bounded_diverse_exploration(base, _request())
    second = bounded_diverse_exploration(base, _request())
    assert [item["alternative"]["alternative_id"] for item in first["representatives"]] == [item["alternative"]["alternative_id"] for item in second["representatives"]]
    chosen = first["representatives"][0]
    child = bounded_diverse_exploration(chosen, {**_request(), "direction": "LOWER_HEIGHT", "budget": "QUICK", "controls": {"floors": {"mode": "RANGE", "min": 2, "max": 5}}})
    assert child["request"]["parent_alternative_id"] == chosen["alternative"]["alternative_id"]
    assert all(item["parent_alternative_id"] == chosen["alternative"]["alternative_id"] for item in child["candidates"])


def test_unsupported_direction_is_explicit():
    base = {"alternative": generate_upao001_alternatives()[0].__dict__}
    with pytest.raises(ValueError, match="UNSUPPORTED_EXPLORATION_DIRECTION"):
        bounded_diverse_exploration(base, {**_request(), "direction": "UNKNOWN_DIRECTION"})
