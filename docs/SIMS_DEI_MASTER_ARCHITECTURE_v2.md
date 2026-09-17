# SiMS-DeI 2.0 — Master Architecture

**Sistema:** Sistema de Inteligencia de Diseño Espacial Multiescala (SiMS-DeI)  
**Lenguaje formal:** SICL — Spatial Intelligence Command Language  
**Baseline:** `sicl-core@b377aa65380ea2cc1a7fc77a9cd63830197f5371`  
**Tag:** `sicl-2.0-multiscale-complete`  
**Rama de origen:** `main`, consolidada desde `integration-v2`  
**Fecha:** 15 de septiembre de 2026  
**Estado:** Baseline técnico 2.0 — RFC-001 a RFC-009 implementados

> Este documento sintetiza la arquitectura implementada en el Core Python de SiMS-DeI 2.0. No sustituye al Core Contract ni autoriza capacidades que estén marcadas como futuras, parciales o fuera de alcance.

## 1. Executive Summary

SiMS-DeI 2.0 es un sistema de inteligencia para organizar, documentar y analizar decisiones de diseño espacial en múltiples escalas. Su función no es reemplazar al arquitecto ni decidir por él. El sistema conserva el contexto del proyecto, distingue hechos de supuestos, registra evidencia y fuentes, ejecuta análisis reproducibles y presenta resultados descriptivos para revisión humana.

SICL proporciona el lenguaje formal de interacción con el Core. La arquitectura combina una capa de dominio Python, persistencia SQLite, un intérprete CLI, una API REST canónica `/v1/...` y eventos append-only. Las capacidades analíticas —agentes, simulación, comparación, Pareto, debate y Site Intelligence— producen observaciones, evaluaciones o resultados descriptivos; ninguna crea una `Decision` automáticamente.

El baseline 2.0 contiene nueve RFC implementados y **146 tests passing**. La integración se publicó en `main` y se etiquetó como `sicl-2.0-multiscale-complete`.

## 2. Definición de SiMS-DeI

SiMS-DeI es el sistema superior de inteligencia de diseño espacial multiescala. Puede operar sobre un proyecto arquitectónico, una parcela, un edificio, una ciudad, una región o una escala nacional, siempre que la escala se declare explícitamente y que los datos utilizados mantengan su procedencia y estado epistemológico.

El sistema separa cinco funciones: **registrar**, **relacionar**, **analizar**, **revisar** y **decidir**. Registrar conserva el estado y los eventos. Relacionar conecta proyectos y entidades mediante vínculos explícitos. Analizar calcula evaluaciones o resultados. Revisar exige autoridad humana. Decidir registra una decisión humana con actor y autoridad.

## 3. Rol de SICL

SICL es el lenguaje formal y operativo de SiMS-DeI. Sus comandos expresan operaciones sobre entidades del dominio, por ejemplo `/PROJECT CREATE`, `/FACT SET`, `/EVALUATE`, `/SIMULATE RUN` y `/DECISION RECORD`.

SICL no es un agente autónomo ni una autoridad normativa. Cada comando se interpreta contra un repositorio SQLite y, cuando muta el estado, genera un evento trazable. Los comandos analíticos pueden producir resultados, pero no tienen permiso ontológico para crear decisiones humanas.

## 4. Arquitectura general

```text
Usuario / Arquitecto
        |
        | SICL CLI o HTTP /v1
        v
FastAPI API Layer ---- envelope canónico, autenticación server-side
        |
        v
SICL Interpreter ---- validaciones, invariantes, eventos
        |
        +--> Domain Model ---- Project y entidades canónicas
        +--> Analytical Modules ---- agents, simulation, optimization, design
        +--> SQLiteRepository ---- state tables + append-only event log
        |
        v
Snapshots, history, reports y resultados descriptivos
```

### 4.1 Persistencia

SQLite es el adaptador aprobado del baseline. Las tablas de estado almacenan proyectos y entidades. La tabla `events` es append-only y conserva `id`, `timestamp`, `project_id`, `type`, `payload`, `actor` y `source`. Las entidades históricas relevantes —Evidence, Simulation, MultiobjectiveResult, PlanningInstrument, Regulation, NormativeInterpretation, NormativeSnapshot y ScaleRelation— poseen controles append-only propios.

