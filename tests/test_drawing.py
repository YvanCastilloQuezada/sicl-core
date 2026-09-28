from __future__ import annotations
import pytest
from sicl.drawing import (Arc, Circle, Dimension, DimensionKind, Hatch, HatchPattern, Line, LineWeight, Orientation, PaperSize, Point, Polyline, Rect, Scale, Sheet, Specialty, Text, TextAnchor, TitleBlock, TitleBlockField, Viewport, export_sheet_svg, export_view_svg)

def make_title_block() -> TitleBlock:
    return TitleBlock("VIVIENDA UNIFAMILIAR", "LIMA, PERU", "PROPIETARIO DE PRUEBA", Specialty.ARCHITECTURE, "ARQUITECTO DE PRUEBA", "CAP-00000", "A-01", "A", "2026-09-27")

def test_scale_conversion_is_deterministic():
    s = Scale.S_1_50
    assert s.denominator == 50
    assert s.real_mm_to_paper_mm(1000.0) == 20.0
    assert s.paper_mm_to_real_mm(20.0) == 1000.0

def test_polyline_requires_at_least_two_points():
    with pytest.raises(ValueError): Polyline((Point(0, 0),))

def test_rect_corners_and_polyline():
    r = Rect(Point(0, 0), 100, 50)
    assert r.corners() == (Point(0, 0), Point(100, 0), Point(100, 50), Point(0, 50))
    assert r.to_polyline().closed is True

def test_text_requires_content():
    with pytest.raises(ValueError): Text(Point(0, 0), "")

def test_hatch_rejects_empty_pattern():
    with pytest.raises(ValueError): Hatch((Point(0, 0), Point(1, 0), Point(1, 1)), HatchPattern.NONE)

def test_dimension_requires_two_extension_points():
    with pytest.raises(ValueError): Dimension(DimensionKind.LINEAR_CHAIN, (Point(0, 0),), "1.00")

def test_title_block_rejects_missing_required_fields():
    with pytest.raises(ValueError): TitleBlock("", "LIMA", "OWNER", Specialty.ARCHITECTURE, "ARQ", "CAP", "A-01")

def test_title_block_accepts_valid_iso_date():
    assert any(f.key == "FECHA" and f.value == "2026-09-27" for f in make_title_block().to_fields())

def test_title_block_rejects_bad_iso_date():
    with pytest.raises(ValueError): TitleBlock("P", "L", "O", Specialty.ARCHITECTURE, "A", "CAP", "A-01", date_iso="27-09-2026")

def test_viewport_requires_name():
    with pytest.raises(ValueError): Viewport("", Scale.S_1_50, (0, 0))

def test_sheet_a3_landscape_dimensions():
    sheet = Sheet.for_vivienda_a3(make_title_block())
    assert sheet.paper.width_mm() == 420.0
    assert sheet.paper.height_mm() == 297.0
    assert sheet.inner_width_mm() == 385.0
    assert sheet.inner_height_mm() == 277.0

def test_export_view_svg_is_deterministic():
    vp = Viewport("TEST", Scale.S_1_50, (0, 0), (Line(Point(0, 0), Point(1000, 0), LineWeight.CUT), Text(Point(500, 200), "SALA", 3.0, TextAnchor.MIDDLE)))
    svg1, svg2 = export_view_svg(vp, 200.0, 100.0), export_view_svg(vp, 200.0, 100.0)
    assert svg1 == svg2 and "<line" in svg1 and "SALA" in svg1

def test_export_sheet_svg_contains_title_block_and_viewport():
    base = Sheet.for_vivienda_a3(make_title_block())
    sheet = Sheet(base.paper, base.title_block, (Viewport("PLANTA BAJA", Scale.S_1_50, (30.0, 250.0), (Rect(Point(0, 0), 5000, 4000, LineWeight.CUT),), (150.0, 20.0)),))
    svg = export_sheet_svg(sheet)
    assert "VIVIENDA UNIFAMILIAR" in svg and "CAP-00000" in svg and "PLANTA BAJA (1:50)" in svg and "<svg" in svg

def test_export_sheet_svg_escapes_user_text():
    tb = TitleBlock("A & B <C>", "LIMA", "OWNER", Specialty.ARCHITECTURE, "ARQ", "CAP-1", "A-01")
    svg = export_sheet_svg(Sheet.for_vivienda_a3(tb))
    assert "A &amp; B &lt;C&gt;" in svg and "A & B <C>" not in svg

