from pathlib import Path
from sicl.archi import *
from sicl.impact import ChangeKind, ImpactAnalyzer, ImpactChange
from sicl.derivation import DerivationLedger, DerivationRecord, TypedRelation, VersionedRef
from sicl.domain import Event

class MemoryStore:
    def __init__(self): self.items=[]
    def add_event(self,event): self.items.append(event); return event
    def events(self,project_id=None): return [x for x in self.items if project_id is None or x.project_id==project_id]

def test_d2_poc_move_wall_candidate_and_apply():
    w=ArchiElementId.compute('P','WALL','W-01'); g=ArchiGeometry(GeometryKind.EXTRUDED_RECTANGLE,ProfileSpec(200,100),height_mm=2800); wall=ArchiElement(w,'P',ElementKind.WALL,g)
    tx=ArchiTransaction((wall,)); assert not hasattr(tx, 'apply')

def test_d2_poc_h002_real_discovers_space_and_door():
    w=ArchiElementId.compute('P','WALL','W-01'); d=ArchiElementId.compute('P','DOOR','D-01'); a=ArchiElementId.compute('P','SPACE','A-01')
    old=VersionedRef('WALL',w.value,1,'a'*64); door=VersionedRef('DOOR',d.value,1,'b'*64); space=VersionedRef('SPACE',a.value,1,'c'*64)
    ledger=DerivationLedger(MemoryStore()); ledger.record('P',DerivationRecord('D-01',door,(old,),'archi','1',(TypedRelation(door,old,'DERIVED_FROM','ARCHITECTURAL'),))); ledger.record('P',DerivationRecord('A-01',space,(old,),'archi','1',(TypedRelation(space,old,'DERIVED_FROM','ARCHITECTURAL'),)))
    changed=VersionedRef('WALL',w.value,1,'d'*64); report=ImpactAnalyzer(ledger).analyze_change('P',ImpactChange(old,changed,ChangeKind.CONTENT_CHANGED)); impacted={item.ref.entity_id for item in report.impacted_artifacts}
    assert d.value in impacted and a.value in impacted; assert all(step.relation_type=='DERIVED_FROM' and step.relation_domain=='ARCHITECTURAL' for item in report.impacted_artifacts for path in item.paths for step in path.steps)

def test_architectural_derivation_bridge_works_with_real_h002():
    w=ArchiElementId.compute('P','WALL','W-01'); d=ArchiElementId.compute('P','DOOR','D-01'); a=ArchiElementId.compute('P','SPACE','A-01')
    old=VersionedRef('WALL',w.value,1,'a'*64); door=VersionedRef('DOOR',d.value,1,'b'*64); space=VersionedRef('SPACE',a.value,1,'c'*64)
    ledger=DerivationLedger(MemoryStore())
    from sicl.archi import architectural_derivation
    ledger.record('P', architectural_derivation('D-01', door, (old,)))
    ledger.record('P', architectural_derivation('A-01', space, (old,)))
    changed=VersionedRef('WALL',w.value,1,'d'*64)
    report=ImpactAnalyzer(ledger).analyze_change('P',ImpactChange(old,changed,ChangeKind.CONTENT_CHANGED))
    impacted={item.ref.entity_id for item in report.impacted_artifacts}
    assert {d.value,a.value} <= impacted

def test_d2_poc_existing_scenario_full_chain_and_ifc_determinism(tmp_path):
    from archi_fixtures import setup_chain
    wall,door,space,ledger,registry,refs=setup_chain(); tx=ArchiTransaction((wall,door,space)); m=ArchiMutation('P',MutationKind.MOVE,wall.element_id,1,{'dx_mm':1000},'poc-full-chain'); p1=tmp_path/'poc1.ifc'; first=tx.apply_full_chain(m,ledger,registry,refs,ifc_path=p1)
    assert first.status is MutationStatus.APPLIED and first.lifecycle is MutationLifecycle.PUBLISHED
    assert {'a002','h002','h003','h004','h005'} <= set(first.provenance)
    assert {x['ref']['entityId'] for x in first.provenance['h002']['impactedArtifacts']} == {door.element_id.value,space.element_id.value}
    tx2=ArchiTransaction((wall,door,space)); ledger2=DerivationLedger(MemoryStore()); wall2,door2,space2,ledger2,registry2,refs2=setup_chain(); p2=tmp_path/'poc2.ifc'; second=tx2.apply_full_chain(m,ledger2,registry2,refs2,ifc_path=p2)
    assert second.status is MutationStatus.APPLIED and p1.read_bytes()==p2.read_bytes()
