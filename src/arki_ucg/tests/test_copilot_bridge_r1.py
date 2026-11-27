"""Copilot Bridge R1 tests: decision contract only."""
from dataclasses import replace

from arki_ucg.canonical_identity import create_canonical_identity
from arki_ucg.pipeline import CanonicalPipeline
from arki_ucg.copilot_bridge import (
    CanonicalCopilotBridge,
    COPILOT_BRIDGE_CONTRACT_VERSION,
)


def make_identity(seed="A"):
    return create_canonical_identity((
        "ARKI", "URBANISMO", "PLANIFICAR", "DISEÑAR",
        "CIUDAD", "SISTEMA", "BASE", seed,
    ))


def configured_bridge(identity):
    pipeline = CanonicalPipeline()
    pipeline.register(identity)
    pipeline.grant(identity)
    return CanonicalCopilotBridge(pipeline)


def test_bridge_denies_identity_not_registered():
    identity = make_identity()
    bridge = CanonicalCopilotBridge(CanonicalPipeline())

    result = bridge.evaluate_identity(identity)

    assert result.accepted
    assert result.decision == "DENY"
    assert result.code == "GATE_RESOLUTION_DENIED"


def test_bridge_permit_decision_only():
    identity = make_identity()
    bridge = configured_bridge(identity)

    result = bridge.evaluate_identity(identity)

    assert result.accepted
    assert result.decision == "PERMIT_DECISION_ONLY"
    assert result.code == "BRIDGE_DECISION_PERMIT"
    assert result.fingerprint == identity.fingerprint


def test_bridge_denies_when_registered_without_grant():
    identity = make_identity()
    pipeline = CanonicalPipeline()
    pipeline.register(identity)
    bridge = CanonicalCopilotBridge(pipeline)

    result = bridge.evaluate_identity(identity)

    assert result.decision == "DENY"
    assert result.code == "GATE_AUTHORIZATION_DENIED"


def test_bridge_rejects_forged_identity():
    identity = replace(make_identity(), fingerprint="0" * 64)
    bridge = CanonicalCopilotBridge(CanonicalPipeline())

    result = bridge.evaluate_identity(identity)

    assert not result.accepted
    assert result.decision == "DENY"
    assert result.code == "BRIDGE_IDENTITY_INVALID"


def test_bridge_denies_missing_pipeline():
    result = CanonicalCopilotBridge(None).evaluate_identity(make_identity())

    assert not result.accepted
    assert result.decision == "DENY"
    assert result.code == "BRIDGE_PIPELINE_UNAVAILABLE"


def test_bridge_contract_version_is_stable():
    identity = make_identity()
    result = configured_bridge(identity).evaluate_identity(identity)

    assert result.contract_version == COPILOT_BRIDGE_CONTRACT_VERSION


def test_bridge_repeated_decisions_are_deterministic():
    identity = make_identity()
    bridge = configured_bridge(identity)

    first = bridge.evaluate_identity(identity)
    second = bridge.evaluate_identity(identity)

    assert first == second


def test_bridge_has_no_execution_capability():
    bridge = configured_bridge(make_identity())

    assert not hasattr(bridge, "execute")
    assert not hasattr(bridge, "run")
    assert not hasattr(bridge, "dispatch")
