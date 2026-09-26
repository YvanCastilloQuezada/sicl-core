from __future__ import annotations

def grid_axes(horizontal: tuple[str, ...] = ("A", "A'", "B", "B'", "C"), vertical: tuple[str, ...] = tuple(str(i) for i in range(1, 10))) -> dict:
    return {"horizontal": list(horizontal), "vertical": list(vertical), "symbol": "circle_8mm"}

def double_dimension_rings(partial: list[float], between_axes: list[float], total: float) -> dict:
    return {"partial": partial, "between_axes": between_axes, "total": total, "rings": 2, "unit": "m"}

def npt_level(value: float, label: str | None = None) -> dict:
    return {"value": value, "label": label or f"NPT {value:+.2f}", "symbol": "triangle"}

def room_label(name: str, area_m2: float) -> dict:
    return {"name": name, "area_m2": area_m2, "text": f"{name} · {area_m2:.2f} m²"}