def test_legacy_title_block_fields_remain_available():
    from sicl.drawing.title_block import REQUIRED_FIELDS, peru_title_block
    block = peru_title_block("P", "A-01", "Plan")
    assert len(REQUIRED_FIELDS) == 8 and len(block) >= 8

def test_arc_and_circle_serialize_as_vector_geometry():
    vp = Viewport("GEOMETRY", Scale.S_1_50, (0, 100), (Arc(Point(100, 100), 50, 0, 90, primitive_id="A-1", semantic_role="door-swing"), Circle(Point(300, 100), 25, primitive_id="C-1", semantic_role="column")))
    svg = export_view_svg(vp, 200.0, 100.0)
    assert '<path ' in svg and ' A ' in svg and '<circle ' in svg
    assert 'data-primitive-id="A-1"' in svg and 'data-primitive-id="C-1"' in svg


def test_dimension_has_dimension_line_arrows_kind_and_text():
    vp = Viewport("DIM", Scale.S_1_50, (0, 100), (Dimension(DimensionKind.LINEAR_BETWEEN_AXES, (Point(0, 0), Point(1000, 0)), "1000", Point(500, 100), primitive_id="DIM-1", semantic_role="overall-dimension"),))
    svg = export_view_svg(vp, 200.0, 100.0)
    assert 'marker-start="url(#dim-arrow)"' in svg and 'marker-end="url(#dim-arrow)"' in svg
    assert 'data-dimension-kind="linear_axes"' in svg and '1000' in svg


def test_svg_preserves_layers_and_semantic_metadata():
    vp = Viewport("META", Scale.S_1_50, (0, 100), (Line(Point(0, 0), Point(100, 0), layer="WALLS", primitive_id="W-1", semantic_role="wall", source_ref="archi:W-1"), Text(Point(10, 10), "SALA", layer="ANNOTATIONS", primitive_id="T-1", semantic_role="room-label")))
    svg = export_view_svg(vp, 200.0, 100.0)
    assert 'id="layer-WALLS"' in svg and 'id="layer-ANNOTATIONS"' in svg
    assert 'data-source-ref="archi:W-1"' in svg and 'data-semantic-role="wall"' in svg


def test_viewport_title_block_collision_fails_closed():
    tb = make_title_block()
    base = Sheet.for_vivienda_a3(tb)
    colliding = Viewport("COLLISION", Scale.S_1_50, (250, 260), (Rect(Point(0, 0), 3000, 3000),))
    with pytest.raises(ValueError, match="viewport/title-block collision"):
        export_sheet_svg(Sheet(base.paper, base.title_block, (colliding,)))


def test_invalid_geometry_fails_closed():
    with pytest.raises(ValueError): Circle(Point(0, 0), 0)
    with pytest.raises(ValueError): Arc(Point(0, 0), -1, 0, 90)
    with pytest.raises(ValueError): Rect(Point(0, 0), 0, 10)


def test_runtime_complete_vector_output_parses_and_is_deterministic():
    import hashlib
    import xml.etree.ElementTree as ET
    tb = make_title_block()
    base = Sheet.for_vivienda_a3(tb)
    elements = (Rect(Point(0, 0), 3000, 2000, LineWeight.CUT, "WALLS", "W-1", "wall", "archi:W-1"), Hatch((Point(0, 0), Point(3000, 0), Point(3000, 2000), Point(0, 2000)), HatchPattern.CONCRETE, "HATCH", "H-1", "wall-material", "archi:W-1"), Arc(Point(500, 500), 300, 0, 90, primitive_id="A-1", semantic_role="opening-swing"), Circle(Point(2500, 1500), 150, primitive_id="C-1", semantic_role="column"), Dimension(DimensionKind.LINEAR_CHAIN, (Point(0, 0), Point(3000, 0)), "3000", Point(1500, 3000), primitive_id="D-1", semantic_role="dimension"))
    vp = Viewport("VECTOR FOUNDATION", Scale.S_1_50, (30, 250), elements, (100, 20))
    sheet = Sheet(base.paper, base.title_block, (vp,))
    svg1, svg2 = export_sheet_svg(sheet), export_sheet_svg(sheet)
    ET.fromstring(svg1)
    assert svg1 == svg2 and hashlib.sha256(svg1.encode()).hexdigest() == hashlib.sha256(svg2.encode()).hexdigest()
    assert all(token in svg1 for token in ("<path", "<circle", "marker-start", "data-layer=\"WALLS\"", "data-primitive-id=\"W-1\"", "url(#concrete)"))
