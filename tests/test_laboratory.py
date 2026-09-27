"""Tests del Laboratorio de IA con las 4 reglas fundamentales."""
import tempfile
from pathlib import Path

import pytest

from sicl.laboratory.authority_gate import AuthorityGate, AuthorityRequiredError
from sicl.laboratory.corpus_validator import CorpusValidationStatus, CorpusValidator
from sicl.laboratory.deterministic_generator import DeterministicGenerator
from sicl.laboratory.sandbox_ledger import SandboxEventType, SandboxLedger


@pytest.fixture
def temp_ledger():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as handle:
        temp_path = Path(handle.name)
    ledger = SandboxLedger(storage_path=temp_path)
    yield ledger
    temp_path.unlink(missing_ok=True)


class TestLAB001Trazabilidad:
    def test_lab_001_provenance_required(self, temp_ledger):
        alternative = DeterministicGenerator(temp_ledger).generate("P1", "test prompt", seed=42, corpus=["source1", "source2", "source3"])
        assert alternative.provenance_signature is not None
        assert "content_hash" in alternative.provenance_signature
        assert "generator_id" in alternative.provenance_signature

    def test_lab_001_events_recorded(self, temp_ledger):
        DeterministicGenerator(temp_ledger).generate("P1", "test prompt", seed=42, corpus=["source1", "source2", "source3"])
        events = temp_ledger.list_events("P1")
        assert len(events) == 2
        assert events[0].event_type == SandboxEventType.GENERATION_REQUESTED
        assert events[1].event_type == SandboxEventType.ALTERNATIVE_GENERATED


class TestLAB002Determinismo:
    def test_lab_002_deterministic_generation(self, temp_ledger):
        generator = DeterministicGenerator(temp_ledger)
        alt1 = generator.generate("P1", "test prompt", seed=42, corpus=["source1", "source2", "source3"])
        alt2 = generator.generate("P1", "test prompt", seed=42, corpus=["source1", "source2", "source3"])
        assert alt1.content == alt2.content
        assert alt1.alternative_id == alt2.alternative_id

    def test_lab_002_different_seed_different_output(self, temp_ledger):
        generator = DeterministicGenerator(temp_ledger)
        alt1 = generator.generate("P1", "test prompt", seed=42, corpus=["source1", "source2", "source3"])
        alt2 = generator.generate("P1", "test prompt", seed=99, corpus=["source1", "source2", "source3"])
        assert alt1.content != alt2.content
        assert alt1.alternative_id != alt2.alternative_id


class TestLAB003FailClosed:
    def test_lab_003_uncertain_when_corpus_insufficient(self, temp_ledger):
        result = CorpusValidator(temp_ledger, min_sources=3).validate("P1", ["source1"])
        assert result.status == CorpusValidationStatus.INSUFFICIENT
        assert result.available_sources == 1
        assert result.required_sources == 3
        assert "insufficient" in result.message.lower()

    def test_lab_003_sufficient_corpus(self, temp_ledger):
        result = CorpusValidator(temp_ledger, min_sources=3).validate("P1", ["source1", "source2", "source3"])
        assert result.status == CorpusValidationStatus.SUFFICIENT
        assert result.available_sources == 3


class TestLAB004AutoridadHumana:
    def test_lab_004_promote_requires_authority(self, temp_ledger):
        with pytest.raises(AuthorityRequiredError):
            AuthorityGate(temp_ledger).promote_to_canonical("P1", "ALT-123", authority_approval_id="")

    def test_lab_004_promote_with_authority(self, temp_ledger):
        result = AuthorityGate(temp_ledger).promote_to_canonical("P1", "ALT-123", authority_approval_id="AUTH-YVAN-001")
        assert result.status.value == "PROMOTED"
        assert result.authority_approval_id == "AUTH-YVAN-001"

    def test_lab_004_rejection_is_recorded(self, temp_ledger):
        with pytest.raises(AuthorityRequiredError):
            AuthorityGate(temp_ledger).promote_to_canonical("P1", "ALT-123", authority_approval_id="")
        events = temp_ledger.list_events("P1")
        assert events[-1].payload["status"] == "REJECTED"

    def test_lab_004_promotion_event_is_recorded(self, temp_ledger):
        AuthorityGate(temp_ledger).promote_to_canonical("P1", "ALT-123", authority_approval_id="AUTH-YVAN-001")
        events = temp_ledger.list_events("P1")
        assert events[-1].event_type == SandboxEventType.PROMOTED_TO_CANONICAL
        assert events[-1].payload["authorityApprovalId"] == "AUTH-YVAN-001"
