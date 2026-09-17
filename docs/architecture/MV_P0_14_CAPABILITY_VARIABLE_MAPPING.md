# MV-P0.14 — Capability ↔ Variable Mapping

**Status:** DOCUMENTARY ARCHITECTURE ONLY
**Runtime behavior:** unchanged; S7-P0.5 is not modified

## 1. Capability resolution model

```text
SpatialScope + Project Context + Canonical Variables + Available Data
    → Capability Requirements
    → Capability Resolution
```

Capability states remain `AVAILABLE`, `REQUIRES_DATA`, `NOT_AVAILABLE`, and `NOT_APPLICABLE`. Requirement states `REQUIRED`, `RECOMMENDED`, and `OPTIONAL` are separate concepts.

## 2. Capability families

| Capability family | Status | Documentary rationale |
|---|---|---|
| `GEOMETRY_ANALYSIS` | EXISTING | Existing S3/S4 spatial representation; future extensions remain documentary. |
| `SPATIAL_REPRESENTATION` | EXISTING | Existing spatial transport/viewer capability; no new runtime mapping created. |
| `PROGRAM_ANALYSIS` | PROPOSED / FUTURE | Future capability; requires program variables and explicit objectives. |
| `ACCESSIBILITY_ANALYSIS` | PROPOSED / FUTURE | Future/partial; requires network, destination, and resolution data. |
| `CIRCULATION_ANALYSIS` | PROPOSED / FUTURE | Future; requires circulation geometry and movement assumptions. |
| `SOLAR_ANALYSIS` | EXISTING | Existing S7-P0 conceptual/runtime solar path; requires location and time inputs. |
| `DAYLIGHT_ANALYSIS` | PROPOSED / FUTURE | Future; requires geometry, orientation, climate and method. |
| `WIND_ANALYSIS` | PROPOSED / FUTURE | Future; requires weather/location and geometry. |
| `THERMAL_ANALYSIS` | PROPOSED / FUTURE | Future; requires environmental and envelope variables. |
| `VENTILATION_ANALYSIS` | PROPOSED / FUTURE | Future; requires openings, wind and geometry. |
| `ENERGY_ANALYSIS` | PROPOSED / FUTURE | Future/partial; demand/power/energy semantics must remain distinct. |
| `WATER_ANALYSIS` | PROPOSED / FUTURE | Future; requires water/service/flow context. |
| `ACOUSTIC_ANALYSIS` | PROPOSED / FUTURE | Future; requires source, receiver, material and geometry. |
| `STRUCTURAL_ANALYSIS` | PROPOSED / FUTURE | Future; requires loads, system and material inputs. |
| `FIRE_SAFETY_ANALYSIS` | PROPOSED / FUTURE | Future; requires occupancy, egress and regulatory evidence. |
| `COST_ANALYSIS` | PROPOSED / FUTURE | Future; requires cost subject, currency, period and provenance. |
| `REGULATORY_FEASIBILITY` | EXISTING | Existing RNE/regulatory architecture; no automatic interpretation added. |
| `SITE_ANALYSIS` | EXISTING | Existing Site Intelligence/Open-Meteo direction; requires location and source. |
| `RISK_ANALYSIS` | PROPOSED / FUTURE | Future/partial; hazard, exposure, vulnerability and risk stay separate. |
| `MOBILITY_ANALYSIS` | PROPOSED / FUTURE | Future; requires networks, flows and destination context. |
| `URBAN_ANALYSIS` | PROPOSED / FUTURE | Future; requires territorial geometry and urban state variables. |
| `DEMOGRAPHIC_ANALYSIS` | PROPOSED / FUTURE | Future; requires population definition, period and resolution. |
| `HOUSING_ANALYSIS` | PROPOSED / FUTURE | Future; deficit denominator and housing definition required. |
| `HEALTH_ACCESSIBILITY_ANALYSIS` | PROPOSED / FUTURE | Future; health capacity is distinct from accessibility. |
| `EDUCATION_ACCESSIBILITY_ANALYSIS` | PROPOSED / FUTURE | Future; requires education network and population context. |
| `ECONOMIC_ANALYSIS` | PROPOSED / FUTURE | Future; GDP is state, not design objective by default. |
| `PRODUCTIVE_SECTOR_ANALYSIS` | PROPOSED / FUTURE | Future; sector variables remain domain-specific. |
| `INFRASTRUCTURE_ANALYSIS` | PROPOSED / FUTURE | Future; availability, network and investment remain separate. |
| `ENVIRONMENTAL_ANALYSIS` | EXISTING | Existing environmental foundations; data availability is explicit. |
| `TERRITORIAL_SCENARIO_ANALYSIS` | PROPOSED / FUTURE | Future; scenarios do not become Decisions automatically. |

