from datetime import datetime, timezone

import pytest

from sicl.copilot_evidence import (
    ClaimStatus, EvidenceKind, EvidenceLink, EvidenceRelation, EvidenceSource,
    ResearchClaim, ResearchPacket,
)


def source():
    return EvidenceSource(source_id="src-1", kind=EvidenceKind.WEB, title="Municipal plan",
                        uri="https://example.invalid/plan", publisher="Municipality",
                        retrieved_at="2026-11-26T10:00:00Z", published_at="2026-01-01T00:00:00Z",
                        jurisdiction="Peru", sha256="a" * 64)


def claim(status=ClaimStatus.SUPPORTED, links=()):
    return ResearchClaim(claim_id="cl-1", statement="The plan identifies a public space deficit.",
                       status=status, links=links, confidence=0.8, scope="district")


def test_source_requires_iso_dates_and_valid_hash():
    with pytest.raises(ValueError, match="ISO-8601"):
        EvidenceSource(source_id="s", kind=EvidenceKind.WEB, title="Title", uri="https://example.com",
                      publisher="p", retrieved_at="yesterday")
    with pytest.raises(ValueError, match="64 hexadecimal"):
        EvidenceSource(source_id="s", kind=EvidenceKind.WEB, title="Title", uri="https://example.com",
                      publisher="p", retrieved_at="2026-11-26T10:00:00Z", sha256="bad")


def test_claim_must_be_supported_by_linked_evidence():
    with pytest.raises(ValueError, match="require evidence"):
        claim()


def test_proposed_claim_is_not_misrepresented_as_source_supported():
    proposed = claim(ClaimStatus.PROPOSED, (EvidenceLink("src-1", EvidenceRelation.CONTEXT),))
    with pytest.raises(ValueError, match="cannot be presented"):
        proposed


def test_research_packet_rejects_unknown_source_reference():
    with pytest.raises(ValueError, match="unknown sources"):
        ResearchPacket(packet_id="rp-1", created_at="2026-11-26T10:00:00Z", query="urban spaces",
                       sources=(source(),), claims=(claim(links=(EvidenceLink("src-unknown", EvidenceRelation.SUPPORTS),)),))


def test_packet_accepts_provenance_and_claim_links():
    evidence_claim = claim(links=(EvidenceLink("src-1", EvidenceRelation.SUPPORTS,
                                               excerpt="Brief supporting excerpt"),))
    packet = ResearchPacket(packet_id="rp-1", created_at="2026-11-26T10:00:00Z", query="urban spaces",
                           sources=(source(),), claims=(evidence_claim,), limitations=("Not independently verified",))
    assert packet.claims[0].links[0].source_id == packet.sources[0].source_id


def test_packet_rejects_duplicate_source_and_claim_ids():
    c = claim(links=(EvidenceLink("src-1", EvidenceRelation.SUPPORTS),))
    with pytest.raises(ValueError, match="duplicate source_id"):
        ResearchPacket(packet_id="rp", created_at="2026-11-26T10:00:00Z", query="q",
                       sources=(source(), source()), claims=(c,))
