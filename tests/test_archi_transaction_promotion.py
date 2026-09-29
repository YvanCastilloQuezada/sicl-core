import pytest

from sicl.a002 import HumanAuthorityRef, SufficiencyStatus
from sicl.archi import (
    ArchiElement,
    ArchiElementId,
    ArchiGeometry,
    ArchiTransaction,
    ElementKind,
    GeometryKind,
    MutationLifecycle,
    MutationStatus,
    ProfileSpec,
)
from sicl.archi.creation_validation import StructuralValidationResult, validate_creation
from sicl.archi.sufficiency import snapshot_for_creation
from sicl.archi.transaction import PromotionResult, PublishResult
from sicl.derivation import DerivationLedger


class Store:
    def __init__(self):
        self.items = []

    def add_event(self, event):
        self.items.append(event)
        return event

    def add_events_atomic(self, events):
        self.items.extend(events)
        return list(events)

    def events(self, project_id=None):
        return [
            event
            for event in self.items
            if project_id is None or event.project_id == project_id
        ]


def element(nonce: str) -> ArchiElement:
    return ArchiElement(
        ArchiElementId.compute("P", "SPACE", nonce),
        "P",
        ElementKind.SPACE,
        ArchiGeometry(
            GeometryKind.EXTRUDED_RECTANGLE,
            ProfileSpec(3000, 3000),
            height_mm=2800,
        ),
        provenance={"source": "developer-proposal"},
    )


def authority() -> HumanAuthorityRef:
    return HumanAuthorityRef(
        actor_id="Yvan",
        decision_context="ARCHI_PROMOTE_INITIAL_ELEMENTS",
        recorded_at_iso="2026-09-29T12:01:00Z",
        reference="review-1",
    )


def sufficient_snapshot():
    return snapshot_for_creation(
        project_id="P",
        developer_proposal_id="proposal-1",
        developer_proposal_fingerprint="a" * 64,
        human_review_id="review-1",
        human_review_actor="Yvan",
        human_review_timestamp="2026-09-29T12:01:00Z",
    )


def valid_inputs(tx: ArchiTransaction, candidate: tuple[ArchiElement, ...]):
    return dict(
        project_id="P",
        proposal_id="proposal-1",
        candidate_elements=candidate,
        prepared_derivations=(),
        structural_validation=validate_creation(
            project_id="P",
            candidate_elements=candidate,
            existing_canonical=tx.canonical,
        ),
        sufficiency_snapshot=sufficient_snapshot(),
        human_authority_ref=authority(),
        ledger=DerivationLedger(Store()),
    )


def test_promote_initial_elements_applies_and_merges_with_existing_canonical():
    existing = element("existing")
    created = element("created")
    tx = ArchiTransaction((existing,))
    result = tx.promote_initial_elements(**valid_inputs(tx, (created,)))
    assert isinstance(result, PromotionResult)
    assert result.status is MutationStatus.APPLIED
    assert result.lifecycle is MutationLifecycle.PUBLISHED
    assert result.reason == "PROMOTED"
    assert result.derivation_recorded is True
    assert tx.canonical == (existing, created)
    assert result.canonical == result.candidate == tx.canonical


@pytest.mark.parametrize("field", ("project_id", "proposal_id"))
def test_promote_initial_elements_rejects_empty_identity(field):
    tx = ArchiTransaction(())
    args = valid_inputs(tx, (element("created"),))
    args[field] = " "
    with pytest.raises(ValueError, match=field):
        tx.promote_initial_elements(**args)


def test_structural_failure_blocks_without_publication(monkeypatch):
    tx = ArchiTransaction((element("existing"),))
    before = tx.canonical
    args = valid_inputs(tx, (element("created"),))
    args["structural_validation"] = StructuralValidationResult(
        False, ("CANDIDATE_ELEMENTS_EMPTY",)
    )
    monkeypatch.setattr(
        tx,
        "_publish_candidate",
        lambda **kwargs: pytest.fail("_publish_candidate must not be called"),
    )
    result = tx.promote_initial_elements(**args)
    assert result.status is MutationStatus.BLOCKED
    assert result.lifecycle is MutationLifecycle.EVALUATED
    assert result.reason.startswith("STRUCTURAL_VALIDATION_FAILED:")
    assert result.canonical == before == tx.canonical


