from __future__ import annotations

import pytest

from sicl.derivation import DerivationRecord, TypedRelation, VersionedRef
from sicl.h005.contract import ActionNotEligibleError, eligible_for_automatic_recomputation
from sicl.h005.registry import AmbiguousHandlerError, HandlerNotRegisteredError, RecomputationRegistry
from sicl.reaction import ActionStatus, ActionType, PlannedAction


def action(action_type=ActionType.RECOMPUTE, status=ActionStatus.PLANNED, authority=False):
    return PlannedAction(VersionedRef("Area", "A", 1), action_type, status, 0, "test", authority)


def test_only_planned_recompute_without_authority_is_eligible():
    assert eligible_for_automatic_recomputation(action()) is True
    assert eligible_for_automatic_recomputation(action(ActionType.REVIEW, ActionStatus.REQUIRES_AUTHORITY, True)) is False
    assert eligible_for_automatic_recomputation(action(ActionType.REJECT, ActionStatus.REQUIRES_AUTHORITY, True)) is False
    assert eligible_for_automatic_recomputation(action(ActionType.ESCALATE, ActionStatus.BLOCKED, True)) is False
    assert eligible_for_automatic_recomputation(action(ActionType.RECOMPUTE, ActionStatus.REQUIRES_AUTHORITY, True)) is False


def test_candidate_rejects_forged_non_recompute_actions():
    with pytest.raises(ActionNotEligibleError):
        from sicl.h005.contract import RecomputationCandidate
        RecomputationCandidate.from_action(action(ActionType.REVIEW, ActionStatus.REQUIRES_AUTHORITY, True), method="m", method_version="1")


def test_registry_requires_explicit_handler_and_rejects_unknown():
    registry = RecomputationRegistry()
    with pytest.raises(HandlerNotRegisteredError, match="HANDLER_NOT_REGISTERED"):
        registry.resolve("m", "1")
    handler = lambda project, record, refs: record
    registry.register("m", "1", handler)
    assert registry.resolve("m", "1") is handler


def test_registry_rejects_ambiguous_handlers():
    registry = RecomputationRegistry()
    registry.register("m", "1", lambda project, record, refs: record)
    registry.register("m", "1", lambda project, record, refs: record)
    with pytest.raises(AmbiguousHandlerError, match="AMBIGUOUS_HANDLER"):
        registry.resolve("m", "1")


def test_registry_does_not_execute_registration_or_use_reflection():
    registry = RecomputationRegistry()
    called = []
    registry.register("m", "1", lambda *args: called.append(args))
    assert called == []
    assert registry.keys()[0].method == "m"
