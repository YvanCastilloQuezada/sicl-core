"""Tests para el generador y verificador de etiquetas de contenido."""
from sicl.compliance.content_labeling import ContentLabeler


def test_generate_label_creates_valid_structure():
    label = ContentLabeler.generate_label("Generated architectural layout", "LLM-Arch-v2", "arch_layout_v1", ["doi:10.1234/test"])
    assert label["generator_id"] == "LLM-Arch-v2"
    assert label["domain_profile_ref"] == "arch_layout_v1"
    assert len(label["content_hash"]) == 64
    assert label["standard"] == "C2PA-inspired"


def test_verify_label_success():
    content = "Test content for labeling"
    label = ContentLabeler.generate_label(content, "TestGen", "test_domain")
    valid, message = ContentLabeler.verify_label(content, label)
    assert valid is True
    assert "verified successfully" in message


def test_verify_label_tampered_content():
    label = ContentLabeler.generate_label("Original content", "TestGen", "test_domain")
    valid, message = ContentLabeler.verify_label("Tampered content", label)
    assert valid is False
    assert "tampered" in message.lower()


def test_verify_label_missing_hash():
    valid, message = ContentLabeler.verify_label("Test content", {"generator_id": "TestGen"})
    assert valid is False
    assert "missing content_hash" in message
