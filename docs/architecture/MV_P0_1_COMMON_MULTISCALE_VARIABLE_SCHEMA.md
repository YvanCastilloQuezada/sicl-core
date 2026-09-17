# MV-P0.1 — Common Multiscale Variable Schema

**Proyecto:** SiMS-DeI / SICL
**Programa:** MV-P0 — Multiscale Variable Matrix Definition
**Estado:** AUTHORIZED FOR ARCHITECTURE SPECIFICATION ONLY
**Product implementation:** NOT AUTHORIZED
**Baseline:** `sicl-core` plus MV-P0.0 audit at `a8cb56675a1e82712e3478e8ef2d371747dda7e4`
**S7-P0.5 reference:** `4c2017957354bd40c035c5e5bd2cd2fab7efbc58`

> This document defines the semantic contract for a future multiscale variable catalog. It does not create runtime entities, database tables, APIs, migrations, data rows, validators, translations, or product behavior.

## 1. Executive Decision

MV-P0.1 approves the **hybrid architecture** as the future direction, with observations. The architecture reuses the current `ProjectVariable` and `SuggestedVariable` concepts, preserves the constitutional entities already present in SICL, and introduces two conceptual layers: `VariableDefinition` and `ScaleVariableProfile`.

The preferred conceptual chain is:

```text
VariableDefinition
        ↓
ScaleVariableProfile
        ↓
SuggestedVariable
        ↓
ProjectVariable
```

`SuggestedVariable` remains the suggestion and adoption bridge. `ProjectVariable` remains the project-specific adoption, value, and state. The new layers are specified conceptually only. Their persistence and exact implementation are deferred.

**Decision:** APPROVED_WITH_OBSERVATIONS. The pattern is resolved for architecture, but the persistence model, full taxonomy, value serializers, and implementation boundaries require decisions before MV-P0.2.

## 2. Governing Evidence

This specification preserves the findings of MV-P0.0. `SuggestedVariable` and `ProjectVariable` already exist. RFC-021 is implemented on the audited main baseline. Variable identity, roles, typing, units, scale applicability, temporal semantics, provenance, and missing-data semantics remain partial. The capability layer in S7-P0.5 is useful but is not a variable catalog.

The approved Decision Locks establish that the same design process must remain available across all eleven spatial scales, while the interface, data requirements, agents, and visual priorities adapt by scale. The future catalog must therefore describe a common semantic system without creating eleven unrelated vocabularies.

## 3. Existing Architecture Reuse

The following concepts are reused without semantic replacement:

| Concept | Current responsibility | MV-P0.1 treatment |
|---|---|---|
| `SpatialScope` | Canonical design scale with eleven values | Reuse unchanged as project design scale |
| `SuggestedVariable` | Non-authoritative suggestion | Reuse as adoption bridge |
| `ProjectVariable` | Explicit project-specific value/state | Reuse as project layer |
| `Fact` | Declared project fact | Preserve as separate entity |
| `Assumption` | Explicit assumption | Preserve as separate entity |
| `Objective` | Direction and purpose of evaluation | Preserve as separate entity |
| `Constraint` | Project restriction | Preserve as separate entity |
| `Source` | Source metadata | Reuse as structured provenance source |
| `Evidence` | Traceable evidence | Reuse as source-supported evidence |
| `Evaluation` | Alternative/objective result | Preserve as derived assessment |
| `CapabilityResolution` | Capability applicability/availability | Reuse conceptually; do not change S7-P0.5 |
| `DesignKnowledge` | Advisory design knowledge | Keep advisory and non-authoritative |
| `Regulation` | Normative source and status | Keep separate from variable meaning |

No current entity should be replaced by a universal `Variable` class merely to simplify catalog navigation.

## 4. Hybrid Architecture

The hybrid architecture has four semantic layers. Only two are future conceptual layers.

### 4.1 VariableDefinition

`VariableDefinition` answers: **What does this variable mean?** It is language-independent and project-independent. It defines semantic identity, not a project value.

Classification: **POTENTIAL FUTURE METADATA RECORD**, with persistence unresolved.

### 4.2 ScaleVariableProfile

`ScaleVariableProfile` answers: **Where, when, and under what conditions does this variable apply?** It refines a definition by `SpatialScope`, typology, context, stage, jurisdiction, objectives, provenance needs, and capability links.

Classification: **POTENTIAL FUTURE PROFILE RECORD**, with persistence unresolved.

### 4.3 SuggestedVariable

`SuggestedVariable` presents a possible variable to a user or project. It does not create project state and does not create an objective, constraint, recommendation, review, or decision.

Classification: **EXISTING ENTITY**.

### 4.4 ProjectVariable

`ProjectVariable` records explicit project adoption, value, authority, and version lineage. It is the project-specific state layer.

Classification: **EXISTING ENTITY**.

