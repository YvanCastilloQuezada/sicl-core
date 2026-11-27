"""CP-04 provenance/evidence contracts for Copilot research outputs.

These data contracts do not fetch sources, verify URLs, or determine truth. They
require explicit provenance and keep sourced claims separate from hypotheses.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EvidenceKind(str, Enum):
    WEB = "WEB"
    DOCUMENT = "DOCUMENT"
    IMAGE = "IMAGE"
    DATASET = "DATASET"
    ENGINE_OUTPUT = "ENGINE_OUTPUT"
    USER_OBSERVATION = "USER_OBSERVATION"


class ClaimStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONFLICTED = "CONFLICTED"
    UNVERIFIED = "UNVERIFIED"
    PROPOSED = "PROPOSED"


class EvidenceRelation(str, Enum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    CONTEXT = "CONTEXT"


def _iso_datetime(value: str, field: str) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be ISO-8601") from exc


@dataclass(frozen=True)
class EvidenceSource:
    source_id: str
    kind: EvidenceKind
    title: str
    uri: str | None
    publisher: str | None
    retrieved_at: str
    published_at: str | None = None
    jurisdiction: str | None = None
    version: str | None = None
    sha256: str | None = None
    note: str = ""

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.title.strip():
            raise ValueError("source_id and title are required")
        _iso_datetime(self.retrieved_at, "retrieved_at")
        if self.published_at:
            _iso_datetime(self.published_at, "published_at")
        if self.sha256 is not None and (len(self.sha256) != 64 or any(c not in "0123456789abcdefABCDEF" for c in self.sha256)):
            raise ValueError("sha256 must be 64 hexadecimal characters")
        if self.kind in {EvidenceKind.WEB, EvidenceKind.DOCUMENT} and not self.uri:
            raise ValueError("web/document evidence requires a source URI or reference")


@dataclass(frozen=True)
class EvidenceLink:
    source_id: str
    relation: EvidenceRelation
    excerpt: str = ""
    note: str = ""

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source_id is required")
        if len(self.excerpt) > 2000:
            raise ValueError("excerpt exceeds 2000 characters")


@dataclass(frozen=True)
class ResearchClaim:
    claim_id: str
    statement: str
    status: ClaimStatus
    links: tuple[EvidenceLink, ...] = ()
    confidence: float | None = None
    scope: str = ""

    def __post_init__(self) -> None:
        if not self.claim_id.strip() or not self.statement.strip():
            raise ValueError("claim_id and statement are required")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if self.status is ClaimStatus.PROPOSED and self.links:
            raise ValueError("proposed claims cannot be presented as source-supported")
        if self.status in {ClaimStatus.SUPPORTED, ClaimStatus.CONFLICTED} and not self.links:
            raise ValueError("supported/conflicted claims require evidence links")


@dataclass(frozen=True)
class ResearchPacket:
    packet_id: str
    created_at: str
    query: str
    sources: tuple[EvidenceSource, ...]
    claims: tuple[ResearchClaim, ...]
    limitations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.packet_id.strip() or not self.query.strip():
            raise ValueError("packet_id and query are required")
        _iso_datetime(self.created_at, "created_at")
        source_ids = [s.source_id for s in self.sources]
        claim_ids = [c.claim_id for c in self.claims]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("duplicate source_id")
        if len(claim_ids) != len(set(claim_ids)):
            raise ValueError("duplicate claim_id")
        known = set(source_ids)
        unknown_refs = sorted({link.source_id for claim in self.claims for link in claim.links if link.source_id not in known})
        if unknown_refs:
            raise ValueError("claim references unknown sources: " + ", ".join(unknown_refs))
