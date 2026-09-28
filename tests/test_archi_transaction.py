from sicl.archi import *
def target(): return ArchiElement(ArchiElementId.compute('P','WALL','w'),'P',ElementKind.WALL,ArchiGeometry(GeometryKind.EXTRUDED_RECTANGLE,ProfileSpec(200,100),height_mm=2800))
def test_blocked_preserves_canonical_and_replay_is_idempotent():
    t=target(); tx=ArchiTransaction((t,)); delete=ArchiMutation('P',MutationKind.DELETE,t.element_id,1,{},'d'); blocked=tx.apply(delete); assert blocked.status is MutationStatus.BLOCKED and tx.canonical==(t,)
    move=ArchiMutation('P',MutationKind.MOVE,t.element_id,1,{'dx_mm':100},'m'); applied=tx.apply(move); assert applied.status is MutationStatus.APPLIED and applied.canonical[0].version==2; replay=tx.apply(move); assert replay.reason=='REPLAY_NO_DOUBLE_APPLICATION' and len(tx.canonical)==1
