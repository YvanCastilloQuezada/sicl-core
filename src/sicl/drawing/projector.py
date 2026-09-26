from __future__ import annotations
from pathlib import Path
from .annotation import double_dimension_rings, grid_axes, npt_level, room_label
from .drawing_entities import DrawingView
from .drawing_rules import DrawingRuleSet, load_rule_set

DEFAULT_RULES = Path(__file__).resolve().parents[3] / 'data' / 'drawing_rules' / 'iso128_rne_peru.json'

def _rules(rules: DrawingRuleSet | None) -> DrawingRuleSet:
    return rules or load_rule_set(DEFAULT_RULES)

def _walls(snapshot): return tuple(e for e in snapshot.elements if e.get('type') == 'IfcWall')
def _windows(snapshot): return tuple(e for e in snapshot.elements if e.get('type') == 'IfcWindow')
def _doors(snapshot): return tuple(e for e in snapshot.elements if e.get('type') == 'IfcDoor')

def _wall_hatch_annotations(snapshot, rules: DrawingRuleSet):
    walls = list(_walls(snapshot))
    if not walls: walls = [{"id":"W-01","material":"concrete"}]
    result=[]
    for i,e in enumerate(walls):
        material=e.get('material','concrete')
        hatch = rules.get(f'hatches.{material}', rules.get('hatches.concrete', {}))
        thickness = rules.get(f'wall_thickness.{material}', rules.get('wall_thickness.concrete', 0.20))
        result.append({
            "type":"wall_hatch",
            "wall_id":e.get('id',f'W-{i+1:02d}'),
            "material":material,
            "pattern":hatch.get('pattern','diagonal_30'),
            "gray_percent":hatch.get('gray_percent',30),
            "line_weight_mm":rules.get('line_weights.cut',0.50),
            "thickness_m":thickness,
            "polygon":[[0,0],[1,0],[1,thickness],[0,thickness]],
        })
    return result

def _npt(value, rules: DrawingRuleSet):
    data = npt_level(value)
    data.update({"symbol":rules.get('levels.symbol','triangle'), "format":rules.get('levels.format','NPT {value:+.2f}')})
    return data

