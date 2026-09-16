# RFC-011 — Institutional Memory

**Estado:** IMPLEMENTED en `rfc-011-institutional-memory`  
**Base:** RFC-010 Design Generation  
**Propósito:** conservar proyecciones versionadas de conocimiento derivado de proyectos cerrados sin reescribir hechos, decisiones ni la fuente canónica.

## Modelo

`InstitutionalMemory` es una proyección global, no una entidad canónica de `Project`. Cada registro contiene `memory_id`, `memory_type`, `scope`, `project_id_source`, `summary`, referencias a `evidence` y `decisions_referenced`, `state`, `confidence`, `anonymized`, `created_at` y `version`.

Los tipos permitidos son `DECISION_PATTERN`, `PREFERENCE_PATTERN`, `EVALUATION_PATTERN`, `GENERATION_PATTERN` y `LESSON_LEARNED`. Los estados son `ACTIVE`, `SUPERSEDED` y `REVOKED`; la confianza puede ser `HIGH`, `MEDIUM`, `LOW` o `UNKNOWN`.

## Autoridad y anonimización

La extracción exige `actor` y `authority` humanos, y solo acepta proyectos en estado `CLOSED`. La política predeterminada anonimiza identificadores directos y excluye datos sensibles. `project_id_source` permanece nulo salvo que la operación se implemente explícitamente con autorización de conservación del identificador.

La memoria no decide, no recomienda, no reescribe hechos o decisiones y no se aplica automáticamente. Su aplicación requiere una acción humana explícita con `actor`. La aplicación solo registra un evento de aplicación y no altera hechos, preferencias, alternativas, evaluaciones, recomendaciones ni decisiones del proyecto destino.

## CLI

- `/MEMORY LIST`
- `/MEMORY SHOW <memory_id>`
- `/MEMORY EXTRACT <project_id> <actor> <authority>`
- `/MEMORY REVOKE <memory_id> <actor> <authority>`
- `/MEMORY APPLY <memory_id> <project_id>` — usa el actor de la sesión CLI.
- `/MEMORY TYPES`

## HTTP v1

- `GET /v1/memory`
- `GET /v1/memory/{memory_id}`
- `GET /v1/memory/types`
- `POST /v1/memory/extract` con `{project_id, actor, authority}`
- `POST /v1/memory/{memory_id}/revoke` con `{actor, authority}`
- `POST /v1/projects/{project_id}/memory/apply` con `{memory_id, actor}`

## Persistencia e invariantes

La tabla `institutional_memory` es append-only y conserva una fila por versión. Las operaciones `UPDATE` y `DELETE` directas son rechazadas mediante triggers SQLite. Revocar crea una nueva versión `REVOKED`; una memoria revocada no puede aplicarse.

La extracción registra un evento auditable asociado al proyecto fuente sin modificar el estado de sus entidades. La aplicación registra `INSTITUTIONAL_MEMORY_APPLIED` en el proyecto destino. Ninguna de estas operaciones crea una `Decision`.
