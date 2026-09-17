# MV-P0.2 — Object-Scale Variable Matrix

**Project:** SiMS-DeI / SICL
**Program:** MV-P0 — Multiscale Variable Matrix Definition
**Status:** AUTHORIZED FOR VARIABLE MATRIX SPECIFICATION
**Product implementation:** NOT AUTHORIZED
**SpatialScope:** `objeto`
**Lineage:** MV-P0.1 common schema, commit `c7d9cdee2aaa6a8ee7ccabc304515bc8a444336d`

> This document specifies an empty-to-populatable object-scale variable matrix. It defines semantic records only. It does not create a runtime catalog, load project data, create entities, add database tables, add APIs, or modify the Core.

## 1. Executive Summary

MV-P0.2 defines the first concrete multiscale variable matrix for `SpatialScope = objeto`. Object means a spatial or design component that may be evaluated independently or as part of a larger system. Examples include furniture, equipment, facade components, shading devices, lighting components, urban furniture, modular elements, prefabricated elements, doors, windows, solar components, and signage or accessibility components.

The matrix deliberately remains compact. It contains **39 conceptual variable records** across the main object-design families. Three records are conditional `NOT_APPLICABLE` examples, which demonstrates that applicability depends on object type and context rather than on `SpatialScope` alone.

The object minimum profile contains **14 records**. The recommended complete profile contains all **39 records**, including conditional families. No real project values, manufacturer values, external datasets, or fabricated measurements are included.

The matrix preserves the MV-P0.1 chain:

```text
VariableDefinition
        ↓
ScaleVariableProfile
        ↓
SuggestedVariable
        ↓
ProjectVariable
```

`Fact`, `Assumption`, `Objective`, `Constraint`, `Source`, `Evidence`, `Evaluation`, `Recommendation`, `HumanReview`, and `Decision` remain separate canonical concepts.

## 2. Governing Contract

The governing architecture is MV-P0.1. IDs are stable, semantic, and language independent. Visible labels are not IDs. Every matrix record uses `spatial_scope = objeto`.

The matrix defines variable meaning and profile applicability. It does not define a project value. A future `ProjectVariable` may adopt one of these definitions only through an explicit project action with actor and authority.

Requirement values are `REQUIRED`, `RECOMMENDED`, `OPTIONAL`, and `NOT_APPLICABLE`. Capability states are not used as requirement values. Provenance values describe actual values or observations, not abstract definitions.

## 3. Object Scale Definition

`objeto` is the scale at which a component, element, artifact, device, or design object can be described and evaluated as a coherent unit. The object may be physically independent, embedded in a building, located in a public space, or connected to a larger system.

This definition does not create a typology ontology. The examples below are explanatory contexts for conditional applicability, not a closed classification system.

Object-scale design intelligence should answer questions about identity, function, geometry, position, material, human interaction, safety, fabrication, assembly, maintenance, durability, cost, and selected environmental or regulatory properties.

## 4. Design Questions

The matrix must support at least these questions:

1. What object is being designed or evaluated?
2. What function does it serve?
3. What dimensions and shape are required?
4. Where is it positioned in its containing space or system?
5. How is it oriented?
6. What material or material system is used?
7. Can a person use it safely and comfortably?
8. Does it meet relevant accessibility clearances?
9. Does it fit its containing space and nearby objects?
10. Can it be fabricated, transported, assembled, and installed?
11. What maintenance does it require?
12. What durability or lifecycle conditions matter?
13. What does it cost as a conceptual design metric?
14. Does environmental exposure affect performance?
15. Does a regulation constrain a dimension, material, or performance property?
16. Which values are design-controllable, contextual, assumed, measured, or derived?

The matrix does not decide answers. It identifies the semantic variables needed to ask and evaluate them.

## 5. Variable Families

The matrix covers the following families:

| Family | Purpose at object scale |
|---|---|
| Identity / classification | Identify and classify the object without creating a typology ontology |
| Function | Describe intended use and functional role |
| Geometry | Describe dimensions and shape |
| Position / orientation | Locate and orient the object in its context |
| Spatial relation | Describe containment, adjacency, clearance, and connection |
| Material | Describe material selection and finish |
| Physical properties | Describe mass, weight, density, and related properties |
| Human / ergonomics | Describe human interaction and fit |
| Accessibility | Describe accessible use and clearance |
| Safety | Describe safety-related conditions |
| Structural / mechanical performance | Describe loads, resistance, and mechanical behavior where applicable |
| Environmental performance | Describe environmental exposure or response where applicable |
| Energy | Describe consumption or generation where applicable |
| Light / solar | Describe light and solar relationships where applicable |
| Acoustic | Describe acoustic properties where applicable |
| Fire | Describe fire performance where applicable |
| Fabrication | Describe production requirements |
| Assembly / installation | Describe joining, placement, and installation |
| Maintenance / durability | Describe upkeep and expected service behavior |
| Lifecycle / cost | Describe conceptual cost and lifecycle information |
| Design intent | Record representable non-factual intent without claiming subjective judgment is objective |
| Regulatory reference | Link potential normative constraints through Regulation, Evidence, Interpretation, and Constraint |