### 4.2 API y seguridad

La API canónica se sirve bajo `/v1`. Las rutas pueden exigir `SICL_CORE_SERVICE_TOKEN` mediante el header `Authorization: Bearer ...`; el token pertenece exclusivamente al servidor y no forma parte de los payloads de navegador. Las respuestas canónicas utilizan un envelope con `contract_version`, `status`, `code`, `message`, `project_id`, `observed_version` y `data`.

## 5. Entidades canónicas por RFC

| RFC | Entidades o capacidades | Estado en 2.0 |
|---|---|---|
| RFC-001 | `SpatialScope`, `TemporalScope`, scopes de `Project` | Implementado |
| RFC-002 | `Source`, `Evidence`, tipos y estados de evidencia; HTTP Evidence | Implementado |
| RFC-003 | `Regulation`, `NormativeInterpretation`, `NormativeSnapshot` | Implementado como estructura; corpus real fuera de alcance |
| RFC-004 | `DesignPrinciple` read-only | Implementado como catálogo; sin referentes reales cargados |
| RFC-005 | `Evaluation`, `Comparison` y endpoints HTTP | Implementado |
| RFC-006 | `Simulation` y métodos deterministas/sensibilidad | Implementado; ejecución limitada a métodos declarados |
| RFC-007 | `MultiobjectiveResult`, Pareto y trade-offs | Implementado |
| RFC-008 | `PlanningInstrument` y vínculos con proyectos | Implementado como estructura; catálogo real vacío |
| RFC-009 | `ScaleRelation`, jerarquía multiescala e importación trazable de objetivos | Implementado |

Además, el Core conserva las entidades base `Project`, `Stage`, `Objective`, `Constraint`, `Role`, `Fact`, `Assumption`, `Preference`, `HumanReview`, `Decision`, `Alternative`, `Recommendation` y `Event`.

## 6. Mapa de las nueve escalas

| Orden | Scope | Interpretación |
|---:|---|---|
| 1 | `pais` | País |
| 2 | `region` | Región |
| 3 | `provincia_metropoli` | Provincia o metrópoli |
| 4 | `ciudad_distrito` | Ciudad o distrito |
| 5 | `barrio_sector` | Barrio o sector |
| 6 | `parcela_sitio` | Parcela o sitio |
| 7 | `edificio` | Edificio |
| 8 | `espacio` | Espacio |
| 9 | `objeto` | Objeto |

La escala espacial de un proyecto es opcional y nunca se infiere. La relación `CONTAINS` requiere scopes explícitos y una relación ancestro→descendiente válida. `OVERLAPS`, `INFLUENCES` y `DEPENDS_ON` son relaciones declaradas; no se generan automáticamente.

## 7. Superficie HTTP `/v1`

### 7.1 Salud, catálogos y diseño

- `GET /v1/health`
- `GET /v1/operations-research/methods`
- `GET /v1/simulations/methods`
- `GET /v1/design/principles`
- `GET /v1/design/principles/{principle_id}`
- `GET /v1/scales`
- `GET /v1/scales/{scope}/parent`
- `GET /v1/scales/{scope}/children`

### 7.2 Proyectos, snapshots, comandos y auditoría

- `GET /v1/projects`
- `POST /v1/projects`
- `GET /v1/projects/{project_id}/snapshot`
- `GET /v1/projects/{project_id}/history`
- `POST /v1/projects/{project_id}/commands`
- `POST /v1/projects/{project_id}/preferences`
- `POST /v1/projects/{project_id}/human-reviews`
- `POST /v1/projects/{project_id}/decisions`
- `POST /v1/projects/{project_id}/recommendations`
- `GET /v1/projects/{project_id}/council`

### 7.3 Site Intelligence y agentes

- `POST /v1/projects/{project_id}/site-observations`
- `POST /v1/projects/{project_id}/agents/{agent}/evaluations`
- `POST /v1/projects/{project_id}/pareto`
- `POST /v1/projects/{project_id}/debate`

### 7.4 Evidence, Evaluation y Comparison

- `POST /v1/projects/{project_id}/evidence`
- `GET /v1/projects/{project_id}/evidence`
- `GET /v1/projects/{project_id}/evidence/{evidence_id}`
- `POST /v1/projects/{project_id}/evaluations`
- `GET /v1/projects/{project_id}/evaluations`
- `POST /v1/projects/{project_id}/comparisons`
- `GET /v1/projects/{project_id}/comparisons`

