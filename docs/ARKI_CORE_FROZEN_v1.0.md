# ARKI Ciclo Cognitivo Core — FROZEN v1.0

Por la autoridad de Wilfredo Yvan Castillo Quezada (Product Owner), se declara formalmente congelado el núcleo cognitivo de ARKI.

## Módulos Congelados
| Módulo | Propósito | Estado |
|---|---|---|
| **H-001** | Derivation Integrity (Trazabilidad y RT-A/RT-D) | 🧊 FROZEN |
| **H-002** | Impact Analysis (Descubrimiento topológico read-only) | 🧊 FROZEN |
| **H-003** | Validity / Invalidation (Evaluación de estado) | 🧊 FROZEN |
| **H-004** | Reaction Planning (Planificación de reacciones) | 🧊 FROZEN |

## Garantías del Núcleo v1.0

1. **Read-Only Guarantee:** Ninguno de estos módulos muta el `DerivationLedger` ni el `EventStore`.
2. **Human Authority:** Ninguna invalidación o recomputación se ejecuta automáticamente sin pasar por un estado de `REQUIRES_HUMAN_AUTHORITY` o `PLANNED`.
3. **Fail-Closed:** Ante corrupción de datos, hashes faltantes o ciclos, el sistema escala (`ESCALATE` / `BLOCKED`) en lugar de adivinar.

## Regla de Modificación
A partir de la firma de este manifiesto, **ningún cambio estructural** será aceptado en H-001 a H-004 sin una justificación de negocio crítica aprobada por Human Authority. Solo se aceptarán parches de seguridad o correcciones de bugs funcionales graves.

### Excepción autorizada F-02 — 2026-09-27

Se autoriza el cambio en `src/sicl/drawing/ifc_synthetic.py` y
`scripts/generate_synthetic_ifc.py` para corregir un defecto grave del
helper productivo que escribía sobre el IFC rastreado durante la generación
de fixtures. La corrección dirige la salida al destino solicitado o a un
archivo temporal; **H-001, H-002, H-003 y H-004 no fueron modificados**.

### Alcance experimental de Compliance y Laboratory

`sicl.compliance` y `sicl.laboratory` son capas experimentales de gobernanza.
No constituyen certificación legal de cumplimiento, no deben presentarse como
EU AI Act compliant ni ISO/IEC 42001 certified ante terceros, y requieren
auditoría externa formal antes de cualquier claim comercial o regulatorio.

### Excepciones y reservas documentales RD-02 — 2026-09-27

- **R1 — Dependencia runtime:** se autoriza `jsonschema>=4,<5` en
  `pyproject.toml` para ejecutar formalmente los contratos Draft-07 de
  Compliance. Esta dependencia no modifica H-001–H-004.
- **R2 — Evidencia ISO parcial:** un log vacío devuelve `NOT_EVALUATED`;
  logs pequeños quedan declarados como evidencia parcial y no equivalen a
  certificación estadística ni auditoría externa.
- **R3 — JSON Schema fail-closed:** los payloads inválidos producen estado
  explícito `NON_COMPLIANT`; la suite de contratos verifica este rechazo.
- **R4 — Baseline operativo:** el baseline canónico es
  `sicl-core-1.0-rd02-remediated-2026-09-27` @
  `505ccd120772f7236ddb6ce476f3ee5b95e2e2b8`.

#### Baselines históricos

- `sicl-core-1.0-rt97-patched`: merge RT-97 previo a la remediación.
- `sicl-core-1.0-full-baseline-2026-09-27`: post RT-97 + F-02 + Compliance.

**RD-02 REMEDIATION: COMPLETE.** Las reservas R1–R4 quedan registradas como
excepciones documentales; ninguna bloquea el inicio del siguiente hito.

**FIRMADO:** Wilfredo Yvan Castillo Quezada, Product Owner & Human Authority, 2026-09-27
