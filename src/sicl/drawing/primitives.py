"""2D drawing primitives. Frozen, deterministic, SVG-friendly."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import math


def _finite(value: float, name: str) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")


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
    primitive_id: str | None = None
    semantic_role: str | None = None
    source_ref: str | None = None
    def __post_init__(self) -> None:
        for name, value in (("start.x", self.start.x), ("start.y", self.start.y), ("end.x", self.end.x), ("end.y", self.end.y)):
            _finite(value, name)


@dataclass(frozen=True)
class Polyline:
    points: tuple[Point, ...]
    weight: LineWeight = LineWeight.MEDIUM
    closed: bool = False
    layer: str = "0"
    dashed: bool = False
    primitive_id: str | None = None
    semantic_role: str | None = None
    source_ref: str | None = None
    def __post_init__(self) -> None:
        if len(self.points) < 2:
            raise ValueError("Polyline requires at least 2 points")
        for point in self.points:
            _finite(point.x, "point.x")
            _finite(point.y, "point.y")


@dataclass(frozen=True)
class Rect:
    origin: Point
    width: float
    height: float
    weight: LineWeight = LineWeight.MEDIUM
    layer: str = "0"
    primitive_id: str | None = None
    semantic_role: str | None = None
    source_ref: str | None = None
    def __post_init__(self) -> None:
        _finite(self.origin.x, "origin.x")
        _finite(self.origin.y, "origin.y")
        if not math.isfinite(self.width) or not math.isfinite(self.height) or self.width <= 0 or self.height <= 0:
            raise ValueError("Rect width and height must be positive finite values")
    def corners(self) -> tuple[Point, Point, Point, Point]:
        x0, y0 = self.origin.x, self.origin.y
        x1, y1 = x0 + self.width, y0 + self.height
        return (Point(x0, y0), Point(x1, y0), Point(x1, y1), Point(x0, y1))
    def to_polyline(self) -> Polyline:
        return Polyline(self.corners(), self.weight, closed=True, layer=self.layer, primitive_id=self.primitive_id, semantic_role=self.semantic_role, source_ref=self.source_ref)


@dataclass(frozen=True)
class Text:
    position: Point
    content: str
    height_mm: float = 2.5
    anchor: TextAnchor = TextAnchor.START
    rotation_deg: float = 0.0
    layer: str = "0"
    primitive_id: str | None = None
    semantic_role: str | None = None
    source_ref: str | None = None
    def __post_init__(self) -> None:
        if not self.content:
            raise ValueError("Text content must be non-empty")
        if self.height_mm <= 0 or not math.isfinite(self.height_mm):
            raise ValueError("Text height must be positive and finite")
        _finite(self.position.x, "position.x")
        _finite(self.position.y, "position.y")
        _finite(self.rotation_deg, "rotation_deg")


@dataclass(frozen=True)
class Hatch:
    boundary: tuple[Point, ...]
    pattern: HatchPattern
    layer: str = "HATCH"
    primitive_id: str | None = None
    semantic_role: str | None = None
    source_ref: str | None = None
    def __post_init__(self) -> None:
        if len(self.boundary) < 3:
            raise ValueError("Hatch boundary requires at least 3 points")
        if self.pattern == HatchPattern.NONE:
            raise ValueError("Hatch pattern NONE is not a valid hatch")
        for point in self.boundary:
            _finite(point.x, "point.x")
            _finite(point.y, "point.y")


@dataclass(frozen=True)
class Circle:
    center: Point
    radius: float
    weight: LineWeight = LineWeight.MEDIUM
    layer: str = "0"
    primitive_id: str | None = None
    semantic_role: str | None = None
    source_ref: str | None = None
    def __post_init__(self) -> None:
        _finite(self.center.x, "center.x")
        _finite(self.center.y, "center.y")
        if not math.isfinite(self.radius) or self.radius <= 0:
            raise ValueError("Circle radius must be positive and finite")


@dataclass(frozen=True)
class Arc:
    center: Point
    radius: float
    start_deg: float
    end_deg: float
    weight: LineWeight = LineWeight.MEDIUM
    layer: str = "0"
    primitive_id: str | None = None
    semantic_role: str | None = None
    source_ref: str | None = None
    def __post_init__(self) -> None:
        _finite(self.center.x, "center.x")
        _finite(self.center.y, "center.y")
        if not math.isfinite(self.radius) or self.radius <= 0:
            raise ValueError("Arc radius must be positive and finite")
        _finite(self.start_deg, "start_deg")
        _finite(self.end_deg, "end_deg")


@dataclass(frozen=True)
class Dimension:
    kind: DimensionKind
    extension_points: tuple[Point, ...]
    text: str
    text_position: Point | None = None
    layer: str = "DIM"
    primitive_id: str | None = None
    semantic_role: str | None = None
    source_ref: str | None = None
    def __post_init__(self) -> None:
        if len(self.extension_points) < 2:
            raise ValueError("Dimension requires at least 2 extension points")
        if not self.text:
            raise ValueError("Dimension text must be non-empty")
        for point in self.extension_points:
            _finite(point.x, "point.x")
            _finite(point.y, "point.y")
