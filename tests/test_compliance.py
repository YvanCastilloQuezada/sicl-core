"""Tests para el módulo de compliance (Pilar VIII - Reglas 41, 42, 43)."""
import hashlib
from pathlib import Path

import pytest

from sicl.compliance import ComplianceStatus, ComplianceValidator


@pytest.fixture
def validator():
    return ComplianceValidator(Path(__file__).parent.parent / "docs" / "schemas")


class TestRule41DomainProfile:
    def test_valid_minimal_profile(self, validator):
        result = validator.validate_domain_profile({"domain_id": "test_domain_v1", "risk_tier": "MINIMAL", "hard_constraints": ["no_violate_physics"], "aia_required": False})
        assert result.status == ComplianceStatus.COMPLIANT
        assert result.rule_id == "RULE_41"

    def test_valid_high_risk_profile(self, validator):
        result = validator.validate_domain_profile({"domain_id": "bio_longevity_v1", "risk_tier": "HIGH", "hard_constraints": ["somatic_only"], "aia_required": True})
        assert result.status == ComplianceStatus.COMPLIANT

    def test_high_risk_without_aia_required_fails(self, validator):
        result = validator.validate_domain_profile({"domain_id": "bio_longevity_v1", "risk_tier": "HIGH", "hard_constraints": [], "aia_required": False})
        assert result.status == ComplianceStatus.NON_COMPLIANT
        assert "aia_required=True" in result.message

    def test_unacceptable_risk_tier_blocked(self, validator):
        result = validator.validate_domain_profile({"domain_id": "forbidden_domain", "risk_tier": "UNACCEPTABLE", "hard_constraints": [], "aia_required": False})
        assert result.status == ComplianceStatus.NON_COMPLIANT
        assert "UNACCEPTABLE" in result.message

    def test_missing_required_fields(self, validator):
        result = validator.validate_domain_profile({"domain_id": "test", "risk_tier": "MINIMAL"})
        assert result.status == ComplianceStatus.NON_COMPLIANT
        assert "Missing required fields" in result.message

    def test_invalid_risk_tier(self, validator):
        result = validator.validate_domain_profile({"domain_id": "test", "risk_tier": "INVALID_TIER", "hard_constraints": [], "aia_required": False})
        assert result.status == ComplianceStatus.NON_COMPLIANT
        assert "Invalid risk_tier" in result.message


class TestRule42ProvenanceSignature:
    def test_valid_signature(self, validator):
        content = "test output content"
        signature = {"generator_id": "LLM-Bio-Gen-v3", "timestamp": "2026-09-28T10:00:00Z", "content_hash": hashlib.sha256(content.encode()).hexdigest(), "hash_algorithm": "SHA256_HASH", "domain_profile_ref": "bio_longevity_v1"}
        assert validator.validate_provenance_signature(content, signature).status == ComplianceStatus.COMPLIANT

    def test_tampered_content_detected(self, validator):
        original = "original content"
        signature = {"generator_id": "LLM-Bio-Gen-v3", "timestamp": "2026-09-28T10:00:00Z", "content_hash": hashlib.sha256(original.encode()).hexdigest(), "hash_algorithm": "SHA256_HASH", "domain_profile_ref": "bio_longevity_v1"}
        result = validator.validate_provenance_signature("tampered content", signature)
        assert result.status == ComplianceStatus.NON_COMPLIANT
        assert "tampered" in result.message.lower()

    def test_invalid_hash_length(self, validator):
        result = validator.validate_provenance_signature("content", {"generator_id": "LLM-Bio-Gen-v3", "timestamp": "2026-09-28T10:00:00Z", "content_hash": "abc123", "hash_algorithm": "SHA256_HASH", "domain_profile_ref": "bio_longevity_v1"})
        assert result.status == ComplianceStatus.NON_COMPLIANT
        assert "64 hex characters" in result.message

    def test_missing_signature_fields(self, validator):
        result = validator.validate_provenance_signature("content", {"generator_id": "LLM-Bio-Gen-v3"})
        assert result.status == ComplianceStatus.NON_COMPLIANT
        assert "Missing required provenance hash fields" in result.message

    def test_invalid_hash_algorithm(self, validator):
        content = "test"
        signature = {"generator_id": "LLM-Bio-Gen-v3", "timestamp": "2026-09-28T10:00:00Z", "content_hash": hashlib.sha256(content.encode()).hexdigest(), "hash_algorithm": "INVALID_ALGO", "domain_profile_ref": "bio_longevity_v1"}
        result = validator.validate_provenance_signature(content, signature)
        assert result.status == ComplianceStatus.NON_COMPLIANT
        assert "Schema validation failed" in result.message