## 5. VariableDefinition Contract

### 5.1 Responsibility

A definition gives one stable semantic identity to a variable whose meaning, dimensional interpretation, measurement method, and intended use are sufficiently coherent. It must not contain a project-specific value.

### 5.2 Candidate field classification

| Field | Classification | Rationale |
|---|---|---|
| `variable_id` | REQUIRED | Stable language-independent identity |
| `domain_id` | REQUIRED | Connects the definition to governed domain vocabulary |
| `canonical_name` | REQUIRED | Human-readable canonical name; not an ID |
| `description` | REQUIRED | States meaning and boundaries |
| `data_type` | REQUIRED | Declares the conceptual value type |
| `unit_semantics` | REQUIRED | Defines dimensional expectations, not display formatting alone |
| `temporal_semantics` | REQUIRED | Prevents loss of reference period and time basis |
| `spatial_resolution_semantics` | REQUIRED | Distinguishes data support from design scale |
| `provenance_requirements` | REQUIRED | Declares what provenance a value must carry |
| `source_requirements` | OPTIONAL | Useful where a class of source is required |
| `validation_semantics` | OPTIONAL | Defines future validation intent without implementing validators |
| `definition_version` | REQUIRED | Historical interpretation requires immutable version references |
| localization keys | REQUIRED | Visible text must be localized without changing IDs |
| `status` | REQUIRED | Governs draft, approved, deprecated, and obsolete definitions |
| project value | NOT NEEDED | Belongs to `ProjectVariable` |
| project actor | NOT NEEDED | Belongs to adoption/project state |
| recommendation | NOT NEEDED | Belongs to recommendation workflow |
| decision | NOT NEEDED | Belongs to human authority workflow |

### 5.3 Definition invariants

A definition does not create a project variable. A definition does not create an objective or constraint. A definition does not assert that data are available. A definition does not certify a regulatory requirement.

## 6. ScaleVariableProfile Contract

A profile is a conditional applicability record associated with one definition. It must not create eleven copies of the same variable merely because the variable is reused across eleven scales.

```text
ONE VariableDefinition
        ↓
ZERO OR MORE ScaleVariableProfiles
```

A different definition is justified only when meaning, dimension, measurement method, spatial support, temporal semantics, derivation, or decision use changes materially.

| Profile field | Classification | Meaning |
|---|---|---|
| `variable_id` | REQUIRED | References the definition |
| `spatial_scope` | REQUIRED | Selects one canonical design scale |
| `requirement_level` | REQUIRED | Required, recommended, optional, or not applicable |
| `applicability` | REQUIRED | Explains the resolved applicability |
| `typology_conditions` | OPTIONAL | Future conditional refinement |
| `context_conditions` | OPTIONAL | Future contextual refinement |
| `stage_conditions` | OPTIONAL | Design-stage refinement |
| `jurisdiction_conditions` | OPTIONAL | Jurisdictional refinement |
| `objective_conditions` | OPTIONAL | Objective-dependent relevance |
| `required_provenance` | REQUIRED | Minimum value provenance |
| `capability_links` | OPTIONAL | Links to capabilities without replacing capability status |
| `profile_version` | REQUIRED | Preserves historical interpretation |

## 7. SuggestedVariable

`SuggestedVariable` remains an advisory object. It may reference a `VariableDefinition` and a `ScaleVariableProfile`, but it must not duplicate their semantic fields as a second authority.

The user or authorized project actor must explicitly adopt or create project state. A suggestion may be dismissed, replaced, or accepted. Acceptance is an action that creates or records project state; it is not an automatic side effect of catalog visibility.

The following distinctions are constitutional:

```text
SUGGESTED VARIABLE != PROJECT VARIABLE
SUGGESTION != PROJECT STATE
SUGGESTION != AUTOMATIC ADOPTION
```

## 8. ProjectVariable

The current `ProjectVariable` fields remain conceptually valid: actor, authority, type, value, unit, spatial scope, source, version, supersession, and normative reference. No destructive replacement is proposed.

Future implementations may replace free-text references with canonical metadata references, but the migration must preserve historical values and event lineage. The project layer may customize value, display unit, local label alias, requirement interpretation, source selection, and notes only where the global definition’s semantic identity remains unchanged.

A project customization must not mutate the global definition or profile.

## 9. Constitutional Entity Separation

The following entities remain distinct:

| Entity | Permitted relationship | Forbidden collapse |
|---|---|---|
| `Fact` | May reference a definition or source | Must not become a project variable automatically |
| `Assumption` | May reference a definition and basis | Must not become measured fact |
| `Objective` | May identify a measurable variable or metric | Must not become a definition |
| `Constraint` | May constrain a variable | Must not become an automatic decision |
| `Evaluation` | May use a derived metric | Must not become project state |
| `Recommendation` | May consider evaluations | Must not be created by catalog rules |
| `HumanReview` | May review data and recommendations | Must remain human-authorized |
| `Decision` | May record final authority | Must never be generated by a variable catalog |

