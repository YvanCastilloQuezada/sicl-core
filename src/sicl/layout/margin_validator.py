from __future__ import annotations

from .sheet_grid import SheetGrid
from .sheet_zone import LayoutElement, SheetZone


def validate_margins(elements: list[LayoutElement], grid: SheetGrid) -> list[str]:
    x1, y1, x2, y2 = grid.content_bbox
    violations: list[str] = []
    for element in elements:
        ex1, ey1, ex2, ey2 = element.bbox
        if ex1 < x1 or ey1 < y1 or ex2 > x2 or ey2 > y2:
            violations.append(element.element_id)
    return violations


def validate_truncations(elements: list[LayoutElement], zones: list[SheetZone], grid: SheetGrid) -> list[str]:
    truncations: list[str] = []
    zone_by_type = {zone.zone_type: zone for zone in zones}
    for element in elements:
        if not (0 <= element.bbox[0] <= element.bbox[2] <= grid.sheet_format.width_mm and 0 <= element.bbox[1] <= element.bbox[3] <= grid.sheet_format.height_mm):
            truncations.append(element.element_id)
            continue
        expected_zone = {"title": "title", "cajetin": "cajetin", "scale_bar": "scale"}.get(element.element_type)
        if expected_zone and expected_zone in zone_by_type and not zone_by_type[expected_zone].contains(element.bbox):
            truncations.append(element.element_id)
    return truncations


def missing_required_zones(zones: list[SheetZone]) -> list[str]:
    present = {zone.zone_type for zone in zones}
    return [zone_type for zone_type in ("title", "cajetin", "drawing") if zone_type not in present]
