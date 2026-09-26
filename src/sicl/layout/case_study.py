from __future__ import annotations

from .layout_engine import SheetLayout, calculate_layout, create_layout, declare_zones, validate_layout
from .sheet_zone import LayoutElement, SheetZone

SHEETS = [
    ("CN-01", "Planta Baja · Nivel 01"),
    ("CN-02", "Planta Alta · Nivel 02"),
    ("CN-03", "Corte Longitudinal A–A"),
    ("CN-04", "Elevación Principal · Sur"),
    ("CN-05", "Lámina de Síntesis"),
]


def casa_nido_layout(sheet_id: str, title: str) -> SheetLayout:
    layout = create_layout(sheet_id, "A3", "H", {"top": 20, "bottom": 20, "left": 25, "right": 25})
    zones = [
        SheetZone("title", 25, 252, 395, 277),
        SheetZone("cajetin", 230, 20, 395, 80),
        SheetZone("drawing", 25, 90, 345, 245),
        SheetZone("norte", 350, 225, 395, 250),
        SheetZone("scale", 25, 82, 110, 89),
        SheetZone("notes", 115, 82, 220, 89),
    ]
    elements = [
        LayoutElement(f"{sheet_id}-title", "title", (30, 257, 210, 270), metadata={"text": title}),
        LayoutElement(f"{sheet_id}-drawing", "drawing", (30, 95, 340, 240)),
        LayoutElement(f"{sheet_id}-cajetin", "cajetin", (235, 25, 390, 75)),
        LayoutElement(f"{sheet_id}-north", "north", (355, 230, 380, 245)),
        LayoutElement(f"{sheet_id}-scale", "scale_bar", (30, 83, 105, 88)),
    ]
    return calculate_layout(declare_zones(layout, zones), elements)


def validate_casa_nido() -> dict[str, object]:
    sheets: list[dict[str, object]] = []
    for sheet_id, title in SHEETS:
        layout = casa_nido_layout(sheet_id, title)
        result = validate_layout(layout)
        sheets.append({
            "layout_id": sheet_id,
            "title": title,
            "format": layout.format.name,
            "orientation": layout.format.orientation,
            "margins": layout.margins,
            "zones": [zone.zone_type for zone in layout.zones],
            "elements": [element.element_id for element in layout.elements],
            "status": result.status,
            "collisions": len(result.collisions),
            "margin_violations": len(result.margin_violations),
            "truncations": len(result.truncations),
            "title_present": result.title_present,
            "north_present": result.north_present,
            "scale_present": result.scale_present,
            "cajetin_present": result.cajetin_present,
        })
    return {
        "project": "CASA NIDO DE CAMPO",
        "engine": "RFC-034.1 Sheet Composition & Layout Engine",
        "renders_pdf": False,
        "core_changed": False,
        "decision_created": False,
        "sheet_count": len(sheets),
        "valid_sheet_count": sum(sheet["status"] == "VALID" for sheet in sheets),
        "total_collisions": sum(int(sheet["collisions"]) for sheet in sheets),
        "total_margin_violations": sum(int(sheet["margin_violations"]) for sheet in sheets),
        "sheets": sheets,
    }
