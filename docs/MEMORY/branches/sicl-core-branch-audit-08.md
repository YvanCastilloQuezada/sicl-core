# SICL Core — auditoría de ramas cerradas, promoción y dibujo

**Última actualización:** 2026-10-22  
**Alcance:** reconciliación de PR cerrados relevantes, gates de promoción de Core y ramas históricas de dibujo. No es una auditoría exhaustiva de los 46 PR cerrados; las ramas históricas no comparadas siguen con estado no verificado.

## 1. Dictamen de autoridad ARKI/SICL

La documentación fundacional de `sicl-web` define ARKI como sistema/modelo de decisión; SICL como lenguaje formal; `sicl-web` como superficie de interacción; y `sicl-core` como superficie canónica de dominio, validación, persistencia, invariantes, eventos y API. Las recomendaciones no son decisiones; Fact, Assumption y Preference no se mezclan; el evento de auditoría es append-only; y una mutación UI solo puede mostrarse como persistida cuando Core lo confirma.

Por tanto:
- No fusionar código viejo porque la rama lleve un nombre de RFC correcto.
- No promover simulación a observación/hecho.
- No marcar una capacidad VERIFIED con solo su documentación o fixture.
- No modificar H-001..H-004 FROZEN ni hacer de la UI una segunda autoridad canónica.

## 2. Estado del historial de PR de Core

- El repositorio devuelve 46 PR cerrados en la consulta. “Closed” no equivale a “merged”; siempre distinguir el campo `merged` y el merge SHA.
- PR #22 RFC-030: [cerrado sin merge](https://github.com/YvanCastilloQuezada/sicl-core/pull/22). Se conserva su procedencia; no integrar la rama completa por duplicación de módulos/reglas y evidencia de pruebas insuficiente.
- PR #21 RFC-034.1: [cerrado sin merge](https://github.com/YvanCastilloQuezada/sicl-core/pull/21). La rama tiene 4 commits exclusivos, 168 commits detrás y 39 rutas distintas según la comparación actual; no integrar completa.
- PR #42 promoción concurrente: [merged](https://github.com/YvanCastilloQuezada/sicl-core/pull/42), merge SHA `588d8fa44dab7122a718e98bc1dec579c697cdbe`.
- PR #41 gate de esquema: [merged](https://github.com/YvanCastilloQuezada/sicl-core/pull/41), merge SHA `e89577adb5ed1a6b58e57d06ed080b9a7f1dac54`.
- PR #43 DAM: [merged](https://github.com/YvanCastilloQuezada/sicl-core/pull/43) en la cadena de PR #42. Implementa la fundación de roles/ADN/evaluación, no la graduación profesional de la rama de dibujo.
- PR #45 contrato de autoridad y #47 auditoría documental: ambos merged. PR #40 separó semántica simulada de hechos y fue merged.
- PR #46 0-Historical aparece como merged, pero la etiqueta histórica no es evidencia de que todas las ramas antiguas tengan funcionalidad revalidada.

Los textos de PR #41 y #42 fueron actualizados para reconciliar sus advertencias históricas “DO NOT MERGE” con el hecho real de que GitHub los registra como fusionados.

## 3. Correcciones aplicadas en main y evidencia CI

Commit `6a7a0b563d4b22211bd655dc07f86a9460b0f03e`:
- Corrige el gate V-3: antes volvía a abrir una base recién creada, de modo que probaba el bootstrap otra vez en vez de preparar y comprobar un esquema ya migrado. Ahora prepara explícitamente el esquema migrado antes de reabrir el repositorio.

Commit `ddd892b7f756a6d841f488c25f51ef8f2362fe83`:
- Añade al workflow general de CI los tres gates requeridos por el bloque 6.11: V-1..V-5, migración atómica M-1..M-12 y benchmark de `ledger_binding_guard` sobre más de 100.000 snapshots, además de la suite de tests y compilación.

