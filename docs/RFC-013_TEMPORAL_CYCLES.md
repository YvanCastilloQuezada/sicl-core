# RFC-013 — Temporal Cycles

**Estado:** IMPLEMENTED; extendido por RFC-013.1 en `rfc-013-1-temporal-evolution`
**Base:** RFC-012 Multi-Actor Model

## Entidades

`TemporalCycle` modela un horizonte `2030`, `2040`, `2050` o `CUSTOM`, con fecha de inicio, fecha final opcional, supuestos, objetivos y actores involucrados. Sus estados son `DRAFT`, `ACTIVE` y `SUPERSEDED`.

`ScenarioBranch` representa una rama no sobrescribiente vinculada opcionalmente a un ciclo. Contiene condiciones, objetivos, estado (`PROPOSED`, `EVALUATED`, `SELECTED`, `DISCARDED`) y trazabilidad de selección humana.

`ScenarioEvolution` representa una propuesta explícita de transición de un escenario entre dos ciclos. Contiene `evolution_id`, `scenario_id`, `from_cycle_id`, `to_cycle_id`, `changes`, `triggers`, `state`, `applied_by`, `applied_at` y `version`. Sus estados son `PROPOSED`, `EVALUATED`, `APPLIED` y `REJECTED`.

## Reglas

Los ciclos solo agregan proyecciones y no modifican decisiones pasadas. Las ramas se persisten como versiones append-only. La selección exige un actor activo y un `HumanReview` aprobado con la misma autoridad. Ningún escenario se considera correcto por defecto ni se selecciona automáticamente.

Una evolución no modifica ciclos previos ni reescribe decisiones, recomendaciones o escenarios históricos. No se infiere automáticamente. Su aplicación exige actor y authority humanos explícitos, registra un evento y conserva todas sus versiones.

## CLI

- `/CYCLE CREATE <cycle_id> <horizon> <start_date>`
- `/CYCLE LIST`
- `/CYCLE SHOW <cycle_id>`
- `/SCENARIO CREATE <branch_id> <parent_cycle_id> <name>`
- `/SCENARIO LIST`
- `/SCENARIO SELECT <branch_id> <actor> <authority>`
- `/EVOLUTION CREATE <evolution_id> <scenario_id> <from_cycle_id> <to_cycle_id>`
- `/EVOLUTION ADD CHANGE <evolution_id> <key> <value>`
- `/EVOLUTION ADD TRIGGER <evolution_id> <trigger>`
- `/EVOLUTION APPLY <evolution_id> <actor> <authority>`
- `/EVOLUTION LIST`
- `/EVOLUTION SHOW <evolution_id>`

## HTTP v1

- `POST /v1/projects/{project_id}/cycles`
- `GET /v1/projects/{project_id}/cycles`
- `GET /v1/projects/{project_id}/cycles/{cycle_id}`
- `POST /v1/projects/{project_id}/scenarios`
- `GET /v1/projects/{project_id}/scenarios`
- `POST /v1/projects/{project_id}/scenarios/{branch_id}/select`
- `POST /v1/projects/{project_id}/scenario-evolutions`
- `GET /v1/projects/{project_id}/scenario-evolutions`
- `GET /v1/projects/{project_id}/scenario-evolutions/{evolution_id}`
- `POST /v1/scenario-evolutions/{evolution_id}/apply`

## Persistencia

Las tablas `temporal_cycles` y `scenario_branches` tienen triggers append-only. La selección de una rama inserta una nueva versión de la misma rama y conserva la versión propuesta anterior. Los eventos registran creación y selección, y los ciclos se recuperan entre sesiones.

La tabla `scenario_evolutions` tiene triggers append-only. Crear, modificar y aplicar una evolución insertan versiones nuevas; nunca actualizan ni eliminan versiones anteriores. La aplicación solo cambia el estado de la evolución y sus metadatos de aplicación. No modifica `temporal_cycles` ni `scenario_branches`.
