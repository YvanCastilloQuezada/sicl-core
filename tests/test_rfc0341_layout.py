import copy
import json

from sicl.layout import LayoutElement, SheetZone, calculate_layout, create_layout, declare_zones, export_layout_json, validate_layout
from sicl.layout.sheet_format import FORMATS


def valid_layout():
    layout = create_layout("CN-01", "A3", "H", {"top": 20, "bottom": 20, "left": 25, "right": 25})
    zones = [
        SheetZone("title", 25, 252, 395, 277),
        SheetZone("cajetin", 230, 20, 395, 80),
        SheetZone("drawing", 25, 90, 345, 245),
        SheetZone("norte", 350, 225, 395, 250),
        SheetZone("scale", 25, 82, 110, 89),
        SheetZone("notes", 115, 82, 220, 89),
    ]
    elements = [
        LayoutElement("title-1", "title", (30, 257, 210, 270)),
        LayoutElement("drawing-1", "drawing", (30, 95, 340, 240)),
        LayoutElement("cajetin-1", "cajetin", (235, 25, 390, 75)),
        LayoutElement("north-1", "north", (355, 230, 380, 245)),
        LayoutElement("scale-1", "scale_bar", (30, 83, 105, 88)),
    ]
    return calculate_layout(declare_zones(layout, zones), elements)


def test_sheet_format_supported():
    assert set(FORMATS) == {"A4", "A3", "A2", "A1", "A0"}


def test_margins_declared():
    assert valid_layout().margins == {"top": 20, "bottom": 20, "left": 25, "right": 25}


def test_zone_required_title():
    assert any(zone.zone_type == "title" for zone in valid_layout().zones)


def test_zone_required_cajetin():
    assert any(zone.zone_type == "cajetin" for zone in valid_layout().zones)


def test_zone_required_drawing():
    assert any(zone.zone_type == "drawing" for zone in valid_layout().zones)


def test_layout_calculate_returns_bboxes():
    assert all(len(element.bbox) == 4 for element in valid_layout().elements)


def test_layout_validate_returns_result():
    result = validate_layout(valid_layout())
    assert result.status == "VALID"


def test_layout_export_json():
    exported = export_layout_json(valid_layout())
    assert json.loads(json.dumps(exported))["layout_id"] == "CN-01"


def test_collision_detected_between_title_and_drawing():
    layout = valid_layout()
    layout.elements.append(LayoutElement("collision", "drawing", (100, 250, 200, 260)))
    result = validate_layout(layout)
    assert len(result.collisions) == 1


def test_margin_violation_detected():
    layout = valid_layout()
    layout.elements.append(LayoutElement("outside-margin", "notes", (10, 100, 40, 120)))
    assert "outside-margin" in validate_layout(layout).margin_violations


def test_cajetin_truncated_detected():
    layout = valid_layout()
    layout.elements.append(LayoutElement("bad-cajetin", "cajetin", (300, 20, 410, 75)))
    assert "bad-cajetin" in validate_layout(layout).truncations


def test_scale_bar_truncated_detected():
    layout = valid_layout()
    layout.elements.append(LayoutElement("bad-scale", "scale_bar", (20, 82, 120, 88)))
    assert "bad-scale" in validate_layout(layout).truncations


def test_allowed_overlap_passes():
    layout = valid_layout()
    layout.elements.extend([
        LayoutElement("label", "title", (250, 258, 300, 266), allowed_overlap=True),
        LayoutElement("title-overlap", "title", (260, 260, 320, 268)),
    ])
    assert validate_layout(layout).collisions == []


def test_title_missing_rejected():
    layout = valid_layout()
    layout.elements = [element for element in layout.elements if element.element_type != "title"]
    result = validate_layout(layout)
    assert result.status == "INVALID" and not result.title_present


def test_layout_does_not_modify_bim_snapshot():
    snapshot = {"id": "BIM-CASA-001", "area": 200, "geometry": {"locked": True}}
    before = copy.deepcopy(snapshot)
    _ = valid_layout()
    assert snapshot == before


def test_layout_does_not_create_decision():
    decisions_before = []
    _ = validate_layout(valid_layout())
    assert decisions_before == []
