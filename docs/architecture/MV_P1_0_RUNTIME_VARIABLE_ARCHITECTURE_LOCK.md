# MV-P1.0 — Runtime Variable Architecture Lock

**Project:** SiMS-DeI / SICL
**Status:** APPROVED FOR MV-P1.1 IMPLEMENTATION
**Functional base:** `d1cec3222a04ccfd969b2dfb81c222bb97294767`
**Documentary baseline:** `d9c97ee19ba6d3a2ea5849c39b1ae6cbb0ebf000`
**Date:** 2026-09-17

## Purpose

This document converts the approved MV-P0 variable architecture into the smallest safe runtime design. It does not load the complete 119-variable catalogue, implement spatial location, or create a second variable subsystem.

The runtime preserves the existing constitutional boundary between catalogue information, project state, human adoption, and decisions.

## CURRENT_RUNTIME_REUSE

The current Core already contains the two project-facing structures required by RFC-021:

- `SuggestedVariable` is an immutable dataclass representing a proposal or catalogue suggestion.
- `ProjectVariable` is an immutable dataclass representing explicit project state.

`ProjectVariable` already requires `project_id`, a normalized key, a variable type, a value, `actor_id`, and `authority`. It also carries `unit`, `spatial_scope`, `source`, `version`, `supersedes_variable_id`, and an optional normative reference. The event log reconstructs project variables from `PROJECT_VARIABLE_RECORDED` events.

SQLite persistence is currently project-centric. The project aggregate stores `project_variables` in memory, while the durable representation is the append-only event payload. This is compatible with immutable catalogue metadata because catalogue definitions do not need to be copied into the project row.

The existing `SpatialScope` enum is the sole canonical 11-scale vocabulary. No replacement scale enum is required.

## NEW_RUNTIME_STRUCTURES

MV-P1.1 adds two immutable, catalogue-level structures in `src/sicl/variable_catalog.py`:

`VariableDefinition` is the stable semantic identity of a variable. It contains:

- `canonical_variable_id`;
- `canonical_name`;
- `domain`;
- `semantic_definition`;
- `data_type`;
- `unit_semantics`;
- `base_or_derived`;
- `definition_version`;
- `status`.

`ScaleVariableProfile` expresses the relationship between one definition and one existing `SpatialScope`. It contains:

- `canonical_variable_id`;
- `spatial_scope`;
- `requirement`;
- `applicability`;
- `conditional_applicability`;
- `spatial_support`;
- `temporal_semantics`;
- `profile_version`.

The structures are frozen, serializable, and validated at construction. Duplicate definition IDs, duplicate definition/profile versions, invalid scopes, and invalid requirement or applicability states are rejected deterministically.

## EXTENDED_RUNTIME_STRUCTURES

`SuggestedVariable` is extended only with optional catalogue references: `canonical_variable_id`, `catalog_version`, and `definition_version`. Existing positional construction remains compatible because the fields have defaults.

`ProjectVariable` is extended with the same optional catalogue references plus `profile_version`. Existing project-variable payloads remain valid. New variables may reference a definition and the exact profile version adopted by the project.

These are extensions of RFC-021 entities. No `CanonicalProjectVariable`, `RuntimeProjectVariableV2`, or other parallel entity is created.

## VARIABLE_DEFINITION_RUNTIME

The catalogue is a static, immutable, packaged runtime registry. The registry exposes deterministic lookup by `canonical_variable_id`, profile lookup by `(canonical_variable_id, SpatialScope)`, and a small validation seed. Definitions are not mutable through project commands.

The first seed is intentionally narrow and contains only identities that are independently clear in MV-P0.16 and useful for the UPAO-001 vertical slice at `edificacion` and `parcela_sitio`:

- `BUILDING_FOOTPRINT`;
- `BUILDING_GROSS_AREA`;
- `BUILDING_MASSING`;
- `BUILDING_FLOORS`;
- `SITE_COORDINATE_REFERENCE`;
- `SITE_SOIL_CONDITION`;
- `SITE_ET0`;
- `SITE_VPD`.

The seed is runtime validation data, not the production catalogue.

## SCALE_VARIABLE_PROFILE_RUNTIME

Profiles use the existing `SpatialScope` enum and are indexed by the pair `(canonical_variable_id, spatial_scope)`. A profile can be required, recommended, optional, or not applicable. Applicability is represented separately from requirement semantics.

The seed includes building profiles for `edificacion` and site profiles for `parcela_sitio`. Site environmental profiles are compatible with the existing S7 environmental capability, but this slice does not modify S7 behavior or call an external source.

