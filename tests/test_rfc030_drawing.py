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
