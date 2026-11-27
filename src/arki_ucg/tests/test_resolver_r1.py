"""Resolver R1 functional tests."""
from dataclasses import replace

from arki_ucg.canonical_identity import create_canonical_identity
from arki_ucg.registry import CanonicalRegistry
from arki_ucg.resolver import CanonicalResolver


def make_identity(seed="A"):
    return create_canonical_identity((
        "ARKI",
        "URBANISMO",
        "PLANIFICAR",
        "DISEÑAR",
        "CIUDAD",
        "SISTEMA",
        "BASE",
        seed,
    ))


def make_resolver():
    registry = CanonicalRegistry()
    return registry, CanonicalResolver(registry)


def test_resolve_registered_identity_exactly():
    registry, resolver = make_resolver()
    identity = make_identity()
    registered = registry.register(identity)

    result = resolver.resolve(identity)

    assert registered.accepted
    assert result.resolved
    assert result.code == "RESOLVER_EXACT_MATCH"
    assert result.entry == registered.entry


def test_unregistered_identity_not_found():
    registry, resolver = make_resolver()
    identity = make_identity("B")

    result = resolver.resolve(identity)

    assert not result.resolved
    assert result.code == "RESOLVER_NOT_FOUND"
    assert len(registry) == 0


def test_invalid_fingerprint_rejected():
    _, resolver = make_resolver()
    forged = replace(make_identity(), fingerprint="0" * 64)

    result = resolver.resolve(forged)

    assert not result.resolved
    assert result.code == "RESOLVER_IDENTITY_INVALID"


def test_resolver_does_not_register():
    registry, resolver = make_resolver()
    identity = make_identity()

    resolver.resolve(identity)

    assert len(registry) == 0


def test_resolve_distinct_registered_identity():
    registry, resolver = make_resolver()
    first = make_identity("A")
    second = make_identity("B")

    registry.register(first)
    registry.register(second)

    result = resolver.resolve(second)

    assert result.resolved
    assert result.entry.levels == second.levels


def test_exact_lookup_no_fuzzy_match():
    registry, resolver = make_resolver()
    registered = make_identity("A")
    near_but_distinct = make_identity("B")

    registry.register(registered)

    result = resolver.resolve(near_but_distinct)

    assert not result.resolved
    assert result.code == "RESOLVER_NOT_FOUND"


def test_result_is_immutable():
    _, resolver = make_resolver()
    result = resolver.resolve(make_identity())

    try:
        result.resolved = True
    except AttributeError:
        pass
    else:
        raise AssertionError("ResolverResult must be immutable")
