from dataclasses import replace
from sicl.archi import *
def test_mutation_id_ignores_provenance_timestamp():
    t=ArchiElementId.compute('P','WALL','w'); a=ArchiMutation('P',MutationKind.MOVE,t,1,{'dx_mm':100},'n','2026-01-01'); b=replace(a,requested_at_iso='2027-01-01'); assert a.compute_id()==b.compute_id()
def test_nonce_changes_identity_and_payload_is_canonical():
    t=ArchiElementId.compute('P','WALL','w'); a=ArchiMutation('P',MutationKind.MOVE,t,1,{'b':2,'a':1},'n'); b=replace(a,request_nonce='m'); assert a.compute_id()!=b.compute_id(); assert list(a.canonical_dict()['canonical_payload'])==['b','a']
