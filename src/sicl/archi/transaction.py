"""Transactional architectural mutation boundary with the real H-002..H-005 chain."""
from __future__ import annotations
from dataclasses import dataclass, replace
from enum import Enum
from typing import Mapping
import hashlib
import os
import tempfile
from pathlib import Path
from .model import ArchiElement
from .mutation import ArchiMutation
from .sufficiency import snapshot_for
from ..a002 import SufficiencyEngine
from ..derivation import DerivationLedger, VersionedRef
from ..impact import ChangeKind, ImpactAnalyzer, ImpactChange
from ..validity import ValidityAnalyzer
from ..reaction import ReactionPlanner
from ..h005 import ExecutionStatus, RecomputationRegistry, SelectiveRecomputationEngine
from .ifc_export import export_ifc

class MutationLifecycle(str, Enum):
    PROPOSED="PROPOSED"; EVALUATED="EVALUATED"; AUTHORIZED="AUTHORIZED"; APPLIED="APPLIED"; PUBLISHED="PUBLISHED"
class MutationStatus(str, Enum):
    ALLOW="ALLOW"; BLOCKED="BLOCKED"; NEEDS_REVIEW="NEEDS_REVIEW"; FAILED="FAILED"; APPLIED="APPLIED"
    INVALID="INVALID"; UNKNOWN="UNKNOWN"; ESCALATE="ESCALATE"; REQUIRES_AUTHORITY="REQUIRES_AUTHORITY"

@dataclass(frozen=True)
class MutationResult:
    mutation_id: str
    status: MutationStatus
    lifecycle: MutationLifecycle
    canonical: tuple[ArchiElement,...]
    candidate: tuple[ArchiElement,...] = ()
    reason: str = ""
    derivation_recorded: bool = False
    provenance: dict = None

class _MemoryStore:
    def __init__(self): self.items=[]
    def add_event(self,event): self.items.append(event); return event
    def add_events_atomic(self, events): self.items.extend(events); return list(events)
    def events(self,project_id=None): return [e for e in self.items if project_id is None or e.project_id==project_id]

