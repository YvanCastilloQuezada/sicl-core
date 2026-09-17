# MV-P0.3 — Space-Scale Variable Matrix

**Project:** SiMS-DeI / SICL
**Program:** MV-P0 — Multiscale Variable Matrix Definition
**Status:** AUTHORIZED FOR VARIABLE MATRIX SPECIFICATION
**Product implementation:** NOT AUTHORIZED
**SpatialScope:** `espacio`
**Lineage:** MV-P0.2 Object Variable Matrix, commit `2c3d8e20a39eede18399d955d7437e60fc6e7b80`

> This document defines the conceptual variable matrix for an occupiable or functionally meaningful spatial unit. It does not create runtime catalog records, project values, database tables, API routes, migrations, capabilities, or frontend behavior.

## 1. Executive Summary

`espacio` represents a room, classroom, office, laboratory, commercial space, bedroom, kitchen, bathroom, corridor, lobby, waiting area, auditorium, workshop, clinical space, technical space, or other occupiable or functionally meaningful spatial unit. These examples are contextual only. MV-P0.3 does not create a space typology ontology.

This matrix defines **36 conceptual variable records**. The minimum profile contains **18 records** sufficient to understand a space as a design unit. The recommended complete profile contains all **36 records**, including environmental, human-use, access, performance, and lifecycle variables that apply conditionally.

Requirement counts are:

- `REQUIRED`: 18
- `RECOMMENDED`: 11
- `OPTIONAL`: 4
- `NOT_APPLICABLE`: 3

The matrix preserves the MV-P0.1 contract and the lessons from MV-P0.2. `SPACE_AREA` is not `BUILDING_AREA`. Actual occupancy is not design capacity or regulatory maximum occupancy. Environmental inputs are not analyses, derived metrics, or evaluations. Regulatory requirements are not project variable values.

## 2. Space Definition

A space is a bounded or functionally coherent spatial unit that can be occupied, used, traversed, serviced, or evaluated as part of a larger system. It may be enclosed, partially enclosed, open, interior, exterior, public, private, technical, or operational.

The space scale is where geometry and human use interact directly. It is also the first matrix scale where daylight, solar exposure, temperature, humidity, ventilation, air quality, acoustics, privacy, visibility, and occupancy become strongly relevant. Their presence in the matrix does not imply that every space needs every variable.

The canonical chain remains:

```text
VariableDefinition
        ↓
ScaleVariableProfile
        ↓
SuggestedVariable
        ↓
ProjectVariable
```

`Fact`, `Assumption`, `Objective`, `Constraint`, `Source`, `Evidence`, `Evaluation`, `Recommendation`, `HumanReview`, and `Decision` remain separate concepts.

## 3. Design Questions

The space matrix supports these design questions:

1. What space is being designed or evaluated?
2. What use or function does it support?
3. What dimensions, area, volume, and proportions are required?
4. How many people occupy it, and how is that different from its design capacity?
5. What activities occur there and during which periods?
6. How does it connect to adjacent spaces?
7. Are access, circulation, clear widths, and egress adequate?
8. Where should doors, windows, and other openings be located?
9. Does daylight matter, and what daylight analysis is appropriate?
10. Does solar exposure matter?
11. What ventilation and air-quality conditions matter?
12. What thermal and humidity conditions matter?
13. What acoustic, privacy, and visibility conditions matter?
14. What furniture and equipment must fit?
15. Is the space accessible and safe to evacuate?
16. What water, sanitary, and electrical services are required?
17. What maintenance and operational conditions matter?
18. What cost metric is relevant, if cost is in scope?
19. Which regulatory requirements constrain the design?

The matrix identifies semantic variables. It does not answer these questions automatically.

## 4. Variable Families

