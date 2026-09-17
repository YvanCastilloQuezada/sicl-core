from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.deps import get_repository
from api.schemas import CopilotTranslateRequest, OGCQueryRequest, ParcelSnapshotCreateRequest
from sicl.copilot import OllamaCopilot, intent_to_dict
from sicl.gis import cadastral_catalog, fetch_ogc_features, ingest_geojson, parcel_to_dict
from sicl.repository import SQLiteRepository

router = APIRouter(prefix="/v1", tags=["gis-copilot"])


@router.get("/gis/catalogs")
def list_gis_catalogs(jurisdiction: str | None = None):
    return {"contract_version": "1.0", "status": "OK", "code": "OK", "message": "Cadastral source catalog", "data": {"jurisdiction": jurisdiction, "sources": cadastral_catalog(jurisdiction)}}


@router.post("/projects/{project_id}/gis/parcel-snapshots")
def create_parcel_snapshot(project_id: str, request: ParcelSnapshotCreateRequest, repo: SQLiteRepository = Depends(get_repository)):
    try:
        item = ingest_geojson(request.feature, project_id, request.source_url, request.source_type, request.jurisdiction, request.source_crs, request.analysis_crs, request.validity_date)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"code": "INVALID_GEOJSON", "message": str(exc)}) from exc
    repo.insert_parcel_snapshot(item)
    return {"contract_version": "1.0", "status": "OK", "code": "OK", "message": "Parcel snapshot received for human review", "project_id": project_id, "data": {"snapshot": parcel_to_dict(item), "decision_created": False}}


@router.get("/projects/{project_id}/gis/parcel-snapshots")
def list_parcel_snapshots(project_id: str, repo: SQLiteRepository = Depends(get_repository)):
    items = repo.list_parcel_snapshots(project_id)
    return {"contract_version": "1.0", "status": "OK", "code": "OK", "message": "Parcel snapshots", "project_id": project_id, "data": {"snapshots": [parcel_to_dict(item) for item in items], "decision_created": False}}


@router.post("/projects/{project_id}/gis/ogc-query")
def query_ogc(project_id: str, request: OGCQueryRequest, repo: SQLiteRepository = Depends(get_repository)):
    try:
        items = fetch_ogc_features(request.url, project_id, request.source_type, request.jurisdiction, request.source_crs, request.analysis_crs)
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=422, detail={"code": "OGC_QUERY_REJECTED", "message": str(exc)}) from exc
    for item in items:
        repo.insert_parcel_snapshot(item)
    return {"contract_version": "1.0", "status": "OK", "code": "OK", "message": "OGC features received for human review", "project_id": project_id, "data": {"snapshots": [parcel_to_dict(item) for item in items], "decision_created": False}}


@router.post("/copilot/translate")
def translate_copilot(request: CopilotTranslateRequest):
    try:
        intent = OllamaCopilot(model=request.model).translate_preview(request.text)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail={"code": str(exc).split(":", 1)[0], "message": str(exc)}) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"code": "INVALID_COPILOT_OUTPUT", "message": str(exc)}) from exc
    return {"contract_version": "1.0", "status": "OK", "code": "OK", "message": "SICL command preview generated; not executed", "data": {"intent": intent_to_dict(intent), "executed": False, "decision_created": False}}
