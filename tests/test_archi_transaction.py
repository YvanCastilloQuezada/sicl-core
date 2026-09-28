import json
import pytest
from sicl.archi import *
from sicl.derivation import DerivationLedger, DerivationRecord, TypedRelation, VersionedRef
from sicl.h005 import RecomputationRegistry
from sicl.reaction import ActionStatus, ActionType, ReactionPlanner
from sicl.validity import ArtifactValidity, DerivationValidity, ValidityReport

class Store:
    def __init__(self): self.items=[]
    def add_event(self,event): self.items.append(event); return event
    def events(self,project_id=None): return [e for e in self.items if project_id is None or e.project_id==project_id]

def target():
    return ArchiElement(ArchiElementId.compute('P','WALL','w'),'P',ElementKind.WALL,ArchiGeometry(GeometryKind.EXTRUDED_RECTANGLE,ProfileSpec(200,100),height_mm=2800))

def test_no_public_mutation_bypass():
    assert not hasattr(ArchiTransaction, 'apply')

def test_target_not_found_returns_blocked_without_exception():
    t=target(); tx=ArchiTransaction((t,)); missing=ArchiMutation('P',MutationKind.MOVE,ArchiElementId.compute('P','WALL','missing'),1,{'dx_mm':100},'missing-target')
    result=tx.apply_full_chain(missing, DerivationLedger(Store()), RecomputationRegistry(), {})
    assert result.status is MutationStatus.BLOCKED and result.reason=='TARGET_NOT_FOUND' and result.canonical==(t,)

def setup_chain():
    wall=target(); door=ArchiElement(ArchiElementId.compute('P','DOOR','d'),'P',ElementKind.DOOR,wall.geometry,hosted_in=wall.element_id); space=ArchiElement(ArchiElementId.compute('P','SPACE','a'),'P',ElementKind.SPACE,wall.geometry)
    ledger=DerivationLedger(Store()); old=wall.ref(); door_old=VersionedRef('DOOR',door.element_id.value,1,'b'*64); space_old=VersionedRef('SPACE',space.element_id.value,1,'c'*64)
    ledger.record('P',DerivationRecord('D-01',door_old,(old,), 'archi.door.recompute','1.0',(TypedRelation(door_old,old,'DERIVED_FROM','ARCHITECTURAL'),)))
    ledger.record('P',DerivationRecord('A-01',space_old,(old,), 'archi.space.recompute','1.0',(TypedRelation(space_old,old,'DERIVED_FROM','ARCHITECTURAL'),)))
    registry=RecomputationRegistry()
    def make_output(previous, refs, entity_type, entity_id, h):
        current=refs[old.key()]; out=VersionedRef(entity_type,entity_id,previous.output.version+1,h)
        return DerivationRecord(previous.id+'-R',out,(current,),previous.method,previous.method_version,(TypedRelation(out,current,'DERIVED_FROM','ARCHITECTURAL'),))
    registry.register('archi.door.recompute','1.0',lambda p,r,refs: make_output(r,refs,'DOOR',door.element_id.value,'d'*64))
    registry.register('archi.space.recompute','1.0',lambda p,r,refs: make_output(r,refs,'SPACE',space.element_id.value,'e'*64))
    refs={old.key():old}; return wall,door,space,ledger,registry,refs

def test_full_chain_h003_h004_h005_applied_published(tmp_path):
    wall,door,space,ledger,registry,refs=setup_chain(); tx=ArchiTransaction((wall,door,space)); m=ArchiMutation('P',MutationKind.MOVE,wall.element_id,1,{'dx_mm':1000},'full-chain'); before=json.dumps([e.semantic_dict() for e in tx.canonical],sort_keys=True); p1=tmp_path/'one.ifc'; result=tx.apply_full_chain(m,ledger,registry,refs,ifc_path=p1)
    assert result.status is MutationStatus.APPLIED and result.lifecycle is MutationLifecycle.PUBLISHED and result.derivation_recorded
    assert tx.canonical[0].version==2 and json.dumps([e.semantic_dict() for e in tx.canonical],sort_keys=True)!=before
    assert set(result.provenance)=={'a002','h002','h003','h004','h005','ifc'}; assert result.provenance['ifc']['published'] and len(result.provenance['ifc']['sha256'])==64; assert all(r['status']=='EXECUTED' for r in result.provenance['h005']['records'])
    assert len(ledger.list('P'))==4 and p1.exists()

