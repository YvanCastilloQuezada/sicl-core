import pytest
from sicl.derivation import VersionedRef, TypedRelation, DerivationRecord, DerivationValidationError
from sicl.impact import *

H=lambda c: c*64
def ref(t,i,v,h=None): return VersionedRef(t,i,v,h)
def rec(i,out,inputs, domain="COMPUTATIONAL", rel="COMPUTED_FROM", assumptions=()):
    return DerivationRecord(i,out,tuple(inputs),"method","1",
        tuple(TypedRelation(out,x,rel,domain) for x in inputs),assumptions=assumptions)

class Ledger:
    def __init__(self,*records): self.records=list(records); self.calls=0
    def list(self,project_id): self.calls+=1; return list(self.records)

def content_change(r,after_hash):
    return ImpactChange(r,ref(r.entity_type,r.entity_id,r.version,after_hash),ChangeKind.CONTENT_CHANGED)

def chain(hash_inputs=True):
    g=ref("Geometry","G1",3,H("a"))
    gi=ref("Geometry","G1",3,H("a") if hash_inputs else None)
    a=ref("Area","A1",1,H("b")); q=ref("Quantity","Q1",2,H("c")); c=ref("Cost","C1",4,H("d"))
    return Ledger(rec("DA",a,[gi]),rec("DQ",q,[a]),rec("DC",c,[q])),g,a,q,c

def test_rt01_missing_hash_is_uncertain_not_invisible():
    l,g,a,q,c=chain(False)
    r=ImpactAnalyzer(l).analyze_change("P",content_change(g,H("e")))
    assert [x.ref for x in r.impacted_artifacts]==[a,q,c]
    assert r.impacted_artifacts[0].confidence==Confidence.UNCERTAIN
    assert r.impacted_artifacts[0].paths[0].steps[0].reason=="MISSING_CONTENT_HASH"

def test_exact_hash_is_certain():
    l,g,a,q,c=chain(True)
    r=ImpactAnalyzer(l).analyze_change("P",content_change(g,H("e")))
    assert r.impacted_artifacts[0].confidence==Confidence.CERTAIN

def test_rt03_version_upgrade_is_not_retroactive_impact():
    l,g,a,q,c=chain()
    ch=ImpactChange(g,ref("Geometry","G1",4,H("a")),ChangeKind.VERSION_UPGRADED)
    r=ImpactAnalyzer(l).analyze_change("P",ch)
    assert r.impacted_artifacts==()
    assert r.fail_closed_reason=="NO_AUTOMATIC_RETROACTIVE_IMPACT"

def test_identity_change_is_not_retroactive_impact():
    l,g,a,q,c=chain()
    ch=ImpactChange(g,ref("Geometry","G2",1,H("a")),ChangeKind.IDENTITY_CHANGED)
    assert ImpactAnalyzer(l).analyze_change("P",ch).impacted_artifacts==()

def test_invalid_change_kind_contract_rejected():
    g=ref("Geometry","G",1,H("a"))
    with pytest.raises(DerivationValidationError):
        ImpactChange(g,ref("Geometry","G",2,H("b")),ChangeKind.CONTENT_CHANGED)

def test_rt04_coverage_warning_is_always_explicit():
    l,g,*_=chain()
    r=ImpactAnalyzer(l).analyze_change("P",content_change(g,H("e")))
    assert r.coverage_warning=="GRAPH_MAY_BE_INCOMPLETE"
    assert r.canonical_dict()["coverageWarning"]=="GRAPH_MAY_BE_INCOMPLETE"

def test_no_impact_does_not_claim_complete_coverage():
    g=ref("Geometry","G",1,H("a"))
    r=ImpactAnalyzer(Ledger()).analyze_change("P",content_change(g,H("b")))
    assert r.impacted_artifacts==()
    assert r.coverage_warning=="GRAPH_MAY_BE_INCOMPLETE"

