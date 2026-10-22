# ARKI Core v1.0 — Patched Baseline Declaration

**Estado:** AUTORIZADO / BASELINE OPERATIVO

## Baselines

- **Baseline histórico auditado:** `5533bd8eb1e3b81c37d089bd30b424f2a4c1e231`
- **Checkpoint pre-RT-97:** `bbc8d75dcfbb75240a3f77a6dae62d2e01bd0d61`
- **Baseline parcheado vigente:** `b80141892867b8498a87f26b2ae7e1bfa03a7749`

## Alcance del cambio

El baseline parcheado conserva H-001, H-002 y H-003 sin modificaciones. En H-004 incorpora únicamente la corrección funcional RT-97: cuando un nodo está afectado simultáneamente por una cascada `BLOCKED_DEPENDENCY` y por un ciclo, el plan conserva ambas razones y la unión de sus dependencias bloqueantes.

El cambio está implementado en `src/sicl/reaction.py` y cubierto por el test adversarial `test_h004_node_blocked_by_cascade_and_cycle_preserves_both_reasons` en `tests/test_reaction.py`.

## Estado de congelación

El manifiesto histórico [ARKI_CORE_FROZEN_v1.0.md](ARKI_CORE_FROZEN_v1.0.md) permanece vigente para la identidad y los contratos de H-001 a H-004. RT-97 se clasifica como parche funcional grave permitido por la regla de modificación del manifiesto; no es un rediseño estructural ni una ampliación de capacidades.

## Verificación

- Test focal RT-97: PASS.
- Regresión H-001–H-004: PASS.
- H-001, H-002 y H-003: sin cambios en el commit del parche.
- Providers externos: 0.

**Propósito:** declarar de forma explícita la transición del baseline histórico al baseline operativo parcheado antes de reanudar pruebas de Nivel 8–10.
