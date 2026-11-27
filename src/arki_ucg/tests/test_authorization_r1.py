"""Authorization R1 tests: explicit grants only."""
from dataclasses import replace

from arki_ucg.canonical_identity import create_canonical_identity
from arki_ucg.registry import CanonicalRegistry
from arki_ucg.resolver import CanonicalResolver
from arki_ucg.authorization import CanonicalAuthorization


def make_identity(seed="A"):
    return create_canonical_identity((
        "ARKI", "URBANISMO", "PLANIFICAR", "DISEÑAR",
        "CIUDAD", "SISTEMA", "BASE", seed,
    ))


def resolved(identity):
    registry = CanonicalRegistry()
    registry.register(identity)
    return CanonicalResolver(registry).resolve(identity)


def test_denied_without_explicit_grant():
    identity = make_identity()
    auth = CanonicalAuthorization()
    assert auth.authorize(identity, resolved(identity)).code == "AUTH_DENIED"


def test_explicit_grant_allows_exact_identity():
    identity = make_identity()
    auth = CanonicalAuthorization()
    assert auth.grant(identity).authorized
    result = auth.authorize(identity, resolved(identity))
    assert result.authorized
    assert result.code == "AUTH_ALLOWED"


def test_grant_does_not_authorize_distinct_identity():
    first = make_identity("A")
    second = make_identity("B")
    auth = CanonicalAuthorization()
    auth.grant(first)
    assert auth.authorize(second, resolved(second)).code == "AUTH_DENIED"


def test_resolution_required():
    identity = make_identity()
    auth = CanonicalAuthorization()
    auth.grant(identity)
    result = auth.authorize(identity, None)
    assert not result.authorized
    assert result.code == "AUTH_RESOLUTION_REQUIRED"


def test_resolution_identity_mismatch_rejected():
    first = make_identity("A")
    second = make_identity("B")
    auth = CanonicalAuthorization()
    auth.grant(first)
    result = auth.authorize(first, resolved(second))
    assert not result.authorized
    assert result.code == "AUTH_RESOLUTION_MISMATCH"


def test_revoke_removes_grant():
    identity = make_identity()
    auth = CanonicalAuthorization()
    auth.grant(identity)
    assert auth.revoke(identity).authorized
    assert not auth.has_grant(identity)
    assert auth.authorize(identity, resolved(identity)).code == "AUTH_DENIED"


def test_revoke_unknown_grant():
    auth = CanonicalAuthorization()
    result = auth.revoke(make_identity())
    assert not result.authorized
    assert result.code == "AUTH_GRANT_NOT_FOUND"


def test_invalid_identity_cannot_be_granted():
    auth = CanonicalAuthorization()
    forged = replace(make_identity(), fingerprint="0" * 64)
    result = auth.grant(forged)
    assert not result.authorized
    assert result.code == "AUTH_IDENTITY_INVALID"
    assert len(auth) == 0


def test_grants_are_identity_specific_and_counted():
    auth = CanonicalAuthorization()
    first, second = make_identity("A"), make_identity("B")
    auth.grant(first)
    auth.grant(second)
    assert len(auth) == 2
    assert auth.has_grant(first)
    assert auth.has_grant(second)
