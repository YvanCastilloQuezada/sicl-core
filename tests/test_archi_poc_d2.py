from sicl.archi import *
from sicl.impact import ChangeKind, ImpactAnalyzer, ImpactChange
from sicl.derivation import DerivationLedger, VersionedRef
from sicl.domain import Event

class MemoryStore:
    def __init__(self): self.items=[]
    def add_event(self,event): self.items.append(event); return event
    def events(self,project_id=None): return [x for x in self.items if project_id is None or x.project_id==project_id]

def test_d2_poc_move_wall_candidate_and_apply():
    w=ArchiElementId.compute('P','WALL','W-01'); g=ArchiGeometry(GeometryKind.EXTRUDED_RECTANGLE,ProfileSpec(200,100),height_mm=2800); wall=ArchiElement(w,'P',ElementKind.WALL,g)
    tx=ArchiTransaction((wall,)); mutation=ArchiMutation('P',MutationKind.MOVE,w,1,{'dx_mm':1000},'poc-1'); result=tx.apply(mutation)
    assert result.status is MutationStatus.APPLIED; assert result.canonical[0].geometry.x_mm==1000; assert result.canonical[0].version==2; assert tx.apply(mutation).reason=='REPLAY_NO_DOUBLE_APPLICATION'

def test_d2_poc_h002_real_discovers_space_and_door():
    w=ArchiElementId.compute('P','WALL','W-01'); d=ArchiElementId.compute('P','DOOR','D-01'); a=ArchiElementId.compute('P','SPACE','A-01')
    old=VersionedRef('WALL',w.value,1,'a'*64); door=VersionedRef('DOOR',d.value,1,'b'*64); space=VersionedRef('SPACE',a.value,1,'c'*64)
    ledger=DerivationLedger(MemoryStore())
    ledger.record('P', architectural_derivation('D-01',door,(old,)))
    ledger.record('P', architectural_derivation('A-01',space,(old,)))
    changed=VersionedRef('WALL',w.value,1,'d'*64)
    report=ImpactAnalyzer(ledger).analyze_change('P',ImpactChange(old,changed,ChangeKind.CONTENT_CHANGED))
    impacted={item.ref.entity_id for item in report.impacted_artifacts}
    assert d.value in impacted and a.value in impacted
    assert all(step.relation_type=='DERIVED_FROM' and step.relation_domain=='ARCHITECTURAL' for item in report.impacted_artifacts for path in item.paths for step in path.steps)
