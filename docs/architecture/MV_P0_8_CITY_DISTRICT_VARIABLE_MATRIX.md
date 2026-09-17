# MV-P0.8 — District / City Variable Matrix

**SpatialScope:** `distrito_ciudad`
**Status:** SPECIFICATION ONLY
**Product implementation:** NOT AUTHORIZED

## 1. Scale definition

The `distrito_ciudad` scale represents territorial design intelligence for district / city. It is not a statistical dashboard. It preserves the design chain: current state/context → problem/opportunity → objectives → constraints → design or scenario variables → alternatives/scenarios → analysis → derived metrics → evaluation → trade-offs/Pareto where appropriate → HumanReview → Decision.

The matrix uses stable semantic domains rather than current government institutions. Domain is not government institution. No external sources are mapped in this batch.

## 2. Minimum and recommended profiles

The minimum profile contains **15 records**. The recommended complete profile contains **30 records**. The remaining records are conditional or recommended by project typology, context, stage, available data, and objectives. The count is not an optimization target.

## 3. Matrix contract

| ID | Domain | Requirement | Role | Type | Unit semantics | Temporal semantics | Spatial resolution | Applicability |
|---|---|---|---|---|---|---|---|---|
| `CITY_DISTRICT_BOUNDARY` | BOUNDARY | REQUIRED | CONTEXT | GEOMETRY | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_AREA` | AREA | REQUIRED | DERIVED_METRIC | DECIMAL | domain-specific unit | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_POPULATION` | POPULATION | REQUIRED | STATE | DECIMAL | domain-specific unit | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_POPULATION_GROWTH` | POPULATION | REQUIRED | DERIVED_METRIC | DECIMAL | domain-specific unit | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_DENSITY` | DENSITY | REQUIRED | DERIVED_METRIC | DECIMAL | domain-specific unit | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_MIGRATION` | MIGRATION | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_HOUSEHOLDS` | HOUSEHOLDS | REQUIRED | STATE | DECIMAL | domain-specific unit | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_HOUSING_STOCK` | HOUSING | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_HOUSING_DEFICIT` | HOUSING | REQUIRED | DERIVED_METRIC | DECIMAL | domain-specific unit | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_OVERCROWDING` | OVERCROWDING | REQUIRED | DERIVED_METRIC | DECIMAL | domain-specific unit | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_AFFORDABILITY` | AFFORDABILITY | REQUIRED | DERIVED_METRIC | DECIMAL | domain-specific unit | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_BASIC_SERVICES` | BASIC | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_EMPLOYMENT` | EMPLOYMENT | REQUIRED | STATE | DECIMAL | domain-specific unit | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_ECONOMIC_ACTIVITY` | ECONOMIC | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_LAND_USE` | LAND | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_URBANIZED_AREA` | URBANIZED | RECOMMENDED | DERIVED_METRIC | DECIMAL | domain-specific unit | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_URBAN_EXPANSION` | URBAN | RECOMMENDED | DERIVED_METRIC | DECIMAL | domain-specific unit | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_ROAD_NETWORK` | ROAD | RECOMMENDED | CONTEXT | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_PUBLIC_TRANSPORT` | PUBLIC | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_TRIPS` | TRIPS | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_CONGESTION` | CONGESTION | RECOMMENDED | DERIVED_METRIC | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_HEALTH_FACILITIES` | HEALTH | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_HEALTH_ACCESSIBILITY` | HEALTH | OPTIONAL | DERIVED_METRIC | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_EDUCATION_FACILITIES` | EDUCATION | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_WATER_SANITATION` | WATER | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_DIGITAL_CONNECTIVITY` | DIGITAL | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_GREEN_INFRASTRUCTURE` | GREEN | OPTIONAL | DESIGN_VARIABLE | COLLECTION | count/value/collection | SCENARIO/PROJECT_STATE | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_FLOOD_RISK` | FLOOD | OPTIONAL | DERIVED_METRIC | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_PUBLIC_INVESTMENT` | PUBLIC | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `CITY_DISTRICT_URBAN_DEVELOPMENT_SCENARIO` | URBAN | OPTIONAL | DESIGN_VARIABLE | COLLECTION | count/value/collection | SCENARIO/PROJECT_STATE | scope-specific dataset resolution | where relevant and data are available |

## 4. Territorial design semantics

State/context variables describe observed or declared conditions. Design/scenario variables describe controllable choices or scenario assumptions. Derived metrics require a declared method. Evaluations require explicit objectives, evidence, provenance, and a human-governed process. No state value automatically becomes an objective, constraint, decision, or project performance metric.

Socioeconomic, productive, environmental, infrastructure, governance, and risk domains are stable semantic domains. They are not ministries, agencies, or automatically authoritative interpretations.

## 5. Temporal semantics

Where relevant, records distinguish observation year, reference period, measurement frequency, scenario year, validity period, and retrieval time. Historical/observed values are not silently compared with projected/scenario values. Incompatible years remain `MISSING`, `UNKNOWN`, or `NOT_AVAILABLE` as appropriate.

## 6. Spatial resolution

`SpatialScope = distrito_ciudad` is not identical to dataset spatial resolution. A distrito_ciudad project may use finer or coarser datasets when the resolution, aggregation, provenance, and limitations are explicit. No GIS implementation is created.

## 7. Conditional applicability and provenance

Variables apply only where the design question, typology, context, stage, available data, and objectives justify them. `NOT_APPLICABLE` is distinct from `NOT_AVAILABLE`; `ZERO` is distinct from `MISSING`; `MISSING` is distinct from `UNKNOWN`; `NOT_AVAILABLE` is distinct from `ASSUMED`.

Each record requires source-class and evidence metadata when populated. No external source claim or value is loaded in this specification.

## 8. Design Knowledge and regulatory relationship

Design Knowledge may provide patterns, strategies, or questions for territorial analysis, but it does not create project values. Regulation follows `Regulation → Evidence/Interpretation → Constraint → project relation`; a rule is not automatically a project variable value or Decision. Human Authority is preserved.

## 9. Scale-specific design/scenario candidates

Candidate interventions include spatial structure, service/facility networks, mobility and transport corridors, housing strategies, green/ecological networks, infrastructure portfolios, productive corridors, risk reduction, water and energy strategies, and public investment scenarios. These candidates are not mandatory variables.

## 10. Gate

`CITY_DISTRICT_VARIABLE_COUNT = 30`
`CITY_DISTRICT_MINIMUM_COUNT = 15`
`CITY_DISTRICT_COMPLETE_COUNT = 30`
`TERRITORIAL_STATE_DESIGN_SEPARATION = PASS`
`SOCIOECONOMIC_VARIABLE_MODEL = PASS`
`PRODUCTIVE_SECTOR_MODEL = PASS`
`TEMPORAL_SEMANTICS = PASS`
`SPATIAL_RESOLUTION_SEMANTICS = PASS`
`CONDITIONAL_APPLICABILITY = PASS`
`PROVENANCE = PASS`
`HUMAN_AUTHORITY = PASS`
`PRODUCT_IMPLEMENTATION = NO`

**Status:** MV-P0.8 specification PASS.

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SiMS-DeI SICL Core repository"
