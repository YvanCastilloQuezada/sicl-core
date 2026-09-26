from __future__ import annotations

REQUIRED_FIELDS = ("project", "sheet", "title", "scale", "date", "author", "revision", "status")

def peru_title_block(project: str, sheet: str, title: str, scale: str = "1:50") -> dict:
    block = {"project": project, "sheet": sheet, "title": title, "scale": scale, "date": "2026-09-26", "author": "SICL / ARKI", "revision": "R00", "status": "DRAFT"}
    missing = [key for key in REQUIRED_FIELDS if not block.get(key)]
    if missing: raise ValueError(f"missing title block fields: {missing}")
    return {**block, "format": "A3", "dimensions_mm": {"width": 180, "height": 60}}
