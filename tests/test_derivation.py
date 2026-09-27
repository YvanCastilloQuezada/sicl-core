from __future__ import annotations
import pytest
from sicl.domain import Event
from sicl.derivation import DerivationLedger,DerivationRecord,DerivationValidationError,TypedRelation,VersionedRef

class MemoryStore:
    def __init__(self): self.items=[]
    def add_event(self,event): self.items.append(event); return event
    def events(self,project_id=None): return [x for x in self.items if project_id is None or x.project_id==project_id]

def ref(t,i,v): return VersionedRef(t,i,v)
def record(rid,out,inputs,relation_type="COMPUTED_FROM",domain="COMPUTATIONAL"):
    return DerivationRecord(rid,out,tuple(inputs),"controlled_method","1.0",tuple(TypedRelation(out,x,relation_type,domain) for x in inputs))

def test_ref_roundtrip_validation_and_normalization():
    x=ref(" Geometry "," G1 ",3); assert x.to_dict()=={"entityType":"Geometry","entityId":"G1","version":3}; assert VersionedRef.from_dict(x.to_dict())==x
    for bad in ["3",0,-1,True]:
        with pytest.raises(DerivationValidationError): VersionedRef("Geometry","G1",bad)

def test_relation_direction_is_unambiguous():
    area,geo=ref("Area","A1",1),ref("Geometry","G1",3)
    r=TypedRelation(area,geo,"COMPUTED_FROM","COMPUTATIONAL"); assert TypedRelation.from_dict(r.to_dict())==r
    with pytest.raises(DerivationValidationError): TypedRelation(area,geo,"SUPPORTED_BY","ARCHITECTURAL")

def test_record_rejects_reversed_relation_duplicate_input_self_input_and_extra_edge():
    a,g,q=ref("Area","A1",1),ref("Geometry","G1",3),ref("Quantity","Q1",1)
    with pytest.raises(DerivationValidationError): DerivationRecord("D",a,(g,),"m","1",(TypedRelation(g,a,"COMPUTED_FROM","COMPUTATIONAL"),))
    with pytest.raises(DerivationValidationError): record("D",a,[g,g])
    with pytest.raises(DerivationValidationError): record("D",a,[a])
    with pytest.raises(DerivationValidationError): DerivationRecord("D",a,(g,),"m","1",(TypedRelation(a,g,"COMPUTED_FROM","COMPUTATIONAL"),TypedRelation(a,q,"COMPUTED_FROM","COMPUTATIONAL")))

def test_roundtrip_fingerprint_deterministic():
    x=record("D-A",ref("Area","A1",1),[ref("Geometry","G1",3)]); y=DerivationRecord.from_dict(x.to_dict()); assert y==x; assert y.stable_fingerprint()==x.stable_fingerprint()

def test_computational_why_and_leaf_inputs():
    s=MemoryStore(); l=DerivationLedger(s); g=ref("Geometry","G1",3); a=ref("RoomArea","A1",1); q=ref("Quantity","Q1",2); c=ref("Cost","C1",4)
    for r in [record("D-A",a,[g]),record("D-Q",q,[a]),record("D-C",c,[q])]: l.record("P1",r)
    e=l.explain("P1",c); assert [x["id"] for x in e["records"]]==["D-C","D-Q","D-A"]; assert e["leaf_inputs"]==[g.to_dict()]; assert len(s.items)==3

def test_epistemic_why_uses_supported_by_and_derived_from():
    s=MemoryStore(); l=DerivationLedger(s); src=ref("Source","S1",1); ev=ref("Evidence","E1",2); cl=ref("Claim","C1",1); h=ref("Hypothesis","H1",3)
    l.record("P",record("D-E",ev,[src],"DERIVED_FROM","EPISTEMIC")); l.record("P",record("D-C",cl,[ev],"SUPPORTED_BY","EPISTEMIC")); l.record("P",record("D-H",h,[cl],"SUPPORTED_BY","EPISTEMIC"))
    assert [x.id for x in l.why("P",h)]==["D-H","D-C","D-E"]

def test_cycle_is_bounded_but_does_not_mutate():
    s=MemoryStore(); l=DerivationLedger(s); a=ref("Area","A",1); q=ref("Quantity","Q",1); l.record("P",record("DA",a,[q])); l.record("P",record("DQ",q,[a])); assert len(l.why("P",a))==2; assert len(s.items)==2

def test_record_is_idempotent_conflicting_id_rejected_but_independent_output_derivation_allowed():
    s=MemoryStore(); l=DerivationLedger(s); a=ref("Area","A",1); g=ref("Geometry","G",1); r=record("D",a,[g]); l.record("P",r); l.record("P",r); assert len(s.items)==1
    with pytest.raises(DerivationValidationError): l.record("P",record("D",ref("Area","A2",1),[g]))
    l.record("P",record("D2",a,[ref("Geometry","G2",1)]))
    assert [item.id for item in l.why("P",a)] == ["D", "D2"]

def test_dependency_checks_distinguish_missing_and_version_mismatch_without_stale_inference():
    s=MemoryStore(); l=DerivationLedger(s); g=ref("Geometry","G1",3); a=ref("Area","A1",1); l.record("P",record("D",a,[g]))
    assert l.dependency_checks("P",{})==[{"record_id":"D","reference":g.to_dict(),"code":"MISSING_DEPENDENCY"}]
    x=l.dependency_checks("P",{("Geometry","G1"):4}); assert x[0]["code"]=="VERSION_MISMATCH" and "stale" not in str(x).lower(); assert len(s.items)==1

