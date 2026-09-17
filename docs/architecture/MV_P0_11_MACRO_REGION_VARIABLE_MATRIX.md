# MV-P0.11 — Macro-Region Variable Matrix

**SpatialScope:** `macro_region`
**Status:** SPECIFICATION ONLY
**Product implementation:** NOT AUTHORIZED

## 1. Scale definition

The `macro_region` scale represents territorial design intelligence for macro-region. It is not a statistical dashboard. It preserves the design chain: current state/context → problem/opportunity → objectives → constraints → design or scenario variables → alternatives/scenarios → analysis → derived metrics → evaluation → trade-offs/Pareto where appropriate → HumanReview → Decision.

The matrix uses stable semantic domains rather than current government institutions. Domain is not government institution. No external sources are mapped in this batch.

## 2. Minimum and recommended profiles

The minimum profile contains **15 records**. The recommended complete profile contains **30 records**. The remaining records are conditional or recommended by project typology, context, stage, available data, and objectives. The count is not an optimization target.

## 3. Matrix contract

| ID | Domain | Requirement | Role | Type | Unit semantics | Temporal semantics | Spatial resolution | Applicability |
|---|---|---|---|---|---|---|---|---|
| `MACRO_REGION_COMPONENT_REGIONS` | COMPONENT | REQUIRED | CONTEXT | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_POPULATION` | POPULATION | REQUIRED | STATE | DECIMAL | domain-specific unit | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_POPULATION_FLOWS` | POPULATION | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_MIGRATION` | MIGRATION | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_URBAN_SYSTEMS` | URBAN | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_INTERREGIONAL_HIERARCHY` | INTERREGIONAL | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_AGGREGATE_GVA` | AGGREGATE | REQUIRED | STATE | DECIMAL | domain-specific unit | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_REGIONAL_CONTRIBUTION` | REGIONAL | REQUIRED | DERIVED_METRIC | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_PRODUCTIVE_SPECIALIZATION` | PRODUCTIVE | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_EMPLOYMENT` | EMPLOYMENT | REQUIRED | STATE | DECIMAL | domain-specific unit | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_PRODUCTIVE_CHAINS` | PRODUCTIVE | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_AGRICULTURE` | AGRICULTURE | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_FISHERIES` | FISHERIES | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_MINING` | MINING | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_INDUSTRY` | INDUSTRY | REQUIRED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_TOURISM` | TOURISM | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_INTERREGIONAL_TRADE` | INTERREGIONAL | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_FREIGHT_FLOWS` | FREIGHT | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_PASSENGER_FLOWS` | PASSENGER | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_ECONOMIC_CORRIDORS` | ECONOMIC | RECOMMENDED | CONTEXT | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_LOGISTICS_HUBS` | LOGISTICS | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_ENERGY_FLOWS` | ENERGY | RECOMMENDED | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_WATER_TRANSFERS` | WATER | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_HEALTH_REFERRAL_NETWORKS` | HEALTH | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_EDUCATION_NETWORKS` | EDUCATION | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_ECOLOGICAL_CORRIDORS` | ECOLOGICAL | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_SHARED_HAZARDS` | SHARED | OPTIONAL | DERIVED_METRIC | COLLECTION | count/value/collection | PERIOD/DERIVED | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_STRATEGIC_INFRASTRUCTURE` | STRATEGIC | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_INTERREGIONAL_INVESTMENT` | INTERREGIONAL | OPTIONAL | STATE | COLLECTION | count/value/collection | OBSERVATION/REFERENCE_PERIOD | scope-specific dataset resolution | where relevant and data are available |
| `MACRO_REGION_DEVELOPMENT_SCENARIO` | DEVELOPMENT | OPTIONAL | DESIGN_VARIABLE | COLLECTION | count/value/collection | SCENARIO/PROJECT_STATE | scope-specific dataset resolution | where relevant and data are available |

## 4. Territorial design semantics

State/context variables describe observed or declared conditions. Design/scenario variables describe controllable choices or scenario assumptions. Derived metrics require a declared method. Evaluations require explicit objectives, evidence, provenance, and a human-governed process. No state value automatically becomes an objective, constraint, decision, or project performance metric.

Socioeconomic, productive, environmental, infrastructure, governance, and risk domains are stable semantic domains. They are not ministries, agencies, or automatically authoritative interpretations.

## 5. Temporal semantics

Where relevant, records distinguish observation year, reference period, measurement frequency, scenario year, validity period, and retrieval time. Historical/observed values are not silently compared with projected/scenario values. Incompatible years remain `MISSING`, `UNKNOWN`, or `NOT_AVAILABLE` as appropriate.

## 6. Spatial resolution

`SpatialScope = macro_region` is not identical to dataset spatial resolution. A macro_region project may use finer or coarser datasets when the resolution, aggregation, provenance, and limitations are explicit. No GIS implementation is created.

## 7. Conditional applicability and provenance

Variables apply only where the design question, typology, context, stage, available data, and objectives justify them. `NOT_APPLICABLE` is distinct from `NOT_AVAILABLE`; `ZERO` is distinct from `MISSING`; `MISSING` is distinct from `UNKNOWN`; `NOT_AVAILABLE` is distinct from `ASSUMED`.

Each record requires source-class and evidence metadata when populated. No external source claim or value is loaded in this specification.

## 8. Design Knowledge and regulatory relationship

Design Knowledge may provide patterns, strategies, or questions for territorial analysis, but it does not create project values. Regulation follows `Regulation → Evidence/Interpretation → Constraint → project relation`; a rule is not automatically a project variable value or Decision. Human Authority is preserved.

## 9. Scale-specific design/scenario candidates

Candidate interventions include spatial structure, service/facility networks, mobility and transport corridors, housing strategies, green/ecological networks, infrastructure portfolios, productive corridors, risk reduction, water and energy strategies, and public investment scenarios. These candidates are not mandatory variables.

## 10. Gate

`MACRO_REGION_VARIABLE_COUNT = 30`
`MACRO_REGION_MINIMUM_COUNT = 15`
`MACRO_REGION_COMPLETE_COUNT = 30`
`TERRITORIAL_STATE_DESIGN_SEPARATION = PASS`
`SOCIOECONOMIC_VARIABLE_MODEL = PASS`
`PRODUCTIVE_SECTOR_MODEL = PASS`
`TEMPORAL_SEMANTICS = PASS`
`SPATIAL_RESOLUTION_SEMANTICS = PASS`
`CONDITIONAL_APPLICABILITY = PASS`
`PROVENANCE = PASS`
`HUMAN_AUTHORITY = PASS`
`PRODUCT_IMPLEMENTATION = NO`

**Status:** MV-P0.11 specification PASS.

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SiMS-DeI SICL Core repository"
