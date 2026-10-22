"""Referential integrity validation for D-2.

Validates hosted_in / contained_in references against a known-id set.
Used across creation, mutation, rehydration, and IFC export boundaries.
"""
from __future__ import annotations

from .identity import ArchiElementId
from .model import ArchiElement


class ReferentialIntegrityError(ValueError):
    """Raised when a D-2 boundary receives elements with invalid references."""


def validate_references(
    elements: tuple[ArchiElement, ...],
    known_ids: set[ArchiElementId] | None = None,
) -> tuple[str, ...]:
    """Return deterministic diagnostics for invalid hosted/contained references."""
    if known_ids is None:
        known_ids = {element.element_id for element in elements}

    errors: list[str] = []
    for element in elements:
        element_id = element.element_id
        if element.hosted_in is not None:
            if element.hosted_in == element_id:
                errors.append(f"SELF_HOSTED_IN:{element_id.value}")
            elif element.hosted_in not in known_ids:
                errors.append(f"ORPHAN_HOSTED_IN:{element_id.value}->{element.hosted_in.value}")
        if element.contained_in is not None:
            if element.contained_in == element_id:
                errors.append(f"SELF_CONTAINED_IN:{element_id.value}")
            elif element.contained_in not in known_ids:
                errors.append(f"ORPHAN_CONTAINED_IN:{element_id.value}->{element.contained_in.value}")
    return tuple(errors)


__all__ = ["ReferentialIntegrityError", "validate_references"]
