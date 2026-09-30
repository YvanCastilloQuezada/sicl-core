"""Core-owned DeveloperProposal -> canonical D-2 promotion service.

D-2 is authoritative.  Validation and conversion happen before persistence;
IFC/ledger publication is a convergent effect after the D-2 snapshot commit.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from pydantic import ValidationError

from api.schemas_developer import DeveloperProposalSchema, ProposedArchiElementDTOSchema
from .a002 import HumanAuthorityRef
from .archi.creation_validation import validate_creation
from .archi.identity import ArchiElementId
from .archi.model import ArchiElement, ArchiGeometry, ElementKind, GeometryKind, ProfileSpec
from .archi.sufficiency import snapshot_for_creation
from .archi.transaction import ArchiTransaction, MutationStatus
from .derivation import DerivationLedger
from .domain import Event, now_iso
from .repository import SQLiteRepository


EffectsStatus = Literal["COMPLETE", "PARTIAL", "FAILED", "NOT_ATTEMPTED"]


@dataclass(frozen=True)
class PromotionOutcome:
    committed: bool
    proposal_id: str
    snapshot_id: str | None = None
    d2_version: int | None = None
    canonical: tuple[ArchiElement, ...] = ()
    effects_status: EffectsStatus = "NOT_ATTEMPTED"
    reason: str = ""


def _audit(repo: SQLiteRepository, project_id: str, event_type: str, reason: str, *,
           proposal_id: str, fingerprint: str, review_id: str, actor: str = "ARKI_CORE",
           extra: dict[str, Any] | None = None) -> None:
    payload = {
        "proposal_id": proposal_id,
        "proposal_fingerprint": fingerprint,
        "human_review_id": review_id,
        "reason": reason,
    }
    payload.update(extra or {})
    repo.add_event(Event(None, now_iso(), project_id, event_type, payload, actor, "ARKI_DEVELOPER_PROMOTION"))


def _reject(repo: SQLiteRepository, project_id: str, proposal_id: str, fingerprint: str,
            review_id: str, reason: str, actor: str = "ARKI_CORE") -> PromotionOutcome:
    # A missing project cannot own a valid audit event because events are project-scoped.
    if repo.get_project(project_id) is not None:
        _audit(repo, project_id, "DEVELOPER_PROMOTION_REJECTED", reason,
               proposal_id=proposal_id, fingerprint=fingerprint, review_id=review_id, actor=actor)
    return PromotionOutcome(False, proposal_id, reason=reason)


def _reasoning_execution(repo: SQLiteRepository, project_id: str, proposal_id: str) -> dict[str, Any] | None:
    for event in repo.events(project_id):
        if event.type != "REASONING_EXECUTION_RECORDED":
            continue
        execution = (event.payload or {}).get("execution")
        if (
            isinstance(execution, dict)
            and execution.get("execution_id") == proposal_id
            and execution.get("kind") == "DEVELOPER_PROPOSAL"
        ):
            return execution
    return None


def _already_committed(repo: SQLiteRepository, project_id: str, proposal_id: str,
                       fingerprint: str, review_id: str) -> PromotionOutcome | None:
    try:
        snapshot = repo.get_developer_promotion_commit(
            project_id, proposal_id, fingerprint, review_id
        )
    except RuntimeError as exc:
        return PromotionOutcome(True, proposal_id, effects_status="FAILED", reason=str(exc))
    if snapshot is None:
        return None
    failed = any(
        event.type in {"D2_EFFECTS_FAILED", "D2_INTERNAL_INCONSISTENCY"}
        and (event.payload or {}).get("snapshot_id") == snapshot.snapshot_id
        for event in repo.events(project_id)
    )
    return PromotionOutcome(
        True, proposal_id, snapshot.snapshot_id, snapshot.version, snapshot.elements,
        "FAILED" if failed else "NOT_ATTEMPTED", "ALREADY_COMMITTED",
    )

def _int_field(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"GEOMETRY_CONTRACT_NOT_MAPPED:{field}")
    return value


def _geometry(raw: dict[str, Any] | None) -> ArchiGeometry:
    if raw is None:
        raise ValueError("MISSING_GEOMETRY")
    if not isinstance(raw, dict):
        raise ValueError("GEOMETRY_CONTRACT_NOT_MAPPED")
    geometry_fields = {"kind", "profile", "x_mm", "y_mm", "z_mm", "height_mm"}
    if set(raw) != geometry_fields:
        raise ValueError("GEOMETRY_CONTRACT_NOT_MAPPED")
    try:
        kind = GeometryKind(raw.get("kind"))
    except (TypeError, ValueError):
        raise ValueError("GEOMETRY_CONTRACT_NOT_MAPPED") from None
    profile = raw.get("profile")
    if not isinstance(profile, dict) or set(profile) != {"width_mm", "depth_mm", "radius_mm"}:
        raise ValueError("GEOMETRY_CONTRACT_NOT_MAPPED")
    try:
        radius = profile.get("radius_mm")
        if radius is not None:
            radius = _int_field(radius, "profile.radius_mm")
        return ArchiGeometry(
            kind=kind,
            profile=ProfileSpec(
                _int_field(profile.get("width_mm"), "profile.width_mm"),
                _int_field(profile.get("depth_mm"), "profile.depth_mm"),
                radius,
            ),
            x_mm=_int_field(raw.get("x_mm"), "x_mm"),
            y_mm=_int_field(raw.get("y_mm"), "y_mm"),
            z_mm=_int_field(raw.get("z_mm"), "z_mm"),
            height_mm=_int_field(raw.get("height_mm"), "height_mm"),
        )
    except (TypeError, ValueError) as exc:
        if str(exc).startswith("GEOMETRY_CONTRACT_NOT_MAPPED"):
            raise
        raise ValueError("GEOMETRY_CONTRACT_NOT_MAPPED") from exc


def _properties(raw: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in raw.items():
        valid = (
            value is None
            or isinstance(value, (str, int, float, bool))
            or (isinstance(value, tuple) and all(isinstance(item, str) for item in value))
        )
        if not valid or isinstance(value, (list, dict, set, bytearray)):
            raise ValueError(f"UNSUPPORTED_PROPERTY_VALUE:{key}")
        result[key] = value
    if result.get("canonical") is True:
        raise ValueError("UNSUPPORTED_PROPERTY_VALUE:canonical")
    return result


def _element(project_id: str, proposal: DeveloperProposalSchema,
             dto: ProposedArchiElementDTOSchema) -> ArchiElement:
    try:
        kind = ElementKind(dto.kind)
    except ValueError:
        raise ValueError("UNKNOWN_ELEMENT_KIND") from None
    geometry = _geometry(dto.geometry)
    properties = _properties(dto.properties)
    provenance = {
        "developer_proposal": {
            "proposal_id": proposal.proposal_id,
            "fingerprint": proposal.fingerprint,
        },
        "developer_element": {
            "provisional_id": dto.provisional_id,
            "epistemic_status": dto.epistemic_status,
            "refs": [
                {"source": ref.source, "ref": ref.ref, "fingerprint": ref.fingerprint}
                for ref in dto.provenance
            ],
        },
    }
    return ArchiElement(
        element_id=ArchiElementId.compute(project_id, kind.value, dto.provisional_id),
        project_id=project_id,
        kind=kind,
        geometry=geometry,
        properties=properties,
        provenance=provenance,
        version=1,
    )


def promote_developer_proposal(
    *,
    repo: SQLiteRepository,
    project_id: str,
    proposal_id: str,
    proposal_fingerprint: str,
    human_review_id: str,
    ledger: DerivationLedger,
    ifc_path: str | None = None,
) -> PromotionOutcome:
    if not isinstance(project_id, str) or not project_id.strip():
        return PromotionOutcome(False, proposal_id, reason="PROJECT_NOT_FOUND")
    project = repo.get_project(project_id)
    if project is None:
        return PromotionOutcome(False, proposal_id, reason="PROJECT_NOT_FOUND")

    prior = _already_committed(repo, project_id, proposal_id, proposal_fingerprint, human_review_id)
    if prior is not None:
        return prior

    execution = _reasoning_execution(repo, project_id, proposal_id)
    if execution is None:
        return _reject(repo, project_id, proposal_id, proposal_fingerprint, human_review_id, "PROPOSAL_NOT_FOUND")
    if execution.get("fingerprint") != proposal_fingerprint:
        return _reject(repo, project_id, proposal_id, proposal_fingerprint, human_review_id, "PROPOSAL_FINGERPRINT_MISMATCH")

    try:
        proposal = DeveloperProposalSchema.model_validate(execution.get("payload"))
    except (ValidationError, TypeError, ValueError):
        return _reject(repo, project_id, proposal_id, proposal_fingerprint, human_review_id, "INVALID_DEVELOPER_PROPOSAL")
    if execution.get("fingerprint") != proposal.fingerprint:
        return _reject(repo, project_id, proposal_id, proposal_fingerprint, human_review_id, "PROPOSAL_FINGERPRINT_INCONSISTENT")

    review = project.human_reviews.get(human_review_id)
    if review is None:
        return _reject(repo, project_id, proposal_id, proposal_fingerprint, human_review_id, "HUMAN_REVIEW_NOT_FOUND")
    if (
        review.referenced_entity_type != "DEVELOPER_PROPOSAL"
        or review.referenced_entity_id != proposal_id
        or review.referenced_fingerprint != proposal_fingerprint
        or review.status != "APPROVED"
    ):
        return _reject(repo, project_id, proposal_id, proposal_fingerprint, human_review_id,
                       "HUMAN_REVIEW_BINDING_MISMATCH", review.actor)

    if proposal.proposed_relations:
        return _reject(repo, project_id, proposal_id, proposal_fingerprint, human_review_id,
                       "RELATIONS_NOT_YET_SUPPORTED", review.actor)
    if proposal.proposed_derivations:
        return _reject(repo, project_id, proposal_id, proposal_fingerprint, human_review_id,
                       "DERIVATIONS_NOT_YET_SUPPORTED", review.actor)

    try:
        candidate_elements = tuple(_element(project_id, proposal, dto) for dto in proposal.proposed_elements)
    except (TypeError, ValueError) as exc:
        return _reject(repo, project_id, proposal_id, proposal_fingerprint, human_review_id,
                       str(exc), review.actor)

    existing_canonical = repo.get_d2(project_id) or ()
    structural = validate_creation(
        project_id=project_id,
        candidate_elements=candidate_elements,
        existing_canonical=existing_canonical,
    )
    if not structural.valid:
        return _reject(repo, project_id, proposal_id, proposal_fingerprint, human_review_id,
                       "STRUCTURAL_VALIDATION_FAILED", review.actor)

    sufficiency = snapshot_for_creation(
        project_id=project_id,
        developer_proposal_id=proposal_id,
        developer_proposal_fingerprint=proposal_fingerprint,
        human_review_id=human_review_id,
        human_review_actor=review.actor,
        human_review_timestamp=review.timestamp,
    )
    if not sufficiency.permits:
        return _reject(repo, project_id, proposal_id, proposal_fingerprint, human_review_id,
                       "SUFFICIENCY_NOT_PERMITTED", review.actor)

    authority = HumanAuthorityRef(
        actor_id=review.actor,
        decision_context="ARCHI_PROMOTE_INITIAL_ELEMENTS",
        recorded_at_iso=review.timestamp,
        reference=review.review_id,
    )
    candidate = tuple(existing_canonical) + candidate_elements
    current = repo.get_d2_current_snapshot(project_id)
    base_version = current.version if current is not None else 0
    try:
        commit_status, snapshot = repo.commit_developer_promotion(
            project_id, candidate, review.actor, proposal_id,
            proposal_fingerprint, human_review_id, base_version,
        )
    except RuntimeError as exc:
        if str(exc) == "STALE_BASE_VERSION":
            raise
        return _reject(repo, project_id, proposal_id, proposal_fingerprint, human_review_id,
                       "PROMOTION_PERSIST_FAILED", review.actor)
    except Exception:
        raise

    if commit_status == "ALREADY_COMMITTED":
        return _already_committed(
            repo, project_id, proposal_id, proposal_fingerprint, human_review_id
        ) or PromotionOutcome(
            True, proposal_id, snapshot.snapshot_id, snapshot.version,
            snapshot.elements, "NOT_ATTEMPTED", "ALREADY_COMMITTED",
        )

    transaction = ArchiTransaction(existing_canonical)
    try:
        result = transaction.promote_initial_elements(
            project_id=project_id,
            proposal_id=proposal_id,
            candidate_elements=candidate_elements,
            prepared_derivations=(),
            structural_validation=structural,
            sufficiency_snapshot=sufficiency,
            human_authority_ref=authority,
            ledger=ledger,
            ifc_path=ifc_path,
        )
    except Exception:
        _audit(repo, project_id, "D2_EFFECTS_FAILED", "PROMOTION_EFFECTS_FAILED",
               proposal_id=proposal_id, fingerprint=proposal_fingerprint, review_id=human_review_id,
               actor=review.actor, extra={"snapshot_id": snapshot.snapshot_id, "d2_version": snapshot.version})
        return PromotionOutcome(True, proposal_id, snapshot.snapshot_id, snapshot.version,
                                snapshot.elements, "FAILED", "PROMOTION_EFFECTS_FAILED")

    if result.canonical != snapshot.elements:
        _audit(repo, project_id, "D2_INTERNAL_INCONSISTENCY", "CANONICAL_SNAPSHOT_MISMATCH",
               proposal_id=proposal_id, fingerprint=proposal_fingerprint, review_id=human_review_id,
               actor=review.actor, extra={"snapshot_id": snapshot.snapshot_id, "d2_version": snapshot.version})
        return PromotionOutcome(True, proposal_id, snapshot.snapshot_id, snapshot.version,
                                snapshot.elements, "FAILED", "CANONICAL_SNAPSHOT_MISMATCH")

    if result.status is not MutationStatus.APPLIED:
        _audit(repo, project_id, "D2_EFFECTS_FAILED", result.reason or "PROMOTION_EFFECTS_FAILED",
               proposal_id=proposal_id, fingerprint=proposal_fingerprint, review_id=human_review_id,
               actor=review.actor, extra={"snapshot_id": snapshot.snapshot_id, "d2_version": snapshot.version})
        return PromotionOutcome(True, proposal_id, snapshot.snapshot_id, snapshot.version,
                                snapshot.elements, "FAILED", result.reason or "PROMOTION_EFFECTS_FAILED")

    effects: EffectsStatus = "PARTIAL" if result.reason == "PROMOTED_CLEANUP_DEFERRED" else "COMPLETE"
    return PromotionOutcome(True, proposal_id, snapshot.snapshot_id, snapshot.version,
                            snapshot.elements, effects, result.reason or "PROMOTED")


__all__ = ["PromotionOutcome", "promote_developer_proposal"]