### 7.5 Simulation y Multiobjective

- `POST /v1/projects/{project_id}/simulations`
- `GET /v1/projects/{project_id}/simulations`
- `GET /v1/projects/{project_id}/simulations/{simulation_id}`
- `POST /v1/projects/{project_id}/multiobjective/pareto`
- `POST /v1/projects/{project_id}/multiobjective/tradeoffs`
- `GET /v1/projects/{project_id}/multiobjective`
- `GET /v1/projects/{project_id}/multiobjective/{multiobjective_id}`

### 7.6 Planning Instruments y relaciones multiescala

- `GET /v1/planning/instruments`
- `GET /v1/planning/instruments/{instrument_id}`
- `GET /v1/planning/types`
- `POST /v1/projects/{project_id}/planning/instruments`
- `GET /v1/projects/{project_id}/planning/instruments`
- `POST /v1/projects/{project_id}/scale-relations`
- `GET /v1/projects/{project_id}/scale-relations`
- `POST /v1/projects/{project_id}/import-objective`

### 7.7 Regulatory Corpus

- `POST /v1/regulations`
- `GET /v1/regulations`
- `GET /v1/regulations/{regulation_id}`
- `POST /v1/regulations/{regulation_id}/status`
- `POST /v1/regulations/{regulation_id}/interpretations`
- `GET /v1/regulations/{regulation_id}/interpretations`
- `POST /v1/interpretations/{interpretation_id}/review`
- `POST /v1/projects/{project_id}/normative-snapshots`
- `GET /v1/projects/{project_id}/normative-snapshots`
- `POST /v1/normative-snapshots/{snapshot_id}/freeze`

## 8. Comandos CLI

### 8.1 Proyecto y estado

```text
/PROJECT CREATE <project_id> <name> [spatial_scope] [temporal_scope]
/PROJECT OPEN <project_id>
/PROJECT SET SCOPE <spatial_scope> [temporal_scope]
/PROJECT IMPORT OBJECTIVE <source_project_id> <objective_id>
/PROJECT SHOW
/PROJECT LIST
/STAGE SET <stage>
/STATUS
/HISTORY
/HELP
/EXIT
```

### 8.2 Conocimiento y decisión

```text
/OBJECTIVE SET <key> <direction> <value>
/CONSTRAINT SET <key> <operator> <value> [unit]
/ROLE ADD <name> <actor>
/FACT SET <statement> [source]
/ASSUMPTION SET <statement> [basis]
/EVIDENCE ADD <evidence_id> <statement> <evidence_type> [source_id] [evidence_url]
/EVIDENCE LIST
/EVIDENCE SHOW <evidence_id>
/HUMAN REVIEW <review> <actor> <authority> [reason]
/DECISION RECORD <statement> <actor> <authority>
```

### 8.3 Análisis

```text
/ALTERNATIVE CREATE <name> [description]
/ALTERNATIVE SET <alternative> <key> <value>
/ALTERNATIVE LIST
/EVALUATE <alternative> <objective> <value> [unit] [confidence] [source]
/COMPARE <alternative> <alternative> [...]
/RECOMMEND
/AGENT RUN <agent> <alternative>
/DEBATE <alternative>
/SITE INTELLIGENCE <location>
/GENERATE <alternative> <objective_1> <objective_2>
/PARETO <objective_1> <objective_2>
/TRADEOFF_MATRIX <objective_1> <objective_2>
/MULTIOBJECTIVE PARETO <objective_1> <objective_2> [...]
/MULTIOBJECTIVE TRADEOFFS <objective_1> <objective_2>
/MULTIOBJECTIVE LIST
/MULTIOBJECTIVE SHOW <multiobjective_id>
```

### 8.4 Simulation, diseño, planificación y regulación