No family is assumed applicable to every object.

## 6. Object Minimum Dataset

The minimum profile contains 14 records:

| ID | Concept | Why minimum |
|---|---|---|
| `OBJECT_ID` | Stable object identity | Distinguishes the object instance or design subject |
| `OBJECT_CLASS` | Object class label | Provides a controlled classification hook without creating a typology ontology |
| `OBJECT_FUNCTION` | Intended function | Establishes what the object is meant to do |
| `OBJECT_QUANTITY` | Count | Supports repeated elements and component quantities |
| `OBJECT_LENGTH` | Length | Establishes basic dimensional state |
| `OBJECT_WIDTH` | Width | Establishes basic dimensional state |
| `OBJECT_HEIGHT` | Height | Establishes basic dimensional state |
| `OBJECT_SHAPE` | Shape/geometry representation | Establishes basic geometric identity |
| `OBJECT_POSITION` | Position in containing context | Establishes spatial placement |
| `OBJECT_ORIENTATION` | Orientation | Establishes directional placement when meaningful |
| `OBJECT_MATERIAL` | Material choice or description | Establishes the primary material state |
| `OBJECT_CONTAINER_REFERENCE` | Containing space/system | Connects object to its larger context |
| `OBJECT_PRIMARY_OBJECTIVE` | Primary design objective reference | Connects the object to explicit design intent without becoming an Objective entity |
| `OBJECT_PROVENANCE` | Provenance metadata | Prevents synthetic or assumed data from appearing measured |

The minimum profile is intentionally not a complete performance model. It is the smallest useful state for object-scale design reasoning.

## 7. Recommended Complete Dataset

The complete profile contains the 14 minimum records plus 25 conditional or recommended records. It adds spatial relationships, material properties, human interaction, fabrication, lifecycle, performance, and design intent.

The complete profile does not apply universally. A passive furniture object may not need electrical power, solar orientation, acoustic absorption, or fire-resistance rating. A photovoltaic component may need solar orientation and electrical output. A shading device may need solar exposure and clearances. The profile uses conditions instead of separate object catalogs.

## 8. Variable Matrix

All records below use `spatial_scope = objeto`. The `source_class` field names source classes rather than specific vendors or institutions. Candidate capability links are marked `PROPOSED/FUTURE`; they are not runtime capabilities.

### 8.1 Identity, function, geometry, and context

