from dataclasses import asdict

import pytest

from sicl.advanced_evolution import advanced_evolution, cross_branch, design_distance, inheritance_profile, search_by_example
from sicl.spatial_generator import generate_upao001_alternatives


def parent(strategy="compact"):
    value = next(item for item in generate_upao001_alternatives() if item.parameters.get("strategy") == strategy)
    return {"alternative": asdict(value), "design_dna": {"composition_family": strategy.upper()}}


def test_directed_mutation_is_bounded_and_traceable():
    result = advanced_evolution(parent(), {"mode": "MUTATE", "target": "footprint_ratio", "intensity": 40, "bounds": {"footprint_ratio": {"min": 0.30, "max": 0.55}}})
    assert result["mutation"]["intensity"] == 40
    assert result["inheritance"]["bounded"]
    assert result["decision_created"] is False


def test_cross_branch_surfaces_conflict_without_auto_resolution():
    result = cross_branch(parent("compact"), parent("courtyard"), ["strategy"], ["strategy"])
    assert result["status"] == "CONFLICT"
    assert result["auto_conflict_decision"] is False


def test_distance_is_transparent_not_quality_and_search_has_modes():
    left, right = parent("compact"), parent("courtyard")
    distance = design_distance(left, right)
    assert distance["is_quality_score"] is False
    search = search_by_example(left, [right], "DIVERSE")
    assert search["mode"] == "DIVERSE"
    assert search["seed_is_preference"] is False


def test_invalid_mutation_is_rejected():
    with pytest.raises(ValueError, match="UNSUPPORTED_MUTATION_TARGET"):
        advanced_evolution(parent(), {"mode": "MUTATE", "target": "profitability", "intensity": 40})
