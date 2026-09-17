# SiMS-DeI/SICL — Arquitectura vigente 2.11 y matriz RFC-015–026

**Baseline de código:** `sims-dei-2.11-deploy-e2e`

**Core main:** `f2c4d205198e6050cdfd50e228e8ba21d3d4c79f`

**Frontend main:** `17422b2922918512dc5f93bb8371e57f0038d54a`

## 1. Propósito

Este documento complementa la arquitectura histórica v2.2. Su finalidad es registrar las capacidades verificadas después de RFC-015 y evitar que un documento histórico se interprete como el estado actual del producto.

## 2. Matriz de estado

| RFC | Capacidad | Estado verificado | Evidencia principal |
|---|---|---|---|
| RFC-015 | Frontend v2 funcional | Implementado en frontend main | `docs/RFC-015_FRONTEND_V2.md`, páginas y pruebas frontend |
| RFC-016 | Source HTTP | Implementado en Core main | rutas Source, contrato y pruebas |
| RFC-017 | Versionado del Core Contract | Implementado documentalmente en main | `docs/RFC-017_CORE_CONTRACT_VERSIONING.md` |
| RFC-018 | Proceso formal de RFC | Implementado documentalmente en main | `docs/RFC-018_RFC_PROCESS.md` |
| RFC-019 Core | Once escalas espaciales | Implementado en Core main | `SpatialScope`, tests multiescala y contrato |
| RFC-019 Frontend | Alias SICL localizados | Propuesto; no cambia el Core | catálogo i18n y documentación frontend |
| RFC-020 | Factibility Filtering | Implementado en Core main | `src/sicl/feasibility.py`, endpoints y tests |
| RFC-021 | Project Variables by Scale | Implementado en Core main | `ProjectVariable`, `SuggestedVariable`, tests |
| RFC-022 | Guided Interface | Implementado en frontend main | Guided Shell, catálogos, tour, Help y pruebas |
| RFC-023 | Proxy y contrato de conectividad | Implementación local verificada; E2E remoto bloqueado | `server/coreHttpClient.ts`, RFC-023/024 |
| RFC-024 | System Completion | Local/mock validado; remoto pendiente | Camino A mock, health, timeout y correlation IDs |
| RFC-025 | Corpus normativo peruano | Piloto implementado y trazable | RNE A.010, E.030, E.060, IS.010, EM.010 |
| RFC-026 | Design Knowledge Agent | Piloto funcional en main | catálogo, consulta multiescala y pruebas HTTP |

## 3. Simulaciones y análisis

El catálogo actual de simulación contiene `deterministic_basic_v1`, `sensitivity_linear_v1` y `monte_carlo_v1`. Monte Carlo admite `NORMAL`, `UNIFORM` y `TRIANGULAR`, conserva una semilla reproducible, registra inputs, outputs y hash canónico, y limita las iteraciones a 10.000. Las simulaciones son append-only y no crean `Recommendation`, `HumanReview` ni `Decision`.

La CLI admite la forma especializada `/SIMULATE MONTE_CARLO <alternative_id> <objective_id> <parameter_name> <distribution_json> [iterations]`. La distribución es JSON y debe declarar `type` y sus `parameters`. También existe `/SIMULATE RUN` para ejecutar un método registrado con inputs JSON.

El filtro RFC-020 produce `FEASIBLE`, `INFEASIBLE`, `INSUFFICIENT_DATA` o `UNKNOWN`. La frontera `feasible_pareto_front` retiene únicamente alternativas con estado `FEASIBLE`. Las restricciones duras pueden invalidar una alternativa; los datos insuficientes no se convierten en aprobación implícita.

## 4. Generación y diseño

Los métodos de generación registrados son `parametric_grid_v1`, `pattern_variation_v1`, `evolutionary_v1` y `llm_assisted_v1`. Los tres primeros producen candidatos `GeneratedAlternative` bajo métodos declarados. `evolutionary_v1` usa semilla y límites de población/generaciones. `llm_assisted_v1` conserva el contrato, pero permanece `DEFINED_NOT_CONFIGURED` o `LLM_NOT_CONFIGURED` cuando no existe un proveedor autorizado.

Una `GeneratedAlternative` no es una `Alternative` formal. La promoción requiere una acción explícita con actor y autoridad. Generación, simulación y Pareto no crean decisiones.

## 5. Variables, actores y tiempo

`ProjectVariable` requiere proyecto, clave normalizada, tipo, valor, actor y autoridad. `SuggestedVariable` es una sugerencia y no muta la ontología. `InstitutionalMemory` conserva conocimiento con estado y trazabilidad. `Actor` y `ActorPosition` registran participantes y posiciones. `TemporalCycle`, `ScenarioBranch` y `ScenarioEvolution` representan ciclos, ramas y transiciones explícitas.

## 6. Normativa y conocimiento de diseño

RFC-025 distingue ingesta documental, evidencia, interpretación normativa y decisión. Una fuente `NO_VERIFICADA` o modificada se presenta como referencia y exige revisión humana. RFC-026 separa fuentes de conocimiento, items y patrones de diseño. Alexander y Ching son referencias teóricas; el RNE es una fuente normativa cuyo estado debe revisarse. Ninguna heurística se convierte automáticamente en restricción.

## 7. Integración frontend

El frontend inicia en Guided Mode. El modo experto es configurable. Los catálogos, formularios y Command Bar ayudan a aprender SICL, pero el contrato canónico sigue siendo el comando SICL. El proxy server-side añade el token y clasifica `CORE_UNAVAILABLE`, `CORE_UNAUTHORIZED`, errores de ontología y errores de servicio.

## 8. Limitaciones honestas

La integración remota no está verificada hasta disponer de `SICL_CORE_URL`, `SICL_CORE_SERVICE_TOKEN`, volumen persistente y un Ollama accesible desde el Core. Revit y Archicad requieren sus hosts y SDKs nativos. La exportación BIM permanece condicionada a HumanReview. El alias localizado RFC-019 del frontend no sustituye la sintaxis canónica del Core.

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SICL Core repository"
[2]: https://github.com/YvanCastilloQuezada/sicl-web "SiMS-DeI web repository"
