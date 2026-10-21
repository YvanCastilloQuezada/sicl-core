# SICL Web — auditoría de ramas (lote 7: rendimiento, idioma y Mapas Vivos)

Base: `main@9ae8fe504bbb964d8b89d87709ee773e64cbbacb`. Tests no ejecutados en esta auditoría.

## feat/frontend-performance-cache-skeletons
- SHA: `4bcc28c1b8119c5b6523886ebe39d2637bcfcf6e`
- Último commit: perf: cache core reads and add loading skeletons (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/4bcc28c1b8119c5b6523886ebe39d2637bcfcf6e
- Comparación: behind; ahead 0, behind 396; 0 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: ninguna reportada
- Lectura: Rendimiento frontend y skeletons; revisar métricas reales, regresiones y si el cambio ya fue absorbido por main.
- Pruebas: no ejecutadas.
- Recomendación: rastrear PR y CI por SHA; rescatar solo cambios no presentes en main y aún necesarios.

## feat/help-system
- SHA: `19f48f2cebd1cb7fbba9fd158978643d9d8f6222`
- Último commit: fix: wire help button into home header (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/19f48f2cebd1cb7fbba9fd158978643d9d8f6222
- Comparación: behind; ahead 0, behind 452; 0 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: ninguna reportada
- Lectura: Sistema de ayuda; comprobar integración UI y contenido vigente.
- Pruebas: no ejecutadas.
- Recomendación: rastrear PR y CI por SHA; rescatar solo cambios no presentes en main y aún necesarios.

## feat/i18n-core
- SHA: `a101fe08f69acaa7f01a69a17a22ed135c110953`
- Último commit: feat: add core i18n language switching (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/a101fe08f69acaa7f01a69a17a22ed135c110953
- Comparación: behind; ahead 0, behind 459; 0 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: ninguna reportada
- Lectura: Infraestructura base de internacionalización; contrastar rutas y fallback con main.
- Pruebas: no ejecutadas.
- Recomendación: rastrear PR y CI por SHA; rescatar solo cambios no presentes en main y aún necesarios.

## feat/i18n-full-consistency-gate
- SHA: `c05acb636a8f9e3d5372c913bae5209b2ebddbaa`
- Último commit: feat: centralize audited UI copy in i18n (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/c05acb636a8f9e3d5372c913bae5209b2ebddbaa
- Comparación: behind; ahead 0, behind 369; 0 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: ninguna reportada
- Lectura: Gate de consistencia i18n; comprobar que detecte traducciones faltantes y que CI lo ejecute.
- Pruebas: no ejecutadas.
- Recomendación: rastrear PR y CI por SHA; rescatar solo cambios no presentes en main y aún necesarios.

## feat/m001-e3-gate-hardening
- SHA: `4a4e049783d8e015bcb6fab7ce64efa91b6d2214`
- Último commit: test(maqueta-viva): verify E3 gate membership and exact scenario validation (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/4a4e049783d8e015bcb6fab7ce64efa91b6d2214
- Comparación: diverged; ahead 436, behind 59; 436 commits exclusivos; 90 rutas reportadas.
- Rutas únicas: added .github/workflows/arki-controlled-executor.yml, added .github/workflows/arki-f1-f10-evidence.yml, added .github/workflows/arki-research-trends.yml, added .github/workflows/maqueta-viva-smoke.yml, added ARKI-MAQUETA-VIVA.cmd, added ARKI-RESEARCH-WATCH.cmd, modified client/index.html, modified client/src/App.tsx
- Lectura: Hardening del gate E3 para M001; confirmar qué evidencia y reglas exactas se imponen.
- Pruebas: no ejecutadas.
- Recomendación: rastrear PR y CI por SHA; rescatar solo cambios no presentes en main y aún necesarios.

## feat/mv-p1-final-integration
- SHA: `3dfb03c9bd18ff64ba13ee596199af169b46d1e5`
- Último commit: fix: make Web CI reproducible (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/3dfb03c9bd18ff64ba13ee596199af169b46d1e5
- Comparación: behind; ahead 0, behind 355; 0 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: ninguna reportada
- Lectura: Integración final del primer paquete de Mapas Vivos; el nombre no prueba que el contrato Core-Web esté integrado hoy.
- Pruebas: no ejecutadas.
- Recomendación: rastrear PR y CI por SHA; rescatar solo cambios no presentes en main y aún necesarios.

## feat/mv-p1-location-picker-web
- SHA: `89529ef62f458f9f010920eb0c15e43c52a8f779`
- Último commit: feat: add human-confirmed location picker (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/89529ef62f458f9f010920eb0c15e43c52a8f779
- Comparación: behind; ahead 0, behind 357; 0 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: ninguna reportada
- Lectura: Selector de ubicación web para Mapas Vivos; revisar geolocalización/permisos y compatibilidad con backend.
- Pruebas: no ejecutadas.
- Recomendación: rastrear PR y CI por SHA; rescatar solo cambios no presentes en main y aún necesarios.

## feat/night-blue-unified-header
- SHA: `b86b5fc6436f4629f26a284eaa992aa6ac4327d4`
- Último commit: feat: unify night blue theme and application header (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/b86b5fc6436f4629f26a284eaa992aa6ac4327d4
- Comparación: behind; ahead 0, behind 390; 0 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: ninguna reportada
- Lectura: Consolidación de encabezado/tema visual; probable cambio de presentación, verificar alcance y adopción.
- Pruebas: no ejecutadas.
- Recomendación: rastrear PR y CI por SHA; rescatar solo cambios no presentes en main y aún necesarios.
