"""ACE88 integrated trust/replay tests; executed on ARKI-02 with full dependencies."""
import base64
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from sicl.human_authority_crypto import ACTION, CONTRACT, canonical_bytes
from test_developer_promotion import setup_repo, run, FP, PROJECT, PROPOSAL, REVIEW


def signed(repo, *, key_id='k1', actor='architect', register=True, mutate=None):
    private = Ed25519PrivateKey.generate()
    public = base64.b64encode(private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)).decode()
    if register:
        repo.register_authority_key_offline(project_id=PROJECT, key_id=key_id,
                                            actor_id=actor, public_key_b64=public)
    now = datetime.now(timezone.utc)
    payload = dict(contract=CONTRACT, action=ACTION, projectId=PROJECT, proposalId=PROPOSAL,
                   fingerprint=FP, actorId=actor, reviewId=REVIEW, keyId=key_id,
                   decision='APPROVED', issuedAt=(now-timedelta(seconds=10)).isoformat(),
                   expiresAt=(now+timedelta(seconds=100)).isoformat(), nonce='nonce-'+key_id)
    if mutate:
        payload.update(mutate)
    signature = base64.b64encode(private.sign(canonical_bytes(payload))).decode()
    return dict(approval_payload=payload, approval_signature_b64=signature)


def test_unknown_key_cannot_promote():
    repo = setup_repo()
    try:
        out = run(repo, **signed(repo, register=False))
        assert not out.committed and repo.get_d2(PROJECT) is None
    finally:
        repo.close()


def test_revoked_key_cannot_promote():
    repo = setup_repo()
    try:
        proof = signed(repo)
        repo.revoke_authority_key_offline(PROJECT, 'k1')
        out = run(repo, **proof)
        assert not out.committed and repo.get_d2(PROJECT) is None
    finally:
        repo.close()


def test_actor_mismatch_cannot_promote():
    repo = setup_repo()
    try:
        out = run(repo, **signed(repo, actor='attacker'))
        assert not out.committed and repo.get_d2(PROJECT) is None
    finally:
        repo.close()


def test_bad_review_binding_cannot_promote():
    repo = setup_repo()
    try:
        out = run(repo, **signed(repo, mutate={'reviewId':'wrong'}))
        assert not out.committed and repo.get_d2(PROJECT) is None
    finally:
        repo.close()


def test_bad_signature_cannot_promote():
    repo = setup_repo()
    try:
        proof = signed(repo)
        proof['approval_signature_b64'] = 'not-a-signature'
        out = run(repo, **proof)
        assert not out.committed and repo.get_d2(PROJECT) is None
    finally:
        repo.close()
