import pytest
from sicl.archi import *
from sicl.derivation import TypedRelation, VersionedRef

def ids(): return ArchiElementId.compute('P','WALL','w'), ArchiElementId.compute('P','DOOR','d')
def test_relationship_id_stable_across_geometry():
    w,d=ids(); a=ArchiRelationship.create(RelationshipKind.HOSTED_IN,d,w); b=ArchiRelationship.create(RelationshipKind.HOSTED_IN,d,w); assert a.relationship_id==b.relationship_id

def test_h001_projection_uses_closed_vocabulary():
    w,d=ids(); rel=project_derived_from(VersionedRef('DOOR',d.value,1),VersionedRef('WALL',w.value,1)); assert rel.relation_type=='DERIVED_FROM' and rel.relation_domain=='ARCHITECTURAL'
    with pytest.raises(ValueError): TypedRelation(VersionedRef('DOOR',d.value,1),VersionedRef('WALL',w.value,1),'HOSTED_IN','ARCHITECTURAL')
