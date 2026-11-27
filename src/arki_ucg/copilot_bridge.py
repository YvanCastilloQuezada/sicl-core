"""UCG Copilot Bridge R1.

Stable decision interface between Copilot and UCG.
Identity must already be canonical. No NLP, tools or execution.
"""
from dataclasses import dataclass

from .canonical_identity import verify_canonical_identity

COPILOT_BRIDGE_CONTRACT_VERSION = "UCG-COPILOT-BRIDGE-R1"


@dataclass(frozen=True)
class CopilotBridgeResult:
    contract_version: str
    accepted: bool
    decision: str
    code: str
    fingerprint: str = None


class CanonicalCopilotBridge:
    """Expose UCG's decision pipeline without exposing execution."""

    def __init__(self, pipeline):
        self._pipeline = pipeline

    def evaluate_identity(self, identity):
        verification = verify_canonical_identity(identity)

        if not verification.valid:
            return CopilotBridgeResult(
                contract_version=COPILOT_BRIDGE_CONTRACT_VERSION,
                accepted=False,
                decision="DENY",
                code="BRIDGE_IDENTITY_INVALID",
            )

        if self._pipeline is None:
            return CopilotBridgeResult(
                contract_version=COPILOT_BRIDGE_CONTRACT_VERSION,
                accepted=False,
                decision="DENY",
                code="BRIDGE_PIPELINE_UNAVAILABLE",
            )

        result = self._pipeline.evaluate(identity)

        if not result.permitted:
            return CopilotBridgeResult(
                contract_version=COPILOT_BRIDGE_CONTRACT_VERSION,
                accepted=True,
                decision="DENY",
                code=result.code,
                fingerprint=identity.fingerprint,
            )

        return CopilotBridgeResult(
            contract_version=COPILOT_BRIDGE_CONTRACT_VERSION,
            accepted=True,
            decision="PERMIT_DECISION_ONLY",
            code="BRIDGE_DECISION_PERMIT",
            fingerprint=identity.fingerprint,
        )
