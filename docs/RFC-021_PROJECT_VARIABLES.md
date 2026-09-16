# RFC-021 — Decision Variables by Scale

**Estado:** IMPLEMENTED ON MAIN — incluido en `main@faff4f8e`.

## ProjectVariable

A `ProjectVariable` is explicit project state. It has a normalized key, type (`OBJECTIVE`, `CONSTRAINT`, or `PARAMETER`), value, spatial scope, actor, authority, source, and version lineage. `actor_id` and `authority` are mandatory.

## SuggestedVariable

A `SuggestedVariable` is only a catalog suggestion. It does not create an Objective, Constraint, Preference, Recommendation, or Decision. A user must explicitly record a ProjectVariable.

## Invariants

Variables are unique by `project_id + normalized_key`. Changes are represented as new versions with `supersedes_variable_id`; history is retained in the append-only Event Log. A normative reference is traceability metadata and does not constitute automatic legal interpretation.

## Interfaces

CLI: `/VARIABLE ADD <variable_id> <key> <type> <value> <actor_id> <authority> [unit] [spatial_scope]` and `/VARIABLE LIST`.

HTTP: `POST /v1/projects/{project_id}/variables` and `GET /v1/projects/{project_id}/variables`.

## Boundary

Registering a variable does not authorize a decision. It only records explicit project information for later evaluation.


## Baseline consolidado

RFC-021 quedó consolidado en `main` junto con RFC-019 y RFC-020 mediante el commit `faff4f8e9ce416fa1f9523b4396b85fdd9b342f8`. La persistencia append-only, la validación de autoridad y las rutas HTTP fueron verificadas en la suite completa del Core.
