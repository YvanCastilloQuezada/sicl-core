from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid
import shutil

router = APIRouter(prefix="/api/v1/files", tags=["files"])

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), project_id: str = "default"):
    allowed_extensions = {".ifc", ".pdf", ".dwg", ".rvt", ".json", ".dxf"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Formato no permitido. Usa: {', '.join(allowed_extensions)}")
    
    unique_filename = f"{project_id}_{uuid.uuid4().hex}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "status": "success",
        "filename": file.filename,
        "saved_as": unique_filename,
        "path": str(file_path),
        "message": f"Archivo '{file.filename}' recibido. ARKI lo está procesando."
    }
