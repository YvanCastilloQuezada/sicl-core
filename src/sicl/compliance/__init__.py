"""ARKI Compliance Validator — Pilar VIII (Rules 41, 42, 43).

Este módulo implementa las reglas de cumplimiento normativo y soberanía
sin modificar el Core congelado (H-001 a H-004).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class ComplianceStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    PENDING_REVIEW = "PENDING_REVIEW"


@dataclass(frozen=True)
class ComplianceResult:
    rule_id: str
    status: ComplianceStatus
    message: str
    details: dict[str, Any] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ruleId": self.rule_id,
            "status": self.status.value,
            "message": self.message,
            "details": self.details or {},
        }


class ComplianceValidator:
    """Valida los contratos de gobernanza del Pilar VIII."""

    def __init__(self, schemas_dir: Path | None = None):
        if schemas_dir is None:
            schemas_dir = Path(__file__).parent.parent.parent.parent / "docs" / "schemas"
        self.schemas_dir = schemas_dir
        self._load_schemas()

    def _load_schemas(self):
        try:
            with open(self.schemas_dir / "domain_profile.json", encoding="utf-8") as f:
                self.domain_profile_schema = json.load(f)
            with open(self.schemas_dir / "provenance_signature.json", encoding="utf-8") as f:
                self.provenance_signature_schema = json.load(f)
            with open(self.schemas_dir / "ethical_impact_assessment.json", encoding="utf-8") as f:
                self.ethical_impact_assessment_schema = json.load(f)
        except FileNotFoundError as exc:
            raise RuntimeError(
                f"Schemas not found in {self.schemas_dir}. Ensure docs/schemas/ exists with the 3 JSON files."
            ) from exc

    def validate_domain_profile(self, profile: dict[str, Any]) -> ComplianceResult:
        required_fields = ["domain_id", "risk_tier", "hard_constraints", "aia_required"]
        missing_fields = [field for field in required_fields if field not in profile]
        if missing_fields:
            return ComplianceResult("RULE_41", ComplianceStatus.NON_COMPLIANT, f"Missing required fields: {missing_fields}", {"missing_fields": missing_fields})

        valid_tiers = ["MINIMAL", "LIMITED", "HIGH", "UNACCEPTABLE"]
        if profile["risk_tier"] not in valid_tiers:
            return ComplianceResult("RULE_41", ComplianceStatus.NON_COMPLIANT, f"Invalid risk_tier: {profile['risk_tier']}. Must be one of {valid_tiers}", {"invalid_tier": profile["risk_tier"]})
        if profile["risk_tier"] in ["HIGH", "LIMITED"] and not profile.get("aia_required", False):
            return ComplianceResult("RULE_41", ComplianceStatus.NON_COMPLIANT, f"risk_tier={profile['risk_tier']} requires aia_required=True", {"risk_tier": profile["risk_tier"]})
        if profile["risk_tier"] == "UNACCEPTABLE":
            return ComplianceResult("RULE_41", ComplianceStatus.NON_COMPLIANT, "risk_tier=UNACCEPTABLE: operation blocked by compliance policy", {"risk_tier": "UNACCEPTABLE"})
        return ComplianceResult("RULE_41", ComplianceStatus.COMPLIANT, f"Domain profile valid for risk_tier={profile['risk_tier']}", {"risk_tier": profile["risk_tier"], "aia_required": profile.get("aia_required", False)})

    def validate_provenance_signature(self, output_content: str | bytes, signature: dict[str, Any]) -> ComplianceResult:
        required_fields = ["generator_id", "timestamp", "content_hash", "signature_algorithm", "domain_profile_ref"]
        missing_fields = [field for field in required_fields if field not in signature]
        if missing_fields:
            return ComplianceResult("RULE_42", ComplianceStatus.NON_COMPLIANT, f"Missing required signature fields: {missing_fields}", {"missing_fields": missing_fields})

        content_hash = signature["content_hash"]
        if len(content_hash) != 64 or not all(char in "0123456789abcdef" for char in content_hash):
            return ComplianceResult("RULE_42", ComplianceStatus.NON_COMPLIANT, "Invalid content_hash: must be 64 hex characters", {"content_hash_length": len(content_hash)})
        if isinstance(output_content, str):
            output_content = output_content.encode("utf-8")
        computed_hash = hashlib.sha256(output_content).hexdigest()
        if computed_hash != content_hash:
            return ComplianceResult("RULE_42", ComplianceStatus.NON_COMPLIANT, "Content hash mismatch: output has been tampered with", {"computed_hash": computed_hash, "provided_hash": content_hash})

        valid_algorithms = ["SHA256_RSA", "C2PA", "ED25519", "HMAC_SHA256"]
        if signature["signature_algorithm"] not in valid_algorithms:
            return ComplianceResult("RULE_42", ComplianceStatus.NON_COMPLIANT, f"Invalid signature_algorithm: {signature['signature_algorithm']}", {"invalid_algorithm": signature["signature_algorithm"]})
        return ComplianceResult("RULE_42", ComplianceStatus.COMPLIANT, "Provenance signature valid and content integrity verified", {"generator_id": signature["generator_id"], "timestamp": signature["timestamp"], "algorithm": signature["signature_algorithm"]})

    def validate_ethical_impact_assessment(self, output_ref: str, aia: dict[str, Any], risk_tier: str) -> ComplianceResult:
        if risk_tier == "MINIMAL":
            return ComplianceResult("RULE_43", ComplianceStatus.COMPLIANT, "AIA not required for MINIMAL risk tier", {"risk_tier": risk_tier})
        if risk_tier in ["LIMITED", "HIGH"]:
            required_fields = ["assessment_id", "target_output_ref", "bias_declaration", "harm_assessment_score", "status"]
            missing_fields = [field for field in required_fields if field not in aia]
            if missing_fields:
                return ComplianceResult("RULE_43", ComplianceStatus.NON_COMPLIANT, f"AIA required for risk_tier={risk_tier} but missing fields: {missing_fields}", {"missing_fields": missing_fields, "risk_tier": risk_tier})
            if aia["status"] != "APPROVED":
                return ComplianceResult("RULE_43", ComplianceStatus.PENDING_REVIEW, f"AIA status is {aia['status']}, not APPROVED", {"aia_status": aia["status"], "risk_tier": risk_tier})
            if not aia.get("authority_approval_id"):
                return ComplianceResult("RULE_43", ComplianceStatus.NON_COMPLIANT, "AIA is APPROVED but missing authority_approval_id", {"aia_status": aia["status"]})
            harm_score = aia.get("harm_assessment_score", 0)
            if not (0 <= harm_score <= 100):
                return ComplianceResult("RULE_43", ComplianceStatus.NON_COMPLIANT, f"harm_assessment_score {harm_score} out of range [0, 100]", {"harm_score": harm_score})
            if aia["target_output_ref"] != output_ref:
                return ComplianceResult("RULE_43", ComplianceStatus.NON_COMPLIANT, f"AIA target_output_ref mismatch: expected {output_ref}, got {aia['target_output_ref']}", {"expected": output_ref, "actual": aia["target_output_ref"]})
            return ComplianceResult("RULE_43", ComplianceStatus.COMPLIANT, f"AIA approved for risk_tier={risk_tier}", {"assessment_id": aia["assessment_id"], "harm_score": harm_score, "authority_approval_id": aia["authority_approval_id"]})
        return ComplianceResult("RULE_43", ComplianceStatus.NON_COMPLIANT, f"Unexpected risk_tier: {risk_tier}", {"risk_tier": risk_tier})

    def validate_full_compliance(self, domain_profile: dict[str, Any], output_content: str | bytes, signature: dict[str, Any], output_ref: str, aia: dict[str, Any] | None = None) -> list[ComplianceResult]:
        result_41 = self.validate_domain_profile(domain_profile)
        results = [result_41]
        if result_41.status == ComplianceStatus.NON_COMPLIANT:
            return results
        results.append(self.validate_provenance_signature(output_content, signature))
        risk_tier = domain_profile.get("risk_tier", "MINIMAL")
        if aia is None and risk_tier in ["LIMITED", "HIGH"]:
            results.append(ComplianceResult("RULE_43", ComplianceStatus.NON_COMPLIANT, f"AIA required for risk_tier={risk_tier} but not provided", {"risk_tier": risk_tier}))
        elif aia is not None:
            results.append(self.validate_ethical_impact_assessment(output_ref, aia, risk_tier))
        return results


__all__ = ["ComplianceStatus", "ComplianceResult", "ComplianceValidator"]