The catalog rule is not a human decision. `Evaluation != Decision`. `CapabilityResolution != Recommendation`. `Fact != ProjectVariable` unless an explicit project action records both separately.

## 10. Requirement Semantics

Variable requirement and capability availability are separate dimensions.

| Requirement | Definition |
|---|---|
| `REQUIRED` | Necessary for the specified profile purpose or capability under applicable conditions |
| `RECOMMENDED` | Materially improves analysis or understanding but does not block the base workflow |
| `OPTIONAL` | Useful additional information that is not required for the defined workflow |
| `NOT_APPLICABLE` | Does not meaningfully apply under the resolved profile conditions |

`NOT_APPLICABLE` does not mean unavailable data. It means the variable has no meaningful role in that profile.

## 11. Capability Availability Separation

The S7-P0.5 capability vocabulary remains:

- `AVAILABLE`
- `REQUIRES_DATA`
- `NOT_AVAILABLE`
- `NOT_APPLICABLE`

The conceptual chain is:

```text
ScaleVariableProfile
requirement = REQUIRED
        ↓
Project data missing
        ↓
CapabilityResolution
status = REQUIRES_DATA
```

A required variable can be missing while the capability is `REQUIRES_DATA`. A variable can be `NOT_APPLICABLE` while a capability is available for another profile. No future implementation may use one overloaded enum for both dimensions.

## 12. Role Semantics

The canonical entities already cover `Fact`, `Assumption`, `Objective`, `Constraint`, and `Evaluation`. A lightweight metadata role vocabulary may describe concepts that do not deserve new entities:

- `INPUT`: value consumed by an analysis or method.
- `PARAMETER`: configurable value that controls a method.
- `CONTEXT`: descriptive condition used to interpret a project.
- `REFERENCE`: source or reference value used for comparison.
- `DESIGN_VARIABLE`: explicit design choice subject to evaluation.
- `DERIVED_METRIC`: deterministic or model-derived output.

These roles must not duplicate canonical entities. For example, `FACT` must remain a Fact, and `DERIVED_METRIC` must not replace Evaluation.

**Decision:** APPROVED_WITH_OBSERVATIONS. A role taxonomy is useful as metadata, but its implementation is deferred.

## 13. Data Types

The future catalog should distinguish the following conceptual data types: `INTEGER`, `DECIMAL`, `BOOLEAN`, `STRING`, `ENUM`, `DATE`, `DATETIME`, `DURATION`, `REFERENCE`, `GEOMETRY`, and `COLLECTION`.

`INTEGER` and `DECIMAL` should remain separate. Integer semantics express discrete counts or identifiers with numeric meaning. Decimal semantics express measured or calculated quantities. A common display concept may exist later, but it must not erase validation differences.

The state of a value must be separate from its type:

- `null` means no value is supplied in a representation where null is permitted.
- `MISSING` means a required value has not been provided.
- `UNKNOWN` means the value is not known.
- `ZERO` is a legitimate numeric value where the definition permits it.

## 14. Units

A future unit governance layer should distinguish canonical unit identity, display symbol, dimension, conversion policy, unitless values, currency handling, percentages, densities, and compound units.

The catalog must not freeze a complete unit registry in MV-P0.1. Candidate examples include `m`, `m²`, `m³`, `ha`, `km`, `km²`, `degrees`, `persons`, `persons/km²`, `W/m²`, `kWh`, `MW`, `m³/s`, `%`, `currency`, and `currency/person`.

A unitless variable must explicitly declare that it is unitless. A percentage must state whether it is a fraction or percentage display. Currency must preserve currency code, reference date, and conversion basis when relevant.

**Strategy:** controlled unit registry later; no conversion engine now.

## 15. Temporal Semantics

`TemporalScope` must not be overloaded if it represents planning horizon. Future variable metadata should distinguish:

- `observation_time` for an instant;
- `reference_period` for the period represented;
- `measurement_frequency` such as hourly or annual;
- `scenario_year` for scenario-based planning;
- `valid_from` and `valid_to` for validity;
- `retrieved_at` for source retrieval.

Candidate resolutions are `STATIC`, `PROJECT_STATE`, `INSTANT`, `HOURLY`, `DAILY`, `MONTHLY`, `QUARTERLY`, `ANNUAL`, `MULTIYEAR`, and `SCENARIO_YEAR`.

Definition-level semantics describe what a variable can mean. Profile-level semantics describe what a scale requires. Value, Source, or Evidence metadata carries actual timestamps. No single field should carry all three meanings.

## 16. Spatial Resolution

`SpatialScope` identifies project design scale. It is not the same as data spatial resolution.