| Family | Space-scale purpose |
|---|---|
| Identity / classification | Identify the space without creating a complete typology ontology |
| Function / use | Describe intended use and functional role |
| Geometry | Describe length, width, height, area, volume, and proportions |
| Occupancy / capacity | Distinguish actual use, intended capacity, and regulated maximum |
| Activities / schedule | Describe use patterns and periods |
| Position / orientation | Locate and orient the space in its containing building or system |
| Adjacency / access | Describe connections, accesses, openings, and neighboring spaces |
| Circulation / egress | Describe movement and safe exit conditions |
| Accessibility | Describe accessible use and clearances |
| Daylight / artificial lighting | Describe light inputs and design analysis contexts |
| Solar / environmental | Describe solar, thermal, humidity, ventilation, and air-quality contexts |
| Acoustics / privacy / visibility | Describe sensory and social performance conditions |
| Ergonomics / furniture / equipment | Describe fit and operational requirements |
| Safety / fire | Describe hazards, evacuation, and fire conditions |
| Material / finish | Describe space-level surface or finish conditions |
| Energy / sanitary / electrical | Describe services conditionally |
| Maintenance / durability / cost | Describe operation and lifecycle concerns |
| Regulatory relationships | Link normative sources to evidence, interpretation, and constraint |

No family is universally applicable to every space.

## 5. Minimum Profile

The minimum profile contains 18 records:

| ID | Concept | Rationale |
|---|---|---|
| `SPACE_ID` | Space identity | Distinguishes the spatial unit |
| `SPACE_CLASS` | Space class | Provides a classification hook without creating a typology ontology |
| `SPACE_FUNCTION` | Space function/use | Establishes intended use |
| `SPACE_LENGTH` | Space length | Establishes a primary dimension |
| `SPACE_WIDTH` | Space width | Establishes a primary dimension |
| `SPACE_HEIGHT` | Space height | Establishes vertical dimension where meaningful |
| `SPACE_AREA` | Space area | Establishes the plan extent of the space |
| `SPACE_VOLUME` | Space volume | Establishes three-dimensional extent where meaningful |
| `SPACE_OCCUPANCY` | Actual or observed occupancy | Describes use state without becoming capacity |
| `SPACE_CAPACITY` | Design capacity | Describes intended design load separately from occupancy |
| `SPACE_ACCESS` | Space access | Identifies access points or access condition |
| `SPACE_ADJACENCY` | Adjacency relation | Connects the space to other spaces |
| `SPACE_CIRCULATION` | Circulation condition | Describes movement through or within the space |
| `SPACE_ORIENTATION` | Space orientation | Describes directional relation where meaningful |
| `SPACE_OPENINGS` | Openings | Describes doors, windows, and other openings at space scale |
| `SPACE_CONTAINER_REFERENCE` | Containing building/system | Links the space to its larger context |
| `SPACE_PRIMARY_CONSTRAINT` | Primary constraint reference | Points to a Constraint without replacing it |
| `SPACE_PROVENANCE` | Provenance metadata | Prevents assumed or synthetic values from appearing measured |

The minimum profile is compact. Detailed door material, thickness, hardware, or fabrication belongs primarily to `objeto`; its effect on access, opening area, clear width, or egress belongs to `espacio`.

## 6. Recommended Complete Profile

The complete profile adds 18 records:

- activity and schedule;
- clear width and egress;
- accessibility;
- daylight and ventilation;
- air quality and thermal conditions;
- acoustic isolation;
- privacy and visibility;
- furniture fit and equipment load;
- sanitary demand and electrical demand;
- estimated cost and maintenance plan.

These variables are conditional. A classroom may need acoustic isolation, daylight, occupancy, furniture fit, and air quality. An open circulation space may not require acoustic isolation. A bathroom may require sanitary demand. A passive room may not require electrical demand. A laboratory may require equipment load.

## 7. Variable Matrix

Every record has `spatial_scope = espacio`. Candidate capabilities are `PROPOSED/FUTURE` unless already canonical elsewhere; this document does not create runtime capability IDs.

### 7.1 Identity, geometry, occupancy, and context

