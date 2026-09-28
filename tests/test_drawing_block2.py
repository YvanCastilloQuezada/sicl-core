from dataclasses import replace
import xml.etree.ElementTree as ET

import pytest

from sicl.archi import ArchiElement
from sicl.drawing import (
    DrawingAdapterError,
    Scale,
    graphic_scene_to_svg,
)
from sicl.projection import project_architectural_plan
from sicl.representation import GraphicStyle
from test_projection import contracts, poc_elements


ROLES = (
    "WALL_CUT", "WALL_PROJECTED", "SPACE_BOUNDARY", "DOOR_EVIDENCE",
    "WINDOW_EVIDENCE", "OPENING_CUT", "OPENING_PROJECTED",
    "COLUMN_CUT", "COLUMN_PROJECTED", "SLAB_PROJECTED", "BEAM_PROJECTED",
)


def make_scene(elements=None, style=None):
    elements = tuple(elements or poc_elements())
    source, view, profile, _old_style, annotation = contracts(elements)
    style = style or GraphicStyle(
        "BLOCK2-STYLE",
        line_weights={role: "CUT" if role == "WALL_CUT" else "MEDIUM" for role in ROLES},
    )
    return project_architectural_plan(elements, source, view, profile, style, annotation)


def test_graphicscene_to_svg_real_vector_e2e_and_traceability():
    scene = make_scene()
    adapted, svg = graphic_scene_to_svg(scene, scale=Scale.S_1_50)
    root = ET.fromstring(svg)
    ns = {"s": "http://www.w3.org/2000/svg"}
    polygons = root.findall(".//s:polygon", ns)
    assert len(polygons) == 6
    assert not root.findall(".//s:image", ns)
    assert all(item.primitive_id in adapted.primitive_sources for item in adapted.viewport.elements)
    assert all("data-primitive-id" in item.attrib for item in polygons)
    assert all("data-source-ref" in item.attrib for item in polygons)
    entity_ids = {entity.entity_id for entity in scene.entities}
    assert {item.attrib["data-source-ref"] for item in polygons} == entity_ids


def test_svg_is_deterministic_and_coordinates_are_explicitly_transformed():
    scene = make_scene()
    first, svg1 = graphic_scene_to_svg(scene)
    second, svg2 = graphic_scene_to_svg(scene)
    assert svg1 == svg2
    assert first.primitive_ids == second.primitive_ids
    assert first.coordinate_policy == "PLAN_XY_MM->SVG_DEVICE_MM; explicit_bbox_margin"
    assert first.y_axis_policy == "PLAN_Y_UP_TO_SVG_Y_DOWN"
    assert 'xmlns="http://www.w3.org/2000/svg"' in svg1


def test_style_changes_appearance_not_geometry():
    base_style = GraphicStyle("STYLE-A", line_weights={role: "MEDIUM" for role in ROLES})
    cut_style = GraphicStyle("STYLE-B", line_weights={role: ("CUT" if role == "WALL_CUT" else "MEDIUM") for role in ROLES})
    scene_a = make_scene(style=base_style)
    scene_b = make_scene(style=cut_style)
    adapted_a, svg_a = graphic_scene_to_svg(scene_a)
    adapted_b, svg_b = graphic_scene_to_svg(scene_b)
    assert [item.geometry_intent for item in scene_a.entities] == [item.geometry_intent for item in scene_b.entities]
    assert svg_a != svg_b
    wall_a = next(item for item in adapted_a.viewport.elements if item.semantic_role == "WALL_CUT")
    wall_b = next(item for item in adapted_b.viewport.elements if item.semantic_role == "WALL_CUT")
    assert wall_a.weight != wall_b.weight


