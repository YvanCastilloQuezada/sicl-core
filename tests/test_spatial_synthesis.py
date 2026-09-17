from sicl.spatial_synthesis import build_spatial_graph, demo_program, generate_space_layout, synthesize_form_space


def test_program_and_graph_preserve_required_and_preferred_relationships():
    program = demo_program()
    graph = build_spatial_graph(program)
    assert len(program.requirements) == 5
    assert {edge.strength for edge in graph.edges} == {"REQUIRED", "PREFERRED"}
    assert graph.nodes == tuple(item.id for item in program.requirements)


def test_space_layout_has_identifiable_spaces_and_circulation():
    program = demo_program()
    graph = build_spatial_graph(program)
    layout = generate_space_layout(program, graph, "UPAO-001-P3-A", "COURTYARD")
    representation = layout["representation"]
    zones = [item for item in representation["elements"] if item["element_type"] == "SPATIAL_ZONE"]
    circulation = [item for item in representation["elements"] if item["element_type"] == "CIRCULATION_ELEMENT"]
    assert len(zones) == 6
    assert len(circulation) == 1
    assert all(item["metadata"]["program_requirement_id"] for item in zones)
    assert layout["validation"] == "GENERATED_LAYOUT_NOT_VALIDATED"


def test_form_space_synthesis_keeps_lineage_and_no_winner():
    program = demo_program()
    graph = build_spatial_graph(program)
    layouts = [generate_space_layout(program, graph, f"UPAO-001-P3-{family[0]}", family) for family in ("CENTRALIZED", "COURTYARD", "LINEAR")]
    result = synthesize_form_space(program, graph, layouts)
    assert len(result["alternatives"]) == 3
    assert result["lineage"]["graph_to_space"] is True
    assert result["automatic_winner"] is False
    assert result["decision_created"] is False
