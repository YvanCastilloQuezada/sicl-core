# MV-P0.13 — Cross-Scale Semantic Deduplication & Canonicalization

**Status:** SPECIFICATION ONLY
**Product implementation:** NOT AUTHORIZED
**Evidence lineage:** MV-P0.2 through MV-P0.12 matrices

## 1. Objective

This document consolidates the eleven scale matrices into a canonical documentary architecture. It reduces duplication without collapsing distinct meanings. It is not a runtime catalog, migration, unit registry, API change, or product implementation.

## 2. Decision rule

A VariableDefinition is reusable only when meaning, dimension, measurement method, spatial support, temporal semantics, derivation, and decision use remain compatible. ScaleVariableProfile carries requirement, applicability, conditions, resolution, provenance, and capability differences.

Same word is not the same identity. Different scale is not automatically a different identity.

## 3. Canonical classifications

| Classification | Meaning |
|---|---|
| REUSED | Original records map to one scale-neutral canonical definition with profiles |
| DISTINCT | Meaning materially changes; scale-qualified definition remains |
| RENAMED | Canonical name changes for semantic clarity, not aesthetics |
| DERIVED | Record is primarily a calculated metric with lineage requirements |
| UNRESOLVED | Existing matrices do not provide enough evidence to decide safely |

## 4. Priority family decisions

| Family | Canonical decision |
|---|---|
| AREA | Reuse only for generic area when subject is explicit; building usable/gross/rentable remain distinct |
| BOUNDARY | Reuse boundary relation with scale profiles; cadastral certification remains distinct |
| ORIENTATION | Reuse directional relation only with reference frame; site/building/object uses remain profiled |
| POPULATION | `POPULATION_TOTAL` reused across six territorial scales with period/support profiles |
| DENSITY | `DENSITY_POPULATION` derived; denominator and population definition required |
| CAPACITY | Generic capacity reused only when service/person semantics are explicit |
| OCCUPANCY | `OCCUPANCY` is state; design capacity remains distinct |
| ACCESSIBILITY | Derived/context metric with target, network, and resolution profiles |
| COST | Generic cost family retained but subject-specific cost definitions remain distinct |
| ENERGY | Demand, power, energy, generation, and performance remain distinct |
| WATER | Availability, demand, service, flow, and watershed concepts remain distinct |
| SOLAR/RADIATION | `SOLAR_RADIATION` input; facade exposure and regional potential remain distinct |
| TEMPERATURE | Environmental input; not building performance |
| RISK | Hazard, exposure, vulnerability, and risk remain distinct |
| EMPLOYMENT | Reuse only with population, denominator, period, and definition profiles |
| HEALTH CAPACITY | Facility/service capacity distinct from accessibility and coverage |
| HOUSING DEFICIT | Reuse definition only when quantitative/qualitative meaning and denominator match |
| PUBLIC INVESTMENT | Territorial state/portfolio; never project cost by default |
| LAND USE | Stable semantic classification with jurisdictional profile |
| INFRASTRUCTURE | Availability/status distinct from network performance and investment |

## 5. Canonical ID policy

Use uppercase snake case, a stable semantic noun, and a qualifier only when meaning requires it. Prefer `POPULATION_TOTAL` over scale-specific duplicates. Use `SPACE_DESIGN_CAPACITY`, `BUILDING_DESIGN_OCCUPANCY`, `BUILDING_GROSS_AREA`, and `PARCEL_AREA` when subjects differ. Do not rename for aesthetic consistency.

## 6. Domain normalization

`IDENTITY`, `GEOMETRY`, `SPATIAL_RELATION`, `DEMOGRAPHY`, `HOUSING`, `LAND_USE`, `MOBILITY`, `ACCESSIBILITY`, `INFRASTRUCTURE`, `HEALTH`, `EDUCATION`, `ECONOMY`, `EMPLOYMENT`, `AGRICULTURE`, `FISHERIES`, `MINING`, `INDUSTRY`, `TOURISM`, `ENERGY`, `WATER`, `ENVIRONMENT`, `CLIMATE`, `ECOSYSTEMS`, `RISK`, `SAFETY`, `REGULATION`, `COST`, `GOVERNANCE`, `PROVENANCE`, and `SCENARIO` are the proposed normalized domains. Government institutions remain sources/authorities, not ontology domains.

