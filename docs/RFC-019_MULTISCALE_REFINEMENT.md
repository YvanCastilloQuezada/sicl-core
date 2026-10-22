# RFC-019 — Multiscale Refinement

**Estado:** IMPLEMENTED ON MAIN — incluido en `main@f2c4d205198e6050cdfd50e228e8ba21d3d4c79f`

## Objetivo

RFC-019 formaliza once escalas espaciales canónicas en el Core sin inferir una escala cuando el proyecto no la declara.

## Escalas

`pais` → `macro_region` → `region` → `provincia_metropoli` → `distrito_ciudad` → `zona_barrio_sector` → `parcela_sitio` → `edificacion` → `sistema` → `espacio` → `objeto`.

## Migración

Los valores heredados se convierten explícitamente: `edificio` a `edificacion`, `ciudad_distrito` a `distrito_ciudad` y `barrio_sector` a `zona_barrio_sector`. La migración es idempotente, crea respaldo antes de escribir, incrementa la versión del proyecto y registra `SCOPE_MIGRATED` con actor `system:migration:019`.

## Rollback

El módulo `src/sicl/migrations/019_multiscale_refinement.py` permite restaurar un backup o revertir cambios identificados por sus eventos de migración. Las tablas de eventos siguen siendo append-only; el rollback añade un evento compensatorio y no elimina el historial.

## Invariantes

El catálogo no infiere relaciones territoriales. Cada scope tiene un único padre salvo `pais`, cada scope puede tener un hijo inmediato en la cadena canónica, y las relaciones no adyacentes se registran mediante `ScaleRelation`. RFC-019 no crea decisiones ni cambia la autoridad humana.

## Verificación

La rama fue verificada con la suite completa del Core, 214 casos recolectados y todos pasando, además de `compileall` y `git diff --check`.


## Baseline consolidado

RFC-019 quedó consolidado en `main@faff4f8e` junto con RFC-020 y RFC-021. La migración de las once escalas espaciales, el contrato HTTP, los tests multiescala y la documentación asociada forman parte del baseline verificable.
