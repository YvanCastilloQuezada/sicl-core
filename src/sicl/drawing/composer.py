from __future__ import annotations
from pathlib import Path
from .drawing_entities import DrawingSet, DrawingSheet
from .ifc_synthetic import BIMModelSnapshot
from .projector import project_view
from .title_block import peru_title_block
from .tables import normative_table, area_table, opening_table
from sicl.layout import SheetZone, LayoutElement, calculate_layout, create_layout, declare_zones, validate_layout

def compose_drawing_set(project_id: str, snapshot: BIMModelSnapshot, mode: str = "SINGLE_VIEW_PER_SHEET") -> DrawingSet:
    views = [
        project_view(snapshot,"PLAN","Planta arquitectónica N1",level="N1"),
        project_view(snapshot,"ROOF_PLAN","Planta de techos",level="N1"),
        project_view(snapshot,"SECTION_LONG","Corte vertical longitudinal",direction="LONGITUDINAL"),
        project_view(snapshot,"SECTION_TRANS","Corte vertical transversal",direction="TRANSVERSE"),
        project_view(snapshot,"ELEVATION","Elevación frontal",direction="SOUTH"),
    ]
    if mode == "SINGLE_VIEW_PER_SHEET":
        sheets = [DrawingSheet(f"A-{i+1:02d}", view.title, (view,)) for i, view in enumerate(views)]
    elif mode == "PROFESSIONAL_LAYOUT":
        sheets = [DrawingSheet("A-01", "Plantas arquitectónicas", tuple(views[:2])), DrawingSheet("A-02", "Cortes, elevación y cuadros", tuple(views[2:]),)]
    else: raise ValueError("unsupported drawing layout mode")
    drawing_set = DrawingSet(f"DS-{project_id}-{mode}", project_id, mode, sheets)
    for sheet in drawing_set.sheets:
        layout = create_layout(sheet.sheet_id, "A3", "H", {"top":20,"bottom":20,"left":25,"right":25})
        zones = [SheetZone("title",25,252,395,277),SheetZone("cajetin",230,20,395,80),SheetZone("drawing",25,90,345,245),SheetZone("norte",350,225,395,250),SheetZone("scale",25,82,110,89),SheetZone("notes",115,82,220,89)]
        elements = [LayoutElement(f"{sheet.sheet_id}-title","title",(30,257,210,270)),LayoutElement(f"{sheet.sheet_id}-drawing","drawing",(30,95,340,240)),LayoutElement(f"{sheet.sheet_id}-cajetin","cajetin",(235,25,390,75)),LayoutElement(f"{sheet.sheet_id}-north","north",(355,230,380,245)),LayoutElement(f"{sheet.sheet_id}-scale","scale_bar",(30,83,105,88))]
        layout = calculate_layout(declare_zones(layout,zones), elements)
        if not validate_layout(layout).is_valid: raise ValueError(f"layout invalid: {sheet.sheet_id}")
    return drawing_set

def sheet_metadata(sheet: DrawingSheet) -> dict:
    return {"title_block": peru_title_block("EDIFICIO-YVAN-TRUJILLO-01",sheet.sheet_id,sheet.title),"normative_table":normative_table(),"area_table":area_table(),"opening_table":opening_table(),"legend":"Fondo #FFFFFF · líneas #000000 · achurados gris 30/50/70 · NORTE · escala gráfica"}
