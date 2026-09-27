"""ARKI H-002 — read-only Impact Analysis / WHAT-IF.

The analyzer reports only consequences represented by registered derivation
edges. Absence from this report is NEVER proof of absence of architectural
consequence.

IMPACT DETECTED != INVALIDATED != RECOMPUTED != CHANGED.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import hashlib, json
from typing import Any, Protocol, Sequence
from .derivation import VersionedRef, DerivationRecord, DerivationValidationError

CONTRACT_VERSION = 1
COVERAGE_WARNING = "GRAPH_MAY_BE_INCOMPLETE"

class ChangeKind(str, Enum):
    CONTENT_CHANGED = "CONTENT_CHANGED"
    VERSION_UPGRADED = "VERSION_UPGRADED"
    IDENTITY_CHANGED = "IDENTITY_CHANGED"
    UNKNOWN = "UNKNOWN"

class Confidence(str, Enum):
    CERTAIN = "CERTAIN"
    UNCERTAIN = "UNCERTAIN"

@dataclass(frozen=True)
class ImpactChange:
    before: VersionedRef
    after: VersionedRef
    change_kind: ChangeKind

    def __post_init__(self):
        if not isinstance(self.before, VersionedRef) or not isinstance(self.after, VersionedRef):
            raise DerivationValidationError("before/after must be VersionedRef")
        if not isinstance(self.change_kind, ChangeKind):
            raise DerivationValidationError("change_kind must be ChangeKind")
        same_identity = self.before.key() == self.after.key()
        if self.change_kind == ChangeKind.CONTENT_CHANGED:
            if not same_identity or self.before.version != self.after.version:
                raise DerivationValidationError("CONTENT_CHANGED requires same identity and version")
            if not self.before.content_hash or not self.after.content_hash or self.before.content_hash == self.after.content_hash:
                raise DerivationValidationError("CONTENT_CHANGED requires two different content hashes")
        elif self.change_kind == ChangeKind.VERSION_UPGRADED:
            if not same_identity or self.after.version <= self.before.version:
                raise DerivationValidationError("VERSION_UPGRADED requires same identity and increasing version")
        elif self.change_kind == ChangeKind.IDENTITY_CHANGED:
            if same_identity:
                raise DerivationValidationError("IDENTITY_CHANGED requires different identity")

@dataclass(frozen=True)
class ImpactStep:
    source: VersionedRef
    target: VersionedRef
    derivation_id: str
    relation_type: str
    relation_domain: str
    confidence: Confidence
    reason: str

    def semantic_tuple(self):
        return (self.source.entity_type,self.source.entity_id,self.source.version,
                self.relation_type,self.relation_domain,
                self.target.entity_type,self.target.entity_id,self.target.version)

@dataclass(frozen=True)
class ImpactPath:
    steps: tuple[ImpactStep,...]
    @property
    def target(self): return self.steps[-1].target
    @property
    def depth(self): return len(self.steps)
    @property
    def confidence(self):
        return Confidence.UNCERTAIN if any(s.confidence == Confidence.UNCERTAIN for s in self.steps) else Confidence.CERTAIN

@dataclass(frozen=True)
class ImpactedArtifact:
    ref: VersionedRef
    min_depth: int
    confidence: Confidence
    derivation_records: tuple[str,...]
    paths: tuple[ImpactPath,...]

@dataclass(frozen=True)
class ImpactReport:
    change: ImpactChange
    impacted_artifacts: tuple[ImpactedArtifact,...]
    cycles: tuple[tuple[tuple[Any,...],...],...]
    coverage_warning: str = COVERAGE_WARNING
    partial: bool = False
    partial_depth: int | None = None
    fail_closed_reason: str | None = None
    assumptions_traversable: bool = False
    contract_version: int = CONTRACT_VERSION

    def canonical_dict(self):
        def ref(r): return r.to_dict()
        return {
            "contractVersion":self.contract_version,
            "change":{"before":ref(self.change.before),"after":ref(self.change.after),"changeKind":self.change.change_kind.value},
            "impactedArtifacts":[{
                "ref":ref(a.ref),"minDepth":a.min_depth,"confidence":a.confidence.value,
                "derivationRecords":list(a.derivation_records),
                "paths":[[{"source":ref(s.source),"target":ref(s.target),"derivationId":s.derivation_id,
                            "relationType":s.relation_type,"relationDomain":s.relation_domain,
                            "confidence":s.confidence.value,"reason":s.reason} for s in p.steps] for p in a.paths]
            } for a in self.impacted_artifacts],
            "cycles":[[list(x) for x in cycle] for cycle in self.cycles],
            "coverageWarning":self.coverage_warning,"partial":self.partial,"partialDepth":self.partial_depth,
            "failClosedReason":self.fail_closed_reason,"assumptionsTraversable":self.assumptions_traversable,
        }

    def stable_fingerprint(self):
        raw=json.dumps(self.canonical_dict(),sort_keys=True,separators=(",",":"),ensure_ascii=False)
        return hashlib.sha256(raw.encode()).hexdigest()

class LedgerReader(Protocol):
    def list(self, project_id:str)->list[DerivationRecord]: ...

def _same_entity_version(a:VersionedRef,b:VersionedRef)->bool:
    return a.key()==b.key() and a.version==b.version

def _edge_confidence(consumer_input:VersionedRef, source:VersionedRef)->tuple[Confidence,str]:
    # Match identity+version first. Hash absence never makes a consumer invisible.
    if not _same_entity_version(consumer_input,source):
        raise DerivationValidationError("confidence requested for different entity/version")
    if source.content_hash is None:
        return Confidence.UNCERTAIN,"SOURCE_CONTENT_HASH_MISSING"
    if consumer_input.content_hash is None:
        return Confidence.UNCERTAIN,"MISSING_CONTENT_HASH"
    if consumer_input.content_hash != source.content_hash:
        return Confidence.UNCERTAIN,"CONTENT_HASH_CONFLICT"
    return Confidence.CERTAIN,"EXACT_VERSION_AND_HASH"

def _canonical_cycle(steps:Sequence[ImpactStep])->tuple[tuple[Any,...],...]:
    edges=tuple(s.semantic_tuple() for s in steps)
    if not edges: return ()
    rotations=[edges[i:]+edges[:i] for i in range(len(edges))]
    return min(rotations)

class ImpactAnalyzer:
    def __init__(self, ledger:LedgerReader, *, max_total_transitive_paths:int=10000):
        if isinstance(max_total_transitive_paths,bool) or not isinstance(max_total_transitive_paths,int) or max_total_transitive_paths<1:
            raise DerivationValidationError("max_total_transitive_paths must be positive integer")
        self.ledger=ledger
        self.max_total_transitive_paths=max_total_transitive_paths

    def analyze_change(self, project_id:str, change:ImpactChange)->ImpactReport:
        if not isinstance(change,ImpactChange):
            raise DerivationValidationError("change must be ImpactChange")
        # A new version or replacement identity does not retroactively alter the old immutable entity.
        if change.change_kind in (ChangeKind.VERSION_UPGRADED,ChangeKind.IDENTITY_CHANGED):
            return ImpactReport(change,(),(),fail_closed_reason="NO_AUTOMATIC_RETROACTIVE_IMPACT")
        if change.change_kind == ChangeKind.UNKNOWN:
            return ImpactReport(change,(),(),partial=True,partial_depth=0,fail_closed_reason="UNKNOWN_CHANGE_KIND")
        return self._traverse(project_id,change,change.before)

    def analyze_dependency(self, project_id:str, source:VersionedRef)->ImpactReport:
        # Static dependency query, not a claim that a change occurred.
        synthetic=ImpactChange(source,source,ChangeKind.UNKNOWN)
        return self._traverse(project_id,synthetic,source)

    def _traverse(self,project_id:str,change:ImpactChange,source:VersionedRef)->ImpactReport:
        records=self.ledger.list(project_id)
        consumers:dict[tuple[str,str,int],list[tuple[DerivationRecord,VersionedRef]]]={}
        for rec in records:
            for inp in rec.inputs:
                consumers.setdefault((inp.entity_type,inp.entity_id,inp.version),[]).append((rec,inp))
        for bucket in consumers.values():
            bucket.sort(key=lambda x:(x[0].output.entity_type,x[0].output.entity_id,x[0].output.version,x[0].id))

        # Depth 1 is always collected completely before transitive limiting.
        paths_by_target:dict[VersionedRef,list[ImpactPath]]={}
        queue:list[ImpactPath]=[]
        cycles:set[tuple[tuple[Any,...],...]]=set()
        for rec,consumer_input in consumers.get((source.entity_type,source.entity_id,source.version),()):
            rel=next(r for r in rec.relations if r.from_ref==rec.output and r.to_ref==consumer_input)
            conf,reason=_edge_confidence(consumer_input,source)
            step=ImpactStep(source,rec.output,rec.id,rel.relation_type,rel.relation_domain,conf,reason)
            p=ImpactPath((step,))
            paths_by_target.setdefault(rec.output,[]).append(p); queue.append(p)

        transitive_count=0
        partial=False; partial_depth=None; fail_reason=None
        while queue:
            path=queue.pop(0)
            current=path.target
            path_nodes=(path.steps[0].source,)+tuple(s.target for s in path.steps)
            next_edges=consumers.get((current.entity_type,current.entity_id,current.version),())
            for rec,consumer_input in next_edges:
                rel=next(r for r in rec.relations if r.from_ref==rec.output and r.to_ref==consumer_input)
                conf,reason=_edge_confidence(consumer_input,current)
                step=ImpactStep(current,rec.output,rec.id,rel.relation_type,rel.relation_domain,conf,reason)
                if rec.output in path_nodes:
                    start=path_nodes.index(rec.output)
                    cycle_steps=path.steps[start:]+(step,)
                    cycles.add(_canonical_cycle(cycle_steps))
                    continue
                if transitive_count >= self.max_total_transitive_paths:
                    partial=True
                    partial_depth=max(1,path.depth)
                    fail_reason="MAX_TOTAL_TRANSITIVE_PATHS_EXCEEDED"
                    queue.clear()
                    break
                new_path=ImpactPath(path.steps+(step,))
                bucket=paths_by_target.setdefault(rec.output,[])
                sig=tuple(s.semantic_tuple()+(s.derivation_id,) for s in new_path.steps)
                if not any(tuple(s.semantic_tuple()+(s.derivation_id,) for s in old.steps)==sig for old in bucket):
                    bucket.append(new_path); queue.append(new_path); transitive_count+=1

        artifacts=[]
        for ref,paths in paths_by_target.items():
            paths=sorted(paths,key=lambda p:(p.depth,tuple(s.semantic_tuple()+(s.derivation_id,) for s in p.steps)))
            confidence=Confidence.UNCERTAIN if any(p.confidence==Confidence.UNCERTAIN for p in paths) else Confidence.CERTAIN
            derivs=tuple(sorted({s.derivation_id for p in paths for s in p.steps if s.target==ref}))
            artifacts.append(ImpactedArtifact(ref,min(p.depth for p in paths),confidence,derivs,tuple(paths)))
        artifacts.sort(key=lambda a:(a.min_depth,a.ref.entity_type,a.ref.entity_id,a.ref.version,a.ref.content_hash or ""))
        return ImpactReport(change,tuple(artifacts),tuple(sorted(cycles)),partial=partial,partial_depth=partial_depth,fail_closed_reason=fail_reason)

__all__=["ChangeKind","Confidence","ImpactChange","ImpactStep","ImpactPath","ImpactedArtifact","ImpactReport","ImpactAnalyzer"]