def test_project_scoping():
    s=MemoryStore(); l=DerivationLedger(s); a=ref("Area","A",1); g=ref("Geometry","G",1); l.record("P1",record("D1",a,[g])); l.record("P2",record("D2",a,[g])); assert [x.id for x in l.why("P1",a)]==["D1"]


def test_content_hash_detects_same_version_content_corruption_without_action():
    s=MemoryStore(); l=DerivationLedger(s)
    h1="a"*64; h2="b"*64
    g=VersionedRef("Geometry","G1",3,h1); a=ref("Area","A1",1)
    l.record("P",record("D",a,[g]))
    checks=l.integrity_checks("P",{("Geometry","G1"):VersionedRef("Geometry","G1",3,h2)})
    assert checks[0]["code"]=="CONTENT_HASH_MISMATCH"
    assert len(s.items)==1

def test_content_hash_is_optional_backward_compatible_and_validated():
    legacy=ref("Geometry","G1",3)
    assert "contentHash" not in legacy.to_dict()
    hashed=VersionedRef("Geometry","G1",3,"a"*64)
    assert VersionedRef.from_dict(hashed.to_dict())==hashed
    with pytest.raises(DerivationValidationError): VersionedRef("Geometry","G1",3,"BAD")


def test_historical_malformed_derivation_event_fails_closed():
    store = MemoryStore()
    store.items.append(Event(None, "2026-01-01T00:00:00+00:00", "P1", "DERIVATION_RECORDED", {"wrong": {}}, "x", "x"))
    ledger = DerivationLedger(store)
    with pytest.raises(DerivationValidationError):
        ledger.list("P1")


def test_assumptions_are_canonical_and_unique():
    g, a = ref("Geometry", "G1", 1), ref("Area", "A1", 1)
    item = DerivationRecord("D", a, (g,), "m", "1", (TypedRelation(a, g, "COMPUTED_FROM", "COMPUTATIONAL"),), assumptions=("  controlled assumption  ",))
    assert item.assumptions == ("controlled assumption",)
    with pytest.raises(DerivationValidationError):
        DerivationRecord("D2", a, (g,), "m", "1", (TypedRelation(a, g, "COMPUTED_FROM", "COMPUTATIONAL"),), assumptions=("x", " x "))


def test_stable_fingerprint_is_independent_of_dependency_order():
    g1, g2, out = ref("Geometry", "G1", 1), ref("Geometry", "G2", 1), ref("Area", "A1", 1)
    r1 = DerivationRecord("D", out, (g1,g2), "m", "1",
        (TypedRelation(out,g1,"COMPUTED_FROM","COMPUTATIONAL"), TypedRelation(out,g2,"COMPUTED_FROM","COMPUTATIONAL")),
        assumptions=("b","a"))
    r2 = DerivationRecord("D", out, (g2,g1), "m", "1",
        (TypedRelation(out,g2,"COMPUTED_FROM","COMPUTATIONAL"), TypedRelation(out,g1,"COMPUTED_FROM","COMPUTATIONAL")),
        assumptions=("a","b"))
    assert r1.stable_fingerprint() == r2.stable_fingerprint()


def test_unknown_schema_fields_fail_closed():
    raw = ref("Geometry","G1",1).to_dict()
    raw["futureMagic"] = True
    with pytest.raises(DerivationValidationError):
        VersionedRef.from_dict(raw)


def test_derivation_contract_version_is_explicit_and_fail_closed():
    item = record("D", ref("Area","A1",1), [ref("Geometry","G1",1)])
    raw = item.to_dict()
    assert raw["contractVersion"] == 1
    raw["contractVersion"] = 2
    with pytest.raises(DerivationValidationError):
        DerivationRecord.from_dict(raw)


def test_multiple_independent_derivations_for_same_output_are_preserved():
    store = MemoryStore()
    ledger = DerivationLedger(store)
    g1, g2 = ref("Geometry", "G1", 1), ref("Geometry", "G2", 1)
    a = ref("Area", "A1", 1)
    ledger.record("P1", record("D1", a, [g1]))
    ledger.record("P1", record("D2", a, [g2]))
    why = ledger.why("P1", a)
    assert [item.id for item in why] == ["D1", "D2"]
    assert {item.inputs[0] for item in why} == {g1, g2}


def test_identity_gap_is_explicit_when_hashes_absent():
    store = MemoryStore()
    ledger = DerivationLedger(store)
    g = ref("Geometry", "G1", 1)
    a = ref("Area", "A1", 1)
    ledger.record("P", record("D", a, [g]))
    checks = ledger.integrity_checks("P", {g.key(): ref("Geometry", "G1", 1)})
    assert checks == [{
        "record_id": "D",
        "reference": g.to_dict(),
        "current": g.to_dict(),
        "code": "IDENTITY_UNVERIFIABLE",
    }]


def test_identity_gap_is_uncertain_when_only_one_side_has_hash():
    store = MemoryStore()
    ledger = DerivationLedger(store)
    g = VersionedRef("Geometry", "G1", 1, "a" * 64)
    a = ref("Area", "A1", 1)
    ledger.record("P", record("D", a, [g]))
    current = ref("Geometry", "G1", 1)
    checks = ledger.integrity_checks("P", {g.key(): current})
    assert checks[0]["code"] == "IDENTITY_UNCERTAIN"