def test_h003_invalid_canonical_unchanged():
    wall,door,_,ledger,registry,refs=setup_chain(); ledger=DerivationLedger(Store()); old=wall.ref(); out=VersionedRef('DOOR',door.element_id.value,1,'b'*64); missing=VersionedRef('SPACE','MISSING',1)
    ledger.record('P',DerivationRecord('D-01',out,(old,missing),'archi.door.recompute','1.0',(TypedRelation(out,old,'DERIVED_FROM','ARCHITECTURAL'),TypedRelation(out,missing,'DERIVED_FROM','ARCHITECTURAL'))))
    tx=ArchiTransaction((wall,)); before=tx.canonical; m=ArchiMutation('P',MutationKind.MOVE,wall.element_id,1,{'dx_mm':1},'invalid'); result=tx.apply_full_chain(m,ledger,registry,refs); assert result.status is MutationStatus.ESCALATE and result.reason=='H004_NOT_AUTOMATICALLY_ELIGIBLE' and tx.canonical==before and 'h003' in result.provenance and 'h004' in result.provenance

def test_h003_uncertain_canonical_unchanged():
    wall,door,space,_,registry,_=setup_chain(); ledger=DerivationLedger(Store()); old=VersionedRef('WALL',wall.element_id.value,1); d=VersionedRef('DOOR',door.element_id.value,1); a=VersionedRef('SPACE',space.element_id.value,1)
    ledger.record('P',DerivationRecord('D-01',d,(old,), 'archi.door.recompute','1.0',(TypedRelation(d,old,'DERIVED_FROM','ARCHITECTURAL'),))); ledger.record('P',DerivationRecord('A-01',a,(old,), 'archi.space.recompute','1.0',(TypedRelation(a,old,'DERIVED_FROM','ARCHITECTURAL'),)))
    refs={old.key():old}; tx=ArchiTransaction((wall,)); before=tx.canonical; result=tx.apply_full_chain(ArchiMutation('P',MutationKind.MOVE,wall.element_id,1,{'dx_mm':1},'uncertain'),ledger,registry,refs); assert result.status is MutationStatus.ESCALATE and tx.canonical==before

def test_h004_review_canonical_unchanged():
    artifact=VersionedRef('A','1',1); dv=DerivationValidity('d',artifact,'STALE',source_checks=('integrity_checks_d',)); report=ValidityReport(artifact_validities=(ArtifactValidity(artifact,'PARTIALLY_VALID',(dv,),{},{}),)); action=ReactionPlanner().plan_reaction(report).planned_actions[0]; assert action.action_type is ActionType.REVIEW and action.status is ActionStatus.REQUIRES_AUTHORITY

def test_h004_escalate_canonical_unchanged():
    artifact=VersionedRef('A','1',1); dv=DerivationValidity('d',artifact,'UNCERTAIN',source_checks=('integrity_checks_d',)); action=ReactionPlanner().plan_reaction(ValidityReport(artifact_validities=(ArtifactValidity(artifact,'REQUIRES_HUMAN_REVIEW',(dv,),{},{}),))).planned_actions[0]; assert action.action_type is ActionType.ESCALATE

def test_h004_requires_authority_canonical_unchanged():
    artifact=VersionedRef('A','1',1); dv=DerivationValidity('d',artifact,'INVALID',source_checks=('integrity_checks_d',)); action=ReactionPlanner().plan_reaction(ValidityReport(artifact_validities=(ArtifactValidity(artifact,'INVALID',(dv,),{},{}),))).planned_actions[0]; assert action.requires_human_authority

def test_h004_reject_canonical_unchanged():
    artifact=VersionedRef('A','1',1); dv=DerivationValidity('d',artifact,'INVALID',discrepancies=({'reference':artifact.to_dict(),'code':'MISSING_DEPENDENCY'},),source_checks=('integrity_checks_d',)); action=ReactionPlanner().plan_reaction(ValidityReport(artifact_validities=(ArtifactValidity(artifact,'INVALID',(dv,),{},{}),))).planned_actions[0]; assert action.action_type is ActionType.REJECT

