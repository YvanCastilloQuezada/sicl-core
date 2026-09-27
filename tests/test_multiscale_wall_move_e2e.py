"""
ARKI — Prueba Multiescala E2E: Wall-Move Lite

Escenario: Mover muro interior W-14 +0.80m hacia el este.

Cadena causal esperada (8 escalas):
  1. Geometría: W-14 se desplaza +0.80m
  2. Espacios: H-07 (área +5.6%), P-03 (área -9.9%)
  3. Cantidades: Piso H-07, Piso P-03, Pintura
  4. Costo: Δ materiales + Δ mano de obra = +$342 USD
  5. Normativa: P-03 ancho 1.20m → 1.08m (VIOLA RNE A.010 mín 1.10m)
  6. Circulación: Ruta evacuación R-2 distancia 18.4m → 19.1m
  7. Asoleamiento: Ventana V-22 horas sol directo -12%
  8. Decisión arquitectónica: PARTI "pasillo luminoso" COMPROMETIDO

Este test verifica que:
- H-002 descubre todas las escalas
- H-003 evalúa correctamente (Costo=STALE, Normativa=REQUIRES_HUMAN_REVIEW)
- coverageWarning está presente
"""
import pytest
from sicl.domain import Event
from sicl.derivation import DerivationLedger, DerivationRecord, VersionedRef, TypedRelation
from sicl.impact import ImpactAnalyzer, ImpactChange, ChangeKind
from sicl.validity import ValidityAnalyzer


def ref(entity_type, entity_id, version, content_hash=None):
    return VersionedRef(entity_type, entity_id, version, content_hash)


def record(derivation_id, output, inputs, relation_type="COMPUTED_FROM", domain="COMPUTATIONAL"):
    return DerivationRecord(
        derivation_id,
        output,
        tuple(inputs),
        "method",
        "1",
        tuple(TypedRelation(output, inp, relation_type, domain) for inp in inputs)
    )


class MemoryStore:
    def __init__(self):
        self.items = []

    def add_event(self, event):
        self.items.append(event)
        return event

    def events(self, project_id=None):
        return [item for item in self.items if project_id is None or item.project_id == project_id]


def current_refs_from_ledger(ledger, project_id, updates, omit=()):
    """Construye el snapshot actual desde el ledger y aplica solo cambios observados."""
    refs = {}
    for derivation in ledger.list(project_id):
        refs[derivation.output.key()] = derivation.output
        for input_ref in derivation.inputs:
            refs[input_ref.key()] = input_ref
    refs.update(updates)
    for key in omit:
        refs.pop(key, None)
    return refs


