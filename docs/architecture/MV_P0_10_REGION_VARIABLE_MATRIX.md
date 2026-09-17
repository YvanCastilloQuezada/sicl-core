# MV-P0.10 — Region Variable Matrix

**SpatialScope:** `region`
**Status:** SPECIFICATION ONLY
**Product implementation:** NOT AUTHORIZED

## 1. Scale definition

The `region` scale represents territorial design intelligence for region. It is not a statistical dashboard. It preserves the design chain: current state/context → problem/opportunity → objectives → constraints → design or scenario variables → alternatives/scenarios → analysis → derived metrics → evaluation → trade-offs/Pareto where appropriate → HumanReview → Decision.

The matrix uses stable semantic domains rather than current government institutions. Domain is not government institution. No external sources are mapped in this batch.

## 2. Minimum and recommended profiles

The minimum profile contains **16 records**. The recommended complete profile contains **32 records**. The remaining records are conditional or recommended by project typology, context, stage, available data, and objectives. The count is not an optimization target.

## 3. Matrix contract

| ID | Domain | Requirement | Role | Type | Unit semantics | Temporal semantics | Spatial resolution | Applicability |
|---|---|---|---|---|---|---|---|---|
| `REGION_TERRITORIAL_BOUNDARY` | TERRITORIAL | REQUIRED | CONTEXT | GEOMETRY | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `REGION_COMPONENT_PROVINCES` | COMPONENT | REQUIRED | CONTEXT | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `REGION_POPULATION` | POPULATION | REQUIRED | STATE | DECIMAL | domain-specific unit | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_URBAN_RURAL_DISTRIBUTION` | URBAN | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_MIGRATION` | MIGRATION | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_URBAN_SYSTEM` | URBAN | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_REGIONAL_GVA` | REGIONAL | REQUIRED | STATE | DECIMAL | domain-specific unit | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_SECTOR_COMPOSITION` | SECTOR | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_PRODUCTIVITY` | PRODUCTIVITY | REQUIRED | DERIVED_METRIC | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `REGION_EMPLOYMENT` | EMPLOYMENT | REQUIRED | STATE | DECIMAL | domain-specific unit | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_INFORMALITY` | INFORMALITY | REQUIRED | DERIVED_METRIC | DECIMAL | domain-specific unit | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `REGION_INCOME` | INCOME | REQUIRED | STATE | DECIMAL | domain-specific unit | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_POVERTY` | POVERTY | REQUIRED | STATE | DECIMAL | domain-specific unit | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_AGRICULTURE` | AGRICULTURE | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_CULTIVATED_AREA` | CULTIVATED | REQUIRED | STATE | DECIMAL | domain-specific unit | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_AGRICULTURAL_PRODUCTION` | AGRICULTURAL | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_IRRIGATION` | IRRIGATION | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_FISHERIES` | FISHERIES | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_MINING` | MINING | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_INDUSTRY` | INDUSTRY | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_TOURISM` | TOURISM | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_HEALTH_COVERAGE` | HEALTH | RECOMMENDED | DERIVED_METRIC | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `REGION_EDUCATION_ACCESSIBILITY` | EDUCATION | RECOMMENDED | DERIVED_METRIC | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `REGION_ROADS_PORTS_AIRPORTS` | ROADS | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_ENERGY_GENERATION` | ENERGY | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_WATER_AVAILABILITY` | WATER | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_ECOSYSTEMS` | ECOSYSTEMS | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_HAZARDS` | HAZARDS | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_PUBLIC_INVESTMENT` | PUBLIC | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `REGION_REGIONAL_SCENARIO` | REGIONAL | OPTIONAL | DESIGN_VARIABLE | COLLECTION | count/value/collection | SCENARIO/PROJECT_STATE | scope-specific dataset resolution | where relevant and data are available |
| `REGION_STRATEGIC_INVESTMENT_ALLOCATION` | STRATEGIC | OPTIONAL | DESIGN_VARIABLE | COLLECTION | count/value/collection | SCENARIO/PROJECT_STATE | scope-specific dataset resolution | where relevant and data are available |
| `REGION_PROVENANCE` | PROVENANCE | OPTIONAL | CONTEXT | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |

## 4. Territorial design semantics

State/context variables describe observed or declared conditions. Design/scenario variables describe controllable choices or scenario assumptions. Derived metrics require a declared method. Evaluations require explicit objectives, evidence, provenance, and a human-governed process. No state value automatically becomes an objective, constraint, decision, or project performance metric.

Socioeconomic, productive, environmental, infrastructure, governance, and risk domains are stable semantic domains. They are not ministries, agencies, or automatically authoritative interpretations.

## 5. Temporal semantics

Where relevant, records distinguish observation year, reference period, measurement frequency, scenario year, validity period, and retrieval time. Historical/observed values are not silently compared with projected/scenario values. Incompatible years remain `MISSING`, `UNKNOWN`, or `NOT_AVAILABLE` as appropriate.

## 6. Spatial resolution

`SpatialScope = region` is not identical to dataset spatial resolution. A region project may use finer or coarser datasets when the resolution, aggregation, provenance, and limitations are explicit. No GIS implementation is created.

## 7. Conditional applicability and provenance

Variables apply only where the design question, typology, context, stage, available data, and objectives justify them. `NOT_APPLICABLE` is distinct from `NOT_AVAILABLE`; `ZERO` is distinct from `MISSING`; `MISSING` is distinct from `UNKNOWN`; `NOT_AVAILABLE` is distinct from `ASSUMED`.

Each record requires source-class and evidence metadata when populated. No external source claim or value is loaded in this specification.

## 8. Design Knowledge and regulatory relationship

Design Knowledge may provide patterns, strategies, or questions for territorial analysis, but it does not create project values. Regulation follows `Regulation → Evidence/Interpretation → Constraint → project relation`; a rule is not automatically a project variable value or Decision. Human Authority is preserved.

## 9. Scale-specific design/scenario candidates

Candidate interventions include spatial structure, service/facility networks, mobility and transport corridors, housing strategies, green/ecological networks, infrastructure portfolios, productive corridors, risk reduction, water and energy strategies, and public investment scenarios. These candidates are not mandatory variables.

## 10. Gate

`REGION_VARIABLE_COUNT = 32`
`REGION_MINIMUM_COUNT = 16`
`REGION_COMPLETE_COUNT = 32`
`TERRITORIAL_STATE_DESIGN_SEPARATION = PASS`
`SOCIOECONOMIC_VARIABLE_MODEL = PASS`
`PRODUCTIVE_SECTOR_MODEL = PASS`
`TEMPORAL_SEMANTICS = PASS`
`SPATIAL_RESOLUTION_SEMANTICS = PASS`
`CONDITIONAL_APPLICABILITY = PASS`
`PROVENANCE = PASS`
`HUMAN_AUTHORITY = PASS`
`PRODUCT_IMPLEMENTATION = NO`

**Status:** MV-P0.10 specification PASS.

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SiMS-DeI SICL Core repository"
