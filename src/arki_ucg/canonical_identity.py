"""
UCG Canonical Semantic Identity — R1.

Strict identity snapshot for exactly eight canonical semantic levels.
This module is isolated from legacy normalization and execution systems.
Fingerprints provide integrity checking, not authentication.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
from typing import Tuple

from .model import ValidationIssue, ValidationResult
from .canonical_policy import (
    validate_canonical_text,
    CanonicalTextError,
)

CANONICAL_IDENTITY_CONTRACT_VERSION = "UCG-CANONICAL-IDENTITY-R1"
FINGERPRINT_CONTRACT_VERSION = "UCG-FINGERPRINT-R1"
IDENTITY_LEVEL_COUNT = 8


@dataclass(frozen=True)
class CanonicalSemanticIdentity:
    """Immutable canonical snapshot of L1-L8; not an authorization token."""

    levels: Tuple[str, ...]
    contract_version: str
    fingerprint_version: str
    fingerprint: str


def _validate_levels(levels: object) -> Tuple[str, ...]:
    if type(levels) is not tuple:
        raise ValueError("IDENTITY_LEVELS_CONTAINER_INVALID")

    if len(levels) != IDENTITY_LEVEL_COUNT:
        raise ValueError("IDENTITY_LEVELS_SHAPE_INVALID")

    validated = []

    for index, level in enumerate(levels, start=1):
        try:
            validated.append(validate_canonical_text(level))
        except CanonicalTextError as exc:
            raise ValueError(
                f"IDENTITY_LEVEL_{index}_INVALID:{exc}"
            ) from exc

    return tuple(validated)


def _fingerprint_payload(
    levels: Tuple[str, ...],
    contract_version: str,
    fingerprint_version: str,
) -> dict:
    return {
        "levels": list(levels),
        "contract_version": contract_version,
        "fingerprint_version": fingerprint_version,
    }


def _compute_fingerprint(
    levels: Tuple[str, ...],
    contract_version: str,
    fingerprint_version: str,
) -> str:
    payload = _fingerprint_payload(
        levels,
        contract_version,
        fingerprint_version,
    )

    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def create_canonical_identity(
    levels: Tuple[str, ...],
) -> CanonicalSemanticIdentity:
    """Create identity from an already-canonical tuple; never normalizes."""

    canonical_levels = _validate_levels(levels)

    fingerprint = _compute_fingerprint(
        canonical_levels,
        CANONICAL_IDENTITY_CONTRACT_VERSION,
        FINGERPRINT_CONTRACT_VERSION,
    )

    return CanonicalSemanticIdentity(
        levels=canonical_levels,
        contract_version=CANONICAL_IDENTITY_CONTRACT_VERSION,
        fingerprint_version=FINGERPRINT_CONTRACT_VERSION,
        fingerprint=fingerprint,
    )


def verify_canonical_identity(
    identity: object,
) -> ValidationResult:
    """Fail-closed verification of type, versions, canonical levels and hash."""

    if type(identity) is not CanonicalSemanticIdentity:
        return ValidationResult.failure(
            ValidationIssue(
                code="CANONICAL_IDENTITY_TYPE_INVALID",
                message="Expected exact CanonicalSemanticIdentity type.",
            )
        )

    issues = []

    if type(identity.contract_version) is not str:
        issues.append(
            ValidationIssue(
                code="CANONICAL_CONTRACT_VERSION_TYPE_INVALID",
                message="Contract version must be an exact string.",
            )
        )
    elif identity.contract_version != CANONICAL_IDENTITY_CONTRACT_VERSION:
        issues.append(
            ValidationIssue(
                code="CANONICAL_CONTRACT_VERSION_UNSUPPORTED",
                message="Canonical identity contract version is unsupported.",
            )
        )

    if type(identity.fingerprint_version) is not str:
        issues.append(
            ValidationIssue(
                code="FINGERPRINT_VERSION_TYPE_INVALID",
                message="Fingerprint version must be an exact string.",
            )
        )
    elif identity.fingerprint_version != FINGERPRINT_CONTRACT_VERSION:
        issues.append(
            ValidationIssue(
                code="FINGERPRINT_VERSION_UNSUPPORTED",
                message="Fingerprint version is unsupported.",
            )
        )

    if issues:
        return ValidationResult.failure(*issues)

    try:
        levels = _validate_levels(identity.levels)
    except ValueError as exc:
        return ValidationResult.failure(
            ValidationIssue(
                code="CANONICAL_LEVELS_INVALID",
                message=str(exc),
            )
        )

    if type(identity.fingerprint) is not str:
        return ValidationResult.failure(
            ValidationIssue(
                code="CANONICAL_FINGERPRINT_TYPE_INVALID",
                message="Fingerprint must be an exact string.",
            )
        )

    try:
        expected = _compute_fingerprint(
            levels,
            identity.contract_version,
            identity.fingerprint_version,
        )

        matches = hmac.compare_digest(
            identity.fingerprint,
            expected,
        )
    except Exception:
        matches = False

    if not matches:
        return ValidationResult.failure(
            ValidationIssue(
                code="CANONICAL_FINGERPRINT_MISMATCH",
                message="Fingerprint does not match canonical identity payload.",
            )
        )

    return ValidationResult.success()