def test_multiscale_wall_move_e2e():
    """
    Prueba E2E: mover muro W-14 +0.80m debe impactar 8 escalas.
    """
    ledger = DerivationLedger(MemoryStore())
    project_id = "wall-move-test"

    # ──────────────────────────────────────────────
    # ESCALA 1: Geometría (muro W-14)
    # ──────────────────────────────────────────────
    w14_v1 = ref("Wall", "W-14", 1, "a" * 64)  # Posición original
    w14_v2 = ref("Wall", "W-14", 1, "b" * 64)  # Posición nueva (+0.80m)

    # ──────────────────────────────────────────────
    # ESCALA 2: Espacios (H-07 y P-03)
    # ──────────────────────────────────────────────
    h07_v1 = ref("Space", "H-07", 1, "c" * 64)  # Área 14.2m²
    h07_v2 = ref("Space", "H-07", 2, "d" * 64)  # Área 15.0m² (+5.6%)

    p03_v1 = ref("Space", "P-03", 1, "e" * 64)  # Área 8.1m², ancho 1.20m
    p03_v2 = ref("Space", "P-03", 2, "f" * 64)  # Área 7.3m², ancho 1.08m (-9.9%)

    # Derivaciones: espacios derivan del muro
    ledger.record(project_id, record("D-H07", h07_v1, [w14_v1]))
    ledger.record(project_id, record("D-P03", p03_v1, [w14_v1]))

    # ──────────────────────────────────────────────
    # ESCALA 3: Cantidades (pisos y pintura)
    # ──────────────────────────────────────────────
    piso_h07_v1 = ref("Quantity", "PISO-H07", 1, "1" * 64)
    piso_p03_v1 = ref("Quantity", "PISO-P03", 1, "2" * 64)
    pintura_v1 = ref("Quantity", "PINTURA", 1, "3" * 64)

    # Derivaciones: cantidades derivan de espacios
    ledger.record(project_id, record("D-PISO-H07", piso_h07_v1, [h07_v1]))
    ledger.record(project_id, record("D-PISO-P03", piso_p03_v1, [p03_v1]))
    ledger.record(project_id, record("D-PINTURA", pintura_v1, [h07_v1, p03_v1]))

    # ──────────────────────────────────────────────
    # ESCALA 4: Costo
    # ──────────────────────────────────────────────
    costo_v1 = ref("Cost", "COSTO", 1, "4" * 64)

    # Derivación: costo deriva de cantidades
    ledger.record(project_id, record("D-COSTO", costo_v1, [piso_h07_v1, piso_p03_v1, pintura_v1]))

    # ──────────────────────────────────────────────
    # ESCALA 5: Normativa (RNE A.010)
    # ──────────────────────────────────────────────
    rne_a010 = ref("Regulation", "RNE-A010", 1, "5" * 64)

    # Relación epistémica: P-03 SUPPORTED_BY RNE-A010 (ancho mínimo 1.10m)
    ledger.record(project_id, record("D-RNE-P03", p03_v1, [rne_a010],
                                     relation_type="SUPPORTED_BY", domain="EPISTEMIC"))

    # ──────────────────────────────────────────────
    # ESCALA 6: Circulación (ruta evacuación R-2)
    # ──────────────────────────────────────────────
    ruta_r2_v1 = ref("Route", "R-2", 1, "6" * 64)

    # Derivación: ruta deriva de espacios
    ledger.record(project_id, record("D-RUTA-R2", ruta_r2_v1, [p03_v1]))

    # ──────────────────────────────────────────────
    # ESCALA 7: Asoleamiento (ventana V-22)
    # ──────────────────────────────────────────────
    ventana_v22_v1 = ref("Window", "V-22", 1, "7" * 64)

    # Derivación: ventana deriva del muro (afecta sombra proyectada)
    ledger.record(project_id, record("D-V22", ventana_v22_v1, [w14_v1]))

    # ──────────────────────────────────────────────
    # ESCALA 8: Decisión arquitectónica (PARTI)
    # ──────────────────────────────────────────────
    parti_v1 = ref("DesignIntent", "PARTI-PASILLO-LUMINOSO", 1, "8" * 64)
    parti_evidence_v1 = ref("DesignEvidence", "PARTI-EVIDENCE", 1, "9" * 64)

    # Relación arquitectónica: PARTI deriva de los espacios.
    # H-001 reserva SUPPORTED_BY para el dominio EPISTEMIC.
    ledger.record(project_id, record("D-PARTI", parti_v1, [p03_v1, parti_evidence_v1],
                                     relation_type="DERIVED_FROM", domain="ARCHITECTURAL"))

    recorded = {item.id: item for item in ledger.list(project_id)}
    assert any(
        relation.relation_type == "SUPPORTED_BY"
        and relation.relation_domain == "EPISTEMIC"
        and relation.to_ref.entity_id == "RNE-A010"
        for relation in recorded["D-RNE-P03"].relations
    )
    assert all(
        relation.relation_domain == "ARCHITECTURAL"
        for relation in recorded["D-PARTI"].relations
    )

    # ──────────────────────────────────────────────
    # EJECUCIÓN: Impact Analysis (H-002)
    # ──────────────────────────────────────────────
    analyzer = ImpactAnalyzer(ledger)

    # Cambio: W-14 cambia de contenido manteniendo la identidad/version del snapshot causal
    change = ImpactChange(
        before=w14_v1,
        after=w14_v2,
        change_kind=ChangeKind.CONTENT_CHANGED
    )

    ledger_before_impact = ledger.list(project_id)
    impact_report = analyzer.analyze_change(project_id, change)

    # ──────────────────────────────────────────────
    # VERIFICACIÓN: H-002 descubre todas las escalas
    # ──────────────────────────────────────────────
    impacted_ids = {artifact.ref.entity_id for artifact in impact_report.impacted_artifacts}

    # Debe descubrir: H-07, P-03, PISO-H07, PISO-P03, PINTURA, COSTO, R-2, V-22, PARTI
    expected_impacts = {"H-07", "P-03", "PISO-H07", "PISO-P03", "PINTURA", "COSTO", "R-2", "V-22", "PARTI-PASILLO-LUMINOSO"}

    assert impacted_ids == expected_impacts, f"H-002 no descubrió todas las escalas. Faltan: {expected_impacts - impacted_ids}"

    # coverageWarning debe estar presente
    assert impact_report.coverage_warning == "GRAPH_MAY_BE_INCOMPLETE"
    assert impact_report.partial is False
    assert impact_report.partial_depth is None

    # ──────────────────────────────────────────────
    # EJECUCIÓN: Validity Analysis (H-003)
    # ──────────────────────────────────────────────
    validity_analyzer = ValidityAnalyzer(ledger)

    # Estado actual: snapshot derivado del ledger + cambios observados.
    current_refs = current_refs_from_ledger(
        ledger,
        project_id,
        {
            ("Wall", "W-14"): w14_v2,
            ("Space", "H-07"): h07_v2,
            ("Space", "P-03"): p03_v2,
            ("Quantity", "PISO-H07"): ref("Quantity", "PISO-H07", 2, "9" * 64),
            ("Quantity", "PISO-P03"): ref("Quantity", "PISO-P03", 2, "a" * 64),
            ("Quantity", "PINTURA"): ref("Quantity", "PINTURA", 2, "b" * 64),
            ("Cost", "COSTO"): ref("Cost", "COSTO", 2, "c" * 64),
            ("Route", "R-2"): ref("Route", "R-2", 2, "d" * 64),
            ("Window", "V-22"): ref("Window", "V-22", 2, "e" * 64),
        },
        omit=(("Regulation", "RNE-A010"), ("DesignEvidence", "PARTI-EVIDENCE")),
    )

    validity_report = validity_analyzer.evaluate_validity(project_id, current_refs)

    # ──────────────────────────────────────────────
    # VERIFICACIÓN: H-003 evalúa correctamente
    # ──────────────────────────────────────────────

    # COSTO debe ser STALE (todas sus derivaciones son STALE)
    costo_validity = next(av for av in validity_report.artifact_validities if av.artifact_ref.entity_id == "COSTO")
    assert costo_validity.state == "FULLY_STALE"
    assert costo_validity.recommendation["action"] == "RECOMPUTE"
    assert costo_validity.recommendation["requiresHumanAuthority"] is False
    assert costo_validity.derivation_validities[0].source_checks == ("integrity_checks_D-COSTO",)

    # P-03 debe ser REQUIRES_HUMAN_REVIEW (porque viola normativa)
    p03_validity = next(av for av in validity_report.artifact_validities if av.artifact_ref.entity_id == "P-03")
    assert p03_validity.state == "REQUIRES_HUMAN_REVIEW"
    assert p03_validity.recommendation["requiresHumanAuthority"] is True
    assert any(
        discrepancy["code"] == "MISSING_DEPENDENCY"
        for derivation in p03_validity.derivation_validities
        for discrepancy in derivation.discrepancies
    )

    # PARTI debe ser REQUIRES_HUMAN_REVIEW (decisión arquitectónica comprometida)
    parti_validity = next(av for av in validity_report.artifact_validities
                          if av.artifact_ref.entity_id == "PARTI-PASILLO-LUMINOSO")
    assert parti_validity.state == "REQUIRES_HUMAN_REVIEW"
    assert parti_validity.recommendation["requiresHumanAuthority"] is True

    # H-07 debe ser STALE (pero no requiere revisión humana, solo recomputar)
    h07_validity = next(av for av in validity_report.artifact_validities if av.artifact_ref.entity_id == "H-07")
    assert h07_validity.state == "FULLY_STALE"
    assert h07_validity.recommendation["action"] == "RECOMPUTE"
    assert h07_validity.recommendation["requiresHumanAuthority"] is False

    # ──────────────────────────────────────────────
    # VERIFICACIÓN: Read-only guarantee
    # ──────────────────────────────────────────────
    assert ledger.list(project_id) == ledger_before_impact
    assert validity_report.read_only is True

    print("✅ Prueba Multiescala E2E PASÓ")
    print(f"   - H-002 descubrió {len(impact_report.impacted_artifacts)} artefactos impactados")
    print(f"   - H-003 evaluó {len(validity_report.artifact_validities)} artefactos")
    print(f"   - COSTO: FULLY_STALE → RECOMPUTE")
    print(f"   - P-03: REQUIRES_HUMAN_REVIEW (violación normativa)")
    print(f"   - PARTI: REQUIRES_HUMAN_REVIEW (decisión arquitectónica)")


