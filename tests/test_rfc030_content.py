from pathlib import Path

from sicl.drawing import compose_drawing_set, export_drawing_set
from sicl.drawing.drawing_rules import load_rule_set, validate_rule_set
from sicl.drawing.ifc_synthetic import create_synthetic_ifc, import_ifc_snapshot

ROOT = Path(__file__).parents[1]
RULES = ROOT / 'data/drawing_rules/iso128_rne_peru.json'

def _snapshot(tmp_path):
    path = tmp_path / 'drawing-standard.ifc'
    create_synthetic_ifc(path)
    return import_ifc_snapshot('DRAWING-STANDARD', path)

def _pdf_text(path):
    try:
        from pypdf import PdfReader
        return '\n'.join(page.extract_text() or '' for page in PdfReader(str(path)).pages)
    except ImportError:
        return path.read_bytes().decode('latin1', errors='ignore')

def test_plan_matches_drawing_standard(tmp_path):
    rules = load_rule_set(RULES)
    assert validate_rule_set(rules) == []
    drawing_set = compose_drawing_set('DRAWING-STANDARD', _snapshot(tmp_path))
    plan = drawing_set.sheets[0].views[0]
    annotations = plan.annotations
    standard = next(a for a in annotations if a.get('type') == 'drawing_standard')
    hatches = [a for a in annotations if a.get('type') == 'wall_hatch']
    stairs = [a for a in annotations if a.get('type') == 'stair_symbol']
    dimensions = [a for a in annotations if a.get('type') == 'dimensions']
    npt = [a for a in annotations if a.get('type') == 'npt']
    assert standard['rule_set_id'] == 'ISO128_RNE_PERU'
    assert len(hatches) >= 8 and all(h['thickness_m'] in (0.15, 0.20) for h in hatches)
    assert stairs and stairs[0]['steps'] == 14 and stairs[0]['direction_arrow'] is True
    assert dimensions and dimensions[0]['rings'] == 2 and dimensions[0]['numeric'] is True
    assert npt and npt[0]['symbol'] == 'triangle'
    output = tmp_path / 'plan-standard.pdf'
    export_drawing_set(type(drawing_set)(drawing_set.drawing_set_id, drawing_set.project_id, drawing_set.mode, [drawing_set.sheets[0]]), output)
    text = _pdf_text(output)
    assert 'NPT' in text
    assert 'ESCALERA' in text
    assert '3.33 m' in text or '10.00 m' in text
