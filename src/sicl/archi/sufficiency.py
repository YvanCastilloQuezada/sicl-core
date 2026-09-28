"""A-002 integration for architectural mutations; no duplicated sufficiency logic."""
from __future__ import annotations
from dataclasses import dataclass
from .mutation import ArchiMutation, MutationKind
from .model import ArchiElement
from ..a002 import (EvidenceRef, KnowledgeItem, KnowledgeState, OperationRequirement, SufficiencyEngine, SufficiencyRequest, SufficiencyResult)

_OPERATIONS={MutationKind.MOVE:"archi.move",MutationKind.RESIZE:"archi.resize",MutationKind.ADD_OPENING:"archi.add_opening",MutationKind.DELETE:"archi.delete"}
@dataclass(frozen=True)
class ArchiSufficiencySnapshot:
    operation: str
    result: SufficiencyResult
    @property
    def permits(self): return self.result.permits_h005

def snapshot_for(mutation: ArchiMutation, target: ArchiElement | None, engine: SufficiencyEngine | None = None) -> ArchiSufficiencySnapshot:
    operation=_OPERATIONS[mutation.mutation_kind]; engine=engine or SufficiencyEngine()
    knowledge=[]; requirements=[]; evidence=[]
    def add_known(field, value):
        evidence_id = f"ARCHI-{field}"
        ref = EvidenceRef.from_statement(evidence_id, f"{field}={value}", "ARCHI_MODEL", mutation.project_id)
        evidence.append(ref); knowledge.append(KnowledgeItem(field, value, KnowledgeState.KNOWN, (evidence_id,)))
    if target is not None:
        add_known("target_id", target.element_id.value)
        add_known("target_version", target.version)
        add_known("content_hash", target.content_hash())
    else:
        add_known("target_id", mutation.target_id.value)
        add_known("target_version", mutation.target_version)
    requirements += [OperationRequirement("target_id", (KnowledgeState.KNOWN,), True), OperationRequirement("target_version", (KnowledgeState.KNOWN,), True), OperationRequirement("content_hash", (KnowledgeState.KNOWN,), True)]
    if mutation.mutation_kind is MutationKind.ADD_OPENING:
        requirements.append(OperationRequirement("host", (KnowledgeState.KNOWN,), True))
        if "host_id" in mutation.canonical_payload: add_known("host", mutation.canonical_payload["host_id"])
    if mutation.mutation_kind is MutationKind.DELETE:
        requirements.append(OperationRequirement("human_authority_ref", (KnowledgeState.KNOWN,), True, require_human_authority=True))
    req=SufficiencyRequest(mutation.project_id, operation, tuple(knowledge), tuple(requirements), tuple(evidence))
    return ArchiSufficiencySnapshot(operation, engine.evaluate(req))

__all__=["ArchiSufficiencySnapshot","snapshot_for"]