| ID | Canonical name | Domain | Requirement | Role | Data type | Unit semantics | Temporal semantics | Spatial resolution | Applicability | Provenance | Source class | Capability links | Description |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `OBJECT_ID` | Object identity | IDENTITY | REQUIRED | CONTEXT | STRING | unitless | PROJECT_STATE | OBJECT | All object-scale records | REAL or ASSUMED | USER_INPUT, DESIGN_DOCUMENT | None | Stable identity for the design subject |
| `OBJECT_CLASS` | Object class | IDENTITY | REQUIRED | CLASSIFICATION | ENUM | unitless | PROJECT_STATE | OBJECT | All object-scale records; label is not a typology ontology | REAL, ASSUMED, or SYNTHETIC | USER_INPUT, DESIGN_DOCUMENT | None | Controlled classification hook |
| `OBJECT_FUNCTION` | Object function | FUNCTION | REQUIRED | DESIGN_VARIABLE | ENUM or STRING | unitless | PROJECT_STATE | OBJECT | All objects with an intended function | ASSUMED or DESIGN_DOCUMENT | USER_INPUT, DESIGN_DOCUMENT | PROPOSED/FUTURE OBJECT_GEOMETRY_ANALYSIS | Intended use or functional role |
| `OBJECT_QUANTITY` | Object quantity | IDENTITY | REQUIRED | PARAMETER | INTEGER | unitless count | PROJECT_STATE | OBJECT | Repeated or counted objects | REAL, ASSUMED, or SYNTHETIC | USER_INPUT, MEASUREMENT | PROPOSED/FUTURE OBJECT_GEOMETRY_ANALYSIS | Number of equivalent objects |
| `OBJECT_SHAPE` | Object shape/geometry | GEOMETRY | REQUIRED | DESIGN_VARIABLE | GEOMETRY | geometry-dependent | PROJECT_STATE or DESIGN_REVISION | OBJECT | All objects represented geometrically | DESIGN_DOCUMENT, SYNTHETIC, or REAL | DESIGN_DOCUMENT, BIM_MODEL, MEASUREMENT | PROPOSED/FUTURE OBJECT_GEOMETRY_ANALYSIS | Geometric representation without assuming a particular file format |
| `OBJECT_LENGTH` | Object length | GEOMETRY | REQUIRED | DESIGN_VARIABLE | DECIMAL | length | PROJECT_STATE | OBJECT | Objects for which length is meaningful; otherwise `NOT_APPLICABLE` | REAL, ASSUMED, or SYNTHETIC | USER_INPUT, DESIGN_DOCUMENT, MEASUREMENT | PROPOSED/FUTURE OBJECT_GEOMETRY_ANALYSIS | Primary linear dimension |
| `OBJECT_WIDTH` | Object width | GEOMETRY | REQUIRED | DESIGN_VARIABLE | DECIMAL | length | PROJECT_STATE | OBJECT | Objects for which width is meaningful; otherwise `NOT_APPLICABLE` | REAL, ASSUMED, or SYNTHETIC | USER_INPUT, DESIGN_DOCUMENT, MEASUREMENT | PROPOSED/FUTURE OBJECT_GEOMETRY_ANALYSIS | Primary transverse dimension |
| `OBJECT_HEIGHT` | Object height | GEOMETRY | REQUIRED | DESIGN_VARIABLE | DECIMAL | length | PROJECT_STATE | OBJECT | Objects for which height is meaningful; otherwise `NOT_APPLICABLE` | REAL, ASSUMED, or SYNTHETIC | USER_INPUT, DESIGN_DOCUMENT, MEASUREMENT | PROPOSED/FUTURE OBJECT_GEOMETRY_ANALYSIS | Primary vertical dimension |
| `OBJECT_POSITION` | Object position | POSITION | REQUIRED | DESIGN_VARIABLE | GEOMETRY or REFERENCE | length/coordinate | PROJECT_STATE | OBJECT within containing context | Objects located in a space or system | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, BIM_MODEL, MEASUREMENT | PROPOSED/FUTURE OBJECT_GEOMETRY_ANALYSIS | Position relative to an explicit reference frame |
| `OBJECT_ORIENTATION` | Object orientation | POSITION | REQUIRED | DESIGN_VARIABLE | DECIMAL | angle | PROJECT_STATE | OBJECT within containing context | Directional, solar, or aligned objects; otherwise `NOT_APPLICABLE` | REAL, ASSUMED, or SYNTHETIC | USER_INPUT, DESIGN_DOCUMENT, MEASUREMENT | PROPOSED/FUTURE OBJECT_GEOMETRY_ANALYSIS | Orientation relative to a declared frame |
| `OBJECT_MATERIAL` | Object material | MATERIAL | REQUIRED | DESIGN_VARIABLE | ENUM or STRING | unitless/material identity | PROJECT_STATE | OBJECT | Objects with a material choice | REAL, ASSUMED, or SYNTHETIC | USER_INPUT, DESIGN_DOCUMENT, MANUFACTURER_DATA | PROPOSED/FUTURE MATERIAL_ANALYSIS | Primary material or material system |
| `OBJECT_CONTAINER_REFERENCE` | Containing space/system | SPATIAL_RELATION | REQUIRED | CONTEXT | REFERENCE | unitless reference | PROJECT_STATE | SPACE or SYSTEM reference | Objects embedded in a larger context | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, BIM_MODEL, USER_INPUT | PROPOSED/FUTURE OBJECT_GEOMETRY_ANALYSIS | Reference to containing context |
| `OBJECT_PRIMARY_OBJECTIVE` | Primary object design objective | FUNCTION | REQUIRED | CONTEXT | REFERENCE | unitless reference | PROJECT_STATE | OBJECT | All object designs with an explicit purpose | ASSUMED or DESIGN_DOCUMENT | USER_INPUT, DESIGN_DOCUMENT | None | Reference to an Objective without replacing Objective |

### 8.2 Spatial relationships, human use, material properties, and performance