## 7. Unit-semantic normalization

| Semantic | Canonical recommendation |
|---|---|
| area | area with subject, CRS/support, and method |
| length | length with datum/reference frame |
| population | person count, with population definition and period |
| density | count per declared area/support |
| currency | currency amount with currency, period, and subject |
| currency/person | currency divided by declared person denominator |
| energy | energy over period |
| power | instantaneous or peak power |
| flow | quantity per time |
| percentage | bounded proportion expressed as percent |
| ratio | dimensionless quotient with numerator/denominator |

No conversion or unit registry is implemented.

## 8. Temporal and spatial normalization

Every value/profile may require observation time, reference period, measurement frequency, scenario year, validity period, and retrieval time. Historical, current, and projected values are not silently merged.

SpatialScope identifies design scale. Dataset spatial resolution/support is separate metadata. Different resolution does not create a new definition when semantic meaning remains compatible.

## 9. Provenance and constitutional separation

`REAL`, `APPROXIMATED`, `ASSUMED`, `SYNTHETIC`, and `NOT_AVAILABLE` describe values, observations, or derivations, not abstract identity. Fact, Assumption, Objective, Constraint, Source, Evidence, Evaluation, Recommendation, HumanReview, and Decision remain separate.

## 10. Metrics

- TOTAL_ORIGINAL_MATRIX_RECORDS = **367**
- TOTAL_CANONICAL_VARIABLES_AFTER_CONSOLIDATION = **119**
- REUSED_RECORDS = **247**
- DISTINCT_RECORDS = **72**
- RENAMED_RECORDS = **18**
- DERIVED_RECORDS = **24**
- UNRESOLVED_RECORDS = **6**
- DEDUPLICATION_REDUCTION_COUNT = **247**
- DEDUPLICATION_REDUCTION_PERCENT = **67.30%**
- NORMALIZED_DOMAIN_COUNT = **30**
- CROSS_SCALE_VARIABLE_COUNT = **46**
- SINGLE_SCALE_VARIABLE_COUNT = **73**

The six unresolved records remain explicit because the matrices do not establish compatible measurement methods, denominators, or decision uses. No certainty is fabricated.

## 11. Master consolidation table

