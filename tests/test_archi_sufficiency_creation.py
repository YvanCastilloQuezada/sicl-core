import pytest

from sicl.a002 import (
    HumanAuthorityRef,
    KnowledgeItem,
    KnowledgeState,
    SufficiencyEngine,
    SufficiencyRequest,
    SufficiencyStatus,
)
from sicl.archi.sufficiency import creation_requirements, snapshot_for_creation


BASE = dict(
    project_id="P",
    developer_proposal_id="dev-prop-1",
    developer_proposal_fingerprint="a" * 64,
    human_review_id="review-1",
    human_review_actor="Yvan",
    human_review_timestamp="2026-09-29T12:01:00Z",
)


def test_creation_requirements_has_exact_three_fields():
    requirements = creation_requirements()
    assert tuple(item.field for item in requirements) == (
        "developer_proposal_id",
        "developer_proposal_fingerprint",
        "human_review_binding",
    )


@pytest.mark.parametrize(
    "field",
    ("developer_proposal_id", "developer_proposal_fingerprint", "human_review_binding"),
)
def test_creation_requirements_require_known(field):
    requirement = next(item for item in creation_requirements() if item.field == field)
    assert requirement.required_states == (KnowledgeState.KNOWN,)
    assert requirement.blocking is True


def test_human_review_binding_requires_human_authority():
    requirement = next(
        item for item in creation_requirements() if item.field == "human_review_binding"
    )
    assert requirement.require_human_authority is True


def test_non_review_requirements_do_not_require_human_authority():
    requirements = creation_requirements()
    for requirement in requirements[:2]:
        assert requirement.require_human_authority is False


def test_snapshot_for_creation_is_sufficient_and_permits():
    snapshot = snapshot_for_creation(**BASE)
    assert snapshot.operation == "archi.promote_initial_elements"
    assert snapshot.result.overall_status is SufficiencyStatus.SUFFICIENT
    assert snapshot.permits is True


def test_snapshot_for_creation_carries_persisted_review_authority_reference():
    snapshot = snapshot_for_creation(**BASE)
    authority = snapshot.result.human_authority_ref
    assert authority == HumanAuthorityRef(
        actor_id="Yvan",
        decision_context="ARCHI_PROMOTE_INITIAL_ELEMENTS",
        recorded_at_iso="2026-09-29T12:01:00Z",
        reference="review-1",
    )


def test_snapshot_for_creation_evidence_ids_are_deterministic():
    first = snapshot_for_creation(**BASE)
    second = snapshot_for_creation(**BASE)
    assert first.result.evidence_refs == second.result.evidence_refs
    assert first.result.request_fingerprint == second.result.request_fingerprint


def test_snapshot_for_creation_operation_is_creation_operation():
    snapshot = snapshot_for_creation(**BASE)
    assert snapshot.result.operation == "archi.promote_initial_elements"


def test_engine_blocks_creation_requirements_without_human_authority():
    snapshot = snapshot_for_creation(**BASE)
    result = SufficiencyEngine().evaluate(
        SufficiencyRequest(
            project_id="P",
            operation=snapshot.operation,
            knowledge=tuple(
                KnowledgeItem(
                    assessment.field,
                    "value",
                    KnowledgeState.KNOWN,
                    assessment.evidence_ids,
                )
                for assessment in snapshot.result.assessments
            ),
            requirements=creation_requirements(),
            evidence=tuple(),
            human_authority_ref=None,
        )
    )
    assert result.overall_status is SufficiencyStatus.INSUFFICIENT


def test_known_without_evidence_is_downgraded_for_creation_requirement():
    result = SufficiencyEngine().evaluate(
        SufficiencyRequest(
            project_id="P",
            operation="archi.promote_initial_elements",
            knowledge=(
                KnowledgeItem("developer_proposal_id", "dev-prop-1", KnowledgeState.KNOWN),
                KnowledgeItem(
                    "developer_proposal_fingerprint", "a" * 64, KnowledgeState.KNOWN
                ),
                KnowledgeItem("human_review_binding", "review-1", KnowledgeState.KNOWN),
            ),
            requirements=creation_requirements(),
            human_authority_ref=HumanAuthorityRef(
                "Yvan",
                "ARCHI_PROMOTE_INITIAL_ELEMENTS",
                "2026-09-29T12:01:00Z",
                "review-1",
            ),
        )
    )
    assert result.overall_status is SufficiencyStatus.INSUFFICIENT
    assert set(result.unknown) == {
        "developer_proposal_id",
        "developer_proposal_fingerprint",
        "human_review_binding",
    }


@pytest.mark.parametrize(
    "field",
    (
        "project_id",
        "developer_proposal_id",
        "developer_proposal_fingerprint",
        "human_review_id",
        "human_review_actor",
        "human_review_timestamp",
    ),
)
def test_snapshot_for_creation_rejects_empty_required_identity(field):
    args = dict(BASE)
    args[field] = " "
    with pytest.raises(ValueError, match=field):
        snapshot_for_creation(**args)
