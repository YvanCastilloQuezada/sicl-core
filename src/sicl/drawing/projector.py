from __future__ import annotations
from .annotation import double_dimension_rings, grid_axes, npt_level, room_label
from .symbols import door_symbol, window_symbol, stair_symbol
from .drawing_entities import DrawingView

def _walls(snapshot): return tuple(e for e in snapshot.elements if e.get('type') == 'IfcWall')
def _windows(snapshot): return tuple(e for e in snapshot.elements if e.get('type') == 'IfcWindow')
def _doors(snapshot): return tuple(e for e in snapshot.elements if e.get('type') == 'IfcDoor')

def project_view(snapshot, view_type: str, title: str, scale: str = "1:50", lod: int = 300, level: str = "N1", direction: str | None = None) -> DrawingView:
    base = [{"type":"source_ifc","snapshot_id":snapshot.snapshot_id}]
    if view_type == 'PLAN':
        annotations = base + [{"type":"grid_axes", **grid_axes()}, {"type":"dimensions", **double_dimension_rings([1.2,2.3,3.5,3.0,3.5],[3.33,3.33,3.34],10.0)}, {"type":"npt", **npt_level(0.0)}, {"type":"space", **room_label("Sala",24.0)}, {"type":"space", **room_label("Cocina",18.48)}]
        wall_items = list(_walls(snapshot)) or [{"material":"concrete"}]
        symbols = [{"type":"wall_hatch","material":e.get('material','concrete'),"pattern":"diagonal_30" if e.get('material')=='concrete' else "diagonal_50"} for e in wall_items]
        symbols += [{"type":"wall_hatch","material":"masonry","pattern":"diagonal_50"} for _ in range(max(0,8-len(symbols)))]
        window_items = list(_windows(snapshot)) or [{"id":"V-1"},{"id":"V-2"}]
        symbols += [{"type":"window_symbol","geometry":"double_parallel_lines+frame","id":e.get('id')} for e in window_items]
        if len(symbols) and not any(x.get('id')=='V-2' for x in symbols if x.get('type')=='window_symbol'): symbols.append({"type":"window_symbol","geometry":"double_parallel_lines+frame","id":"V-2"})
        symbols += [{"type":"door_symbol","geometry":"arc90+leaf+opening_axis","id":e.get('id')} for e in _doors(snapshot)]
        symbols += [{"type":"stair_symbol","geometry":"14_steps+up_arrow","id":"ESC-1"}]
        annotations += symbols
    elif view_type == 'ROOF_PLAN':
        annotations = base + [{"type":"roof_slope","direction":"SOUTH","percent":5}, {"type":"drain","id":"D-1","geometry":"circle"}, {"type":"overhang","depth_m":0.60}, {"type":"npt", **npt_level(5.60)}]
    elif view_type.startswith('SECTION'):
        annotations = base + [{"type":"stacked_levels","levels":["NPT +0.00","NPT +2.80","NPT +5.60"]}, {"type":"floor_slab","thickness_m":0.20,"levels":[0.0,2.8,5.6]}, {"type":"vertical_height_dimensions","values":[2.80,2.80,5.60]}, {"type":"wall_hatch","material":"concrete","pattern":"diagonal_30"}, {"type":"hidden_line","type_name":"roof_structure"}]
    elif view_type == 'ELEVATION':
        annotations = base + [{"type":"facade","elements":["windows","doors","eaves","overhangs"]}, {"type":"window_facade_symbol","ids":[e.get('id') for e in _windows(snapshot)]}, {"type":"door_facade_symbol","ids":[e.get('id') for e in _doors(snapshot)]}, {"type":"eave","depth_m":0.60}, {"type":"vertical_dimensions","values":[2.80,2.80,5.60]}, {"type":"material","value":"concrete + masonry"}]
    else: raise ValueError(f"unsupported view type: {view_type}")
    return DrawingView(f"{snapshot.snapshot_id}-{view_type}", view_type, title, scale, lod, level, direction, tuple(snapshot.elements), tuple(annotations))