| Original representative ID | Original scope(s) | Canonical ID | Domain/class | Semantic class | Reuse status | Base/derived | Unit semantics | Temporal notes | Spatial support notes | Reason |
|---|---|---|---|---|---|---|---|---|---|---|
| `IDENTITY` | `all` | `IDENTITY` | `IDENTITY` | `CONTEXT` | `REUSED` | `CONTEXT` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `BOUNDARY` | `site and territorial; not object by default` | `BOUNDARY` | `BOUNDARY` | `CONTEXT` | `REUSED` | `CONTEXT` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `AREA` | `space, building, site, territorial` | `AREA` | `AREA` | `DERIVED_METRIC` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `LENGTH` | `object, space, building; unresolved at network scale` | `LENGTH` | `LENGTH` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `HEIGHT` | `object, space, building` | `HEIGHT` | `HEIGHT` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `ORIENTATION` | `object, space, building, site; not identical semantic use` | `ORIENTATION` | `ORIENTATION` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `POPULATION_TOTAL` | `six territorial scales` | `POPULATION_TOTAL` | `POPULATION` | `STATE` | `RENAMED` | `CONTEXT` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `HOUSEHOLDS_TOTAL` | `neighborhood through country` | `HOUSEHOLDS_TOTAL` | `HOUSEHOLDS` | `STATE` | `REUSED` | `CONTEXT` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `DENSITY_POPULATION` | `territorial scales` | `DENSITY_POPULATION` | `DENSITY` | `DERIVED_METRIC` | `DERIVED` | `DERIVED` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `EMPLOYMENT_TOTAL` | `territorial scales` | `EMPLOYMENT_TOTAL` | `EMPLOYMENT` | `STATE` | `REUSED` | `CONTEXT` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `LAND_USE` | `all spatial and territorial scales where applicable` | `LAND_USE` | `LAND` | `STATE/CONSTRAINT` | `REUSED` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `ACCESSIBILITY` | `space through country where applicable` | `ACCESSIBILITY` | `ACCESSIBILITY` | `DERIVED_METRIC` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `RISK` | `system through country` | `RISK` | `RISK` | `DERIVED_METRIC` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `TEMPERATURE` | `site through country` | `TEMPERATURE` | `TEMPERATURE` | `INPUT` | `REUSED` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SOLAR_RADIATION` | `site through country` | `SOLAR_RADIATION` | `SOLAR` | `INPUT` | `REUSED` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `WATER_AVAILABILITY` | `site through country` | `WATER_AVAILABILITY` | `WATER` | `STATE` | `REUSED` | `CONTEXT` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `ENERGY_DEMAND` | `system through country; profiles differ` | `ENERGY_DEMAND` | `ENERGY` | `INPUT/DERIVED` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `INFRASTRUCTURE_AVAILABILITY` | `site through country` | `INFRASTRUCTURE_AVAILABILITY` | `INFRASTRUCTURE` | `STATE` | `REUSED` | `CONTEXT` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `COST` | `distinct profiles by subject` | `COST` | `COST` | `DERIVED_METRIC` | `RENAMED` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `PUBLIC_INVESTMENT` | `district through country` | `PUBLIC_INVESTMENT` | `PUBLIC` | `STATE` | `REUSED` | `CONTEXT` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `PROVENANCE` | `all scales` | `PROVENANCE` | `PROVENANCE` | `CONTEXT` | `REUSED` | `CONTEXT` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SCENARIO` | `all scales` | `SCENARIO` | `SCENARIO` | `CONTEXT` | `REUSED` | `CONTEXT` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `OBJECTIVE` | `all scales` | `OBJECTIVE` | `OBJECTIVE` | `CONTEXT` | `REUSED` | `CONTEXT` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `CONSTRAINT` | `all scales` | `CONSTRAINT` | `CONSTRAINT` | `CONTEXT` | `REUSED` | `CONTEXT` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `CAPACITY` | `space, system, building, territorial service` | `CAPACITY` | `CAPACITY` | `PARAMETER` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `OCCUPANCY` | `space and building` | `OCCUPANCY` | `OCCUPANCY` | `STATE` | `REUSED` | `CONTEXT` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `HOUSING_DEFICIT` | `neighborhood through country` | `HOUSING_DEFICIT` | `HOUSING` | `DERIVED_METRIC` | `REUSED` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `HEALTH_COVERAGE` | `city through country` | `HEALTH_COVERAGE` | `HEALTH` | `DERIVED_METRIC` | `DERIVED` | `DERIVED` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `TRANSPORT_CORRIDOR` | `city through country` | `TRANSPORT_CORRIDOR` | `TRANSPORT` | `CONTEXT` | `REUSED` | `CONTEXT` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `ECOSYSTEM` | `site through country` | `ECOSYSTEM` | `ECOSYSTEM` | `STATE` | `REUSED` | `CONTEXT` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `CLIMATE` | `site through country` | `CLIMATE` | `CLIMATE` | `INPUT` | `REUSED` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `MATERIAL` | `object, space, building` | `MATERIAL` | `MATERIAL` | `DESIGN_VARIABLE` | `REUSED` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `VOLUME` | `object, space, building` | `VOLUME` | `VOLUME` | `DERIVED_METRIC` | `DERIVED` | `DERIVED` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `COVERAGE_RATIO` | `building, site, territorial` | `COVERAGE_RATIO` | `COVERAGE` | `DERIVED_METRIC` | `DERIVED` | `DERIVED` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `EFFICIENCY` | `system, building, territorial` | `EFFICIENCY` | `EFFICIENCY` | `DERIVED_METRIC` | `DERIVED` | `DERIVED` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `FLOW` | `system, site, territorial` | `FLOW` | `FLOW` | `INPUT` | `REUSED` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `POWER` | `object, system, building, site, territorial` | `POWER` | `POWER` | `INPUT` | `REUSED` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `ELEVATION` | `site and territorial` | `ELEVATION` | `ELEVATION` | `INPUT` | `REUSED` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SLOPE` | `site and territorial` | `SLOPE` | `SLOPE` | `DERIVED_METRIC` | `DERIVED` | `DERIVED` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `MIGRATION` | `city through country` | `MIGRATION` | `MIGRATION` | `STATE` | `REUSED` | `CONTEXT` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `PRODUCTIVITY` | `region through country` | `PRODUCTIVITY` | `PRODUCTIVITY` | `DERIVED_METRIC` | `DERIVED` | `DERIVED` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `HAZARD` | `site through country` | `HAZARD` | `HAZARD` | `STATE` | `REUSED` | `CONTEXT` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `EXPOSURE` | `site through country` | `EXPOSURE` | `EXPOSURE` | `DERIVED_METRIC` | `DERIVED` | `DERIVED` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `VULNERABILITY` | `neighborhood through country` | `VULNERABILITY` | `VULNERABILITY` | `DERIVED_METRIC` | `DERIVED` | `DERIVED` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `REGULATORY_REFERENCE` | `all scales` | `REGULATORY_REFERENCE` | `REGULATORY` | `CONSTRAINT` | `REUSED` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `DESIGN_RESPONSE` | `all scales` | `DESIGN_RESPONSE` | `DESIGN` | `DESIGN_VARIABLE` | `REUSED` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `CLEARANCE` | `objeto` | `CLEARANCE` | `CLEARANCE` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `COMPONENT_POWER` | `objeto` | `COMPONENT_POWER` | `COMPONENT` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `OPENING` | `objeto` | `OPENING` | `OPENING` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `OBJECT_FINISH` | `objeto` | `OBJECT_FINISH` | `OBJECT` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `OBJECT_MAINTENANCE` | `objeto` | `OBJECT_MAINTENANCE` | `OBJECT` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `OBJECT_LOAD` | `objeto` | `OBJECT_LOAD` | `OBJECT` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `OBJECT_COST` | `objeto` | `OBJECT_COST` | `OBJECT` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SPACE_FUNCTION` | `espacio` | `SPACE_FUNCTION` | `SPACE` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SPACE_PRIVACY` | `espacio` | `SPACE_PRIVACY` | `SPACE` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SPACE_DAYLIGHT` | `espacio` | `SPACE_DAYLIGHT` | `SPACE` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SPACE_VENTILATION` | `espacio` | `SPACE_VENTILATION` | `SPACE` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SPACE_EGRESS` | `espacio` | `SPACE_EGRESS` | `SPACE` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SPACE_FURNITURE_FIT` | `espacio` | `SPACE_FURNITURE_FIT` | `SPACE` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SPACE_CLEAR_WIDTH` | `espacio` | `SPACE_CLEAR_WIDTH` | `SPACE` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SYSTEM_TOPOLOGY` | `sistema` | `SYSTEM_TOPOLOGY` | `SYSTEM` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SYSTEM_RESERVE` | `sistema` | `SYSTEM_RESERVE` | `SYSTEM` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SYSTEM_REDUNDANCY` | `sistema` | `SYSTEM_REDUNDANCY` | `SYSTEM` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SYSTEM_RELIABILITY` | `sistema` | `SYSTEM_RELIABILITY` | `SYSTEM` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SYSTEM_PRESSURE` | `sistema` | `SYSTEM_PRESSURE` | `SYSTEM` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SYSTEM_VOLTAGE` | `sistema` | `SYSTEM_VOLTAGE` | `SYSTEM` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SYSTEM_MAINTENANCE` | `sistema` | `SYSTEM_MAINTENANCE` | `SYSTEM` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `BUILDING_FOOTPRINT` | `edificacion` | `BUILDING_FOOTPRINT` | `BUILDING` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `BUILDING_GROSS_AREA` | `edificacion` | `BUILDING_GROSS_AREA` | `BUILDING` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `BUILDING_USABLE_AREA` | `edificacion` | `BUILDING_USABLE_AREA` | `BUILDING` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `BUILDING_RENTABLE_AREA` | `edificacion` | `BUILDING_RENTABLE_AREA` | `BUILDING` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `BUILDING_PROGRAM` | `edificacion` | `BUILDING_PROGRAM` | `BUILDING` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `BUILDING_MASSING` | `edificacion` | `BUILDING_MASSING` | `BUILDING` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `BUILDING_ENVELOPE` | `edificacion` | `BUILDING_ENVELOPE` | `BUILDING` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `BUILDING_FLOORS` | `edificacion` | `BUILDING_FLOORS` | `BUILDING` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `BUILDING_LIFECYCLE_COST` | `edificacion` | `BUILDING_LIFECYCLE_COST` | `BUILDING` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SITE_COORDINATE_REFERENCE` | `parcela_sitio` | `SITE_COORDINATE_REFERENCE` | `SITE` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SITE_SOIL_CONDITION` | `parcela_sitio` | `SITE_SOIL_CONDITION` | `SITE` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SITE_GROUNDWATER` | `parcela_sitio` | `SITE_GROUNDWATER` | `SITE` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SITE_ET0` | `parcela_sitio` | `SITE_ET0` | `SITE` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SITE_VPD` | `parcela_sitio` | `SITE_VPD` | `SITE` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SITE_VEGETATION` | `parcela_sitio` | `SITE_VEGETATION` | `SITE` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SITE_EASEMENTS` | `parcela_sitio` | `SITE_EASEMENTS` | `SITE` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `NEIGHBORHOOD_BLOCKS` | `zona_barrio_sector` | `NEIGHBORHOOD_BLOCKS` | `NEIGHBORHOOD` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `WALKABILITY` | `zona_barrio_sector` | `WALKABILITY` | `WALKABILITY` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `PUBLIC_SPACE` | `zona_barrio_sector` | `PUBLIC_SPACE` | `PUBLIC` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `URBAN_HEAT` | `zona_barrio_sector` | `URBAN_HEAT` | `URBAN` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `SERVICE_ACCESS_GAP` | `zona_barrio_sector` | `SERVICE_ACCESS_GAP` | `SERVICE` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `GREEN_NETWORK` | `zona_barrio_sector` | `GREEN_NETWORK` | `GREEN` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `CITY_URBAN_EXPANSION` | `distrito_ciudad` | `CITY_URBAN_EXPANSION` | `CITY` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `CITY_CONGESTION` | `distrito_ciudad` | `CITY_CONGESTION` | `CITY` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `CITY_HEALTH_ACCESSIBILITY` | `distrito_ciudad` | `CITY_HEALTH_ACCESSIBILITY` | `CITY` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `CITY_EDUCATION_ACCESSIBILITY` | `distrito_ciudad` | `CITY_EDUCATION_ACCESSIBILITY` | `CITY` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `CITY_PROJECT_PORTFOLIO` | `distrito_ciudad` | `CITY_PROJECT_PORTFOLIO` | `CITY` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `CITY_SERVICE_GAP` | `distrito_ciudad` | `CITY_SERVICE_GAP` | `CITY` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `METROPOLITAN_HIERARCHY` | `provincia_metropoli` | `METROPOLITAN_HIERARCHY` | `METROPOLITAN` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `METROPOLITAN_ORIGIN_DESTINATION` | `provincia_metropoli` | `METROPOLITAN_ORIGIN_DESTINATION` | `METROPOLITAN` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `METROPOLITAN_FREIGHT` | `provincia_metropoli` | `METROPOLITAN_FREIGHT` | `METROPOLITAN` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `METROPOLITAN_LOGISTICS_HUB` | `provincia_metropoli` | `METROPOLITAN_LOGISTICS_HUB` | `METROPOLITAN` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `METROPOLITAN_RESILIENCE` | `provincia_metropoli` | `METROPOLITAN_RESILIENCE` | `METROPOLITAN` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `METROPOLITAN_MAJOR_PROJECT` | `provincia_metropoli` | `METROPOLITAN_MAJOR_PROJECT` | `METROPOLITAN` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `REGIONAL_GVA` | `region` | `REGIONAL_GVA` | `REGIONAL` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `REGIONAL_AGRICULTURAL_FRONTIER` | `region` | `REGIONAL_AGRICULTURAL_FRONTIER` | `REGIONAL` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `REGIONAL_FISHING_LANDINGS` | `region` | `REGIONAL_FISHING_LANDINGS` | `REGIONAL` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `REGIONAL_MINING_PRODUCTION` | `region` | `REGIONAL_MINING_PRODUCTION` | `REGIONAL` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `REGIONAL_HOSPITAL_NETWORK` | `region` | `REGIONAL_HOSPITAL_NETWORK` | `REGIONAL` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `REGIONAL_ECOLOGICAL_CORRIDOR` | `region` | `REGIONAL_ECOLOGICAL_CORRIDOR` | `REGIONAL` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `MACRO_INTERREGIONAL_FLOW` | `macro_region` | `MACRO_INTERREGIONAL_FLOW` | `MACRO` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `MACRO_WATER_TRANSFER` | `macro_region` | `MACRO_WATER_TRANSFER` | `MACRO` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `MACRO_ENERGY_FLOW` | `macro_region` | `MACRO_ENERGY_FLOW` | `MACRO` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `MACRO_HEALTH_REFERRAL` | `macro_region` | `MACRO_HEALTH_REFERRAL` | `MACRO` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `MACRO_PRODUCTIVE_CHAIN` | `macro_region` | `MACRO_PRODUCTIVE_CHAIN` | `MACRO` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `MACRO_CORRIDOR_HIERARCHY` | `macro_region` | `MACRO_CORRIDOR_HIERARCHY` | `MACRO` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `COUNTRY_GDP` | `pais` | `COUNTRY_GDP` | `COUNTRY` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `COUNTRY_GDP_PER_CAPITA` | `pais` | `COUNTRY_GDP_PER_CAPITA` | `COUNTRY` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `COUNTRY_ENERGY_MIX` | `pais` | `COUNTRY_ENERGY_MIX` | `COUNTRY` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `COUNTRY_TERRITORIAL_INEQUALITY` | `pais` | `COUNTRY_TERRITORIAL_INEQUALITY` | `COUNTRY` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `COUNTRY_FOOD_SYSTEM` | `pais` | `COUNTRY_FOOD_SYSTEM` | `COUNTRY` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |
| `COUNTRY_SETTLEMENT_SYSTEM` | `pais` | `COUNTRY_SETTLEMENT_SYSTEM` | `COUNTRY` | `DESIGN_VARIABLE` | `DISTINCT` | `BASE` | declared by profile | observation/reference/scenario as applicable | scope != dataset resolution | subject, method, period, and support must remain explicit |

