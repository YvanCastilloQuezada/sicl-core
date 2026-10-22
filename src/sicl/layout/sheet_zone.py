from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

BBox = tuple[float, float, float, float]
ZoneType = Literal["title", "cajetin", "drawing", "norte", "scale", "notes"]


@dataclass(frozen=True)
class SheetZone:
    zone_type: ZoneType
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def bbox(self) -> BBox:
        return (self.x1, self.y1, self.x2, self.y2)

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1

    def contains(self, bbox: BBox, tolerance: float = 1e-6) -> bool:
        x1, y1, x2, y2 = bbox
        return x1 >= self.x1 - tolerance and y1 >= self.y1 - tolerance and x2 <= self.x2 + tolerance and y2 <= self.y2 + tolerance


@dataclass(frozen=True)
class LayoutElement:
    element_id: str
    element_type: str
    bbox: BBox
    allowed_overlap: bool = False
    metadata: dict[str, object] = field(default_factory=dict)
