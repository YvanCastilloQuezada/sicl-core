from sicl.hierarchical_design import derive_hierarchical_state, hierarchical_compare, propagate_space_geometry_change, propagate_upstream_change
from sicl.spatial_generator import UPAO001SpatialGenerator, generate_upao001_alternatives
from sicl.spatial_synthesis import build_spatial_graph, demo_program, generate_space_layout


def _state(alternative):
    representation = UPAO001SpatialGenerator().generate(alternative).to_dict()
    program = demo_program()
    layout = generate_space_layout(program, build_spatial_graph(program), alternative.alternative_id, "COURTYARD")
    return derive_hierarchical_state(alternative.__dict__, representation, layout)


def test_hierarchical_state_derives_site_building_mass_and_space_nodes():
    state = _state(generate_upao001_alternatives()[0])
    assert state["validity"] == "VALID_DERIVED_STATE"
    assert {node["kind"] for node in state["nodes"]} == {"SITE", "BUILDING", "MASS", "SPACE"}
    assert all(node["id"] for node in state["nodes"])
    assert all(dependency["type"] == "DEPENDS_ON" for dependency in state["dependencies"])


def test_upstream_propagation_reports_recomputed_dependents_without_fake_certainty():
    parent = _state(generate_upao001_alternatives()[0])
    child = _state(generate_upao001_alternatives()[1])
    result = propagate_upstream_change(parent, child, "BUILDING")
    assert result["status"] == "RECOMPUTED"
    assert result["affected_nodes"]
    assert result["requires_human_review"] is True
    assert result["unknown"]


def test_hierarchical_compare_is_multilevel_and_never_selects_winner():
    left = _state(generate_upao001_alternatives()[0])
    right = _state(generate_upao001_alternatives()[1])
    result = hierarchical_compare(left, right)
    assert set(result["levels"]) == {"SITE", "BUILDING", "MASS", "SPACE"}
    assert result["no_winner"] is True
    assert result["recommendation_created"] is False
    assert result["decision_created"] is False


def test_mass_geometry_change_recomputes_dependent_spaces_and_requires_review():
    state = _state(generate_upao001_alternatives()[0])
    mass = next(node for node in state["nodes"] if node["kind"] == "MASS")
    result = propagate_space_geometry_change(state, state, mass["id"], {"footprint_ratio": 0.36, "mass_separation": 8.0})
    assert result["status"] == "REQUIRES_HUMAN_REVIEW"
    assert result["recomputed"]
    assert result["requires_human_review"] is True
    assert result["invalidated"] == []
    assert result["unknown"]
