from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal


@dataclass(frozen=True)
class LayoutCollision:
    element_a: str
    element_b: str
    overlap_area: float


@dataclass(frozen=True)
class LayoutValidationResult:
    status: Literal["VALID", "INVALID"]
    collisions: list[LayoutCollision] = field(default_factory=list)
    margin_violations: list[str] = field(default_factory=list)
    truncations: list[str] = field(default_factory=list)
    missing_zones: list[str] = field(default_factory=list)
    title_present: bool = False
    north_present: bool = False
    scale_present: bool = False
    cajetin_present: bool = False

    @property
    def is_valid(self) -> bool:
        return self.status == "VALID"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def report_text(layout_id: str, result: LayoutValidationResult) -> str:
    return "\n".join(
        [
            f"LAYOUT REPORT: {layout_id}",
            f"STATUS: {result.status}",
            f"COLLISIONS: {len(result.collisions)}",
            f"MARGIN_VIOLATIONS: {len(result.margin_violations)}",
            f"TRUNCATIONS: {len(result.truncations)}",
            f"MISSING_ZONES: {', '.join(result.missing_zones) or 'NONE'}",
            f"TITLE: {'CONFIRMED' if result.title_present else 'MISSING'}",
            f"NORTH: {'CONFIRMED' if result.north_present else 'MISSING'}",
            f"SCALE: {'CONFIRMED' if result.scale_present else 'MISSING'}",
            f"CAJETIN: {'CONFIRMED' if result.cajetin_present else 'MISSING'}",
        ]
    )
