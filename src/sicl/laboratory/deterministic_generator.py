"""Deterministic Generator — LAB-002: determinismo estricto."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .sandbox_ledger import SandboxEvent, SandboxEventType, SandboxLedger


@dataclass(frozen=True)
class GeneratedAlternative:
    alternative_id: str
    content: str
    seed: int
    generator_id: str
    timestamp: str
    provenance_hash: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"alternativeId": self.alternative_id, "content": self.content, "seed": self.seed, "generatorId": self.generator_id, "timestamp": self.timestamp, "provenanceHash": self.provenance_hash}


class DeterministicGenerator:
    """Generador determinista; produce un hash de proveniencia, no una firma."""

    def __init__(self, ledger: SandboxLedger, generator_id: str = "LAB-GEN-v1"):
        self.ledger = ledger
        self.generator_id = generator_id

    def generate(self, project_id: str, prompt: str, seed: int, corpus: list[str]) -> GeneratedAlternative:
        now = datetime.now(timezone.utc).isoformat()
        self.ledger.record(SandboxEvent(SandboxEventType.GENERATION_REQUESTED, now, project_id, {"prompt": prompt, "seed": seed}))
        content = f"Generated content for prompt: {prompt} (seed={seed})"
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        provenance_hash = {"generator_id": self.generator_id, "timestamp": now, "content_hash": content_hash, "hash_algorithm": "SHA256_HASH", "domain_profile_ref": project_id, "source_data_refs": [hashlib.sha256(source.encode()).hexdigest()[:16] for source in corpus]}
        alternative = GeneratedAlternative(hashlib.sha256(f"{prompt}{seed}".encode()).hexdigest()[:16], content, seed, self.generator_id, now, provenance_hash)
        self.ledger.record(SandboxEvent(SandboxEventType.ALTERNATIVE_GENERATED, now, project_id, {"alternativeId": alternative.alternative_id, "content": content, "seed": seed, "provenanceHash": provenance_hash}))
        return alternative


__all__ = ["DeterministicGenerator", "GeneratedAlternative"]
