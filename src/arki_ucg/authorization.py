"""UCG Authorization R1: explicit allowlist, no execution."""
from dataclasses import dataclass
from threading import RLock

from .canonical_identity import verify_canonical_identity

AUTHORIZATION_CONTRACT_VERSION = "UCG-AUTHORIZATION-R1"


@dataclass(frozen=True)
class AuthorizationResult:
    authorized: bool
    code: str


class CanonicalAuthorization:
    """Explicit grants tied to verified canonical identity fingerprints."""

    def __init__(self):
        self._grants = {}
        self._lock = RLock()

    def grant(self, identity):
        verification = verify_canonical_identity(identity)
        if not verification.valid:
            return AuthorizationResult(False, "AUTH_IDENTITY_INVALID")

        with self._lock:
            self._grants[identity.fingerprint] = identity.levels

        return AuthorizationResult(True, "AUTH_GRANT_CREATED")

    def revoke(self, identity):
        verification = verify_canonical_identity(identity)
        if not verification.valid:
            return AuthorizationResult(False, "AUTH_IDENTITY_INVALID")

        with self._lock:
            existing = self._grants.get(identity.fingerprint)
            if existing is None or existing != identity.levels:
                return AuthorizationResult(False, "AUTH_GRANT_NOT_FOUND")
            del self._grants[identity.fingerprint]

        return AuthorizationResult(True, "AUTH_GRANT_REVOKED")

    def authorize(self, identity, resolver_result):
        verification = verify_canonical_identity(identity)
        if not verification.valid:
            return AuthorizationResult(False, "AUTH_IDENTITY_INVALID")

        if not getattr(resolver_result, "resolved", False):
            return AuthorizationResult(False, "AUTH_RESOLUTION_REQUIRED")

        entry = getattr(resolver_result, "entry", None)
        if entry is None:
            return AuthorizationResult(False, "AUTH_RESOLUTION_REQUIRED")

        if (
            entry.fingerprint != identity.fingerprint
            or entry.levels != identity.levels
        ):
            return AuthorizationResult(False, "AUTH_RESOLUTION_MISMATCH")

        with self._lock:
            granted_levels = self._grants.get(identity.fingerprint)

        if granted_levels is None:
            return AuthorizationResult(False, "AUTH_DENIED")

        if granted_levels != identity.levels:
            return AuthorizationResult(False, "AUTH_IDENTITY_MISMATCH")

        return AuthorizationResult(True, "AUTH_ALLOWED")

    def has_grant(self, identity):
        verification = verify_canonical_identity(identity)
        if not verification.valid:
            return False

        with self._lock:
            return self._grants.get(identity.fingerprint) == identity.levels

    def __len__(self):
        with self._lock:
            return len(self._grants)
