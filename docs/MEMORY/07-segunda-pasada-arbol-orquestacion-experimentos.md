# Segunda pasada — ramas divergentes de ÁRBOL Vivo, orquestación y experimentos

**Fecha:** 2026-10-21. **Método:** lectura estática de archivos concretos de ramas divergentes y comparación previa contra Web main. No se ejecutaron tests.

## 1. `feat/arbol-vivo-precedencias-seguras-20261010`

- Cabeza: `34e35e84656e75b301c44ac21cf79dd84430f1f0`; comparación: 741 commits exclusivos y 59 por detrás de Web main.
- `tools/maqueta-viva/ARBOL-GEMELO-DIGITAL.md` define ÁRBOL Vivo como columna vertebral documental F1–F10 y ÁRBOL Gemelo Digital como pantalla de observación con tres representaciones de la misma fuente: árbol, cerebro relacional y proyección 3D conceptual.
- El mismo documento declara `verification=UNKNOWN`, `simulation=NOT_EXECUTED`, que la vista 3D no es geometría AGK y que el selector de versiones no restaura ni promociona el estado canónico.
- `docs/arki-master-map/AV_UI_001_ARBOL_VIVO_PREPARATION.md` declara `PREPARATION_ONLY / NOT_IMPLEMENTED / NOT_CANONICAL / NOT_AUTHORIZED_FOR_MERGE`. Describe la pantalla deseada: izquierda memoria/hechos acreditados, centro árbol F1–F10, derecha propuestas/pruebas/métricas/decisiones. También describe `arkiConstructionWaves()`, `arkiDependencyTopology()`, `arkiDecisionDocket()` y `buildUnifiedTraceGraph()` como funciones inspeccionadas estáticamente; no afirma que se haya validado E3/navegador.
- `tools/maqueta-viva/ARKI-LIVING-MEMORY-UPDATE-PROTOCOL.md` dice explícitamente que el módulo experimental no tiene webhooks, conexión CI, ingesta automática, persistencia durable, verificación independiente de firmas/SHA, actualización automática HTML ni integración con planificador. `previousHash` no prueba inmutabilidad/autenticidad y `VERIFIED` es un estado declarado por el emisor, no una verificación independiente.

**Conclusión:** la rama concentra mucho trabajo documental y funcional, pero sus propios documentos separan prototipo, observación y ejecución. No se debe integrar como una unidad de 741 commits; extraer capacidades concretas solo tras revisar dependencias, tests y estados de aprobación.

## 2. `feat/arbol-vivo-functional-repair-20261014`

- Cabeza: `cad38bc314f9e8fa10d6ae542be888879cec1644`; comparación: 851 commits exclusivos y 59 por detrás de Web main.
- `ARKI_THREE_LIVE_SYSTEMS_RECONCILIATION_20261014.md` declara inspección estática, sin pruebas de runtime ni promoción canónica.
- Dictamen del documento: reutilizar antes de desarrollar otro Árbol, Gemelo, Mapa, ADN u orquestador.
- Registra una divergencia concreta: `twinThreeAlternatives()` aparece en documentación, pero no está presente en la plantilla HTML inspeccionada en la rama de autonomía. El propio documento exige resolverlo por historia Git y pruebas, no suponer que existe.
- Define roles separados: Mapa Maestro (estado/documentos), Árbol Vivo (fases/dependencias/bandeja), Gemelo (escenarios/snapshots aislados), ADN-MC (déficits y evaluación), orquestador (planificación) y ACE88/Core (promoción autorizada).

**Conclusión:** la rama de reparación no prueba que las capacidades descritas estén integradas. Su hallazgo más importante es la divergencia entre documentos y plantilla real.

## 3. `feat/arki-autonomy-orchestrator-20261013`

- Cabeza: `1a505fce87f57b7faf040d382c8bb6821bc1bedf`; comparación: 915 commits exclusivos y 59 por detrás de Web main.
- El archivo `arki-autonomy-orchestrator.cjs` se autodefine como planificación autónoma acotada: nunca ejecuta código ni promueve estado canónico.
- Valida que la evidencia de una pieza incluya `verified=true`, commit SHA de 40 caracteres, `testReceipt` y fuente. Valida fase F1–F10, conflicto de fase y estado FROZEN.
- Resultado: acción de revisión de evidencia/autoridad o candidato a experimento aislado; `execution=NOT_EXECUTED`, `canonicalMutation=false`, `ownerGate=REQUIRED_FOR_PROMOTION`, `memoryWrite=NOT_PERFORMED`.

**Conclusión:** el módulo que se leyó es un planificador/gate, no un ejecutor ni un escritor de MEMORY. La enorme divergencia requiere analizar commits exclusivos y pruebas antes de rescatarlo.

## 4. `feat/arki-operational-vitality-mo05-20261015`

- Cabeza: `61a2dba2e5a73a43470a66222a7fbf791c8aaa8b`; comparación: 958 commits exclusivos y 59 por detrás de Web main.
- `arki-adn-mejora-continua.cjs` se declara motor experimental puro y determinista A0/A1/A2. No escribe Core/AGK, no ejecuta un scheduler, no edita código, no modifica FROZEN y no promueve estado canónico.
- Requiere observaciones con esquema, commit fuente, ID y métricas tipadas. Si una medición no está verificada, el déficit queda `UNKNOWN`; candidatos son objetivos hipotéticos.

**Conclusión:** la vitalidad detecta/evalúa déficits y genera candidatos, pero no prueba aprendizaje ni mejora real sin ejecutar experimentos y verificar recibos.

## 5. `experiment/arki-ideas-mapa-vivo-20261015`

- Cabeza: `c3b4f6a911d5527e2ce42ceb1c912521dbffe724`; comparación: 62 commits exclusivos, 57 por detrás; 46 rutas en diff.
- `experiments/arki-ideas/EXTRACTION_LEDGER.md` declara `SOURCE_COPIED / TESTS_NOT_EXECUTED / NO_CANONICAL_PROMOTION`.
- REC-003 copia el contrato de tres alternativas A/B/C para distinguir evidencia hipotética de medida; explícitamente no simula AGK.
- REC-006 copia un pulso HTTP read-only que no certifica arquitectura/Core/D2/AGK.
- Las pruebas concretas de REC-003 y REC-006 están escritas como comandos pendientes en el ledger.

**Conclusión:** es una bolsa de extracción experimental con procedencia y límites, no una integración productiva. No borrar la fuente ni interpretar una copia como absorción.

## 6. Recomendación transversal

1. No fusionar ramas completas con cientos de commits exclusivos.
2. Extraer una lista de capacidades/archivos por contrato y SHA, no por nombre de rama.
3. Comparar documentación, código, tests y resultados: si discrepan, registrar el conflicto como `CONFLICTED/UNKNOWN`, no elegir la versión más optimista.
4. Mantener separadas planificación, observación, experimento, aprendizaje verificado y promoción canónica.
5. Para MEMORY, enlazar estas fuentes y sus SHA como antecedentes; no incorporar el prototipo experimental como fuente de verdad hasta definir persistencia, autenticidad, reconciliación y recuperación E2E.
