"""ACE88 — Developer promotions require verified human provenance."""

from test_developer_promotion import setup_repo, run


def test_forged_approved_review_cannot_promote():
    """
    A service or database writer must not obtain promotion authority
    merely by inserting an APPROVED HumanReview.

    Existing setup_repo creates a legacy review without a
    cryptographically verifiable authorization.
    """
    repo = setup_repo(review_status="APPROVED")

    try:
        outcome = run(repo, approval_payload=None, approval_signature_b64=None)

        assert outcome.committed is False, (
            "ACE88 SECURITY FAILURE: an unverified APPROVED review "
            "authorized a Developer promotion"
        )

        assert repo.get_d2("P") is None, (
            "ACE88 SECURITY FAILURE: unverified human authority "
            "modified canonical D2"
        )
    finally:
        repo.conn.close()
