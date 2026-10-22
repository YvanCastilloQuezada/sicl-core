from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from .bim import BIMElementReference, BIMFormat, BIMModelSnapshot, BIMReviewState
from .domain import SpatialScope
from .regulatory_corpus import load_corpus_fixture


@dataclass(frozen=True)
class RNEValidationFinding:
    element_id: str
    element_entity: str
    regulation_code: str
    regulation_status: str
    result: str
    reason: str
    evidence_ids: list[str]


@dataclass(frozen=True)
class IFCReadResult:
    snapshot: BIMModelSnapshot
    findings: list[RNEValidationFinding]
    source_file: str
    parser: str
    read_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["snapshot"]["format"] = self.snapshot.format.value
        result["snapshot"]["spatial_scope"] = self.snapshot.spatial_scope.value
        result["snapshot"]["review_state"] = self.snapshot.review_state.value
        return result


_ENTITY_RULES: dict[str, tuple[str, ...]] = {
    "IfcWall": ("A.010", "E.030", "E.060"),
    "IfcSlab": ("A.010", "E.030", "E.060"),
    "IfcColumn": ("E.030", "E.060"),
    "IfcBeam": ("E.030", "E.060"),
    "IfcSpace": ("A.010", "IS.010", "EM.010"),
    "IfcDoor": ("A.010",),
    "IfcWindow": ("A.010",),
    "IfcSanitaryTerminal": ("IS.010",),
    "IfcFlowTerminal": ("IS.010", "EM.010"),
    "IfcLightFixture": ("EM.010",),
    "IfcElectricDistributionPoint": ("EM.010",),
}


def _property_dict(element: Any) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for relation in getattr(element, "IsDefinedBy", ()) or ():
        definition = getattr(relation, "RelatingPropertyDefinition", None)
        if definition is None or not hasattr(definition, "HasProperties"):
            continue
        for prop in definition.HasProperties or ():
            name = getattr(prop, "Name", None)
            if not name:
                continue
            nominal = getattr(prop, "NominalValue", None)
            values[str(name)] = getattr(nominal, "wrappedValue", nominal)
    return values


def _element_reference(element: Any) -> BIMElementReference:
    global_id = str(getattr(element, "GlobalId", ""))
    entity = str(getattr(element, "is_a", lambda: type(element).__name__)())
    parameters = _property_dict(element)
    for field in ("Name", "ObjectType", "PredefinedType"):
        value = getattr(element, field, None)
        if value not in (None, ""):
            parameters[field] = value
    return BIMElementReference(
        global_id=global_id,
        entity=entity,
        parameters=parameters,
        provenance={"parser": "IfcOpenShell", "read_only": True},
    )


def validate_elements_against_rne(elements: list[BIMElementReference], fixture_path: str | Path) -> list[RNEValidationFinding]:
    fixture = load_corpus_fixture(fixture_path)
    regulations = {item["code"]: item for item in fixture["regulations"]}
    evidence_by_code: dict[str, list[str]] = {}
    for evidence in fixture["evidence"]:
        code = evidence["article_reference"].split("-")[0]
        evidence_by_code.setdefault(code, []).append(evidence["evidence_id"])
    findings: list[RNEValidationFinding] = []
    for element in elements:
        for code in _ENTITY_RULES.get(element.entity, ()):
            regulation = regulations.get(code)
            if regulation is None:
                continue
            findings.append(RNEValidationFinding(
                element_id=element.global_id,
                element_entity=element.entity,
                regulation_code=code,
                regulation_status=regulation["status"],
                result="REVIEW_REQUIRED",
                reason="The fixture is NO_VERIFICADA; BIM geometry and parameters do not constitute legal compliance evidence.",
                evidence_ids=evidence_by_code.get(code, []),
            ))
    return findings


def parse_ifc_file(
    path: str | Path,
    project_id: str,
    spatial_scope: SpatialScope = SpatialScope.EDIFICACION,
    coordinate_reference_system: str = "UNKNOWN",
    units: str = "SI",
    rne_fixture_path: str | Path | None = None,
) -> IFCReadResult:
    """Parse a physical IFC file without writing to the file or applying changes."""
    try:
        import ifcopenshell
    except ImportError as exc:  # pragma: no cover - exercised in deployment misconfiguration
        raise RuntimeError("IfcOpenShell is required for physical IFC import") from exc
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(str(source))
    model = ifcopenshell.open(str(source))
    elements = [_element_reference(element) for element in model.by_type("IfcProduct") if getattr(element, "GlobalId", None)]
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    snapshot = BIMModelSnapshot(
        exchange_id=f"IFC-{digest[:16]}",
        format=BIMFormat.IFC,
        source_application="IfcOpenShell",
        source_version=str(getattr(ifcopenshell, "version", "unknown")),
        project_id=project_id,
        spatial_scope=spatial_scope,
        coordinate_reference_system=coordinate_reference_system,
        units=units,
        model_hash=f"sha256:{digest}",
        elements=elements,
        review_state=BIMReviewState.HUMAN_REVIEW_REQUIRED,
    )
    findings = validate_elements_against_rne(elements, rne_fixture_path) if rne_fixture_path else []
    return IFCReadResult(snapshot, findings, str(source), "IfcOpenShell", True)


def result_to_json(result: IFCReadResult) -> str:
    return json.dumps(result.to_dict(), indent=2, sort_keys=True, default=str)
