# SICL Web — auditoría de ramas (lote 4: RFC, ideas, ACS y AGK)

Base: `main@9ae8fe504bbb964d8b89d87709ee773e64cbbacb`. No se ejecutaron pruebas.

## docs/rfc015-026-coherence-audit
- SHA: `9a3bcec52b230ba3831eda4eefd95f22bfbb9642`
- Último commit: docs: align frontend references with RFC-015 to RFC-026 audit (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/9a3bcec52b230ba3831eda4eefd95f22bfbb9642
- Diferencia contra main: behind; ahead 0, behind 406; 0 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: sin rutas únicas reportadas
- Avance e interpretación: Auditoría de coherencia RFC-015 a RFC-026; útil como mapa de contratos, pero requiere leer conclusiones y distinguir propuesta, decisión e implementación.
- Pruebas: no ejecutadas ahora.
- Recomendación: rastrear PR, commits exclusivos y dependencias; no promover cambios solo por documentación o nombre.

## docs/rfc-015-frontend-v2
- SHA: `4255d1bf3a19036811129792a34d04f76a33d8a5`
- Último commit: docs: align RFC-015 with functional frontend scope (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/4255d1bf3a19036811129792a34d04f76a33d8a5
- Diferencia contra main: behind; ahead 0, behind 468; 0 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: sin rutas únicas reportadas
- Avance e interpretación: Frontend v2 para RFC-015; comparar con main y el handoff más reciente antes de recuperar UI.
- Pruebas: no ejecutadas ahora.
- Recomendación: rastrear PR, commits exclusivos y dependencias; no promover cambios solo por documentación o nombre.

## docs/rfc-024-system-completion
- SHA: `ca8e4f931c7d0ef0d9b57c153b5b484cfce82a3e`
- Último commit: Checkpoint: Actualiza RFC-024 para registrar la fase operativa inicial implementada: health check server-side, correlation IDs, timeout del proxy, clasificación de errores y 124/124 tests PASS. Mantiene el RFC en DRAFT y declara el E2E remoto como BLOCKED_INFRASTRUCTURE hasta configurar URL, token y persistencia del Core. (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/ca8e4f931c7d0ef0d9b57c153b5b484cfce82a3e
- Diferencia contra main: behind; ahead 0, behind 410; 0 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: sin rutas únicas reportadas
- Avance e interpretación: Trabajo documental sobre RFC-024/system completion; las especificaciones no autorizan por sí solas implementación ni despliegue.
- Pruebas: no ejecutadas ahora.
- Recomendación: rastrear PR, commits exclusivos y dependencias; no promover cambios solo por documentación o nombre.

## experiment/arki-ideas-web-20261015
- SHA: `457d83df9aad1fa2ae4d56c81c40e6e434c043b0`
- Último commit: experiment(arki): preserve source document WEB-IDEA-002 (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/457d83df9aad1fa2ae4d56c81c40e6e434c043b0
- Diferencia contra main: diverged; ahead 4, behind 59; 4 commits exclusivos; 4 rutas reportadas.
- Rutas únicas: added docs/arki-ideas/BRANCH_INVENTORY_20261015.md, added docs/arki-ideas/RECOVERY_PROTOCOL.md, added experiments/arki-ideas/WEB-IDEA-001/docs/ARKI_AUTONOMOUS_RELATION_DISCOVERY_20261014.md, added experiments/arki-ideas/WEB-IDEA-002/docs/ARKI_UNIFIED_TRACE_GRAPH_V1.md
- Avance e interpretación: Repositorio de ideas/experimentos; preservar aislamiento y no tratar código experimental como capacidad productiva. Revisar ledger de extracción y pruebas antes de promover.
- Pruebas: no ejecutadas ahora.
- Recomendación: rastrear PR, commits exclusivos y dependencias; no promover cambios solo por documentación o nombre.

## feat/acs-v1-integration-lab
- SHA: `7bf9786a99d2ffa07dd32c43f426c12657abb2f9`
- Último commit: docs: freeze ARKI v0.6 E2E-002 Phase 1 (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/7bf9786a99d2ffa07dd32c43f426c12657abb2f9
- Diferencia contra main: diverged; ahead 149, behind 88; 149 commits exclusivos; 60 rutas reportadas.
- Rutas únicas: added .github/workflows/compas-capability.yml, added .github/workflows/e2e002-phase1.yml, added docs/ARKI_OPERATIONAL_ARCHITECTURE_FREEZE_1_0.md, added docs/freeze/ARKI_V0_6_E2E002_PHASE1_FREEZE.md, added docs/redteam/ARKI_V0_6_RC_ROUND1_HANDOFF.md, added requirements-compas.txt, added server/agk/familyCompiler.test.ts, added server/agk/familyCompiler.ts, modified server/agk/regeneration.ts, modified server/agk/types.ts, modified server/arkiGeometryKernel.test.ts, modified server/arkiGeometryKernel.ts
- Avance e interpretación: Puente de integración ACS en Web; revisar el contrato de evidencia y el límite de que ACS no es la autoridad de Core.
- Pruebas: no ejecutadas ahora.
- Recomendación: rastrear PR, commits exclusivos y dependencias; no promover cambios solo por documentación o nombre.

## feat/agk-001-operational-spine
- SHA: `2bb70a433bec6963f21d08bb25460b539c8adf1b`
- Último commit: fix(agk): type transaction provenance receipt (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/2bb70a433bec6963f21d08bb25460b539c8adf1b
- Diferencia contra main: behind; ahead 0, behind 104; 0 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: sin rutas únicas reportadas
- Avance e interpretación: Espina operativa AGK: identificar qué contratos y pruebas sobreviven en main y verificar evidencia geométrica real, no solo tests sintéticos.
- Pruebas: no ejecutadas ahora.
- Recomendación: rastrear PR, commits exclusivos y dependencias; no promover cambios solo por documentación o nombre.

## feat/agk-002-causal-regeneration
- SHA: `a41cc8fb8bf0fa2a2dd4d45f60993d66c3bc8bae`
- Último commit: test(agk): close causal identity graph consistency and immutability gaps (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/a41cc8fb8bf0fa2a2dd4d45f60993d66c3bc8bae
- Diferencia contra main: behind; ahead 0, behind 89; 0 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: sin rutas únicas reportadas
- Avance e interpretación: Regeneración causal AGK: validar identidad/intent y regeneración con evidencia; no asumir integración por el nombre de la rama.
- Pruebas: no ejecutadas ahora.
- Recomendación: rastrear PR, commits exclusivos y dependencias; no promover cambios solo por documentación o nombre.

## feat/agk-003-parametric-family-unification
- SHA: `e8b47c31cdf7d3317ade7a312012fcbf065872b8`
- Último commit: Harden AGK CI paths for L-04 verification (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/e8b47c31cdf7d3317ade7a312012fcbf065872b8
- Diferencia contra main: diverged; ahead 11, behind 88; 11 commits exclusivos; 7 rutas reportadas.
- Rutas únicas: added .github/workflows/compas-capability.yml, added server/agk/familyCompiler.test.ts, added server/agk/familyCompiler.ts, modified server/agk/regeneration.ts, modified server/agk/types.ts, modified server/arkiGeometryKernel.test.ts, modified server/arkiGeometryKernel.ts
- Avance e interpretación: Unificación de familias paramétricas AGK; comprobar dependencias con operational spine y causal regeneration para evitar integrar piezas incompatibles.
- Pruebas: no ejecutadas ahora.
- Recomendación: rastrear PR, commits exclusivos y dependencias; no promover cambios solo por documentación o nombre.