## PERSISTENCE_DECISION

Use **static packaged catalogue metadata plus event-backed project adoption**.

No new SQLite table is necessary in MV-P1.1. Definitions and profiles are immutable metadata shipped with the Core. Adopted project values continue to be persisted through the existing `PROJECT_VARIABLE_RECORDED` event and reconstructed into `ProjectVariable`.

This is the smallest architecture that supports stable identity, SQLite MVP operation, migration safety, and future catalogue growth without duplicating project state. A future catalogue persistence migration remains possible if catalogue size or administrative workflows require it.

## VERSIONING_DECISION

Catalogue identity is deterministic:

- `catalog_version` identifies the packaged catalogue snapshot;
- `definition_version` identifies the semantic definition version;
- `profile_version` identifies the scale-specific profile version.

Project variables record these references at adoption time. Missing references remain valid for legacy RFC-021 data and mean that the variable predates MV-P1 catalogue metadata. Future catalogue changes create new versions; they never mutate the meaning of an adopted historical value.

## PROJECT_ADOPTION_MODEL

The canonical flow is:

```text
VariableDefinition
        ↓
ScaleVariableProfile
        ↓
SuggestedVariable
        ↓
explicit project / human adoption
        ↓
ProjectVariable
```

Creating a suggestion does not create project state. Recording a project variable does not create an Objective, Constraint, Recommendation, HumanReview, or Decision. The current actor and authority requirements remain mandatory for adoption.

The runtime does not automatically promote a suggestion. A caller must explicitly create `ProjectVariable`, and the event log records the adoption payload.

## HISTORY_REPRODUCIBILITY

A project variable stores its value, project identity, actor, authority, source, version lineage, and optional catalogue references in the event payload. Reopening the SQLite repository reconstructs the same project variable from the event log.

Changing a global definition or profile in a later catalogue version cannot rewrite an existing event. New adoptions reference the new version, while historical adoptions retain their previous references. This preserves reproducibility without introducing a snapshot package manager.

## FUTURE_EXTENSION_POINTS

The catalogue and profile objects provide stable attachment points for:

- `CapabilityVariableRequirement` through profile capability references in a future additive extension;
- `SourceRequirement` through definition/profile metadata in a future additive extension;
- `SpatialLocation` through site-related profiles, without changing project-variable identity;
- Missing Data Intelligence through profile applicability and value-state evaluation.

None of these extensions is implemented in MV-P1.1.

## REJECTED_ALTERNATIVES

A second project-variable entity was rejected because RFC-021 already supplies the required project state and history boundary.

A mutable global database catalogue was rejected because it could silently change the meaning of historical projects.

A new spatial-scale enum was rejected because the Core already provides the canonical 11-value `SpatialScope`.

A full 119-row runtime seed was rejected because documentary completeness is not a reason to load production data before runtime semantics are verified.

A new SQLite catalogue table was rejected for this slice because static immutable metadata is sufficient and avoids an unnecessary migration.

## IMPLEMENTATION_BOUNDARY

MV-P1.1 includes the catalogue dataclasses, immutable registry, deterministic validation seed, optional metadata extensions to `SuggestedVariable` and `ProjectVariable`, focused tests, and this architecture document.

MV-P1.1 does not include spatial location, maps, MapLibre, geocoding, GIS, external APIs, SourceRequirement, CapabilityVariableRequirement, Missing Data Intelligence, adaptive UI, Web changes, S7 changes, Pareto changes, main merge, or deployment.

## Gates

```text
MV_P1_0_RUNTIME_ARCHITECTURE = PASS
SECOND_VARIABLE_SYSTEM_CREATED = NO
PROJECTVARIABLE_REUSED = YES
SUGGESTEDVARIABLE_REUSED = YES
HUMAN_AUTHORITY_PRESERVED = YES
READY_FOR_MV_P1_1 = YES
```

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SICL Core repository"

[2]: https://github.com/YvanCastilloQuezada/sicl-core/blob/main/docs/RFC-021_PROJECT_VARIABLES.md "RFC-021 Decision Variables by Scale"

[3]: https://github.com/YvanCastilloQuezada/sicl-core/tree/docs/mv-p0-final-batch/docs/architecture "MV-P0 final multiscale variable architecture documentation"

**Author:** Manus AI
**Decision:** Product Owner authorization for MV-P1 Batch B1.
The runtime implementation must preserve all human-authority and provenance boundaries defined above.
