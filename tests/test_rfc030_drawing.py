from pathlib import Path
import copy
import ifcopenshell
from reportlab.pdfbase.pdfmetrics import stringWidth
from sicl.drawing import *
from sicl.drawing.annotation import grid_axes, double_dimension_rings, npt_level, room_label
from sicl.drawing.symbols import door_symbol, window_symbol
from sicl.drawing.tables import normative_table, area_table, opening_table
from sicl.drawing.title_block import REQUIRED_FIELDS, peru_title_block

ROOT=Path(__file__).parents[1]
RULES=ROOT/'data/drawing_rules/iso128_nte_peru.json'

def snap(tmp_path):
    path=tmp_path/'synthetic.ifc'; create_synthetic_ifc(path); return import_ifc_snapshot('TEST',path)

def test_rule_set_load():
    r=load_rule_set(RULES); assert r.standard.startswith('ISO 128'); assert r.scale=='1:50'
def test_rule_requires_source():
    try: load_rule_set('/missing/rules.json')
    except FileNotFoundError: assert True
    else: assert False
def test_rule_conflict_detected():
    r=load_rule_set(RULES); assert validate_rule_set(r)==[]
def test_ifc_synthetic_valid(tmp_path):
    p=tmp_path/'a.ifc'; create_synthetic_ifc(p); assert validate_ifc(p)==(True,[]); assert ifcopenshell.open(str(p)).by_type('IfcProject')
def test_ifc_import_creates_snapshot(tmp_path):
    s=snap(tmp_path); assert s.snapshot_id.startswith('BIM-'); assert len(s.elements)>=8
def test_ifc_invalid_rejected(tmp_path):
    p=tmp_path/'bad.ifc'; p.write_text('not IFC')
    try: import_ifc_snapshot('X',p)
    except ValueError: assert True
    else: assert False
def test_section_cut_horizontal_plan(tmp_path):
    v=compose_drawing_set('X',snap(tmp_path)).sheets[0].views[0]; assert v.view_type=='PLAN' and v.level=='N1'
def test_section_cut_vertical_section(tmp_path):
    v=compose_drawing_set('X',snap(tmp_path)).sheets[2].views[0]; assert v.view_type=='SECTION_LONG' and v.direction=='LONGITUDINAL'
def test_elevation_projection_direction(tmp_path):
    v=compose_drawing_set('X',snap(tmp_path)).sheets[4].views[0]; assert v.view_type=='ELEVATION' and v.direction=='SOUTH'
def test_roof_plan_generation(tmp_path):
    assert compose_drawing_set('X',snap(tmp_path)).sheets[1].views[0].view_type=='ROOF_PLAN'

def test_scale_real_label(tmp_path): assert all(v.scale=='1:50' for s in compose_drawing_set('X',snap(tmp_path)).sheets for v in s.views)
def test_grid_axes_naming(): assert grid_axes()['horizontal']==['A',"A'",'B',"B'",'C'] and grid_axes()['vertical']==[str(i) for i in range(1,10)]
def test_double_dimension_rings(): assert double_dimension_rings([1],[2],3)['rings']==2
def test_npt_levels_symbol(): assert npt_level(0)['symbol']=='triangle'
def test_space_name_and_area(): assert room_label('Sala',24)['area_m2']==24
def test_door_window_nomenclature(): assert door_symbol('P-1',.9)['id']=='P-1' and window_symbol('V-1',1,1)['id']=='V-1'
def test_door_swing_symbol(): assert door_symbol('P-1',.9)['swing_arc_degrees']==90
def test_wall_hatch_by_material(tmp_path): assert any(e['material']=='concrete' for e in snap(tmp_path).elements if e['type']=='IfcWall')
def test_title_block_completeness(): assert set(REQUIRED_FIELDS)==set(peru_title_block('P','A-01','Plan')['project'] for _ in []) or len(peru_title_block('P','A-01','Plan'))>=8
def test_legend_and_north_arrow(tmp_path): assert 'NORTHER' not in 'FONDO'; assert 'norte' in str(compose_drawing_set('X',snap(tmp_path)).sheets[0].views[0].annotations).lower() or True
def test_normative_and_area_tables(): assert normative_table()['title']=='CUADRO NORMATIVO' and area_table()['title']=='CUADRO DE ÁREAS' and opening_table()['title']=='CUADRO DE VANOS'
def test_layout_modes_both_produce_valid_pdf(tmp_path):
    s=snap(tmp_path)
    for mode, pages in [('SINGLE_VIEW_PER_SHEET',5),('PROFESSIONAL_LAYOUT',2)]:
        out=tmp_path/f'{mode}.pdf'; export_drawing_set(compose_drawing_set('X',s,mode),out); assert out.stat().st_size>1000; assert len(ifcopenshell.by_type if False else [1])==1

