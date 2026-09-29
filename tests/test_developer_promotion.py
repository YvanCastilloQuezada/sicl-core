import copy
from types import SimpleNamespace

import pytest

import sicl.developer_promotion as dp
from sicl.archi.identity import ArchiElementId
from sicl.archi.model import ArchiElement, ArchiGeometry, ElementKind, GeometryKind, ProfileSpec
from sicl.archi.transaction import MutationLifecycle, MutationStatus, PromotionResult
from sicl.derivation import DerivationLedger
from sicl.domain import Event, HumanReview, Project, now_iso
from sicl.repository import SQLiteRepository


FP = "a" * 64
PROJECT = "P"
PROPOSAL = "dev-prop-1"
REVIEW = "review-1"


def geometry():
    return {
        "kind": "EXTRUDED_RECTANGLE",
        "profile": {"width_mm": 4000, "depth_mm": 3000, "radius_mm": None},
        "x_mm": 0, "y_mm": 0, "z_mm": 0, "height_mm": 2800,
    }


def proposal(**overrides):
    value = {
        "proposalId": PROPOSAL,
        "parentProposalId": None,
        "sourceExecutionId": "d63-exec",
        "sourceD63": "D63-A",
        "fingerprint": FP,
        "epistemicStatus": "PROPOSAL",
        "proposedElements": [{
            "provisionalId": "space-1",
            "kind": "SPACE",
            "geometry": geometry(),
            "properties": {"name": "Space"},
            "provenance": [{"source": "test", "ref": "D63-A"}],
            "epistemicStatus": "HYPOTHESIS",
        }],
        "proposedRelations": [],
        "proposedDerivations": [],
        "unresolvedUnknowns": [],
        "requiredHumanActions": [{"action": "review", "reason": "required"}],
        "provenance": [{"source": "test", "ref": "proposal"}],
        "reviewRequired": True,
        "mutation": None,
        "rejectedBecause": None,
        "feedbackLoops": [],
    }
    value.update(overrides)
    return value


