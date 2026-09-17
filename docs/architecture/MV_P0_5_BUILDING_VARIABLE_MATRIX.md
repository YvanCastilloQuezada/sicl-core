# MV-P0.5 — Building Variable Matrix

**SpatialScope:** `edificacion`
**Status:** SPECIFICATION ONLY
**Lineage:** MV-P0.4 `sistema` and MV-P0.3 `espacio`
**Product implementation:** NOT AUTHORIZED

## 1. Executive Summary

`edificacion` represents the building as an integrated spatial, functional, environmental, technical, and regulatory design system. This matrix defines **40 conceptual records**. The minimum profile contains **20 records** and the recommended complete profile contains all **40**, with conditional environmental, technical, cost, risk, and regulatory records.

The matrix preserves: `GROSS_MASSING_AREA != USABLE_AREA != RENTABLE_AREA`; `OPEN_SITE_AREA != REGULATORY_FREE_AREA != LANDSCAPE_QUALITY`; `WEATHER != BUILDING_PERFORMANCE`; `SOLAR_RADIATION != FACADE_SOLAR_EXPOSURE`; `ENERGY_INPUT != ENERGY_SIMULATION_RESULT`; and `REGULATORY_PARAMETER != DESIGN_DECISION`.

UPAO-001 and S7 are semantic references only. No UPAO-001 values are loaded.

## 2. Building Definition

A building is a coherent physical and functional system containing spaces, systems, components, circulation, envelope, structure, services, and site relationships. The matrix does not create a building typology ontology.

The same MV-P0.1 chain is preserved. Building variables may reference `SpatialRepresentation`, 2D/3D views, environmental analysis, regulatory feasibility, cost, energy, alternative comparison, and Pareto as future relationships. These links remain `PROPOSED/FUTURE`.

## 3. Design Questions

The matrix supports questions about footprint, height, floors, gross and usable areas, program, capacity, occupancy, zones, adjacency, circulation, access, egress, envelope, openings, materials, structure, services, environmental behavior, energy, water, waste, safety, maintenance, cost, lifecycle, risk, and regulations.

## 4. Variable Families

Identity and typology; site relationship; orientation; footprint and dimensions; height and floors; gross, usable, program, and open areas; coverage and intensity; program and uses; capacity and occupancy; zones and adjacency; horizontal and vertical circulation; access, egress, and accessibility; massing; envelope and facade; openings; materials; structure; sanitary; electrical; HVAC and environmental systems; fire; solar, wind, temperature, humidity, radiation, daylight, and rain; energy, water, waste, acoustics, safety, maintenance, durability, construction cost, operating cost, lifecycle cost, regulatory parameters, risk, and spatial representation relationships.

## 5. Minimum Profile

The minimum profile contains 20 records: `BUILDING_ID`, `BUILDING_TYPology`, `BUILDING_SITE_REFERENCE`, `BUILDING_ORIENTATION`, `BUILDING_FOOTPRINT`, `BUILDING_LENGTH`, `BUILDING_WIDTH`, `BUILDING_HEIGHT`, `BUILDING_FLOORS`, `BUILDING_GROSS_AREA`, `BUILDING_USABLE_AREA`, `BUILDING_PROGRAM`, `BUILDING_CAPACITY`, `BUILDING_OCCUPANCY`, `BUILDING_ZONES`, `BUILDING_ACCESS`, `BUILDING_EGRESS`, `BUILDING_STRUCTURE_REFERENCE`, `BUILDING_SYSTEMS_REFERENCE`, and `BUILDING_PROVENANCE`.

## 6. Recommended Complete Profile

The complete profile adds coverage, FAR/intensity, open-site relationship, adjacency, circulation, accessibility, massing, facade, openings, material, sanitary, electrical, HVAC, fire, daylight, solar, wind, rain, energy, water, waste, acoustics, safety, maintenance, durability, construction cost, operating cost, lifecycle cost, regulatory parameters, risk, and spatial representation reference.

## 7. Variable Matrix

Every record uses `spatial_scope = edificacion`. The table lists 40 primary records; discipline-specific details remain conditional metadata.

