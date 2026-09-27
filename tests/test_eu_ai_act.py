"""Tests para el clasificador EU AI Act."""
from sicl.compliance.eu_ai_act import EUAIActClassifier


def test_classify_domain_high_risk():
    assert EUAIActClassifier.classify_domain("bio_longevity_v1") == "HIGH"
    assert EUAIActClassifier.classify_domain("biometric_identification_system") == "HIGH"


def test_classify_domain_limited_risk():
    assert EUAIActClassifier.classify_domain("arch_layout_generator") == "LIMITED"
    assert EUAIActClassifier.classify_domain("chatbot_customer_service") == "LIMITED"


def test_validate_high_risk_compliant():
    profile = {"risk_tier": "HIGH", "aia_required": True}
    aia = {"status": "APPROVED", "authority_approval_id": "AUTH-001"}
    valid, message = EUAIActClassifier.validate_high_risk_requirements(profile, aia)
    assert valid is True
    assert "Compliant" in message


def test_validate_high_risk_missing_aia():
    profile = {"risk_tier": "HIGH", "aia_required": True}
    valid, message = EUAIActClassifier.validate_high_risk_requirements(profile, None)
    assert valid is False
    assert "requires an Algorithmic Impact Assessment" in message


def test_validate_high_risk_pending_aia():
    profile = {"risk_tier": "HIGH", "aia_required": True}
    aia = {"status": "PENDING_REVIEW", "authority_approval_id": None}
    valid, message = EUAIActClassifier.validate_high_risk_requirements(profile, aia)
    assert valid is False
    assert "status must be APPROVED" in message
