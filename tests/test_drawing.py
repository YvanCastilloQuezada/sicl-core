from __future__ import annotations
import pytest
from sicl.drawing import (Dimension, DimensionKind, Hatch, HatchPattern, Line, LineWeight, Orientation, PaperSize, Point, Polyline, Rect, Scale, Sheet, Specialty, Text, TextAnchor, TitleBlock, TitleBlockField, Viewport, export_sheet_svg, export_view_svg)

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