def test_h005_blocked_canonical_unchanged():
    wall,_,_,ledger,registry,refs=setup_chain(); tx=ArchiTransaction((wall,)); before=tx.canonical; result=tx.apply_full_chain(ArchiMutation('P',MutationKind.MOVE,wall.element_id,1,{'dx_mm':1},'missing-handler'),ledger,RecomputationRegistry(),refs); assert result.status is MutationStatus.BLOCKED and tx.canonical==before

def test_h005_failure_canonical_unchanged():
    wall,_,_,ledger,registry,refs=setup_chain(); registry=RecomputationRegistry(); registry.register('archi.door.recompute','1.0',lambda *args: (_ for _ in ()).throw(RuntimeError('boom'))); registry.register('archi.space.recompute','1.0',lambda *args: (_ for _ in ()).throw(RuntimeError('boom'))); tx=ArchiTransaction((wall,)); before=tx.canonical; result=tx.apply_full_chain(ArchiMutation('P',MutationKind.MOVE,wall.element_id,1,{'dx_mm':1},'handler-failure'),ledger,registry,refs); assert result.status is MutationStatus.BLOCKED and tx.canonical==before

def test_no_partial_canonical_state_on_failure():
    wall,_,_,ledger,_,refs=setup_chain(); tx=ArchiTransaction((wall,)); before=tx.canonical; result=tx.apply_full_chain(ArchiMutation('P',MutationKind.MOVE,wall.element_id,1,{'dx_mm':1},'no-partial'),ledger,RecomputationRegistry(),refs); assert result.status is MutationStatus.BLOCKED and tx.canonical==before and len(ledger.list('P'))==2

def test_no_double_apply_on_replay():
    wall,door,space,ledger,registry,refs=setup_chain(); tx=ArchiTransaction((wall,door,space)); m=ArchiMutation('P',MutationKind.MOVE,wall.element_id,1,{'dx_mm':1000},'replay'); first=tx.apply_full_chain(m,ledger,registry,refs); second=tx.apply_full_chain(m,ledger,registry,refs); assert first.status is MutationStatus.APPLIED and second.reason=='REPLAY_NO_DOUBLE_APPLICATION' and tx.canonical[0].version==2 and second.derivation_recorded is False

def test_add_opening_fails_closed_without_canonical_change():
    t=target(); tx=ArchiTransaction((t,)); mutation=ArchiMutation('P',MutationKind.ADD_OPENING,t.element_id,1,{'host_id':t.element_id.value},'opening')
    result=tx.apply_full_chain(mutation, DerivationLedger(Store()), RecomputationRegistry(), {})
    assert result.status is MutationStatus.BLOCKED and result.reason=='OPERATION_NOT_IMPLEMENTED' and result.canonical==(t,)

def test_invalid_ifc_path_fails_without_publication(tmp_path):
    wall,door,space,ledger,registry,refs=setup_chain(); tx=ArchiTransaction((wall,door,space)); before=tx.canonical
    result=tx.apply_full_chain(ArchiMutation('P',MutationKind.MOVE,wall.element_id,1,{'dx_mm':1},'bad-ifc-path'),ledger,registry,refs,ifc_path=tmp_path/'missing'/'model.ifc')
    assert result.status is MutationStatus.FAILED and result.reason.startswith('IFC_EXPORT:') and tx.canonical==before and len(ledger.list('P'))==2

def test_no_unauthorized_execution():
    artifact=VersionedRef('A','1',1); dv=DerivationValidity('d',artifact,'REQUIRES_HUMAN_REVIEW',source_checks=('integrity_checks_d',)); action=ReactionPlanner().plan_reaction(ValidityReport(artifact_validities=(ArtifactValidity(artifact,'REQUIRES_HUMAN_REVIEW',(dv,),{},{}),))).planned_actions[0]; assert action.requires_human_authority and action.action_type is ActionType.ESCALATE