| ID | Canonical name | Domain | Requirement | Role | Data type | Unit semantics | Temporal semantics | Spatial resolution | Applicability | Provenance | Source class | Capability link | Description |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `SPACE_ID` | Space identity | IDENTITY | REQUIRED | CONTEXT | STRING | unitless | PROJECT_STATE | SPACE | All space profiles | REAL or ASSUMED | USER_INPUT, DESIGN_DOCUMENT | None | Stable identity for the space |
| `SPACE_CLASS` | Space class | IDENTITY | REQUIRED | CLASSIFICATION | ENUM or STRING | unitless | PROJECT_STATE | SPACE | All space profiles; not a typology ontology | REAL, ASSUMED, or SYNTHETIC | USER_INPUT, DESIGN_DOCUMENT | None | Controlled classification hook |
| `SPACE_FUNCTION` | Space function/use | FUNCTION | REQUIRED | DESIGN_VARIABLE | ENUM or STRING | unitless | PROJECT_STATE | SPACE | All spaces with an intended function | ASSUMED or DESIGN_DOCUMENT | USER_INPUT, DESIGN_DOCUMENT | PROPOSED/FUTURE SPACE_ANALYSIS | Intended use or functional role |
| `SPACE_LENGTH` | Space length | GEOMETRY | REQUIRED | DESIGN_VARIABLE | DECIMAL | length | PROJECT_STATE | SPACE | Spaces where length is meaningful | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, BIM_MODEL, MEASUREMENT | PROPOSED/FUTURE SPACE_GEOMETRY_ANALYSIS | Primary linear dimension |
| `SPACE_WIDTH` | Space width | GEOMETRY | REQUIRED | DESIGN_VARIABLE | DECIMAL | length | PROJECT_STATE | SPACE | Spaces where width is meaningful | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, BIM_MODEL, MEASUREMENT | PROPOSED/FUTURE SPACE_GEOMETRY_ANALYSIS | Primary transverse dimension |
| `SPACE_HEIGHT` | Space height | GEOMETRY | REQUIRED | DESIGN_VARIABLE | DECIMAL | length | PROJECT_STATE | SPACE | Enclosed or vertically defined spaces; otherwise conditional | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, BIM_MODEL, MEASUREMENT | PROPOSED/FUTURE SPACE_GEOMETRY_ANALYSIS | Vertical dimension |
| `SPACE_AREA` | Space area | GEOMETRY | REQUIRED | DERIVED_METRIC | DECIMAL | area | PROJECT_STATE or DERIVED | SPACE | All spaces with a meaningful boundary | REAL, APPROXIMATED, ASSUMED, or SYNTHETIC | BIM_MODEL, MEASUREMENT, DERIVED | PROPOSED/FUTURE SPACE_GEOMETRY_ANALYSIS | Area of the space, not building area |
| `SPACE_VOLUME` | Space volume | GEOMETRY | REQUIRED | DERIVED_METRIC | DECIMAL | volume | PROJECT_STATE or DERIVED | SPACE | Three-dimensional spaces; conditional for open or undefined volumes | REAL, APPROXIMATED, ASSUMED, or SYNTHETIC | BIM_MODEL, MEASUREMENT, DERIVED | PROPOSED/FUTURE SPACE_GEOMETRY_ANALYSIS | Volume of the space |
| `SPACE_OCCUPANCY` | Actual occupancy | HUMAN | REQUIRED | CONTEXT | INTEGER or COLLECTION | persons | OBSERVATION or PROJECT_STATE | SPACE | Occupied or observed spaces | REAL, APPROXIMATED, ASSUMED, or SYNTHETIC | MEASUREMENT, USER_INPUT, OFFICIAL_SOURCE | PROPOSED/FUTURE OCCUPANCY_ANALYSIS | Observed or declared use, not design capacity |
| `SPACE_CAPACITY` | Design capacity | HUMAN | REQUIRED | PARAMETER | INTEGER | persons | PROJECT_STATE | SPACE | Spaces with a defined intended capacity | ASSUMED, REAL, or SYNTHETIC | DESIGN_DOCUMENT, TECHNICAL_STANDARD, USER_INPUT | PROPOSED/FUTURE OCCUPANCY_ANALYSIS | Intended design capacity |
| `SPACE_ACCESS` | Space access | ACCESS | REQUIRED | DESIGN_VARIABLE | COLLECTION | relation | PROJECT_STATE | SPACE/SPACE relation | Spaces that must be entered or reached | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, BIM_MODEL, MEASUREMENT | PROPOSED/FUTURE ACCESS_ANALYSIS | Access points and access condition |
| `SPACE_ADJACENCY` | Space adjacency | SPATIAL_RELATION | REQUIRED | CONTEXT | COLLECTION | relation | PROJECT_STATE | SPACE/SPACE relation | Spaces connected to or near other spaces | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, BIM_MODEL, MEASUREMENT | PROPOSED/FUTURE SPACE_NETWORK_ANALYSIS | Neighboring-space relations |
| `SPACE_CIRCULATION` | Circulation condition | CIRCULATION | REQUIRED | CONSTRAINT | COLLECTION or ENUM | relation/clearance | PROJECT_STATE | SPACE/SPACE relation | Spaces used for movement or containing movement paths | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, MEASUREMENT, TECHNICAL_STANDARD | PROPOSED/FUTURE CIRCULATION_ANALYSIS | Movement through or within space |
| `SPACE_ORIENTATION` | Space orientation | POSITION | REQUIRED | DESIGN_VARIABLE | DECIMAL | angle | PROJECT_STATE | SPACE/building relation | Directional or environmental relation is meaningful | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, BIM_MODEL, MEASUREMENT | PROPOSED/FUTURE SOLAR_ANALYSIS | Orientation relative to a declared frame |
| `SPACE_OPENINGS` | Space openings | OPENINGS | REQUIRED | DESIGN_VARIABLE | COLLECTION | count/area/relation | PROJECT_STATE | SPACE/envelope relation | Spaces with doors, windows, or other openings | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, BIM_MODEL, MEASUREMENT | PROPOSED/FUTURE DAYLIGHT_ANALYSIS | Openings and their space-level effects |
| `SPACE_CONTAINER_REFERENCE` | Containing building/system | SPATIAL_RELATION | REQUIRED | CONTEXT | REFERENCE | unitless reference | PROJECT_STATE | BUILDING/SYSTEM reference | Spaces within a larger system | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, BIM_MODEL, USER_INPUT | None | Reference to containing context |
| `SPACE_PRIMARY_CONSTRAINT` | Primary space constraint | GOVERNANCE | REQUIRED | REFERENCE | REFERENCE or COLLECTION | unitless reference | PROJECT_STATE | SPACE | When a constraint is relevant | REAL or ASSUMED | TECHNICAL_STANDARD, REGULATION, DESIGN_DOCUMENT | None | Reference to Constraint without replacing it |
| `SPACE_PROVENANCE` | Space provenance | PROVENANCE | REQUIRED | CONTEXT | COLLECTION | unitless metadata | OBSERVATION or PROJECT_STATE | SPACE | All space records | REAL, APPROXIMATED, ASSUMED, SYNTHETIC, or NOT_AVAILABLE | SOURCE, EVIDENCE, USER_INPUT | None | Provenance for space data |

