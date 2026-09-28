"""ISO 216 paper sizes and orientation, in millimetres."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class PaperSize(str, Enum):
    A4 = "A4"; A3 = "A3"; A2 = "A2"; A1 = "A1"; A0 = "A0"
    @property
    def dimensions_mm(self) -> tuple[float, float]:
        return {PaperSize.A4: (210.0, 297.0), PaperSize.A3: (297.0, 420.0), PaperSize.A2: (420.0, 594.0), PaperSize.A1: (594.0, 841.0), PaperSize.A0: (841.0, 1189.0)}[self]

class Orientation(str, Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"

@dataclass(frozen=True)
class PaperSpec:
    size: PaperSize
    orientation: Orientation = Orientation.LANDSCAPE
    def width_mm(self) -> float:
        short, long = self.size.dimensions_mm
        return long if self.orientation is Orientation.LANDSCAPE else short
    def height_mm(self) -> float:
        short, long = self.size.dimensions_mm
        return short if self.orientation is Orientation.LANDSCAPE else long

@dataclass(frozen=True)
class Margins:
    left_mm: float = 25.0
    top_mm: float = 10.0
    right_mm: float = 10.0
    bottom_mm: float = 10.0

DEFAULT_MARGINS = Margins()
