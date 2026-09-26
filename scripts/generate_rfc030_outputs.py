from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from sicl.drawing import create_synthetic_ifc, import_ifc_snapshot, compose_drawing_set, export_drawing_set
out=Path(__file__).resolve().parents[1]/"docs/reference/RFC030_OUTPUT"; out.mkdir(parents=True,exist_ok=True)
ifc=create_synthetic_ifc(out/"EDIFICIO-YVAN-TRUJILLO-01.ifc"); snapshot=import_ifc_snapshot("EDIFICIO-YVAN-TRUJILLO-01",ifc)
for mode,name in [("SINGLE_VIEW_PER_SHEET","EDIFICIO-YVAN-TRUJILLO-01_SINGLE_VIEW_PER_SHEET.pdf"),("PROFESSIONAL_LAYOUT","EDIFICIO-YVAN-TRUJILLO-01_PROFESSIONAL_LAYOUT.pdf")]: export_drawing_set(compose_drawing_set(snapshot.mode if False else "EDIFICIO-YVAN-TRUJILLO-01",snapshot,mode),out/name)
print(out)
