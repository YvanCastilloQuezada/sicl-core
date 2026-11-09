from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "src"))
from sicl.expediente.specialties_analyzer import SpecialtiesAnalyzer

router = APIRouter()
analyzer = SpecialtiesAnalyzer()

class SpecialtyRequest(BaseModel):
    specialty: str
    params: dict = {}

@router.post("/specialties/analyze")
def run_analysis(req: SpecialtyRequest):
    try:
        result = analyzer.analyze(req.specialty, req.params)
        return {"status": "OK", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
