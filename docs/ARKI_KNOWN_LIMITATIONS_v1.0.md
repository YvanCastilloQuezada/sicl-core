# ARKI Known Limitations & Deferred Debt — v1.0

Este documento formaliza las limitaciones conocidas y la deuda técnica diferida del Ciclo Cognitivo Core (H-001 a H-004).

## Deuda de Calidad de Tests

- **RT-89, RT-91, RT-92, RT-93, RT-95, RT-96:** Tests con nombres correctos pero aserciones estructurales débiles o que usan la API estática en lugar de la dinámica.
- **Impacto:** Nulo en producción. El código subyacente es robusto.
- **Resolución:** Refactorización de tests en fase de mantenimiento.

## Limitaciones de Diseño

- **RT-90 (Normativa):** H-003 detecta `MISSING_DEPENDENCY` cuando falta una norma, pero no evalúa el *contenido* de la norma para dictar `NORMATIVE_VIOLATION`.
- **RT-94 (E2E Hardcoded):** El test E2E inyecta el estado actual manualmente en lugar de derivarlo de una secuencia de eventos de cambio en el ledger.
- **Impacto:** El sistema funciona como un "descubridor de impactos topológicos", no como un "evaluador semántico de contenido arquitectónico".
- **Resolución:** Requiere la implementación de módulos superiores (Evaluación Normativa, H-005+).

**Estado:** `ACKNOWLEDGED AND DEFERRED BY HUMAN AUTHORITY`