def test_join_preserves_all_paths_and_derivation_records():
    g=ref("Geometry","G",1,H("a")); a=ref("Area","A",1,H("b")); p=ref("Perimeter","P",1,H("c")); c=ref("Cost","C",1,H("d"))
    l=Ledger(rec("DA",a,[g]),rec("DP",p,[g]),rec("DC",c,[a,p]))
    r=ImpactAnalyzer(l).analyze_change("P",content_change(g,H("e")))
    ci=next(x for x in r.impacted_artifacts if x.ref==c)
    assert len(ci.paths)==2
    assert ci.derivation_records==("DC",)
    assert {tuple(s.derivation_id for s in path.steps) for path in ci.paths}=={("DA","DC"),("DP","DC")}

def test_rt05_path_limit_preserves_complete_depth_one():
    g=ref("Geometry","G",1,H("a"))
    direct=[ref("Metric",f"M{i}",1,H("b")) for i in range(20)]
    out=ref("Cost","C",1,H("c"))
    l=Ledger(*(rec(f"D{i}",m,[g]) for i,m in enumerate(direct)),rec("DOUT",out,direct))
    r=ImpactAnalyzer(l,max_total_transitive_paths=1).analyze_change("P",content_change(g,H("e")))
    depth1=[x for x in r.impacted_artifacts if x.min_depth==1]
    assert len(depth1)==20
    assert r.partial is True and r.fail_closed_reason=="MAX_TOTAL_TRANSITIVE_PATHS_EXCEEDED"
    assert r.partial_depth>=1

def test_mixed_domain_cycle_fingerprint_does_not_collapse():
    a=ref("X","A",1,H("a")); b=ref("X","B",1,H("b")); c=ref("X","C",1,H("c"))
    # Use DERIVED_FROM because it can represent multiple non-governance domains.
    l1=Ledger(rec("AB",b,[a],"COMPUTATIONAL","DERIVED_FROM"),rec("BC",c,[b],"COMPUTATIONAL","DERIVED_FROM"),rec("CA",a,[c],"COMPUTATIONAL","DERIVED_FROM"))
    l2=Ledger(rec("AB",b,[a],"EPISTEMIC","DERIVED_FROM"),rec("BC",c,[b],"NORMATIVE","DERIVED_FROM"),rec("CA",a,[c],"ARCHITECTURAL","DERIVED_FROM"))
    r1=ImpactAnalyzer(l1).analyze_dependency("P",a)
    r2=ImpactAnalyzer(l2).analyze_dependency("P",a)
    assert r1.cycles != r2.cycles
    assert r1.stable_fingerprint()!=r2.stable_fingerprint()

def test_cycle_rotation_is_canonical():
    a=ref("X","A",1,H("a")); b=ref("X","B",1,H("b")); c=ref("X","C",1,H("c"))
    l=Ledger(rec("AB",b,[a],"COMPUTATIONAL","DERIVED_FROM"),rec("BC",c,[b],"COMPUTATIONAL","DERIVED_FROM"),rec("CA",a,[c],"COMPUTATIONAL","DERIVED_FROM"))
    assert ImpactAnalyzer(l).analyze_dependency("P",a).cycles==ImpactAnalyzer(l).analyze_dependency("P",b).cycles

def test_assumptions_are_explicitly_not_traversable():
    g=ref("Geometry","Terrain",1,H("a")); a=ref("Area","A",1,H("b"))
    # Text assumption is intentionally not converted into a hidden edge.
    l=Ledger(rec("DA",a,[ref("Geometry","Other",1,H("c"))],assumptions=("terrain is flat",)))
    r=ImpactAnalyzer(l).analyze_dependency("P",g)
    assert r.impacted_artifacts==()
    assert r.assumptions_traversable is False
    assert r.coverage_warning=="GRAPH_MAY_BE_INCOMPLETE"