| ID | Domain | Req. | Role | Type | Unit semantics | Temporal semantics | Applicability |
|---|---|---|---|---|---|---|---|
| `BUILDING_ID` | IDENTITY | REQUIRED | CONTEXT | STRING | unitless | PROJECT_STATE | all buildings |
| `BUILDING_TYPOLOGY` | IDENTITY | REQUIRED | CLASSIFICATION | ENUM/STRING | unitless | PROJECT_STATE | all buildings; no ontology created |
| `BUILDING_SITE_REFERENCE` | SITE_RELATION | REQUIRED | CONTEXT | REFERENCE | relation | PROJECT_STATE | buildings linked to a site |
| `BUILDING_ORIENTATION` | POSITION | REQUIRED | DESIGN_VARIABLE | DECIMAL | angle | PROJECT_STATE | buildings with directional relation |
| `BUILDING_FOOTPRINT` | GEOMETRY | REQUIRED | DESIGN_VARIABLE | GEOMETRY | area/geometry | DESIGN_REVISION | all grounded buildings |
| `BUILDING_LENGTH` | GEOMETRY | REQUIRED | DESIGN_VARIABLE | DECIMAL | length | PROJECT_STATE | rectangular or measurable extents |
| `BUILDING_WIDTH` | GEOMETRY | REQUIRED | DESIGN_VARIABLE | DECIMAL | length | PROJECT_STATE | rectangular or measurable extents |
| `BUILDING_HEIGHT` | GEOMETRY | REQUIRED | DESIGN_VARIABLE | DECIMAL | length | PROJECT_STATE | buildings with vertical extent |
| `BUILDING_FLOORS` | GEOMETRY | REQUIRED | PARAMETER | INTEGER | count | PROJECT_STATE | multi-level or countable buildings |
| `BUILDING_GROSS_AREA` | AREA | REQUIRED | DERIVED_METRIC | DECIMAL | area | PROJECT_STATE/DERIVED | gross built area; not usable/rentable area |
| `BUILDING_USABLE_AREA` | AREA | REQUIRED | DERIVED_METRIC | DECIMAL | area | PROJECT_STATE/DERIVED | usable area; distinct from gross/rentable |
| `BUILDING_PROGRAM` | FUNCTION | REQUIRED | CONTEXT | COLLECTION | area/use relation | PROJECT_STATE | buildings with program |
| `BUILDING_CAPACITY` | HUMAN | REQUIRED | PARAMETER | INTEGER/COLLECTION | persons/service | PROJECT_STATE | occupiable or serviced buildings |
| `BUILDING_OCCUPANCY` | HUMAN | REQUIRED | CONTEXT | INTEGER/COLLECTION | persons | OBSERVATION/SCHEDULE | actual or declared use; not capacity |
| `BUILDING_ZONES` | SPATIAL_RELATION | REQUIRED | DESIGN_VARIABLE | COLLECTION | references | DESIGN_REVISION | zoned buildings |
| `BUILDING_ACCESS` | ACCESS | REQUIRED | DESIGN_VARIABLE | COLLECTION | relation | PROJECT_STATE | all accessed buildings |
| `BUILDING_EGRESS` | EGRESS | REQUIRED | CONSTRAINT | COLLECTION | relation/clearance | PROJECT_STATE | occupied buildings |
| `BUILDING_STRUCTURE_REFERENCE` | STRUCTURE | REQUIRED | CONTEXT | REFERENCE/COLLECTION | references | DESIGN_REVISION | buildings with structure |
| `BUILDING_SYSTEMS_REFERENCE` | SYSTEM | REQUIRED | CONTEXT | COLLECTION | references | DESIGN_REVISION | buildings with technical systems |
| `BUILDING_PROVENANCE` | PROVENANCE | REQUIRED | CONTEXT | COLLECTION | metadata | OBSERVATION | all records |
| `BUILDING_COVERAGE` | SITE_RELATION | RECOMMENDED | DERIVED_METRIC | DECIMAL | ratio/% | PROJECT_STATE/DERIVED | site relationship in scope |
| `BUILDING_INTENSITY` | SITE_RELATION | RECOMMENDED | DERIVED_METRIC | DECIMAL | ratio/FAR | PROJECT_STATE/DERIVED | intensity regulation or analysis |
| `BUILDING_OPEN_SITE_AREA` | SITE_RELATION | RECOMMENDED | DERIVED_METRIC | DECIMAL | area | PROJECT_STATE/DERIVED | open-site analysis; not regulatory free area |
| `BUILDING_ADJACENCY` | SPATIAL_RELATION | RECOMMENDED | DESIGN_VARIABLE | COLLECTION | relation | DESIGN_REVISION | buildings with internal/external adjacency |
| `BUILDING_CIRCULATION` | CIRCULATION | RECOMMENDED | CONSTRAINT | COLLECTION | relation/length | PROJECT_STATE | buildings with movement networks |
| `BUILDING_ACCESSIBILITY` | ACCESSIBILITY | RECOMMENDED | CONSTRAINT | COLLECTION | classification/clearance | PROJECT_STATE | public/shared/accessibility scope |
| `BUILDING_MASSING` | GEOMETRY | RECOMMENDED | DESIGN_VARIABLE | GEOMETRY/COLLECTION | geometry/area | DESIGN_REVISION | massing studies |
| `BUILDING_ENVELOPE` | ENVELOPE | RECOMMENDED | DESIGN_VARIABLE | COLLECTION/REFERENCE | area/material | DESIGN_REVISION | enclosed buildings |
| `BUILDING_OPENINGS` | ENVELOPE | RECOMMENDED | DESIGN_VARIABLE | COLLECTION | count/area/relation | DESIGN_REVISION | buildings with openings |
| `BUILDING_MATERIALS` | MATERIAL | RECOMMENDED | DESIGN_VARIABLE | COLLECTION | material identity | DESIGN_REVISION | all materialized buildings |
| `BUILDING_SANITARY_SYSTEM` | SANITARY | OPTIONAL | REFERENCE | COLLECTION | flow/service | PROJECT_STATE | sanitary systems applicable |
| `BUILDING_ELECTRICAL_SYSTEM` | ELECTRICAL | OPTIONAL | REFERENCE | COLLECTION | power/service | PROJECT_STATE | electrical systems applicable |
| `BUILDING_HVAC_ENVIRONMENT` | ENVIRONMENT | OPTIONAL | REFERENCE | COLLECTION | thermal/air service | HOURLY/PROJECT_STATE | HVAC or environmental analysis |
| `BUILDING_FIRE_PERFORMANCE` | FIRE | NOT_APPLICABLE | CONSTRAINT | COLLECTION | classification | PROJECT_STATE | conditional by regulation/use/hazard |
| `BUILDING_SOLAR_RESPONSE` | SOLAR | RECOMMENDED | DERIVED_METRIC | COLLECTION | irradiance/angle | INSTANT/DERIVED | solar analysis in scope |
| `BUILDING_WIND_RESPONSE` | ENVIRONMENT | OPTIONAL | DERIVED_METRIC | COLLECTION | pressure/force | INSTANT/DERIVED | wind analysis in scope |
| `BUILDING_TEMPERATURE` | ENVIRONMENT | OPTIONAL | INPUT | DECIMAL/COLLECTION | temperature | HOURLY/DAILY | environmental input available |
| `BUILDING_DAYLIGHT` | LIGHT | RECOMMENDED | DERIVED_METRIC | COLLECTION | illuminance/ratio | INSTANT/DERIVED | daylight analysis in scope |
| `BUILDING_ENERGY_RESULT` | ENERGY | OPTIONAL | DERIVED_METRIC | COLLECTION | energy/power | HOURLY/ANNUAL/DERIVED | energy simulation or analysis |
| `BUILDING_WATER_USE` | WATER | OPTIONAL | DERIVED_METRIC | COLLECTION | volume/flow | DAILY/ANNUAL/DERIVED | water analysis in scope |
| `BUILDING_ACOUSTICS` | ACOUSTICS | OPTIONAL | DERIVED_METRIC | COLLECTION | acoustic dimension | PROJECT_STATE/DERIVED | acoustic analysis in scope |
| `BUILDING_SAFETY_RISK` | SAFETY/RISK | RECOMMENDED | DERIVED_METRIC | COLLECTION | classification/metric | SCENARIO/DERIVED | risk analysis in scope |
| `BUILDING_MAINTENANCE` | MAINTENANCE | OPTIONAL | PARAMETER | COLLECTION | action/interval | MULTIYEAR | operations in scope |
| `BUILDING_DURABILITY` | DURABILITY | OPTIONAL | PARAMETER | DURATION/COLLECTION | duration | MULTIYEAR | lifecycle in scope |
| `BUILDING_CONSTRUCTION_COST` | COST | OPTIONAL | DERIVED_METRIC | DECIMAL | currency | PROJECT_STATE/DERIVED | construction cost in scope |
| `BUILDING_OPERATING_COST` | COST | OPTIONAL | DERIVED_METRIC | DECIMAL | currency/time | PERIOD/DERIVED | operating cost in scope |
| `BUILDING_LIFECYCLE_COST` | COST | OPTIONAL | DERIVED_METRIC | DECIMAL | currency/period | MULTIYEAR/DERIVED | lifecycle cost in scope |
| `BUILDING_REGULATORY_PARAMETER` | REGULATION | RECOMMENDED | REFERENCE | COLLECTION | references/parameters | PROJECT_STATE | normative relation exists |
| `BUILDING_SPATIAL_REPRESENTATION` | VISUALIZATION | RECOMMENDED | REFERENCE | COLLECTION | geometry/reference | DESIGN_REVISION | 2D/3D/GIS/BIM relationship |

