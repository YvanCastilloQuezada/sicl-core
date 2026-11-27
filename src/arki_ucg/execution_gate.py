"""UCG Execution Gate R1.

Decision-only gate. It never invokes an operation or executes a command.
"""
from dataclasses import dataclass

from .canonical_identity import verify_canonical_identity

EXECUTION_GATE_CONTRACT_VERSION = "UCG-EXECUTION-GATE-R1"


@dataclass(frozen=True)
class ExecutionGateResult:
    permitted: bool
    code: str
    fingerprint: str = None


class CanonicalExecutionGate:
    """Fail-closed decision gate over identity, resolution and authorization."""

    def evaluate(self, identity, resolver_result, authorization_result):
        verification = verify_canonical_identity(identity)
        if not verification.valid:
            return ExecutionGateResult(False, "GATE_IDENTITY_INVALID")

        if not getattr(resolver_result, "resolved", False):
            return ExecutionGateResult(False, "GATE_RESOLUTION_DENIED")

        entry = getattr(resolver_result, "entry", None)
        if entry is None:
            return ExecutionGateResult(False, "GATE_RESOLUTION_DENIED")

        if (
            entry.fingerprint != identity.fingerprint
            or entry.levels != identity.levels
        ):
            return ExecutionGateResult(False, "GATE_IDENTITY_MISMATCH")

        if not getattr(authorization_result, "authorized", False):
            return ExecutionGateResult(False, "GATE_AUTHORIZATION_DENIED")

        if getattr(authorization_result, "code", None) != "AUTH_ALLOWED":
            return ExecutionGateResult(False, "GATE_AUTHORIZATION_DENIED")

        return ExecutionGateResult(
            permitted=True,
            code="GATE_PERMIT_DECISION_ONLY",
            fingerprint=identity.fingerprint,
        )
