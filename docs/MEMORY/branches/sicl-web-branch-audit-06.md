# SICL Web — auditoría de ramas (lote 6: UI, puentes espaciales y F7–F8)

Base: `main@9ae8fe504bbb964d8b89d87709ee773e64cbbacb`. No se ejecutaron pruebas.

## feat/browser-language-detection
- SHA: `8230cbd1c5daccf5b85fbb74b318980d902a898b`
- Último commit: feat: detect language from browser preferences (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/8230cbd1c5daccf5b85fbb74b318980d902a898b
- Diferencia contra main: behind; ahead 0, behind 371; 0 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: sin rutas únicas reportadas
- Avance e interpretación: Detección de idioma en navegador; evaluar impacto de UX y consistencia con la política de español por defecto.
- Pruebas: no ejecutadas ahora.
- Recomendación: comprobar CI/PR y dependencias; mantener diferenciados contrato, prueba y estado de entrega.

## feat/capability-fabric-001-contract
- SHA: `044707afd870d1e3a81b3556b9c1bd1432469784`
- Último commit: Test opaque AGK provenance snapshot semantics (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/044707afd870d1e3a81b3556b9c1bd1432469784
- Diferencia contra main: diverged; ahead 103, behind 88; 103 commits exclusivos; 51 rutas reportadas.
- Rutas únicas: added .github/workflows/compas-capability.yml, added docs/ARKI_OPERATIONAL_ARCHITECTURE_FREEZE_1_0.md, added requirements-compas.txt, added server/agk/familyCompiler.test.ts, added server/agk/familyCompiler.ts, modified server/agk/regeneration.ts, modified server/agk/types.ts, modified server/arkiGeometryKernel.test.ts, modified server/arkiGeometryKernel.ts, added server/capabilityFabric/architecturalCapabilityRepository.test.ts
- Avance e interpretación: Contrato de Capability Fabric; contrastar con ACS y el catálogo canónico para evitar duplicar conceptos de capacidad.
- Pruebas: no ejecutadas ahora.
- Recomendación: comprobar CI/PR y dependencias; mantener diferenciados contrato, prueba y estado de entrega.

## feat/command-bar
- SHA: `45919c5985209ece214af24fc1ba0786bfdd4090`
- Último commit: feat: add global SICL command bar (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/45919c5985209ece214af24fc1ba0786bfdd4090
- Diferencia contra main: behind; ahead 0, behind 446; 0 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: sin rutas únicas reportadas
- Avance e interpretación: Interfaz de barra de comandos; revisar accesibilidad y si la navegación está integrada en main.
- Pruebas: no ejecutadas ahora.
- Recomendación: comprobar CI/PR y dependencias; mantener diferenciados contrato, prueba y estado de entrega.

## feat/d63-to-d2-geometry-bridge
- SHA: `fe6f42b89a07fe2cd9f3e269bc65fc0413bb7701`
- Último commit: fix(geometry): avoid Set iteration under project TypeScript target (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/fe6f42b89a07fe2cd9f3e269bc65fc0413bb7701
- Diferencia contra main: diverged; ahead 1, behind 140; 1 commits exclusivos; 0 rutas reportadas.
- Rutas únicas: sin rutas únicas reportadas
- Avance e interpretación: Puente de topología/conocimiento a D-2; verificar que el contrato no declare geometría ejecutiva si solo demuestra representación conceptual.
- Pruebas: no ejecutadas ahora.
- Recomendación: comprobar CI/PR y dependencias; mantener diferenciados contrato, prueba y estado de entrega.

## feat/e2e001-red-team-hardening
- SHA: `d600b12d4df4d961a203a4cc85898d46fc00296b`
- Último commit: ci(e2e001): include red-test fixtures in canary paths (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/d600b12d4df4d961a203a4cc85898d46fc00296b
- Diferencia contra main: diverged; ahead 95, behind 88; 95 commits exclusivos; 51 rutas reportadas.
- Rutas únicas: added .github/workflows/compas-capability.yml, added docs/ARKI_OPERATIONAL_ARCHITECTURE_FREEZE_1_0.md, added requirements-compas.txt, added server/agk/familyCompiler.test.ts, added server/agk/familyCompiler.ts, modified server/agk/regeneration.ts, modified server/agk/types.ts, modified server/arkiGeometryKernel.test.ts, modified server/arkiGeometryKernel.ts, added server/capabilityFabric/architecturalCapabilityRepository.test.ts
- Avance e interpretación: Hardening red-team E2E-001; identificar amenazas y evidencia de mitigación en el SHA exacto.
- Pruebas: no ejecutadas ahora.
- Recomendación: comprobar CI/PR y dependencias; mantener diferenciados contrato, prueba y estado de entrega.

## feat/e2e002-spatial-reasoning-phase1
- SHA: `7bf9786a99d2ffa07dd32c43f426c12657abb2f9`
- Último commit: docs: freeze ARKI v0.6 E2E-002 Phase 1 (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/7bf9786a99d2ffa07dd32c43f426c12657abb2f9
- Diferencia contra main: diverged; ahead 149, behind 88; 149 commits exclusivos; 60 rutas reportadas.
- Rutas únicas: added .github/workflows/compas-capability.yml, added .github/workflows/e2e002-phase1.yml, added docs/ARKI_OPERATIONAL_ARCHITECTURE_FREEZE_1_0.md, added docs/freeze/ARKI_V0_6_E2E002_PHASE1_FREEZE.md, added docs/redteam/ARKI_V0_6_RC_ROUND1_HANDOFF.md, added requirements-compas.txt, added server/agk/familyCompiler.test.ts, added server/agk/familyCompiler.ts, modified server/agk/regeneration.ts, modified server/agk/types.ts
- Avance e interpretación: Fase 1 de razonamiento espacial E2E-002; la comparación muestra posible identidad de SHA con la rama ACS integration, revisar solapamiento y PR.
- Pruebas: no ejecutadas ahora.
- Recomendación: comprobar CI/PR y dependencias; mantener diferenciados contrato, prueba y estado de entrega.

## feat/f7-f8-integral-closure
- SHA: `3e54b987b3a61b4ca66373255bebd30db8128100`
- Último commit: chore(arki): relocate ADN bridge to branch containing its dependency (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/3e54b987b3a61b4ca66373255bebd30db8128100
- Diferencia contra main: diverged; ahead 438, behind 59; 438 commits exclusivos; 90 rutas reportadas.
- Rutas únicas: added .github/workflows/arki-controlled-executor.yml, added .github/workflows/arki-f1-f10-evidence.yml, added .github/workflows/arki-research-trends.yml, added .github/workflows/maqueta-viva-smoke.yml, added ARKI-MAQUETA-VIVA.cmd, added ARKI-RESEARCH-WATCH.cmd, modified client/index.html, modified client/src/App.tsx, modified client/src/components/ArkiFirstContact.tsx, modified client/src/pages/ArkiDesignFunnelPage.tsx
- Avance e interpretación: Cierre integral F7–F8; por volumen de commits, revisar merge-tree, contratos y tests sin tratar la rama como lista para integrar.
- Pruebas: no ejecutadas ahora.
- Recomendación: comprobar CI/PR y dependencias; mantener diferenciados contrato, prueba y estado de entrega.

## feat/f7-f8-professional-delivery-v1
- SHA: `4e8c6cc12d5bc9bf50ce6b7488784a06bf34b4b5`
- Último commit: docs(audit): add F5-F9 offline red-team evidence pack (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/4e8c6cc12d5bc9bf50ce6b7488784a06bf34b4b5
- Diferencia contra main: diverged; ahead 75, behind 59; 75 commits exclusivos; 31 rutas reportadas.
- Rutas únicas: modified client/index.html, modified client/src/App.tsx, modified client/src/components/ArkiFirstContact.tsx, modified client/src/pages/ArkiSuperarchitectCommandCenterPage.tsx, added docs/arki-master-map/AGK_DELTA_005_PERSISTENT_NAMING_CONTRACT_V1.md, modified docs/arki-master-map/AGK_OCCT_EXECUTION_EVIDENCE_V1.md, added docs/arki-master-map/ARKI_CAPABILITY_INSERTION_MAP_FROM_BUSINESS_PUBLIC_WORKS_V1.md, added docs/arki-master-map/ARKI_F5_F9_PRE_IMPLEMENTATION_RED_TEAM_DOSSIER_V1.md, added docs/arki-master-map/ARKI_F5_F9_RED_TEAM_OFFLINE_EVIDENCE_PACK_V1.md, added docs/arki-master-map/ARKI_F6_AGK_INTEGRAL_CLOSURE_GATE_V1.md
- Avance e interpretación: Entrega profesional F7–F8; comparte SHA con rama de evidencia T4–T7, por lo que hay que identificar si son refs al mismo historial/estado.
- Pruebas: no ejecutadas ahora.
- Recomendación: comprobar CI/PR y dependencias; mantener diferenciados contrato, prueba y estado de entrega.
