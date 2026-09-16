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
| Objective | `objective_id`, `project_id`, `key`, `direction`, `value`, `version` |
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

## 6. Persistencia

SQLite es el adaptador aprobado del MVP. Se usan tablas de estado para Project y sus entidades, y una tabla `events` inmutable. Cada mutación escribe estado y evento atómicamente.

### HTTP v1 — Evaluation y Comparison

La superficie canónica expone `POST` y `GET` para `/v1/projects/{project_id}/evaluations` y `/v1/projects/{project_id}/comparisons`. Las respuestas usan el envelope v1 con `contract_version`, `status`, `code`, `message`, `project_id`, `observed_version` y `data`. Evaluation puede filtrarse por `alternative` y `objective`; Comparison recibe al menos dos alternativas. Recommendation continúa separada y Decision conserva autoridad humana.

## 7. Respuestas y errores

La CLI devuelve objetos `Response` con `status`, `code`, `message` y `data`. Códigos mínimos: `OK`, `INVALID_COMMAND`, `INVALID_ARGUMENT`, `PROJECT_NOT_FOUND`, `PROJECT_ALREADY_EXISTS`, `INVALID_STATE`, `PERSISTENCE_ERROR`, `UNKNOWN_COMMAND`.

## 8. Límites y exclusiones

Los agentes, Pareto, generación, debate y Site Intelligence son analíticos y no autoritativos. No se implementan Project DNA, Requirements formales, UI, BIM, GIS, Digital Twin, IoT ni decisiones automáticas.

**Este contrato no modifica SICL 0.6.**