### 7.2 Human use, environmental performance, and operations

| ID | Canonical name | Domain | Requirement | Role | Data type | Unit semantics | Temporal semantics | Spatial resolution | Applicability | Provenance | Source class | Capability link | Description |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `SPACE_ACTIVITY` | Space activity | ACTIVITIES | RECOMMENDED | CONTEXT | ENUM or COLLECTION | unitless | PROJECT_STATE | SPACE | Spaces with one or more meaningful activities | ASSUMED, REAL, or SYNTHETIC | USER_INPUT, DESIGN_DOCUMENT, MEASUREMENT | PROPOSED/FUTURE OCCUPANCY_ANALYSIS | Activities occurring in the space |
| `SPACE_SCHEDULE` | Space use schedule | SCHEDULE | RECOMMENDED | PARAMETER | COLLECTION | time interval | DAILY, WEEKLY, SEASONAL, or PROJECT_STATE | SPACE | Spaces whose use varies over time | REAL, ASSUMED, or SYNTHETIC | USER_INPUT, MEASUREMENT, DESIGN_DOCUMENT | PROPOSED/FUTURE OCCUPANCY_ANALYSIS | Use periods and schedules |
| `SPACE_CLEAR_WIDTH` | Clear width | ACCESSIBILITY | RECOMMENDED | CONSTRAINT | DECIMAL | length | PROJECT_STATE | SPACE/SPACE relation | Access, circulation, and egress require a clear width | REAL, ASSUMED, or SYNTHETIC | TECHNICAL_STANDARD, DESIGN_DOCUMENT, MEASUREMENT | PROPOSED/FUTURE ACCESSIBILITY_ANALYSIS | Unobstructed width relevant to movement |
| `SPACE_EGRESS` | Egress condition | EGRESS | RECOMMENDED | CONSTRAINT | COLLECTION or ENUM | relation/clearance | PROJECT_STATE | SPACE/SPACE relation | Occupied spaces requiring safe exit | REAL, ASSUMED, or SYNTHETIC | REGULATION, TECHNICAL_STANDARD, DESIGN_DOCUMENT | PROPOSED/FUTURE EGRESS_ANALYSIS | Exit path, exit points, and conditions |
| `SPACE_ACCESSIBILITY` | Space accessibility | ACCESSIBILITY | RECOMMENDED | CONSTRAINT | COLLECTION or ENUM | classification/clearance | PROJECT_STATE | SPACE/user relation | Public, shared, or accessible-use spaces | REAL, ASSUMED, or SYNTHETIC | TECHNICAL_STANDARD, REGULATION, DESIGN_DOCUMENT | PROPOSED/FUTURE ACCESSIBILITY_ANALYSIS | Accessible use conditions |
| `SPACE_DAYLIGHT` | Daylight condition | LIGHT | RECOMMENDED | DERIVED_METRIC | COLLECTION or DECIMAL | illuminance/ratio | INSTANT, DAILY, or DERIVED | SPACE/opening relation | Spaces where daylight is relevant | REAL, APPROXIMATED, ASSUMED, or SYNTHETIC | MEASUREMENT, SIMULATION, DERIVED | PROPOSED/FUTURE DAYLIGHT_ANALYSIS | Daylight input or derived condition; not an Evaluation |
| `SPACE_VENTILATION` | Ventilation condition | ENVIRONMENT | RECOMMENDED | DERIVED_METRIC | COLLECTION or DECIMAL | air-flow dimension | INSTANT, HOURLY, or DERIVED | SPACE/opening/system relation | Spaces where air exchange matters | REAL, APPROXIMATED, ASSUMED, or SYNTHETIC | MEASUREMENT, SIMULATION, DERIVED | PROPOSED/FUTURE VENTILATION_ANALYSIS | Ventilation input or derived condition |
| `SPACE_THERMAL_CONDITION` | Thermal condition | THERMAL | RECOMMENDED | DERIVED_METRIC | COLLECTION or DECIMAL | temperature/thermal dimension | INSTANT, HOURLY, or DERIVED | SPACE | Spaces where thermal conditions matter | REAL, APPROXIMATED, ASSUMED, or SYNTHETIC | MEASUREMENT, SIMULATION, DERIVED | PROPOSED/FUTURE THERMAL_ANALYSIS | Thermal condition; not automatically comfort |
| `SPACE_PRIVACY` | Privacy condition | PRIVACY | RECOMMENDED | CONSTRAINT | COLLECTION or ENUM | classification | PROJECT_STATE | SPACE/SPACE relation | Spaces where visual, acoustic, or social privacy matters | ASSUMED, REAL, or SYNTHETIC | USER_INPUT, DESIGN_DOCUMENT, TECHNICAL_STANDARD | PROPOSED/FUTURE PRIVACY_ANALYSIS | Declared privacy requirement or condition |
| `SPACE_VISIBILITY` | Visibility condition | VISIBILITY | RECOMMENDED | CONSTRAINT | COLLECTION or ENUM | classification/view relation | PROJECT_STATE | SPACE/SPACE relation | Spaces where sightlines, supervision, or orientation matter | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, BIM_MODEL, MEASUREMENT | PROPOSED/FUTURE VISIBILITY_ANALYSIS | Declared visibility relationship |
| `SPACE_FURNITURE_FIT` | Furniture fit | ERGONOMICS | RECOMMENDED | CONSTRAINT | COLLECTION | length/area/relation | PROJECT_STATE | SPACE/object relation | Spaces requiring furniture or equipment fit | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, BIM_MODEL, USER_INPUT | PROPOSED/FUTURE ERGONOMIC_ANALYSIS | Furniture layout and fit condition |
| `SPACE_AIR_QUALITY` | Air quality | ENVIRONMENT | OPTIONAL | DERIVED_METRIC | COLLECTION or DECIMAL | concentration | INSTANT, HOURLY, or DERIVED | SPACE | Spaces where pollutant or air-quality analysis is in scope | REAL, APPROXIMATED, ASSUMED, or SYNTHETIC | MEASUREMENT, SIMULATION, OFFICIAL_SOURCE | PROPOSED/FUTURE AIR_QUALITY_ANALYSIS | Air-quality observation or derived condition |
| `SPACE_EQUIPMENT_LOAD` | Equipment load | EQUIPMENT | OPTIONAL | INPUT | DECIMAL or COLLECTION | force/power/area | PROJECT_STATE | SPACE/object relation | Laboratories, clinical, technical, or equipment-intensive spaces | REAL, ASSUMED, or SYNTHETIC | MANUFACTURER_DATA, DESIGN_DOCUMENT, USER_INPUT | PROPOSED/FUTURE EQUIPMENT_ANALYSIS | Load or service requirement of equipment |
| `SPACE_SANITARY_DEMAND` | Sanitary demand | WATER / SANITARY | NOT_APPLICABLE | INPUT | DECIMAL or COLLECTION | flow/volume | HOURLY, DAILY, or PROJECT_STATE | SPACE/system relation | `NOT_APPLICABLE` where no sanitary service is required; conditional for bathrooms and serviced spaces | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, TECHNICAL_STANDARD, MANUFACTURER_DATA | PROPOSED/FUTURE SANITARY_ANALYSIS | Water or sanitary service demand |
| `SPACE_ELECTRICAL_DEMAND` | Electrical demand | ELECTRICAL | NOT_APPLICABLE | INPUT | DECIMAL or COLLECTION | power/energy | INSTANT, HOURLY, or PROJECT_STATE | SPACE/system relation | `NOT_APPLICABLE` for spaces without electrical service; conditional otherwise | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, MANUFACTURER_DATA, MEASUREMENT | PROPOSED/FUTURE ENERGY_ANALYSIS | Electrical demand or service requirement |
| `SPACE_ACOUSTIC_ISOLATION` | Acoustic isolation | ACOUSTICS | NOT_APPLICABLE | CONSTRAINT | DECIMAL or COLLECTION | acoustic dimension | PROJECT_STATE or DERIVED | SPACE/SPACE relation | `NOT_APPLICABLE` for spaces with no acoustic isolation requirement; conditional for classrooms, clinical, or privacy-sensitive spaces | REAL, APPROXIMATED, ASSUMED, or SYNTHETIC | TECHNICAL_STANDARD, MEASUREMENT, SIMULATION | PROPOSED/FUTURE ACOUSTIC_ANALYSIS | Acoustic isolation requirement or result |
| `SPACE_ESTIMATED_COST` | Estimated space cost | COST | OPTIONAL | DERIVED_METRIC | DECIMAL or COLLECTION | currency | PROJECT_STATE or DERIVED | SPACE | Cost analysis is explicitly in scope | APPROXIMATED, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, DERIVED, USER_INPUT | PROPOSED/FUTURE COST_ANALYSIS | Conceptual construction or operation cost metric |
| `SPACE_MAINTENANCE_PLAN` | Maintenance plan | MAINTENANCE | OPTIONAL | PARAMETER | COLLECTION | interval/action | MULTIYEAR or PROJECT_STATE | SPACE/system relation | Spaces with operational maintenance requirements | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, MANUFACTURER_DATA, USER_INPUT | PROPOSED/FUTURE LIFECYCLE_ANALYSIS | Planned maintenance actions and intervals |

