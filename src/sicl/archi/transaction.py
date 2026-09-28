"""Transactional architectural mutation boundary."""
from __future__ import annotations
from dataclasses import dataclass, replace
from enum import Enum
from typing import Callable
from .model import ArchiElement
from .mutation import ArchiMutation
from .sufficiency import snapshot_for
from ..a002 import SufficiencyEngine

class MutationLifecycle(str, Enum):
    PROPOSED="PROPOSED"; EVALUATED="EVALUATED"; AUTHORIZED="AUTHORIZED"; APPLIED="APPLIED"; PUBLISHED="PUBLISHED"
class MutationStatus(str, Enum):
    ALLOW="ALLOW"; BLOCKED="BLOCKED"; NEEDS_REVIEW="NEEDS_REVIEW"; FAILED="FAILED"; APPLIED="APPLIED"
@dataclass(frozen=True)
class MutationResult:
    mutation_id: str
    status: MutationStatus
    lifecycle: MutationLifecycle
    canonical: tuple[ArchiElement,...]
    candidate: tuple[ArchiElement,...] = ()
    reason: str = ""
    derivation_recorded: bool = False

class ArchiTransaction:
    def __init__(self, elements: tuple[ArchiElement,...] = (), sufficiency_engine: SufficiencyEngine | None = None):
        self._canonical=tuple(elements); self._engine=sufficiency_engine or SufficiencyEngine(); self._applied=set()
    @property
    def canonical(self): return self._canonical
    def apply(self, mutation: ArchiMutation, *, recompute: Callable[[tuple[ArchiElement,...]], tuple[ArchiElement,...]] | None = None) -> MutationResult:
        mid=mutation.compute_id()
        if mid in self._applied: return MutationResult(mid, MutationStatus.APPLIED, MutationLifecycle.PUBLISHED, self._canonical, self._canonical, "REPLAY_NO_DOUBLE_APPLICATION", True)
        target=next((e for e in self._canonical if e.element_id==mutation.target_id and e.version==mutation.target_version), None)
        snap=snapshot_for(mutation,target,self._engine)
        if not snap.permits: return MutationResult(mid, MutationStatus.BLOCKED, MutationLifecycle.EVALUATED, self._canonical, (), ",".join(snap.result.reason_codes) or "A002_BLOCKED", False)
        candidate=list(self._canonical)
        if target is None: return MutationResult(mid, MutationStatus.BLOCKED, MutationLifecycle.EVALUATED, self._canonical, (), "TARGET_NOT_FOUND", False)
        idx=candidate.index(target)
        payload=mutation.canonical_payload
        if mutation.mutation_kind.value=="MOVE":
            g=replace(target.geometry, x_mm=target.geometry.x_mm+int(payload.get("dx_mm",0)), y_mm=target.geometry.y_mm+int(payload.get("dy_mm",0)))
            candidate[idx]=replace(target, geometry=g, version=target.version+1)
        elif mutation.mutation_kind.value=="RESIZE":
            p=replace(target.geometry.profile, width_mm=int(payload["width_mm"]), depth_mm=int(payload["depth_mm"]))
            candidate[idx]=replace(target, geometry=replace(target.geometry, profile=p), version=target.version+1)
        elif mutation.mutation_kind.value=="DELETE": candidate.pop(idx)
        else: candidate.append(target)
        cand=tuple(candidate)
        if recompute is not None: cand=tuple(recompute(cand))
        self._canonical=cand; self._applied.add(mid)
        return MutationResult(mid, MutationStatus.APPLIED, MutationLifecycle.PUBLISHED, self._canonical, self._canonical, "APPLIED", True)

__all__=["MutationLifecycle","MutationStatus","MutationResult","ArchiTransaction"]