class TestRule43EthicalImpactAssessment:
    def test_aia_not_required_for_minimal(self, validator):
        result = validator.validate_ethical_impact_assessment("OUTPUT-123", {}, "MINIMAL")
        assert result.status == ComplianceStatus.COMPLIANT
        assert "not required" in result.message

    def test_valid_approved_aia_for_high_risk(self, validator):
        aia = {"assessment_id": "AIA-001", "target_output_ref": "OUTPUT-123", "bias_declaration": {"known_biases": ["european_population_bias"], "mitigation_steps": ["apply_diversity_weighting"]}, "harm_assessment_score": 25, "authority_approval_id": "AUTH-YVAN-2026-09-28-001", "status": "APPROVED"}
        assert validator.validate_ethical_impact_assessment("OUTPUT-123", aia, "HIGH").status == ComplianceStatus.COMPLIANT

    def test_aia_pending_review_for_high_risk(self, validator):
        aia = {"assessment_id": "AIA-002", "target_output_ref": "OUTPUT-456", "bias_declaration": {"known_biases": [], "mitigation_steps": []}, "harm_assessment_score": 50, "authority_approval_id": None, "status": "PENDING_REVIEW"}
        assert validator.validate_ethical_impact_assessment("OUTPUT-456", aia, "HIGH").status == ComplianceStatus.PENDING_REVIEW

    def test_aia_missing_for_high_risk(self, validator):
        result = validator.validate_ethical_impact_assessment("OUTPUT-789", {}, "HIGH")
        assert result.status == ComplianceStatus.NON_COMPLIANT
        assert "missing fields" in result.message.lower()

    def test_aia_without_authority_approval(self, validator):
        aia = {"assessment_id": "AIA-003", "target_output_ref": "OUTPUT-999", "bias_declaration": {"known_biases": [], "mitigation_steps": []}, "harm_assessment_score": 30, "authority_approval_id": None, "status": "APPROVED"}
        result = validator.validate_ethical_impact_assessment("OUTPUT-999", aia, "HIGH")
        assert result.status == ComplianceStatus.NON_COMPLIANT
        assert "authority_approval_id" in result.message

    def test_aia_harm_score_out_of_range(self, validator):
        aia = {"assessment_id": "AIA-004", "target_output_ref": "OUTPUT-111", "bias_declaration": {"known_biases": [], "mitigation_steps": []}, "harm_assessment_score": 150, "authority_approval_id": "AUTH-001", "status": "APPROVED"}
        result = validator.validate_ethical_impact_assessment("OUTPUT-111", aia, "HIGH")
        assert result.status == ComplianceStatus.NON_COMPLIANT
        assert "out of range" in result.message


class TestFullComplianceValidation:
    def test_full_compliance_minimal_risk(self, validator):
        profile = {"domain_id": "test_domain", "risk_tier": "MINIMAL", "hard_constraints": [], "aia_required": False}
        content = "test output"
        signature = {"generator_id": "LLM-Test-v1", "timestamp": "2026-09-28T10:00:00Z", "content_hash": hashlib.sha256(content.encode()).hexdigest(), "hash_algorithm": "SHA256_HASH", "domain_profile_ref": "test_domain"}
        results = validator.validate_full_compliance(profile, content, signature, "OUTPUT-123")
        assert len(results) == 2
        assert all(result.status == ComplianceStatus.COMPLIANT for result in results)

    def test_full_compliance_high_risk_with_aia(self, validator):
        profile = {"domain_id": "bio_longevity_v1", "risk_tier": "HIGH", "hard_constraints": ["somatic_only"], "aia_required": True}
        content = "bio output"
        signature = {"generator_id": "LLM-Bio-Gen-v3", "timestamp": "2026-09-28T10:00:00Z", "content_hash": hashlib.sha256(content.encode()).hexdigest(), "hash_algorithm": "SHA256_HASH", "domain_profile_ref": "bio_longevity_v1"}
        aia = {"assessment_id": "AIA-001", "target_output_ref": "OUTPUT-456", "bias_declaration": {"known_biases": [], "mitigation_steps": []}, "harm_assessment_score": 20, "authority_approval_id": "AUTH-001", "status": "APPROVED"}
        results = validator.validate_full_compliance(profile, content, signature, "OUTPUT-456", aia)
        assert len(results) == 3
        assert all(result.status == ComplianceStatus.COMPLIANT for result in results)

    def test_full_compliance_high_risk_without_aia_fails(self, validator):
        profile = {"domain_id": "bio_longevity_v1", "risk_tier": "HIGH", "hard_constraints": [], "aia_required": True}
        content = "bio output"
        signature = {"generator_id": "LLM-Bio-Gen-v3", "timestamp": "2026-09-28T10:00:00Z", "content_hash": hashlib.sha256(content.encode()).hexdigest(), "hash_algorithm": "SHA256_HASH", "domain_profile_ref": "bio_longevity_v1"}
        results = validator.validate_full_compliance(profile, content, signature, "OUTPUT-789")
        assert len(results) == 3
        assert results[0].status == ComplianceStatus.COMPLIANT
        assert results[1].status == ComplianceStatus.COMPLIANT
        assert results[2].status == ComplianceStatus.NON_COMPLIANT
        assert "AIA required" in results[2].message
