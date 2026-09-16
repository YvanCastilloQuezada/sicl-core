from __future__ import annotations

import json
from pathlib import Path

import pytest

from sicl.regulatory_corpus import load_corpus_fixture, validate_corpus_fixture

FIXTURE = Path(__file__).parents[1] / "data" / "regulatory" / "rne_a010_sample.json"


def test_rne_a010_fixture_is_traceable_and_unverified() -> None:
    payload = load_corpus_fixture(FIXTURE)
    assert payload["corpus_status"] == "SAMPLE_UNVERIFIED"
    assert payload["regulations"][0]["code"] == "A.010"
    assert payload["regulations"][0]["status"] == "NO_VERIFICADA"
    assert len(payload["sources"]) == 2
    assert len(payload["evidence"]) == 3
    assert len(payload["fixture_hash"]) == 64


def test_rne_a010_fixture_rejects_unknown_source_reference() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["evidence"][0]["source_id"] = "SRC-MISSING"
    with pytest.raises(ValueError, match="evidence source_id"):
        validate_corpus_fixture(payload)