A project may operate at `region` while using population data at district resolution, climate data at grid-cell resolution, transport data on a network, and water data by watershed. The future catalog must preserve both the project scale and the data support/resolution.

The conceptual vocabulary may later include `POINT`, `LINE`, `POLYGON`, `GRID_CELL`, `CENSUS_UNIT`, `PARCEL`, `NETWORK`, `CORRIDOR`, `WATERSHED`, and `ADMINISTRATIVE_UNIT`. This is a specification of required distinctions, not a GIS implementation.

## 17. Provenance

Provenance describes a value, observation, or derivation. It does not describe the abstract meaning of a variable, although a definition may state provenance requirements.

The controlled provenance vocabulary is:

- `REAL`: measured or authoritative external value with adequate traceability.
- `APPROXIMATED`: value estimated through an explicit approximation method.
- `ASSUMED`: value introduced as an explicit project assumption.
- `SYNTHETIC`: generated for testing, education, or simulation.
- `NOT_AVAILABLE`: no value or source is available for the requested item.

A definition can require `REAL` or `REAL|APPROXIMATED`, but the actual value owns the observed provenance classification. `Source` identifies origin metadata. `Evidence` records an auditable assertion about the value or source.

## 18. Source and Evidence

The future relationship is:

```text
VariableDefinition
        ↓ source requirements
ProjectVariable / Observation
        ↓ actual source and evidence
Source
        ↓
Evidence
```

The current structured `Source` and `Evidence` entities must be reused. A future implementation should avoid keeping authoritative provenance only in the free-text `ProjectVariable.source` field.

One value may have multiple evidence records. Evidence may identify capture time, method version, URL, hash, state, and source. A regulatory interpretation may be evidence-backed, but a Source or Evidence record does not automatically become a legal interpretation.

## 19. Derived Metrics

The conceptual lineage is:

```text
Input variable(s)
        +
Method or model
        ↓
Derived metric
        ↓
Evaluation
```

A future derived metric should preserve metric identity, input references, method/model identity, method version, units, time basis, spatial basis, provenance, and derivation timestamp where relevant.

For the environmental example, `shortwave_radiation`, `direct_radiation`, and `diffuse_radiation` are source observations or inputs. `solar_azimuth` and `solar_elevation` are astronomical analysis outputs. `FacadeSolarExposure` is a separate derived metric. `RegionalSolarResourcePotential` is a separate aggregated regional concept. Similar domain does not imply identical variable identity.

## 20. Environmental Example

The following conceptual distinctions are mandatory:

```text
shortwave_radiation       = environmental input / observation
solar_azimuth             = derived astronomical output
solar_elevation           = derived astronomical output
FacadeSolarExposure       = derived spatial building result
RegionalSolarResourcePotential = regional aggregated result
```

These concepts may be related by methods and lineage, but they cannot share an ID simply because they are all related to solar conditions. Each profile must specify its scale, spatial support, time basis, source requirements, and capability relationship.

## 21. Domain Governance

Domains are stable semantic categories, not names of current government institutions. Candidate domains include identity, geometry, geography, program, function, material, human, accessibility, structure, sanitary, electrical, energy, environment, climate, water, soil, landscape, mobility, infrastructure, demography, housing, health, education, economy, employment, agriculture, fisheries, mining, industry, tourism, logistics, connectivity, land use, ecosystems, risks, public investment, cost, regulation, and governance.

The full taxonomy is not frozen here. Governance rules are frozen:

1. Domains must have stable semantic meaning.
2. A domain must not be renamed merely because institutional responsibility changes.
3. Current public institutions may be recorded as authorities or sources.
4. A domain must not encode a single jurisdiction’s organizational chart.
5. Cross-domain references must preserve each concept’s ownership.

## 22. Localization

Canonical IDs are language independent. Visible labels and descriptions use localization keys.

```text
variable_id      = POPULATION
label_key        = variables.population.label
description_key = variables.population.description
```

IDs must not be translated. Translations are not implemented in MV-P0.1. The future catalog must support the eight existing application languages without changing identity or data semantics.

## 23. Versioning

Versioning is required for definitions, profiles, catalog releases, and project adoption. Historical analyses must remain interpretable after catalog updates.

A catalog update must not silently reinterpret historical project data, evaluation results, or decisions. The future implementation should consider immutable version references, snapshots, or both. The exact mechanism remains unresolved.

A project adoption should reference the definition/profile version used at adoption. A later catalog update may create a new profile version, but it must not rewrite the historical event.

## 24. Project Customization

The future relationship is:

```text
Global Definition
        ↓
Project Adoption
        ↓
Project-specific value or override
```

Safe customization may include project value, display unit, local label alias, requirement interpretation where permitted, source selection, and notes. Forbidden customization includes changing the global meaning, dimensional identity, canonical ID, derivation semantics, or historical catalog version.

