from dataclasses import FrozenInstanceError

import pytest

from sicl.copilot_contract import CopilotIntent
from sicl.copilot_capabilities import (
    CAPABILITY_REGISTRY,
    CapabilityRisk,
    capabilities_for_intent,
    get_capability,
    plan_capability_route,
)


def test_registry_is_read_only_and_static():
    with pytest.raises(TypeError):
        CAPABILITY_REGISTRY["user.injected"] = object()
    with pytest.raises(FrozenInstanceError):
        get_capability("operation.execute").available = True


def test_execute_capability_is_unavailable_and_not_authorized():
    spec = get_capability("operation.execute")
    assert spec is not None
    assert spec.risk is CapabilityRisk.R4
    assert not spec.available
    route = plan_capability_route(CopilotIntent.EXECUTE)
    assert route["execution_authorized"] is False
    assert route["ready_for_orchestration"] == []


def test_ambiguous_intent_has_no_route():
    route = plan_capability_route(CopilotIntent.EXECUTE, ambiguous=True)
    assert route["status"] == "CLARIFICATION_REQUIRED"
    assert route["candidates"] == []


@pytest.mark.parametrize(
    "intent,capability_id",
    [
        (CopilotIntent.CONVERSE, "conversation.respond"),
        (CopilotIntent.RESEARCH, "research.search"),
        (CopilotIntent.EXPLORE, "analysis.explore"),
        (CopilotIntent.DESIGN_INTENT, "architecture.design"),
        (CopilotIntent.PREPARE_ACTION, "action.prepare"),
        (CopilotIntent.REVIEW, "review.inspect"),
    ],
)
def test_intent_has_expected_catalog_entry(intent, capability_id):
    assert capability_id in [s.capability_id for s in capabilities_for_intent(intent)]


def test_unknown_capability_is_not_found():
    assert get_capability("unknown.operation") is None


def test_mutation_capabilities_cannot_skip_confirmation():
    with pytest.raises(ValueError, match="bypass confirmation"):
        from sicl.copilot_capabilities import CapabilitySpec
        CapabilitySpec("unsafe", "1", "Unsafe", "test", (CopilotIntent.EXECUTE,),
                       CapabilityRisk.R3, available=True, requires_confirmation=False)
