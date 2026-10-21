# SICL Core — auditoría de ramas (lote 8: recomputación, Mapas Vivos y RFC)

Base: `main@de43b6b833731c87fb6277834484545bd953d76a`. Tests no ejecutados.

## feat/h005-selective-recomputation
- SHA: `fb21a863a6262e0c7337993825de6b03e68a4b44`
- Último commit: fix(H-005): fail closed on malformed actions (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/fb21a863a6262e0c7337993825de6b03e68a4b44
- Comparación: behind; ahead 0, behind 120; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Recomputación selectiva; definir invalidación y dependencias para no reutilizar resultados obsoletos.
- Pruebas: no ejecutadas.
- Recomendación: identificar si el trabajo está ya integrado; si no, revisar tests, dependencias y contrato antes de rescatar.

## feat/multiscale-capability-foundation-s7p05
- SHA: `4c2017957354bd40c035c5e5bd2cd2fab7efbc58`
- Último commit: feat: add multiscale capability applicability foundation (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/4c2017957354bd40c035c5e5bd2cd2fab7efbc58
- Comparación: behind; ahead 0, behind 176; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Fundación multiescala de capacidades; revisar interfaces y evidencia entre Web/Core.
- Pruebas: no ejecutadas.
- Recomendación: identificar si el trabajo está ya integrado; si no, revisar tests, dependencias y contrato antes de rescatar.

## feat/mv-p1-final-integration
- SHA: `42cb5a84846c9ec52b902d2abc9e570be527b56d`
- Último commit: fix: make Core CI dependencies reproducible (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/42cb5a84846c9ec52b902d2abc9e570be527b56d
- Comparación: behind; ahead 0, behind 171; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Integración final Mapas Vivos P1; revisar qué variables y contratos pasan de fundación a runtime.
- Pruebas: no ejecutadas.
- Recomendación: identificar si el trabajo está ya integrado; si no, revisar tests, dependencias y contrato antes de rescatar.

## feat/mv-p1-runtime-variable-foundation
- SHA: `57b095ebd0d19fff25503910fc24253e6bc24bc2`
- Último commit: feat: add immutable multiscale variable catalog foundation (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/57b095ebd0d19fff25503910fc24253e6bc24bc2
- Comparación: behind; ahead 0, behind 183; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Base runtime de variables; importante para que el mapa vivo represente valores con procedencia.
- Pruebas: no ejecutadas.
- Recomendación: identificar si el trabajo está ya integrado; si no, revisar tests, dependencias y contrato antes de rescatar.

## feat/mv-p1-spatial-location-runtime
- SHA: `c56e550ecba21c790dbeeb09915d16e0aa06d50a`
- Último commit: feat: add traceable project spatial location runtime (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/c56e550ecba21c790dbeeb09915d16e0aa06d50a
- Comparación: behind; ahead 0, behind 182; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Runtime de ubicación espacial; revisar fuente, precisión y autoridad de coordenadas.
- Pruebas: no ejecutadas.
- Recomendación: identificar si el trabajo está ya integrado; si no, revisar tests, dependencias y contrato antes de rescatar.

## feat/rfc-030-drawing-standard
- SHA: `6fb8be85ca706987ed8fcc5e2e4fbdda97e7de94`
- Último commit: feat(rfc-030): add ISO128 RNE drawing standard (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/6fb8be85ca706987ed8fcc5e2e4fbdda97e7de94
- Comparación: diverged; ahead 6, behind 158; commits exclusivos 6; rutas 42.
- Rutas: data/drawing_rules/README.md, data/drawing_rules/iso128_nte_peru.json, data/drawing_rules/iso128_rne_peru.json, data/drawing_symbols/default_symbols.json, data/title_blocks/peru_generic.json
- Lectura: Estándar de dibujo RFC-030; verificar requisitos y conformidad del contrato.
- Pruebas: no ejecutadas.
- Recomendación: identificar si el trabajo está ya integrado; si no, revisar tests, dependencias y contrato antes de rescatar.

## feat/rfc-030-ifc-regeneration
- SHA: `9d2b4ade66439a6237b9fc4a4f61e33e9a14f4e3`
- Último commit: feat(rfc-030): regenerate IFC with ifcopenshell.api (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/9d2b4ade66439a6237b9fc4a4f61e33e9a14f4e3
- Comparación: diverged; ahead 5, behind 158; commits exclusivos 5; rutas 39.
- Rutas: data/drawing_rules/README.md, data/drawing_rules/iso128_nte_peru.json, data/drawing_symbols/default_symbols.json, data/title_blocks/peru_generic.json, docs/reference/RFC030_OUTPUT/COMPARISON.md
- Lectura: Regeneración IFC RFC-030; revisar round-trip, pérdidas y evidencia de regeneración.
- Pruebas: no ejecutadas.
- Recomendación: identificar si el trabajo está ya integrado; si no, revisar tests, dependencias y contrato antes de rescatar.

## feat/rfc-034-1-layout-engine
- SHA: `a6f727f2b3088e3ff416b937d7d4c92d2dbc55db`
- Último commit: fix(rfc-030): improve hatch cuts elevation and roof plan (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/a6f727f2b3088e3ff416b937d7d4c92d2dbc55db
- Comparación: diverged; ahead 4, behind 158; commits exclusivos 4; rutas 39.
- Rutas: data/drawing_rules/README.md, data/drawing_rules/iso128_nte_peru.json, data/drawing_symbols/default_symbols.json, data/title_blocks/peru_generic.json, docs/reference/RFC030_OUTPUT/COMPARISON.md
- Lectura: Motor de layout RFC-034.1; determinar límites del solver y datos canónicos.
- Pruebas: no ejecutadas.
- Recomendación: identificar si el trabajo está ya integrado; si no, revisar tests, dependencias y contrato antes de rescatar.