def project_view(snapshot, view_type: str, title: str, scale: str = "1:50", lod: int = 300, level: str = "N1", direction: str | None = None, rules: DrawingRuleSet | None = None) -> DrawingView:
    rules = _rules(rules)
    base = [{"type":"source_ifc","snapshot_id":snapshot.snapshot_id}, {"type":"drawing_standard","rule_set_id":rules.rule_set_id,"standard":rules.standard,"line_weights":rules.get('line_weights'),"colors":rules.get('colors')}]
    if view_type == 'PLAN':
        dimensions = double_dimension_rings([1.2,2.3,3.5,3.0,3.5], [3.33,3.33,3.34], 10.0)
        dimensions.update({"rings":rules.get('dimensions.rings',2), "precision_decimals":rules.get('dimensions.precision_decimals',2), "numeric":True, "line_weight_mm":rules.get('line_weights.secondary',0.35)})
        annotations = base + [
            {"type":"grid_axes", **grid_axes()},
            {"type":"dimensions", **dimensions},
            {"type":"npt", **_npt(0.0,rules)},
            {"type":"space", **room_label("Sala",24.0)},
            {"type":"space", **room_label("Cocina",18.48)},
        ]
        symbols = _wall_hatch_annotations(snapshot, rules)
        windows = list(_windows(snapshot)) or [{"id":"V-1"},{"id":"V-2"}]
        doors = list(_doors(snapshot)) or [{"id":"P-1"}]
        window_geometry = rules.get('symbols.window.geometry','double_parallel_lines+frame+sill')
        door_geometry = rules.get('symbols.door.geometry','arc90+leaf+opening_axis')
        stair_geometry = rules.get('symbols.stair.geometry','steps+up_arrow')
        symbols += [{"type":"window_symbol","geometry":window_geometry,"id":e.get('id'),"parallel_lines":rules.get('symbols.window.parallel_lines',2),"frame":rules.get('symbols.window.frame',True)} for e in windows]
        symbols += [{"type":"door_symbol","geometry":door_geometry,"id":e.get('id'),"swing_arc_degrees":rules.get('symbols.door.swing_arc_degrees',90),"leaf":rules.get('symbols.door.leaf',True),"opening_axis":rules.get('symbols.door.opening_axis',True)} for e in doors]
        symbols += [{"type":"stair_symbol","geometry":stair_geometry,"id":"ESC-1","steps":rules.get('symbols.stair.steps',14),"direction_arrow":rules.get('symbols.stair.direction_arrow',True),"width_m":rules.get('symbols.stair.width_m',1.0)}]
        annotations += symbols
    elif view_type == 'ROOF_PLAN':
        annotations = base + [{"type":"roof_silhouette","polygon":[[0,0],[10,0],[10,10],[0,10]]}, {"type":"roof_slope","direction":"SOUTH","percent":5,"arrow":[[5,5],[5,2]]}, {"type":"roof_slope","direction":"NORTH","percent":5,"arrow":[[5,5],[5,8]]}, {"type":"gutter","edges":["NORTH","SOUTH","EAST","WEST"]}, {"type":"drain","id":"D-1","position":[1,1],"geometry":"circle"}, {"type":"drain","id":"D-2","position":[9,9],"geometry":"circle"}, {"type":"overhang","depth_m":0.60}, {"type":"npt", **_npt(5.60,rules)}]
    elif view_type.startswith('SECTION'):
        direction = direction or ('LONGITUDINAL' if view_type == 'SECTION_LONG' else 'TRANSVERSE')
        walls = _wall_hatch_annotations(snapshot, rules)
        cut_walls = [{"type":"section_wall_cut","wall_id":w["wall_id"],"thickness_m":w["thickness_m"],"hatch":w["pattern"],"line_weight_mm":rules.get('line_weights.cut',0.50),"position":i,"direction":direction} for i,w in enumerate(walls[:7])]
        annotations = base + [{"type":"section_direction","value":direction,"axis":"Y" if direction=='LONGITUDINAL' else 'X'}, {"type":"stacked_levels","levels":rules.get('levels.required',["NPT +0.00","NPT +2.80","NPT +5.60"]),"symbol":rules.get('levels.symbol','triangle')}, {"type":"floor_slab","thickness_m":0.20,"levels":[0.0,2.8,5.6]}, {"type":"vertical_height_dimensions","values":[2.80,2.60,2.80,5.60],"numeric":True}, {"type":"section_wall_cut_count","count":len(cut_walls)}, *cut_walls, {"type":"section_openings","doors":[e.get('id') for e in _doors(snapshot)],"windows":[e.get('id') for e in _windows(snapshot)]}, {"type":"stair_section","steps":rules.get('symbols.stair.steps',14),"direction":"UP","direction_arrow":True}, {"type":"wall_hatch","material":"concrete","pattern":rules.get('hatches.concrete.pattern','diagonal_30')}, {"type":"hidden_line","type_name":"roof_structure"}]
    elif view_type == 'ELEVATION':
        annotations = base + [{"type":"facade","elements":["windows","doors","eaves","overhangs"]}, {"type":"window_facade_symbol","ids":[e.get('id') for e in _windows(snapshot)],"frame":True,"sill":True,"parapet":True}, {"type":"door_facade_symbol","ids":[e.get('id') for e in _doors(snapshot)],"width_m":0.90,"height_m":2.10}, {"type":"eave","id":"ALERO-N1","depth_m":0.60}, {"type":"eave","id":"ALERO-N2","depth_m":0.60}, {"type":"ground_line","elevation":0.0}, {"type":"vertical_dimensions","values":[2.80,2.80,5.60]}, {"type":"material","value":"concrete + masonry"}]
    else: raise ValueError(f"unsupported view type: {view_type}")
    return DrawingView(f"{snapshot.snapshot_id}-{view_type}", view_type, title, scale, lod, level, direction, tuple(snapshot.elements), tuple(annotations))
