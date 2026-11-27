"""UCG Resolver R1.

Resolves exact verified canonical identities against a registry.
No normalization, fuzzy matching, authorization, or execution.
"""
from dataclasses import dataclass

from .canonical_identity import verify_canonical_identity


RESOLVER_CONTRACT_VERSION = "UCG-RESOLVER-R1"


@dataclass(frozen=True)
class ResolverResult:
    resolved: bool
    code: str
    entry: object = None


class CanonicalResolver:
    """Exact resolver over a supplied canonical registry."""

    def __init__(self, registry):
        self._registry = registry

    def resolve(self, identity: object) -> ResolverResult:
        verification = verify_canonical_identity(identity)

        if not verification.valid:
            return ResolverResult(
                resolved=False,
                code="RESOLVER_IDENTITY_INVALID",
            )

        entry = self._registry.get_by_fingerprint(identity.fingerprint)

        if entry is None:
            return ResolverResult(
                resolved=False,
                code="RESOLVER_NOT_FOUND",
            )

        # Fingerprint lookup is not enough: compare exact semantic levels.
        if entry.levels != identity.levels:
            return ResolverResult(
                resolved=False,
                code="RESOLVER_IDENTITY_MISMATCH",
            )

        return ResolverResult(
            resolved=True,
            code="RESOLVER_EXACT_MATCH",
            entry=entry,
        )