def test_order_and_fingerprint_are_deterministic():
    g=ref("Geometry","G",1,H("a")); a=ref("Area","A",1,H("b")); p=ref("Perimeter","P",1,H("c"))
    r1=ImpactAnalyzer(Ledger(rec("DP",p,[g]),rec("DA",a,[g]))).analyze_dependency("P",g)
    r2=ImpactAnalyzer(Ledger(rec("DA",a,[g]),rec("DP",p,[g]))).analyze_dependency("P",g)
    assert r1.canonical_dict()==r2.canonical_dict()
    assert r1.stable_fingerprint()==r2.stable_fingerprint()

def test_unknown_change_kind_fails_closed_without_traversal_claim():
    g=ref("Geometry","G",1,H("a")); other=ref("Geometry","G",1,H("b"))
    r=ImpactAnalyzer(Ledger()).analyze_change("P",ImpactChange(g,other,ChangeKind.UNKNOWN))
    assert r.partial and r.partial_depth==0 and r.fail_closed_reason=="UNKNOWN_CHANGE_KIND"

def test_impact_is_read_only():
    l,g,*_=chain(); before=list(l.records)
    ImpactAnalyzer(l).analyze_change("P",content_change(g,H("e")))
    assert l.records==before


def test_rt06_multiple_derivations_for_same_output_are_exposed_not_hidden():
    g1=ref("Geometry","G1",1,H("a")); g2=ref("Geometry","G2",1,H("b")); out=ref("Area","A",1,H("c"))
    # Simulates a legacy/concurrent ledger state H-001 normally rejects.
    l=Ledger(rec("D1",out,[g1]),rec("D2",out,[g2]))
    r1=ImpactAnalyzer(l).analyze_dependency("P",g1)
    r2=ImpactAnalyzer(l).analyze_dependency("P",g2)
    assert r1.impacted_artifacts[0].derivation_records==("D1",)
    assert r2.impacted_artifacts[0].derivation_records==("D2",)
    assert r1.coverage_warning=="GRAPH_MAY_BE_INCOMPLETE"

def test_rt11_overlapping_cycles_remain_distinct():
    a,b,c,d=[ref("X",x,1,H("a")) for x in "ABCD"]
    l=Ledger(
        rec("AB",b,[a],"COMPUTATIONAL","DERIVED_FROM"),
        rec("BC",c,[b],"COMPUTATIONAL","DERIVED_FROM"),
        rec("CA",a,[c],"COMPUTATIONAL","DERIVED_FROM"),
        rec("BD",d,[b],"COMPUTATIONAL","DERIVED_FROM"),
        rec("DA",a,[d],"COMPUTATIONAL","DERIVED_FROM"),
    )
    r=ImpactAnalyzer(l).analyze_dependency("P",a)
    assert len(r.cycles)==2
    assert r.cycles[0]!=r.cycles[1]

def test_report_contract_version_is_explicit():
    l,g,*_=chain()
    r=ImpactAnalyzer(l).analyze_dependency("P",g)
    assert r.contract_version==1
    assert r.canonical_dict()["contractVersion"]==1


def test_multiple_same_output_derivations_from_same_source_are_all_visible():
    g=ref("Geometry","G",1,H("a")); out=ref("Area","A",1,H("c"))
    l=Ledger(rec("D1",out,[g]),rec("D2",out,[g]))
    item=ImpactAnalyzer(l).analyze_dependency("P",g).impacted_artifacts[0]
    assert item.derivation_records==("D1","D2")
    assert len(item.paths)==2

def test_hash_conflict_is_uncertain_not_silently_dropped():
    source=ref("Geometry","G",1,H("a")); consumed=ref("Geometry","G",1,H("b")); out=ref("Area","A",1,H("c"))
    item=ImpactAnalyzer(Ledger(rec("D",out,[consumed]))).analyze_dependency("P",source).impacted_artifacts[0]
    assert item.confidence==Confidence.UNCERTAIN
    assert item.paths[0].steps[0].reason=="CONTENT_HASH_CONFLICT"
