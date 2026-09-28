from dataclasses import replace

import pytest

from sicl.archi import ArchiElement, ArchiElementId, ArchiGeometry, ElementKind, GeometryKind, ProfileSpec
from sicl.projection import ProjectionError, canonical_d2_fingerprint, project_architectural_plan
from sicl.representation import (
    AnnotationProfile,
    GraphicStyle,
    ProfileKind,
    ProjectionKind,
    RepresentationError,
    RepresentationProfile,
    SourceAuthority,
    SourceSnapshot,
    ViewDefinition,
    ViewFamily,
    ViewType,
)


HASH = "a" * 64


def element(project: str, kind: ElementKind, nonce: str, x: int, y: int, width: int, depth: int, *, hosted_in=None):
    return ArchiElement(
        ArchiElementId.compute(project, kind.value, nonce),
        project,
        kind,
        ArchiGeometry(GeometryKind.EXTRUDED_RECTANGLE, ProfileSpec(width, depth), x_mm=x, y_mm=y, height_mm=2800),
        properties={"source_key": nonce} if kind is ElementKind.DOOR else {},
        hosted_in=hosted_in,
    )


def poc_elements():
    project = "P-POC-S1"
    w01 = element(project, ElementKind.WALL, "W01", 0, 0, 5000, 200)
    w02 = element(project, ElementKind.WALL, "W02", 0, 4800, 5000, 200)
    w03 = element(project, ElementKind.WALL, "W03", 0, 200, 200, 4600)
    w04 = element(project, ElementKind.WALL, "W04", 4800, 200, 200, 4600)
    a01 = element(project, ElementKind.SPACE, "A01", 200, 200, 4600, 4600)
    d01 = element(project, ElementKind.DOOR, "D01", 2200, 0, 900, 200, hosted_in=w01.element_id)
    return (w01, w02, w03, w04, a01, d01)


def contracts(elements):
    source = SourceSnapshot(
        "MODEL-POC-S1", "D2", "1", canonical_d2_fingerprint(elements), SourceAuthority.CANONICAL_SOURCE
    )
    view = ViewDefinition(
        "PLAN-01", ViewType.ARCHITECTURAL_PLAN, ViewFamily.GEOMETRIC, "P-POC-S1",
        projection=ProjectionKind.ORTHOGRAPHIC, cut_plane="z_mm=1000",
        semantic_scope=("P-POC-S1",), representation_purpose="ARCHITECTURAL_PLAN",
    )
    profile = RepresentationProfile("PLAN-PROFILE", ProfileKind.CONCEPTUAL, ViewFamily.GEOMETRIC)
    style = GraphicStyle("NEUTRAL-STYLE")
    annotation = AnnotationProfile("NO-DIMENSIONS")
    return source, view, profile, style, annotation


def test_real_d2_poc_projects_walls_space_and_door_to_graphic_scene():
    elements = poc_elements()
    source, view, profile, style, annotation = contracts(elements)
    scene = project_architectural_plan(elements, source, view, profile, style, annotation)
    assert len(scene.entities) == 6
    assert {entity.trace.source_entity_refs[0] for entity in scene.entities} == {item.element_id.value for item in elements}
    assert {entity.role for entity in scene.entities} == {"WALL_CUT", "SPACE_BOUNDARY", "DOOR_EVIDENCE"}
    door = next(entity for entity in scene.entities if entity.role == "DOOR_EVIDENCE")
    assert "swing" not in door.geometry_intent
    assert "arc" not in door.geometry_intent
    assert door.trace.operation == "ARE-003:ARCHITECTURAL_PLAN:CUT_PROJECTION"


def test_projection_is_deterministic_in_entities_order_ids_and_fingerprint():
    elements = poc_elements()
    source, view, profile, style, annotation = contracts(elements)
    first = project_architectural_plan(elements, source, view, profile, style, annotation)
    second = project_architectural_plan(tuple(reversed(elements)), source, view, profile, style, annotation)
    assert first.canonical_dict() == second.canonical_dict()
    assert first.scene_fingerprint == second.scene_fingerprint
    assert [item.entity_id for item in first.entities] == [item.entity_id for item in second.entities]


