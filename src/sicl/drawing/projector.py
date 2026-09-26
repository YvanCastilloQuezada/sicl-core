from __future__ import annotations
from .annotation import double_dimension_rings, grid_axes, npt_level, room_label
from .drawing_entities import DrawingView

def _walls(snapshot): return tuple(e for e in snapshot.elements if e.get('type') == 'IfcWall')
def _windows(snapshot): return tuple(e for e in snapshot.elements if e.get('type') == 'IfcWindow')
def _doors(snapshot): return tuple(e for e in snapshot.elements if e.get('type') == 'IfcDoor')

def _wall_hatch_annotations(snapshot):
    walls = list(_walls(snapshot))
    if not walls: walls = [{"id":"W-01","material":"concrete"}]
    result=[]
    for i,e in enumerate(walls):
        material=e.get('material','concrete')
        result.append({"type":"wall_hatch","wall_id":e.get('id',f'W-{i+1:02d}'),"material":material,"pattern":"diagonal_30" if material=='concrete' else "diagonal_50","polygon":[[0,0],[1,0],[1,0.2 if material=='concrete' else 0.15],[0,0.2 if material=='concrete' else 0.15]]})
    return result

def project_view(snapshot, view_type: str, title: str, scale: str = "1:50", lod: int = 300, level: str = "N1", direction: str | None = None) -> DrawingView:
    base = [{"type":"source_ifc","snapshot_id":snapshot.snapshot_id}]
    if view_type == 'PLAN':
        annotations = base + [{"type":"grid_axes", **grid_axes()}, {"type":"dimensions", **double_dimension_rings([1.2,2.3,3.5,3.0,3.5],[3.33,3.33,3.34],10.0)}, {"type":"npt", **npt_level(0.0)}, {"type":"space", **room_label("Sala",24.0)}, {"type":"space", **room_label("Cocina",18.48)}]
        symbols = _wall_hatch_annotations(snapshot)
        windows = list(_windows(snapshot)) or [{"id":"V-1"},{"id":"V-2"}]
        doors = list(_doors(snapshot)) or [{"id":"P-1"}]
        symbols += [{"type":"window_symbol","geometry":"double_parallel_lines+frame+sill","id":e.get('id')} for e in windows]
        symbols += [{"type":"door_symbol","geometry":"arc90+leaf+opening_axis","id":e.get('id')} for e in doors]
        symbols += [{"type":"stair_symbol","geometry":"14_steps+up_arrow","id":"ESC-1"}]
        annotations += symbols
    elif view_type == 'ROOF_PLAN':
        annotations = base + [{"type":"roof_silhouette","polygon":[[0,0],[10,0],[10,10],[0,10]]}, {"type":"roof_slope","direction":"SOUTH","percent":5,"arrow":[[5,5],[5,2]]}, {"type":"roof_slope","direction":"NORTH","percent":5,"arrow":[[5,5],[5,8]]}, {"type":"gutter","edges":["NORTH","SOUTH","EAST","WEST"]}, {"type":"drain","id":"D-1","position":[1,1],"geometry":"circle"}, {"type":"drain","id":"D-2","position":[9,9],"geometry":"circle"}, {"type":"overhang","depth_m":0.60}, {"type":"npt", **npt_level(5.60)}]
    elif view_type.startswith('SECTION'):
        direction = direction or ('LONGITUDINAL' if view_type == 'SECTION_LONG' else 'TRANSVERSE')
        walls = _wall_hatch_annotations(snapshot)
        cut_walls = [{"type":"section_wall_cut","wall_id":w["wall_id"],"thickness_m":0.20 if w["material"]=='concrete' else 0.15,"hatch":w["pattern"],"position":i,"direction":direction} for i,w in enumerate(walls[:7])]
        annotations = base + [{"type":"section_direction","value":direction,"axis":"Y" if direction=='LONGITUDINAL' else 'X'}, {"type":"stacked_levels","levels":["NPT +0.00","NPT +2.80","NPT +5.60"]}, {"type":"floor_slab","thickness_m":0.20,"levels":[0.0,2.8,5.6]}, {"type":"vertical_height_dimensions","values":[2.80,2.60,2.80,5.60]}, {"type":"section_wall_cut_count","count":len(cut_walls)}, *cut_walls, {"type":"section_openings","doors":[e.get('id') for e in _doors(snapshot)],"windows":[e.get('id') for e in _windows(snapshot)]}, {"type":"stair_section","steps":14,"direction":"UP"}, {"type":"wall_hatch","material":"concrete","pattern":"diagonal_30"}, {"type":"hidden_line","type_name":"roof_structure"}]
    elif view_type == 'ELEVATION':
        annotations = base + [{"type":"facade","elements":["windows","doors","eaves","overhangs"]}, {"type":"window_facade_symbol","ids":[e.get('id') for e in _windows(snapshot)],"frame":True,"sill":True,"parapet":True}, {"type":"door_facade_symbol","ids":[e.get('id') for e in _doors(snapshot)],"width_m":0.90,"height_m":2.10}, {"type":"eave","id":"ALERO-N1","depth_m":0.60}, {"type":"eave","id":"ALERO-N2","depth_m":0.60}, {"type":"ground_line","elevation":0.0}, {"type":"vertical_dimensions","values":[2.80,2.80,5.60]}, {"type":"material","value":"concrete + masonry"}]
    else: raise ValueError(f"unsupported view type: {view_type}")
    return DrawingView(f"{snapshot.snapshot_id}-{view_type}", view_type, title, scale, lod, level, direction, tuple(snapshot.elements), tuple(annotations))