Project customization must remain project-scoped and append-only where it changes decision-relevant state.

## 25. Capability ↔ Variable Contract

S7-P0.5 currently uses `required_data` and `missing_data` strings. MV-P0.1 does not replace those strings. It defines a migration-compatible future direction:

```text
CapabilityProfile
        ↓
RequiredVariableRule[]
        ↓
VariableDefinition / ScaleVariableProfile
        ↓
Project data availability
        ↓
CapabilityResolution
```

A `RequiredVariableRule` would conceptually state a stable variable identity, acceptable provenance, applicable profile conditions, and whether absence blocks the capability. It would not change the four existing capability states.

## 26. Conditional Requirements

Requirement cannot depend only on `SpatialScope`. Future conditions may include typology, context, stage, jurisdiction, objectives, and available data.

For example, solar exposure may be not applicable to a generic object but meaningful for a photovoltaic or shading component. Both cases may use `objeto`, yet the profile condition differs. MV-P0.1 defines condition extensibility only; it does not create a typology ontology.

## 27. Missing Data

The following distinctions are mandatory:

```text
ZERO            != MISSING
MISSING         != NOT_AVAILABLE
NOT_AVAILABLE   != ASSUMED
NOT_AVAILABLE   != NOT_APPLICABLE
UNKNOWN         != ZERO
```

`MISSING` belongs to value state. `NOT_AVAILABLE` belongs primarily to provenance or capability availability, depending on context. `NOT_APPLICABLE` belongs to variable requirement or capability applicability. These concepts must not be merged into one enum.

## 28. Cross-Scale Identity

One semantic variable may be reused across multiple scales when meaning, dimension, measurement method, spatial support, temporal semantics, derivation, and decision use remain compatible.

Different aggregation does not automatically create a new ID. The same word does not guarantee the same variable. A decision to reuse or create a distinct ID must assess:

- semantic meaning;
- dimension;
- measurement method;
- spatial support;
- temporal semantics;
- derivation;
- decision use.

`POPULATION` may be reused across scales when its measurement meaning remains population count and the spatial support is represented separately. `FacadeSolarExposure` and `RegionalSolarResourcePotential` must not share an ID because their meaning, aggregation, and decision use differ.

## 29. Persistence and Ownership

| Concept | Conceptual owner | Project mutable | Persistence decision |
|---|---|---:|---|
| `VariableDefinition` | System/catalog governance | No | UNRESOLVED |
| `ScaleVariableProfile` | System/catalog governance | No; project may select | UNRESOLVED |
| `SuggestedVariable` | Catalog presentation/adoption bridge | No as global definition | Existing project behavior reused |
| `ProjectVariable` | Project authority | Yes by explicit action | Existing Event Log persistence |
| `Source` | Project/source registry | Project-scoped metadata | Existing persistence |
| `Evidence` | Project evidence registry | Append-only | Existing persistence |
| `CapabilityResolution` | Capability engine | No direct project mutation | S7-P0.5 reference |

Potential storage choices are code/catalog based, repository persisted, database persisted, or hybrid. MV-P0.1 intentionally does not select one because the required catalog size, governance workflow, deployment model, and historical snapshot needs are not yet evidenced.

## 30. Core Contract Impact

MV-P0.1 does not modify the Core Contract. The preferred future evolution is **A initially, with additive B possible after implementation evidence**. The architecture can first be specified outside runtime behavior. If canonical references are later exposed through HTTP, an additive contract extension is preferred.

A breaking change is not justified by the current audit. No migration, endpoint, schema, or serializer is authorized here.

## 31. Required Schema Table

| Concept | Responsibility | Existing reuse | New metadata needed | Persistence | Versioned | Project mutable |
|---|---|---|---|---|---|---|
| `VariableDefinition` | Meaning and identity | `ProjectVariable.normalized_key` as evidence only | Domain, type, units, time, resolution, provenance requirements | Unresolved | Yes | No |
| `ScaleVariableProfile` | Conditional scale applicability | `SpatialScope`, S7 context concepts | Requirement, conditions, capability links | Unresolved | Yes | No |
| `SuggestedVariable` | Advisory suggestion | Existing RFC-021 entity | References to definition/profile | Existing behavior | Possibly | No |
| `ProjectVariable` | Explicit project value/state | Existing RFC-021 entity | Canonical references later | Existing Event Log | Yes | Yes |
| `Fact` | Declared fact | Existing entity | Optional definition reference | Existing | Yes | Yes by explicit record |
| `Assumption` | Explicit assumption | Existing entity | Optional definition and provenance | Existing | Yes | Yes by explicit record |
| `Objective` | Evaluation direction | Existing entity | Optional variable/metric reference | Existing | Yes | Yes by project action |
| `Constraint` | Project restriction | Existing entity | Optional variable reference | Existing | Yes | Yes by project action |
| `Source` | Origin metadata | Existing entity | No replacement | Existing | Yes | Project-scoped |
| `Evidence` | Traceable assertion | Existing entity | Variable/value link later | Existing append-only | Yes | Append-only |
| `DerivedMetric` | Model output | Evaluation/simulation concepts | Input and method lineage | Unresolved | Yes | No direct mutation |
| `Evaluation` | Alternative/objective result | Existing entity | Optional metric reference | Existing append-only | Yes | No direct mutation |
| `CapabilityProfile` | Declares capability data rules | S7 concept | Stable required-variable rules later | Unresolved | Yes | No |
| `CapabilityResolution` | Resolves availability | S7-P0.5 reference | No change in this phase | Reference | Profile versioned | No |

