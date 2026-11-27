"""
UCG Canonical Identity Policy — R1

Strict validation of canonical semantic identity text.

This module does not normalize, transliterate, execute, register,
resolve, or generate commands.

Allowed alphabet:
    A-Z, Ñ, 0-9, ASCII SPACE

Canonical text must already be uppercase and correctly spaced.
"""

import re


CANONICAL_POLICY_VERSION = "UCG-CANONICAL-POLICY-R1"

CANONICAL_PATTERN = re.compile(
    r"[A-ZÑ0-9]+(?: [A-ZÑ0-9]+)*",
    flags=re.ASCII,
)


class CanonicalTextError(ValueError):
    """Raised when text violates the canonical identity policy."""


def validate_canonical_text(value: object) -> str:
    """
    Validate canonical text without modifying it.

    Returns the original string only when it is already canonical.
    Never silently repairs invalid identity text.
    """
    if type(value) is not str:
        raise CanonicalTextError("TYPE_NOT_EXACT_STR")

    if value == "":
        raise CanonicalTextError("EMPTY_VALUE")

    if CANONICAL_PATTERN.fullmatch(value) is None:
        raise CanonicalTextError("NON_CANONICAL_TEXT")

    return value


def is_canonical_text(value: object) -> bool:
    """Return True only for an exact canonical string."""
    try:
        validate_canonical_text(value)
    except CanonicalTextError:
        return False
    return True
