from sicl.archi import ArchiElementId, IfcGlobalId

def test_identity_stable_and_geometry_independent():
    assert ArchiElementId.compute('P','WALL','W-01') == ArchiElementId.compute('P','WALL','W-01')
    assert ArchiElementId.compute('P','WALL','W-01') != ArchiElementId.compute('P','WALL','W-02')
    assert IfcGlobalId.from_archi_id(ArchiElementId.compute('P','WALL','W-01')).value == IfcGlobalId.from_archi_id(ArchiElementId.compute('P','WALL','W-01')).value

def test_identity_source_has_no_runtime_randomness():
    source=open('src/sicl/archi/identity.py').read()
    assert 'uuid.uuid4' not in source and 'time.time' not in source and 'os.urandom' not in source