| ID | Canonical name | Domain | Requirement | Role | Data type | Unit semantics | Temporal semantics | Spatial resolution | Applicability | Provenance | Source class | Capability links | Description |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `OBJECT_CLEARANCE` | Object clearance | ACCESSIBILITY | RECOMMENDED | DESIGN_VARIABLE | DECIMAL or COLLECTION | length | PROJECT_STATE | OBJECT/SPACE relation | When human movement, operation, or safety requires clearance | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, TECHNICAL_STANDARD, MEASUREMENT | PROPOSED/FUTURE ACCESSIBILITY_ANALYSIS | Required free distance around or within the object |
| `OBJECT_ADJACENCY` | Object adjacency relation | SPATIAL_RELATION | RECOMMENDED | CONTEXT | COLLECTION | relation | PROJECT_STATE | OBJECT/SPACE relation | When nearby objects affect use or performance | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, BIM_MODEL, MEASUREMENT | PROPOSED/FUTURE OBJECT_GEOMETRY_ANALYSIS | Explicit neighboring-object relationship |
| `OBJECT_CONNECTION` | Object connection relation | ASSEMBLY | RECOMMENDED | DESIGN_VARIABLE | COLLECTION | relation | PROJECT_STATE | OBJECT/SYSTEM relation | Modular, mechanical, electrical, or structural connections | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, MANUFACTURER_DATA | PROPOSED/FUTURE ASSEMBLY_ANALYSIS | Connection to another component or system |
| `OBJECT_SURFACE_FINISH` | Surface finish | MATERIAL | RECOMMENDED | DESIGN_VARIABLE | ENUM or STRING | unitless | PROJECT_STATE | OBJECT surface | When finish affects use, maintenance, appearance, or performance | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, MANUFACTURER_DATA, TECHNICAL_STANDARD | PROPOSED/FUTURE MATERIAL_ANALYSIS | Finish or surface treatment |
| `OBJECT_MASS` | Object mass | PHYSICAL | RECOMMENDED | DERIVED_METRIC | DECIMAL | mass | PROJECT_STATE or DERIVED | OBJECT | When handling, support, transport, or structural effects matter | REAL, APPROXIMATED, ASSUMED, or SYNTHETIC | MEASUREMENT, MANUFACTURER_DATA, DERIVED | PROPOSED/FUTURE MATERIAL_ANALYSIS | Mass of the object or assembly |
| `OBJECT_WEIGHT` | Object weight | PHYSICAL | RECOMMENDED | DERIVED_METRIC | DECIMAL | force | PROJECT_STATE or DERIVED | OBJECT | When support, lifting, transport, or anchoring matters | REAL, APPROXIMATED, ASSUMED, or SYNTHETIC | MEASUREMENT, DERIVED | PROPOSED/FUTURE STRUCTURAL_ANALYSIS | Weight derived from mass and declared model |
| `OBJECT_DENSITY` | Object density | PHYSICAL | OPTIONAL | INPUT | DECIMAL | mass/volume | PROJECT_STATE | OBJECT material | When material or physical response requires density | REAL, APPROXIMATED, ASSUMED, or SYNTHETIC | MANUFACTURER_DATA, TECHNICAL_STANDARD, MEASUREMENT | PROPOSED/FUTURE MATERIAL_ANALYSIS | Density of material or assembly |
| `OBJECT_ANTHROPOMETRIC_FIT` | Anthropometric fit | HUMAN | RECOMMENDED | DERIVED_METRIC | ENUM or COLLECTION | fit classification | PROJECT_STATE or DERIVED | OBJECT/user relation | Human-use objects; conditional by user group and task | REAL, APPROXIMATED, ASSUMED, or SYNTHETIC | MEASUREMENT, TECHNICAL_STANDARD, DERIVED | PROPOSED/FUTURE ERGONOMIC_ANALYSIS | Fit assessment against declared user criteria |
| `OBJECT_ACCESSIBILITY_CLEARANCE` | Accessibility clearance | ACCESSIBILITY | RECOMMENDED | CONSTRAINT | DECIMAL or COLLECTION | length | PROJECT_STATE | OBJECT/SPACE relation | Objects intended for accessible use or circulation | REAL, ASSUMED, or SYNTHETIC | TECHNICAL_STANDARD, DESIGN_DOCUMENT, MEASUREMENT | PROPOSED/FUTURE ACCESSIBILITY_ANALYSIS | Clearance relevant to accessible use |
| `OBJECT_SAFE_USE_CONDITION` | Safe-use condition | SAFETY | RECOMMENDED | CONSTRAINT | ENUM or COLLECTION | unitless | PROJECT_STATE | OBJECT/user relation | Objects with human contact, movement, load, or hazard | REAL, ASSUMED, or SYNTHETIC | TECHNICAL_STANDARD, DESIGN_DOCUMENT, MEASUREMENT | PROPOSED/FUTURE SAFETY_ANALYSIS | Declared condition required for safe use |

### 8.3 Conditional environmental, fabrication, lifecycle, and regulatory variables

