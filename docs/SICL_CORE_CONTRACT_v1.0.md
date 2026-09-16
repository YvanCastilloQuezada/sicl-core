# SICL Core Contract v1.0

**Estado:** APPROVED — SiMS-DeI CANONICAL BASELINE (v2 repaired)

**Línea:** `sicl-core-v1.0` — independiente de SICL 0.6.

## 1. Alcance constitucional vigente

La base canónica implementa el MVP fundacional y las capacidades analíticas v2 siguientes:

- `Project`
- `Stage`
- `Objective`
- `Constraint` únicamente `HARD`/binaria
- `Role`
- `Fact`
- `Assumption`
- `Evidence` y `Source` como registros de procedencia explícita
- `Decision` como registro básico humano
- `Event` append-only estricto

Capacidades analíticas v2 reconocidas:

- `Alternative`, `Evaluation`, `Comparison` y `Recommendation`.
- `SiteObservation` con fuente y estado de conocimiento explícitos.
- Agentes expertos que producen únicamente `Evaluation`.
- Pareto, generación y debate como operaciones analíticas que no crean `Decision`.

Estas capacidades no adquieren autoridad decisoria por estar reconocidas en el contrato.

`Project DNA`, `Requirements` formales, UI, GIS, BIM, Digital Twin e IoT permanecen fuera de alcance. Las integraciones externas de datos solo pueden producir observaciones/facts con fuente, estado y trazabilidad explícitos.

## 2. Ontología mínima

`Fact` y `Assumption` son entidades distintas. Un hecho no se convierte automáticamente en supuesto ni un supuesto en hecho. La CLI manual registra cada uno con su propio tipo y payload.

`Decision` es un registro humano básico. El sistema no decide automáticamente.

## 3. Entidades

| Entidad | Atributos mínimos |
|---|---|
| Project | `project_id`, `name`, `stage`, `version`, `spatial_scope?`, `temporal_scope` |
| Stage | valor controlado: `DRAFT`, `ACTIVE`, `CLOSED` |
| Objective | `objective_id`, `project_id`, `key`, `direction`, `value`, `version`, `source_parent_objective_id?` |
| Constraint | `constraint_id`, `project_id`, `key`, `operator`, `value`, `unit`, `hard=true`, `version` |
| Role | `role_id`, `project_id`, `name`, `actor`, `version` |
| Fact | `fact_id`, `project_id`, `statement`, `source`, `version` |
| Assumption | `assumption_id`, `project_id`, `statement`, `basis`, `version` |
| Evidence | `evidence_id`, `project_id`, `source_id?`, `statement`, `evidence_type`, `captured_at`, `method_version`, `evidence_url?`, `evidence_hash?`, `state`, `version` |
| Source | `source_id`, `project_id`, `source_type`, `title`, `url?`, `version` |
| Decision | `decision_id`, `project_id`, `statement`, `actor`, `authority`, `version` |
| HumanReview | `review_id`, `project_id`, `statement`, `actor`, `authority`, `status`, `version` |
| SiteObservation | `location`, valores con unidad, `source`, `state`, `captured_at`, `method`, `evidence` |
| Alternative | `alternative_id`, `project_id`, `name`, `description`, `parameters`, `status`, `version`, `source` |
| Evaluation | `evaluation_id`, `alternative_id`, `objective_id`, `value`, `unit`, `confidence`, `source`, `version` |
| Comparison | `comparison_id`, `project_id`, `alternative_ids`, `evaluations`, `tradeoffs`, `version` |
| Simulation | `simulation_id`, `project_id`, `simulation_type`, `method`, `method_version`, `inputs`, `outputs`, `state`, `started_at`, `finished_at?`, `evidence_hash`, `version` |
| DesignPrinciple | `principle_id`, `name`, `category`, `description`, `applicable_scopes`, `source` |
| MultiobjectiveResult | `multiobjective_id`, `project_id`, `method`, `method_version`, `objectives`, `alternatives`, `pareto_front`, `dominated`, `incomplete`, `tradeoffs`, `state`, `inputs_hash`, `created_at`, `version` |
| PlanningInstrument | `instrument_id`, `project_id?`, `instrument_type`, `name`, `jurisdiction`, `authority?`, `approval_date?`, `validity_period?`, `scope_applicable`, `status`, `objectives`, `url?`, `summary?`, `source`, `version` |
| Regulation | `regulation_id`, `jurisdiction`, `authority`, `code`, `title`, `version`, `publication_date?`, `effective_date?`, `status`, `source_url?`, `source_type`, `evidence_hash?`, `scope_applicable`, `parent_regulation_id?`, `summary?`, `version_field` |
| NormativeInterpretation | `interpretation_id`, `regulation_id`, `article_reference`, `interpretation_text`, `applied_to_project_id?`, `interpreted_by`, `interpretation_date`, `confidence`, `state`, `disclaimer`, `version` |
| NormativeSnapshot | `snapshot_id`, `project_id`, `cut_date`, `jurisdiction`, `regulations_included`, `interpretations_included`, `state`, `reviewer?`, `created_at`, `version` |
| ScaleRelation | `relation_id`, `parent_project_id`, `child_project_id`, `relation_type`, `description?`, `created_by`, `created_at`, `version` |
| Event | `id`, `timestamp`, `project_id`, `type`, `payload`, `actor`, `source` |