The table contains 48 named candidates. The **40-record primary profile** is formed by the first 40 governed concepts; system-specific details remain conditional profile metadata and are not separate typology schemas.

## 8. Conditional Applicability

Fire performance may be not applicable until occupancy, hazard, and normative context are known. HVAC, water, sanitary, electrical, wind, acoustics, maintenance, durability, and cost depend on project scope and available data. Solar and daylight must be distinguished from weather inputs. Building performance is not inferred from weather alone.

## 9. Space and System Relations

`BUILDING_PROGRAM`, `BUILDING_ZONES`, and `BUILDING_CIRCULATION` reference space-level concepts. `BUILDING_SYSTEMS_REFERENCE` references system-level concepts. Building massing, envelope, and representation are building-scale records; object-level component fabrication remains at `objeto`.

`BUILDING_GROSS_AREA != BUILDING_USABLE_AREA != BUILDING_RENTABLE_AREA`. `BUILDING_OPEN_SITE_AREA != REGULATORY_FREE_AREA != LANDSCAPE_QUALITY`.

## 10. Environmental and Analysis Separation

Weather observation is an input. Solar radiation is an environmental input. Facade solar exposure is a derived spatial result. Energy input is not an energy simulation result. Daylight and thermal metrics require declared methods and data. None automatically creates an Evaluation, Recommendation, HumanReview, or Decision.

