from __future__ import annotations

from .layout_report import LayoutCollision
from .sheet_zone import LayoutElement


def intersection_area(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def detect_collisions(elements: list[LayoutElement]) -> list[LayoutCollision]:
    collisions: list[LayoutCollision] = []
    for index, element_a in enumerate(elements):
        for element_b in elements[index + 1 :]:
            if element_a.allowed_overlap or element_b.allowed_overlap:
                continue
            overlap = intersection_area(element_a.bbox, element_b.bbox)
            if overlap > 1e-6:
                collisions.append(LayoutCollision(element_a.element_id, element_b.element_id, round(overlap, 6)))
    return collisions
