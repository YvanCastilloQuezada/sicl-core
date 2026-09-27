# ARKI EU AI Act Mapping

Este documento mapea los niveles de riesgo de ARKI a las categorías operativas del EU AI Act.

## Mapeo de niveles de riesgo

| ARKI `risk_tier` | Clasificación EU AI Act | Controles ARKI |
|---|---|---|
| `UNACCEPTABLE` | Prácticas prohibidas (Art. 5) | Bloqueo absoluto y fail-closed. |
| `HIGH` | Sistemas de alto riesgo (Art. 6, Annex III) | AIA obligatoria, trazabilidad completa y supervisión humana. |
| `LIMITED` | Riesgo limitado y transparencia (Art. 50) | Etiquetado de contenido generado y trazabilidad. |
| `MINIMAL` | Riesgo mínimo | Buenas prácticas de trazabilidad. |

## Controles implementados

- **Art. 9:** Regla 41 (`domain_profile` y `risk_tier`).
- **Art. 10:** Regla 42 (`provenance_signature` y fuentes).
- **Art. 13:** transparencia mediante proveniencia y evaluación de sesgos.
- **Art. 14:** supervisión humana en promociones a `CANONICAL`.

**Versión:** 1.0 | **Fecha:** 2026-09-28 | **Estado:** FROZEN
