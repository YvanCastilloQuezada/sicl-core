from dataclasses import asdict

from sicl.advanced_evolution import design_distance
from sicl.hierarchical_design import derive_hierarchical_state
from sicl.spatial_generator import UPAO001SpatialGenerator, generate_upao001_alternatives
from sicl.spatial_synthesis import build_spatial_graph, demo_program, generate_space_layout


def _record(alternative, family="COURTYARD"):
    program = demo_program()
    layout = generate_space_layout(program, build_spatial_graph(program), alternative.alternative_id, family)
    representation = UPAO001SpatialGenerator().generate(alternative).to_dict()
    return {"alternative": asdict(alternative), "representation": representation, "metrics": {"site_area": 1200.0, "footprint_area": 400.0, "gross_massing_area": 6000.0, "open_site_area": 800.0}, "hierarchical_state": derive_hierarchical_state(asdict(alternative), representation, layout)}


def test_same_supported_state_with_different_ids_is_exact_duplicate():
    original = generate_upao001_alternatives()[0]
    left = _record(original)
    right_alt = original.__class__(**{**asdict(original), "alternative_id": "UPAO-001-SAME-STATE"})
    right = _record(right_alt)
    result = design_distance(left, right)
    assert result["classification"] == "EXACT_DUPLICATE"
    assert result["components"]["geometry_distance"] == 0.0


def test_same_family_with_different_geometry_is_not_collapsed_by_family():
    alternatives = generate_upao001_alternatives()
    left = _record(alternatives[0], "COURTYARD")
    right = _record(alternatives[1], "COURTYARD")
    result = design_distance(left, right)
    assert result["classification"] in {"NEAR_DUPLICATE", "MEANINGFULLY_DISTINCT"}
    assert result["components"]["geometry_distance"] is not None
    assert result["is_quality_score"] is False


def test_missing_derived_state_is_explicitly_unknown():
    left = {"alternative": asdict(generate_upao001_alternatives()[0])}
    right = {"alternative": asdict(generate_upao001_alternatives()[1])}
    result = design_distance(left, right)
    assert result["components"]["geometry_distance"] is None
    assert result["component_details"]["relationships"] == "UNKNOWN"
    assert result["explanation"].endswith("Unsupported components remain UNKNOWN.")
