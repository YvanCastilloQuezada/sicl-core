"""Clasificador y validador de dominios según EU AI Act."""
from __future__ import annotations

from typing import Any


class EUAIActClassifier:
    """Clasifica dominios y valida requisitos de alto riesgo del EU AI Act."""

    HIGH_RISK_DOMAINS = [
        "biometric_identification",
        "critical_infrastructure",
        "education_employment",
        "essential_private_services",
        "law_enforcement",
        "migration_asylum",
        "administration_of_justice",
        "bio_longevity",
    ]

    @classmethod
    def classify_domain(cls, domain_id: str) -> str:
        domain_lower = domain_id.lower()
        return "HIGH" if any(domain in domain_lower for domain in cls.HIGH_RISK_DOMAINS) else "LIMITED"

    @classmethod
    def validate_high_risk_requirements(cls, domain_profile: dict[str, Any], aia: dict[str, Any] | None) -> tuple[bool, str]:
        if domain_profile.get("risk_tier") != "HIGH":
            return True, "Not a high-risk domain"
        if not domain_profile.get("aia_required", False):
            return False, "HIGH risk domain requires aia_required=True"
        if aia is None:
            return False, "HIGH risk domain requires an Algorithmic Impact Assessment (AIA)"
        if aia.get("status") != "APPROVED":
            return False, f"AIA status must be APPROVED, got {aia.get('status')}"
        if not aia.get("authority_approval_id"):
            return False, "AIA must have an authority_approval_id for human oversight (Art. 14)"
        return True, "Compliant with EU AI Act High-Risk requirements"


__all__ = ["EUAIActClassifier"]