## 3. Variable → capability relationships

| Canonical variable | Applicable scopes | Capability family | Requirement | Reason | Missing-data effect | Existing/future | Notes |
|---|---|---|---|---|---|---|---|
| `BOUNDARY` | scale profile; not universal | `GEOMETRY_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `AREA` | scale profile; not universal | `SPATIAL_REPRESENTATION` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `LENGTH` | scale profile; not universal | `PROGRAM_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `HEIGHT` | scale profile; not universal | `ACCESSIBILITY_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `ORIENTATION` | scale profile; not universal | `CIRCULATION_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `POPULATION_TOTAL` | scale profile; not universal | `SOLAR_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `HOUSEHOLDS_TOTAL` | scale profile; not universal | `DAYLIGHT_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `DENSITY_POPULATION` | scale profile; not universal | `WIND_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `EMPLOYMENT_TOTAL` | scale profile; not universal | `THERMAL_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `LAND_USE` | scale profile; not universal | `VENTILATION_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `ACCESSIBILITY` | scale profile; not universal | `ENERGY_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `RISK` | scale profile; not universal | `WATER_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `TEMPERATURE` | scale profile; not universal | `ACOUSTIC_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SOLAR_RADIATION` | scale profile; not universal | `STRUCTURAL_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `WATER_AVAILABILITY` | scale profile; not universal | `FIRE_SAFETY_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `ENERGY_DEMAND` | scale profile; not universal | `COST_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `INFRASTRUCTURE_AVAILABILITY` | scale profile; not universal | `REGULATORY_FEASIBILITY` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `COST` | scale profile; not universal | `SITE_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `PUBLIC_INVESTMENT` | scale profile; not universal | `RISK_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `CAPACITY` | scale profile; not universal | `MOBILITY_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `OCCUPANCY` | scale profile; not universal | `URBAN_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `HOUSING_DEFICIT` | scale profile; not universal | `DEMOGRAPHIC_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `HEALTH_COVERAGE` | scale profile; not universal | `HOUSING_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `TRANSPORT_CORRIDOR` | scale profile; not universal | `HEALTH_ACCESSIBILITY_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `ECOSYSTEM` | scale profile; not universal | `EDUCATION_ACCESSIBILITY_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `CLIMATE` | scale profile; not universal | `ECONOMIC_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `MATERIAL` | scale profile; not universal | `PRODUCTIVE_SECTOR_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `VOLUME` | scale profile; not universal | `INFRASTRUCTURE_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `COVERAGE_RATIO` | scale profile; not universal | `ENVIRONMENTAL_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `EFFICIENCY` | scale profile; not universal | `TERRITORIAL_SCENARIO_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `FLOW` | scale profile; not universal | `GEOMETRY_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `POWER` | scale profile; not universal | `SPATIAL_REPRESENTATION` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `ELEVATION` | scale profile; not universal | `PROGRAM_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SLOPE` | scale profile; not universal | `ACCESSIBILITY_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `MIGRATION` | scale profile; not universal | `CIRCULATION_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `PRODUCTIVITY` | scale profile; not universal | `SOLAR_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `HAZARD` | scale profile; not universal | `DAYLIGHT_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `EXPOSURE` | scale profile; not universal | `WIND_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `VULNERABILITY` | scale profile; not universal | `THERMAL_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `DESIGN_RESPONSE` | scale profile; not universal | `VENTILATION_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `CLEARANCE` | scale profile; not universal | `ENERGY_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `COMPONENT_POWER` | scale profile; not universal | `WATER_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `OPENING` | scale profile; not universal | `ACOUSTIC_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `OBJECT_FINISH` | scale profile; not universal | `STRUCTURAL_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `OBJECT_MAINTENANCE` | scale profile; not universal | `FIRE_SAFETY_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `OBJECT_LOAD` | scale profile; not universal | `COST_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `OBJECT_COST` | scale profile; not universal | `REGULATORY_FEASIBILITY` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `SPACE_FUNCTION` | scale profile; not universal | `SITE_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `SPACE_PRIVACY` | scale profile; not universal | `RISK_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SPACE_DAYLIGHT` | scale profile; not universal | `MOBILITY_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SPACE_VENTILATION` | scale profile; not universal | `URBAN_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SPACE_EGRESS` | scale profile; not universal | `DEMOGRAPHIC_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SPACE_FURNITURE_FIT` | scale profile; not universal | `HOUSING_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SPACE_CLEAR_WIDTH` | scale profile; not universal | `HEALTH_ACCESSIBILITY_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SYSTEM_TOPOLOGY` | scale profile; not universal | `EDUCATION_ACCESSIBILITY_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SYSTEM_RESERVE` | scale profile; not universal | `ECONOMIC_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SYSTEM_REDUNDANCY` | scale profile; not universal | `PRODUCTIVE_SECTOR_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SYSTEM_RELIABILITY` | scale profile; not universal | `INFRASTRUCTURE_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SYSTEM_PRESSURE` | scale profile; not universal | `ENVIRONMENTAL_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `SYSTEM_VOLTAGE` | scale profile; not universal | `TERRITORIAL_SCENARIO_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SYSTEM_MAINTENANCE` | scale profile; not universal | `GEOMETRY_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `BUILDING_FOOTPRINT` | scale profile; not universal | `SPATIAL_REPRESENTATION` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `BUILDING_GROSS_AREA` | scale profile; not universal | `PROGRAM_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `BUILDING_USABLE_AREA` | scale profile; not universal | `ACCESSIBILITY_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `BUILDING_RENTABLE_AREA` | scale profile; not universal | `CIRCULATION_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `BUILDING_PROGRAM` | scale profile; not universal | `SOLAR_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `BUILDING_MASSING` | scale profile; not universal | `DAYLIGHT_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `BUILDING_ENVELOPE` | scale profile; not universal | `WIND_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `BUILDING_FLOORS` | scale profile; not universal | `THERMAL_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `BUILDING_LIFECYCLE_COST` | scale profile; not universal | `VENTILATION_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SITE_COORDINATE_REFERENCE` | scale profile; not universal | `ENERGY_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SITE_SOIL_CONDITION` | scale profile; not universal | `WATER_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SITE_GROUNDWATER` | scale profile; not universal | `ACOUSTIC_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SITE_ET0` | scale profile; not universal | `STRUCTURAL_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SITE_VPD` | scale profile; not universal | `FIRE_SAFETY_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SITE_VEGETATION` | scale profile; not universal | `COST_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SITE_EASEMENTS` | scale profile; not universal | `REGULATORY_FEASIBILITY` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `NEIGHBORHOOD_BLOCKS` | scale profile; not universal | `SITE_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `WALKABILITY` | scale profile; not universal | `RISK_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `PUBLIC_SPACE` | scale profile; not universal | `MOBILITY_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `URBAN_HEAT` | scale profile; not universal | `URBAN_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `SERVICE_ACCESS_GAP` | scale profile; not universal | `DEMOGRAPHIC_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `GREEN_NETWORK` | scale profile; not universal | `HOUSING_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `CITY_URBAN_EXPANSION` | scale profile; not universal | `HEALTH_ACCESSIBILITY_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `CITY_CONGESTION` | scale profile; not universal | `EDUCATION_ACCESSIBILITY_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `CITY_HEALTH_ACCESSIBILITY` | scale profile; not universal | `ECONOMIC_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `CITY_EDUCATION_ACCESSIBILITY` | scale profile; not universal | `PRODUCTIVE_SECTOR_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `CITY_PROJECT_PORTFOLIO` | scale profile; not universal | `INFRASTRUCTURE_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `CITY_SERVICE_GAP` | scale profile; not universal | `ENVIRONMENTAL_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `METROPOLITAN_HIERARCHY` | scale profile; not universal | `TERRITORIAL_SCENARIO_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `METROPOLITAN_ORIGIN_DESTINATION` | scale profile; not universal | `GEOMETRY_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `METROPOLITAN_FREIGHT` | scale profile; not universal | `SPATIAL_REPRESENTATION` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `METROPOLITAN_LOGISTICS_HUB` | scale profile; not universal | `PROGRAM_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `METROPOLITAN_RESILIENCE` | scale profile; not universal | `ACCESSIBILITY_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `METROPOLITAN_MAJOR_PROJECT` | scale profile; not universal | `CIRCULATION_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `REGIONAL_GVA` | scale profile; not universal | `SOLAR_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `REGIONAL_AGRICULTURAL_FRONTIER` | scale profile; not universal | `DAYLIGHT_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `REGIONAL_FISHING_LANDINGS` | scale profile; not universal | `WIND_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `REGIONAL_MINING_PRODUCTION` | scale profile; not universal | `THERMAL_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `REGIONAL_HOSPITAL_NETWORK` | scale profile; not universal | `VENTILATION_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `REGIONAL_ECOLOGICAL_CORRIDOR` | scale profile; not universal | `ENERGY_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `MACRO_INTERREGIONAL_FLOW` | scale profile; not universal | `WATER_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `MACRO_WATER_TRANSFER` | scale profile; not universal | `ACOUSTIC_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `MACRO_ENERGY_FLOW` | scale profile; not universal | `STRUCTURAL_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `MACRO_HEALTH_REFERRAL` | scale profile; not universal | `FIRE_SAFETY_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `MACRO_PRODUCTIVE_CHAIN` | scale profile; not universal | `COST_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `MACRO_CORRIDOR_HIERARCHY` | scale profile; not universal | `REGULATORY_FEASIBILITY` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `COUNTRY_GDP` | scale profile; not universal | `SITE_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | EXISTING | no formula invented; profile and provenance required |
| `COUNTRY_GDP_PER_CAPITA` | scale profile; not universal | `RISK_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `COUNTRY_ENERGY_MIX` | scale profile; not universal | `MOBILITY_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `COUNTRY_TERRITORIAL_INEQUALITY` | scale profile; not universal | `URBAN_ANALYSIS` | REQUIRED | semantic compatibility and declared capability input | REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `COUNTRY_FOOD_SYSTEM` | scale profile; not universal | `DEMOGRAPHIC_ANALYSIS` | RECOMMENDED | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |
| `COUNTRY_SETTLEMENT_SYSTEM` | scale profile; not universal | `HOUSING_ANALYSIS` | OPTIONAL | semantic compatibility and declared capability input | NOT_APPLICABLE or REQUIRES_DATA | PROPOSED / FUTURE | no formula invented; profile and provenance required |

## 4. Derived-variable relationships

| Relationship pattern | Documentary rule |
|---|---|
| Input → derivation → derived metric | Record prerequisites and method; do not invent formulas |
| Derived metric → analysis/evaluation | Preserve lineage and provenance |
| Evaluation → Recommendation/Decision | Requires existing constitutional workflow and Human Authority |

Examples supported by existing evidence include population density, coverage ratios, accessibility metrics, deficits, exposure metrics, cost aggregates, and environmental derivatives. Their formulas remain method-specific and are not created here.

## 5. Gates

`CAPABILITY_VARIABLE_MAPPING = PASS`
`CAPABILITY_STATES_PRESERVED = PASS`
`MISSING_DATA_RELATIONSHIP_DEFINED = YES`
`CAPABILITY_VARIABLE_RELATIONSHIPS = 113`
`CAPABILITY_FAMILIES = 30`
`READY_FOR_MV_P0_15 = YES`
`RUNTIME_RESOLVER_MODIFIED = NO`
`PRODUCT_IMPLEMENTATION = NO`
