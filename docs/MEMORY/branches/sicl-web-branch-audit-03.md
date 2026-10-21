# SICL Web — auditoría de ramas (lote 3: CI, Árbol Vivo y documentación)

Base: `main@9ae8fe504bbb964d8b89d87709ee773e64cbbacb`. No se ejecutaron pruebas en esta auditoría.

## audit/l04-workflow-base-044707a
- SHA: `044707afd870d1e3a81b3556b9c1bd1432469784`
- Último commit: Test opaque AGK provenance snapshot semantics (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/044707afd870d1e3a81b3556b9c1bd1432469784
- Diferencia contra main: diverged; ahead 103, behind 88; 103 commits exclusivos; 51 rutas reportadas.
- Rutas únicas: added .github/workflows/compas-capability.yml, added docs/ARKI_OPERATIONAL_ARCHITECTURE_FREEZE_1_0.md, added requirements-compas.txt, added server/agk/familyCompiler.test.ts, added server/agk/familyCompiler.ts, modified server/agk/regeneration.ts, modified server/agk/types.ts, modified server/arkiGeometryKernel.test.ts, modified server/arkiGeometryKernel.ts, added server/capabilityFabric/architecturalCapabilityRepository.test.ts, added server/capabilityFabric/architecturalCapabilityRepository.ts, added server/capabilityFabric/architecturalResearchHarvest.test.ts
- Avance e interpretación: Auditoría de base de workflow: revisar el estado que se usó para construir CI y si main ya lo reemplazó.
- Evidencia de pruebas: no ejecutadas ahora; consultar Actions/logs para el SHA exacto.
- Recomendación: no fusionar solo por etiqueta de rama; seleccionar contenido con evidencia y aprobación.

## ci/arki-f1-f10-evidence-runner-v1
- SHA: `ddb248afd179bae4e35a47916141c934f189dee7`
- Último commit: ci(arki): eliminate cross-branch F8 green; enforce original discovery on PR tree (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/ddb248afd179bae4e35a47916141c934f189dee7
- Diferencia contra main: diverged; ahead 12, behind 59; 12 commits exclusivos; 8 rutas reportadas.
- Rutas únicas: added .github/workflows/arki-f1-f10-evidence.yml, added scripts/arki-phase-evidence-runner.mjs, added server/arkiF7F8Closure.test.ts, added server/arkiF9ConstructionLineage.ts, added server/arkiProfessionalState.ts, added server/arkiProjectEconomicTwin.ts, added server/arkiTechnicalDossier.ts, added shared/arkiCanonicalRefs.ts
- Avance e interpretación: Rama de Evidence Runner F1–F10: comparar workflow, scripts y recibos con los tests/artefactos en main. Un workflow presente no demuestra que el runner haya pasado en el SHA actual.
- Evidencia de pruebas: no ejecutadas ahora; consultar Actions/logs para el SHA exacto.
- Recomendación: no fusionar solo por etiqueta de rama; seleccionar contenido con evidencia y aprobación.

## ci/pr52-merge-candidate-e3-20261010
- SHA: `5b054fc59a4838664e6afb7f43ac0a55b63c51ff`
- Último commit: Merge ddb248afd179bae4e35a47916141c934f189dee7 into ec6ede75a13e6a346816dfd96816272926a575b9 (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/5b054fc59a4838664e6afb7f43ac0a55b63c51ff
- Diferencia contra main: diverged; ahead 13, behind 59; 13 commits exclusivos; 8 rutas reportadas.
- Rutas únicas: added .github/workflows/arki-f1-f10-evidence.yml, added scripts/arki-phase-evidence-runner.mjs, added server/arkiF7F8Closure.test.ts, added server/arkiF9ConstructionLineage.ts, added server/arkiProfessionalState.ts, added server/arkiProjectEconomicTwin.ts, added server/arkiTechnicalDossier.ts, added shared/arkiCanonicalRefs.ts
- Avance e interpretación: Candidato de merge/validación E3 relacionado históricamente con PR #52; revisar merge-tree y evidencia específica. No asumir que PR antiguo está integrado.
- Evidencia de pruebas: no ejecutadas ahora; consultar Actions/logs para el SHA exacto.
- Recomendación: no fusionar solo por etiqueta de rama; seleccionar contenido con evidencia y aprobación.

## docs/av-ui-001-preparation-20261010
- SHA: `02c176d6d317fc45142520f099287f9b0bd356b1`
- Último commit: Merge pull request #56 from YvanCastilloQuezada/feat/arbol-vivo-autoensamblaje-20261011

ARKI: inventario real de tres repositorios y planificación segura de autoensamblaje (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/02c176d6d317fc45142520f099287f9b0bd356b1
- Diferencia contra main: diverged; ahead 708, behind 59; 708 commits exclusivos; 138 rutas reportadas.
- Rutas únicas: added .github/workflows/arki-assembly-planner.yml, added .github/workflows/arki-controlled-executor.yml, added .github/workflows/arki-f1-f10-evidence.yml, added .github/workflows/arki-research-trends.yml, added .github/workflows/av-ui-001-tree-twin.yml, added .github/workflows/maqueta-viva-smoke.yml, added 00_CONTINUIDAD_AUTOENSAMBLAJE.md, added 00_START.md, added ARKI-MAQUETA-VIVA.cmd, added ARKI-RESEARCH-WATCH.cmd, modified client/index.html, modified client/src/App.tsx
- Avance e interpretación: Preparación documental para AV-UI-001; sirve para recuperar requisitos y alcance del Árbol Vivo, no para afirmar implementación UI terminada.
- Evidencia de pruebas: no ejecutadas ahora; consultar Actions/logs para el SHA exacto.
- Recomendación: no fusionar solo por etiqueta de rama; seleccionar contenido con evidencia y aprobación.

## docs/documentation-coherence-2.11
- SHA: `092f65be1cd404ef8e5e18db86263e6c9a22a942`
- Último commit: docs: refresh help manuals and first-contact presentation (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/092f65be1cd404ef8e5e18db86263e6c9a22a942
- Diferencia contra main: behind; ahead 0, behind 408; 0 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: sin rutas únicas reportadas
- Avance e interpretación: Rama de coherencia documental; separar correcciones editoriales de cambios contractuales y verificar cuáles llegaron a main.
- Evidencia de pruebas: no ejecutadas ahora; consultar Actions/logs para el SHA exacto.
- Recomendación: no fusionar solo por etiqueta de rama; seleccionar contenido con evidencia y aprobación.

## docs/executive-presentation-2.15
- SHA: `6d8dd475de0b4ae7b2480fcbac55b8f1886341ea`
- Último commit: docs: add executive presentation index (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/6d8dd475de0b4ae7b2480fcbac55b8f1886341ea
- Diferencia contra main: behind; ahead 0, behind 402; 0 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: sin rutas únicas reportadas
- Avance e interpretación: Rama de presentación ejecutiva: probable material de comunicación; revisar el contenido antes de usarlo como especificación técnica.
- Evidencia de pruebas: no ejecutadas ahora; consultar Actions/logs para el SHA exacto.
- Recomendación: no fusionar solo por etiqueta de rama; seleccionar contenido con evidencia y aprobación.

## docs/frontend-handoff-2.14-fix
- SHA: `d0da03ace2dcc6ea68e0f13d9aabc6ad7ad4d37e`
- Último commit: docs: correct frontend handoff baseline SHA (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/d0da03ace2dcc6ea68e0f13d9aabc6ad7ad4d37e
- Diferencia contra main: behind; ahead 0, behind 403; 0 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: sin rutas únicas reportadas
- Avance e interpretación: Handoff frontend: comparar ambas variantes y la variante -fix; la corrección de nombre no prueba superioridad. Deben rastrearse commits únicos y decisiones de adopción.
- Evidencia de pruebas: no ejecutadas ahora; consultar Actions/logs para el SHA exacto.
- Recomendación: no fusionar solo por etiqueta de rama; seleccionar contenido con evidencia y aprobación.

## docs/frontend-handoff-2.14
- SHA: `89bd162d8b5f15348c0e039c2727bacb1e1f9d27`
- Último commit: docs: add frontend handoff (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/89bd162d8b5f15348c0e039c2727bacb1e1f9d27
- Diferencia contra main: behind; ahead 0, behind 404; 0 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: sin rutas únicas reportadas
- Avance e interpretación: Handoff frontend: comparar ambas variantes y la variante -fix; la corrección de nombre no prueba superioridad. Deben rastrearse commits únicos y decisiones de adopción.
- Evidencia de pruebas: no ejecutadas ahora; consultar Actions/logs para el SHA exacto.
- Recomendación: no fusionar solo por etiqueta de rama; seleccionar contenido con evidencia y aprobación.
