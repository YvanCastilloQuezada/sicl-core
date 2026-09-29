"""Structural creation validation for D-2.

Validates relational invariants of a batch of new ArchiElement before
A-002 sufficiency and publication. Does NOT duplicate validations already
enforced by ArchiElement.__post_init__, ProfileSpec.__post_init__, or
ArchiGeometry.__post_init__.

Structural validity is a precondition for A-002 evaluation. It is not itself
an epistemic sufficiency judgment.

Referential integrity is delegated to the shared D-2 integrity validator.
"""
from __future__ import annotations

from dataclasses import dataclass

from .model import ArchiElement
from .integrity import validate_references


@dataclass(frozen=True)
class StructuralValidationResult:
    valid: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


def validate_creation(
    *,
    project_id: str,
    candidate_elements: tuple[ArchiElement, ...],
    existing_canonical: tuple[ArchiElement, ...],
) -> StructuralValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if not candidate_elements:
        return StructuralValidationResult(False, ("CANDIDATE_ELEMENTS_EMPTY",))

    for index, element in enumerate(candidate_elements):
        if not isinstance(element, ArchiElement):
            errors.append(f"CANDIDATE_NOT_ARCHIELEMENT@{index}")
    if errors:
        return StructuralValidationResult(False, tuple(errors))

    for element in candidate_elements:
        if element.project_id != project_id:
            errors.append(f"PROJECT_ID_MISMATCH:{element.element_id.value}")

    seen_ids = set()
    for element in candidate_elements:
        element_id = element.element_id
        if element_id in seen_ids:
            errors.append(f"DUPLICATE_ELEMENT_ID_IN_BATCH:{element_id.value}")
        seen_ids.add(element_id)

    canonical_ids = {element.element_id for element in existing_canonical}
    for element in candidate_elements:
        if element.element_id in canonical_ids:
            errors.append(f"ELEMENT_ID_COLLIDES_WITH_CANONICAL:{element.element_id.value}")

    for element in candidate_elements:
        if element.properties.get("canonical") is True:
            errors.append(f"PROPERTIES_DECLARE_CANONICAL_TRUE:{element.element_id.value}")
        if not element.provenance:
            errors.append(f"PROVENANCE_MISSING:{element.element_id.value}")

    known_ids = seen_ids | canonical_ids
    errors.extend(validate_references(tuple(candidate_elements), known_ids=known_ids))

    return StructuralValidationResult(
        valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


__all__ = ["StructuralValidationResult", "validate_creation"]