## 32. Semantic State Table

| Dimension | Allowed conceptual states | Meaning |
|---|---|---|
| Variable requirement | `REQUIRED`, `RECOMMENDED`, `OPTIONAL`, `NOT_APPLICABLE` | Importance/applicability in a profile |
| Value state | `PRESENT`, `MISSING`, `UNKNOWN` | Whether a project value is supplied and known |
| Provenance | `REAL`, `APPROXIMATED`, `ASSUMED`, `SYNTHETIC`, `NOT_AVAILABLE` | Origin or derivation status of a value/observation |
| Capability availability | `AVAILABLE`, `REQUIRES_DATA`, `NOT_AVAILABLE`, `NOT_APPLICABLE` | Runtime capability status |

`ZERO` is a value, not a value-state failure. `NOT_APPLICABLE` is not a substitute for missing data. `NOT_AVAILABLE` in capability resolution is not a requirement level.

## 33. Worked Examples

The following examples are conceptual. They do not create data rows or claim real values.

### A. Building height

`VariableDefinition`: `BUILDING_HEIGHT`, domain `GEOMETRY`, data type `DECIMAL`, unit dimension `LENGTH`, spatial meaning `EDIFICACION`, and provenance requirement dependent on whether the value is measured, proposed, or assumed.

`ScaleVariableProfile`: applicable to `EDIFICACION`; requirement may be `REQUIRED` for a building massing workflow and `NOT_APPLICABLE` for a country-scale project profile unless a territorial building-height indicator is separately defined.

`ProjectVariable`: an explicit project value with actor and authority. A proposed height is not a measured height. Its provenance is `ASSUMED` or `SYNTHETIC` when appropriate.

`Evaluation`: may derive massing effects from height. The evaluation is not the height variable itself.

### B. Population

`VariableDefinition`: `POPULATION`, domain `DEMOGRAPHY`, data type `INTEGER`, temporal semantics requiring a reference period, and spatial resolution described separately from project scale.

`ScaleVariableProfile`: may apply at district, province, region, macro-region, or country. The same semantic ID can be reused if the count meaning remains stable and support is recorded.

`Source/Evidence`: a census or statistical source would be linked as actual source and evidence. No real value is fabricated here.

`Capability`: a territorial analysis may require population data, but requirement and availability remain separate.

### C. Shortwave radiation

`VariableDefinition`: `SHORTWAVE_RADIATION`, domain `ENVIRONMENT`, numeric type, energy-per-area unit semantics, and hourly/daily temporal alternatives.

`ScaleVariableProfile`: may be relevant to `EDIFICACION` or `PARCELA_SITIO` for solar analysis, and may have different aggregation profiles at territorial scales.

`ProjectVariable` or observation: carries actual time, location, source, and provenance. An Open-Meteo response is not automatically a design decision.

`Capability`: the S7 solar workflow may declare this data requirement. Missing data can yield `REQUIRES_DATA`.

### D. Facade solar exposure

`VariableDefinition`: `FACADE_SOLAR_EXPOSURE`, domain `ENVIRONMENT`, derived metric, geometry support, and method/version requirements.

`ScaleVariableProfile`: applies to `EDIFICACION` where facade geometry and solar position are meaningful. It may be `NOT_APPLICABLE` for a country-scale profile.

`DerivedMetric`: uses radiation inputs, solar azimuth/elevation, facade geometry, and a method. Its lineage must identify all inputs and method versions.

`Evaluation`: may evaluate alternatives using the metric, but the evaluation remains distinct from the metric and from a decision.

### E. Regional solar resource potential

`VariableDefinition`: `REGIONAL_SOLAR_RESOURCE_POTENTIAL`, domain `ENERGY` or `ENVIRONMENT`, aggregated regional metric with explicit spatial support and time basis.

`ScaleVariableProfile`: applies to `REGION`, `MACRO_REGION`, or `PAIS` only when its aggregation method is defined. It is not a facade metric.

`Source/Evidence`: requires an appropriate regional dataset and method evidence. No real value is fabricated.

`Cross-scale conclusion`: all five examples belong to related domains, but similar domain does not imply identical variable identity.