## 8. Conditional Applicability

The matrix deliberately avoids creating one schema per space type.

| Variable | Context where applicable | Legitimate non-applicable context |
|---|---|---|
| `SPACE_ACOUSTIC_ISOLATION` | Classroom, clinical space, auditorium, recording room, privacy-sensitive office | Open circulation space without acoustic separation requirement |
| `SPACE_SANITARY_DEMAND` | Bathroom, kitchen, clinical or serviced space | Space with no sanitary service or water demand |
| `SPACE_ELECTRICAL_DEMAND` | Office, laboratory, equipment room, lighting-dependent space | Passive space with no electrical service |
| `SPACE_EQUIPMENT_LOAD` | Laboratory, clinic, workshop, technical room | Room without fixed or significant equipment |
| `SPACE_AIR_QUALITY` | Occupied or sensitive space with air-quality objectives | Space where air-quality analysis is not in scope |
| `SPACE_DAYLIGHT` | Occupied space with openings or daylight objective | Enclosed technical space where daylight is not relevant |
| `SPACE_SOLAR` | Space affected by solar exposure or shading | Space with no meaningful solar question |

`NOT_APPLICABLE` is contextual. It does not mean that the family never applies to `espacio`.

## 9. Environmental and Human Variables

Environmental semantics follow the chain:

