import json, pytest
from sicl.derivation import DerivationLedger, DerivationRecord, TypedRelation, VersionedRef, DerivationValidationError
from sicl.impact import ImpactAnalyzer, ImpactChange, ChangeKind
from sicl.domain import Event

class Store:
    def __init__(self): self.items=[]
    def add_event(self,e): self.items.append(e); return e
    def events(self,project_id=None): return [x for x in self.items if project_id is None or x.project_id==project_id]

def ref(t,i,v,h=None): return VersionedRef(t,i,v,h)
def rec(i,out,ins):
    return DerivationRecord(i,out,tuple(ins),"m","1",tuple(TypedRelation(out,x,"COMPUTED_FROM","COMPUTATIONAL") for x in ins))

# RT-63 FIX: Verificación estricta de paths, no solo 'any()'
def test_e4_same_output_multiple_justifications_preserved_in_why_and_impact():
    s=Store(); l=DerivationLedger(s)
    g1,g2=ref("Geometry","G1",1),ref("Geometry","G2",1)
    a=ref("Area","A",1); c=ref("Cost","C",1)
    l.record("P",rec("DA1",a,[g1])); l.record("P",rec("DA2",a,[g2])); l.record("P",rec("DC",c,[a]))
    assert [x.id for x in l.why("P",a)]==["DA1","DA2"]

    r1=ImpactAnalyzer(l).analyze_dependency("P",g1)
    r2=ImpactAnalyzer(l).analyze_dependency("P",g2)

    # Verificación estricta de que los derivation_records están correctamente atribuidos
    a_impact_r1 = next(x for x in r1.impacted_artifacts if x.ref == a)
    a_impact_r2 = next(x for x in r2.impacted_artifacts if x.ref == a)
    assert "DA1" in a_impact_r1.derivation_records
    assert "DA2" in a_impact_r2.derivation_records

def test_e5_identity_states_are_mutually_explicit():
    s=Store(); l=DerivationLedger(s); h1="a"*64; h2="b"*64
    cases=[
        (ref("Geometry","A",1),ref("Geometry","A",1),"IDENTITY_UNVERIFIABLE"),
        (ref("Geometry","B",1,h1),ref("Geometry","B",1),"IDENTITY_UNCERTAIN"),
        (ref("Geometry","C",1,h1),ref("Geometry","C",1,h2),"CONTENT_HASH_MISMATCH"),
        (ref("Geometry","D",1,h1),ref("Geometry","D",2,h1),"VERSION_MISMATCH"),
    ]
    for n,(expected,current,code) in enumerate(cases):
        out=ref("Metric",f"M{n}",1); l.record("P",rec(f"D{n}",out,[expected]))
    current={expected.key():current for expected,current,_ in cases}
    codes={x["record_id"]:x["code"] for x in l.integrity_checks("P",current)}
    assert codes=={f"D{i}":case[2] for i,case in enumerate(cases)}

def test_e6_identical_hash_and_version_produces_no_integrity_issue():
    s=Store(); l=DerivationLedger(s); h="a"*64; g=ref("Geometry","G",1,h); a=ref("Area","A",1)
    l.record("P",rec("D",a,[g]))
    assert l.integrity_checks("P",{g.key():g})==[]

def test_e7_historical_conflicting_same_id_fails_closed():
    s=Store(); l=DerivationLedger(s); a=ref("Area","A",1)
    r1=rec("D",a,[ref("Geometry","G1",1)]); r2=rec("D",a,[ref("Geometry","G2",1)])
    s.items += [
      Event(None,"t","P","DERIVATION_RECORDED",{"derivation":r1.to_dict()},"x","x"),
      Event(None,"t","P","DERIVATION_RECORDED",{"derivation":r2.to_dict()},"x","x")]
    with pytest.raises(DerivationValidationError): l.list("P")

