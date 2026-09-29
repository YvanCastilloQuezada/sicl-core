"""A-002 integration for architectural mutations and initial D-2 creation."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .mutation import ArchiMutation, MutationKind
from .model import ArchiElement
from ..a002 import (
    EvidenceRef,
    HumanAuthorityRef,
    KnowledgeItem,
    KnowledgeState,
    OperationRequirement,
    SpatialScope,
    SufficiencyEngine,
    SufficiencyRequest,
    SufficiencyResult,
    policy_for,
)

_OPERATIONS={MutationKind.MOVE:"archi.move",MutationKind.RESIZE:"archi.resize",MutationKind.ADD_OPENING:"archi.add_opening",MutationKind.DELETE:"archi.delete"}
_CREATION_OPERATION = "archi.promote_initial_elements"


@dataclass(frozen=True)
class ArchiSufficiencySnapshot:
    operation: str
    result: SufficiencyResult
    @property
    def permits(self): return self.result.permits_h005


def snapshot_for(mutation: ArchiMutation, target: ArchiElement | None, engine: SufficiencyEngine | None = None) -> ArchiSufficiencySnapshot:
    operation=_OPERATIONS[mutation.mutation_kind]; engine=engine or SufficiencyEngine()
    knowledge=[]; requirements=[]; evidence=[]
    def add_known(field, value):
        evidence_id = f"ARCHI-{field}"
        ref = EvidenceRef.from_statement(evidence_id, f"{field}={value}", "ARCHI_MODEL", mutation.project_id)
        evidence.append(ref); knowledge.append(KnowledgeItem(field, value, KnowledgeState.KNOWN, (evidence_id,)))
    if target is not None:
        add_known("target_id", target.element_id.value)
        add_known("target_version", target.version)
        add_known("content_hash", target.content_hash())
    else:
        add_known("target_id", mutation.target_id.value)
        add_known("target_version", mutation.target_version)
    requirements += [OperationRequirement("target_id", (KnowledgeState.KNOWN,), True), OperationRequirement("target_version", (KnowledgeState.KNOWN,), True), OperationRequirement("content_hash", (KnowledgeState.KNOWN,), True)]
    if mutation.mutation_kind is MutationKind.ADD_OPENING:
        requirements.append(OperationRequirement("host", (KnowledgeState.KNOWN,), True))
        if "host_id" in mutation.canonical_payload: add_known("host", mutation.canonical_payload["host_id"])
    if mutation.mutation_kind is MutationKind.DELETE:
        requirements.append(OperationRequirement("human_authority_ref", (KnowledgeState.KNOWN,), True, require_human_authority=True))
    req=SufficiencyRequest(mutation.project_id, operation, tuple(knowledge), tuple(requirements), tuple(evidence))
    return ArchiSufficiencySnapshot(operation, engine.evaluate(req))


def _require_non_empty(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty")
    return value


def _creation_evidence_id(kind: str, identity: str) -> str:
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return f"ARCHI-CREATION-{kind}-{digest}"


def creation_requirements() -> tuple[OperationRequirement, ...]:
    return (
        OperationRequirement(
            "developer_proposal_id",
            (KnowledgeState.KNOWN,),
            True,
            reason="initial D-2 promotion requires an identified developer proposal",
        ),
        OperationRequirement(
            "developer_proposal_fingerprint",
            (KnowledgeState.KNOWN,),
            True,
            reason="initial D-2 promotion requires the persisted proposal fingerprint",
        ),
        OperationRequirement(
            "human_review_binding",
            (KnowledgeState.KNOWN,),
            True,
            reason="initial D-2 promotion requires a human review bound to the proposal",
            require_human_authority=True,
        ),
    )


def snapshot_for_creation(
    *,
    project_id: str,
    developer_proposal_id: str,
    developer_proposal_fingerprint: str,
    human_review_id: str,
    human_review_actor: str,
    human_review_timestamp: str,
    knowledge: tuple[KnowledgeItem, ...] = (),
    evidence: tuple[EvidenceRef, ...] = (),
    scale: SpatialScope | None = None,
    jurisdiction: str | None = None,
    policy_allow_assumptions: bool = False,
    engine: SufficiencyEngine | None = None,
) -> ArchiSufficiencySnapshot:
    """Build the A-002 request for initial D-2 creation from persisted evidence."""
    project_id = _require_non_empty(project_id, "project_id")
    developer_proposal_id = _require_non_empty(developer_proposal_id, "developer_proposal_id")
    developer_proposal_fingerprint = _require_non_empty(
        developer_proposal_fingerprint, "developer_proposal_fingerprint"
    )
    human_review_id = _require_non_empty(human_review_id, "human_review_id")
    human_review_actor = _require_non_empty(human_review_actor, "human_review_actor")
    human_review_timestamp = _require_non_empty(human_review_timestamp, "human_review_timestamp")

    proposal_id_evidence = EvidenceRef.from_statement(
        _creation_evidence_id("PROPOSAL-ID", developer_proposal_id),
        f"persisted DEVELOPER_PROPOSAL identity: {developer_proposal_id}",
        "REASONING_EXECUTION_RECORDED",
        project_id,
    )
    proposal_fingerprint_evidence = EvidenceRef.from_statement(
        _creation_evidence_id(
            "PROPOSAL-FINGERPRINT",
            f"{developer_proposal_id}:{developer_proposal_fingerprint}",
        ),
        f"persisted DEVELOPER_PROPOSAL fingerprint: {developer_proposal_fingerprint}",
        "REASONING_EXECUTION_RECORDED",
        project_id,
    )
    review_binding_evidence = EvidenceRef.from_statement(
        _creation_evidence_id(
            "HUMAN-REVIEW-BINDING",
            f"{developer_proposal_id}:{developer_proposal_fingerprint}:{human_review_id}",
        ),
        (
            "persisted HumanReview binding: "
            f"review_id={human_review_id} proposal={developer_proposal_id} "
            f"fingerprint={developer_proposal_fingerprint}"
        ),
        "HUMAN_REVIEW_RECORDED",
        project_id,
    )

    knowledge_all = list(knowledge)
    evidence_all = list(evidence)
    evidence_all.extend(
        (proposal_id_evidence, proposal_fingerprint_evidence, review_binding_evidence)
    )
    knowledge_all.extend(
        (
            KnowledgeItem(
                "developer_proposal_id",
                developer_proposal_id,
                KnowledgeState.KNOWN,
                (proposal_id_evidence.evidence_id,),
            ),
            KnowledgeItem(
                "developer_proposal_fingerprint",
                developer_proposal_fingerprint,
                KnowledgeState.KNOWN,
                (proposal_fingerprint_evidence.evidence_id,),
            ),
            KnowledgeItem(
                "human_review_binding",
                human_review_id,
                KnowledgeState.KNOWN,
                (review_binding_evidence.evidence_id,),
            ),
        )
    )

    human_authority_ref = HumanAuthorityRef(
        actor_id=human_review_actor,
        decision_context="ARCHI_PROMOTE_INITIAL_ELEMENTS",
        recorded_at_iso=human_review_timestamp,
        reference=human_review_id,
    )
    request = SufficiencyRequest(
        project_id=project_id,
        operation=_CREATION_OPERATION,
        knowledge=tuple(knowledge_all),
        requirements=creation_requirements(),
        evidence=tuple(evidence_all),
        scale=scale,
        context=None,
        jurisdiction=jurisdiction,
        policy_allow_assumptions=policy_allow_assumptions,
        policy=policy_for(_CREATION_OPERATION),
        human_authority_ref=human_authority_ref,
    )
    evaluator = engine or SufficiencyEngine()
    return ArchiSufficiencySnapshot(_CREATION_OPERATION, evaluator.evaluate(request))


__all__=[
    "ArchiSufficiencySnapshot",
    "creation_requirements",
    "snapshot_for",
    "snapshot_for_creation",
]
