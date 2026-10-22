from __future__ import annotations
from dataclasses import dataclass, field, asdict

@dataclass(frozen=True)
class DrawingView:
    view_id: str
    view_type: str
    title: str
    scale: str
    lod: int
    level: str | None = None
    direction: str | None = None
    elements: tuple[dict, ...] = ()
    annotations: tuple[dict, ...] = ()
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class SectionCut:
    cut_id: str
    direction: str
    elevation: float
    label: str

@dataclass(frozen=True)
class DrawingSheet:
    sheet_id: str
    title: str
    views: tuple[DrawingView, ...]
    sheet_format: str = "A3"
    orientation: str = "H"
    def to_dict(self): return {"sheet_id": self.sheet_id, "title": self.title, "views": [v.to_dict() for v in self.views], "sheet_format": self.sheet_format, "orientation": self.orientation}

@dataclass
class DrawingSet:
    drawing_set_id: str
    project_id: str
    mode: str
    sheets: list[DrawingSheet] = field(default_factory=list)
    status: str = "DRAFT"
    reviews: list[dict] = field(default_factory=list)
    def append_sheet(self, sheet: DrawingSheet): self.sheets = [*self.sheets, sheet]
    def to_dict(self): return {"drawing_set_id": self.drawing_set_id, "project_id": self.project_id, "mode": self.mode, "sheets": [s.to_dict() for s in self.sheets], "status": self.status, "reviews": self.reviews}
