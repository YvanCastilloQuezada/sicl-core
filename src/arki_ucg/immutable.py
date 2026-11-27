"""
ARKI UCG — Immutable value infrastructure.

Provides recursive freezing, safe thawing and deterministic canonicalization.
No execution capability, command identity or registry behavior is implied.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from typing import Any


class ImmutableValueError(ValueError):
    """Raised when a value cannot be safely frozen or canonicalized."""


def _validate_scalar(value: Any) -> Any:
    # bool must be checked before int because bool subclasses int.
    if value is None or isinstance(value, (str, bool, int)):
        return value

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ImmutableValueError("Non-finite float is forbidden.")
        return value

    raise ImmutableValueError(
        f"Unsupported value type: {type(value).__name__}"
    )


def freeze(value: Any) -> Any:
    """
    Recursively freeze supported values.

    Mapping -> immutable mapping proxy
    list/tuple -> tuple
    set/frozenset -> frozenset

    Cycles are rejected. Shared non-cyclic references are permitted.
    """
    from types import MappingProxyType

    active: set[int] = set()

    def walk(item: Any) -> Any:
        if isinstance(item, Mapping):
            oid = id(item)
            if oid in active:
                raise ImmutableValueError("Cycle detected in mapping.")

            active.add(oid)
            try:
                frozen_items = {}
                for key, val in item.items():
                    if not isinstance(key, str):
                        raise ImmutableValueError(
                            "Mapping keys must be strings."
                        )
                    frozen_items[key] = walk(val)
                return MappingProxyType(frozen_items)
            finally:
                active.remove(oid)

        if isinstance(item, (list, tuple)):
            oid = id(item)
            if oid in active:
                raise ImmutableValueError("Cycle detected in sequence.")

            active.add(oid)
            try:
                return tuple(walk(v) for v in item)
            finally:
                active.remove(oid)

        if isinstance(item, (set, frozenset)):
            oid = id(item)
            if oid in active:
                raise ImmutableValueError("Cycle detected in set.")

            active.add(oid)
            try:
                frozen_values = [walk(v) for v in item]
                # Sets must remain hashable after freezing.
                try:
                    return frozenset(frozen_values)
                except TypeError as exc:
                    raise ImmutableValueError(
                        "Set contains non-hashable frozen values."
                    ) from exc
            finally:
                active.remove(oid)

        return _validate_scalar(item)

    return walk(value)


def thaw(value: Any) -> Any:
    """
    Convert frozen structures into independent JSON-compatible structures.
    Sets become deterministically ordered lists.
    """
    def walk(item: Any) -> Any:
        if isinstance(item, Mapping):
            return {key: walk(val) for key, val in item.items()}

        if isinstance(item, tuple):
            return [walk(v) for v in item]

        if isinstance(item, frozenset):
            values = [walk(v) for v in item]
            return sorted(values, key=canonical_json)

        return _validate_scalar(item)

    return walk(value)


def canonical_json(value: Any) -> str:
    """
    Deterministic JSON representation for supported frozen or raw values.
    """
    normalized = thaw(freeze(value))

    return json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def canonical_fingerprint_payload(value: Any) -> bytes:
    """
    Canonical UTF-8 payload suitable for downstream hashing.
    This function does not create command identity.
    """
    return canonical_json(value).encode("utf-8")
