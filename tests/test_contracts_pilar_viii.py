"""Tests de contrato para los schemas del Pilar VIII (Reglas 41, 42, 43)."""
import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator, ValidationError


SCHEMAS_DIR = Path(__file__).parent.parent / "docs" / "schemas"


class TestSchemaValidity:
    @pytest.mark.parametrize(
        "schema_file",
        [
            "domain_profile.json",
            "provenance_signature.json",
            "ethical_impact_assessment.json",
        ],
    )
    def test_schema_is_valid_json_schema(self, schema_file):
        schema_path = SCHEMAS_DIR / schema_file
        assert schema_path.exists(), f"Schema no encontrado: {schema_path}"
        with open(schema_path, encoding="utf-8") as f:
            schema = json.load(f)
        Draft7Validator.check_schema(schema)
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"


class TestDomainProfileContract:
    @pytest.fixture
    def schema(self):
        with open(SCHEMAS_DIR / "domain_profile.json", encoding="utf-8") as f:
            return json.load(f)

    def test_valid_minimal_profile(self, schema):
        profile = {
            "domain_id": "test_domain_v1",
            "risk_tier": "MINIMAL",
            "hard_constraints": ["no_violate_physics"],
            "aia_required": False,
        }
        Draft7Validator(schema).validate(profile)

    def test_high_risk_profile_requires_aia(self, schema):
        profile = {
            "domain_id": "bio_longevity_v1",
            "risk_tier": "HIGH",
            "hard_constraints": ["somatic_only", "reversibility_required"],
            "aia_required": True,
            "max_acceptable_trade_off_penalty": 0.15,
            "allowed_modification_scope": "somatic_only",
            "required_corpus_tags": ["peer_reviewed", "mammalian_model"],
        }
        Draft7Validator(schema).validate(profile)

    def test_invalid_risk_tier_rejected(self, schema):
        profile = {
            "domain_id": "test",
            "risk_tier": "INVALID_TIER",
            "hard_constraints": [],
            "aia_required": False,
        }
        with pytest.raises(ValidationError):
            Draft7Validator(schema).validate(profile)

    def test_missing_required_field_rejected(self, schema):
        profile = {"domain_id": "test", "risk_tier": "MINIMAL"}
        with pytest.raises(ValidationError):
            Draft7Validator(schema).validate(profile)


class TestProvenanceSignatureContract:
    @pytest.fixture
    def schema(self):
        with open(SCHEMAS_DIR / "provenance_signature.json", encoding="utf-8") as f:
            return json.load(f)

    def test_valid_signature(self, schema):
        sig = {
            "generator_id": "LLM-Bio-Gen-v3",
            "timestamp": "2026-09-28T10:00:00Z",
            "content_hash": "a" * 64,
            "hash_algorithm": "SHA256_HASH",
            "domain_profile_ref": "bio_longevity_v1",
            "source_data_refs": ["doi:10.1038/s41586-023-00000"],
        }
        Draft7Validator(schema).validate(sig)

    def test_invalid_hash_length_rejected(self, schema):
        sig = {
            "generator_id": "LLM-Bio-Gen-v3",
            "timestamp": "2026-09-28T10:00:00Z",
            "content_hash": "abc123",
            "hash_algorithm": "SHA256_HASH",
            "domain_profile_ref": "bio_longevity_v1",
        }
        with pytest.raises(ValidationError):
            Draft7Validator(schema).validate(sig)

    def test_missing_generator_id_rejected(self, schema):
        sig = {
            "timestamp": "2026-09-28T10:00:00Z",
            "content_hash": "a" * 64,
            "hash_algorithm": "SHA256_HASH",
            "domain_profile_ref": "bio_longevity_v1",
        }
        with pytest.raises(ValidationError):
            Draft7Validator(schema).validate(sig)


class TestEthicalImpactAssessmentContract:
    @pytest.fixture
    def schema(self):
        with open(SCHEMAS_DIR / "ethical_impact_assessment.json", encoding="utf-8") as f:
            return json.load(f)

    def test_valid_pending_aia(self, schema):
        aia = {
            "assessment_id": "AIA-001",
            "target_output_ref": "OUTPUT-123",
            "bias_declaration": {
                "known_biases": ["training_data_from_european_populations"],
                "mitigation_steps": ["apply_diversity_weighting"],
            },
            "harm_assessment_score": 25,
            "authority_approval_id": None,
            "status": "PENDING_REVIEW",
            "timestamp": "2026-09-28T10:00:00Z",
        }
        Draft7Validator(schema).validate(aia)

    def test_valid_approved_aia(self, schema):
        aia = {
            "assessment_id": "AIA-002",
            "target_output_ref": "OUTPUT-456",
            "bias_declaration": {"known_biases": [], "mitigation_steps": []},
            "harm_assessment_score": 10,
            "authority_approval_id": "AUTH-YVAN-2026-09-28-001",
            "status": "APPROVED",
            "ethical_review_notes": "Aprobado tras revisión de trade-offs",
            "timestamp": "2026-09-28T11:00:00Z",
        }
        Draft7Validator(schema).validate(aia)

    def test_harm_score_out_of_range_rejected(self, schema):
        aia = {
            "assessment_id": "AIA-003",
            "target_output_ref": "OUTPUT-789",
            "bias_declaration": {"known_biases": [], "mitigation_steps": []},
            "harm_assessment_score": 150,
            "authority_approval_id": None,
            "status": "PENDING_REVIEW",
        }
        with pytest.raises(ValidationError):
            Draft7Validator(schema).validate(aia)

    def test_invalid_status_rejected(self, schema):
        aia = {
            "assessment_id": "AIA-004",
            "target_output_ref": "OUTPUT-999",
            "bias_declaration": {"known_biases": [], "mitigation_steps": []},
            "harm_assessment_score": 50,
            "authority_approval_id": None,
            "status": "MAYBE_APPROVED",
        }
        with pytest.raises(ValidationError):
            Draft7Validator(schema).validate(aia)
