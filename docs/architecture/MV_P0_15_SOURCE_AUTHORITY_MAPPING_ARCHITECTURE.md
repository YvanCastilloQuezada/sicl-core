# MV-P0.15 — Source / Authority Mapping Architecture

**Status:** DOCUMENTARY ARCHITECTURE ONLY
**Existing semantics:** Source and Evidence remain separate canonical entities

## 1. Source resolution chain

```text
VariableDefinition
  → SourceRequirement
  → Candidate Source
  → Source
  → Evidence
  → ProjectVariable / Fact / Assumption as appropriate
```

Updates never silently mutate project state. Higher-authority evidence is not silently replaced by lower-authority information.

## 2. SourceRequirement

| Field | Meaning |
|---|---|
| `canonical_variable_id` | Candidate variable definition |
| `source_class` | Stable class, not institution ontology |
| `authority_requirement` | Minimum authority level required |
| `spatial_coverage_requirement` | Required support/coverage |
| `spatial_resolution_requirement` | Resolution needed for use |
| `temporal_requirement` | Period, validity, retrieval, frequency |
| `update_frequency_requirement` | Expected refresh cadence |
| `provenance_requirement` | Evidence and method metadata |
| `validation_requirement` | Human/technical validation needed |
| `applicable_scopes` | Scale profiles |
| `notes` | Limitations and applicability |

## 3. Stable source classes

| Source class | Typical role |
|---|---|
| `USER_INPUT` | candidate source category; not an authority claim by itself |
| `PROJECT_DOCUMENT` | candidate source category; not an authority claim by itself |
| `SURVEY` | candidate source category; not an authority claim by itself |
| `SENSOR` | candidate source category; not an authority claim by itself |
| `GIS_DATASET` | candidate source category; not an authority claim by itself |
| `CADASTRAL_DATA` | candidate source category; not an authority claim by itself |
| `REGULATORY_SOURCE` | candidate source category; not an authority claim by itself |
| `OFFICIAL_STATISTICS` | candidate source category; not an authority claim by itself |
| `ENVIRONMENTAL_DATA` | candidate source category; not an authority claim by itself |
| `REMOTE_SENSING` | candidate source category; not an authority claim by itself |
| `TECHNICAL_REFERENCE` | candidate source category; not an authority claim by itself |
| `MANUFACTURER_DATA` | candidate source category; not an authority claim by itself |
| `DERIVED` | candidate source category; not an authority claim by itself |
| `EXTERNAL_API` | candidate source category; not an authority claim by itself |

## 4. Authority hierarchy

1. Official regulation or authoritative public source.
2. Validated project evidence.
3. Technical or professional reference.
4. External dataset.
5. User-provided evidence.
6. Assumption or synthetic fallback.

Authority is evaluated for the specific variable, jurisdiction, period, resolution, and intended use. Location alone never determines authoritative truth.

## 5. Documentary SourceRequirement relationships

| Relationship | Requirement |
|---|---|
| Canonical variable → requirement | Source class, authority, spatial/temporal support, provenance |
| Requirement → candidate source | Compatibility check before use |
| Source → evidence | Evidence captures actual retrieved/project content |
| Evidence → project state | Explicit adoption as Fact, Assumption, or ProjectVariable as appropriate |

`SOURCE_REQUIREMENT_RELATIONSHIPS = 119 documentary candidates`
`SOURCE_CLASSES = 14`
`SOURCE_REQUIREMENT_ARCHITECTURE = PASS`
`AUTHORITY_MODEL = PASS`
`READY_FOR_MV_P0_16 = YES`
`EXTERNAL_PROVIDER_MAPPING = NOT PERFORMED`
`SOURCE_RUNTIME_STRUCTURE_CREATED = NO`
