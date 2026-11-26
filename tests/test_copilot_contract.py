import pytest

from sicl.copilot_contract import (
    ActionGateInput,
    CopilotIntent,
    CopilotFact,
    FactStatus,
    evaluate_action_gate,
)


def test_non_execute_intent_is_never_allowed():
    decision = evaluate_action_gate(ActionGateInput(
        intent=CopilotIntent.PREPARE_ACTION,
        explicit_execution_request=True,
        capability_available=True,
        inputs_validated=True,
        permission_granted=True,
        risk_policy_satisfied=True,
        confirmation_required=False,
    ))
    assert not decision.allowed
    assert "intent_is_not_execute" in decision.reasons


@pytest.mark.parametrize(
    "field,reason",
    [
        ("explicit_execution_request", "explicit_execution_request_missing"),
        ("capability_available", "capability_unavailable"),
        ("inputs_validated", "inputs_not_validated"),
        ("permission_granted", "permission_not_granted"),
        ("risk_policy_satisfied", "risk_policy_not_satisfied"),
    ],
)
def test_execution_gate_fails_closed_when_any_gate_is_missing(field, reason):
    values = dict(
        intent=CopilotIntent.EXECUTE,
        explicit_execution_request=True,
        capability_available=True,
        inputs_validated=True,
        permission_granted=True,
        risk_policy_satisfied=True,
        confirmation_required=False,
    )
    values[field] = False
    decision = evaluate_action_gate(ActionGateInput(**values))
    assert not decision.allowed
    assert reason in decision.reasons


def test_execution_requires_confirmation_when_policy_says_so():
    decision = evaluate_action_gate(ActionGateInput(
        intent=CopilotIntent.EXECUTE,
        explicit_execution_request=True,
        capability_available=True,
        inputs_validated=True,
        permission_granted=True,
        risk_policy_satisfied=True,
        confirmation_required=True,
        user_confirmed=False,
    ))
    assert not decision.allowed
    assert decision.reasons == ("user_confirmation_missing",)


def test_execution_allowed_only_when_all_gates_are_satisfied():
    decision = evaluate_action_gate(ActionGateInput(
        intent=CopilotIntent.EXECUTE,
        explicit_execution_request=True,
        capability_available=True,
        inputs_validated=True,
        permission_granted=True,
        risk_policy_satisfied=True,
        confirmation_required=True,
        user_confirmed=True,
    ))
    assert decision.allowed
    assert decision.reasons == ()


def test_missing_fact_cannot_smuggle_in_a_default_value():
    with pytest.raises(ValueError, match="must not carry a value"):
        CopilotFact(key="area_m2", value=20000, status=FactStatus.MISSING)


def test_proposed_fact_can_carry_value_but_is_not_confirmed():
    fact = CopilotFact(key="area_m2", value=20000, status=FactStatus.PROPOSED, source="copilot")
    assert fact.value == 20000
    assert fact.status is FactStatus.PROPOSED


def test_confidence_is_bounded():
    with pytest.raises(ValueError, match="between 0 and 1"):
        CopilotFact(key="typology", value="hospital", status=FactStatus.PROPOSED, confidence=1.5)