```text
INPUT / OBSERVATION
        ↓
ANALYSIS
        ↓
DERIVED METRIC
        ↓
EVALUATION
```

Examples:

- Weather temperature observation is not thermal comfort.
- Ventilation input is not ventilation performance.
- Solar radiation input is not daylight performance.
- Daylight analysis is not an Evaluation.
- An Evaluation may compare alternatives using a derived metric, but it does not replace the metric.

Human-use semantics also require separation:

- actual occupancy is an observation or declared state;
- design capacity is a project parameter;
- regulatory maximum occupancy is a normative interpretation or constraint;
- activity and schedule describe intended use;
- anthropometry, ergonomics, privacy, and visibility describe human interaction conditions.

No weather value alone supports a claim of comfort, energy performance, or ventilation performance.

## 10. State vs Design vs Derived

| Category | Space examples | Semantic boundary |
|---|---|---|
| Context/input | `SPACE_CONTAINER_REFERENCE`, `SPACE_OCCUPANCY`, temperature observation | Describes existing or supplied conditions |
| Design variable | `SPACE_LENGTH`, `SPACE_WIDTH`, `SPACE_ORIENTATION`, `SPACE_OPENINGS` | A project may explicitly change or propose it |
| Constraint | `SPACE_CLEAR_WIDTH`, `SPACE_EGRESS`, `SPACE_ACCESSIBILITY`, `SPACE_PRIVACY` | Restricts or qualifies a design |
| Derived metric | `SPACE_AREA`, `SPACE_VOLUME`, `SPACE_DAYLIGHT`, `SPACE_VENTILATION`, `SPACE_THERMAL_CONDITION` | Produced by measurement, derivation, or analysis |
| Reference | `SPACE_PRIMARY_CONSTRAINT`, normative relation | Points to another canonical entity |
| Objective reference | `SPACE_FUNCTION` or primary objective reference | Does not become an Objective entity |