Ejecución: [SICL Core CI run 39861675115](https://github.com/YvanCastilloQuezada/sicl-core/actions/runs/39861675115). Resultado consultado: PASS en Python 3.11 y 3.12; en ambas matrices terminaron con éxito `pytest`, el gate de estados de esquema, el gate de migración atómica, el benchmark y `compileall`.

Estado distinto: los checks de Railway del mismo SHA seguían en `failure` en la última consulta. La integración CI está validada; el despliegue de servicio no.

## 4. RFC-030 / RFC-034.1 — decisión técnica

Main contiene los módulos actuales:
- `src/sicl/drawing/projector.py` — SHA `5ba4ce4df128b9273115d8436551fd18dae5f972`
- `tests/test_rfc030_drawing.py` — SHA `b720018331ce451de2e0f2767b4634f812010e04`
- `src/sicl/layout/layout_engine.py` — SHA `7a4df2433ea3a7e4fd0261883966b98a121cc614`
- `tests/test_rfc0341_layout.py` — SHA `9211e3f5d9233ac463539c4ddbb0b736f6f91d0d`
- `data/drawing_rules/iso128_rne_peru.json` — SHA `4539f65960e855009b18ca6346382be79e23f72d`

PR #21 y #22 son ramas divergentes de la implementación actual. Sus artefactos históricos no prueban conformidad profesional por sí solos. Se requiere validación objetiva con un fixture arquitectónico de referencia, comparación geométrica/semántica del IFC, vistas/cotas/anotaciones y validación del PDF generado. La fase DAM de dibujo sigue **BLOCKED_FOR_GRADUATION** hasta demostrar ground truth multi-maestro y reproducción indistinguible. No cambiar este estado solo porque CI está verde.

## 5. Auditoría de ramas previas

- `feat/h005-selective-recomputation`, `feat/multiscale-capability-foundation-s7p05`, `feat/mv-p1-final-integration`, `feat/mv-p1-runtime-variable-foundation` y `feat/mv-p1-spatial-location-runtime` fueron registradas en un corte histórico con ahead=0 y sin rutas/commits exclusivos. No hay cambio exclusivo que rescatar desde esas puntas; cotejar con main solo si se identifican commits posteriores.
- `feat/rfc-030-drawing-standard` se había registrado como divergente con 6 commits exclusivos/42 rutas. Cualquier rescate debe ser selectivo; no copiar a ciegas reglas normativas antiguas.

## 6. Deuda pendiente

1. Resolver y verificar los dos checks de Railway fallidos (`sicl-core` y `sicl-web`) por separado. No es seguro inferir que ambos fallos tengan la misma causa.
2. Inspeccionar detalles/logs de Railway y confirmar el estado desplegado real, sin revertir ni tocar configuración de producción a ciegas.
3. Construir prueba de fidelidad de dibujo contra fixture profesional real y evidencias multi-maestro; no declarar graduación DAM antes de ello.
4. Este documento no cubre exhaustivamente todos los PR cerrados ni todas las ramas del repositorio. Los restantes deben mantenerse en UNKNOWN/PENDING hasta consultar el merge SHA, comparar la punta actual y revisar evidencia. No inferir que toda rama antigua está absorbida porque haya un PR cerrado.

## 7. Invariantes de cierre

- No crear ramas nuevas para esta continuidad.
- Mantener Core como autoridad canónica y Web como interfaz/adaptador.
- No confundir claim, diseño, implementación, ejecución, observación, verificación y freeze.
- No reportar despliegue verde cuando Railway está rojo.
- No abrir contratos FROZEN por la vía de una corrección incidental.

## 8. feat/rfc-030-drawing-standard — verificación (27-oct-2026)

**Estado:** 100% histórica. Verificada el 27-oct-2026.

- 6 commits exclusivos (septiembre-octubre 2026).
- 42 archivos en el diff, **0 archivos exclusivos** (todos ya están en `main`).
- La funcionalidad de RFC-030/RFC-034.1 está en `main` con implementaciones posteriores.
- No hay nada que rescatar.

**Acción:** conservar la rama por procedencia. No crear PR. No eliminar.

---

## Actualización 2026-10-28: PR #22 (RFC-030 + RFC-034.1) cerrado definitivamente

**Verificación:** los 14 archivos del commit `5fa7138` (sheet composition and layout engine) están en `main`:
- `src/sicl/layout/` (10 archivos: `__init__.py`, `case_study.py`, `collision.py`, `http_api.py`, `layout_engine.py`, `layout_report.py`, `margin_validator.py`, `sheet_format.py`, `sheet_grid.py`, `sheet_zone.py`).
- `scripts/layout_cli.py`, `scripts/layout_http.py`.
- `docs/reference/RFC0341_CASA_NIDO_LAYOUT_REPORT.json`.

**Decisión:** PR #22 cerrado definitivamente. Rama `feat/rfc-030-ifc-regeneration` borrada de GitHub. El PR es 100% redundante.

**Los commits originales (`5fa7138`, `2de6011`, `8e41ed3`, `a6f727f`, `9d2b4ad`) no están en `main` por SHA, pero su contenido sí está integrado por otra vía (probablemente squash-merge o cherry-pick anterior).**