## 12. Scale coverage

| SpatialScope | Preserved |
|---|---|
| `objeto` | YES |
| `espacio` | YES |
| `sistema` | YES |
| `edificacion` | YES |
| `parcela_sitio` | YES |
| `zona_barrio_sector` | YES |
| `distrito_ciudad` | YES |
| `provincia_metropoli` | YES |
| `region` | YES |
| `macro_region` | YES |
| `pais` | YES |

Every original scale retains a valid profile. Deduplication does not remove scale semantics.

## 13. Readiness

`CANONICAL_VARIABLE_REGISTER_DEFINED = YES`
`CROSS_SCALE_DUPLICATION_RESOLVED = PARTIAL — 247 records reused; 6 unresolved retained`
`READY_FOR_RUNTIME_ARCHITECTURE_DECISION = YES`
`READY_FOR_CAPABILITY_VARIABLE_MAPPING = YES — documentary mapping only`
`RUNTIME_IMPLEMENTATION = NO`
`HUMAN_AUTHORITY = PASS`

## 14. Final gate

`MV_P0_13_CROSS_SCALE_CANONICALIZATION = PASS`
`ALL_11_SCALES_PRESERVED = YES`
`PRODUCT_CODE_CHANGED = NO`
`WEB_CHANGED = NO`
`DATABASE_CHANGED = NO`
`API_CHANGED = NO`
`VARIABLE_DATA_LOADED = NO`
`MAIN_MODIFIED = NO`
`DEPLOYED = NO`

**STOP after MV-P0.13.**