| ID | Canonical name | Domain | Requirement | Role | Data type | Unit semantics | Temporal semantics | Spatial resolution | Applicability | Provenance | Source class | Capability links | Description |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `OBJECT_STRUCTURAL_RESISTANCE` | Structural resistance | STRUCTURE | RECOMMENDED | INPUT | DECIMAL or COLLECTION | force/stress | PROJECT_STATE | OBJECT/system relation | Load-bearing or mechanically stressed objects | REAL, APPROXIMATED, ASSUMED, or SYNTHETIC | TECHNICAL_STANDARD, MANUFACTURER_DATA, MEASUREMENT, SIMULATION | PROPOSED/FUTURE STRUCTURAL_ANALYSIS | Resistance property or requirement |
| `OBJECT_THERMAL_PROPERTY` | Thermal property | ENVIRONMENT | OPTIONAL | INPUT | DECIMAL or COLLECTION | thermal dimension | PROJECT_STATE | OBJECT/material | Components whose thermal behavior matters | REAL, APPROXIMATED, ASSUMED, or SYNTHETIC | MANUFACTURER_DATA, TECHNICAL_STANDARD, MEASUREMENT, SIMULATION | PROPOSED/FUTURE ENERGY_ANALYSIS | Thermal property such as conductivity or resistance |
| `OBJECT_ACOUSTIC_PROPERTY` | Acoustic property | ACOUSTIC | NOT_APPLICABLE | INPUT | DECIMAL or COLLECTION | acoustic dimension | PROJECT_STATE | OBJECT/material | `NOT_APPLICABLE` for objects with no acoustic design role; otherwise conditional | REAL, APPROXIMATED, ASSUMED, or SYNTHETIC | MANUFACTURER_DATA, TECHNICAL_STANDARD, MEASUREMENT, SIMULATION | PROPOSED/FUTURE ACOUSTIC_ANALYSIS | Acoustic absorption, isolation, or emission property |
| `OBJECT_FIRE_PERFORMANCE` | Fire performance | FIRE | NOT_APPLICABLE | CONSTRAINT | ENUM or COLLECTION | classification | PROJECT_STATE | OBJECT/material | `NOT_APPLICABLE` for objects with no applicable fire requirement; otherwise conditional | REAL, ASSUMED, or SYNTHETIC | TECHNICAL_STANDARD, MANUFACTURER_DATA, REGULATION | PROPOSED/FUTURE FIRE_ANALYSIS | Fire behavior or required classification |
| `OBJECT_ELECTRICAL_POWER` | Electrical power | ELECTRICAL | NOT_APPLICABLE | INPUT | DECIMAL | power | PROJECT_STATE | OBJECT/system relation | `NOT_APPLICABLE` to passive objects; conditional for powered components | REAL, ASSUMED, or SYNTHETIC | MANUFACTURER_DATA, MEASUREMENT, TECHNICAL_STANDARD | PROPOSED/FUTURE ENERGY_ANALYSIS | Electrical consumption or rated power |
| `OBJECT_SOLAR_ORIENTATION` | Solar orientation | LIGHT / SOLAR | OPTIONAL | DESIGN_VARIABLE | DECIMAL | angle | PROJECT_STATE | OBJECT/site relation | Shading, photovoltaic, daylight, or solar-responsive objects | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, MEASUREMENT, SIMULATION | PROPOSED/FUTURE SOLAR_ANALYSIS | Orientation used for solar interaction |
| `OBJECT_SOLAR_EXPOSURE` | Solar exposure | LIGHT / SOLAR | OPTIONAL | DERIVED_METRIC | DECIMAL or COLLECTION | irradiance/energy-area | OBSERVATION or DERIVED | OBJECT/site relation | Solar-responsive objects or exposure analysis | REAL, APPROXIMATED, ASSUMED, or SYNTHETIC | MEASUREMENT, SIMULATION, DERIVED | PROPOSED/FUTURE SOLAR_ANALYSIS | Derived exposure metric; not a raw input |
| `OBJECT_FABRICATION_METHOD` | Fabrication method | FABRICATION | RECOMMENDED | DESIGN_VARIABLE | ENUM or STRING | unitless | PROJECT_STATE | OBJECT/product | Manufactured, prefabricated, or fabricated objects | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, MANUFACTURER_DATA | PROPOSED/FUTURE FABRICATION_ANALYSIS | Production method or process |
| `OBJECT_ASSEMBLY_METHOD` | Assembly method | ASSEMBLY | RECOMMENDED | DESIGN_VARIABLE | ENUM or STRING | unitless | PROJECT_STATE | OBJECT/system relation | Objects assembled on site or in production | REAL, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, MANUFACTURER_DATA, TECHNICAL_STANDARD | PROPOSED/FUTURE ASSEMBLY_ANALYSIS | Joining or installation method |
| `OBJECT_MAINTENANCE_INTERVAL` | Maintenance interval | MAINTENANCE | OPTIONAL | PARAMETER | DURATION | duration | PROJECT_STATE or MULTIYEAR | OBJECT | Objects requiring planned maintenance; otherwise conditional | REAL, APPROXIMATED, ASSUMED, or SYNTHETIC | MANUFACTURER_DATA, TECHNICAL_STANDARD, MEASUREMENT | PROPOSED/FUTURE LIFECYCLE_ANALYSIS | Expected interval between maintenance actions |
| `OBJECT_DURABILITY_PERIOD` | Durability period | DURABILITY | OPTIONAL | PARAMETER | DURATION | duration | MULTIYEAR | OBJECT/material | Objects with a declared service-life requirement | REAL, APPROXIMATED, ASSUMED, or SYNTHETIC | MANUFACTURER_DATA, TECHNICAL_STANDARD, MEASUREMENT | PROPOSED/FUTURE LIFECYCLE_ANALYSIS | Expected durability period |
| `OBJECT_ESTIMATED_COST` | Estimated cost | COST | OPTIONAL | DERIVED_METRIC | DECIMAL | currency | PROJECT_STATE or DERIVED | OBJECT | When cost comparison is explicitly in scope | APPROXIMATED, ASSUMED, or SYNTHETIC | DESIGN_DOCUMENT, DERIVED, USER_INPUT | PROPOSED/FUTURE COST_ANALYSIS | Conceptual cost metric; not a financial fact |
| `OBJECT_LIFECYCLE_IMPACT` | Lifecycle impact | LIFECYCLE | OPTIONAL | DERIVED_METRIC | COLLECTION | declared metric semantics | MULTIYEAR | OBJECT/material | Objects evaluated across production, use, maintenance, and end-of-life | APPROXIMATED, ASSUMED, or SYNTHETIC | SIMULATION, DERIVED, TECHNICAL_STANDARD | PROPOSED/FUTURE LIFECYCLE_ANALYSIS | Conceptual lifecycle metric |
| `OBJECT_DESIGN_INTENT` | Design intent | IDENTITY | RECOMMENDED | CONTEXT | STRING or COLLECTION | unitless | PROJECT_STATE | OBJECT | All objects where explicit intent is useful | ASSUMED or DESIGN_DOCUMENT | USER_INPUT, DESIGN_DOCUMENT, DESIGN_KNOWLEDGE | None | Representable intent; not an objective fact or aesthetic truth |
| `OBJECT_NORMATIVE_REFERENCE` | Normative reference | REGULATION | RECOMMENDED | REFERENCE | REFERENCE or COLLECTION | unitless reference | PROJECT_STATE | OBJECT | When a regulation, standard, or municipal rule may constrain the object | REAL or NOT_AVAILABLE | TECHNICAL_STANDARD, OFFICIAL_SOURCE, REGULATION | PROPOSED/FUTURE REGULATORY_ANALYSIS | Reference to normative material, not automatic compliance |

