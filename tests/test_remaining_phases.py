from __future__ import annotations

from datetime import datetime, timezone

from sicl.bim import BIMElementReference, BIMFormat, BIMModelSnapshot, detect_bim_conflicts
from sicl.bim_connectors import ArchicadAdapter, RevitAdapter
from sicl.domain import SpatialScope
from sicl.gis import ingest_geojson, is_expired, reconcile_parcels
from sicl.cli import CLI
from sicl.repository import SQLiteRepository


def _feature(parcel_id: str, value: str):
    return {"type": "Feature", "id": parcel_id, "properties": {"value": value}, "geometry": {"type": "Polygon", "coordinates": [[[0,0],[1,0],[1,1],[0,0]]]}}


def test_parcel_snapshot_persists_append_only_and_expires():
    repo = SQLiteRepository(":memory:")
    assert CLI(repo, actor="test").execute('/PROJECT CREATE P-GIS "GIS"')['code'] == "OK"
    item = ingest_geojson(_feature("P-1", "a"), "P-GIS", "https://example.test/parcel", validity_date="2020-01-01")
    repo.insert_parcel_snapshot(item)
    assert repo.list_parcel_snapshots("P-GIS")[0].parcel_id == "P-1"
    assert is_expired(item, datetime(2026, 1, 1, tzinfo=timezone.utc)) is True
    repo.close()


def test_parcel_boundary_conflict_is_human_review_required():
    left = ingest_geojson(_feature("P-1", "a"), "P-GIS", "https://example.test/a")
    right = ingest_geojson(_feature("P-1", "b"), "https://example.test") if False else ingest_geojson(_feature("P-1", "b"), "P-GIS", "https://example.test/b")
    conflict = reconcile_parcels(left, right)
    assert conflict is not None
    assert conflict.state == "HUMAN_REVIEW_REQUIRED"


def test_bim_conflict_and_native_adapters_are_safe():
    def snapshot(exchange_id, global_id, value):
        return BIMModelSnapshot(exchange_id, BIMFormat.IFC, "test", "1", "P-BIM", SpatialScope.EDIFICACION, "EPSG:4326", "SI", exchange_id, [BIMElementReference(global_id, "IfcWall", {"value": value})])
    conflict = detect_bim_conflicts(snapshot("A", "G1", "a"), snapshot("B", "G1", "b"))
    assert conflict is not None
    assert conflict.state == "HUMAN_REVIEW_REQUIRED"
    assert RevitAdapter().inspect("model.rvt").status == "HOST_REQUIRED"
    assert ArchicadAdapter().inspect("model.pln").status == "HOST_REQUIRED"