### Multiscale Model

`SpatialScope` admite exactamente nueve valores: `pais`, `region`, `provincia_metropoli`, `ciudad_distrito`, `barrio_sector`, `parcela_sitio`, `edificio`, `espacio` y `objeto`. Sus etiquetas de presentación son, respectivamente, País, Región, Provincia / Metrópoli, Ciudad / Distrito, Barrio / Sector, Parcela / Sitio, Edificio, Espacio y Objeto.

`TemporalScope` admite `proyecto`, `corto_plazo`, `mediano_plazo`, `largo_plazo`, `escenario_2030`, `escenario_2040` y `escenario_2050`. El valor por defecto es `proyecto`.

`Project.spatial_scope` es opcional y por defecto es `null`. `null` significa que no se ha declarado una escala; no se infiere escala desde ningún dato del proyecto. `Project.temporal_scope` siempre contiene un valor válido. Los comandos `/PROJECT CREATE <id> <name> [spatial_scope] [temporal_scope]` y `/PROJECT SET SCOPE <spatial_scope> [temporal_scope]` validan estos valores; el segundo registra `SCOPE_CHANGED` como evento append-only.

## 4. Comandos aprobados

```text
/PROJECT CREATE <project_id> <name>
/PROJECT CREATE <project_id> <name> [spatial_scope] [temporal_scope]
/PROJECT OPEN <project_id>
/PROJECT SET SCOPE <spatial_scope> [temporal_scope]
/PROJECT IMPORT OBJECTIVE <source_project_id> <objective_id>
/PROJECT SHOW
/PROJECT LIST
/STAGE SET <stage>
/OBJECTIVE SET <key> <direction> <value>
/CONSTRAINT SET <key> <operator> <value> [unit]
/ROLE ADD <name> <actor>
/FACT SET <statement> [source]
/ASSUMPTION SET <statement> [basis]
/EVIDENCE ADD <evidence_id> <statement> <evidence_type> [source_id] [evidence_url]
/EVIDENCE LIST
/EVIDENCE SHOW <evidence_id>
/EVALUATE <alternative> <objective> <value> [unit] [confidence] [source]
/COMPARE <alternative> <alternative> [...]
/SIMULATE RUN <simulation_type> <method> [params]
/SIMULATE LIST
/SIMULATE SHOW <simulation_id>
/SIMULATE METHODS
/DESIGN PRINCIPLES
/DESIGN PRINCIPLE <principle_id>
/MULTIOBJECTIVE PARETO <obj_1> <obj_2> [...]
/MULTIOBJECTIVE TRADEOFFS <obj_1> <obj_2>
/MULTIOBJECTIVE LIST
/MULTIOBJECTIVE SHOW <multiobjective_id>
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
/SCALE PARENT <scope>
/SCALE CHILDREN <scope>
/SCALE RELATE <parent_project_id> <child_project_id> <relation_type> [description]
/SCALE RELATIONS <project_id>
/DECISION RECORD <statement> <actor> <authority>
/STATUS
/HISTORY
/HELP
/EXIT
```

