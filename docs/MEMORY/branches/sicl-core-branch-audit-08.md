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
- SHA histórico de PR #22: `9d2b4ade66439a6237b9fc4a4f61e33e9a14f4e3`.
- PR: [#22](https://github.com/YvanCastilloQuezada/sicl-core/pull/22), sigue abierto, no fusionado, `mergeable=false`; base registrado por PR: `1aba412f9fdb035c970a18b2a6f60b58a19cd662`, obsoleto frente a main actual.
- Comparación actual `main@6dd4f3006450754e2fab01ff4040b5ba79afb0bc...feat/rfc-030-ifc-regeneration`: `diverged`, 5 commits de rama y 162 commits detrás de main.
- CI histórico del PR: [run 36274189118](https://github.com/YvanCastilloQuezada/sicl-core/actions/runs/36274189118) FAIL en Python 3.12 durante colección; Python 3.11 cancelado. Causa real: `ModuleNotFoundError: No module named 'reportlab'` al importar `sicl.drawing.pdf_export`; `pyproject.toml` de la rama había quitado `reportlab` de `.[test]` aunque PDF exporter y tests lo importan.
- La funcionalidad de RFC-030/RFC-034.1 está en gran parte ya en main con implementaciones distintas y más recientes. Se confirmó en main: `src/sicl/drawing/__init__.py`, `ifc_synthetic.py`, `projector.py`, `pdf_export.py`, `http_api.py`, `composer.py`, `scripts/generate_synthetic_ifc.py`, `scripts/drawing_cli.py`, `src/sicl/layout/layout_engine.py`, `src/sicl/layout/http_api.py`, tests `test_rfc030_drawing.py` y `test_rfc0341_layout.py`, y RFCs/documentación correspondientes.
- Regla de seguridad de generación IFC ya mejorada en main: el helper recibe un destino/archivo temporal, en vez de reescribir silenciosamente el IFC rastreado.
- No integrar el PR #22 en bloque: las versiones de rama tienen diferencias respecto del estado más nuevo de main, usan rule set obsoleto `iso128_nte_peru.json` frente a `iso128_rne_peru.json`, y los tests contienen afirmaciones triviales (`or True`, comprobación de título que acepta cualquier longitud, el modo PDF no valida número de páginas). Son señal de que falta prueba real de calidad, no evidencia de salida profesional.
- Dependencias: el PR/branch editaba `pyproject.toml` removiendo `reportlab` y dependencias base. No copiar ese cambio; main conserva `reportlab>=4,<5` en `.[test]`. CI actual de main pasa en Python 3.11/3.12.
- Estado de producto: RFC-030 documentado como base técnica, pero la fase DAM de dibujo sigue bloqueada para graduación según `docs/learning/PHASE1_REPORT.md`: se probó IfcOpenShell Draw (1.094 entidades, SVG 62.135 bytes), pero solo un maestro disponible, el IFC no corresponde al fixture A-01, y no se reprodujo indistinguiblemente el plano. No declarar graduación ni calidad profesional demostrada.
- Dictamen actual: **cerrar PR #22 sin fusionar**, conservar el registro de procedencia y continuar desde main integrado, arreglando/verificando dependencias y agregando pruebas no triviales sobre el motor actual. No se modifica H-001..H-004 ni se altera la autoridad canónica.
