# SICL Core — auditoría de ramas (lote 8: recomputación, Mapas Vivos y RFC)

Base histórica: `main@de43b6b833731c87fb6277834484545bd953d76a`.  
Última verificación de este documento: 2026-10-22.

## feat/h005-selective-recomputation
- SHA histórico: `fb21a863a6262e0c7337993825de6b03e68a4b44`.
- Comparación previamente registrada: behind, ahead 0, behind 120; sin commits exclusivos.
- Lectura: recomputación selectiva; definir invalidación y dependencias para no reutilizar resultados obsoletos.
- Pruebas de esa rama: no ejecutadas en esta auditoría.
- Dictamen: no rescatar contenido de una rama que no presenta commits exclusivos según esa comparación.

## feat/multiscale-capability-foundation-s7p05
- SHA histórico: `4c2017957354bd40c035c5e5bd2cd2fab7efbc58`.
- Comparación previamente registrada: behind, ahead 0, behind 176; sin commits exclusivos.
- Lectura: base multiescala de capacidades; verificar interfaces y evidencia Web/Core solo si vuelve a aparecer contenido exclusivo.

## feat/mv-p1-final-integration
- SHA histórico: `42cb5a84846c9ec52b902d2abc9e570be527b56d`.
- Comparación previamente registrada: behind, ahead 0, behind 171; sin commits exclusivos.
- Dictamen: no hay cambio exclusivo que rescatar desde esa punta histórica.

## feat/mv-p1-runtime-variable-foundation
- SHA histórico: `57b095ebd0d19fff25503910fc24253e6bc24bc2`.
- Comparación previamente registrada: behind, ahead 0, behind 183; sin commits exclusivos.

## feat/mv-p1-spatial-location-runtime
- SHA histórico: `c56e550ecba21c790dbeeb09915d16e0aa06d50a`.
- Comparación previamente registrada: behind, ahead 0, behind 182; sin commits exclusivos.

## feat/rfc-030-drawing-standard
- SHA histórico: `6fb8be85ca706987ed8fcc5e2e4fbdda97e7de94`.
- La rama se registró históricamente como divergente, con 6 commits exclusivos y 42 rutas. Requiere reconciliación selectiva contra los módulos actuales de dibujo. El rule set vigente de main es `data/drawing_rules/iso128_rne_peru.json`; la variante NTE es histórica y no debe copiarse sin verificar su autoridad normativa.

## feat/rfc-030-ifc-regeneration — PR #22
- PR: https://github.com/YvanCastilloQuezada/sicl-core/pull/22
- SHA histórico: `9d2b4ade66439a6237b9fc4a4f61e33e9a14f4e3`.
- Estado confirmado: cerrado sin merge el 2026-10-22; no reintegrar la rama completa.
- Motivos: versión obsoleta respecto de `main`, divergencia, regla de dibujo antigua y tests que no demuestran fidelidad profesional. El CI histórico falló al coleccionar tests por falta de `reportlab` tras modificar el extra de test.
- Main sí contiene los módulos `src/sicl/drawing`, `src/sicl/layout`, pruebas y artefactos RFC-030/RFC-034.1. Su existencia no equivale a graduación DAM ni reproducción profesional acreditada.

## RFC-034.1 — PR #21 cerrado sin merge
- PR: https://github.com/YvanCastilloQuezada/sicl-core/pull/21
- Estado confirmado el 2026-10-22: cerrado sin merge; rama `feat/rfc-034-1-layout-engine`.
- Comparación actual consultada después de PR #22: 4 commits ahead, 168 behind, divergente; 39 rutas con cambios.
- El diff incluye una implementación antigua de `src/sicl/drawing`/ `src/sicl/layout`, `iso128_nte_peru.json`, IFC sintético, reportes y PDF fixtures. No fusionar esa rama en bloque.
- Main conserva estos archivos vigentes: `src/sicl/drawing/projector.py` SHA `5ba4ce4df128b9273115d8436551fd18dae5f972`, `tests/test_rfc030_drawing.py` SHA `b720018331ce451de2e0f2767b4634f812010e04`, `src/sicl/layout/layout_engine.py` SHA `7a4df2433ea3a7e4fd0261883966b98a121cc614`, `tests/test_rfc0341_layout.py` SHA `9211e3f5d9233ac463539c4ddbb0b736f6f91d0d`, `data/drawing_rules/iso128_rne_peru.json` SHA `4539f65960e855009b18ca6346382be79e23f72d`.
- Dictamen: conservar la procedencia; si se necesita recuperar alguna capacidad, hacerlo por archivo/commit concreto después de comparación funcional. No copiar fixtures y PDF como evidencia de conformidad sin revisar contenido y procedencia.

## PR #41 y #42 — bloque 6.11 / promoción concurrente
- PR #42: https://github.com/YvanCastilloQuezada/sicl-core/pull/42. Cerrado como merged; merge SHA `588d8fa44dab7122a718e98bc1dec579c697cdbe`.
- PR #41: https://github.com/YvanCastilloQuezada/sicl-core/pull/41. Cerrado como merged; merge SHA `e89577adb5ed1a6b58e57d06ed080b9a7f1dac54`.
- Sus descripciones originales decían “Do not merge”/“closed without merge”; las descripciones se reconciliaron el 2026-10-22 para distinguir intención histórica de estado real en GitHub.
- El código de promoción está presente en main. No declarar cerrado todo el bloque 6.11 por solo haber fusionado esos PR: los gates de migración, esquema y benchmark no estaban ejecutándose en el workflow general.
- Correcciones aplicadas directamente a main el 2026-10-22:
  - `tests/verification/ci_v1_v5_schema_state_gate.py`: V-3 ahora construye explícitamente un esquema migrado antes de reabrirlo, en vez de crear una base nueva y probar de nuevo el bootstrap.
  - `.github/workflows/ci.yml`: incluye el gate V-1..V-5, migración M-1..M-12 y benchmark del ledger sobre más de 100.000 snapshots.
- Evidencia exacta: commit de prueba `6a7a0b563d4b22211bd655dc07f86a9460b0f03e`; commit de CI `ddd892b7f756a6d841f488c25f51ef8f2362fe83`. GitHub Actions run `39861675115` completó con éxito los trabajos Python 3.11 y 3.12, incluyendo pytest, los tres gates explícitos y compileall.
- Estado separado de despliegue: los checks de Railway para `sicl-core` y `sicl-web` siguen reportando fallo para ese SHA en la última consulta. CI verde no implica despliegue verde.

## Reglas de auditoría
1. Comparar contra la punta vigente de main, no contra una base histórica.
2. Una rama cerrada no significa necesariamente merged; consultar `merged` y merge SHA.
3. No asumir que un PDF/IFC fixture prueba calidad de salida sin validación independiente de geometría, escala, vistas y contenido.
4. Una suite genérica verde no sustituye los gates explícitos congelados.
5. No tocar el contrato FROZEN ni cambiar la autoridad canónica como parte de recuperación documental.
6. No crear ramas nuevas para esta auditoría; hacer correcciones acotadas directamente en main cuando son inequívocas, con pruebas y SHA.