## 5. Invariantes

1. Los identificadores de proyecto son únicos.
2. Solo existen etapas `DRAFT`, `ACTIVE` y `CLOSED`.
3. No se modifica un proyecto inexistente.
4. `Objective.direction` es obligatorio y solo admite `MAXIMIZE` o `MINIMIZE`.
5. Todo `Constraint` del MVP es `hard=true`; no se admite un nivel soft.
6. Fact y Assumption se almacenan separadamente.
7. Decision conserva actor y authority, requiere un `HumanReview` aprobado del mismo actor y authority, y nunca es generada por análisis automático.
8. Toda mutación exitosa produce exactamente un Event.
9. La tabla de eventos es append-only: no se actualiza ni elimina.
10. State y Event se persisten en una única transacción.
11. El cierre del proyecto impide nuevas mutaciones.
12. El historial devuelve eventos ordenados por inserción temporal.
13. Los estados de conocimiento admitidos son `UNKNOWN`, `CONFLICTING`, `INSUFFICIENT` y `OBSERVED`; ningún estado se sustituye silenciosamente por otro.
14. `SiteObservation` no crea restricciones normativas; la normativa requiere una fuente específica y autoridad humana.
15. `Evidence` solo registra declaraciones capturadas; no se convierte automáticamente en `Fact` o `Assumption`.
16. `Evidence` acepta únicamente los tipos y estados canónicos, calcula SHA-256 desde `statement` cuando falta hash y es append-only.
17. `Evaluation` requiere una Alternative y un Objective existentes; no crea Recommendation ni Decision.
18. `Comparison` requiere al menos dos Alternatives existentes y no crea Recommendation ni Decision.
19. `Simulation` es append-only, no crea Recommendation ni Decision y no convierte Assumption en Fact.
20. Los tipos admitidos son `DETERMINISTIC`, `MONTE_CARLO`, `SCENARIO` y `SENSITIVITY`; esta fase ejecuta únicamente métodos deterministas y de sensibilidad.
21. `DesignPrinciple` es un catálogo read-only con fuente declarada; no crea Decision, Recommendation ni Evaluation automática.
22. `MultiobjectiveResult` es descriptivo: no crea Recommendation, Decision, Alternative ni Evaluation.
23. Cada objetivo multiobjetivo requiere dirección explícita `MAXIMIZE` o `MINIMIZE`; la ausencia produce `OBJECTIVE_DIRECTION_REQUIRED`.
24. Si falta una evaluación requerida, la alternativa aparece en `incomplete` y el estado del resultado es `INSUFFICIENT`.
25. `MultiobjectiveResult` es append-only y conserva el hash SHA-256 de sus entradas.
26. `PlanningInstrument` no es normativa obligatoria, `DesignPrinciple`, `Reference` ni `Preference`.
27. Si falta una fuente verificable, `PlanningInstrument.status=UNKNOWN`.
28. Un `PlanningInstrument` no crea automáticamente Constraint, Recommendation, Preference ni Decision.
29. El vínculo a un Project es explícito, admite 0..N instrumentos y registra `PLANNING_INSTRUMENT_LINKED` con actor y timestamp.
30. Planning Instruments y sus vínculos son append-only; una modificación requiere una nueva versión.
31. `Regulation` no es `PlanningInstrument`, `DesignPrinciple`, `Reference` ni `Preference`.
32. Sin fuente oficial o sin vigencia verificada, una Regulation no se presenta como vigente y su estado inicial es `NO_VERIFICADA`.
33. `NormativeInterpretation` siempre contiene el disclaimer: `No constituye certificación legal ni reemplaza revisión profesional.`
34. Una Interpretation requiere revisión humana con actor y authority para estar en estado `REVIEWED`; no crea Constraint automáticamente.
35. Un `NormativeSnapshot` en estado `FROZEN` es inmutable; los cambios normativos requieren un snapshot nuevo.
36. Regulatory Intelligence no decide, recomienda ni certifica cumplimiento.
37. La jerarquía espacial solo es un catálogo consultable; no infiere relaciones territoriales.
38. `CONTAINS` requiere scopes espaciales explícitos y una relación ancestro→descendiente válida.
39. `ScaleRelation` es append-only; no se actualiza ni elimina y toda creación conserva actor, timestamp y evento.
40. La importación de un Objective requiere una relación `CONTAINS` explícita y conserva `source_parent_objective_id`; no copia autoridad ni crea decisiones.

