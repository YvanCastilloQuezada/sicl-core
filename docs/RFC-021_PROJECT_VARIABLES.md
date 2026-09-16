# RFC-021 — Decision Variables by Scale

**Estado:** IMPLEMENTED ON BRANCH — pendiente de merge de RFC-019 a `main`.

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