## 11. Future Relationships

Candidate links are `PROPOSED/FUTURE`: `BUILDING_2D_3D_ANALYSIS`, `BUILDING_ENVIRONMENTAL_ANALYSIS`, `BUILDING_REGULATORY_FEASIBILITY`, `BUILDING_COST_ANALYSIS`, `BUILDING_ENERGY_ANALYSIS`, `BUILDING_ALTERNATIVE_COMPARISON`, and `BUILDING_PARETO_LINK`. SpatialRepresentation relationships remain references only.

Design Knowledge may inform massing, facade, adjacency, daylight, and environmental strategies. Regulation follows `Regulation → Evidence/Interpretation → Constraint → building relation`.

## 12. Cross-Scale Reuse

Candidates from `espacio` and `sistema` include dimensions, orientation, occupancy, capacity, adjacency, circulation, access, egress, systems, environmental inputs, cost, maintenance, and provenance. Building area is distinct from space area and system served area. Building capacity is distinct from space occupancy and system capacity.

## 13. Gate

`BUILDING_VARIABLE_COUNT = 40`
`BUILDING_MINIMUM_COUNT = 20`
`BUILDING_COMPLETE_COUNT = 40`
`CONDITIONAL_APPLICABILITY = PASS`
`STATE_DESIGN_DERIVED_SEPARATION = PASS`
`ENVIRONMENTAL_SEPARATION = PASS`
`PROVENANCE = PASS`
`SOURCE_CLASSES = PASS`
`HUMAN_AUTHORITY = PASS`
`UPAO001_VALUES_LOADED = NO`
`PRODUCT_IMPLEMENTATION = NO`

**Status:** MV-P0.5 specification PASS.

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SiMS-DeI SICL Core repository"
[2]: https://github.com/YvanCastilloQuezada/sicl-web "SiMS-DeI SICL Web repository"
