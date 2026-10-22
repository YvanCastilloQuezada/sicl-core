# RFC-006 — Simulation Contract

**Estado:** IMPLEMENTED
**Base:** `integration-v2` (`1492c074`)
**Rama:** `rfc-006-simulation-contract`

## Objetivo

Definir `Simulation` como capacidad analítica canónica para ejecuciones deterministas y de sensibilidad. Una Simulation registra inputs, outputs, método, estado y hash de evidencia. No tiene autoridad decisoria.

## Entidad

`Simulation` contiene:

- `simulation_id`
- `project_id`
- `simulation_type`
- `method`
- `method_version`
- `inputs`
- `outputs`
- `state`
- `started_at`
- `finished_at`
- `evidence_hash`
- `version`

Los tipos admitidos son `DETERMINISTIC`, `MONTE_CARLO`, `SCENARIO` y `SENSITIVITY`. Los métodos deterministas y de sensibilidad están implementados en RFC-006; `monte_carlo_v1` está implementado en RFC-006.1. `SCENARIO` permanece definido como tipo, pero sin método ejecutable en esta fase.

Los estados son `PLANNED`, `EXECUTED`, `FAILED` e `INSUFFICIENT`. Si falta un input requerido, se registra una Simulation `INSUFFICIENT`. El hash SHA-256 se calcula sobre la representación JSON canónica de `inputs` y `outputs`.

## Catálogo inicial

| Método | Tipo | Inputs requeridos | Outputs |
|---|---|---|---|
| `deterministic_basic_v1` | `DETERMINISTIC` | `alternative_id`, `objective_id`, `parameter_value` | `objective_value`, `delta` |
| `sensitivity_linear_v1` | `SENSITIVITY` | `alternative_id`, `objective_id`, `parameter`, `range` | `sensitivity_coefficient`, `samples` |

Los outputs incluyen además `feasibility` y `provenance` cuando la ejecución es válida.

## CLI

```text
/SIMULATE RUN <simulation_type> <method> [params]
/SIMULATE LIST
/SIMULATE SHOW <simulation_id>
/SIMULATE METHODS
```

Los parámetros pueden proporcionarse como un objeto JSON o como pares `key=value`.

## HTTP v1

| Método | Endpoint | Resultado |
|---|---|---|
| `POST` | `/v1/projects/{project_id}/simulations` | Ejecuta y registra una Simulation |
| `GET` | `/v1/projects/{project_id}/simulations` | Lista Simulations del proyecto |
| `GET` | `/v1/projects/{project_id}/simulations/{simulation_id}` | Recupera una Simulation |
| `GET` | `/v1/simulations/methods` | Lista el catálogo disponible |

Las respuestas de proyecto usan el envelope canónico v1 y contienen `contract_version`, `project_id` y `observed_version`.

## Invariantes

Simulation no crea Decision, no crea Recommendation y no convierte Assumption en Fact. Es append-only: sus filas no se actualizan ni eliminan; una nueva ejecución/versionado produce un nuevo registro. Un método inexistente devuelve `METHOD_NOT_FOUND`; un método incompatible con el tipo solicitado devuelve `METHOD_TYPE_MISMATCH`; una solicitud HTTP sin inputs requeridos devuelve `INSUFFICIENT_INPUTS` con HTTP 422.

Simulation es distinta de Evaluation. Evaluation registra una valoración de una Alternative respecto a un Objective; Simulation registra la ejecución reproducible de un método sobre inputs y outputs. Una Simulation no sustituye una Evaluation ni la crea automáticamente.

La capacidad no constituye certificación profesional ni validación normativa.
