# MV-P0.6 — Parcel/Site Variable Matrix

**SpatialScope:** `parcela_sitio`
**Status:** SPECIFICATION ONLY
**Lineage:** MV-P0.5 `edificacion`, MV-P0.4 `sistema`, MV-P0.3 `espacio`
**Product implementation:** NOT AUTHORIZED

## 1. Executive Summary

`parcela_sitio` represents the physical, environmental, infrastructural, contextual, and regulatory site that receives or relates to a design intervention. This matrix defines **40 conceptual records**. The minimum profile contains **20 records** and the recommended complete profile contains all **40**, with conditional GIS, cadastral, environmental, infrastructure, hazard, and regulatory variables.

The matrix preserves:

```text
PARCEL_AREA != BUILDING_FOOTPRINT
SITE_ORIENTATION != BUILDING_ORIENTATION
WEATHER_OBSERVATION != SITE_DESIGN_RESPONSE
FLOOD_HAZARD != FLOOD_DESIGN_DECISION
ZONING_RULE != PROJECT_VARIABLE_VALUE
TOPOGRAPHIC_DATA != SURVEY_CERTIFICATION
ENVIRONMENTAL_REFERENCE_LOCATION != CADASTRAL_LOCATION
```

Future GIS relationships are conceptual only. GIS is not implemented and no real cadastral data are loaded.

## 2. Site Definition

A parcel/site is a spatially bounded or operationally defined physical context for design. It may include cadastral boundaries, terrain, soil, hydrology, environmental conditions, access, utilities, neighboring uses, hazards, restrictions, land use, zoning, and development cost.

This matrix does not certify cadastral boundaries, survey accuracy, ownership, zoning, or environmental compliance. Those require authoritative sources, Evidence, normative interpretation, and human review.

## 3. Design Questions

The matrix supports questions about where the site is, how its boundary and area are defined, how terrain and soil affect design, what water and hazard conditions exist, how access and infrastructure work, what neighboring uses and views matter, what restrictions apply, how occupation can occur, and what site-development cost or risk is relevant.

## 4. Variable Families

Identity and boundary; area and dimensions; orientation and coordinates; reference system and elevation; slope, contours, morphology; soil, bearing, permeability; hydrology, drainage, groundwater, flood; solar, wind, temperature, humidity, radiation, rain, UV; vegetation, landscape, ET0, VPD, soil moisture; road, pedestrian, service access; water, sewer, electricity, energy, telecommunications; adjacent uses, buildings, views, noise, pollution; existing occupation and structures; easements and restrictions; land use, zoning, setbacks, height, coverage/buildability; heritage, environmental, seismic, flood, landslide, and other hazards; infrastructure availability; site cost, site-development cost, and regulatory relationships.

## 5. Minimum Profile

The minimum profile contains 20 records: `SITE_ID`, `SITE_BOUNDARY`, `SITE_AREA`, `SITE_ORIENTATION`, `SITE_COORDINATE_REFERENCE`, `SITE_ELEVATION`, `SITE_SLOPE`, `SITE_TERRAIN_MORPHOLOGY`, `SITE_SOIL_CONDITION`, `SITE_ACCESS`, `SITE_WATER_SERVICE`, `SITE_SEWER_SERVICE`, `SITE_ELECTRICITY_SERVICE`, `SITE_ADJACENT_USES`, `SITE_EXISTING_STRUCTURES`, `SITE_LAND_USE`, `SITE_ZONING`, `SITE_PHYSICAL_RESTRICTIONS`, `SITE_PRIMARY_HAZARD`, and `SITE_PROVENANCE`.

## 6. Recommended Complete Profile

The complete profile adds contours, bearing, permeability, hydrology, drainage, groundwater, flood exposure, solar, wind, temperature, humidity, rain, vegetation, ET0, VPD, soil moisture, pedestrian/service access, energy, telecommunications, adjacent buildings, views, noise, pollution, occupation, easements, setbacks, height limits, coverage/buildability, heritage/environmental restrictions, seismic risk, landslide risk, infrastructure availability, site cost, site-development cost, and normative reference.

## 7. Variable Matrix

Every record uses `spatial_scope = parcela_sitio`. Candidate GIS and analysis capabilities are `PROPOSED/FUTURE` only.