```text
/SIMULATE RUN <simulation_type> <method> [params]
/SIMULATE LIST
/SIMULATE SHOW <simulation_id>
/SIMULATE METHODS
/DESIGN PRINCIPLES
/DESIGN PRINCIPLE <principle_id>
/SCALE PARENT <scope>
/SCALE CHILDREN <scope>
/SCALE RELATE <parent_project_id> <child_project_id> <relation_type> [description]
/SCALE RELATIONS <project_id>
/PLANNING ADD <instrument_id> <instrument_type> <name> [jurisdiction] [url]
/PLANNING LIST
/PLANNING SHOW <instrument_id>
/PLANNING TYPES
/REGULATION ADD <regulation_id> <code> <title> [jurisdiction] [source_url]
/REGULATION LIST
/REGULATION SHOW <regulation_id>
/REGULATION STATUS <regulation_id> <status>
/INTERPRET ADD <interpretation_id> <regulation_id> <article_reference> <interpretation_text>
/INTERPRET LIST [regulation_id]
/INTERPRET REVIEW <interpretation_id> <actor> <authority>
/SNAPSHOT CREATE <snapshot_id> <project_id> <cut_date>
/SNAPSHOT LIST <project_id>
/SNAPSHOT FREEZE <snapshot_id> <reviewer>
```

## 9. Invariantes constitucionales

1. `Fact` y `Assumption` son entidades epistemológicamente distintas.
2. `UNKNOWN`, `CONFLICTING`, `INSUFFICIENT` y `OBSERVED` no se sustituyen silenciosamente.
3. Una `Recommendation` nunca es una `Decision`.
4. Una `Recommendation` no puede crear una `Decision`.
5. Una `Decision` requiere `HumanReview` aprobado, actor y authority.
6. El sistema nunca decide automáticamente.
7. Toda mutación exitosa produce un evento auditable.
8. Los eventos son append-only y conservan actor y source.
9. State y Event se escriben en una transacción.
10. Un proyecto `CLOSED` no acepta mutaciones.
11. `Constraint` es `HARD` en el alcance vigente.
12. `Evidence` no se transforma automáticamente en `Fact` o `Assumption`.
13. Los agentes solo producen `Evaluation`.
14. Pareto, Simulation, Comparison, Debate y Multiobjective son descriptivos o analíticos.
15. `SiteObservation` no infiere zonificación ni obligación normativa.
16. Toda interpretación normativa incluye disclaimer y requiere revisión profesional humana.
17. `NormativeSnapshot` congelado es inmutable.
18. Las relaciones multiescala se registran explícitamente; no se infieren.
19. Importar un objetivo conserva `source_parent_objective_id` y no transfiere autoridad.
20. Los secretos de servicio son server-side y no se exponen al navegador.

## 10. Estado por capacidad

| Capacidad | Estado | Observación |
|---|---|---|
| Core de dominio y SQLite | Implementado | 146 tests passing |
| CLI SICL | Implementado | Comandos documentados en esta arquitectura |
| HTTP `/v1` | Implementado | Envelope canónico y rutas RFC |
| Project scopes | Implementado | Nueve escalas y siete scopes temporales |
| Evidence / Source | Implementado | Procedencia y append-only |
| Regulatory Corpus | Estructura implementada | No contiene corpus jurídico real |
| Design Intelligence | Implementado read-only | Catálogo declarado; sin referentes reales |
| Evaluation / Comparison | Implementado | Requiere entidades y objetivos existentes |
| Simulation | Implementado | No crea decisiones |
| Multiobjective / Pareto | Implementado | Resultado descriptivo y append-only |
| Planning Instruments | Estructura implementada | Catálogo real vacío |
| ScaleRelation | Implementado | Relaciones explícitas, sin GIS |
| Site Intelligence | Implementado | Observación con fuente/estado; no normativa |
| Agentes expertos | Implementado | Solo evaluaciones |
| HumanReview | Implementado | Precondición para Decision |
| Decision | Implementado | Registro humano explícito |
| SiMS-DeI web frontend | Separado | No forma parte de este commit del Core |

## 11. Qué NO está implementado

No forman parte del baseline 2.0: un corpus normativo real o certificación legal; revisión jurídica externa; GIS o límites territoriales; geocodificación; BIM; Digital Twin; IoT; Project DNA; Requirements formales; agentes autónomos con autoridad; propagación automática de objetivos, facts, constraints o decisiones; Monte Carlo no declarado por el contrato operativo; sincronización con fuentes externas en tiempo real; generación automática de decisiones; autenticación de usuarios de negocio; y el documento maestro anterior a esta versión.

