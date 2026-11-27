"""UCG Pipeline R1 tests. No real execution is performed."""
from dataclasses import replace

from arki_ucg.canonical_identity import create_canonical_identity
from arki_ucg.pipeline import CanonicalPipeline


def make_identity(seed="A"):
    return create_canonical_identity((
        "ARKI", "URBANISMO", "PLANIFICAR", "DISEÑAR",
        "CIUDAD", "SISTEMA", "BASE", seed,
    ))


def test_pipeline_denies_unregistered_identity():
    pipeline = CanonicalPipeline()
    identity = make_identity()

    result = pipeline.evaluate(identity)

    assert not result.permitted
    assert result.code == "GATE_RESOLUTION_DENIED"


def test_pipeline_denies_registered_without_grant():
    pipeline = CanonicalPipeline()
    identity = make_identity()

    assert pipeline.register(identity).accepted

    result = pipeline.evaluate(identity)

    assert not result.permitted
    assert result.code == "GATE_AUTHORIZATION_DENIED"


def test_pipeline_permits_decision_after_register_and_grant():
    pipeline = CanonicalPipeline()
    identity = make_identity()

    assert pipeline.register(identity).accepted
    assert pipeline.grant(identity).authorized

    result = pipeline.evaluate(identity)

    assert result.permitted
    assert result.code == "GATE_PERMIT_DECISION_ONLY"
    assert result.resolution.resolved
    assert result.authorization.authorized
    assert result.gate.permitted


def test_pipeline_revoke_blocks_future_decisions():
    pipeline = CanonicalPipeline()
    identity = make_identity()

    pipeline.register(identity)
    pipeline.grant(identity)
    assert pipeline.evaluate(identity).permitted

    assert pipeline.revoke(identity).authorized

    result = pipeline.evaluate(identity)

    assert not result.permitted
    assert result.code == "GATE_AUTHORIZATION_DENIED"


def test_pipeline_does_not_grant_automatically_on_register():
    pipeline = CanonicalPipeline()
    identity = make_identity()

    pipeline.register(identity)

    assert not pipeline.authorization.has_grant(identity)
    assert not pipeline.evaluate(identity).permitted


def test_pipeline_identity_mismatch_is_denied():
    pipeline = CanonicalPipeline()
    first = make_identity("A")
    second = make_identity("B")

    pipeline.register(first)
    pipeline.grant(first)

    result = pipeline.evaluate(second)

    assert not result.permitted


def test_invalid_identity_fails_closed():
    pipeline = CanonicalPipeline()
    forged = replace(make_identity(), fingerprint="0" * 64)

    result = pipeline.evaluate(forged)

    assert not result.permitted
    assert result.code == "GATE_IDENTITY_INVALID"


def test_pipeline_repeated_evaluation_is_deterministic():
    pipeline = CanonicalPipeline()
    identity = make_identity()

    pipeline.register(identity)
    pipeline.grant(identity)

    first = pipeline.evaluate(identity)
    second = pipeline.evaluate(identity)

    assert first.permitted == second.permitted
    assert first.code == second.code
    assert first.resolution.entry == second.resolution.entry


def test_pipeline_has_no_execution_method():
    pipeline = CanonicalPipeline()

    assert not hasattr(pipeline, "execute")
    assert not hasattr(pipeline, "run")
