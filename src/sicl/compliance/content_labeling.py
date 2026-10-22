"""Etiquetado experimental de contenido; hash de integridad, no firma C2PA/RSA."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any


class ContentLabeler:
    """Genera y verifica etiquetas de hash para contenido generado por IA."""

    @staticmethod
    def generate_label(content: str | bytes, generator_id: str, domain_profile_ref: str, source_data_refs: list[str] | None = None) -> dict[str, Any]:
        content_bytes = content.encode("utf-8") if isinstance(content, str) else content
        return {
            "generator_id": generator_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content_hash": hashlib.sha256(content_bytes).hexdigest(),
            "hash_algorithm": "SHA256_HASH",
            "domain_profile_ref": domain_profile_ref,
            "source_data_refs": source_data_refs or [],
            "label_version": "1.1",
            "standard": "hash-integrity-only",
        }

    @staticmethod
    def verify_label(content: str | bytes, label: dict[str, Any]) -> tuple[bool, str]:
        content_bytes = content.encode("utf-8") if isinstance(content, str) else content
        expected_hash = label.get("content_hash")
        if not expected_hash:
            return False, "Label missing content_hash"
        if label.get("hash_algorithm") != "SHA256_HASH":
            return False, "Unsupported or misleading hash_algorithm"
        computed_hash = hashlib.sha256(content_bytes).hexdigest()
        if computed_hash != expected_hash:
            return False, "Content hash mismatch: content has been tampered with"
        return True, "Hash label verified successfully"


__all__ = ["ContentLabeler"]
