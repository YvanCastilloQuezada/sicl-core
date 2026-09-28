from sicl.archi import *
def target(): return ArchiElement(ArchiElementId.compute('P','WALL','w'),'P',ElementKind.WALL,ArchiGeometry(GeometryKind.EXTRUDED_RECTANGLE,ProfileSpec(200,100),height_mm=2800))
def test_move_uses_archi_operation_and_allows():
    t=target(); m=ArchiMutation('P',MutationKind.MOVE,t.element_id,t.version,{'dx_mm':100},'n'); s=snapshot_for(m,t); assert s.operation=='archi.move' and s.permits
def test_delete_requires_authority_and_blocks():
    t=target(); m=ArchiMutation('P',MutationKind.DELETE,t.element_id,t.version,{},'n'); s=snapshot_for(m,t); assert s.operation=='archi.delete' and not s.permits
