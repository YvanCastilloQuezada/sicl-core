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
    """RT-A/RT-63: múltiples derivaciones y atribución estricta por path."""
    s=Store(); l=DerivationLedger(s)
    g1=ref("Geometry","G1",1,"a"*64); g2=ref("Geometry","G2",1,"b"*64)
    a=ref("Area","A",1,"c"*64); c=ref("Cost","C",1,"d"*64)
    l.record("P",rec("DA1",a,[g1])); l.record("P",rec("DA2",a,[g2])); l.record("P",rec("DC",c,[a]))
    assert [x.id for x in l.why("P",a)]==["DA1","DA2"]
    r1=ImpactAnalyzer(l).analyze_dependency("P",g1)
    r2=ImpactAnalyzer(l).analyze_dependency("P",g2)
    a1=next(x for x in r1.impacted_artifacts if x.ref==a)
    a2=next(x for x in r2.impacted_artifacts if x.ref==a)
    assert set(a1.derivation_records)=={"DA1"}
    assert set(a2.derivation_records)=={"DA2"}
    c1=next(x for x in r1.impacted_artifacts if x.ref==c)
    c2=next(x for x in r2.impacted_artifacts if x.ref==c)
    assert "DC" in c1.derivation_records
    assert "DC" in c2.derivation_records


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
def test_e11_change_kind_content_vs_version_vs_identity_vs_unknown():
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

    ch_identity=ImpactChange(g,ref("Geometry","G2",1,"a"*64),ChangeKind.IDENTITY_CHANGED)
    r_identity=ImpactAnalyzer(l).analyze_change("P",ch_identity)
    assert r_identity.impacted_artifacts==()
    assert r_identity.fail_closed_reason=="NO_AUTOMATIC_RETROACTIVE_IMPACT"

    ch_unknown=ImpactChange(g,ref("Geometry","G",1,"d"*64),ChangeKind.UNKNOWN)
    r_unknown=ImpactAnalyzer(l).analyze_change("P",ch_unknown)
    assert r_unknown.partial is True
    assert r_unknown.partial_depth==0
    assert r_unknown.fail_closed_reason=="UNKNOWN_CHANGE_KIND"

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
    depth1_nodes={x.ref for x in r.impacted_artifacts if x.min_depth==1}
    assert depth1_nodes==set(mids)
    assert r.partial_depth >= 1


# ──────────────────────────────────────────────
# TESTS FALTANTES PARA VECTORES RT
# ──────────────────────────────────────────────

def test_e14_cycle_canonicalization_with_mixed_domains():
    """RT-02: ciclos con dominios mixtos no colisionan."""
    s = Store()
    l = DerivationLedger(s)
    a = ref("X", "A", 1, "a" * 64)
    b = ref("X", "B", 1, "b" * 64)
    c = ref("X", "C", 1, "c" * 64)

    # Ciclo 1: todos COMPUTATIONAL
    l.record("P", rec("AB1", b, [a]))
    l.record("P", rec("BC1", c, [b]))
    l.record("P", rec("CA1", a, [c]))

    r1 = ImpactAnalyzer(l).analyze_dependency("P", a)

    # Ciclo 2: dominios mixtos (simulado con ledger mock)
    # Nota: H-001 no permite dominios mixtos en el mismo output,
    # pero H-002 debe manejarlos si llegan desde un reader legacy
    class MockLedger:
        def list(self, project_id):
            return [
                DerivationRecord("AB2", b, (a,), "m", "1",
                    (TypedRelation(b, a, "DERIVED_FROM", "EPISTEMIC"),)),
                DerivationRecord("BC2", c, (b,), "m", "1",
                    (TypedRelation(c, b, "DERIVED_FROM", "NORMATIVE"),)),
                DerivationRecord("CA2", a, (c,), "m", "1",
                    (TypedRelation(a, c, "DERIVED_FROM", "ARCHITECTURAL"),)),
            ]

    r2 = ImpactAnalyzer(MockLedger()).analyze_dependency("P", a)

    # Los ciclos deben ser distintos (dominios diferentes)
    assert r1.cycles != r2.cycles

