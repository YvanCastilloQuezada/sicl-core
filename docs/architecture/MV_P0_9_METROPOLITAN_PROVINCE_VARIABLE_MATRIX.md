# MV-P0.9 — Province / Metropolis Variable Matrix

**SpatialScope:** `provincia_metropoli`
**Status:** SPECIFICATION ONLY
**Product implementation:** NOT AUTHORIZED

## 1. Scale definition

The `provincia_metropoli` scale represents territorial design intelligence for province / metropolis. It is not a statistical dashboard. It preserves the design chain: current state/context → problem/opportunity → objectives → constraints → design or scenario variables → alternatives/scenarios → analysis → derived metrics → evaluation → trade-offs/Pareto where appropriate → HumanReview → Decision.

The matrix uses stable semantic domains rather than current government institutions. Domain is not government institution. No external sources are mapped in this batch.

## 2. Minimum and recommended profiles

The minimum profile contains **14 records**. The recommended complete profile contains **28 records**. The remaining records are conditional or recommended by project typology, context, stage, available data, and objectives. The count is not an optimization target.

## 3. Matrix contract

| ID | Domain | Requirement | Role | Type | Unit semantics | Temporal semantics | Spatial resolution | Applicability |
|---|---|---|---|---|---|---|---|---|
| `METROPOLITAN_PROVINCE_TERRITORIAL_BOUNDARY` | TERRITORIAL | REQUIRED | CONTEXT | GEOMETRY | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_COMPONENT_DISTRICTS` | COMPONENT | REQUIRED | CONTEXT | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_POPULATION` | POPULATION | REQUIRED | STATE | DECIMAL | domain-specific unit | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_POPULATION_GROWTH` | POPULATION | REQUIRED | DERIVED_METRIC | DECIMAL | domain-specific unit | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_MIGRATION` | MIGRATION | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_SETTLEMENT_DISTRIBUTION` | SETTLEMENT | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_URBAN_HIERARCHY` | URBAN | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_CENTERS_SUBCENTERS` | CENTERS | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_METROPOLITAN_EXPANSION` | METROPOLITAN | REQUIRED | DERIVED_METRIC | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_ECONOMIC_ACTIVITY` | ECONOMIC | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_EMPLOYMENT` | EMPLOYMENT | REQUIRED | STATE | DECIMAL | domain-specific unit | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_HOUSING_DEFICIT` | HOUSING | REQUIRED | DERIVED_METRIC | DECIMAL | domain-specific unit | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_LAND_AVAILABILITY` | LAND | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_AFFORDABILITY` | AFFORDABILITY | REQUIRED | DERIVED_METRIC | DECIMAL | domain-specific unit | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_ORIGIN_DESTINATION` | ORIGIN | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_METROPOLITAN_TRANSPORT` | METROPOLITAN | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_FREIGHT_FLOWS` | FREIGHT | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_TRANSPORT_CORRIDORS` | TRANSPORT | RECOMMENDED | CONTEXT | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_LOGISTICS_HUBS` | LOGISTICS | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_HEALTH_NETWORK` | HEALTH | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_EDUCATION_NETWORK` | EDUCATION | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_WATER_SYSTEMS` | WATER | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_ENERGY_SYSTEMS` | ENERGY | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_WATERSHEDS` | WATERSHEDS | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_MULTIHAZARD_EXPOSURE` | MULTIHAZARD | OPTIONAL | DERIVED_METRIC | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_CRITICAL_INFRASTRUCTURE` | CRITICAL | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_RESILIENCE` | RESILIENCE | OPTIONAL | DERIVED_METRIC | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `METROPOLITAN_PROVINCE_MAJOR_PROJECTS` | MAJOR | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |

## 4. Territorial design semantics

State/context variables describe observed or declared conditions. Design/scenario variables describe controllable choices or scenario assumptions. Derived metrics require a declared method. Evaluations require explicit objectives, evidence, provenance, and a human-governed process. No state value automatically becomes an objective, constraint, decision, or project performance metric.

Socioeconomic, productive, environmental, infrastructure, governance, and risk domains are stable semantic domains. They are not ministries, agencies, or automatically authoritative interpretations.

## 5. Temporal semantics

Where relevant, records distinguish observation year, reference period, measurement frequency, scenario year, validity period, and retrieval time. Historical/observed values are not silently compared with projected/scenario values. Incompatible years remain `MISSING`, `UNKNOWN`, or `NOT_AVAILABLE` as appropriate.

## 6. Spatial resolution

`SpatialScope = provincia_metropoli` is not identical to dataset spatial resolution. A provincia_metropoli project may use finer or coarser datasets when the resolution, aggregation, provenance, and limitations are explicit. No GIS implementation is created.

## 7. Conditional applicability and provenance

Variables apply only where the design question, typology, context, stage, available data, and objectives justify them. `NOT_APPLICABLE` is distinct from `NOT_AVAILABLE`; `ZERO` is distinct from `MISSING`; `MISSING` is distinct from `UNKNOWN`; `NOT_AVAILABLE` is distinct from `ASSUMED`.

Each record requires source-class and evidence metadata when populated. No external source claim or value is loaded in this specification.

## 8. Design Knowledge and regulatory relationship

Design Knowledge may provide patterns, strategies, or questions for territorial analysis, but it does not create project values. Regulation follows `Regulation → Evidence/Interpretation → Constraint → project relation`; a rule is not automatically a project variable value or Decision. Human Authority is preserved.

## 9. Scale-specific design/scenario candidates

Candidate interventions include spatial structure, service/facility networks, mobility and transport corridors, housing strategies, green/ecological networks, infrastructure portfolios, productive corridors, risk reduction, water and energy strategies, and public investment scenarios. These candidates are not mandatory variables.

## 10. Gate

`METROPOLITAN_PROVINCE_VARIABLE_COUNT = 28`
`METROPOLITAN_PROVINCE_MINIMUM_COUNT = 14`
`METROPOLITAN_PROVINCE_COMPLETE_COUNT = 28`
`TERRITORIAL_STATE_DESIGN_SEPARATION = PASS`
`SOCIOECONOMIC_VARIABLE_MODEL = PASS`
`PRODUCTIVE_SECTOR_MODEL = PASS`
`TEMPORAL_SEMANTICS = PASS`
`SPATIAL_RESOLUTION_SEMANTICS = PASS`
`CONDITIONAL_APPLICABILITY = PASS`
`PROVENANCE = PASS`
`HUMAN_AUTHORITY = PASS`
`PRODUCT_IMPLEMENTATION = NO`

**Status:** MV-P0.9 specification PASS.

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SiMS-DeI SICL Core repository"