def test_architectural_geometry_change_changes_only_relevant_graphic_result():
    elements = poc_elements()
    source, view, profile, style, annotation = contracts(elements)
    first = project_architectural_plan(elements, source, view, profile, style, annotation)
    moved = replace(elements[0], geometry=replace(elements[0].geometry, x_mm=300))
    changed_elements = (moved, *elements[1:])
    changed_source = replace(source, source_fingerprint=canonical_d2_fingerprint(changed_elements))
    second = project_architectural_plan(changed_elements, changed_source, view, profile, style, annotation)
    first_by_source = {e.trace.source_entity_refs[0]: e for e in first.entities}
    second_by_source = {e.trace.source_entity_refs[0]: e for e in second.entities}
    assert second.scene_fingerprint != first.scene_fingerprint
    assert second_by_source[moved.element_id.value].geometry_intent != first_by_source[moved.element_id.value].geometry_intent
    assert second_by_source[elements[1].element_id.value].geometry_intent == first_by_source[elements[1].element_id.value].geometry_intent


def test_cut_plane_classifies_geometry_above_without_inventing_visibility():
    elements = poc_elements()
    above = replace(elements[0], geometry=replace(elements[0].geometry, z_mm=2000))
    elements = (above, *elements[1:])
    source, view, profile, style, annotation = contracts(elements)
    scene = project_architectural_plan(elements, source, view, profile, style, annotation)
    above_entity = next(entity for entity in scene.entities if entity.trace.source_entity_refs == (above.element_id.value,))
    assert above_entity.geometry_intent["visibility"] == "ABOVE_BEYOND"


def test_unsupported_view_and_projection_fail_closed():
    elements = poc_elements()
    source, view, profile, style, annotation = contracts(elements)
    with pytest.raises(ProjectionError, match="UNSUPPORTED_PROJECTION"):
        project_architectural_plan(elements, source, replace(view, projection=ProjectionKind.PERSPECTIVE), profile, style, annotation)
    with pytest.raises(ProjectionError, match="UNSUPPORTED_VIEW"):
        project_architectural_plan(elements, source, replace(view, view_type=ViewType.SECTION, cut_plane="z_mm=1000"), profile, style, annotation)


def test_source_fingerprint_mismatch_and_empty_d2_block():
    elements = poc_elements()
    source, view, profile, style, annotation = contracts(elements)
    with pytest.raises(ProjectionError, match="SOURCE_FINGERPRINT_MISMATCH"):
        project_architectural_plan(elements, replace(source, source_fingerprint=HASH), view, profile, style, annotation)
    with pytest.raises(ProjectionError, match="EMPTY_D2_SOURCE"):
        project_architectural_plan((), source, view, profile, style, annotation)


def test_door_hosting_does_not_create_swing_arc():
    elements = poc_elements()
    source, view, profile, style, annotation = contracts(elements)
    scene = project_architectural_plan(elements, source, view, profile, style, annotation)
    door = next(entity for entity in scene.entities if entity.trace.source_entity_refs[0] == elements[-1].element_id.value)
    assert door.role == "DOOR_EVIDENCE"
    assert door.geometry_intent["kind"] == "rectangle"
    assert "opening_direction" not in door.geometry_intent


def test_projection_is_read_only_and_renderer_neutral():
    elements = poc_elements()
    before = tuple(item.semantic_dict() for item in elements)
    source, view, profile, style, annotation = contracts(elements)
    scene = project_architectural_plan(elements, source, view, profile, style, annotation)
    assert tuple(item.semantic_dict() for item in elements) == before
    assert not hasattr(scene, "svg")
    assert not hasattr(scene, "sheet")
    assert not hasattr(scene, "viewport")
