"""2D drawing primitives. Frozen, deterministic, SVG-friendly."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class LineWeight(str, Enum):
    CUT = "0.70"
    HEAVY = "0.50"
    MEDIUM = "0.35"
    THIN = "0.25"
    HAIR = "0.13"
    HIDDEN = "0.18"

class TextAnchor(str, Enum):
    START = "start"
    MIDDLE = "middle"
    END = "end"

class HatchPattern(str, Enum):
    NONE = "none"
    SOLID = "solid"
    EARTH = "earth"
    CONCRETE = "concrete"
    MASONRY = "masonry"
    WOOD = "wood"
    INSULATION = "insulation"
    GLASS = "glass"

class DimensionKind(str, Enum):
    LINEAR_CHAIN = "linear_chain"
    LINEAR_OVERALL = "linear_overall"
    LINEAR_BETWEEN_AXES = "linear_axes"
    RADIAL = "radial"
    ANGULAR = "angular"

@dataclass(frozen=True, order=True)
class Point:
    x: float
    y: float
    def offset(self, dx: float, dy: float) -> "Point":
        return Point(self.x + dx, self.y + dy)

@dataclass(frozen=True)
class Line:
    start: Point
    end: Point
    weight: LineWeight = LineWeight.MEDIUM
    layer: str = "0"
    dashed: bool = False

@dataclass(frozen=True)
class Polyline:
    points: tuple[Point, ...]
    weight: LineWeight = LineWeight.MEDIUM
    closed: bool = False
    layer: str = "0"
    dashed: bool = False
    def __post_init__(self) -> None:
        if len(self.points) < 2:
            raise ValueError("Polyline requires at least 2 points")

@dataclass(frozen=True)
class Rect:
    origin: Point
    width: float
    height: float
    weight: LineWeight = LineWeight.MEDIUM
    layer: str = "0"
    def corners(self) -> tuple[Point, Point, Point, Point]:
        x0, y0 = self.origin.x, self.origin.y
        x1, y1 = x0 + self.width, y0 + self.height
        return (Point(x0, y0), Point(x1, y0), Point(x1, y1), Point(x0, y1))
    def to_polyline(self) -> Polyline:
        return Polyline(self.corners(), self.weight, closed=True, layer=self.layer)

@dataclass(frozen=True)
class Text:
    position: Point
    content: str
    height_mm: float = 2.5
    anchor: TextAnchor = TextAnchor.START
    rotation_deg: float = 0.0
    layer: str = "0"
    def __post_init__(self) -> None:
        if not self.content:
            raise ValueError("Text content must be non-empty")
        if self.height_mm <= 0:
            raise ValueError("Text height must be positive")

@dataclass(frozen=True)
class Hatch:
    boundary: tuple[Point, ...]
    pattern: HatchPattern
    layer: str = "HATCH"
    def __post_init__(self) -> None:
        if len(self.boundary) < 3:
            raise ValueError("Hatch boundary requires at least 3 points")
        if self.pattern == HatchPattern.NONE:
            raise ValueError("Hatch pattern NONE is not a valid hatch")

@dataclass(frozen=True)
class Dimension:
    kind: DimensionKind
    extension_points: tuple[Point, ...]
    text: str
    text_position: Point | None = None
    layer: str = "DIM"
    def __post_init__(self) -> None:
        if len(self.extension_points) < 2:
            raise ValueError("Dimension requires at least 2 extension points")
        if not self.text:
            raise ValueError("Dimension text must be non-empty")
