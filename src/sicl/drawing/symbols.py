from __future__ import annotations

def door_symbol(identifier: str, width_m: float, swing: str = "LEFT") -> dict:
    return {"id": identifier, "type": "door", "width_m": width_m, "leaf": True, "swing_arc_degrees": 90, "opening_direction": swing}

def window_symbol(identifier: str, width_m: float, height_m: float) -> dict:
    return {"id": identifier, "type": "window", "width_m": width_m, "height_m": height_m, "nomenclature": identifier}

def stair_symbol(identifier: str, steps: int, direction: str = "UP") -> dict:
    return {"id": identifier, "type": "stair", "steps": steps, "direction": direction}

def sanitary_symbol(identifier: str, fixture: str) -> dict:
    return {"id": identifier, "type": "sanitary", "fixture": fixture}