## 9. Conditional Applicability

The matrix demonstrates conditional applicability without creating separate object catalogs.

| Variable | Example condition | Requirement when condition is false |
|---|---|---|
| `OBJECT_STRUCTURAL_RESISTANCE` | Load-bearing, suspended, anchored, or mechanically stressed object | `NOT_APPLICABLE` may be resolved in a future profile |
| `OBJECT_THERMAL_PROPERTY` | Thermal transfer or insulation is part of the design question | `NOT_APPLICABLE` may be resolved in a future profile |
| `OBJECT_ACOUSTIC_PROPERTY` | Object has an acoustic function or affects acoustic transmission | Matrix uses a legitimate `NOT_APPLICABLE` baseline |
| `OBJECT_FIRE_PERFORMANCE` | Applicable regulation or hazard class exists | Matrix uses a legitimate `NOT_APPLICABLE` baseline |
| `OBJECT_ELECTRICAL_POWER` | Object consumes or generates electricity | Matrix uses a legitimate `NOT_APPLICABLE` baseline |
| `OBJECT_SOLAR_ORIENTATION` | Photovoltaic, shading, daylight, or solar-response purpose | It may be optional or not applicable |
| `OBJECT_SOLAR_EXPOSURE` | Solar exposure is relevant to the design question | It may be not applicable |
| `OBJECT_MAINTENANCE_INTERVAL` | Maintenance is planned or operationally relevant | It may remain optional |

`NOT_APPLICABLE` is a profile result, not a universal statement that the domain never applies to `objeto`.

## 10. Requirement Classification

The 39 records are classified as follows:

| Requirement | Count | Interpretation |
|---|---:|---|
| `REQUIRED` | 14 | Minimum object state |
| `RECOMMENDED` | 9 | Broadly useful, but not always workflow-blocking |
| `OPTIONAL` | 5 | Useful when a design question requires it |
| `NOT_APPLICABLE` | 3 | Legitimate baseline examples for conditional families |
| **Total** | **39** | **No artificial target** |

The three `NOT_APPLICABLE` records are `OBJECT_ACOUSTIC_PROPERTY`, `OBJECT_FIRE_PERFORMANCE`, and `OBJECT_ELECTRICAL_POWER`. The matrix record remains available for conditional reclassification; the record is not deleted.

## 11. Types and Units

The matrix uses conceptual type semantics only:

- Length and dimensions use `DECIMAL / length`.
- Quantity uses `INTEGER / unitless count`.
- Orientation uses `DECIMAL / angle`.
- Geometry uses `GEOMETRY / geometry-dependent`.
- Material and classifications use `ENUM` or `STRING / unitless`.
- Cost uses `DECIMAL / currency` without selecting a currency or conversion engine.
- Durability and maintenance use `DURATION / duration`.
- Metrics use declared dimensions and provenance.

No conversion, range validation, serialization, or unit registry is implemented.

## 12. Provenance

The matrix defines acceptable provenance classes and does not assign actual values. `REAL` is appropriate for measured or authoritative data. `APPROXIMATED` is appropriate only when an approximation method is declared. `ASSUMED` is appropriate for an explicit project assumption. `SYNTHETIC` is appropriate for educational or test data. `NOT_AVAILABLE` means the required source or value is unavailable.

A future project record must preserve Source and Evidence links. A matrix row does not claim that any source exists.

## 13. Source Classes

The matrix uses these source classes:

- `USER_INPUT`
- `DESIGN_DOCUMENT`
- `MANUFACTURER_DATA`
- `TECHNICAL_STANDARD`
- `MEASUREMENT`
- `SIMULATION`
- `DERIVED`
- `OFFICIAL_SOURCE`
- `BIM_MODEL` as a design-document class extension when formally governed