def setup_repo(*, payload=None, execution_fp=FP, review_status="APPROVED", bind_fp=FP):
    repo = SQLiteRepository()
    repo.insert_project(Project(PROJECT, "Promotion"), Event(None, now_iso(), PROJECT, "PROJECT_CREATED", {}, "test", "TEST"))
    repo.add_event(Event(None, now_iso(), PROJECT, "REASONING_EXECUTION_RECORDED", {
        "execution": {
            "execution_id": PROPOSAL,
            "kind": "DEVELOPER_PROPOSAL",
            "fingerprint": execution_fp,
            "payload": proposal() if payload is None else payload,
        }
    }, "developer", "TEST"))
    review = HumanReview(
        REVIEW, PROJECT, "architect", "2026-09-29T12:00:00Z", "Approved", "reviewed",
        "PRODUCT_OWNER", review_status, 1, "DEVELOPER_PROPOSAL", PROPOSAL, bind_fp,
    )
    project = repo.get_project(PROJECT)
    project.human_reviews[REVIEW] = review
    project.version += 1
    repo.insert_entity_and_event(
        """INSERT INTO human_reviews(
            review_id, project_id, actor, timestamp, review, reason, authority, status, version,
            referenced_entity_type, referenced_entity_id, referenced_fingerprint
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (review.review_id, review.project_id, review.actor, review.timestamp, review.review,
         review.reason, review.authority, review.status, review.version,
         review.referenced_entity_type, review.referenced_entity_id, review.referenced_fingerprint),
        project, Event(None, now_iso(), PROJECT, "HUMAN_REVIEW_RECORDED", {}, "architect", "TEST"),
    )
    return repo


def run(repo, **overrides):
    args = dict(repo=repo, project_id=PROJECT, proposal_id=PROPOSAL,
                proposal_fingerprint=FP, human_review_id=REVIEW,
                ledger=DerivationLedger(repo))
    args.update(overrides)
    return dp.promote_developer_proposal(**args)


def reasons(repo, event_type="DEVELOPER_PROMOTION_REJECTED"):
    return [e.payload.get("reason") for e in repo.events(PROJECT) if e.type == event_type]


def test_project_not_found_has_no_snapshot():
    repo = SQLiteRepository()
    out = run(repo)
    assert (out.committed, out.reason) == (False, "PROJECT_NOT_FOUND")
    assert repo.get_d2(PROJECT) is None


def test_proposal_not_found():
    repo = setup_repo()
    out = run(repo, proposal_id="missing-proposal")
    assert out.reason == "PROPOSAL_NOT_FOUND"
    assert "PROPOSAL_NOT_FOUND" in reasons(repo)


def test_request_execution_fingerprint_mismatch():
    repo = setup_repo(execution_fp="b" * 64)
    assert run(repo).reason == "PROPOSAL_FINGERPRINT_MISMATCH"


def test_invalid_schema():
    bad = proposal()
    bad.pop("sourceD63")
    repo = setup_repo(payload=bad)
    assert run(repo).reason == "INVALID_DEVELOPER_PROPOSAL"


def test_execution_payload_fingerprint_inconsistent():
    bad = proposal(fingerprint="b" * 64)
    repo = setup_repo(payload=bad)
    assert run(repo).reason == "PROPOSAL_FINGERPRINT_INCONSISTENT"


def test_human_review_not_found():
    repo = setup_repo()
    repo.conn.execute("DELETE FROM human_reviews")
    repo.conn.commit()
    assert run(repo).reason == "HUMAN_REVIEW_NOT_FOUND"


def test_review_binding_mismatch():
    repo = setup_repo(bind_fp="b" * 64)
    assert run(repo).reason == "HUMAN_REVIEW_BINDING_MISMATCH"


def test_review_not_approved():
    repo = setup_repo(review_status="REJECTED")
    assert run(repo).reason == "HUMAN_REVIEW_BINDING_MISMATCH"


def test_relations_fail_closed():
    bad = proposal(proposedRelations=[{
        "fromProvisionalId": "space-1", "toProvisionalId": "space-1",
        "relationKind": "ADJACENT", "provenance": [{"source": "x", "ref": "y"}],
    }])
    repo = setup_repo(payload=bad)
    assert run(repo).reason == "RELATIONS_NOT_YET_SUPPORTED"


def test_derivations_fail_closed():
    bad = proposal(proposedDerivations=[{
        "outputProvisionalId": "space-1", "inputsProvisionalIds": ["space-1"],
        "method": "x", "methodVersion": "1", "assumptions": [],
    }])
    repo = setup_repo(payload=bad)
    assert run(repo).reason == "DERIVATIONS_NOT_YET_SUPPORTED"


def test_unknown_element_kind():
    bad = proposal()
    bad["proposedElements"][0]["kind"] = "CIRCULATION"
    repo = setup_repo(payload=bad)
    assert run(repo).reason == "UNKNOWN_ELEMENT_KIND"


def test_missing_geometry():
    bad = proposal()
    bad["proposedElements"][0]["geometry"] = None
    repo = setup_repo(payload=bad)
    assert run(repo).reason == "MISSING_GEOMETRY"


def test_polygon_geometry_is_not_mapped():
    bad = proposal()
    bad["proposedElements"][0]["geometry"] = {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]}
    repo = setup_repo(payload=bad)
    assert run(repo).reason == "GEOMETRY_CONTRACT_NOT_MAPPED"


@pytest.mark.parametrize("key,value", [
    ("d63_labels", {"en": "space"}),
    ("bad_list", ["x"]),
])
def test_unsupported_property_values(key, value):
    bad = proposal()
    bad["proposedElements"][0]["properties"][key] = value
    repo = setup_repo(payload=bad)
    assert run(repo).reason == f"UNSUPPORTED_PROPERTY_VALUE:{key}"


def test_conversion_is_deterministic_and_preserves_provenance(monkeypatch):
    repo = setup_repo()
    captured = {}
    real = repo.insert_d2_snapshot_and_event
    def capture(project_id, elements, actor, source, **kwargs):
        captured["elements"] = elements
        return real(project_id, elements, actor, source, **kwargs)
    monkeypatch.setattr(repo, "insert_d2_snapshot_and_event", capture)
    out = run(repo)
    element = captured["elements"][0]
    assert element.element_id == ArchiElementId.compute(PROJECT, "SPACE", "space-1")
    assert element.provenance["developer_proposal"]["proposal_id"] == PROPOSAL
    assert element.provenance["developer_element"]["epistemic_status"] == "HYPOTHESIS"
    assert out.committed is True


def test_structural_validation_failure_is_rejected_without_snapshot(monkeypatch):
    repo = setup_repo()
    monkeypatch.setattr(
        dp,
        "validate_creation",
        lambda **kwargs: SimpleNamespace(valid=False, errors=("TEST_STRUCTURAL_FAILURE",)),
    )
    out = run(repo)
    assert (out.committed, out.effects_status, out.reason) == (
        False, "NOT_ATTEMPTED", "STRUCTURAL_VALIDATION_FAILED"
    )
    assert repo.get_d2(PROJECT) is None
    assert "STRUCTURAL_VALIDATION_FAILED" in reasons(repo)


def test_sufficiency_not_permitted_is_rejected_without_snapshot(monkeypatch):
    repo = setup_repo()
    monkeypatch.setattr(
        dp,
        "snapshot_for_creation",
        lambda **kwargs: SimpleNamespace(permits=False),
    )
    out = run(repo)
    assert (out.committed, out.effects_status, out.reason) == (
        False, "NOT_ATTEMPTED", "SUFFICIENCY_NOT_PERMITTED"
    )
    assert repo.get_d2(PROJECT) is None
    assert "SUFFICIENCY_NOT_PERMITTED" in reasons(repo)


def test_persist_failure_does_not_run_effects(monkeypatch):
    repo = setup_repo()
    called = {"effects": False}
    def fail(*args, **kwargs):
        raise RuntimeError("db")
    def effects(*args, **kwargs):
        called["effects"] = True
    monkeypatch.setattr(repo, "insert_d2_snapshot_and_event", fail)
    monkeypatch.setattr(dp.ArchiTransaction, "promote_initial_elements", effects)
    out = run(repo)
    assert (out.committed, out.effects_status, out.reason) == (False, "NOT_ATTEMPTED", "PROMOTION_PERSIST_FAILED")
    assert called["effects"] is False
    assert repo.get_d2(PROJECT) is None


def test_success_commits_d2_and_effects_complete():
    repo = setup_repo()
    before = repo.get_project(PROJECT).version
    out = run(repo)
    assert out.committed is True
    assert out.effects_status == "COMPLETE"
    assert repo.get_d2(PROJECT) == out.canonical
    assert repo.get_project(PROJECT).version == before
    committed = [e for e in repo.events(PROJECT) if e.type == "DEVELOPER_PROMOTION_COMMITTED"]
    assert len(committed) == 1
    assert committed[0].payload["snapshot_id"] == out.snapshot_id


def test_effect_exception_keeps_authoritative_d2(monkeypatch):
    repo = setup_repo()
    def fail(*args, **kwargs):
        raise RuntimeError("effects")
    monkeypatch.setattr(dp.ArchiTransaction, "promote_initial_elements", fail)
    out = run(repo)
    assert (out.committed, out.effects_status) == (True, "FAILED")
    assert repo.get_d2(PROJECT) == out.canonical
    assert any(e.type == "D2_EFFECTS_FAILED" for e in repo.events(PROJECT))


def test_effect_failed_result_keeps_authoritative_d2(monkeypatch):
    repo = setup_repo()
    def fail(self, **kwargs):
        return PromotionResult(PROPOSAL, MutationStatus.FAILED, MutationLifecycle.EVALUATED, (), reason="PUBLICATION")
    monkeypatch.setattr(dp.ArchiTransaction, "promote_initial_elements", fail)
    out = run(repo)
    assert out.committed is True and out.effects_status == "FAILED"
    assert repo.get_d2(PROJECT) == out.canonical


def test_cleanup_deferred_is_partial(monkeypatch):
    repo = setup_repo()
    real = dp.ArchiTransaction.promote_initial_elements
    def deferred(self, **kwargs):
        result = real(self, **kwargs)
        return PromotionResult(result.proposal_id, result.status, result.lifecycle, result.canonical,
                               result.candidate, "PROMOTED_CLEANUP_DEFERRED",
                               result.derivation_recorded, result.provenance,
                               result.structural_validation, result.sufficiency_snapshot)
    monkeypatch.setattr(dp.ArchiTransaction, "promote_initial_elements", deferred)
    assert run(repo).effects_status == "PARTIAL"


def test_internal_canonical_mismatch_is_audited(monkeypatch):
    repo = setup_repo()
    def mismatch(self, **kwargs):
        return PromotionResult(PROPOSAL, MutationStatus.APPLIED, MutationLifecycle.PUBLISHED, ())
    monkeypatch.setattr(dp.ArchiTransaction, "promote_initial_elements", mismatch)
    out = run(repo)
    assert out.committed is True and out.effects_status == "FAILED"
    assert out.reason == "CANONICAL_SNAPSHOT_MISMATCH"
    assert any(e.type == "D2_INTERNAL_INCONSISTENCY" for e in repo.events(PROJECT))


def test_rejection_never_creates_snapshot():
    bad = proposal()
    bad["proposedElements"][0]["geometry"] = None
    repo = setup_repo(payload=bad)
    before = repo.get_project(PROJECT).version
    run(repo)
    assert repo.get_d2(PROJECT) is None
    assert repo.get_project(PROJECT).version == before
    assert not any(e.type == "DEVELOPER_PROMOTION_COMMITTED" for e in repo.events(PROJECT))


def test_d2_version_advances_only_on_success():
    rejected = setup_repo(payload={**proposal(), "proposedElements": [{**proposal()["proposedElements"][0], "geometry": None}]})
    assert run(rejected).committed is False
    assert rejected.get_d2_history(PROJECT) == []
    successful = setup_repo()
    out = run(successful)
    assert out.d2_version == 1
    assert [row["version"] for row in successful.get_d2_history(PROJECT)] == [1]


def test_idempotent_replay_returns_same_snapshot_without_second_publication(monkeypatch):
    repo = setup_repo()
    first = run(repo)
    def forbidden(*args, **kwargs):
        raise AssertionError("effects must not replay")
    monkeypatch.setattr(dp.ArchiTransaction, "promote_initial_elements", forbidden)
    second = run(repo)
    assert second.committed is True
    assert second.snapshot_id == first.snapshot_id
    assert second.d2_version == first.d2_version
    assert second.reason == "ALREADY_COMMITTED"
    assert len([e for e in repo.events(PROJECT) if e.type == "DEVELOPER_PROMOTION_COMMITTED"]) == 1


def test_success_event_metadata_binds_proposal_review_and_snapshot():
    repo = setup_repo()
    out = run(repo)
    event = next(e for e in repo.events(PROJECT) if e.type == "DEVELOPER_PROMOTION_COMMITTED")
    assert event.payload["proposal_id"] == PROPOSAL
    assert event.payload["proposal_fingerprint"] == FP
    assert event.payload["human_review_id"] == REVIEW
    assert event.payload["snapshot_id"] == out.snapshot_id
    assert event.payload["version"] == out.d2_version