def test_e8_report_serialization_is_deterministic():
    s=Store(); l=DerivationLedger(s); g=ref("Geometry","G",1); a=ref("Area","A",1)
    l.record("P",rec("D",a,[g])); analyzer=ImpactAnalyzer(l)
    one=json.dumps(analyzer.analyze_dependency("P",g).canonical_dict(),sort_keys=True,separators=(",",":"))
    two=json.dumps(analyzer.analyze_dependency("P",g).canonical_dict(),sort_keys=True,separators=(",",":"))
    assert one==two

def test_e9_analysis_is_strictly_read_only_even_repeated():
    s=Store(); l=DerivationLedger(s); g=ref("Geometry","G",1); a=ref("Area","A",1)
    l.record("P",rec("D",a,[g])); before=[x for x in s.items]
    for _ in range(10): ImpactAnalyzer(l).analyze_dependency("P",g)
    assert s.items==before and len(s.items)==1

def test_e10_changed_version_does_not_alias_old_exact_reference():
    s=Store(); l=DerivationLedger(s); old=ref("Geometry","G",1); new=ref("Geometry","G",2); a=ref("Area","A",1)
    l.record("P",rec("D",a,[old]))
    assert ImpactAnalyzer(l).analyze_dependency("P",new).impacted_artifacts==()
    assert [x.ref for x in ImpactAnalyzer(l).analyze_dependency("P",old).impacted_artifacts]==[a]

# RT-62 FIX: Tests adicionales para cubrir vectores RT faltantes
def test_e11_change_kind_content_vs_version_vs_identity():
    """RT-03: change_kind distingue contenido, versión e identidad."""
    s=Store(); l=DerivationLedger(s)
    g=ref("Geometry","G",1,"a"*64)
    l.record("P",rec("D",ref("Area","A",1),[g]))

    # CONTENT_CHANGED: misma identidad, mismo version, distinto hash
    ch_content = ImpactChange(g, ref("Geometry","G",1,"b"*64), ChangeKind.CONTENT_CHANGED)
    r_content = ImpactAnalyzer(l).analyze_change("P", ch_content)
    assert len(r_content.impacted_artifacts) == 1

    # VERSION_UPGRADED: no impacta retroactivamente
    ch_version = ImpactChange(g, ref("Geometry","G",2,"a"*64), ChangeKind.VERSION_UPGRADED)
    r_version = ImpactAnalyzer(l).analyze_change("P", ch_version)
    assert r_version.impacted_artifacts == ()
    assert r_version.fail_closed_reason == "NO_AUTOMATIC_RETROACTIVE_IMPACT"

def test_e12_coverage_warning_semantic():
    """RT-04: coverage_warning es explícito incluso sin impacto."""
    s=Store(); l=DerivationLedger(s)
    g=ref("Geometry","G",1,"a"*64)
    ch = ImpactChange(g, ref("Geometry","G",1,"b"*64), ChangeKind.CONTENT_CHANGED)
    r = ImpactAnalyzer(l).analyze_change("P", ch)
    assert r.coverage_warning == "GRAPH_MAY_BE_INCOMPLETE"
    assert r.impacted_artifacts == ()

def test_e13_path_explosion_partial_report():
    """RT-05: path explosion con partial/partialDepth."""
    s=Store(); l=DerivationLedger(s)
    g=ref("Geometry","G",1,"a"*64)
    mids=[ref("Metric",f"M{i}",1,"b"*64) for i in range(5)]
    out=ref("Cost","C",1,"c"*64)
    for i,m in enumerate(mids): l.record("P",rec(f"D{i}",m,[g]))
    l.record("P",rec("DC",out,mids))

    r = ImpactAnalyzer(l, max_total_transitive_paths=2).analyze_change("P", ImpactChange(g, ref("Geometry","G",1,"d"*64), ChangeKind.CONTENT_CHANGED))
    assert r.partial is True
    assert r.fail_closed_reason == "MAX_TOTAL_TRANSITIVE_PATHS_EXCEEDED"
    assert r.partial_depth >= 1