class ArchiTransaction:
    def __init__(self, elements: tuple[ArchiElement,...] = (), sufficiency_engine: SufficiencyEngine | None = None):
        self._canonical=tuple(elements); self._engine=sufficiency_engine or SufficiencyEngine(); self._applied=set()
    @property
    def canonical(self): return self._canonical

    def _candidate(self, mutation: ArchiMutation):
        target=next((e for e in self._canonical if e.element_id==mutation.target_id and e.version==mutation.target_version), None)
        if target is None: return None, tuple(self._canonical)
        candidate=list(self._canonical); idx=candidate.index(target); payload=mutation.canonical_payload
        if mutation.mutation_kind.value=="MOVE":
            g=replace(target.geometry, x_mm=target.geometry.x_mm+int(payload.get("dx_mm",0)), y_mm=target.geometry.y_mm+int(payload.get("dy_mm",0)))
            candidate[idx]=replace(target, geometry=g, version=target.version+1)
        elif mutation.mutation_kind.value=="RESIZE":
            p=replace(target.geometry.profile, width_mm=int(payload["width_mm"]), depth_mm=int(payload["depth_mm"]))
            candidate[idx]=replace(target, geometry=replace(target.geometry, profile=p), version=target.version+1)
        elif mutation.mutation_kind.value=="DELETE": candidate.pop(idx)
        elif mutation.mutation_kind.value=="ADD_OPENING":
            # ADD_OPENING is explicitly fail-closed until its semantic
            # candidate representation is implemented.
            pass
        else: raise ValueError(f"unsupported mutation kind: {mutation.mutation_kind!r}")
        return target, tuple(candidate)

    @staticmethod
    def _stage_ifc(path: Path, payload: bytes) -> Path:
        """Write IFC bytes beside the destination without publishing them."""
        fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".stage", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
        except Exception:
            Path(name).unlink(missing_ok=True)
            raise
        return Path(name)

    @staticmethod
    def _promote_ifc(stage: Path, final: Path) -> Path | None:
        """Atomically promote a staged IFC, retaining the previous version."""
        backup = None
        if final.exists():
            backup = final.with_name(f".{final.name}.previous")
            backup.unlink(missing_ok=True)
            os.replace(final, backup)
        try:
            os.replace(stage, final)
        except Exception:
            if backup is not None and backup.exists():
                os.replace(backup, final)
            raise
        return backup

    @staticmethod
    def _rollback_ifc(final: Path, backup: Path | None) -> None:
        """Restore the prior IFC, or remove a new file, after publication failure."""
        if backup is not None and backup.exists():
            final.unlink(missing_ok=True)
            os.replace(backup, final)
        else:
            final.unlink(missing_ok=True)

    def apply_full_chain(self, mutation: ArchiMutation, ledger: DerivationLedger, registry: RecomputationRegistry, current_refs: Mapping[tuple[str,str], VersionedRef], *, ifc_path=None) -> MutationResult:
        """Run A-002, H-002, H-003, H-004, H-005, then publish ledger and IFC."""
        mid=mutation.compute_id()
        if mid in self._applied: return MutationResult(mid, MutationStatus.APPLIED, MutationLifecycle.PUBLISHED, self._canonical, self._canonical, "REPLAY_NO_DOUBLE_APPLICATION", False, {"replay": True})
        target, candidate=self._candidate(mutation)
        if target is None: return MutationResult(mid, MutationStatus.BLOCKED, MutationLifecycle.EVALUATED, self._canonical, (), "TARGET_NOT_FOUND", False, {})
        if mutation.mutation_kind.value=="ADD_OPENING": return MutationResult(mid, MutationStatus.BLOCKED, MutationLifecycle.EVALUATED, self._canonical, (), "OPERATION_NOT_IMPLEMENTED", False, {"operation": mutation.mutation_kind.value})
        snap=snapshot_for(mutation,target,self._engine)
        prov={"a002":snap.result.to_dict()}
        if not snap.permits: return MutationResult(mid, MutationStatus.BLOCKED, MutationLifecycle.EVALUATED, self._canonical, (), "A002_BLOCKED", False, prov)
        old_ref=target.ref(); new_target=next(e for e in candidate if e.element_id==target.element_id)
        # H-002 CONTENT_CHANGED is a same-version WHAT-IF observation. The
        # published architectural element receives version+1 only after H-005.
        new_ref=VersionedRef(old_ref.entity_type, old_ref.entity_id, old_ref.version, new_target.content_hash())
        impact=ImpactAnalyzer(ledger).analyze_change(mutation.project_id, ImpactChange(old_ref,new_ref,ChangeKind.CONTENT_CHANGED))
        prov["h002"] = impact.canonical_dict()
        if not impact.impacted_artifacts: return MutationResult(mid, MutationStatus.BLOCKED, MutationLifecycle.EVALUATED, self._canonical, (), "H002_UNKNOWN_NO_IMPACT", False, prov)
        changed_refs=dict(current_refs); changed_refs[old_ref.key()]=new_ref
        validity=ValidityAnalyzer(ledger).evaluate_validity(mutation.project_id, changed_refs, {"mutationId":mid})
        prov["h003"] = validity.canonical_dict()
        reaction=ReactionPlanner().plan_reaction(validity); prov["h004"]=reaction.canonical_dict()
        eligible=[a for a in reaction.planned_actions if a.action_type.value=="RECOMPUTE" and a.status.value=="PLANNED" and not a.requires_human_authority]
        ineligible=[a for a in reaction.planned_actions if a not in eligible]
        prov["h004"]["eligibility"]={"eligible": [a.to_dict() for a in eligible], "ineligible": [a.to_dict() for a in ineligible]}
        if len(eligible)!=len(reaction.planned_actions):
            action_types={action.action_type.value for action in ineligible}
            blocked_status = (MutationStatus.INVALID if "REJECT" in action_types else
                              MutationStatus.ESCALATE if "ESCALATE" in action_types else
                              MutationStatus.NEEDS_REVIEW if "REVIEW" in action_types else
                              MutationStatus.REQUIRES_AUTHORITY)
            return MutationResult(mid, blocked_status, MutationLifecycle.EVALUATED, self._canonical, (), "H004_NOT_AUTOMATICALLY_ELIGIBLE", False, prov)
        # H-005 is real, but runs against a temporary ledger so failures cannot partially publish.
        temp=DerivationLedger(_MemoryStore())
        for record in ledger.list(mutation.project_id): temp.record(mutation.project_id, record)
        h005=SelectiveRecomputationEngine(temp, registry).execute(mutation.project_id, reaction, changed_refs)
        prov["h005"]=h005.to_dict()
        if any(r.status is not ExecutionStatus.EXECUTED for r in h005.records): return MutationResult(mid, MutationStatus.BLOCKED, MutationLifecycle.EVALUATED, self._canonical, (), "H005_BLOCKED_OR_FAILED", False, prov)
        try:
            # Serialization is in-memory. A supplied path is an external
            # publication target, not the serialization boundary.
            ifc_bytes=export_ifc(candidate, None)
            prov["ifc"]={"sha256":hashlib.sha256(ifc_bytes).hexdigest(),"published":False,"staged":ifc_path is not None}
        except Exception as exc: return MutationResult(mid, MutationStatus.FAILED, MutationLifecycle.EVALUATED, self._canonical, (), f"IFC_EXPORT:{type(exc).__name__}", False, prov)

        stage = None
        final = Path(ifc_path) if ifc_path is not None else None
        backup = None
        promoted = False
        cleanup_backup = True
        try:
            if final is not None:
                stage = self._stage_ifc(final, ifc_bytes)
                # Promotion precedes ledger publication. If it fails, the
                # ledger is untouched; if ledger publication fails, the prior
                # final file is restored below.
                backup = self._promote_ifc(stage, final)
                promoted = True

            existing_ids = {record.id for record in ledger.list(mutation.project_id)}
            new_records = [record for record in temp.list(mutation.project_id) if record.id not in existing_ids]
            ledger.record_batch(mutation.project_id, new_records, actor="ARCHI_D2")
        except Exception as exc:
            if promoted and final is not None:
                try:
                    self._rollback_ifc(final, backup)
                except Exception as rollback_exc:
                    cleanup_backup = False
                    return MutationResult(mid, MutationStatus.FAILED, MutationLifecycle.EVALUATED, self._canonical, (), f"TRANSACTION_ROLLBACK_FAILED:{type(rollback_exc).__name__}", False, prov)
            return MutationResult(mid, MutationStatus.FAILED, MutationLifecycle.EVALUATED, self._canonical, (), f"PUBLICATION:{type(exc).__name__}", False, prov)
        finally:
            if stage is not None:
                stage.unlink(missing_ok=True)
            if backup is not None and cleanup_backup:
                backup.unlink(missing_ok=True)

        prov["ifc"]["published"] = final is not None
        self._canonical=candidate; self._applied.add(mid)
        return MutationResult(mid, MutationStatus.APPLIED, MutationLifecycle.PUBLISHED, self._canonical, self._canonical, "APPLIED_PUBLISHED", True, prov)

__all__=["MutationLifecycle","MutationStatus","MutationResult","ArchiTransaction"]
