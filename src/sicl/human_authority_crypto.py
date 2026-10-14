"""ACE88: cryptographic verification of scoped human approvals."""

from __future__ import annotations

import base64
import binascii
import json
from datetime import datetime, timezone

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


CONTRACT = "ARKI_HUMAN_APPROVAL_V2"
ACTION = "DEVELOPER_PROPOSAL_APPROVE"


class HumanAuthorityError(ValueError):
    pass


def canonical_bytes(payload: dict) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def verify_approval(
    *,
    payload: dict,
    signature_b64: str,
    public_key_b64: str,
    project_id: str,
    proposal_id: str,
    fingerprint: str,
    review_id: str,
    key_id: str,
    now: datetime | None = None,
) -> dict:
    if not isinstance(payload, dict):
        raise HumanAuthorityError("INVALID_AUTHORITY_PAYLOAD")

    expected_fields = {
        "contract",
        "action",
        "projectId",
        "proposalId",
        "fingerprint",
        "actorId",
        "reviewId",
        "keyId",
        "decision",
        "issuedAt",
        "expiresAt",
        "nonce",
    }

    if set(payload) != expected_fields:
        raise HumanAuthorityError("INVALID_AUTHORITY_FIELDS")

    if payload["contract"] != CONTRACT or payload["action"] != ACTION:
        raise HumanAuthorityError("INVALID_AUTHORITY_SCOPE")

    if (
        payload["projectId"] != project_id
        or payload["proposalId"] != proposal_id
        or payload["fingerprint"] != fingerprint
    ):
        raise HumanAuthorityError("AUTHORITY_BINDING_MISMATCH")

    if (
        payload["reviewId"] != review_id
        or payload["keyId"] != key_id
        or payload["decision"] != "APPROVED"
    ):
        raise HumanAuthorityError("AUTHORITY_REVIEW_BINDING_MISMATCH")

    for field in ("actorId", "nonce", "reviewId", "keyId"):
        if not isinstance(payload[field], str) or not payload[field].strip():
            raise HumanAuthorityError("INVALID_AUTHORITY_IDENTITY")

    try:
        issued = datetime.fromisoformat(payload["issuedAt"].replace("Z", "+00:00"))
        expires = datetime.fromisoformat(payload["expiresAt"].replace("Z", "+00:00"))
    except (TypeError, ValueError, AttributeError) as exc:
        raise HumanAuthorityError("INVALID_AUTHORITY_TIME") from exc

    if issued.tzinfo is None or expires.tzinfo is None:
        raise HumanAuthorityError("INVALID_AUTHORITY_TIME")

    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise HumanAuthorityError("INVALID_AUTHORITY_TIME")

    if (
        issued > current
        or expires <= current
        or expires <= issued
        or (expires - issued).total_seconds() > 300
    ):
        raise HumanAuthorityError("AUTHORITY_EXPIRED_OR_INVALID")

    try:
        public_key = Ed25519PublicKey.from_public_bytes(
            base64.b64decode(public_key_b64, validate=True)
        )
        signature = base64.b64decode(signature_b64, validate=True)
        public_key.verify(signature, canonical_bytes(payload))
    except (InvalidSignature, ValueError, TypeError, binascii.Error) as exc:
        raise HumanAuthorityError("INVALID_AUTHORITY_SIGNATURE") from exc

    return payload.copy()