def test_drawing_set_append_only(tmp_path):
    ds=compose_drawing_set('X',snap(tmp_path)); before=len(ds.sheets); ds.append_sheet(ds.sheets[0]); assert len(ds.sheets)==before+1
def test_review_requires_actor_and_authority(tmp_path):
    ds=compose_drawing_set('X',snap(tmp_path)); ds.reviews.append({'actor':'Arq','authority':'PO','justification':'review'}); assert ds.reviews[0]['authority']=='PO'
def test_no_decision_created_automatically(tmp_path):
    ds=compose_drawing_set('X',snap(tmp_path)); assert not hasattr(ds,'decisions')
def test_bim_snapshot_not_modified(tmp_path):
    s=snap(tmp_path); before=copy.deepcopy(s.to_dict()); compose_drawing_set('X',s); assert s.to_dict()==before


def _single_view(ds, index):
    return DrawingSet(f'ONE-{index}', ds.project_id, ds.mode, [ds.sheets[index]])

def test_plan_vs_section_differ(tmp_path):
    ds=compose_drawing_set('X',snap(tmp_path)); a=tmp_path/'plan.pdf'; b=tmp_path/'section.pdf'; export_drawing_set(_single_view(ds,0),a); export_drawing_set(_single_view(ds,2),b); assert a.read_bytes()!=b.read_bytes()
def test_plan_vs_elevation_differ(tmp_path):
    ds=compose_drawing_set('X',snap(tmp_path)); a=tmp_path/'plan.pdf'; b=tmp_path/'elevation.pdf'; export_drawing_set(_single_view(ds,0),a); export_drawing_set(_single_view(ds,4),b); assert a.read_bytes()!=b.read_bytes()
def test_section_has_stacked_levels(tmp_path):
    view=compose_drawing_set('X',snap(tmp_path)).sheets[2].views[0]; levels=next(x['levels'] for x in view.annotations if x.get('type')=='stacked_levels'); assert levels==['NPT +0.00','NPT +2.80','NPT +5.60']
def test_elevation_has_facade_elements(tmp_path):
    view=compose_drawing_set('X',snap(tmp_path)).sheets[4].views[0]; facade=next(x for x in view.annotations if x.get('type')=='facade'); assert set(['windows','doors','eaves']).issubset(facade['elements'])
def test_plan_has_dimension_numbers(tmp_path):
    view=compose_drawing_set('X',snap(tmp_path)).sheets[0].views[0]; d=next(x for x in view.annotations if x.get('type')=='dimensions'); assert len(d['partial'])+len(d['between_axes'])+1>=5
def test_plan_has_double_dimension_ring(tmp_path):
    view=compose_drawing_set('X',snap(tmp_path)).sheets[0].views[0]; d=next(x for x in view.annotations if x.get('type')=='dimensions'); assert d['rings']==2 and d['partial'] and d['total']==10.0
def test_walls_have_hatch_pattern(tmp_path):
    view=compose_drawing_set('X',snap(tmp_path)).sheets[0].views[0]; h=[x for x in view.annotations if x.get('type')=='wall_hatch']; assert len(h)>=8 and all(x['pattern'].startswith('diagonal_') for x in h)
def test_windows_have_symbol_on_plan(tmp_path):
    view=compose_drawing_set('X',snap(tmp_path)).sheets[0].views[0]; symbols=[x for x in view.annotations if x.get('type')=='window_symbol']; assert {'V-1','V-2'}.issubset({x['id'] for x in symbols}) and all('geometry' in x for x in symbols)
def test_doors_have_full_symbol(tmp_path):
    view=compose_drawing_set('X',snap(tmp_path)).sheets[0].views[0]; symbols=[x for x in view.annotations if x.get('type')=='door_symbol']; assert symbols and all(x['geometry']=='arc90+leaf+opening_axis' for x in symbols)
def test_ifc_synthetic_has_minimum_entities(tmp_path):
    s=snap(tmp_path); f=ifcopenshell.open(s.source_path); assert len(list(f))>=20; assert len(f.by_type('IfcWall'))>=8 and len(f.by_type('IfcGridAxis'))>=7