| ID | Domain | Req. | Role | Type | Unit semantics | Temporal semantics | Spatial resolution | Applicability |
|---|---|---|---|---|---|---|---|---|
| `SITE_ID` | IDENTITY | REQUIRED | CONTEXT | STRING | unitless | PROJECT_STATE | SITE | all sites |
| `SITE_BOUNDARY` | GEOMETRY/CADASTRAL | REQUIRED | CONTEXT | GEOMETRY | geometry | SURVEY/PROJECT_STATE | PARCEL | bounded sites |
| `SITE_AREA` | GEOMETRY | REQUIRED | DERIVED_METRIC | DECIMAL | area | PROJECT_STATE/DERIVED | PARCEL | sites with boundary |
| `SITE_ORIENTATION` | POSITION | REQUIRED | DESIGN_VARIABLE | DECIMAL | angle | PROJECT_STATE | SITE | orientation meaningful |
| `SITE_COORDINATE_REFERENCE` | GEOSPATIAL | REQUIRED | CONTEXT | REFERENCE | CRS/reference | PROJECT_STATE | SITE | mapped sites |
| `SITE_ELEVATION` | TERRAIN | REQUIRED | INPUT | DECIMAL/COLLECTION | length/elevation | OBSERVATION | POINT/GRID | terrain data available |
| `SITE_SLOPE` | TERRAIN | REQUIRED | DERIVED_METRIC | DECIMAL/COLLECTION | ratio/angle | SURVEY/DERIVED | GRID/POLYGON | terrain analysis |
| `SITE_TERRAIN_MORPHOLOGY` | TERRAIN | REQUIRED | CONTEXT | GEOMETRY/COLLECTION | geometry/classification | SURVEY/PROJECT_STATE | SITE | all sites with terrain context |
| `SITE_SOIL_CONDITION` | SOIL | REQUIRED | INPUT | COLLECTION | soil classification | OBSERVATION/PROJECT_STATE | SITE/SAMPLE | soil information relevant |
| `SITE_ACCESS` | ACCESS | REQUIRED | DESIGN_VARIABLE | COLLECTION | relation | PROJECT_STATE | SITE/network | sites requiring access |
| `SITE_WATER_SERVICE` | INFRASTRUCTURE | REQUIRED | CONTEXT | ENUM/COLLECTION | service | PROJECT_STATE | SITE/network | service assessment |
| `SITE_SEWER_SERVICE` | INFRASTRUCTURE | REQUIRED | CONTEXT | ENUM/COLLECTION | service | PROJECT_STATE | SITE/network | service assessment |
| `SITE_ELECTRICITY_SERVICE` | INFRASTRUCTURE | REQUIRED | CONTEXT | ENUM/COLLECTION | service | PROJECT_STATE | SITE/network | service assessment |
| `SITE_ADJACENT_USES` | CONTEXT | REQUIRED | CONTEXT | COLLECTION | classification/relation | PROJECT_STATE | SITE/neighborhood | sites with surrounding uses |
| `SITE_EXISTING_STRUCTURES` | CONTEXT | REQUIRED | CONTEXT | COLLECTION | references/geometry | PROJECT_STATE | SITE | sites with existing structures |
| `SITE_LAND_USE` | LAND_USE | REQUIRED | CONTEXT | ENUM/REFERENCE | classification | PROJECT_STATE | SITE/jurisdiction | land-use context |
| `SITE_ZONING` | REGULATION | REQUIRED | REFERENCE | ENUM/REFERENCE | classification/reference | VALIDITY_PERIOD | SITE/jurisdiction | zoning information available |
| `SITE_PHYSICAL_RESTRICTIONS` | CONSTRAINT | REQUIRED | CONSTRAINT | COLLECTION | relation/geometry | PROJECT_STATE | SITE | restrictions present |
| `SITE_PRIMARY_HAZARD` | RISK | REQUIRED | INPUT | COLLECTION | classification/metric | SCENARIO/OBSERVATION | SITE | hazard context exists |
| `SITE_PROVENANCE` | PROVENANCE | REQUIRED | CONTEXT | COLLECTION | metadata | OBSERVATION | SITE | all records |
| `SITE_CONTOURS` | TERRAIN | RECOMMENDED | INPUT | GEOMETRY/COLLECTION | elevation | SURVEY/PROJECT_STATE | GRID/LINE | topography in scope |
| `SITE_BEARING_CHARACTERISTICS` | SOIL | RECOMMENDED | INPUT | COLLECTION | force/stress | OBSERVATION/PROJECT_STATE | SAMPLE/SITE | structural soil analysis |
| `SITE_PERMEABILITY` | SOIL/HYDROLOGY | RECOMMENDED | INPUT | DECIMAL | flow coefficient | OBSERVATION | SAMPLE/SITE | drainage or water analysis |
| `SITE_HYDROLOGY` | WATER | RECOMMENDED | INPUT | COLLECTION | flow/relationship | SEASONAL/OBSERVATION | WATERSHED/SITE | hydrology in scope |
| `SITE_DRAINAGE` | WATER | RECOMMENDED | DESIGN_VARIABLE | COLLECTION/GEOMETRY | flow/relation | PROJECT_STATE | SITE/network | drainage design |
| `SITE_GROUNDWATER` | WATER | OPTIONAL | INPUT | DECIMAL/COLLECTION | elevation/flow | SEASONAL/OBSERVATION | SAMPLE/SITE | groundwater relevant |
| `SITE_FLOOD_EXPOSURE` | RISK | RECOMMENDED | DERIVED_METRIC | COLLECTION | probability/depth | SCENARIO/DERIVED | FLOOD_ZONE/SITE | flood analysis |
| `SITE_SOLAR_CONDITION` | ENVIRONMENT | RECOMMENDED | INPUT | COLLECTION | radiation/angle | HOURLY/DAILY | GRID/SITE | solar analysis |
| `SITE_WIND_CONDITION` | ENVIRONMENT | OPTIONAL | INPUT | COLLECTION | speed/direction | HOURLY/DAILY | GRID/SITE | wind analysis |
| `SITE_TEMPERATURE` | ENVIRONMENT | OPTIONAL | INPUT | DECIMAL/COLLECTION | temperature | HOURLY/DAILY | GRID/SITE | climate input |
| `SITE_HUMIDITY` | ENVIRONMENT | OPTIONAL | INPUT | DECIMAL | ratio/% | HOURLY/DAILY | GRID/SITE | climate input |
| `SITE_RAIN` | ENVIRONMENT | OPTIONAL | INPUT | DECIMAL | depth/rate | DAILY/SEASONAL | GRID/SITE | rain/drainage analysis |
| `SITE_VEGETATION` | LANDSCAPE | RECOMMENDED | CONTEXT | COLLECTION/GEOMETRY | classification/area | OBSERVATION/PROJECT_STATE | SITE | existing vegetation |
| `SITE_ET0` | ENVIRONMENT | OPTIONAL | DERIVED_METRIC | DECIMAL | depth/time | DAILY/DERIVED | GRID/SITE | water-landscape analysis |
| `SITE_VPD` | ENVIRONMENT | OPTIONAL | DERIVED_METRIC | DECIMAL | pressure | HOURLY/DERIVED | GRID/SITE | plant or climate analysis |
| `SITE_SOIL_MOISTURE` | SOIL | OPTIONAL | INPUT | DECIMAL | ratio/volume | HOURLY/DAILY | GRID/SITE | soil-water analysis |
| `SITE_PEDESTRIAN_ACCESS` | ACCESS | RECOMMENDED | DESIGN_VARIABLE | COLLECTION | relation | PROJECT_STATE | SITE/network | pedestrian planning |
| `SITE_SERVICE_ACCESS` | ACCESS | OPTIONAL | DESIGN_VARIABLE | COLLECTION | relation | PROJECT_STATE | SITE/network | service access relevant |
| `SITE_ENERGY_SERVICE` | INFRASTRUCTURE | OPTIONAL | CONTEXT | COLLECTION | power/energy | PROJECT_STATE | SITE/network | energy service assessment |
| `SITE_TELECOMMUNICATIONS` | INFRASTRUCTURE | OPTIONAL | CONTEXT | COLLECTION | service | PROJECT_STATE | SITE/network | communications relevant |
| `SITE_ADJACENT_BUILDINGS` | CONTEXT | RECOMMENDED | CONTEXT | COLLECTION/GEOMETRY | references | PROJECT_STATE | SITE/neighborhood | surrounding buildings |
| `SITE_VIEWS` | CONTEXT | RECOMMENDED | CONSTRAINT | COLLECTION | view/relation | PROJECT_STATE | SITE/horizon | view analysis |
| `SITE_NOISE` | ENVIRONMENT | OPTIONAL | INPUT | DECIMAL/COLLECTION | acoustic dimension | HOURLY/DAILY | GRID/SITE | noise analysis |
| `SITE_POLLUTION` | ENVIRONMENT | OPTIONAL | INPUT | DECIMAL/COLLECTION | concentration | HOURLY/DAILY | GRID/SITE | pollution analysis |
| `SITE_EASEMENTS` | REGULATION | RECOMMENDED | CONSTRAINT | COLLECTION/GEOMETRY | relation/area | VALIDITY_PERIOD | PARCEL | legal or physical easements |
| `SITE_SETBACKS` | REGULATION | RECOMMENDED | CONSTRAINT | DECIMAL/COLLECTION | length/area | VALIDITY_PERIOD | PARCEL | setback rules |
| `SITE_HEIGHT_LIMITS` | REGULATION | RECOMMENDED | CONSTRAINT | DECIMAL | length | VALIDITY_PERIOD | PARCEL/jurisdiction | height rules |
| `SITE_COVERAGE_BUILDABILITY` | REGULATION | RECOMMENDED | DERIVED_METRIC | DECIMAL/COLLECTION | ratio/area | VALIDITY_PERIOD/DERIVED | PARCEL | development feasibility |
| `SITE_HERITAGE_ENVIRONMENTAL_RESTRICTIONS` | REGULATION | RECOMMENDED | CONSTRAINT | COLLECTION | classification/relation | VALIDITY_PERIOD | PARCEL | heritage/environmental limits |
| `SITE_SEISMIC_RISK` | RISK | RECOMMENDED | DERIVED_METRIC | COLLECTION | classification/metric | SCENARIO/DERIVED | REGION/SITE | seismic analysis |
| `SITE_LANDSLIDE_RISK` | RISK | OPTIONAL | DERIVED_METRIC | COLLECTION | classification/metric | SCENARIO/DERIVED | GRID/SITE | slope hazard analysis |
| `SITE_INFRASTRUCTURE_AVAILABILITY` | INFRASTRUCTURE | RECOMMENDED | DERIVED_METRIC | COLLECTION | service status | PROJECT_STATE/DERIVED | SITE/network | service availability |
| `SITE_COST` | COST | OPTIONAL | DERIVED_METRIC | DECIMAL | currency | PROJECT_STATE/DERIVED | SITE | land/site cost in scope |
| `SITE_DEVELOPMENT_COST` | COST | OPTIONAL | DERIVED_METRIC | DECIMAL | currency | PROJECT_STATE/DERIVED | SITE | site-development cost in scope |
| `SITE_NORMATIVE_REFERENCE` | REGULATION | RECOMMENDED | REFERENCE | COLLECTION | references | VALIDITY_PERIOD | SITE/jurisdiction | normative relations |

