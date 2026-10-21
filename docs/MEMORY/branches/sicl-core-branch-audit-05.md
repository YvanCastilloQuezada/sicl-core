# SICL Core — auditoría de ramas (lote 5: representación 3D y ARE)

Base: `main@de43b6b833731c87fb6277834484545bd953d76a`. Pruebas no ejecutadas.

## feat/arki3d-archi-model
- SHA: `cbf09ac36e3e704caa83bd92a00299b44b68e039`
- Último commit: fix(d2.2r): close post-commit IFC cleanup window (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/cbf09ac36e3e704caa83bd92a00299b44b68e039
- Comparación: behind; ahead 0, behind 104; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Modelo arquitectónico 3D; determinar si es esquema, escena, runtime o representación demostrada.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: verificar dependencias, pruebas y contrato Core antes de integrar.

## feat/arki-are-001-contract
- SHA: `e80bd3a21a3f7db6f543e99e4106c103904e2a4f`
- Último commit: docs(architecture): close ARE source and dependency semantics (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/e80bd3a21a3f7db6f543e99e4106c103904e2a4f
- Comparación: behind; ahead 0, behind 97; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Contrato de ARKIRE; fijar límites antes de implementar.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: verificar dependencias, pruebas y contrato Core antes de integrar.

## feat/arki-are-002-runtime-foundation
- SHA: `4208106b347bf8685fce1b3a1df754d5ce960bd8`
- Último commit: fix(are): derive freshness from source authority (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/4208106b347bf8685fce1b3a1df754d5ce960bd8
- Comparación: behind; ahead 0, behind 93; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Fundación de runtime ARE; revisar dependencias con contrato y seguridad.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: verificar dependencias, pruebas y contrato Core antes de integrar.

## feat/arki-are-003-2d-projection
- SHA: `c914a279d688aada4e036c8e0c7aafab3f3e7afc`
- Último commit: fix(are): enforce projection view semantics (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/c914a279d688aada4e036c8e0c7aafab3f3e7afc
- Comparación: behind; ahead 0, behind 90; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Proyección 2D; verificar que sea derivada de modelo y no segunda autoridad geométrica.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: verificar dependencias, pruebas y contrato Core antes de integrar.

## feat/arki-case-001-controlled-house
- SHA: `34617e0b3c51143eafe8187fe1fcc67338115314`
- Último commit: test(case): add controlled house E2E validation (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/34617e0b3c51143eafe8187fe1fcc67338115314
- Comparación: diverged; ahead 1, behind 85; commits exclusivos 1; rutas 7.
- Rutas: artifacts/arki-case-001/ARKI_CASE_001_BASE.svg, artifacts/arki-case-001/ARKI_CASE_001_EVIDENCE.json, artifacts/arki-case-001/ARKI_CASE_001_MUTATED.svg, artifacts/arki-case-001/ARKI_CASE_001_TRACEABILITY.json, docs/cases/ARKI_CASE_001_REPORT.md, scripts/arki_case_001.py
- Lectura: Caso de vivienda controlada; clasificar fixtures sintéticos y evidencia real.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: verificar dependencias, pruebas y contrato Core antes de integrar.

## feat/arki-m1-vector-plan-pipeline
- SHA: `944dd524a112f3feb1007ddbed27f308549bc77d`
- Último commit: fix(arkidraw): enforce graphic trace integrity (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/944dd524a112f3feb1007ddbed27f308549bc77d
- Comparación: behind; ahead 0, behind 86; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Pipeline vectorial de planos; revisar transformaciones, trazabilidad y datos de entrada.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: verificar dependencias, pruebas y contrato Core antes de integrar.

## feat/arki-phase1-multimaster
- SHA: `39b7798c762dd3464811d6d4d2eae366441fc262`
- Último commit: docs(arki): record phase1 multi-master learning (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/39b7798c762dd3464811d6d4d2eae366441fc262
- Comparación: diverged; ahead 7, behind 158; commits exclusivos 7; rutas 55.
- Rutas: data/drawing_rules/README.md, data/drawing_rules/iso128_nte_peru.json, data/drawing_rules/iso128_rne_peru.json, data/drawing_symbols/default_symbols.json, data/title_blocks/peru_generic.json, docs/learning/PHASE1_REPORT.md
- Lectura: Fase 1 multimaster; revisar consistencia transaccional y fuentes de verdad.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: verificar dependencias, pruebas y contrato Core antes de integrar.

## feat/arkidraw-block1
- SHA: `90e1bd74f2dc7de82792e5bf811369cd4c954269`
- Último commit: fix(arkidraw): enforce dimension kind semantics (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/90e1bd74f2dc7de82792e5bf811369cd4c954269
- Comparación: behind; ahead 0, behind 114; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: ARKIDraw bloque 1; identificar primitives/contratos y su relación con bloques posteriores.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: verificar dependencias, pruebas y contrato Core antes de integrar.
