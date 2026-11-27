"""
UCG-VALIDATED-IDENTITY-01 — Validated semantic identity.

An identity is a validated, normalized snapshot of L1-L8.
It is not a command ID, capability, authorization or execution token.

Integrity fingerprints detect alteration. They are not cryptographic
authentication and do not prevent deliberate object forgery.
Consumers must verify and revalidate before relying on this object.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
from typing import Tuple

from .model import (
    LEVELS,
    CommandDefinition,
    ValidationIssue,
    ValidationResult,
)
from .normalization import (
    CONTRACT_VERSION as NORMALIZATION_VERSION,
    normalize_semantic_text,
)
from .semantic_validator import validate_command_semantics


IDENTITY_CONTRACT_VERSION = "UCG-VALIDATED-IDENTITY-01"


@dataclass(frozen=True)
class ValidatedSemanticIdentity:
    """Immutable validated snapshot; not an authorization credential."""

    levels: Tuple[str, ...]
    normalization_version: str
    contract_version: str
    fingerprint: str


def _payload(
    levels: Tuple[str, ...],
    normalization_version: str,
    contract_version: str,
) -> dict:
    return {
        "levels": list(levels),
        "normalization_version": normalization_version,
        "contract_version": contract_version,
    }


def _fingerprint(
    levels: Tuple[str, ...],
    normalization_version: str,
    contract_version: str,
) -> str:
    canonical = json.dumps(
        _payload(levels, normalization_version, contract_version),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _snapshot_command(levels: Tuple[str, ...]) -> CommandDefinition:
    if not isinstance(levels, tuple) or len(levels) != len(LEVELS):
        raise ValueError("IDENTITY_LEVELS_SHAPE_INVALID")

    if any(type(value) is not str for value in levels):
        raise ValueError("IDENTITY_LEVEL_TYPE_INVALID")

    return CommandDefinition(**dict(zip(LEVELS, levels)))


def create_validated_identity(
    command: CommandDefinition,
) -> ValidatedSemanticIdentity:
    """
    Validate the supplied command internally and emit an atomic identity.

    No caller-supplied ValidationResult is accepted.
    """

    if type(command) is not CommandDefinition:
        raise ValueError("IDENTITY_SOURCE_TYPE_INVALID")

    # Capture a source snapshot first; subsequent source mutation cannot
    # change the emitted identity.
    source_levels = tuple(command.level_values)

    snapshot = _snapshot_command(source_levels)

    result = validate_command_semantics(snapshot)
    if not result.valid:
        codes = ",".join(issue.code for issue in result.issues)
        raise ValueError(f"IDENTITY_SEMANTIC_INVALID:{codes}")

    normalized_levels = tuple(
        normalize_semantic_text(value)
        for value in source_levels
    )

    if len(normalized_levels) != len(LEVELS):
        raise ValueError("IDENTITY_LEVELS_SHAPE_INVALID")

    fingerprint = _fingerprint(
        normalized_levels,
        NORMALIZATION_VERSION,
        IDENTITY_CONTRACT_VERSION,
    )

    return ValidatedSemanticIdentity(
        levels=normalized_levels,
        normalization_version=NORMALIZATION_VERSION,
        contract_version=IDENTITY_CONTRACT_VERSION,
        fingerprint=fingerprint,
    )


def verify_validated_identity(
    identity: object,
) -> ValidationResult:
    """
    Fail-closed integrity and semantic verification at consumption time.

    Revalidates the semantic snapshot; isinstance alone is not trusted.
    """

    issues = []

    # RT008: establish an exact-type trust boundary before field processing.
    if type(identity) is not ValidatedSemanticIdentity:
        return ValidationResult.failure(
            ValidationIssue(
                code="IDENTITY_OBJECT_TYPE_INVALID",
                message="Expected exact ValidatedSemanticIdentity type.",
            )
        )

    # Validate version fields before comparison or fingerprint construction.
    if type(identity.contract_version) is not str:
        issues.append(
            ValidationIssue(
                code="IDENTITY_CONTRACT_VERSION_TYPE_INVALID",
                message="Identity contract version must be an exact string.",
            )
        )
    elif identity.contract_version != IDENTITY_CONTRACT_VERSION:
        issues.append(
            ValidationIssue(
                code="IDENTITY_CONTRACT_VERSION_UNSUPPORTED",
                message="Identity contract version is unsupported.",
            )
        )

    if type(identity.normalization_version) is not str:
        issues.append(
            ValidationIssue(
                code="IDENTITY_NORMALIZATION_VERSION_TYPE_INVALID",
                message="Normalization version must be an exact string.",
            )
        )
    elif identity.normalization_version != NORMALIZATION_VERSION:
        issues.append(
            ValidationIssue(
                code="IDENTITY_NORMALIZATION_VERSION_UNSUPPORTED",
                message="Identity normalization version is unsupported.",
            )
        )

    # Require an exact tuple and exact strings; subclasses may override behavior.
    if type(identity.levels) is not tuple or len(identity.levels) != len(LEVELS):
        issues.append(
            ValidationIssue(
                code="IDENTITY_LEVELS_SHAPE_INVALID",
                message="Identity must contain exactly eight ordered levels.",
            )
        )
        return ValidationResult.failure(*issues)

    if any(type(value) is not str for value in identity.levels):
        issues.append(
            ValidationIssue(
                code="IDENTITY_LEVEL_TYPE_INVALID",
                message="All identity levels must be exact strings.",
            )
        )
        return ValidationResult.failure(*issues)

    # Fail closed on malformed version/fingerprint types before hashing.
    if any(
        issue.code in {
            "IDENTITY_CONTRACT_VERSION_TYPE_INVALID",
            "IDENTITY_NORMALIZATION_VERSION_TYPE_INVALID",
            "IDENTITY_CONTRACT_VERSION_UNSUPPORTED",
            "IDENTITY_NORMALIZATION_VERSION_UNSUPPORTED",
        }
        for issue in issues
    ):
        return ValidationResult.failure(*issues)

    if type(identity.fingerprint) is not str:
        issues.append(
            ValidationIssue(
                code="IDENTITY_FINGERPRINT_MISMATCH",
                message="Identity integrity fingerprint must be an exact string.",
            )
        )
        return ValidationResult.failure(*issues)

    try:
        expected_fingerprint = _fingerprint(
            identity.levels,
            identity.normalization_version,
            identity.contract_version,
        )
        fingerprint_matches = hmac.compare_digest(
            identity.fingerprint,
            expected_fingerprint,
        )
    except Exception:
        fingerprint_matches = False

    if not fingerprint_matches:
        issues.append(
            ValidationIssue(
                code="IDENTITY_FINGERPRINT_MISMATCH",
                message="Identity integrity fingerprint does not match.",
            )
        )
        return ValidationResult.failure(*issues)

    # Reconstruct and validate from the identity snapshot itself.
    try:
        reconstructed = _snapshot_command(identity.levels)
        semantic_result = validate_command_semantics(reconstructed)
        normalized_again = tuple(
            normalize_semantic_text(value)
            for value in identity.levels
        )
    except Exception as exc:
        issues.append(
            ValidationIssue(
                code="IDENTITY_REVALIDATION_FAILED",
                message=f"Identity revalidation failed: {type(exc).__name__}.",
            )
        )
        return ValidationResult.failure(*issues)

    if not semantic_result.valid:
        issues.extend(semantic_result.issues)

    if normalized_again != identity.levels:
        issues.append(
            ValidationIssue(
                code="IDENTITY_NORMALIZATION_DRIFT",
                message="Snapshot is not canonical under the current normalizer.",
        )
        )

    if issues:
        return ValidationResult.failure(*issues)

    return ValidationResult.success()