La implementación de una capacidad futura requiere su RFC, contrato, tests y decisión de gobernanza correspondiente.

## 12. Roadmap 2.1 — RFC-010 a RFC-013

El siguiente roadmap es una propuesta de trabajo, no una autorización automática de implementación.

| RFC futura | Tema propuesto | Resultado esperado |
|---|---|---|
| RFC-010 | Identity, roles and authority model | Separar actor técnico, usuario autenticado, rol profesional, autoridad y alcance de firma; sin debilitar HumanReview |
| RFC-011 | Evidence provenance and external source synchronization | Versionado de capturas, refresh controlado, hashes, expiración y reconciliación de fuentes externas |
| RFC-012 | Cross-scale propagation and consistency | Reglas explícitas y revisables para propagación de objetivos/restricciones entre proyectos relacionados; nunca inferencia silenciosa |
| RFC-013 | Production operations and release governance | Migraciones, backups, observabilidad, despliegue, política de secretos, retención de eventos y release gates |

Cada RFC debe definir alcance, entidades, endpoints, invariantes, pruebas y límites antes de tocar `main`.

## 13. Referencias

- [RFC-001 — Multiscale Model](RFC-001_MULTISCALE_MODEL.md)
- [RFC-002 — Evidence HTTP](RFC-002_EVIDENCE_HTTP.md)
- [RFC-003 — Regulatory Corpus](RFC-003_REGULATORY_CORPUS.md)
- [RFC-004 — Design Intelligence Scope](RFC-004_DESIGN_INTELLIGENCE_SCOPE.md)
- [RFC-005 — Evaluation / Comparison HTTP](RFC-005_EVALUATION_COMPARISON_HTTP.md)
- [RFC-006 — Simulation Contract](RFC-006_SIMULATION_CONTRACT.md)
- [RFC-007 — Multiobjective Contract](RFC-007_MULTIOBJECTIVE_CONTRACT.md)
- [RFC-008 — Planning Instruments](RFC-008_PLANNING_INSTRUMENTS.md)
- [RFC-009 — Multiscale Relations](RFC-009_MULTISCALE_RELATIONS.md)
- [SICL Core Contract v1.0](SICL_CORE_CONTRACT_v1.0.md)

## 14. Firma del baseline

```text
SYSTEM: SiMS-DeI
LANGUAGE: SICL
RELEASE: 2.0
TAG: sicl-2.0-multiscale-complete
COMMIT: b377aa65380ea2cc1a7fc77a9cd63830197f5371
RFC_SCOPE: RFC-001..RFC-009
TESTS: 146 passing
MAIN: published
DEPLOYMENT: not performed by this document
```

**Firma arquitectónica del baseline:** SiMS-DeI 2.0 queda descrito como un Core analítico, trazable y multiescala, con autoridad humana explícita y sin decisión automática.


## Estado vigente de capacidades — actualización 2026-09-16

> Esta sección supersede las afirmaciones históricas de este documento que indiquen que GIS, BIM o el Copiloto local están fuera de alcance. El baseline vigente incluye RFC-027, RFC-028 y RFC-029.

El Core actual incluye importación IFC física de solo lectura, snapshots BIM persistentes, BIMChangeSet en modo PREVIEW, detección de conflictos BIM, contratos de exportación que exigen HumanReview, persistencia SQLite de ParcelSnapshot, catálogo GIS por jurisdicción, caducidad y ParcelBoundaryConflict, consulta OGC API Features y traducción Ollama a comandos SICL en modo PREVIEW_ONLY.

Estas capacidades no otorgan autoridad automática. El Copiloto no ejecuta comandos ni crea decisiones. Los adaptadores Revit y Archicad requieren sus hosts y SDKs nativos. La exportación BIM queda pendiente de ejecución externa después de una HumanReview aprobada. Las fuentes catastrales requieren registro explícito, licencia y validación humana.

La referencia operativa es [`PRODUCTION_CORE_DEPLOYMENT_MANUAL.md`](PRODUCTION_CORE_DEPLOYMENT_MANUAL.md). La suite E2E se ejecuta con `PYTHONPATH=.:src pytest -q tests/test_e2e_ollama_sicl.py -ra`.
