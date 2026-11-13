from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import sqlite3
from pathlib import Path
from typing import List, Optional
import re

router = APIRouter(prefix="/api/v1/normativa", tags=["normativa"])

DB_PATH = Path("data/normativa.db")

class NormativaSearchRequest(BaseModel):
    query: str
    categoria: Optional[str] = None
    limit: int = 5

class NormativaArticulo(BaseModel):
    norma: str
    articulo: str
    titulo: str
    contenido: str
    keywords: str
    relevancia: float

@router.post("/search", response_model=List[NormativaArticulo])
async def search_normativa(request: NormativaSearchRequest):
    if not DB_PATH.exists():
        raise HTTPException(status_code=500, detail="Base de datos de normativa no inicializada")
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Búsqueda por keywords y contenido
    keywords = request.query.lower().split()
    
    results = []
    
    # Consulta base
    query = """
    SELECT norma, articulo, titulo, contenido, keywords
    FROM articulos
    WHERE 1=1
    """
    params = []
    
    if request.categoria:
        query += " AND categoria = ?"
        params.append(request.categoria)
    
    # Buscar por keywords en contenido o keywords
    for keyword in keywords:
        query += f" AND (contenido LIKE ? OR keywords LIKE ? OR titulo LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
    
    query += " LIMIT ?"
    params.append(request.limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    for row in rows:
        # Calcular relevancia (cuántas keywords coinciden)
        content_lower = row[3].lower()
        matches = sum(1 for kw in keywords if kw in content_lower)
        relevancia = matches / len(keywords) if keywords else 0
        
        results.append({
            "norma": row[0],
            "articulo": row[1],
            "titulo": row[2],
            "contenido": row[3],
            "keywords": row[4],
            "relevancia": round(relevancia * 100, 1)
        })
    
    conn.close()
    return results

@router.get("/categorias")
async def get_categorias():
    if not DB_PATH.exists():
        return []
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT categoria FROM articulos")
    categorias = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categorias

@router.get("/articulos/{norma}")
async def get_articulos_by_norma(norma: str):
    if not DB_PATH.exists():
        return []
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
    SELECT norma, articulo, titulo, contenido, keywords
    FROM articulos
    WHERE norma LIKE ?
    ORDER BY articulo
    """, (f"%{norma}%",))
    
    results = [
        {
            "norma": row[0],
            "articulo": row[1],
            "titulo": row[2],
            "contenido": row[3],
            "keywords": row[4]
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return results
