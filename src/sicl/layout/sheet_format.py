from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SheetFormat:
    name: str
    width_mm: float
    height_mm: float
    orientation: str = "H"

    def oriented(self, orientation: str) -> "SheetFormat":
        orientation = orientation.upper()
        if orientation not in {"H", "V"}:
            raise ValueError("orientation must be H or V")
        if orientation == self.orientation:
            return self
        return SheetFormat(self.name, self.height_mm, self.width_mm, orientation)


FORMATS: dict[str, SheetFormat] = {
    "A4": SheetFormat("A4", 297, 210),
    "A3": SheetFormat("A3", 420, 297),
    "A2": SheetFormat("A2", 594, 420),
    "A1": SheetFormat("A1", 841, 594),
    "A0": SheetFormat("A0", 1189, 841),
}


def get_format(name: str, orientation: str = "H") -> SheetFormat:
    try:
        return FORMATS[name.upper()].oriented(orientation)
    except KeyError as exc:
        raise ValueError(f"unsupported sheet format: {name}") from exc
