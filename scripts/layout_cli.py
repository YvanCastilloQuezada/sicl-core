#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sicl.layout import LayoutElement, SheetZone, calculate_layout, create_layout, declare_zones, export_layout_json, report_text, validate_layout
from sicl.layout.sheet_format import get_format

STORE = Path("/tmp/arki-rfc0341-layouts.json")


def load_store() -> dict[str, dict]:
    return json.loads(STORE.read_text()) if STORE.exists() else {}


def save_store(data: dict[str, dict]) -> None:
    STORE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def from_dict(data: dict):
    layout = create_layout(data["layout_id"], data["format"]["name"], data["format"]["orientation"], data["margins"])
    zones = [SheetZone(z["zone_type"], z["x1"], z["y1"], z["x2"], z["y2"]) for z in data.get("zones", [])]
    elements = [LayoutElement(e["element_id"], e["element_type"], tuple(e["bbox"]), e.get("allowed_overlap", False), e.get("metadata", {})) for e in data.get("elements", [])]
    declare_zones(layout, zones)
    return calculate_layout(layout, elements)


def parse_json(value: str):
    return json.loads(value)


def main() -> int:
    global STORE
    parser = argparse.ArgumentParser(prog="/LAYOUT")
    parser.add_argument("command", nargs="+")
    parser.add_argument("--orientation", choices=["H", "V"], default="H")
    parser.add_argument("--top", type=float)
    parser.add_argument("--bottom", type=float)
    parser.add_argument("--left", type=float)
    parser.add_argument("--right", type=float)
    parser.add_argument("--zones")
    parser.add_argument("--elements")
    parser.add_argument("--format", dest="output_format", default="JSON")
    parser.add_argument("--store", default=str(STORE))
    args = parser.parse_args()
    STORE = Path(args.store)
    data = load_store()
    command = [part.upper() for part in args.command]

    if len(command) >= 3 and command[:2] == ["FORMAT", "SET"]:
        print(json.dumps(asdict(get_format(args.command[2], args.orientation))))
        return 0
    if command == ["MARGINS", "SET"]:
        margins = {key: getattr(args, key) for key in ("top", "bottom", "left", "right")}
        if any(value is None for value in margins.values()): parser.error("all margins are required")
        print(json.dumps(margins))
        return 0
    if len(command) >= 3 and command[:2] == ["ZONES", "DECLARE"]:
        layout_id = args.command[2]
        layout = create_layout(layout_id, "A3", args.orientation)
        declare_zones(layout, [SheetZone(z["zone_type"], z["x1"], z["y1"], z["x2"], z["y2"]) for z in parse_json(args.zones or "[]")])
        data[layout_id] = layout.to_dict(); save_store(data); print(json.dumps(data[layout_id], ensure_ascii=False)); return 0
    if len(command) >= 3 and command[:2] == ["ZONES", "SHOW"]:
        print(json.dumps(data[args.command[2]]["zones"], ensure_ascii=False)); return 0
    if len(command) >= 2 and command[0] == "CALCULATE":
        layout_id = args.command[1]; layout = from_dict(data[layout_id])
        elements = [LayoutElement(e["element_id"], e["element_type"], tuple(e["bbox"]), e.get("allowed_overlap", False), e.get("metadata", {})) for e in parse_json(args.elements or "[]")]
        data[layout_id] = calculate_layout(layout, elements).to_dict(); save_store(data); print(json.dumps(data[layout_id], ensure_ascii=False)); return 0
    if len(command) >= 2 and command[0] == "VALIDATE":
        layout = from_dict(data[args.command[1]]); result = validate_layout(layout); data[layout.layout_id] = layout.to_dict(); save_store(data); print(json.dumps(result.to_dict(), ensure_ascii=False)); return 0
    if len(command) >= 2 and command[0] == "SHOW":
        print(json.dumps(data[args.command[1]], ensure_ascii=False)); return 0
    if len(command) >= 2 and command[0] == "REPORT":
        layout = from_dict(data[args.command[1]]); print(report_text(layout.layout_id, validate_layout(layout))); return 0
    if len(command) >= 2 and command[0] == "EXPORT" and args.output_format.upper() == "JSON":
        print(json.dumps(data[args.command[1]], indent=2, ensure_ascii=False)); return 0
    parser.error("unsupported /LAYOUT command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
