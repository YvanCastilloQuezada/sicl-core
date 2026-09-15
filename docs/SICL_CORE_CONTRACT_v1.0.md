# SICL Core Contract v1.0

**Estado:** APPROVED FOR IMPLEMENTATION

**Línea:** `sicl-core-v1.0` — independiente de SICL 0.6.

## 1. Alcance MVP aprobado

El MVP implementa exclusivamente:

- `Project`
- `Stage`
- `Objective`
- `Constraint` únicamente `HARD`/binaria
- `Role`
- `Fact`
- `Assumption`
- `Decision` como registro básico humano
- `Event` append-only estricto

`Alternative`, `Evaluation`, `Comparison` y `Recommendation` pertenecen a SICL v1.1. `Project DNA`, `Agents`, `Requirements` formales, optimización, UI, GIS, BIM, clima y APIs externas quedan fuera del MVP.

## 2. Ontología mínima

`Fact` y `Assumption` son entidades distintas. Un hecho no se convierte automáticamente en supuesto ni un supuesto en hecho. La CLI manual registra cada uno con su propio tipo y payload.

`Decision` es un registro humano básico. El sistema no decide automáticamente.

## 3. Entidades

| Entidad | Atributos mínimos |
|---|---|
| Project | `project_id`, `name`, `stage`, `version` |
| Stage | valor controlado: `DRAFT`, `ACTIVE`, `CLOSED` |
| Objective | `objective_id`, `project_id`, `key`, `direction`, `value`, `version` |
| Constraint | `constraint_id`, `project_id`, `key`, `operator`, `value`, `unit`, `hard=true`, `version` |
| Role | `role_id`, `project_id`, `name`, `actor`, `version` |
| Fact | `fact_id`, `project_id`, `statement`, `source`, `version` |
| Assumption | `assumption_id`, `project_id`, `statement`, `basis`, `version` |
| Decision | `decision_id`, `project_id`, `statement`, `actor`, `authority`, `version` |
| Event | `id`, `timestamp`, `project_id`, `type`, `payload`, `actor`, `source` |

## 4. Comandos aprobados

```text
/PROJECT CREATE <project_id> <name>
/PROJECT OPEN <project_id>
/PROJECT SHOW
/PROJECT LIST
/STAGE SET <stage>
/OBJECTIVE SET <key> <direction> <value>
/CONSTRAINT SET <key> <operator> <value> [unit]
/ROLE ADD <name> <actor>
/FACT SET <statement> [source]
/ASSUMPTION SET <statement> [basis]
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
7. Decision conserva actor y authority y no es generada por análisis automático.
8. Toda mutación exitosa produce exactamente un Event.
9. La tabla de eventos es append-only: no se actualiza ni elimina.
10. State y Event se persisten en una única transacción.
11. El cierre del proyecto impide nuevas mutaciones.
12. El historial devuelve eventos ordenados por inserción temporal.

## 6. Persistencia

SQLite es el adaptador aprobado del MVP. Se usan tablas de estado para Project y sus entidades, y una tabla `events` inmutable. Cada mutación escribe estado y evento atómicamente.

## 7. Respuestas y errores

La CLI devuelve objetos `Response` con `status`, `code`, `message` y `data`. Códigos mínimos: `OK`, `INVALID_COMMAND`, `INVALID_ARGUMENT`, `PROJECT_NOT_FOUND`, `PROJECT_ALREADY_EXISTS`, `INVALID_STATE`, `PERSISTENCE_ERROR`, `UNKNOWN_COMMAND`.

## 8. Exclusiones

No se implementan Alternative, Evaluation, Comparison, Recommendation, Project DNA, Agents, Requirements formales, Optimization, Site Intelligence, Generative, Feasibility avanzada, UI ni integraciones externas.

**Este contrato no modifica SICL 0.6.**
