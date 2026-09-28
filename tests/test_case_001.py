import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from scripts.arki_case_001 import build_case_model, project_case, run_case
from sicl.drawing import DrawingAdapterError, graphic_scene_to_svg
from sicl.representation import GraphicTrace
from dataclasses import replace


def _bounds(svg):
    root = ET.fromstring(svg)
    ns = {"s": "http://www.w3.org/2000/svg"}
    points = []
    for polygon in root.findall(".//s:polygon", ns):
        points.extend(tuple(float(value) for value in pair.split(",")) for pair in polygon.attrib["points"].split())
    for circle in root.findall('.//s:circle[@data-primitive-id]', ns):
        cx, cy, radius = (float(circle.attrib[key]) for key in ("cx", "cy", "r"))
        points.extend(((cx - radius, cy - radius), (cx + radius, cy + radius)))
    return min(x for x, _ in points), min(y for _, y in points), max(x for x, _ in points), max(y for _, y in points)


def test_case_001_model_inventory_and_real_projection():
    model = build_case_model()
    counts = {kind.value: sum(item.kind is kind for item in model) for kind in type(model[0].kind)}
    assert counts["SITE"] == 1
    assert counts["SPACE"] == 6
    assert counts["WALL"] == 12
    assert counts["DOOR"] == 5
    assert counts["WINDOW"] == 4
    projectable, source, scene, adapted, svg = project_case(model)
    assert len(projectable) == 27
    assert len(scene.entities) == 27
    assert len(adapted.viewport.elements) == 27
    assert "<image" not in svg


def test_case_001_svg_is_parseable_vector_deterministic_and_geometrically_scaled(tmp_path):
    evidence = run_case(tmp_path)
    base = (tmp_path / "ARKI_CASE_001_BASE.svg").read_text()
    repeat = project_case(build_case_model())[4]
    assert ET.fromstring(base).tag.endswith("svg")
    assert hashlib.sha256(base.encode()).hexdigest() == hashlib.sha256(repeat.encode()).hexdigest()
    root = ET.fromstring(base)
    width = float(root.attrib["width"].removesuffix("mm"))
    height = float(root.attrib["height"].removesuffix("mm"))
    xmin, ymin, xmax, ymax = _bounds(base)
    assert xmax - xmin == pytest.approx(200.0, abs=0.001)
    assert xmin == pytest.approx(10.0, abs=0.001)
    assert xmax == pytest.approx(width - 10.0, abs=0.001)
    assert ymin == pytest.approx(10.0, abs=0.001)
    assert ymax == pytest.approx(height - 10.0, abs=0.001)
    assert evidence["fabrication_audit"]["fabricated_items"] == 0
    assert evidence["svg_primitive_inventory"]["raster_images"] == 0


def test_case_001_controlled_wall_mutation_reaches_svg_and_preserves_unaffected_identity(tmp_path):
    evidence = run_case(tmp_path)
    assert evidence["base_svg_sha256"] != evidence["mutated_svg_sha256"]
    assert evidence["mutation"]["delta_x_mm"] == 600
    assert len(evidence["unaffected_entities"]) == 2
    base = (tmp_path / "ARKI_CASE_001_BASE.svg").read_text()
    mutated = (tmp_path / "ARKI_CASE_001_MUTATED.svg").read_text()
    assert evidence["mutation"]["target"] in str(evidence["traceability"])
    assert base != mutated


def test_case_001_traceability_contains_wall_space_and_opening_evidence(tmp_path):
    run_case(tmp_path)
    trace = json.loads((tmp_path / "ARKI_CASE_001_TRACEABILITY.json").read_text())
    roles = {item["svg_data_semantic_role"] for item in trace}
    assert {"WALL_CUT", "SPACE_BOUNDARY", "DOOR_EVIDENCE", "WINDOW_EVIDENCE"} <= roles
    for item in trace:
        assert item["d2_element_id"]
        assert item["graphic_entity_id"]
        assert item["primitive_id"]
        assert item["svg_data_source_ref"] == item["graphic_entity_id"]


def test_case_001_adversarial_role_and_operation_contradictions_block():
    model = build_case_model()
    _, _, scene, _, _ = project_case(model)
    entity = scene.entities[0]
    role_bad = replace(entity, trace=replace(entity.trace, semantic_role="DOOR_EVIDENCE"))
    with pytest.raises(DrawingAdapterError, match="GRAPHIC_TRACE_ROLE_MISMATCH"):
        graphic_scene_to_svg(replace(scene, entities=(role_bad, *scene.entities[1:])))
    operation_bad = replace(entity, trace=replace(entity.trace, operation="ARE-003:ARCHITECTURAL_PLAN:BELOW_CUT_PROJECTION"))
    with pytest.raises(DrawingAdapterError, match="GRAPHIC_TRACE_OPERATION_MISMATCH"):
        graphic_scene_to_svg(replace(scene, entities=(operation_bad, *scene.entities[1:])))
