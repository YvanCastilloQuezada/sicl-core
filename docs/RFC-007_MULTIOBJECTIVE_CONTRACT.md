# RFC-007 — Multiobjective Contract

**Estado:** IMPLEMENTED
**Base:** `integration-v2` con RFC-004 consolidado

## Objetivo

RFC-007 expone de forma canónica la frontera de Pareto y la matriz de trade-offs ya soportadas por SICL. El resultado persistido es descriptivo: no selecciona una alternativa, no crea una Recommendation y no crea una Decision.

## Entidad `MultiobjectiveResult`

Cada resultado contiene `multiobjective_id`, `project_id`, `method`, `method_version`, `objectives`, `alternatives`, `pareto_front`, `dominated`, `incomplete`, `tradeoffs`, `state`, `inputs_hash`, `created_at` y `version`. `state` es `EXECUTED` cuando las evaluaciones requeridas están completas e `INSUFFICIENT` cuando falta alguna evaluación.

Los resultados son append-only y se almacenan en SQLite con triggers que rechazan `UPDATE` y `DELETE`. El hash SHA-256 identifica el conjunto de entradas usado para el cálculo.

## Métodos soportados

| Método | Objetivos | Resultado |
|---|---:|---|
| `pareto_front_v1` | Dos o más | `pareto_front`, `dominated`, `incomplete` y matriz de valores |
| `tradeoff_matrix_v1` | Exactamente dos | matriz de valores y estado de completitud |

La dirección de cada objetivo debe ser explícita: `MAXIMIZE` o `MINIMIZE`. Si falta, se devuelve `OBJECTIVE_DIRECTION_REQUIRED`.

## CLI

- `/MULTIOBJECTIVE PARETO <obj_1> <obj_2> [...]`
- `/MULTIOBJECTIVE TRADEOFFS <obj_1> <obj_2>`
- `/MULTIOBJECTIVE LIST`
- `/MULTIOBJECTIVE SHOW <multiobjective_id>`

Los comandos legacy `/PARETO` y `/TRADEOFF_MATRIX` permanecen sin cambios.

## HTTP `/v1`

- `POST /v1/projects/{id}/multiobjective/pareto` — body `{ "objectives": ["..."] }`, mínimo dos objetivos.
- `POST /v1/projects/{id}/multiobjective/tradeoffs` — body con exactamente dos objetivos.
- `GET /v1/projects/{id}/multiobjective` — lista resultados.
- `GET /v1/projects/{id}/multiobjective/{multiobjective_id}` — recupera un resultado.

Todas las respuestas exitosas usan el envelope canónico con `contract_version`, `project_id` y `observed_version`.

## Relación con Evaluation y Comparison

El cálculo lee `Alternative`, `Objective` y `Evaluation`. No modifica esas entidades. `tradeoffs` representa valores observados por alternativa y objetivo; no es una Comparison ni sustituye sus relaciones persistidas.

## Invariantes

1. `MultiobjectiveResult` no crea `Recommendation`.
2. `MultiobjectiveResult` no crea `Decision`.
3. La frontera de Pareto es descriptiva, no prescriptiva.
4. Las alternativas con evaluaciones incompletas aparecen en `incomplete` y producen estado `INSUFFICIENT`.
5. Los resultados son append-only.
6. No se modifican los comandos legacy.