The matrix contains 54 named candidates. The **40-record primary profile** contains the first 40 governed concepts; conditional environmental, hazard, infrastructure, and cost details remain profile metadata rather than discipline-specific schemas.

## 8. Conditional Applicability

Groundwater, ET0, VPD, soil moisture, wind, humidity, rain, pollution, noise, landslide risk, service access, telecommunications, cost, and development cost apply only when the design question and data support exist. Heritage and environmental restrictions apply only where a relevant authority or evidence exists. GIS and cadastral relationships are future conceptual links, not current features.

## 9. GIS and Source Separation

Future GIS relationships may connect boundary, coordinate reference, terrain, contours, hazards, infrastructure, adjacent uses, and zoning to GeoJSON, OGC API Features, or other governed spatial sources. This document does not implement GIS, import cadastral data, certify boundaries, or create `ParcelSnapshot` records.

Environmental reference location is not cadastral location. A weather observation point does not certify the parcel. A zoning rule is not a project value. A topographic dataset is not a survey certification.

## 10. Cross-Scale Reuse

Candidates from `objeto`, `espacio`, `sistema`, and `edificacion` include identity, geometry, orientation, access, material, environmental inputs, risk, cost, maintenance, and provenance. `SITE_AREA` is distinct from `BUILDING_FOOTPRINT`. `SITE_ORIENTATION` is distinct from `BUILDING_ORIENTATION`. `SITE_ADJACENT_BUILDINGS` is a site context relation, not building massing.

