from types import SimpleNamespace

import pytest

from sicl.design_memory import direction_event, explain_design, project_memory, query_memory, replay


class FakeRepo:
    def __init__(self):
        self.project = SimpleNamespace(
            alternatives={"A": SimpleNamespace(alternative_id="A", project_id="P", name="A", description="base", parameters={}, status="GENERATED", version=1, source="fixture")},
            generated_alternatives={},
        )
        self._events = [
            SimpleNamespace(id=1, timestamp="2026-01-01T00:00:00Z", project_id="P", type="HUMAN_INTENT_CONFIRMED", actor="architect", source="intent", payload={"alternative_id": "A", "intent": {"statement": "preserve courtyard"}}),
            SimpleNamespace(id=2, timestamp="2026-01-01T00:01:00Z", project_id="P", type="DESIGN_OPERATION_APPLIED", actor="system", source="gdi", payload={"alternative_id": "A", "operation": "COURTYARD"}),
        ]
    def get_project(self, project_id):
        return self.project if project_id == "P" else None
    def events(self, project_id):
        return self._events


def test_projection_is_derived_and_replay_is_read_only():
    memory = project_memory(FakeRepo(), "P")
    assert memory["second_historical_ledger"] is False
    assert len(memory["history"]) == 2
    replayed = replay(memory, "A")
    assert replayed["mutates_project"] is False
    assert replayed["creates_decision"] is False


def test_explanation_uses_evidence_and_unknowns_are_explicit():
    explanation = explain_design(project_memory(FakeRepo(), "P"), "A")
    assert explanation["evidence_references"] == [1, 2]
    assert explanation["human_reason"] == "not recorded"
    assert explanation["decision_created"] is False


def test_queries_are_deterministic_and_direction_requires_human_actor():
    result = query_memory(project_memory(FakeRepo(), "P"), "HOW_DID_WE_GET_HERE")
    assert result["result_type"] == "history"
    event = direction_event("P", "A", "REJECTED_BY_HUMAN", "architect", "circulation is less clear")
    assert event["payload"]["reason_is_system_inferred"] is False
    with pytest.raises(ValueError, match="INVALID_DIRECTION_STATUS"):
        direction_event("P", "A", "REJECTED", "system", None)
