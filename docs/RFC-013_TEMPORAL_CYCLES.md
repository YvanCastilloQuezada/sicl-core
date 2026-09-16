# RFC-013 — Temporal Cycles

**Estado:** IMPLEMENTED en `rfc-013-temporal-cycles`  
**Base:** RFC-012 Multi-Actor Model

## Entidades

`TemporalCycle` modela un horizonte `2030`, `2040`, `2050` o `CUSTOM`, con fecha de inicio, fecha final opcional, supuestos, objetivos y actores involucrados. Sus estados son `DRAFT`, `ACTIVE` y `SUPERSEDED`.

`ScenarioBranch` representa una rama no sobrescribiente vinculada opcionalmente a un ciclo. Contiene condiciones, objetivos, estado (`PROPOSED`, `EVALUATED`, `SELECTED`, `DISCARDED`) y trazabilidad de selección humana.

## Reglas

Los ciclos solo agregan proyecciones y no modifican decisiones pasadas. Las ramas se persisten como versiones append-only. La selección exige un actor activo y un `HumanReview` aprobado con la misma autoridad. Ningún escenario se considera correcto por defecto ni se selecciona automáticamente.

## CLI

- `/CYCLE CREATE <cycle_id> <horizon> <start_date>`
- `/CYCLE LIST`
- `/CYCLE SHOW <cycle_id>`
- `/SCENARIO CREATE <branch_id> <parent_cycle_id> <name>`
- `/SCENARIO LIST`
- `/SCENARIO SELECT <branch_id> <actor> <authority>`

## HTTP v1

- `POST /v1/projects/{project_id}/cycles`
- `GET /v1/projects/{project_id}/cycles`
- `GET /v1/projects/{project_id}/cycles/{cycle_id}`
- `POST /v1/projects/{project_id}/scenarios`
- `GET /v1/projects/{project_id}/scenarios`
- `POST /v1/projects/{project_id}/scenarios/{branch_id}/select`

## Persistencia

Las tablas `temporal_cycles` y `scenario_branches` tienen triggers append-only. La selección de una rama inserta una nueva versión de la misma rama y conserva la versión propuesta anterior. Los eventos registran creación y selección, y los ciclos se recuperan entre sesiones.
