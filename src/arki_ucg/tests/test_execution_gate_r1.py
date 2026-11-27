"""Execution Gate R1 tests. No real execution is performed."""
from dataclasses import replace

from arki_ucg.canonical_identity import create_canonical_identity
from arki_ucg.registry import CanonicalRegistry
from arki_ucg.resolver import CanonicalResolver
from arki_ucg.authorization import CanonicalAuthorization
from arki_ucg.execution_gate import CanonicalExecutionGate


def make_identity(seed="A"):
    return create_canonical_identity((
        "ARKI", "URBANISMO", "PLANIFICAR", "DISEÑAR",
        "CIUDAD", "SISTEMA", "BASE", seed,
    ))


def build_chain(identity, grant=True):
    registry = CanonicalRegistry()
    registry.register(identity)
    resolver = CanonicalResolver(registry)
    resolution = resolver.resolve(identity)
    authorization = CanonicalAuthorization()
    if grant:
        authorization.grant(identity)
    auth_result = authorization.authorize(identity, resolution)
    return resolution, auth_result


def test_permit_decision_when_all_gates_pass():
    identity = make_identity()
    resolution, auth_result = build_chain(identity)
    gate = CanonicalExecutionGate()

    result = gate.evaluate(identity, resolution, auth_result)

    assert result.permitted
    assert result.code == "GATE_PERMIT_DECISION_ONLY"
    assert result.fingerprint == identity.fingerprint


def test_denies_without_authorization():
    identity = make_identity()
    resolution, auth_result = build_chain(identity, grant=False)

    result = CanonicalExecutionGate().evaluate(identity, resolution, auth_result)

    assert not result.permitted
    assert result.code == "GATE_AUTHORIZATION_DENIED"


def test_denies_missing_resolution():
    identity = make_identity()
    resolution, auth_result = build_chain(identity)
    result = CanonicalExecutionGate().evaluate(identity, None, auth_result)

    assert not result.permitted
    assert result.code == "GATE_RESOLUTION_DENIED"


def test_denies_invalid_identity():
    identity = replace(make_identity(), fingerprint="0" * 64)
    resolution, auth_result = build_chain(make_identity())

    result = CanonicalExecutionGate().evaluate(identity, resolution, auth_result)

    assert not result.permitted
    assert result.code == "GATE_IDENTITY_INVALID"


def test_denies_resolution_identity_mismatch():
    identity = make_identity("A")
    other = make_identity("B")
    resolution, auth_result = build_chain(other)

    result = CanonicalExecutionGate().evaluate(identity, resolution, auth_result)

    assert not result.permitted
    assert result.code == "GATE_IDENTITY_MISMATCH"


def test_denies_authorization_mismatch():
    identity = make_identity()
    resolution, _ = build_chain(identity)
    other_auth = CanonicalAuthorization()
    denied = other_auth.authorize(identity, resolution)

    result = CanonicalExecutionGate().evaluate(identity, resolution, denied)

    assert not result.permitted
    assert result.code == "GATE_AUTHORIZATION_DENIED"


def test_gate_is_decision_only():
    identity = make_identity()
    resolution, auth_result = build_chain(identity)
    gate = CanonicalExecutionGate()

    result = gate.evaluate(identity, resolution, auth_result)

    # Gate has no execution method and does not mutate the registry.
    assert result.permitted
    assert not hasattr(gate, "execute")
    assert not hasattr(gate, "run")


def test_gate_result_is_immutable():
    identity = make_identity()
    resolution, auth_result = build_chain(identity)
    result = CanonicalExecutionGate().evaluate(
        identity, resolution, auth_result
    )

    try:
        result.permitted = False
    except AttributeError:
        pass
    else:
        raise AssertionError("ExecutionGateResult must be immutable")
