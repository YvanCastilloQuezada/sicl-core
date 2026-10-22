# SICL Core — auditoría de ramas (lote 10: integración, despliegue y contexto ambiental)

Base: `main@de43b6b833731c87fb6277834484545bd953d76a`. No se ejecutaron pruebas.

## feat/vsm-phase1-registry-script
- SHA: `f8ec89bf74a9c9cc3d972b2dd2a3ece0722bd08b`
- Último commit: feat(vsm): add weekly master registry and detector (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/f8ec89bf74a9c9cc3d972b2dd2a3ece0722bd08b
- Comparación: diverged; ahead 10, behind 158; commits exclusivos 10; rutas 61.
- Rutas: data/drawing_rules/README.md, data/drawing_rules/iso128_nte_peru.json, data/drawing_rules/iso128_rne_peru.json, data/drawing_symbols/default_symbols.json, data/master_registry/logs/2026-09-26_weekly_review.md
- Lectura: Script de registro VSM; revisar si registra evidencia o solo metadatos.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: revisar PR/CI y configuración real; no inferir despliegue funcional por el nombre de la rama.

## feat/weather-environmental-context-p1
- SHA: `1c416551a945286e3b7fab6a5f01e8852442ea7b`
- Último commit: docs: add canonical master handoff (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/1c416551a945286e3b7fab6a5f01e8852442ea7b
- Comparación: diverged; ahead 39, behind 168; commits exclusivos 39; rutas 62.
- Rutas: api/deps.py, api/routes/v1.py, api/schemas.py, docs/ARCHITECT-MVP-VALIDATION-PREP-01.md, docs/DESIGN-KNOWLEDGE-ALEXANDER-CES-PILOT.md
- Lectura: Contexto ambiental y meteorológico; la procedencia/fecha del dato es esencial.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: revisar PR/CI y configuración real; no inferir despliegue funcional por el nombre de la rama.

## fix/railway-src-import
- SHA: `7e0c2d794a8923b77565731824c9aecea72b0392`
- Último commit: fix: bootstrap src path for Railway API imports (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/7e0c2d794a8923b77565731824c9aecea72b0392
- Comparación: behind; ahead 0, behind 280; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Corrección de importación para Railway; cambio operativo de build/deploy, no capacidad ARKI.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: revisar PR/CI y configuración real; no inferir despliegue funcional por el nombre de la rama.

## fix/revert-railway-editable-install
- SHA: `1af6802f0956b6b01e4afdf7f169b1e336677198`
- Último commit: revert: remove editable install from Railway build (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/1af6802f0956b6b01e4afdf7f169b1e336677198
- Comparación: diverged; ahead 1, behind 287; commits exclusivos 1; rutas 2.
- Rutas: Procfile, requirements.txt
- Lectura: Reversión de editable install; debe leerse junto con la rama de importación para establecer secuencia correcta.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: revisar PR/CI y configuración real; no inferir despliegue funcional por el nombre de la rama.

## fix/site-semantics-001
- SHA: `bd1069ad1804c62dc436b71144fcd05a4d187a01`
- Último commit: SITE-SEMANTICS-001: test sourced versus simulated epistemics (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/bd1069ad1804c62dc436b71144fcd05a4d187a01
- Comparación: behind; ahead 0, behind 2; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Semántica del sitio; verificar vocabulario y compatibilidad con contratos de dominio.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: revisar PR/CI y configuración real; no inferir despliegue funcional por el nombre de la rama.

## integrate/spatial-s6p01-core
- SHA: `3f52d87bf0696470a39c13504dbd57a2c1e6c450`
- Último commit: Merge commit 'd6aabb6980f92037dc4fe2f53c1b50b0b29647ea' into integrate/spatial-s6p01-core (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/3f52d87bf0696470a39c13504dbd57a2c1e6c450
- Comparación: behind; ahead 0, behind 179; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Integración espacial S6P01; revisar commit/PR para distinguir integración efectiva de una rama preparatoria.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: revisar PR/CI y configuración real; no inferir despliegue funcional por el nombre de la rama.

## integration-v2
- SHA: `b377aa65380ea2cc1a7fc77a9cd63830197f5371`
- Último commit: Merge remote-tracking branch 'origin/rfc-009-multiscale-relations' into integration-v2 (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/b377aa65380ea2cc1a7fc77a9cd63830197f5371
- Comparación: behind; ahead 0, behind 252; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Segunda línea de integración; comparar su historial y alcance con main.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: revisar PR/CI y configuración real; no inferir despliegue funcional por el nombre de la rama.

## railway/fix-deploy-ba7603
- SHA: `d0de2079b274cbc36512cd9ce9ee76f6e16d5dc6`
- Último commit: fix: remove editable install and restore PYTHONPATH=src (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/d0de2079b274cbc36512cd9ce9ee76f6e16d5dc6
- Comparación: diverged; ahead 1, behind 287; commits exclusivos 1; rutas 2.
- Rutas: Procfile, requirements.txt
- Lectura: Corrección de despliegue Railway; revisar si ya está absorbida y si depende del proveedor/entorno.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: revisar PR/CI y configuración real; no inferir despliegue funcional por el nombre de la rama.
