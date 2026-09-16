from __future__ import annotations

import ifcopenshell

from sicl.domain import SpatialScope
from sicl.ifc_adapter import parse_ifc_file


FIXTURE = "data/regulatory/rne_a010_sample.json"


def _write_ifc(path) -> None:
    model = ifcopenshell.file(schema="IFC4")
    model.create_entity("IfcWall", GlobalId="2Hwall00000000001", OwnerHistory=None, Name="External wall")
    model.create_entity("IfcSpace", GlobalId="2Hspace000000001", OwnerHistory=None, Name="Living space")
    model.write(str(path))


def test_parse_physical_ifc_is_read_only_and_rne_review_required(tmp_path) -> None:
    source = tmp_path / "sample.ifc"
    _write_ifc(source)
    result = parse_ifc_file(source, "IFC-P-001", SpatialScope.EDIFICACION, "EPSG:4326", "SI", FIXTURE)
    assert result.read_only is True
    assert result.parser == "IfcOpenShell"
    assert result.snapshot.model_hash.startswith("sha256:")
    assert result.snapshot.format.value == "IFC"
    assert {element.entity for element in result.snapshot.elements} >= {"IfcWall", "IfcSpace"}
    assert result.findings
    assert all(finding.result == "REVIEW_REQUIRED" for finding in result.findings)
    assert all(finding.regulation_status == "NO_VERIFICADA" for finding in result.findings)
    assert source.exists()


def test_ifc_import_rejects_missing_file(tmp_path) -> None:
    try:
        parse_ifc_file(tmp_path / "missing.ifc", "IFC-P-002")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("missing IFC file must be rejected")