## 34. 11-Scale Empty Profile Contract

Each of the eleven future profiles uses the same empty structure. MV-P0.1 defines no variable rows.

| Field | Required in future profile |
|---|---|
| `spatial_scope` | Yes |
| applicable variable definitions | Yes, empty until MV-P0.2 onward |
| requirement levels | Yes |
| conditional applicability | Yes |
| required provenance | Yes |
| capability links | Yes, when applicable |
| recommended source classes | Yes |
| temporal requirements | Yes |
| spatial-resolution requirements | Yes |
| profile version | Yes |
| governance status | Yes |

The contract applies equally to `PAIS`, `MACRO_REGION`, `REGION`, `PROVINCIA_METROPOLI`, `DISTRITO_CIUDAD`, `ZONA_BARRIO_SECTOR`, `PARCELA_SITIO`, `EDIFICACION`, `SISTEMA`, `ESPACIO`, and `OBJETO`.

No scale is populated by this document.

## 35. Future Matrix Record

The future MV-P0.2 onward matrix uses one record shape. It contains no data rows in MV-P0.1.

| Column | Classification |
|---|---|
| `variable_id` | REQUIRED |
| `domain` | REQUIRED |
| `spatial_scope` | REQUIRED |
| `requirement` | REQUIRED |
| `role` | OPTIONAL |
| `data_type` | REQUIRED |
| `unit` | REQUIRED when dimensional |
| `temporal_semantics` | REQUIRED when time-dependent |
| `spatial_resolution` | REQUIRED when spatial data |
| `applicability_conditions` | OPTIONAL |
| `provenance_requirement` | REQUIRED |
| `source_class` | OPTIONAL |
| `capability_links` | OPTIONAL |
| `notes` | OPTIONAL |
| `profile_version` | REQUIRED |
| `display/localization keys` | REQUIRED for visible text |

Derived fields may later include resolved status, missing inputs, and catalog snapshot. They must not be entered as canonical definition rows.

## 36. Validation Categories

Future validators should be defined in categories without implementing them:

1. **Identity validation:** canonical ID format, uniqueness, and alias separation.
2. **Type validation:** value matches declared data type.
3. **Unit validation:** value unit is compatible with declared dimension.
4. **Range validation:** value is inside definition-specific bounds where justified.
5. **Temporal validation:** timestamps and periods satisfy the definition.
6. **Spatial validation:** data support and project scale are not confused.
7. **Provenance validation:** required origin and status are present.
8. **Source/Evidence validation:** references are structured and traceable.
9. **Applicability validation:** profile conditions are evaluated distinctly from availability.

No validator is implemented by MV-P0.1.

## 37. Human Authority

No catalog action may automatically create a `Recommendation`, `HumanReview`, `Decision`, or approval. A suggestion may lead to an explicit user action, but the action must remain visible and attributable.

The following invariants remain binding:

```text
SuggestedVariable != automatic adoption
CapabilityResolution != Recommendation
Evaluation != Decision
Catalog rule != Human Decision
```

A catalog may identify missing data or applicable variables. It may not silently resolve normative ambiguity or grant authority.

## 38. Compatibility

The future design must remain compatible with RFC-021 `SuggestedVariable`, RFC-021 `ProjectVariable`, existing projects, HTTP and CLI interfaces, repository event replay, Evaluation/Pareto, S7 environmental analysis, and S7-P0.5 CapabilityResolution.

The first implementation must preserve old project records and must not require destructive migration. Existing `ProjectVariable` values must remain interpretable. Existing free-text source fields may be retained during migration while structured references are added later.

No compatibility code is written here.

## 39. Risks and Mitigations

| Risk | Mitigation principle |
|---|---|
| Duplicate ontology | Reuse existing canonical entities and define explicit relationships |
| Overloaded Variable entity | Keep Fact, Assumption, Objective, Constraint, and Evaluation separate |
| Free-text unit drift | Define controlled unit semantics before validation |
| Semantic ID collisions | Use language-independent stable IDs and governance review |
| Mixing Fact and Variable | Require explicit adoption and preserve entity boundaries |
| Mixing Objective and Variable | Let Objective reference a variable/metric without becoming one |
| Mixing missing and zero | Keep value state separate from numeric value |
| Mixing `NOT_AVAILABLE` and `NOT_APPLICABLE` | Keep requirement and capability dimensions separate |
| Government-agency coupling | Govern stable domains; associate institutions as authorities/sources |
| Historical reinterpretation | Use immutable catalog/profile references or snapshots |
| Frontend-only applicability | Resolve applicability through a controlled capability/profile model |
| Untraceable provenance | Reuse Source/Evidence and require value-level provenance |
| Cross-scale false equivalence | Apply meaning, dimension, support, time, derivation, and decision-use tests |
| Catalog explosion | Prefer one definition with multiple profiles unless semantics genuinely differ |

