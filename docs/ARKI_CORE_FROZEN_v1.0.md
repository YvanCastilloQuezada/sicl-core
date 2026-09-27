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

**FIRMADO:** Wilfredo Yvan Castillo Quezada, Product Owner & Human Authority, 2026-09-27