A project action may create a `ProjectVariable`. It does not automatically create a Fact, Assumption, Objective, Constraint, Recommendation, HumanReview, or Decision.

## 11. Cross-Scale Reuse with Object

Potential reuse candidates from MV-P0.2 include:

- dimensions such as length, width, and height;
- orientation;
- position;
- material;
- clearance;
- cost;
- maintenance;
- provenance;
- geometry representation.

These are candidates only. Their identity must be reviewed under the MV-P0.1 rule: reuse is allowed only when meaning, dimension, measurement method, spatial support, temporal semantics, derivation, and decision use remain compatible.

The following variables are semantically distinct from object variables:

| Space variable | Why distinct from object-scale concept |
|---|---|
| `SPACE_AREA` | Area of a spatial unit, not the surface area of an object |
| `SPACE_VOLUME` | Volume of an occupiable unit, not object volume |
| `SPACE_OCCUPANCY` | People using a space, not object quantity |
| `SPACE_CAPACITY` | Intended spatial capacity, not object count |
| `SPACE_ADJACENCY` | Relation between spaces, not object adjacency alone |
| `SPACE_CIRCULATION` | Movement through a space, not component geometry |
| `SPACE_OPENINGS` | Effect and relation of openings at space scale, not door/window fabrication properties |
| `SPACE_DAYLIGHT` | Space-level light condition, not a component’s optical property |
| `SPACE_EQUIPMENT_LOAD` | Space service/load requirement, not equipment material or object mass |
| `SPACE_SANITARY_DEMAND` | Space service demand, not fixture geometry |

Global deduplication remains deferred to MV-P0.13.

## 12. Capability Relationships

Candidate capability relationships are conceptual and future-facing:

- `SPACE_GEOMETRY_ANALYSIS`
- `OCCUPANCY_ANALYSIS`
- `SPACE_NETWORK_ANALYSIS`
- `CIRCULATION_ANALYSIS`
- `EGRESS_ANALYSIS`
- `ACCESSIBILITY_ANALYSIS`
- `DAYLIGHT_ANALYSIS`
- `SOLAR_ANALYSIS`
- `VENTILATION_ANALYSIS`
- `AIR_QUALITY_ANALYSIS`
- `THERMAL_ANALYSIS`
- `ACOUSTIC_ANALYSIS`
- `PRIVACY_ANALYSIS`
- `VISIBILITY_ANALYSIS`
- `ERGONOMIC_ANALYSIS`
- `ENERGY_ANALYSIS`
- `SANITARY_ANALYSIS`
- `COST_ANALYSIS`
- `LIFECYCLE_ANALYSIS`

