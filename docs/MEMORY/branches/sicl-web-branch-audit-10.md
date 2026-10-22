# SICL Web — auditoría de ramas (lote 10: red team, RFC y pruebas)

Base: `main@9ae8fe504bbb964d8b89d87709ee773e64cbbacb`. Pruebas no ejecutadas durante esta auditoría.

## redteam/deepseek/e2e002-phase1
- SHA: `89991017fe5b76986484a56c816b48204fb9c3cb`
- Comparación: diverged; ahead 148, behind 88; commits exclusivos 148; rutas reportadas 59.
- Rutas representativas: .github/workflows/compas-capability.yml, .github/workflows/e2e002-phase1.yml, docs/ARKI_OPERATIONAL_ARCHITECTURE_FREEZE_1_0.md, docs/redteam/ARKI_V0_6_RC_ROUND1_HANDOFF.md, requirements-compas.txt, server/agk/familyCompiler.test.ts
- Avance e interpretación: Dos nombres de red team apuntan al mismo SHA; son alias de la misma referencia de contenido, no dos avances independientes. Debe revisarse la evidencia adversarial E2E-002 y su cobertura.
- Pruebas: no ejecutadas ahora; no convertir el nombre test/verify en resultado aprobado.
- Recomendación: recuperar logs por SHA y verificar solapamiento con main; conservar evidencia adversarial con alcance y límites explícitos.

## redteam/qwen/e2e002-phase1
- SHA: `89991017fe5b76986484a56c816b48204fb9c3cb`
- Comparación: diverged; ahead 148, behind 88; commits exclusivos 148; rutas reportadas 59.
- Rutas representativas: .github/workflows/compas-capability.yml, .github/workflows/e2e002-phase1.yml, docs/ARKI_OPERATIONAL_ARCHITECTURE_FREEZE_1_0.md, docs/redteam/ARKI_V0_6_RC_ROUND1_HANDOFF.md, requirements-compas.txt, server/agk/familyCompiler.test.ts
- Avance e interpretación: Dos nombres de red team apuntan al mismo SHA; son alias de la misma referencia de contenido, no dos avances independientes. Debe revisarse la evidencia adversarial E2E-002 y su cobertura.
- Pruebas: no ejecutadas ahora; no convertir el nombre test/verify en resultado aprobado.
- Recomendación: recuperar logs por SHA y verificar solapamiento con main; conservar evidencia adversarial con alcance y límites explícitos.

## rfc-002-phase-d
- SHA: `c228a2ae2361f0fd1264557b9b742c922184cf18`
- Comparación: behind; ahead 0, behind 471; commits exclusivos 0; rutas reportadas 0.
- Rutas representativas: sin rutas únicas reportadas
- Avance e interpretación: Trabajo de fase D de RFC-002; contrastar el alcance de evidencia/HTTP y su contrato con Core.
- Pruebas: no ejecutadas ahora; no convertir el nombre test/verify en resultado aprobado.
- Recomendación: recuperar logs por SHA y verificar solapamiento con main; conservar evidencia adversarial con alcance y límites explícitos.

## rfc-015-phase-a
- SHA: `9ab6c8b2ad202b44f1e498eb1a084a75d705b393`
- Comparación: behind; ahead 0, behind 466; commits exclusivos 0; rutas reportadas 0.
- Rutas representativas: sin rutas únicas reportadas
- Avance e interpretación: Fase A de RFC-015; revisar si las decisiones de frontend ya se integraron y qué queda documental.
- Pruebas: no ejecutadas ahora; no convertir el nombre test/verify en resultado aprobado.
- Recomendación: recuperar logs por SHA y verificar solapamiento con main; conservar evidencia adversarial con alcance y límites explícitos.

## style/command-bar-contrast
- SHA: `661b37094a6bd4501b543c94728474e211cf9c7e`
- Comparación: behind; ahead 0, behind 441; commits exclusivos 0; rutas reportadas 0.
- Rutas representativas: sin rutas únicas reportadas
- Avance e interpretación: Ajuste visual de contraste de la command bar.
- Pruebas: no ejecutadas ahora; no convertir el nombre test/verify en resultado aprobado.
- Recomendación: recuperar logs por SHA y verificar solapamiento con main; conservar evidencia adversarial con alcance y límites explícitos.

## test/arki-autonomy-offline-ci-20261014
- SHA: `3950e403f2b9aa1464a38e25fe543b06c1eb87dc`
- Comparación: diverged; ahead 914, behind 59; commits exclusivos 914; rutas reportadas 264.
- Rutas representativas: .github/workflows/arki-assembly-planner.yml, .github/workflows/arki-controlled-executor.yml, .github/workflows/arki-f1-f10-evidence.yml, .github/workflows/arki-research-trends.yml, .github/workflows/av-ui-001-tree-twin.yml, .github/workflows/maqueta-viva-smoke.yml
- Avance e interpretación: CI offline para autonomía; verificar que no dependa de secretos/red y que pruebe el módulo exacto de MEMORY.
- Pruebas: no ejecutadas ahora; no convertir el nombre test/verify en resultado aprobado.
- Recomendación: recuperar logs por SHA y verificar solapamiento con main; conservar evidencia adversarial con alcance y límites explícitos.

## test/e2e001-agk-path-canary
- SHA: `746f2eebf1763e8be74e2e4d52f10d304221d945`
- Comparación: diverged; ahead 11, behind 88; commits exclusivos 11; rutas reportadas 6.
- Rutas representativas: server/agk/familyCompiler.test.ts, server/agk/familyCompiler.ts, server/agk/regeneration.ts, server/agk/types.ts, server/arkiGeometryKernel.test.ts, server/arkiGeometryKernel.ts
- Avance e interpretación: Canary de ruta AGK para E2E-001; es evidencia acotada a la ruta/caso de prueba.
- Pruebas: no ejecutadas ahora; no convertir el nombre test/verify en resultado aprobado.
- Recomendación: recuperar logs por SHA y verificar solapamiento con main; conservar evidencia adversarial con alcance y límites explícitos.

## test/maqueta-viva-construction-waves-e3
- SHA: `df700c4a71dbc9c8ae44636c1388444aa34027e5`
- Comparación: diverged; ahead 433, behind 59; commits exclusivos 433; rutas reportadas 88.
- Rutas representativas: .github/workflows/arki-controlled-executor.yml, .github/workflows/arki-f1-f10-evidence.yml, .github/workflows/arki-research-trends.yml, .github/workflows/maqueta-viva-smoke.yml, ARKI-MAQUETA-VIVA.cmd, ARKI-RESEARCH-WATCH.cmd
- Avance e interpretación: Pruebas de construcción de ondas/precedencias de Maqueta Viva; relacionar con ciclos, dependencias faltantes y FROZEN.
- Pruebas: no ejecutadas ahora; no convertir el nombre test/verify en resultado aprobado.
- Recomendación: recuperar logs por SHA y verificar solapamiento con main; conservar evidencia adversarial con alcance y límites explícitos.

## verify/commit-6
- SHA: `44a19eb49c024693c15d07e3a1b6d02cc402d3b3`
- Comparación: behind; ahead 0, behind 174; commits exclusivos 0; rutas reportadas 0.
- Rutas representativas: sin rutas únicas reportadas
- Avance e interpretación: Rama de verificación identificada como commit-6; necesita leer workflow/commit para entender el criterio que verifica.
- Pruebas: no ejecutadas ahora; no convertir el nombre test/verify en resultado aprobado.
- Recomendación: recuperar logs por SHA y verificar solapamiento con main; conservar evidencia adversarial con alcance y límites explícitos.
