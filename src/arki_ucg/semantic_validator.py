"""
ARKI UCG-CHAR-01 — Experimental semantic field validator.

This module validates semantic text fields separately from normalization.
It does not create command IDs, resolve identity, access a Registry,
grant capabilities, or authorize execution.
"""

from __future__ import annotations

import unicodedata
from typing import Optional

from .model import (
    LEVELS,
    CommandDefinition,
    ValidationIssue,
    ValidationResult,
    validate_definition,
)
from .normalization import NormalizationError, normalize_semantic_text


CHAR_POLICY_CONTRACT = "UCG-CHAR-01-EXPERIMENTAL"

REJECT_CATEGORIES = frozenset({
    "Cc", "Cf", "Cs", "Co", "Cn", "Zl", "Zp", "Me",
})


def validate_semantic_text(
    value: str,
    level: Optional[str] = None,
) -> ValidationResult:
    """
    Validate one required semantic field.

    Policy:
    - Input must be str.
    - Reject Cc, Cf, Cs, Co, Cn, Zl, Zp and Me.
    - Apply UCG-NORM-02.
    - Reject empty output.
    - Reject leading Mn after normalization.
    - Preserve attached Mn and Mc provisionally.
    - Preserve symbols (S*) without deciding identity equivalence.

    Mn handling is deliberately conservative and is not a complete
    Unicode grapheme or linguistic validation algorithm.
    """
    if not isinstance(value, str):
        return ValidationResult.failure(
            ValidationIssue(
                code="SEMANTIC_TEXT_TYPE_INVALID",
                message="Semantic field must be a string.",
                level=level,
            )
        )

    for char in value:
        category = unicodedata.category(char)

        if category in REJECT_CATEGORIES:
            return ValidationResult.failure(
                ValidationIssue(
                    code="SEMANTIC_UNICODE_CATEGORY_FORBIDDEN",
                message=(
                    f"Forbidden Unicode category {category} "
                    f"(U+{ord(char):04X})."
                ),
                level=level,
                )
            )

    try:
        normalized = normalize_semantic_text(value)
    except NormalizationError as exc:
        return ValidationResult.failure(
            ValidationIssue(
                code="SEMANTIC_NORMALIZATION_REJECTED",
                message=str(exc),
                level=level,
            )
        )

    if not normalized:
        return ValidationResult.failure(
            ValidationIssue(
                code="SEMANTIC_FIELD_EMPTY_AFTER_NORMALIZATION",
                message="Required semantic field is empty after normalization.",
                level=level,
            )
        )

    first_category = unicodedata.category(normalized[0])

    if first_category == "Mn":
        return ValidationResult.failure(
            ValidationIssue(
                code="SEMANTIC_COMBINING_MARK_LEADING",
                message="A semantic field cannot begin with a Mn combining mark.",
                level=level,
            )
        )

    return ValidationResult.success()


def validate_command_semantics(
    definition: CommandDefinition,
) -> ValidationResult:
    """
    Validate structure and all eight semantic levels independently.

    Structural issues are preserved. Semantic diagnostics are not
    suppressed by structural failures. This function does not generate
    identity, resolve commands, access Registry or authorize execution.
    """
    structural = validate_definition(definition)
    issues = list(structural.issues)

    for level in LEVELS:
        value = getattr(definition, level, None)
        result = validate_semantic_text(value, level=level)

        if not result.valid:
            issues.extend(result.issues)

    if issues:
        return ValidationResult.failure(*issues)

    return ValidationResult.success()
