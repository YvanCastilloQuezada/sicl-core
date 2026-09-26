from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .collision import detect_collisions
from .layout_report import LayoutValidationResult
from .margin_validator import missing_required_zones, validate_margins, validate_truncations
from .sheet_format import SheetFormat, get_format
from .sheet_grid import SheetGrid
from .sheet_zone import LayoutElement, SheetZone

DEFAULT_MARGINS = {"top": 20.0, "bottom": 20.0, "left": 25.0, "right": 25.0}


@dataclass
class SheetLayout:
    layout_id: str
    format: SheetFormat
    margins: dict[str, float] = field(default_factory=lambda: DEFAULT_MARGINS.copy())
    zones: list[SheetZone] = field(default_factory=list)
    elements: list[LayoutElement] = field(default_factory=list)
    validation_result: LayoutValidationResult | None = None

    def grid(self) -> SheetGrid:
        return SheetGrid(self.format, self.margins)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["format"] = asdict(self.format)
        value["zones"] = [asdict(zone) for zone in self.zones]
        value["elements"] = [asdict(element) for element in self.elements]
        value["validation_result"] = self.validation_result.to_dict() if self.validation_result else None
        return value


def create_layout(layout_id: str, format_name: str = "A3", orientation: str = "H", margins: dict[str, float] | None = None) -> SheetLayout:
    selected_margins = {**DEFAULT_MARGINS, **(margins or {})}
    if any(value < 0 for value in selected_margins.values()):
        raise ValueError("margins cannot be negative")
    return SheetLayout(layout_id, get_format(format_name, orientation), selected_margins)


def declare_zones(layout: SheetLayout, zones: list[SheetZone]) -> SheetLayout:
    layout.zones = list(zones)
    return layout


def calculate_layout(layout: SheetLayout, elements: list[LayoutElement]) -> SheetLayout:
    # This method only stores/calculates geometry. It never renders, writes PDFs, or mutates BIM data.
    layout.elements = list(elements)
    layout.validation_result = None
    return layout


def validate_layout(layout: SheetLayout) -> LayoutValidationResult:
    collisions = detect_collisions(layout.elements)
    margin_violations = validate_margins(layout.elements, layout.grid())
    truncations = validate_truncations(layout.elements, layout.zones, layout.grid())
    missing_zones = missing_required_zones(layout.zones)
    types = {element.element_type for element in layout.elements}
    result = LayoutValidationResult(
        status="VALID" if not (collisions or margin_violations or truncations or missing_zones or "title" not in types) else "INVALID",
        collisions=collisions,
        margin_violations=margin_violations,
        truncations=truncations,
        missing_zones=missing_zones,
        title_present="title" in types,
        north_present="north" in types,
        scale_present="scale_bar" in types,
        cajetin_present="cajetin" in types,
    )
    layout.validation_result = result
    return result


def export_layout_json(layout: SheetLayout) -> dict[str, Any]:
    return layout.to_dict()