These are source classes, not specific providers. A future Source record must carry actual source metadata and Evidence where the project uses the variable.

## 14. Design Knowledge Relationships

Design Knowledge may inform recommended dimensions, proportions, ergonomic ranges, spatial relationships, material selection, assembly, maintenance, and design principles. It may provide a strategy candidate, reference range, or open question.

The relationship is advisory:

```text
DesignKnowledgeItem / DesignPattern
        ↓ advisory reference
VariableDefinition / ScaleVariableProfile
        ↓ explicit project adoption if desired
ProjectVariable
```

Design Knowledge does not create a variable value, constraint, recommendation, review, or decision. A design pattern may suggest that a dimension deserves attention, but it does not establish a mandatory dimension.

## 15. Regulatory Relationships

Potential object-scale normative families include accessibility dimensions, fire performance, safety, electrical properties, and structural performance.

The preserved relationship is:

```text
Regulation
        ↓
Evidence / NormativeInterpretation
        ↓
Constraint
        ↓
Variable relation
```

A normative reference row is not proof of compliance. A regulation does not automatically become a value. Human review remains required before a normative interpretation is treated as a project constraint.

## 16. Capability Relationships

The matrix identifies candidate capability relationships only. No runtime capability IDs are created. Candidate links are marked `PROPOSED/FUTURE`:

- `OBJECT_GEOMETRY_ANALYSIS`
- `ERGONOMIC_ANALYSIS`
- `ACCESSIBILITY_ANALYSIS`
- `MATERIAL_ANALYSIS`
- `STRUCTURAL_ANALYSIS`
- `SAFETY_ANALYSIS`
- `SOLAR_ANALYSIS`
- `ENERGY_ANALYSIS`
- `ACOUSTIC_ANALYSIS`
- `FIRE_ANALYSIS`
- `FABRICATION_ANALYSIS`
- `ASSEMBLY_ANALYSIS`
- `LIFECYCLE_ANALYSIS`
- `COST_ANALYSIS`

A future capability profile may declare required variables. Capability availability must remain distinct from matrix requirement.

## 17. State Variables vs Design Variables

The matrix deliberately distinguishes information types:

| Category | Examples |
|---|---|
| Context/input information | `OBJECT_CONTAINER_REFERENCE`, `OBJECT_POSITION`, existing material, measured dimensions |
| Design-controllable variables | `OBJECT_LENGTH`, `OBJECT_WIDTH`, `OBJECT_HEIGHT`, `OBJECT_MATERIAL`, `OBJECT_ORIENTATION`, `OBJECT_FABRICATION_METHOD` |
| Constraints | `OBJECT_CLEARANCE`, `OBJECT_ACCESSIBILITY_CLEARANCE`, `OBJECT_SAFE_USE_CONDITION`, `OBJECT_FIRE_PERFORMANCE` |
| Derived metrics | `OBJECT_MASS`, `OBJECT_WEIGHT`, `OBJECT_SOLAR_EXPOSURE`, `OBJECT_ESTIMATED_COST`, `OBJECT_LIFECYCLE_IMPACT` |
| Intent/context | `OBJECT_FUNCTION`, `OBJECT_PRIMARY_OBJECTIVE`, `OBJECT_DESIGN_INTENT` |

These categories do not replace Fact, Assumption, Objective, Constraint, or Evaluation. They describe how a future variable profile may be used.

## 18. Derived Metrics

Candidate derived metrics are kept separate from input variables:

- volume from geometry;
- surface area from geometry;
- mass from volume and density;
- weight from mass and declared gravitational model;
- material quantity from geometry and material specification;
- clearance compliance from geometry, user criteria, and constraints;
- ergonomic fit from geometry and anthropometric criteria;
- solar exposure from geometry, orientation, solar position, and environmental inputs;
- estimated cost from quantity, material, fabrication, and declared cost assumptions.

No formula or computation engine is implemented. No metric is claimed to be a real measurement.

## 19. Cross-Scale Reuse Candidates

The following IDs are candidates for later cross-scale review, not final global identity decisions:

- `OBJECT_LENGTH` may relate to `length` concepts at `espacio`, `edificacion`, or `sistema`.
- `OBJECT_WIDTH` may relate to width concepts at other scales.
- `OBJECT_HEIGHT` may relate to height concepts at `edificacion` or `espacio`.
- `OBJECT_ORIENTATION` may relate to orientation in site or building analysis.
- `OBJECT_MATERIAL` may relate to material at building or system scale.
- `OBJECT_ESTIMATED_COST` may relate to cost at larger scales.
- `OBJECT_POSITION` may relate to position and coordinates at parcel or building scale.

Global deduplication is explicitly deferred to MV-P0.13. Reuse requires semantic, dimensional, temporal, spatial-support, derivation, and decision-use compatibility.

## 20. NOT_APPLICABLE Examples

The matrix proves the following legitimate cases:

