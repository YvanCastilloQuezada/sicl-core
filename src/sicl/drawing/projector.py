from __future__ import annotations
from .annotation import double_dimension_rings, grid_axes, npt_level, room_label
from .symbols import door_symbol, window_symbol, stair_symbol
from .drawing_entities import DrawingView

def project_view(snapshot, view_type: str, title: str, scale: str = "1:50", lod: int = 300, level: str = "N1", direction: str | None = None) -> DrawingView:
    elements = tuple(snapshot.elements)
    return DrawingView(f"{snapshot.snapshot_id}-{view_type}", view_type, title, scale, lod, level, direction, elements, (
        {"type":"grid_axes", **grid_axes()},
        {"type":"dimensions", **double_dimension_rings([3.0,4.0,3.0],[5.0,5.0],10.0)},
        {"type":"npt", **npt_level(0.0)},
        {"type":"space", **room_label("Sala",24.0)},
        {"type":"door", **door_symbol("P-1",0.90)},
        {"type":"window", **window_symbol("V-1",1.20,1.20)},
        {"type":"stair", **stair_symbol("ESC-1",16)},
    ))
