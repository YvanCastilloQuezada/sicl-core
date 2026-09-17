from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from .domain import SpatialScope


class BIMFormat(str, Enum):
    IFC = "IFC"
    REVIT = "REVIT"
    ARCHICAD = "ARCHICAD"


class BIMReviewState(str, Enum):
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    REVIEWED = "REVIEWED"
    REJECTED = "REJECTED"


class BIMChangeSetMode(str, Enum):
    PREVIEW = "PREVIEW"
    APPLY_PENDING = "APPLY_PENDING"
    APPLIED = "APPLIED"


@dataclass(frozen=True)
class BIMElementReference:
    global_id: str
    entity: str
    parameters: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.global_id.strip() or not self.entity.strip():
            raise ValueError("global_id and entity are required")


@dataclass(frozen=True)
class BIMModelSnapshot:
    exchange_id: str
    format: BIMFormat
    source_application: str
    source_version: str
    project_id: str
    spatial_scope: SpatialScope
    coordinate_reference_system: str
    units: str
    model_hash: str
    elements: list[BIMElementReference]
    review_state: BIMReviewState = BIMReviewState.HUMAN_REVIEW_REQUIRED
    version: int = 1

    def __post_init__(self) -> None:
        if not self.exchange_id.strip() or not self.project_id.strip():
            raise ValueError("exchange_id and project_id are required")
        if not self.source_application.strip() or not self.source_version.strip():
            raise ValueError("source application and version are required")
        if not self.coordinate_reference_system.strip() or not self.units.strip():
            raise ValueError("coordinate reference system and units are required")
        if not self.model_hash.strip():
            raise ValueError("model_hash is required for traceability")


@dataclass(frozen=True)
class BIMParameterMapping:
    mapping_id: str
    source_parameter: str
    canonical_key: str
    unit: str | None = None
    status: str = "PENDING_REVIEW"
    notes: str | None = None


@dataclass(frozen=True)
class BIMChangeSet:
    change_set_id: str
    project_id: str
    snapshot_id: str
    changes: list[dict[str, Any]]
    requested_by: str
    mode: BIMChangeSetMode = BIMChangeSetMode.PREVIEW
    review_state: BIMReviewState = BIMReviewState.HUMAN_REVIEW_REQUIRED
    version: int = 1

    def __post_init__(self) -> None:
        if not self.change_set_id.strip() or not self.snapshot_id.strip() or not self.requested_by.strip():
            raise ValueError("change_set_id, snapshot_id and requested_by are required")
        if self.mode is not BIMChangeSetMode.PREVIEW:
            raise ValueError("RFC-027 initial implementation only permits PREVIEW change sets")


def element_to_dict(item: BIMElementReference) -> dict[str, Any]:
    return asdict(item)


def snapshot_to_dict(item: BIMModelSnapshot) -> dict[str, Any]:
    result = asdict(item)
    result["format"] = item.format.value
    result["spatial_scope"] = item.spatial_scope.value
    result["review_state"] = item.review_state.value
    result["elements"] = [element_to_dict(element) for element in item.elements]
    return result


def mapping_to_dict(item: BIMParameterMapping) -> dict[str, Any]:
    return asdict(item)


def change_set_to_dict(item: BIMChangeSet) -> dict[str, Any]:
    result = asdict(item)
    result["mode"] = item.mode.value
    result["review_state"] = item.review_state.value
    return result


def build_preview_change_set(change_set_id: str, project_id: str, snapshot_id: str, changes: list[dict[str, Any]], requested_by: str) -> BIMChangeSet:
    """Create a non-mutating preview; no BIM file or element is changed."""
    return BIMChangeSet(change_set_id, project_id, snapshot_id, changes, requested_by)


@dataclass(frozen=True)
class BIMExportRequest:
    export_id: str
    change_set_id: str
    target_format: BIMFormat
    target_application: str
    human_review_id: str
    approved: bool
    source_model_hash: str
    requested_by: str
    status: str = "PENDING_EXTERNAL_EXECUTION"

    def __post_init__(self) -> None:
        if not self.export_id.strip() or not self.change_set_id.strip() or not self.human_review_id.strip():
            raise ValueError("export_id, change_set_id and human_review_id are required")
        if not self.approved:
            raise ValueError("export requires explicit approved HumanReview")


@dataclass(frozen=True)
class BIMConflict:
    conflict_id: str
    project_id: str
    left_snapshot_id: str
    right_snapshot_id: str
    differing_global_ids: list[str]
    state: str = "HUMAN_REVIEW_REQUIRED"


def detect_bim_conflicts(left: BIMModelSnapshot, right: BIMModelSnapshot) -> BIMConflict | None:
    if left.project_id != right.project_id:
        raise ValueError("BIM conflict comparison requires the same project")
    left_by_id = {item.global_id: item for item in left.elements}
    right_by_id = {item.global_id: item for item in right.elements}
    ids = sorted(set(left_by_id) | set(right_by_id))
    differing = [global_id for global_id in ids if left_by_id.get(global_id) != right_by_id.get(global_id)]
    if not differing:
        return None
    return BIMConflict(f"CONFLICT-{left.exchange_id}-{right.exchange_id}", left.project_id, left.exchange_id, right.exchange_id, differing)


def export_request_to_dict(item: BIMExportRequest) -> dict[str, Any]:
    result = asdict(item)
    result["target_format"] = item.target_format.value
    return result


def conflict_to_dict(item: BIMConflict) -> dict[str, Any]:
    return asdict(item)