def test_sufficiency_failure_blocks_without_publication(monkeypatch):
    tx = ArchiTransaction((element("existing"),))
    before = tx.canonical
    args = valid_inputs(tx, (element("created"),))
    blocked = snapshot_for_creation(
        project_id="P",
        developer_proposal_id="proposal-1",
        developer_proposal_fingerprint="a" * 64,
        human_review_id="review-1",
        human_review_actor="Yvan",
        human_review_timestamp="2026-09-29T12:01:00Z",
        knowledge=(),
    )
    object.__setattr__(blocked.result, "overall_status", SufficiencyStatus.INSUFFICIENT)
    args["sufficiency_snapshot"] = blocked
    monkeypatch.setattr(
        tx,
        "_publish_candidate",
        lambda **kwargs: pytest.fail("_publish_candidate must not be called"),
    )
    result = tx.promote_initial_elements(**args)
    assert result.status is MutationStatus.BLOCKED
    assert result.reason == "SUFFICIENCY_NOT_PERMITTED: INSUFFICIENT"
    assert result.canonical == before == tx.canonical


def test_publication_failure_returns_failed_and_preserves_canonical(monkeypatch):
    tx = ArchiTransaction((element("existing"),))
    before = tx.canonical
    args = valid_inputs(tx, (element("created"),))
    monkeypatch.setattr(
        tx,
        "_publish_candidate",
        lambda **kwargs: PublishResult(
            False, before, reason="PUBLICATION:RuntimeError", provenance={"x": 1}
        ),
    )
    result = tx.promote_initial_elements(**args)
    assert result.status is MutationStatus.FAILED
    assert result.lifecycle is MutationLifecycle.EVALUATED
    assert result.reason == "PUBLICATION:RuntimeError"
    assert result.candidate == ()
    assert tx.canonical == before


def test_cleanup_deferred_is_applied_not_rolled_back(monkeypatch):
    existing = element("existing")
    created = element("created")
    tx = ArchiTransaction((existing,))
    monkeypatch.setattr(tx, "_cleanup_ifc", lambda stage, backup: ["cleanup:OSError"])
    result = tx.promote_initial_elements(**valid_inputs(tx, (created,)))
    assert result.status is MutationStatus.APPLIED
    assert result.reason == "PROMOTED_CLEANUP_DEFERRED"
    assert result.provenance["cleanup"]["status"] == "DEFERRED"
    assert tx.canonical == (existing, created)


def test_promotion_never_touches_applied_replay_bookkeeping():
    tx = ArchiTransaction(())
    before = set(tx._applied)
    tx.promote_initial_elements(**valid_inputs(tx, (element("created"),)))
    assert tx._applied == before == set()


def test_result_preserves_validation_and_sufficiency_evidence():
    tx = ArchiTransaction(())
    args = valid_inputs(tx, (element("created"),))
    result = tx.promote_initial_elements(**args)
    assert result.structural_validation is args["structural_validation"]
    assert result.sufficiency_snapshot is args["sufficiency_snapshot"]


def test_human_authority_is_propagated_to_publication_provenance():
    tx = ArchiTransaction(())
    result = tx.promote_initial_elements(**valid_inputs(tx, (element("created"),)))
    assert result.provenance["promotion"]["human_authority_ref"] == {
        "actor_id": "Yvan",
        "decision_context": "ARCHI_PROMOTE_INITIAL_ELEMENTS",
        "recorded_at_iso": "2026-09-29T12:01:00Z",
        "reference": "review-1",
    }


def test_project_id_and_merged_candidate_reach_single_publisher(monkeypatch):
    existing = element("existing")
    created = element("created")
    tx = ArchiTransaction((existing,))
    calls = []
    original = tx._publish_candidate

    def counted(**kwargs):
        calls.append(kwargs)
        return original(**kwargs)

    monkeypatch.setattr(tx, "_publish_candidate", counted)
    result = tx.promote_initial_elements(**valid_inputs(tx, (created,)))
    assert result.status is MutationStatus.APPLIED
    assert len(calls) == 1
    assert calls[0]["project_id"] == "P"
    assert calls[0]["candidate"] == (existing, created)


def test_promotion_does_not_require_or_create_archi_mutation():
    tx = ArchiTransaction(())
    result = tx.promote_initial_elements(**valid_inputs(tx, (element("created"),)))
    assert result.proposal_id == "proposal-1"
    assert not hasattr(result, "mutation_id")
