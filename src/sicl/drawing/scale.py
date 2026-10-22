"""Architectural scales. Deterministic, no floats as keys."""
from __future__ import annotations
from enum import Enum

class Scale(str, Enum):
    S_1_10 = "1:10"
    S_1_20 = "1:20"
    S_1_25 = "1:25"
    S_1_50 = "1:50"
    S_1_75 = "1:75"
    S_1_100 = "1:100"
    S_1_200 = "1:200"
    S_1_250 = "1:250"
    S_1_500 = "1:500"
    S_1_1000 = "1:1000"
    @property
    def denominator(self) -> int:
        return int(self.value.split(":")[1])
    def real_mm_to_paper_mm(self, real_mm: float) -> float:
        if real_mm < 0:
            raise ValueError("real dimension must be non-negative")
        return real_mm / self.denominator
    def paper_mm_to_real_mm(self, paper_mm: float) -> float:
        if paper_mm < 0:
            raise ValueError("paper dimension must be non-negative")
        return paper_mm * self.denominator

DEFAULT_SCALE_BY_VIEW: dict[str, Scale] = {
    "site_plan": Scale.S_1_500,
    "floor_plan": Scale.S_1_50,
    "elevation": Scale.S_1_50,
    "section": Scale.S_1_50,
    "detail": Scale.S_1_20,
    "isometric": Scale.S_1_100,
    "perspective": Scale.S_1_100,
}
