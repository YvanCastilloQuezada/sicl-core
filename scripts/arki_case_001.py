"""ARKI-CASE-001 controlled-house E2E evidence runner.

This module is a case fixture and evidence producer. It does not modify any
canonical engine and deliberately emits only the current vector capabilities.
"""
from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
from typing import Iterable

from sicl.archi import ArchiElement, ArchiElementId, ArchiGeometry, ElementKind, GeometryKind, ProfileSpec
from sicl.drawing import Scale, graphic_scene_to_svg
from sicl.projection import canonical_d2_fingerprint, project_architectural_plan
from sicl.representation import (
    AnnotationProfile,
    GraphicStyle,
    ProfileKind,
    ProjectionKind,
    RepresentationProfile,
    SourceAuthority,
    SourceSnapshot,
    ViewDefinition,
    ViewFamily,
    ViewType,
)

PROJECT = "ARKI-CASE-001"
SITE_KEY = "S1"
WIDTH_MM = 10_000
DEPTH_MM = 9_000
MARGIN_MM = 10.0
SCALE = Scale.S_1_50


def _id(kind: ElementKind, key: str) -> ArchiElementId:
    return ArchiElementId.compute(PROJECT, kind.value, key)


def _rect(kind: ElementKind, key: str, x: int, y: int, width: int, depth: int, *, height: int = 2800, properties=None, contained_in=None, hosted_in=None) -> ArchiElement:
    return ArchiElement(
        _id(kind, key), PROJECT, kind,
        ArchiGeometry(GeometryKind.EXTRUDED_RECTANGLE, ProfileSpec(width, depth), x_mm=x, y_mm=y, height_mm=height),
        properties=properties or {},
        contained_in=contained_in,
        contained_in_version=1 if contained_in else None,
        hosted_in=hosted_in,
        hosted_in_version=1 if hosted_in else None,
    )


def build_case_model() -> tuple[ArchiElement, ...]:
    site = _rect(ElementKind.SITE, SITE_KEY, 0, 0, WIDTH_MM, DEPTH_MM, height=100)
    site_id = site.element_id
    walls = [
        _rect(ElementKind.WALL, "W01", 0, 0, 10_000, 200),
        _rect(ElementKind.WALL, "W02", 0, 8_800, 10_000, 200),
        _rect(ElementKind.WALL, "W03", 0, 200, 200, 8_600),
        _rect(ElementKind.WALL, "W04", 9_800, 200, 200, 8_600),
        _rect(ElementKind.WALL, "W05", 4_000, 200, 200, 3_000),
        _rect(ElementKind.WALL, "W06", 7_000, 200, 200, 3_000),
        _rect(ElementKind.WALL, "W07", 0, 3_600, 4_000, 200),
        _rect(ElementKind.WALL, "W08", 4_200, 3_600, 2_800, 200),
        _rect(ElementKind.WALL, "W09", 7_200, 3_600, 2_600, 200),
        _rect(ElementKind.WALL, "W10", 4_000, 3_800, 200, 5_000),
        _rect(ElementKind.WALL, "W11", 7_000, 3_800, 200, 5_000),
        _rect(ElementKind.WALL, "W12", 2_000, 6_200, 2_000, 200),
    ]
    spaces = [
        _rect(ElementKind.SPACE, "S01", 200, 200, 3_600, 3_200, contained_in=site_id),
        _rect(ElementKind.SPACE, "S02", 4_200, 200, 2_600, 3_200, contained_in=site_id),
        _rect(ElementKind.SPACE, "S03", 7_200, 200, 2_600, 3_200, contained_in=site_id),
        _rect(ElementKind.SPACE, "S04", 200, 3_800, 3_600, 4_800, contained_in=site_id),
        _rect(ElementKind.SPACE, "S05", 4_200, 3_800, 2_600, 2_200, contained_in=site_id),
        _rect(ElementKind.SPACE, "S06", 7_200, 3_800, 2_600, 4_800, contained_in=site_id),
    ]
    doors = [
        _rect(ElementKind.DOOR, "D01", 1_000, 0, 900, 200, properties={"source_key": "D01"}, hosted_in=walls[0].element_id),
        _rect(ElementKind.DOOR, "D02", 4_000, 1_200, 200, 900, properties={"source_key": "D02"}, hosted_in=walls[4].element_id),
        _rect(ElementKind.DOOR, "D03", 7_000, 1_600, 200, 900, properties={"source_key": "D03"}, hosted_in=walls[5].element_id),
        _rect(ElementKind.DOOR, "D04", 4_800, 3_600, 900, 200, properties={"source_key": "D04"}, hosted_in=walls[7].element_id),
        _rect(ElementKind.DOOR, "D05", 7_800, 3_600, 900, 200, properties={"source_key": "D05"}, hosted_in=walls[8].element_id),
    ]
    windows = [
        _rect(ElementKind.WINDOW, "V01", 2_600, 0, 1_000, 200, properties={"source_key": "V01"}, hosted_in=walls[0].element_id),
        _rect(ElementKind.WINDOW, "V02", 5_400, 8_800, 1_000, 200, properties={"source_key": "V02"}, hosted_in=walls[1].element_id),
        _rect(ElementKind.WINDOW, "V03", 0, 4_600, 200, 1_000, properties={"source_key": "V03"}, hosted_in=walls[2].element_id),
        _rect(ElementKind.WINDOW, "V04", 9_800, 6_200, 200, 1_000, properties={"source_key": "V04"}, hosted_in=walls[3].element_id),
    ]
    return (site, *walls, *spaces, *doors, *windows)


