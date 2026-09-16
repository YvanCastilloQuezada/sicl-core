"""Controlled ingestion boundary for RFC-025 regulatory corpus fixtures.

This module validates provenance and shape only. It does not infer legal validity,
create constraints, or mark a regulation as vigente without human review.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REQUIRED_SOURCE_KEYS = {"source_id", "source_type", "title", "url", "version"}
REQUIRED_REGULATION_KEYS = {"regulation_id", "code", "title", "authority", "jurisdiction", "version", "status", "source_id", "scope_applicable"}
REQUIRED_EVIDENCE_KEYS = {"evidence_id", "source_id", "evidence_type", "article_reference", "statement", "method_version", "state"}
ALLOWED_SOURCE_TYPES = {"OFFICIAL", "SECONDARY", "USER_PROVIDED", "UNKNOWN"}
ALLOWED_REGULATION_STATUSES = {"VIGENTE", "MODIFICADA", "DEROGADA", "NO_VERIFICADA"}


def load_corpus_fixture(path: str | Path) -> dict[str, Any]:
    """Load and validate a JSON fixture without changing repository state."""
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    validate_corpus_fixture(payload)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["fixture_hash"] = hashlib.sha256(canonical).hexdigest()
    payload["fixture_path"] = str(fixture_path)
    return payload


def validate_corpus_fixture(payload: dict[str, Any]) -> None:
    if payload.get("schema_version") != "rne-corpus-fixture/1":
        raise ValueError("unsupported regulatory corpus fixture schema")
    if payload.get("corpus_status") != "SAMPLE_UNVERIFIED":
        raise ValueError("fixture must remain SAMPLE_UNVERIFIED until human review")
    sources = payload.get("sources")
    regulations = payload.get("regulations")
    evidence = payload.get("evidence")
    if not isinstance(sources, list) or not sources:
        raise ValueError("fixture requires at least one source")
    if not isinstance(regulations, list) or not regulations:
        raise ValueError("fixture requires at least one regulation")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("fixture requires at least one evidence record")

    source_ids: set[str] = set()
    for source in sources:
        missing = REQUIRED_SOURCE_KEYS - source.keys()
        if missing:
            raise ValueError(f"source missing keys: {sorted(missing)}")
        if source["source_id"] in source_ids:
            raise ValueError(f"duplicate source_id: {source['source_id']}")
        if source["source_type"] not in ALLOWED_SOURCE_TYPES:
            raise ValueError(f"invalid source_type: {source['source_type']}")
        if not str(source["url"]).startswith(("https://", "http://")):
            raise ValueError("source url must be an HTTP(S) URL")
        source_ids.add(source["source_id"])

    regulation_ids: set[str] = set()
    for regulation in regulations:
        missing = REQUIRED_REGULATION_KEYS - regulation.keys()
        if missing:
            raise ValueError(f"regulation missing keys: {sorted(missing)}")
        if regulation["regulation_id"] in regulation_ids:
            raise ValueError(f"duplicate regulation_id: {regulation['regulation_id']}")
        if regulation["source_id"] not in source_ids:
            raise ValueError(f"regulation source_id does not exist: {regulation['source_id']}")
        if regulation["status"] not in ALLOWED_REGULATION_STATUSES:
            raise ValueError(f"invalid regulation status: {regulation['status']}")
        regulation_ids.add(regulation["regulation_id"])

    evidence_ids: set[str] = set()
    for item in evidence:
        missing = REQUIRED_EVIDENCE_KEYS - item.keys()
        if missing:
            raise ValueError(f"evidence missing keys: {sorted(missing)}")
        if item["evidence_id"] in evidence_ids:
            raise ValueError(f"duplicate evidence_id: {item['evidence_id']}")
        if item["source_id"] not in source_ids:
            raise ValueError(f"evidence source_id does not exist: {item['source_id']}")
        evidence_ids.add(item["evidence_id"])
