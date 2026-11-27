"""UCG Registry R1.

Stores verified canonical identities only.
Registry does not normalize, resolve, authorize, or execute.
"""
from dataclasses import dataclass
from threading import RLock
from typing import Tuple

from .canonical_identity import (
    CanonicalSemanticIdentity,
    verify_canonical_identity,
)


REGISTRY_CONTRACT_VERSION = "UCG-REGISTRY-R1"


@dataclass(frozen=True)
class RegistryEntry:
    identity: CanonicalSemanticIdentity
    fingerprint: str
    levels: Tuple[str, ...]


@dataclass(frozen=True)
class RegistryResult:
    accepted: bool
    code: str
    entry: RegistryEntry = None


class CanonicalRegistry:
    """In-memory registry for exact canonical identities."""

    def __init__(self):
        self._entries_by_fingerprint = {}
        self._lock = RLock()

    def register(self, identity: object) -> RegistryResult:
        verification = verify_canonical_identity(identity)

        if not verification.valid:
            return RegistryResult(
                accepted=False,
                code="REGISTRY_IDENTITY_INVALID",
            )

        fingerprint = identity.fingerprint
        levels = identity.levels

        with self._lock:
            existing = self._entries_by_fingerprint.get(fingerprint)

            if existing is not None:
                if existing.levels == levels:
                    return RegistryResult(
                        accepted=False,
                        code="REGISTRY_DUPLICATE",
                        entry=existing,
                    )

                return RegistryResult(
                    accepted=False,
                    code="REGISTRY_FINGERPRINT_COLLISION",
                )

            # Defensive semantic duplicate check independent of fingerprint.
            for stored in self._entries_by_fingerprint.values():
                if stored.levels == levels:
                    return RegistryResult(
                        accepted=False,
                        code="REGISTRY_SEMANTIC_DUPLICATE",
                        entry=stored,
                    )

            entry = RegistryEntry(
                identity=identity,
                fingerprint=fingerprint,
                levels=levels,
        )

            self._entries_by_fingerprint[fingerprint] = entry

            return RegistryResult(
                accepted=True,
                code="REGISTRY_REGISTERED",
                entry=entry,
            )

    def get_by_fingerprint(self, fingerprint: str):
        if type(fingerprint) is not str:
            return None

        with self._lock:
            return self._entries_by_fingerprint.get(fingerprint)

    def contains(self, identity: object) -> bool:
        verification = verify_canonical_identity(identity)

        if not verification.valid:
            return False

        with self._lock:
            entry = self._entries_by_fingerprint.get(identity.fingerprint)
            return entry is not None and entry.levels == identity.levels

    def snapshot(self) -> Tuple[RegistryEntry, ...]:
        """Return an immutable snapshot; never exposes the internal dictionary."""
        with self._lock:
            return tuple(self._entries_by_fingerprint.values())

    def __len__(self) -> int:
        with self._lock:
            return len(self._entries_by_fingerprint)