def test_e2e_unrelated_branch_not_impacted():
    """RT-44: una rama no relacionada no entra en el impacto."""
    ledger = DerivationLedger(MemoryStore())
    project_id = "unrelated-branch"
    wall = ref("Wall", "W-14", 1, "a" * 64)
    area = ref("Space", "H-07", 1, "b" * 64)
    other_wall = ref("Wall", "W-99", 1, "c" * 64)
    other_area = ref("Space", "S-99", 1, "d" * 64)
    ledger.record(project_id, record("D-H07", area, [wall]))
    ledger.record(project_id, record("D-S99", other_area, [other_wall]))
    report = ImpactAnalyzer(ledger).analyze_change(
        project_id,
        ImpactChange(wall, ref("Wall", "W-14", 1, "e" * 64), ChangeKind.CONTENT_CHANGED),
    )
    assert {item.ref.entity_id for item in report.impacted_artifacts} == {"H-07"}


def test_e2e_unknown_dependency_wall_opening_is_reported_as_incomplete():
    """RT-45/RT-52: unregistered consequences remain unknown, never silently absent."""
    ledger = DerivationLedger(MemoryStore())
    project_id = "unknown-opening"
    wall = ref("Wall", "W-14", 1, "a" * 64)
    area = ref("Space", "H-07", 1, "b" * 64)
    ledger.record(project_id, record("D-H07", area, [wall]))
    report = ImpactAnalyzer(ledger).analyze_change(
        project_id,
        ImpactChange(wall, ref("Wall", "W-14", 1, "e" * 64), ChangeKind.CONTENT_CHANGED),
    )
    assert all(item.ref.entity_id != "O-1" for item in report.impacted_artifacts)
    assert report.coverage_warning == "GRAPH_MAY_BE_INCOMPLETE"