def _contracts(elements: Iterable[ArchiElement]):
    source = SourceSnapshot(PROJECT, "D2", "1", canonical_d2_fingerprint(tuple(elements)), SourceAuthority.CANONICAL_SOURCE)
    view = ViewDefinition(
        "CASE-001-PLAN", ViewType.ARCHITECTURAL_PLAN, ViewFamily.GEOMETRIC, PROJECT,
        projection=ProjectionKind.ORTHOGRAPHIC, view_direction="TOP", cut_plane="z_mm=1000",
        semantic_scope=(PROJECT,), representation_purpose="ARCHITECTURAL_PLAN",
    )
    profile = RepresentationProfile("CASE-001-PROFILE", ProfileKind.CONCEPTUAL, ViewFamily.GEOMETRIC)
    roles = ("WALL_CUT", "WALL_PROJECTED", "SPACE_BOUNDARY", "DOOR_EVIDENCE", "WINDOW_EVIDENCE")
    style = GraphicStyle("CASE-001-STYLE", line_weights={role: "MEDIUM" for role in roles})
    annotation = AnnotationProfile("CASE-001-NO-ANNOTATIONS")
    return source, view, profile, style, annotation


def project_case(elements: tuple[ArchiElement, ...]):
    projectable = tuple(element for element in elements if element.kind is not ElementKind.SITE)
    source, view, profile, style, annotation = _contracts(projectable)
    scene = project_architectural_plan(projectable, source, view, profile, style, annotation)
    adapted, svg = graphic_scene_to_svg(scene, scale=SCALE, margin_mm=MARGIN_MM)
    return projectable, source, scene, adapted, svg


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _svg_inventory(svg: str) -> dict[str, object]:
    import xml.etree.ElementTree as ET
    root = ET.fromstring(svg)
    ns = {"s": "http://www.w3.org/2000/svg"}
    primitives = []
    for element in root.iter():
        if "data-primitive-id" in element.attrib:
            primitives.append({key: element.attrib[key] for key in ("data-primitive-id", "data-source-ref", "data-semantic-role")})
    return {"parseable": True, "raster_images": len(root.findall(".//s:image", ns)), "primitives": primitives}


def _fabrication_audit(*svgs: str) -> dict[str, object]:
    forbidden = (
        "DOOR_SWING", "ROOM_LABEL", "AREA_LABEL", "DIMENSION", "MATERIAL_HATCH",
        "FURNITURE", "SANITARY_FIXTURE", "NORTH_ARROW", "AXIS", "SECTION_MARK",
        "ELEVATION_MARK",
    )
    found = sorted({marker for svg in svgs for marker in forbidden if marker in svg.upper()})
    return {"fabricated_items": len(found), "forbidden_markers_found": found}