No capability ID is created. A future capability profile must declare required variables and use the S7-P0.5 availability states separately from matrix requirement.

## 13. Design Knowledge and Regulatory Relationships

Design Knowledge may inform space proportions, adjacency patterns, circulation principles, privacy strategies, daylight strategies, furniture layouts, and design patterns. It remains advisory:

```text
DesignKnowledge
        ↓ advisory reference
VariableDefinition / ScaleVariableProfile
        ↓ explicit project adoption
ProjectVariable
```

Design Knowledge is not a value and does not create a decision.

Regulatory relationships remain:

```text
Regulation
        ↓
Evidence / NormativeInterpretation
        ↓
Constraint
        ↓
space-variable relation
```

Accessibility, egress, fire, occupancy, sanitary, electrical, and clear-width requirements may be normative. A regulatory requirement is not automatically a project variable value. Human review is required before interpretation becomes a project constraint.

## 14. Derived Metrics

Candidate derived metrics include:

- floor area from space geometry;
- volume from area and height or 3D geometry;
- occupancy density from occupancy and area;
- opening-to-wall ratio from openings and envelope geometry;
- daylight metrics from openings, geometry, solar position, and light inputs;
- ventilation metrics from airflow inputs, openings, schedules, and geometry;
- thermal metrics from observations, envelope inputs, schedules, and models;
- acoustic metrics from material, geometry, and sound inputs;
- circulation efficiency from paths, clear widths, and space relations;
- estimated cost from area, assemblies, assumptions, and declared cost inputs.

No formulas are implemented. No metric is automatically converted into an Evaluation record.

## 15. Gaps and Decisions

Open decisions include:

1. Which space variable definitions require formal catalog governance?
2. Which unit and time registries will be authoritative?
3. How are conditional expressions represented without a typology ontology?
4. How are actual occupancy and design capacity versioned?
5. Which environmental inputs are accepted for each analysis?
6. How are openings represented without duplicating object-scale door/window properties?
7. How are space-level and building-level metrics linked without identity collision?
8. Which source classes require Evidence and retrieval timestamps?
9. How are normative interpretations reviewed and signed?
10. Which candidate capabilities become canonical after implementation evidence?
11. What is the next scale for MV-P0.4?
12. How will MV-P0.13 perform global cross-scale deduplication?

Before implementation, the Product Owner must review the 36 records, requirement counts, conditional cases, and cross-scale distinctions.

## Final Gate

MV_P0_3_SPECIFICATION_ONLY = YES

SPACE_VARIABLE_MATRIX_DEFINED = YES

SPACE_MINIMUM_PROFILE_DEFINED = YES

SPACE_COMPLETE_PROFILE_DEFINED = YES

SPATIAL_SCOPE = espacio

VARIABLE_COUNT = 36

MINIMUM_PROFILE_COUNT = 18

COMPLETE_PROFILE_COUNT = 36

REQUIRED_COUNT = 18

RECOMMENDED_COUNT = 11

OPTIONAL_COUNT = 4

CONDITIONAL_NOT_APPLICABLE_COUNT = 3

DUPLICATE_IDS = 0

CROSS_SCALE_REUSE_CANDIDATES = 9

DISTINCT_FROM_OBJECT_VARIABLES = YES

ENVIRONMENTAL_MODEL_SEPARATION = PASS

OCCUPANCY_SEMANTICS = PASS

CONDITIONAL_APPLICABILITY = PASS

PROVENANCE = PASS

SOURCE_CLASSES = PASS

DESIGN_KNOWLEDGE_RELATIONSHIP = PASS

REGULATORY_RELATIONSHIP = PASS

CAPABILITY_RELATIONSHIP = PASS — conceptual links only

REAL_DATA_LOADED = NO
PRODUCT_CODE_CHANGED = NO
WEB_CHANGED = NO
DATABASE_CHANGED = NO
API_CHANGED = NO
MAIN_MODIFIED = NO
DEPLOYED = NO

BLOCKERS = Product Owner review is required before MV-P0.4; no implementation blocker exists because implementation is explicitly out of scope.

MV_P0_3 = PASS

READY_FOR_MV_P0_4 = NO — pending review and next-scale authorization.

**STOP.**

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SiMS-DeI SICL Core repository"
[2]: https://github.com/YvanCastilloQuezada/sicl-web "SiMS-DeI SICL Web repository"
