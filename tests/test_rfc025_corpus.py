from __future__ import annotations

import json
from pathlib import Path

import pytest

from sicl.regulatory_corpus import evidence_traceability_report, load_corpus_fixture, validate_corpus_fixture

FIXTURE = Path(__file__).parents[1] / "data" / "regulatory" / "rne_a010_sample.json"


def test_rne_fixture_is_traceable_and_unverified() -> None:
    payload = load_corpus_fixture(FIXTURE)
    assert payload["corpus_status"] == "SAMPLE_UNVERIFIED"
    assert {item["code"] for item in payload["regulations"]} == {"A.010", "E.030", "E.060", "IS.010", "EM.010"}
    assert len(payload["sources"]) == 6
    assert len(payload["evidence"]) == 7
    assert all(item["status"] == "NO_VERIFICADA" for item in payload["regulations"])
    assert len(payload["fixture_hash"]) == 64


def test_a010_evidence_review_has_complete_source_links() -> None:
    payload = load_corpus_fixture(FIXTURE)
    report = evidence_traceability_report(payload)
    assert report["all_traceable"] is True
    assert report["evidence_count"] == 7
    assert all(row["source_type"] == "OFFICIAL" for row in report["rows"])
    assert all(row["article_reference"] and row["method_version"] for row in report["rows"])


def test_fixture_rejects_unknown_source_reference() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["evidence"][0]["source_id"] = "SRC-MISSING"
    with pytest.raises(ValueError, match="evidence source_id"):
        validate_corpus_fixture(payload)


def test_fixture_rejects_missing_article_reference() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["evidence"][0]["article_reference"] = ""
    with pytest.raises(ValueError, match="article_reference"):
        validate_corpus_fixture(payload)