## 6. Persistencia

SQLite es el adaptador aprobado del MVP. Se usan tablas de estado para Project y sus entidades, y una tabla `events` inmutable. Cada mutación escribe estado y evento atómicamente.

### HTTP v1 — Evaluation y Comparison

La superficie canónica expone `POST` y `GET` para `/v1/projects/{project_id}/evaluations` y `/v1/projects/{project_id}/comparisons`. Las respuestas usan el envelope v1 con `contract_version`, `status`, `code`, `message`, `project_id`, `observed_version` y `data`. Evaluation puede filtrarse por `alternative` y `objective`; Comparison recibe al menos dos alternativas. Recommendation continúa separada y Decision conserva autoridad humana.

### HTTP v1 — Design Intelligence

La superficie read-only expone `GET /v1/design/principles`, `GET /v1/design/principles?category=<CATEGORY>` y `GET /v1/design/principles/{principle_id}`. Solo se exponen principios con `source` declarada; no se cargan referentes reales en esta fase.

### HTTP v1 — Multiobjective

La superficie canónica expone `POST /v1/projects/{project_id}/multiobjective/pareto`, `POST /v1/projects/{project_id}/multiobjective/tradeoffs`, `GET /v1/projects/{project_id}/multiobjective` y `GET /v1/projects/{project_id}/multiobjective/{multiobjective_id}`. Todas las respuestas usan el envelope v1 y conservan `contract_version`, `project_id` y `observed_version`.

### HTTP v1 — Planning Instruments

La superficie canónica expone `GET /v1/planning/instruments`, `GET /v1/planning/instruments/{instrument_id}`, `GET /v1/planning/types`, `POST /v1/projects/{project_id}/planning/instruments` y `GET /v1/projects/{project_id}/planning/instruments`. La carga de instrumentos reales no pertenece a esta fase.

### HTTP v1 — Regulatory Corpus

La superficie canónica expone los diez endpoints de RFC-003 para Regulations, NormativeInterpretations y NormativeSnapshots. El corpus real, la interpretación jurídica y la certificación de vigencia están fuera de esta fase.

### HTTP v1 — Multiscale Relations

La superficie canónica expone `GET /v1/scales`, `GET /v1/scales/{scope}/parent`, `GET /v1/scales/{scope}/children`, `POST /v1/projects/{project_id}/scale-relations`, `GET /v1/projects/{project_id}/scale-relations` y `POST /v1/projects/{project_id}/import-objective`. Estas operaciones registran relaciones y trazabilidad explícitas; no cargan GIS ni realizan inferencia territorial.

## 7. Respuestas y errores

La CLI devuelve objetos `Response` con `status`, `code`, `message` y `data`. Códigos mínimos: `OK`, `INVALID_COMMAND`, `INVALID_ARGUMENT`, `PROJECT_NOT_FOUND`, `PROJECT_ALREADY_EXISTS`, `INVALID_STATE`, `PERSISTENCE_ERROR`, `UNKNOWN_COMMAND`.

## 8. Límites y exclusiones

Los agentes, Pareto, generación, debate y Site Intelligence son analíticos y no autoritativos. No se implementan Project DNA, Requirements formales, UI, BIM, GIS, Digital Twin, IoT ni decisiones automáticas.

**Este contrato no modifica SICL 0.6.**
