from __future__ import annotations

from dataclasses import dataclass

from .sheet_format import SheetFormat


@dataclass(frozen=True)
class SheetGrid:
    sheet_format: SheetFormat
    margins: dict[str, float]
    columns: int = 12
    gutter_mm: float = 5.0

    @property
    def content_bbox(self) -> tuple[float, float, float, float]:
        return (
            self.margins["left"],
            self.margins["bottom"],
            self.sheet_format.width_mm - self.margins["right"],
            self.sheet_format.height_mm - self.margins["top"],
        )

    @property
    def column_width_mm(self) -> float:
        x1, _, x2, _ = self.content_bbox
        return (x2 - x1 - self.gutter_mm * (self.columns - 1)) / self.columns

    def column_bbox(self, start: int, span: int, y1: float, y2: float) -> tuple[float, float, float, float]:
        if start < 1 or span < 1 or start + span - 1 > self.columns:
            raise ValueError("grid column range is outside the sheet")
        x1 = self.content_bbox[0] + (start - 1) * (self.column_width_mm + self.gutter_mm)
        x2 = x1 + span * self.column_width_mm + (span - 1) * self.gutter_mm
        return (x1, y1, x2, y2)
