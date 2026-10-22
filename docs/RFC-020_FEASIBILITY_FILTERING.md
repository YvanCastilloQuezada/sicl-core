# RFC-020 — Feasibility Filtering

**Estado:** IMPLEMENTED ON MAIN — incluido en `main@f2c4d205198e6050cdfd50e228e8ba21d3d4c79f`.

## Purpose

RFC-020 evaluates whether an Alternative satisfies declared hard and soft constraints. It is an analytical result, not a Recommendation, HumanReview, or Decision.

## States

`FEASIBLE` means every evaluated hard constraint is satisfied. `INFEASIBLE` means at least one hard constraint is violated. `INSUFFICIENT_DATA` means a required value is absent. `UNKNOWN` means evaluation cannot be determined safely.

## Pareto boundary

Only `FEASIBLE` alternatives may enter `feasible_pareto_front`. `INFEASIBLE`, `UNKNOWN`, and `INSUFFICIENT_DATA` alternatives remain visible in the full result for auditability and are excluded from the feasible front.

## Human authority

The filter never creates a Recommendation, HumanReview, or Decision. A human actor remains responsible for interpretation and subsequent authorized workflow actions.

## Interfaces

CLI: `/FEASIBILITY CHECK <alternative_id> '<values_json>'` and `/MULTIOBJECTIVE FEASIBLE_PARETO '<pareto_ids_json>'`.

HTTP: `POST /v1/projects/{project_id}/feasibility` and `POST /v1/projects/{project_id}/multiobjective/feasible-pareto`.

## Verification

The directed CLI test demonstrates a hard investment limit of 100: value 90 is `FEASIBLE`, value 120 is `INFEASIBLE`, and the feasible front retains only the first alternative.


## Baseline consolidado

RFC-020 quedó consolidado en `main` junto con RFC-019 y RFC-021 mediante el commit `faff4f8e9ce416fa1f9523b4396b85fdd9b342f8`. La suite completa del Core y la compilación de `src`, `api` y `tests` pasan sobre este baseline.
