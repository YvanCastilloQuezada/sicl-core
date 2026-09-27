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

**FIRMADO:** Wilfredo Yvan Castillo Quezada, Product Owner & Human Authority, 2026-09-27