1. `OBJECT_ELECTRICAL_POWER` is `NOT_APPLICABLE` to a passive furniture object with no electrical function.
2. `OBJECT_ACOUSTIC_PROPERTY` is `NOT_APPLICABLE` to an object with no acoustic function or material-performance question.
3. `OBJECT_FIRE_PERFORMANCE` is `NOT_APPLICABLE` where no applicable fire requirement or hazard classification is established.
4. `OBJECT_STRUCTURAL_RESISTANCE` is `NOT_APPLICABLE` for an un-loaded decorative object in a profile where structural performance is not a design question.

A photovoltaic or shading component can make `OBJECT_SOLAR_ORIENTATION` applicable. A powered component can make `OBJECT_ELECTRICAL_POWER` applicable. The same `SpatialScope` therefore supports different resolved profiles.

## 21. Gaps and Open Questions

The matrix does not decide the following implementation questions:

- Whether definition and profile records are stored in code, a repository, a database, or a hybrid.
- Whether geometry values use a dedicated geometry contract or remain references to BIM/GIS representations.
- Which unit registry is authoritative.
- Which source classes require specific evidence.
- How conditional expressions are represented.
- How profile version snapshots are exposed.
- How object classes are governed without creating a typology ontology.
- How manufacturer data are validated.
- How object metrics link to Evaluation and Pareto.
- Which candidate capabilities become canonical.
- How regulatory applicability is reviewed by human authority.

These decisions belong to later MV phases.

## 22. Decisions for MV-P0.3

MV-P0.3 should define the next spatial scope only after reviewing the object matrix’s identity reuse candidates and conditional semantics. It should not copy the 39 object records mechanically.

Before MV-P0.3, the Product Owner should decide whether the object matrix is sufficiently compact, whether any required family is missing, how `NOT_APPLICABLE` is resolved, and whether the next scale should prioritize `espacio` or follow the approved program sequence.

The next phase must preserve the same record contract and must not create independent applications per scale.

## 23. Evidence and Traceability

| Evidence | Use |
|---|---|
| MV-P0.1 common schema | Defines layers, requirements, data types, units, time, resolution, provenance, and human authority |
| MV-P0.0 audit | Establishes current implementation gaps and reuse principles |
| RFC-021 | Establishes current `SuggestedVariable` and `ProjectVariable` boundaries |
| S7-P0.5 capability reference | Establishes capability availability vocabulary without merging it into requirements |
| Existing `SpatialScope` | Establishes `objeto` as one canonical scale |

No external sources were researched. No external-source claims are made. No real data are loaded.

## Validation

- All matrix records use `spatial_scope = objeto`.
- Duplicate variable IDs = **0**.
- Every record has a requirement classification.
- Every record has a role classification.
- Every record has type semantics.
- Unit semantics are explicit, including unitless values.
- Conditional variables identify applicability conditions.
- No fabricated project values are present.
- No external-source claim is presented as evidence.
- Candidate capability links are explicitly marked `PROPOSED/FUTURE`.
- Constitutional entity separation is preserved.
- Human Authority is preserved.
- `git diff --check` = **PASS**.

## Final Gate

MV_P0_2_SPECIFICATION_ONLY = YES

OBJECT_VARIABLE_MATRIX_DEFINED = YES

OBJECT_MINIMUM_PROFILE_DEFINED = YES

OBJECT_COMPLETE_PROFILE_DEFINED = YES

CONDITIONAL_APPLICABILITY_PROVEN = YES

NOT_APPLICABLE_SEMANTICS_PROVEN = YES

READY_FOR_MV_P0_3 = NO — requires Product Owner review of the matrix and the decisions in section 22.

SPATIAL_SCOPE = objeto

VARIABLE_COUNT = 39

MINIMUM_PROFILE_COUNT = 14

COMPLETE_PROFILE_COUNT = 39

REQUIRED_COUNT = 14

RECOMMENDED_COUNT = 14

OPTIONAL_COUNT = 8

CONDITIONAL_NOT_APPLICABLE_COUNT = 3

CROSS_SCALE_REUSE_CANDIDATES = 7

DESIGN_VARIABLES_IDENTIFIED = YES

CONTEXT_INPUTS_IDENTIFIED = YES

DERIVED_METRICS_IDENTIFIED = YES

PROVENANCE_CONTRACT = PASS

SOURCE_CLASS_CONTRACT = PASS

DESIGN_KNOWLEDGE_RELATIONSHIP = PASS

REGULATORY_RELATIONSHIP = PASS

CAPABILITY_RELATIONSHIP = PASS — conceptual links only

DUPLICATE_IDS = 0

REAL_DATA_LOADED = NO
PRODUCT_CODE_CHANGED = NO
WEB_CHANGED = NO
DATABASE_CHANGED = NO
API_CHANGED = NO
NEW_DEPENDENCIES = NO
MAIN_MODIFIED = NO
DEPLOYED = NO

**STOP.**

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SiMS-DeI SICL Core repository"
[2]: https://github.com/YvanCastilloQuezada/sicl-web "SiMS-DeI SICL Web repository"
