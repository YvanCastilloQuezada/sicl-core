import base64
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from sicl.human_authority_crypto import (
    ACTION,
    CONTRACT,
    HumanAuthorityError,
    canonical_bytes,
    verify_approval,
)


NOW = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)


def approval():
    key = Ed25519PrivateKey.generate()

    payload = {
        "contract": CONTRACT,
        "action": ACTION,
        "projectId": "P",
        "proposalId": "PROP-1",
        "fingerprint": "a" * 64,
        "actorId": "OWNER",
        "reviewId": "REV-1",
        "keyId": "OWNER-KEY-1",
        "decision": "APPROVED",
        "issuedAt": (NOW - timedelta(seconds=10)).isoformat(),
        "expiresAt": (NOW + timedelta(seconds=120)).isoformat(),
        "nonce": "unique-nonce-1",
    }

    signature = base64.b64encode(
        key.sign(canonical_bytes(payload))
    ).decode()

    public_key = base64.b64encode(
        key.public_key().public_bytes(
            Encoding.Raw,
            PublicFormat.Raw,
        )
    ).decode()

    return payload, signature, public_key


def verify(payload, signature, public_key, **overrides):
    params = {
        "payload": payload,
        "signature_b64": signature,
        "public_key_b64": public_key,
        "project_id": "P",
        "proposal_id": "PROP-1",
        "fingerprint": "a" * 64,
        "review_id": "REV-1",
        "key_id": "OWNER-KEY-1",
        "now": NOW,
    }
    params.update(overrides)
    return verify_approval(**params)


def test_valid_approval():
    payload, signature, public_key = approval()
    assert verify(payload, signature, public_key) == payload


@pytest.mark.parametrize("field,value", [
    ("projectId", "OTHER"),
    ("proposalId", "OTHER"),
    ("fingerprint", "b" * 64),
    ("action", "OTHER_ACTION"),
    ("actorId", ""),
    ("nonce", ""),
    ("reviewId", "REV-OTHER"),
    ("keyId", "OTHER-KEY"),
    ("decision", "REJECTED"),
])
def test_modified_scope_is_rejected(field, value):
    payload, signature, public_key = approval()
    payload[field] = value

    with pytest.raises(HumanAuthorityError):
        verify(payload, signature, public_key)


def test_invalid_signature():
    payload, _, public_key = approval()

    with pytest.raises(HumanAuthorityError):
        verify(payload, "invalid-base64", public_key)


def test_expired_approval():
    payload, signature, public_key = approval()

    with pytest.raises(HumanAuthorityError):
        verify(
            payload,
            signature,
            public_key,
            now=NOW + timedelta(hours=1),
        )


def test_wrong_public_key():
    payload, signature, _ = approval()
    another = Ed25519PrivateKey.generate()

    wrong_key = base64.b64encode(
        another.public_key().public_bytes(
            Encoding.Raw,
            PublicFormat.Raw,
        )
    ).decode()

    with pytest.raises(HumanAuthorityError):
        verify(payload, signature, wrong_key)


def test_naive_clock_rejected():
    payload, signature, public_key = approval()

    with pytest.raises(HumanAuthorityError):
        verify(
            payload,
            signature,
            public_key,
            now=datetime(2026, 10, 14, 12, 0),
        )
