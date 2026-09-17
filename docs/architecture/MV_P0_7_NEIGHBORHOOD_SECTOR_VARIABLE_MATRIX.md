# MV-P0.7 — Neighborhood / Barrio / Sector Variable Matrix

**SpatialScope:** `zona_barrio_sector`
**Status:** SPECIFICATION ONLY
**Product implementation:** NOT AUTHORIZED

## 1. Scale definition

The `zona_barrio_sector` scale represents territorial design intelligence for neighborhood / barrio / sector. It is not a statistical dashboard. It preserves the design chain: current state/context → problem/opportunity → objectives → constraints → design or scenario variables → alternatives/scenarios → analysis → derived metrics → evaluation → trade-offs/Pareto where appropriate → HumanReview → Decision.

The matrix uses stable semantic domains rather than current government institutions. Domain is not government institution. No external sources are mapped in this batch.

## 2. Minimum and recommended profiles

The minimum profile contains **15 records**. The recommended complete profile contains **30 records**. The remaining records are conditional or recommended by project typology, context, stage, available data, and objectives. The count is not an optimization target.

## 3. Matrix contract

| ID | Domain | Requirement | Role | Type | Unit semantics | Temporal semantics | Spatial resolution | Applicability |
|---|---|---|---|---|---|---|---|---|
| `NEIGHBORHOOD_SECTOR_BOUNDARY` | BOUNDARY | REQUIRED | CONTEXT | GEOMETRY | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_AREA` | AREA | REQUIRED | DERIVED_METRIC | DECIMAL | domain-specific unit | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_URBAN_MORPHOLOGY` | URBAN | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_BLOCKS` | BLOCKS | REQUIRED | CONTEXT | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_PLOTS` | PLOTS | REQUIRED | CONTEXT | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_BUILDING_STOCK` | BUILDING | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_BUILDING_HEIGHTS` | BUILDING | REQUIRED | DERIVED_METRIC | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_COVERAGE` | COVERAGE | REQUIRED | DERIVED_METRIC | DECIMAL | domain-specific unit | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_DENSITY` | DENSITY | REQUIRED | DERIVED_METRIC | DECIMAL | domain-specific unit | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_POPULATION` | POPULATION | REQUIRED | STATE | DECIMAL | domain-specific unit | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_HOUSEHOLDS` | HOUSEHOLDS | REQUIRED | STATE | DECIMAL | domain-specific unit | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_HOUSING_DEFICIT` | HOUSING | REQUIRED | DERIVED_METRIC | DECIMAL | domain-specific unit | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_LAND_USE` | LAND | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_MIXED_USE` | MIXED | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_STREET_NETWORK` | STREET | REQUIRED | CONTEXT | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_ROAD_HIERARCHY` | ROAD | RECOMMENDED | CONTEXT | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_PEDESTRIAN_NETWORK` | PEDESTRIAN | RECOMMENDED | CONTEXT | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_PUBLIC_TRANSPORT` | PUBLIC | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_ACCESSIBILITY` | ACCESSIBILITY | RECOMMENDED | DERIVED_METRIC | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_WALKABILITY` | WALKABILITY | RECOMMENDED | DERIVED_METRIC | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_PUBLIC_SPACE` | PUBLIC | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_GREEN_SPACE` | GREEN | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_WATER_SERVICE` | WATER | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_SEWER_SERVICE` | SEWER | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_ELECTRICITY_SERVICE` | ELECTRICITY | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_URBAN_HEAT` | URBAN | OPTIONAL | DERIVED_METRIC | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_AIR_QUALITY` | AIR | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_FLOOD_EXPOSURE` | FLOOD | OPTIONAL | DERIVED_METRIC | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_URBAN_REGULATIONS` | URBAN | OPTIONAL | CONSTRAINT | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `NEIGHBORHOOD_SECTOR_INTERVENTION_SCENARIO` | INTERVENTION | OPTIONAL | DESIGN_VARIABLE | COLLECTION | count/value/collection | SCENARIO/PROJECT_STATE | scope-specific dataset resolution | where relevant and data are available |

## 4. Territorial design semantics

State/context variables describe observed or declared conditions. Design/scenario variables describe controllable choices or scenario assumptions. Derived metrics require a declared method. Evaluations require explicit objectives, evidence, provenance, and a human-governed process. No state value automatically becomes an objective, constraint, decision, or project performance metric.

Socioeconomic, productive, environmental, infrastructure, governance, and risk domains are stable semantic domains. They are not ministries, agencies, or automatically authoritative interpretations.

## 5. Temporal semantics

Where relevant, records distinguish observation year, reference period, measurement frequency, scenario year, validity period, and retrieval time. Historical/observed values are not silently compared with projected/scenario values. Incompatible years remain `MISSING`, `UNKNOWN`, or `NOT_AVAILABLE` as appropriate.

## 6. Spatial resolution

`SpatialScope = zona_barrio_sector` is not identical to dataset spatial resolution. A zona_barrio_sector project may use finer or coarser datasets when the resolution, aggregation, provenance, and limitations are explicit. No GIS implementation is created.

## 7. Conditional applicability and provenance

Variables apply only where the design question, typology, context, stage, available data, and objectives justify them. `NOT_APPLICABLE` is distinct from `NOT_AVAILABLE`; `ZERO` is distinct from `MISSING`; `MISSING` is distinct from `UNKNOWN`; `NOT_AVAILABLE` is distinct from `ASSUMED`.

Each record requires source-class and evidence metadata when populated. No external source claim or value is loaded in this specification.

## 8. Design Knowledge and regulatory relationship

Design Knowledge may provide patterns, strategies, or questions for territorial analysis, but it does not create project values. Regulation follows `Regulation → Evidence/Interpretation → Constraint → project relation`; a rule is not automatically a project variable value or Decision. Human Authority is preserved.

## 9. Scale-specific design/scenario candidates

Candidate interventions include spatial structure, service/facility networks, mobility and transport corridors, housing strategies, green/ecological networks, infrastructure portfolios, productive corridors, risk reduction, water and energy strategies, and public investment scenarios. These candidates are not mandatory variables.

## 10. Gate

`NEIGHBORHOOD_SECTOR_VARIABLE_COUNT = 30`
`NEIGHBORHOOD_SECTOR_MINIMUM_COUNT = 15`
`NEIGHBORHOOD_SECTOR_COMPLETE_COUNT = 30`
`TERRITORIAL_STATE_DESIGN_SEPARATION = PASS`
`SOCIOECONOMIC_VARIABLE_MODEL = PASS`
`PRODUCTIVE_SECTOR_MODEL = PASS`
`TEMPORAL_SEMANTICS = PASS`
`SPATIAL_RESOLUTION_SEMANTICS = PASS`
`CONDITIONAL_APPLICABILITY = PASS`
`PROVENANCE = PASS`
`HUMAN_AUTHORITY = PASS`
`PRODUCT_IMPLEMENTATION = NO`

**Status:** MV-P0.7 specification PASS.

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SiMS-DeI SICL Core repository"