## 40. Proposed Decision Locks

The following compact locks are proposed for Product Owner review. They are not implemented locks in runtime code.

- **DL-MV-SCHEMA-01 — Hybrid reuse:** Reuse RFC-021 project entities and add future definition/profile metadata only where gaps are evidenced.
- **DL-MV-SCHEMA-02 — Three layers:** Use `VariableDefinition → ScaleVariableProfile → SuggestedVariable → ProjectVariable`.
- **DL-MV-SCHEMA-03 — Constitutional separation:** Preserve Fact, Assumption, Objective, Constraint, Evaluation, Recommendation, HumanReview, and Decision as separate concepts.
- **DL-MV-SCHEMA-04 — Requirement semantics:** Use `REQUIRED`, `RECOMMENDED`, `OPTIONAL`, and `NOT_APPLICABLE` for variable requirements.
- **DL-MV-SCHEMA-05 — Capability separation:** Preserve the S7-P0.5 capability states and do not merge them with variable requirements.
- **DL-MV-SCHEMA-06 — Units and time:** Govern units, temporal meaning, and spatial resolution separately from project scale.
- **DL-MV-SCHEMA-07 — Provenance:** Attach provenance to values, observations, and derivations; preserve structured Source/Evidence.
- **DL-MV-SCHEMA-08 — Cross-scale identity:** Reuse IDs only when semantic, dimensional, temporal, spatial, derivational, and decision-use criteria remain compatible.
- **DL-MV-SCHEMA-09 — Versioning:** Do not silently reinterpret historical project data or Evaluation results after catalog updates.
- **DL-MV-SCHEMA-10 — Human Authority:** Catalog rules and capability results never create recommendations, reviews, decisions, or approvals automatically.

## 41. Decisions Required Before MV-P0.2

Before populating any scale matrix, Product Owner decisions are required on catalog ownership, persistence strategy, catalog release versioning, profile approval workflow, value type representation, unit registry scope, temporal metadata ownership, spatial support vocabulary, provenance status ownership, capability rule ownership, project customization limits, and migration policy.

The implementation order should also be decided. The safest sequence is to define the catalog record format, validate it against a small number of non-production examples, review the constitutional boundaries, and only then populate one scale at a time.

## 42. Evidence Appendix

| Evidence | Location | Architectural use |
|---|---|---|
| MV-P0.0 audit | `docs/architecture/MV_P0_0_CURRENT_VARIABLE_ARCHITECTURE_AUDIT.md` | Current gaps and reuse findings |
| RFC-021 | `docs/RFC-021_PROJECT_VARIABLES.md` | Existing variable contract |
| Project variables | `src/sicl/feasibility.py` | Existing `ProjectVariable` and `SuggestedVariable` |
| Project replay | `src/sicl/repository.py` | Event-based persistence behavior |
| HTTP variable routes | `api/routes/v1.py` | Existing POST/GET surface |
| Spatial scales | `src/sicl/domain.py` | Eleven canonical `SpatialScope` values |
| Source/Evidence | `src/sicl/domain.py` | Existing provenance primitives |
| Regulation | `src/sicl/domain.py` | Normative entities and snapshots |
| Site Intelligence | `src/sicl/site_intelligence.py` | Open-Meteo and fallback observation architecture |
| S7-P0.5 capability reference | commit `4c201795...`, `src/sicl/capabilities.py` | Availability/applicability separation |

## Final Gate

MV_P0_1_SPECIFICATION_ONLY = YES

HYBRID_ARCHITECTURE_DEFINED = YES

THREE_LAYER_PATTERN_RESOLVED = YES

REQUIREMENT_VS_CAPABILITY_SEPARATED = YES

UNITS_GOVERNANCE_DEFINED = YES

TEMPORAL_SPATIAL_SEMANTICS_DEFINED = YES

PROVENANCE_CONTRACT_DEFINED = YES

SOURCE_EVIDENCE_CONTRACT_DEFINED = YES

CROSS_SCALE_IDENTITY_RULE_DEFINED = YES

CAPABILITY_VARIABLE_CONTRACT_DEFINED = YES

HUMAN_AUTHORITY_PRESERVED = YES

VARIABLES_LOADED = NO

PRODUCT_IMPLEMENTATION = NO

READY_FOR_MV_P0_2 = NO — pending the decisions in section 41.

PRODUCT_CODE_CHANGED = NO
WEB_CHANGED = NO
DATABASE_CHANGED = NO
API_CHANGED = NO
NEW_DEPENDENCIES = NO
MAIN_MODIFIED = NO
DEPLOYED = NO

**STOP.**

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SiMS-DeI SICL Core repository"
[2]: https://github.com/YvanCastilloQuezada/sicl-web "SiMS-DeI SICL Web repository"