def test_mutation_reaches_svg_while_unaffected_primitives_remain_stable():
    elements = poc_elements()
    scene_a = make_scene(elements)
    moved = replace(elements[0], geometry=replace(elements[0].geometry, x_mm=300))
    changed = (moved, *elements[1:])
    source, view, profile, _style, annotation = contracts(changed)
    style = GraphicStyle("BLOCK2-STYLE", line_weights={role: "MEDIUM" for role in ROLES})
    scene_b = project_architectural_plan(changed, source, view, profile, style, annotation)
    adapted_a, svg_a = graphic_scene_to_svg(scene_a)
    adapted_b, svg_b = graphic_scene_to_svg(scene_b)
    assert svg_a != svg_b
    unaffected = elements[1].element_id.value
    source_a = next(entity.entity_id for entity in scene_a.entities if entity.trace.source_entity_refs == (unaffected,))
    source_b = next(entity.entity_id for entity in scene_b.entities if entity.trace.source_entity_refs == (unaffected,))
    assert source_a == source_b
    prim_a = next(pid for pid, eid in adapted_a.primitive_sources.items() if eid == source_a)
    prim_b = next(pid for pid, eid in adapted_b.primitive_sources.items() if eid == source_b)
    assert prim_a == prim_b


def test_door_evidence_has_no_swing_arc_and_no_material_hatch():
    scene = make_scene()
    adapted, svg = graphic_scene_to_svg(scene)
    assert not any(item.semantic_role == "DOOR_EVIDENCE" and item.__class__.__name__ == "Arc" for item in adapted.viewport.elements)
    assert "url(#masonry)" not in svg and "url(#concrete)" not in svg


def test_unknown_role_geometry_and_style_fail_closed():
    scene = make_scene()
    unknown = replace(scene.entities[0], role="UNKNOWN_ROLE")
    bad_scene = replace(scene, entities=(unknown, *scene.entities[1:]))
    with pytest.raises(DrawingAdapterError, match="UNSUPPORTED_GRAPHIC_ROLE:UNKNOWN_ROLE"):
        graphic_scene_to_svg(bad_scene)
    missing_style = GraphicStyle("MISSING", line_weights={})
    with pytest.raises(DrawingAdapterError, match="STYLE_MAPPING_REQUIRED"):
        graphic_scene_to_svg(make_scene(style=missing_style))


def test_empty_scene_is_explicitly_rejected():
    scene = make_scene()
    empty = replace(scene, entities=())
    with pytest.raises(DrawingAdapterError, match="EMPTY_GRAPHIC_SCENE"):
        graphic_scene_to_svg(empty)


def test_unknown_visibility_and_cut_relation_fail_closed():
    scene = make_scene()
    unknown = replace(scene.entities[0], geometry_intent={**dict(scene.entities[0].geometry_intent), "visibility": "UNKNOWN_VISIBILITY"})
    with pytest.raises(DrawingAdapterError, match="UNRESOLVED_VISIBILITY"):
        graphic_scene_to_svg(replace(scene, entities=(unknown, *scene.entities[1:])))
    unresolved = replace(scene.entities[0], geometry_intent={**dict(scene.entities[0].geometry_intent), "cut_relation": "ABOVE_CUT"})
    with pytest.raises(DrawingAdapterError, match="UNRESOLVED_CUT_RELATION"):
        graphic_scene_to_svg(replace(scene, entities=(unresolved, *scene.entities[1:])))


def test_malformed_trace_and_geometry_fail_closed():
    scene = make_scene()
    malformed_trace = replace(scene.entities[0], trace=None)
    with pytest.raises(DrawingAdapterError, match="MALFORMED_GRAPHIC_TRACE"):
        graphic_scene_to_svg(replace(scene, entities=(malformed_trace, *scene.entities[1:])))
    malformed_geometry = replace(scene.entities[0], geometry_intent={**dict(scene.entities[0].geometry_intent), "width_mm": "nan"})
    with pytest.raises(DrawingAdapterError, match="NONFINITE_GEOMETRY"):
        graphic_scene_to_svg(replace(scene, entities=(malformed_geometry, *scene.entities[1:])))
    negative_geometry = replace(scene.entities[0], geometry_intent={**dict(scene.entities[0].geometry_intent), "depth_mm": -1})
    with pytest.raises(DrawingAdapterError, match="NONPOSITIVE_GEOMETRY"):
        graphic_scene_to_svg(replace(scene, entities=(negative_geometry, *scene.entities[1:])))