## 11. Design Knowledge, Regulation, and Capabilities

Design Knowledge may inform site planning patterns, access, vegetation, orientation, water strategies, and risk-sensitive design. It remains advisory and does not produce site values.

Regulation follows `Regulation → Evidence/Interpretation → Constraint → site relation`. Zoning, setbacks, height, coverage, heritage, environmental, easement, and hazard rules do not automatically become project variable values or decisions.

Candidate capabilities are `PROPOSED/FUTURE`: `SITE_GIS_ANALYSIS`, `SITE_TERRAIN_ANALYSIS`, `SITE_HYDROLOGY_ANALYSIS`, `SITE_HAZARD_ANALYSIS`, `SITE_INFRASTRUCTURE_ANALYSIS`, `SITE_ENVIRONMENTAL_ANALYSIS`, `SITE_REGULATORY_FEASIBILITY`, `SITE_COST_ANALYSIS`, and `SITE_SCENARIO_ANALYSIS`.

## 12. Gate

`SITE_VARIABLE_COUNT = 40`
`SITE_MINIMUM_COUNT = 20`
`SITE_COMPLETE_COUNT = 40`
`CONDITIONAL_APPLICABILITY = PASS`
`STATE_DESIGN_DERIVED_SEPARATION = PASS`
`ENVIRONMENTAL_SEPARATION = PASS`
`PROVENANCE = PASS`
`SOURCE_CLASSES = PASS`
`DESIGN_KNOWLEDGE_RELATIONSHIP = PASS`
`REGULATORY_RELATIONSHIP = PASS`
`CAPABILITY_RELATIONSHIP = PASS — conceptual links only`
`GIS_IMPLEMENTED = NO`
`REAL_CADASTRAL_DATA_LOADED = NO`
`PRODUCT_IMPLEMENTATION = NO`

**Status:** MV-P0.6 specification PASS.

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SiMS-DeI SICL Core repository"
[2]: https://github.com/YvanCastilloQuezada/sicl-web "SiMS-DeI SICL Web repository"
