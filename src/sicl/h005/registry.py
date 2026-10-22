"""Explicit, auditable recomputation handler registry for H-005."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from ..derivation import DerivationRecord, VersionedRef


class RegistryError(Exception):
    pass


class HandlerNotRegisteredError(RegistryError):
    pass


class AmbiguousHandlerError(RegistryError):
    pass


@dataclass(frozen=True, order=True)
class HandlerKey:
    method: str
    method_version: str


RecomputationHandler = Callable[[str, DerivationRecord, Mapping[tuple[str, str], VersionedRef]], DerivationRecord]


class RecomputationRegistry:
    """Only explicitly registered callables can be resolved."""

    def __init__(self) -> None:
        self._handlers: dict[HandlerKey, tuple[RecomputationHandler, ...]] = {}

    def register(self, method: str, method_version: str, handler: RecomputationHandler) -> None:
        if not isinstance(method, str) or not method.strip() or not isinstance(method_version, str) or not method_version.strip():
            raise RegistryError("method and method_version must be non-empty strings")
        if not callable(handler):
            raise RegistryError("handler must be callable")
        key = HandlerKey(method.strip(), method_version.strip())
        existing = self._handlers.get(key, ())
        self._handlers[key] = existing + (handler,)

    def resolve(self, method: str, method_version: str) -> RecomputationHandler:
        key = HandlerKey(method, method_version)
        handlers = self._handlers.get(key, ())
        if not handlers:
            raise HandlerNotRegisteredError(f"HANDLER_NOT_REGISTERED: {method}@{method_version}")
        if len(handlers) != 1:
            raise AmbiguousHandlerError(f"AMBIGUOUS_HANDLER: {method}@{method_version}")
        return handlers[0]

    def keys(self) -> tuple[HandlerKey, ...]:
        return tuple(sorted(self._handlers))


__all__ = ["RegistryError", "HandlerNotRegisteredError", "AmbiguousHandlerError", "HandlerKey", "RecomputationHandler", "RecomputationRegistry"]
