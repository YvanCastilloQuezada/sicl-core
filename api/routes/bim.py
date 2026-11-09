from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import sys
from pathlib import Path

# Añadir src al path para importar los motores
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "src"))
from sicl.expediente.bim_converter import BIMConverter
from sicl.expediente.bim_enricher import BIMEnricher

router = APIRouter()

class ConvertRequest(BaseModel):
    points: list[tuple[float, float]] = [(0,0), (10,0), (10,10), (0,10), (0,0)]
    height: float = 3.0

class EnrichRequest(BaseModel):
    ifc_path: str

@router.post("/bim/convert")
def convert_2d_to_ifc(req: ConvertRequest):
    try:
        converter = BIMConverter()
        for i in range(len(req.points)-1):
            converter.create_wall_from_2d_line(req.points[i], req.points[i+1], height=req.height)
        
        output_path = "/tmp/arki_base.ifc"
        converter.export_ifc(output_path)
        return {"status": "OK", "schema": "IFC4X3", "file": output_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bim/enrich")
def enrich_ifc(req: EnrichRequest):
    try:
        enricher = BIMEnricher(req.ifc_path)
        enricher.enrich_walls()
        enricher.enrich_windows()
        
        output_path = "/tmp/arki_enriched_LOD300.ifc"
        enricher.export(output_path)
        return {"status": "OK", "schema": enricher.model.schema, "file": output_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
