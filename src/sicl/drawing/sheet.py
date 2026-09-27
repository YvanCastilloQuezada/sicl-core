"""Sheet composition: paper + margins + title block + viewports."""
from __future__ import annotations
from dataclasses import dataclass, field
from .paper import DEFAULT_MARGINS, Margins, Orientation, PaperSize, PaperSpec
from .primitives import Dimension, Hatch, Line, Polyline, Rect, Text
from .scale import Scale
from .title_block import TitleBlock

@dataclass(frozen=True)
class Viewport:
    name: str
    scale: Scale
    origin_paper_mm: tuple[float, float]
    elements: tuple[Line | Polyline | Rect | Text | Hatch | Dimension, ...] = field(default_factory=tuple)
    label_position_paper_mm: tuple[float, float] | None = None
    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Viewport name is required")

@dataclass(frozen=True)
class Sheet:
    paper: PaperSpec
    title_block: TitleBlock
    viewports: tuple[Viewport, ...] = field(default_factory=tuple)
    margins: Margins = DEFAULT_MARGINS
    general_notes: tuple[str, ...] = field(default_factory=tuple)
    @classmethod
    def for_vivienda_a3(cls, title_block: TitleBlock) -> "Sheet":
        return cls(PaperSpec(PaperSize.A3, Orientation.LANDSCAPE), title_block)
    def inner_width_mm(self) -> float:
        return self.paper.width_mm() - self.margins.left_mm - self.margins.right_mm
    def inner_height_mm(self) -> float:
        return self.paper.height_mm() - self.margins.top_mm - self.margins.bottom_mm