def test_e15_unknown_dependency_per_artifact():
    """RT-04/RT-22: UNKNOWN_DEPENDENCY por artefacto."""
    s = Store()
    l = DerivationLedger(s)
    g = ref("Geometry", "G", 1, "a" * 64)
    a = ref("Area", "A", 1, "b" * 64)
    l.record("P", rec("D", a, [g]))

    # Cambiar contenido de G
    ch = ImpactChange(g, ref("Geometry", "G", 1, "c" * 64), ChangeKind.CONTENT_CHANGED)
    r = ImpactAnalyzer(l).analyze_change("P", ch)

    # coverage_warning debe estar presente
    assert r.coverage_warning == "GRAPH_MAY_BE_INCOMPLETE"
    # El artifact A debe estar impactado
    assert len(r.impacted_artifacts) == 1
    assert r.impacted_artifacts[0].ref == a

def test_e16_assumptions_not_traversable():
    """RT-07: assumptions no traversables."""
    s = Store()
    l = DerivationLedger(s)
    g = ref("Geometry", "G", 1, "a" * 64)
    a = ref("Area", "A", 1, "b" * 64)

    # Derivación con assumption textual
    record_with_assumption = DerivationRecord(
        "D", a, (g,), "m", "1",
        (TypedRelation(a, g, "COMPUTED_FROM", "COMPUTATIONAL"),),
        assumptions=("terrain is flat",)
    )
    l.record("P", record_with_assumption)

    # Cambiar contenido de G
    ch = ImpactChange(g, ref("Geometry", "G", 1, "c" * 64), ChangeKind.CONTENT_CHANGED)
    r = ImpactAnalyzer(l).analyze_change("P", ch)

    # assumptions no deben ser traversables
    assert r.assumptions_traversable is False
    # coverage_warning debe estar presente
    assert r.coverage_warning == "GRAPH_MAY_BE_INCOMPLETE"

def test_e17_overlapping_cycles_remain_distinct():
    """RT-11: ciclos superpuestos permanecen distintos."""
    s = Store()
    l = DerivationLedger(s)
    a = ref("X", "A", 1, "a" * 64)
    b = ref("X", "B", 1, "b" * 64)
    c = ref("X", "C", 1, "c" * 64)
    d = ref("X", "D", 1, "d" * 64)

    # Ciclo 1: A → B → C → A
    l.record("P", rec("AB", b, [a]))
    l.record("P", rec("BC", c, [b]))
    l.record("P", rec("CA", a, [c]))

    # Ciclo 2: A → B → D → A (comparte A → B)
    l.record("P", rec("BD", d, [b]))
    l.record("P", rec("DA", a, [d]))

    r = ImpactAnalyzer(l).analyze_dependency("P", a)

    # Debe haber 2 ciclos distintos
    assert len(r.cycles) == 2
    assert r.cycles[0] != r.cycles[1]

def test_e18_deterministic_ordering_with_reversed_ledger():
    """RT-14: determinismo con ledger invertido."""
    s1 = Store()
    l1 = DerivationLedger(s1)
    g = ref("Geometry", "G", 1, "a" * 64)
    a = ref("Area", "A", 1, "b" * 64)
    p = ref("Perimeter", "P", 1, "c" * 64)

    # Orden 1: P primero, A segundo
    l1.record("P", rec("DP", p, [g]))
    l1.record("P", rec("DA", a, [g]))

    r1 = ImpactAnalyzer(l1).analyze_dependency("P", g)

    # Orden 2: A primero, P segundo
    s2 = Store()
    l2 = DerivationLedger(s2)
    l2.record("P", rec("DA", a, [g]))
    l2.record("P", rec("DP", p, [g]))

    r2 = ImpactAnalyzer(l2).analyze_dependency("P", g)

    # Los reportes deben ser idénticos (determinismo)
    assert r1.canonical_dict() == r2.canonical_dict()
