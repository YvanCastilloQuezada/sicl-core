# RFC-012 — Multi-Actor Model

**Estado:** IMPLEMENTED en `rfc-012-multi-actor-model`  
**Base:** RFC-011 Institutional Memory  
**Propósito:** registrar explícitamente actores, autoridad y posiciones divergentes en decisiones espaciales.

## Entidades

`Actor` pertenece a un proyecto y contiene `actor_id`, `project_id`, `role`, `name`, `authority_level`, `interests`, `constraints`, `state`, `created_at` y `version`.

`ActorPosition` contiene `position_id`, `project_id`, `actor_id`, `subject_type`, `subject_id`, `stance`, `reason`, `conditions`, `created_at` y `version`.

Roles: `CLIENT`, `ARCHITECT`, `ENGINEER`, `REGULATOR`, `COMMUNITY`, `DEVELOPER`, `OTHER`. Niveles: `ADVISORY`, `CONTRIBUTORY`, `DECISIONAL`, `VETO`. Estados: `ACTIVE`, `INACTIVE`. Posiciones: `SUPPORT`, `OPPOSE`, `NEUTRAL`, `CONDITIONAL`.

## Autoridad

Solo un actor activo con autoridad `DECISIONAL` puede registrar una `Decision`, y la operación continúa requiriendo `HumanReview` aprobado, actor y authority. Un actor `VETO` puede bloquear una Decision cuando registra una posición `OPPOSE` o `CONDITIONAL` sobre un `DECISION_PROPOSED`. Los actores `ADVISORY` y `CONTRIBUTORY` no deciden.

Las posiciones no reemplazan `HumanReview` ni `Decision`. El desacuerdo se conserva como dato; SICL no lo resuelve automáticamente.

## CLI

- `/ACTOR ADD <actor_id> <role> <name> <authority_level>`
- `/ACTOR LIST`
- `/ACTOR SHOW <actor_id>`
- `/POSITION ADD <actor_id> <subject_type> <subject_id> <stance> <reason>`
- `/POSITION LIST [subject_id]`

## HTTP v1

- `POST /v1/projects/{project_id}/actors`
- `GET /v1/projects/{project_id}/actors`
- `GET /v1/projects/{project_id}/actors/{actor_id}`
- `POST /v1/projects/{project_id}/positions`
- `GET /v1/projects/{project_id}/positions`
- `GET /v1/projects/{project_id}/positions/{position_id}`

## Persistencia

Las tablas `actors` y `actor_positions` son append-only y tienen triggers SQLite que rechazan `UPDATE` y `DELETE`. Cada alta incrementa la versión del proyecto y registra un evento auditable. Las posiciones se recuperan entre sesiones.
