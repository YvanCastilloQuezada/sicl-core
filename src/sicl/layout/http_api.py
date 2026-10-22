from __future__ import annotations

import json
from dataclasses import asdict
from urllib.parse import parse_qs, urlparse

from .layout_engine import calculate_layout, create_layout, declare_zones, export_layout_json, validate_layout
from .sheet_format import FORMATS
from .sheet_zone import LayoutElement, SheetZone


class LayoutHttpService:
    """HTTP application boundary for layout calculation; it never renders or emits PDFs."""

    def __init__(self) -> None:
        self.layouts: dict[str, object] = {}

    def handle(self, method: str, path: str, payload: dict | None = None):
        parsed = urlparse(path)
        parts = [part for part in parsed.path.split("/") if part]
        query = parse_qs(parsed.query)
        if method == "GET" and parsed.path == "/v1/layouts/formats":
            return 200, {name: asdict(fmt) for name, fmt in FORMATS.items()}
        if len(parts) >= 2 and parts[0:2] == ["v1", "layouts"]:
            if method == "POST" and len(parts) == 2:
                body = payload or {}
                layout_id = str(body["layout_id"])
                layout = create_layout(layout_id, body.get("format", "A3"), body.get("orientation", "H"), body.get("margins"))
                self.layouts[layout_id] = layout
                return 201, export_layout_json(layout)
            layout_id = parts[2] if len(parts) > 2 else ""
            layout = self.layouts.get(layout_id)
            if method == "DELETE" and layout is not None:
                del self.layouts[layout_id]
                return 204, None
            if layout is None:
                return 404, {"error": "layout not found"}
            if method == "GET" and len(parts) == 3:
                return 200, export_layout_json(layout)
            if method == "POST" and len(parts) == 4 and parts[3] == "calculate":
                body = payload or {}
                zones = [SheetZone(z["zone_type"], z["x1"], z["y1"], z["x2"], z["y2"]) for z in body.get("zones", [])]
                elements = [LayoutElement(e["element_id"], e["element_type"], tuple(e["bbox"]), e.get("allowed_overlap", False), e.get("metadata", {})) for e in body.get("elements", [])]
                declare_zones(layout, zones); calculate_layout(layout, elements)
                return 200, export_layout_json(layout)
            if method == "POST" and len(parts) == 4 and parts[3] == "validate":
                return 200, validate_layout(layout).to_dict()
            if method == "GET" and len(parts) == 4 and parts[3] == "report":
                return 200, validate_layout(layout).to_dict()
            if method == "GET" and len(parts) == 4 and parts[3] == "export" and query.get("format", ["JSON"])[0].upper() == "JSON":
                return 200, export_layout_json(layout)
        return 404, {"error": "route not found"}