def run_case(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    model = build_case_model()
    projectable, source, scene, adapted, base_svg = project_case(model)
    base_path = output_dir / "ARKI_CASE_001_BASE.svg"
    base_path.write_text(base_svg, encoding="utf-8")
    repeat_svg = project_case(model)[4]
    mutated_model = tuple(replace(item, geometry=replace(item.geometry, x_mm=item.geometry.x_mm + 600), version=item.version + 1) if item.element_id == _id(ElementKind.WALL, "W07") else item for item in model)
    mutated_projectable, mutated_source, mutated_scene, mutated_adapted, mutated_svg = project_case(mutated_model)
    mutated_path = output_dir / "ARKI_CASE_001_MUTATED.svg"
    mutated_path.write_text(mutated_svg, encoding="utf-8")
    base_by_source = {entity.trace.source_entity_refs[0]: entity for entity in scene.entities}
    mutated_by_source = {entity.trace.source_entity_refs[0]: entity for entity in mutated_scene.entities}
    target_d2 = _id(ElementKind.WALL, "W07").value
    traceability = []
    for entity in scene.entities:
        primitive_id = next(pid for pid, source_ref in adapted.primitive_sources.items() if source_ref == entity.entity_id)
        traceability.append({
            "d2_element_id": entity.trace.source_entity_refs[0],
            "d2_version": next(item.version for item in projectable if item.element_id.value == entity.trace.source_entity_refs[0]),
            "graphic_entity_id": entity.entity_id,
            "graphic_trace": entity.trace.__dict__,
            "primitive_id": primitive_id,
            "svg_data_source_ref": entity.entity_id,
            "svg_data_semantic_role": entity.role,
        })
    inventory = {kind.value: sum(item.kind is kind for item in model) for kind in ElementKind}
    represented_ids = set(base_by_source)
    not_visible = [item.element_id.value for item in model if item.kind is ElementKind.SITE]
    evidence = {
        "baseline_commit": "71e72bb1abfb217bf4854f464ae443764281f469",
        "case_id": "ARKI-CASE-001",
        "scale": "1:50",
        "margin_mm": MARGIN_MM,
        "d2_element_inventory": inventory,
        "d2_elements_in_projection": len(projectable),
        "graphic_scene_entity_inventory": {"count": len(scene.entities), "represented_source_ids": sorted(represented_ids), "not_visible_or_not_applicable": not_visible},
        "svg_primitive_inventory": _svg_inventory(base_svg),
        "base_svg_sha256": _sha(base_path),
        "mutated_svg_sha256": _sha(mutated_path),
        "svg_determinism": hashlib.sha256(base_svg.encode()).hexdigest() == hashlib.sha256(repeat_svg.encode()).hexdigest(),
        "mutation": {"target": target_d2, "delta_x_mm": 600, "base_entity_id": base_by_source[target_d2].entity_id, "mutated_entity_id": mutated_by_source[target_d2].entity_id},
        "unaffected_entities": [base_by_source[item].entity_id for item in sorted(represented_ids - {target_d2})[:2]],
        "fabrication_audit": _fabrication_audit(base_svg, mutated_svg),
        "unsupported_capabilities": ["SITE projection is NOT_APPLICABLE in ARE-003", "non-rectangular geometry not used"],
        "deferred_capabilities": ["dimensions", "room labels", "door swings", "window/door symbols", "material hatches", "sheet composition", "professional annotations"],
        "traceability": traceability,
    }
    (output_dir / "ARKI_CASE_001_EVIDENCE.json").write_text(json.dumps(evidence, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    (output_dir / "ARKI_CASE_001_TRACEABILITY.json").write_text(json.dumps(traceability, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    return evidence


if __name__ == "__main__":
    run_case(Path("artifacts/arki-case-001"))
