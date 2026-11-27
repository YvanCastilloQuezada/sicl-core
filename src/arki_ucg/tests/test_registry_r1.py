"""Registry R1 functional tests."""
from dataclasses import replace

from arki_ucg.canonical_identity import create_canonical_identity
from arki_ucg.registry import CanonicalRegistry


def identity(seed="A"):
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


def test_register_valid_identity():
    registry = CanonicalRegistry()
    result = registry.register(identity())
    assert result.accepted
    assert result.code == "REGISTRY_REGISTERED"
    assert len(registry) == 1


def test_duplicate_fingerprint_rejected():
    registry = CanonicalRegistry()
    first = identity()
    second = create_canonical_identity(tuple(first.levels))

    assert registry.register(first).accepted
    duplicate = registry.register(second)

    assert not duplicate.accepted
    assert duplicate.code == "REGISTRY_DUPLICATE"
    assert len(registry) == 1


def test_invalid_identity_rejected():
    registry = CanonicalRegistry()
    valid = identity()
    forged = replace(valid, fingerprint="0" * 64)

    result = registry.register(forged)

    assert not result.accepted
    assert result.code == "REGISTRY_IDENTITY_INVALID"
    assert len(registry) == 0


def test_registry_exact_lookup():
    registry = CanonicalRegistry()
    item = identity()
    registered = registry.register(item)

    assert registered.accepted
    assert registry.get_by_fingerprint(item.fingerprint) == registered.entry
    assert registry.contains(item)


def test_unknown_lookup_returns_none():
    registry = CanonicalRegistry()
    assert registry.get_by_fingerprint("unknown") is None


def test_snapshot_is_tuple():
    registry = CanonicalRegistry()
    registry.register(identity())

    snapshot = registry.snapshot()
    assert type(snapshot) is tuple
    assert len(snapshot) == 1


def test_registry_does_not_normalize():
    registry = CanonicalRegistry()

    # Canonical identity creation rejects lowercase instead of repairing it.
    try:
        create_canonical_identity((
            "arki", "URBANISMO", "PLANIFICAR", "DISEÑAR",
            "CIUDAD", "SISTEMA", "BASE", "A",
        ))
    except ValueError:
        pass
    else:
        raise AssertionError("Noncanonical text must not be normalized")


def test_distinct_identity_registers():
    registry = CanonicalRegistry()

    first = identity("A")
    second = identity("B")

    assert registry.register(first).accepted
    assert registry.register(second).accepted
    assert len(registry) == 2


def test_non_string_lookup_rejected():
    registry = CanonicalRegistry()
    assert registry.get_by_fingerprint(None) is None
