> **DECISIÓN DEL PO (2026-10-28):** Se descongela este documento y las 12 Nuevas Cualidades (antes FFOs). Todas pasan a estado ACTIVATED. La implementación del "remainder" se hará en órdenes posteriores, cualidad por cualidad. El registro deja de ser "frozen" y pasa a ser "activo".

# SiMS-DeI — Master Registro de Nuevas Cualidades

**Document status:** Canonical documentary and architectural registry
**Product implementation authority:** None
**Baseline used for classification:** `main` at the documentation branch creation point
**Scope:** Classification and consolidation only

> **DOCUMENTED != AUTHORIZED != IMPLEMENTED != INTEGRATED != DEPLOYED**
>
> The presence of an order, related code, dependencies, tests, TODOs, partial implementation, or architectural compatibility does not authorize future product work. A frozen order may be activated only through an explicit Product Owner execution order that identifies the Nueva Cualidad or an explicitly named subset.

This registry separates already implemented foundations from frozen future scope. A partial implementation never activates its remainder. When a future scope is later implemented, this document must retain the historical frozen intent and record the implementation scope, commit SHA, and remaining frozen scope.

## 1. Executive classification summary

| Nueva Cualidad ID | Title | Status | Already implemented | Frozen remainder | Related locks | Activation required |
|---|---|---|---|---|---|---|
| NC-01 | S7 Environmental Spatial Intelligence — Remaining Scope | ACTIVATED | Open-Meteo source retrieval, solar temporal analysis foundation, provenance, confirmed-location integration, capability readiness, and environmental overlay foundation | Building-performance and advanced environmental intelligence | DL-MULTISCALE-ADAPTIVE-01..15 | YES for remainder |
| NC-02 | Advanced Spatial Location / Geographic Map / GIS | ACTIVATED | SpatialLocation lifecycle, EPSG:4326, manual coordinates, SVG coordinate selector, movable pin, human confirmation, history, and environmental linkage | Geographic basemap, MapLibre, geocoder, boundaries, GIS, cadastral and polygon workflows | DL-MULTISCALE-ADAPTIVE-01..15 | YES for remainder |
| NC-03 | Adaptive Multiscale Workspace | ACTIVATED | Eleven SpatialScopes, capability states, shared workspace direction, and initial capability resolver | Dynamic scale-aware composition, adaptive agents, visualization, and jurisdiction-aware UI | DL-MULTISCALE-ADAPTIVE-01..15 | YES for remainder |
| NC-04 | Multiscale Runtime Variable Catalog Completion | ACTIVATED | Runtime variable definitions, profiles, project-variable lineage foundation, and MV-P1 integration | Complete 119-variable catalog, unit registry, conditional requirements, snapshots, and overrides | MV-P0 locks; DL-MULTISCALE-VARIABLE | YES for remainder |
| NC-05 | Advanced Missing Data Intelligence | ACTIVATED | Present/missing/unknown/not-available distinctions, acquisition categories, Missing Data endpoint and capability linkage | Prioritization, guided acquisition, source discovery, extraction, uncertainty visualization, and impact explanation | DL-MULTISCALE-ADAPTIVE-04..10 | YES for remainder |
| NC-06 | Human Intent Intelligence & Guided Project Definition | ACTIVATED | Existing project forms and human-authority principles; no authorized NLP or intent runtime | Intent extraction, classification, clarification, attribution, conflict handling, and confirmation workflow | DL-PROJECT-INTELLIGENCE-01 | YES |
| NC-07 | Regulatory Intelligence | ACTIVATED | Regulatory entities, RNE fixture/corpus foundations, evidence linkage, and normative state concepts | Jurisdiction resolution, rule applicability, updates, conflict detection, snapshots, and explanations | RFC-025; constitutional authority locks | YES for remainder |
| NC-08 | Design Knowledge Intelligence | ACTIVATED | Initial design-knowledge entities, catalog/query agent foundation, and source/evidence separation | Complete repository, contextual retrieval, applicability explanation, and knowledge-assisted evaluation/generation | RFC-026; human-authority locks | YES for remainder |
| NC-09 | Generative Spatial Design & Alternative Evolution | ACTIVATED | SpatialRepresentation, deterministic UPAO-001 generator, synthetic alternatives, and A/B/C comparison | Parametric, constraint-aware, objective-aware, evolutionary, and AI-assisted generation | S2/S3 spatial locks; AI_GENERATES / HUMAN_DECIDES | YES for remainder |
| NC-10 | Advanced Evaluation, Simulation & Multiobjective Optimization | ACTIVATED | Evaluation, Comparison, raw Pareto, deterministic UPAO-001 dataset, and feasibility foundations | Expanded criteria, uncertainty, sensitivity, scenario analysis, robust optimization, and simulation envelopes | DL-S6P0-01..17; RFC-020 | YES for remainder |
| NC-11 | EL-P0 Multiscale Example Project Library & Data Standard | ACTIVATED | UPAO-001 educational example foundation | Eleven protected examples, working copies, reset semantics, datasets, and provenance library | EL-P0; DL-S6P0-01..03 | YES |
| NC-12 | Interoperability — GIS / BIM / IFC / External Engines | ACTIVATED | IFC read-only foundation, parcel snapshot/GIS boundary concepts, and adapter architecture | Full GIS/BIM exchange, mapping, round-trip, conflict resolution, and external-result ingestion | RFC-027/RFC-028; adapter boundary locks | YES for remainder |

**Current count:** 12 Nueva Cualidads. The classification contains 10 partially implemented orders with frozen remainders, 1 approved frozen order, and 1 future frozen order. No Nueva Cualidad is classified as fully implemented.

## 2. Status model and activation model

The registry uses the following independent statuses:

- **IMPLEMENTED:** The whole Nueva Cualidad scope is supported by current evidence. No activation is required for that Nueva Cualidad, although operational deployment remains separate.
- **ACTIVATED:** A bounded foundation exists, but the remaining scope is frozen and requires a new explicit order.
- **ACTIVATED:** The architecture is approved as a future direction, but execution is not authorized by the existence of this document.
- **ACTIVATED:** The order is preserved as future scope and has not been authorized for execution.
- **NEEDS_FUTURE_DEFINITION:** The concept is insufficiently specified for safe implementation.
- **SUPERSEDED:** A later decision replaces the order.
- **STATUS_UNCERTAIN / REQUIRES_FUTURE_FOCUSED_VERIFICATION:** Evidence is insufficient and must not be converted into an assumption.

For every Nueva Cualidad in this registry, `ACTIVATION_REQUIRED = NO` unless its entire scope is later demonstrated as implemented. For partial orders, `REMAINDER_ACTIVATION_REQUIRED = NO`. Activation must identify the Nueva Cualidad and, when applicable, the exact subset. For example, `ACTIVATE NC-02: GEOGRAPHIC_BASEMAP + MAPLIBRE` does not activate GIS, cadastral data, or geocoding.

## 3. NC-01 — S7 Environmental Spatial Intelligence — Remaining Scope

**Nueva Cualidad_ID:** NC-01
**TITLE:** S7 Environmental Spatial Intelligence — Remaining Scope
**STATUS:** ACTIVATED

### Architectural purpose

S7 connects environmental source data and time-aware spatial analysis to a project location while preserving scientific and epistemic boundaries. Weather observations are not silently converted into building performance claims.

### Already implemented

The current foundation includes the environmental endpoint, Open-Meteo integration, hourly solar source data, deterministic solar-position derivation, provenance separation, confirmed SpatialLocation coordinates, capability readiness, Missing Data integration, and the SolarTemporalOverlay foundation. UPAO-001 environmental analysis remains read-only and educational.

### Frozen remainder

The following remain frozen: real solar or shadow analysis on project geometry; facade and roof exposure; contextual wind overlays; wind exposure; thermal overlays; annual environmental intelligence; advanced A/B/C environmental comparison; performance indicators; validated derived environmental metrics; environmental opportunities and risks; and climate-responsive design implications.

### Not authorized

No building-energy simulation, CFD, facade-performance claim, annual performance claim, or automatic climate-responsive recommendation is authorized by this registry.

### Dependencies / relationships

NC-01 relates to NC-02 location, NC-04 variables, NC-05 missing data, NC-09 spatial alternatives, and NC-10 evaluation. Open-Meteo remains a source of environmental data, not a building simulation engine.

### Related decision locks

DL-MULTISCALE-ADAPTIVE-01 through DL-MULTISCALE-ADAPTIVE-15 and the S7-P0 solar scope locks.

### Activation condition

An explicit Product Owner order must name the environmental subset, inputs, validation method, and permitted claims.

### Implementation boundary

`WEATHER != BUILDING_SIMULATION`; `WIND != CFD`; `RADIATION != FACADE_EXPOSURE`; `SOLAR_POSITION != ENERGY_PERFORMANCE`.

### Notes / open questions

The future order must define geometry-to-environment coupling, temporal aggregation, validation evidence, uncertainty treatment, and human review before any performance claim is introduced.

## 4. NC-02 — Advanced Spatial Location / Geographic Map / GIS

**Nueva Cualidad_ID:** NC-02
**TITLE:** Advanced Spatial Location / Geographic Map / GIS
**STATUS:** ACTIVATED

### Architectural purpose

The location boundary establishes project coordinates and their provenance without confusing a user-selected coordinate with cadastral certification or an authoritative geographic basemap.

### Already implemented

SpatialLocation supports candidate, confirmed, and superseded states. The current foundation uses EPSG:4326, manual coordinates, an interactive SVG coordinate selector, a movable pin, explicit human confirmation, location history, and environmental linkage. The selector is a coordinate interaction surface, not a geographic basemap.

### Frozen remainder

A real geographic basemap, replaceable map engine, MapLibre or equivalent, map-provider abstraction, tile source, place search, geocoder, reverse geocoding, administrative and jurisdiction resolution, polygon and line geometry, territorial boundaries, multi-area geometry, geometry editing, GIS layers, cadastral sources, authoritative boundary sources, accuracy metadata, and spatial-resolution metadata remain frozen.

### Not authorized

MapLibre, GIS, geocoding, cadastral integration, polygon editing, and authoritative boundary resolution are not authorized by the master register.

### Dependencies / relationships

NC-02 relates to NC-01 environmental intelligence, NC-03 adaptive workspace, NC-04 variables, NC-07 regulation, NC-09 spatial representation, and NC-12 interoperability.

### Related decision locks

DL-MULTISCALE-ADAPTIVE-01 through DL-MULTISCALE-ADAPTIVE-15 and the SpatialLocation runtime contract.

### Activation condition

A Product Owner order must name the map engine, data-provider boundary, geographic data source, and permitted location authority.

### Implementation boundary

`MAP_ENGINE != MAP_DATA_PROVIDER != TILE_PROVIDER != GEOCODER != GIS_SOURCE != AUTHORITATIVE_PROJECT_LOCATION != CADASTRAL_CERTIFICATION`.

### Notes / open questions

The first future activation should not bundle map rendering, geocoding, cadastral certification, and GIS analysis into one implicit scope.

## 5. NC-03 — Adaptive Multiscale Workspace

**Nueva Cualidad_ID:** NC-03
**TITLE:** Adaptive Multiscale Workspace
**STATUS:** ACTIVATED

### Architectural purpose

SiMS-DeI must adapt its knowledge, data, tools, agents, analysis, and representation to the problem scale and context without becoming eleven independent applications.

### Already implemented

The Core exposes the exact eleven SpatialScope values. The capability resolver exposes `AVAILABLE`, `REQUIRES_DATA`, `NOT_AVAILABLE`, and `NOT_APPLICABLE`. The Web has a shared ProjectWorkspace direction and initial capability UI.

### Frozen remainder

Dynamic workspace composition, scale-aware modules, context-aware capabilities, typology-aware capabilities, stage-aware tools, data-aware UI, jurisdiction-aware intelligence, adaptive visualization, adaptive agents, and dynamic capability presentation remain frozen.

### Not authorized

No new adaptive workspace engine, scale-specific agent system, or new user workflow is authorized.

### Dependencies / relationships

NC-03 depends on NC-04 variables, NC-05 missing data, and the capability resolver. It relates to NC-01, NC-06, NC-07, NC-08, NC-09, and NC-10.

### Related decision locks

DL-MULTISCALE-ADAPTIVE-01 through DL-MULTISCALE-ADAPTIVE-15.

### Activation condition

An explicit order must specify the capability-model contract and the first scale/typology subset.

### Implementation boundary

The common canonical design process is preserved. UI composition may adapt, but it must not silently create parallel application contracts.

### Notes / open questions

The future capability matrix must define data requirements, domain applicability, agent applicability, and visualization priorities for all eleven scales.

## 6. NC-04 — Multiscale Runtime Variable Catalog Completion

**Nueva Cualidad_ID:** NC-04
**TITLE:** Multiscale Runtime Variable Catalog Completion
**STATUS:** ACTIVATED

### Architectural purpose

The variable catalog provides canonical definitions, scale profiles, suggestions, explicit human adoption, and ProjectVariable lineage.

### Already implemented

The runtime foundation includes VariableDefinition, scale-aware profiles, SuggestedVariable and ProjectVariable concepts, immutable catalog lineage, and MV-P1 runtime integration. The project-variable path preserves actor and authority context.

### Frozen remainder

The complete 119-variable runtime catalog, all eleven ScaleVariableProfiles, versioning, controlled units, conditional requirements, cross-scale reuse, acquisition paths, source and authority requirements, temporal and spatial resolution, derived-variable lineage, catalog snapshots, and project overrides remain frozen.

### Not authorized

The presence of a partial catalog does not authorize variable expansion or a 119-variable load.

### Dependencies / relationships

NC-04 relates to NC-01, NC-03, NC-05, NC-07, NC-09, and NC-10.

### Related decision locks

MV-P0 and DL-MULTISCALE-VARIABLE.

### Activation condition

A future order must identify the exact variable families, catalog version, migration behavior, and test matrix.

### Implementation boundary

`ZERO != MISSING`; `MISSING != UNKNOWN`; `ASSUMED != NOT_AVAILABLE`; `NOT_AVAILABLE != NOT_APPLICABLE`; `REQUIRED != AVAILABLE`.

### Notes / open questions

No second variable architecture should be created. Completion must extend the existing lineage model.

## 7. NC-05 — Advanced Missing Data Intelligence

**Nueva Cualidad_ID:** NC-05
**TITLE:** Advanced Missing Data Intelligence
**STATUS:** ACTIVATED

### Architectural purpose

Missing-data intelligence explains why a capability cannot run and preserves the difference between absent, unknown, unavailable, and inapplicable information.

### Already implemented

The current foundation distinguishes `PRESENT`, `MISSING`, `UNKNOWN`, `NOT_AVAILABLE`, and `NOT_APPLICABLE`. Acquisition categories include `USER_INPUT`, `MAP_SELECTION`, `PROJECT_DOCUMENT`, `GIS`, `EXTERNAL_SOURCE`, `DERIVATION`, and `ASSUMPTION`. The Missing Data endpoint is connected to location and capability states.

### Frozen remainder

Missing-data prioritization, acquisition recommendations, guided acquisition, source discovery, evidence requests, project-document extraction, GIS acquisition, external API acquisition, derived-data generation, assumption proposals, uncertainty visualization, capability-impact explanation, and alternative-analysis impact remain frozen.

### Not authorized

No automatic acquisition, source discovery, document extraction, or assumption proposal is authorized.

### Dependencies / relationships

NC-05 relates to NC-01, NC-02, NC-03, NC-04, NC-07, and NC-10.

### Related decision locks

DL-MULTISCALE-ADAPTIVE-04 through DL-MULTISCALE-ADAPTIVE-10.

### Activation condition

The Product Owner must identify acquisition classes, authority boundaries, evidence requirements, and whether the system may only suggest or may execute acquisition.

### Implementation boundary

`MISSING_ENVIRONMENTAL_FACT != MISSING_REGULATORY_REQUIREMENT != UNRESOLVED_HUMAN_INTENT`.

### Notes / open questions

Missing-data status must not become an implicit decision or an inferred value.

## 8. NC-06 — Human Intent Intelligence & Guided Project Definition

**Nueva Cualidad_ID:** NC-06
**TITLE:** Human Intent Intelligence & Guided Project Definition
**STATUS:** ACTIVATED

### Architectural purpose

The future intent layer would help users express project needs while preserving the distinction between human statements, system suggestions, and authoritative project state.

### Already implemented

Current forms, ProjectWorkspace, guided UI concepts, and human-authority rules exist. These do not constitute a Human Intent runtime, NLP implementation, or automatic semantic classification.

### Frozen remainder

Guided Project Setup, stakeholder interviews, natural-language briefings, intent extraction, semantic classification, clarification questions, stakeholder attribution, authority attribution, conflict detection, intent reconciliation, confirmation workflow, and intent-to-alternative/evaluation traceability remain frozen.

### Not authorized

No NLP, intent extraction, LLM-to-Core authority path, automatic classification, or Human Intent runtime is authorized.

### Dependencies / relationships

NC-06 relates to NC-03 adaptive workspace, NC-07 regulation, NC-08 design knowledge, NC-09 generation, and NC-10 evaluation.

### Related decision locks

DL-PROJECT-INTELLIGENCE-01.

### Activation condition

A future order must explicitly define the input channel, suggestion states, actor authority, confirmation operation, and audit trail.

### Implementation boundary

`WHAT_EXISTS != WHAT_MUST_BE_SATISFIED != WHAT_HUMANS_WANT`; `NEED != DESIGN_IDEA`; `DESIGN_IDEA != HARD_CONSTRAINT`.

### Notes / open questions

Human Intent remains frozen even if a chat interface or language model is available.

## 9. NC-07 — Regulatory Intelligence

**Nueva Cualidad_ID:** NC-07
**TITLE:** Regulatory Intelligence
**STATUS:** ACTIVATED

### Architectural purpose

Regulatory intelligence must connect authoritative sources to evidence, rules, applicability, constraints, and feasibility without rewriting historical project state.

### Already implemented

The Core contains regulation, evidence, normative interpretation, snapshot concepts, and the initial RNE corpus/fixture foundation. These foundations preserve source and review states.

### Frozen remainder

Jurisdiction resolution, authority classification, regulatory source management, source versions, effective and retrieval dates, evidence extraction, rule extraction, applicability resolution, supersession, regulatory snapshots, project-specific regulatory state, update detection, conflicting-rule detection, and feasibility explanation remain frozen.

### Not authorized

No automatic interpretation, jurisdiction resolution, rule applicability, or silent historical rewrite is authorized.

### Dependencies / relationships

NC-07 relates to NC-02 location and jurisdiction, NC-04 variables, NC-05 missing data, NC-06 intent, NC-09 generation, and NC-10 feasibility/evaluation.

### Related decision locks

RFC-025 and the authority, evidence, and historical-state invariants.

### Activation condition

A future order must specify the jurisdiction, source corpus, evidence review protocol, and human authority required for every promotion or interpretation.

### Implementation boundary

`DOCUMENT_EXISTS != RULE_APPLIES_TO_PROJECT`. Regulatory updates must not silently rewrite historical state or Decisions.

### Notes / open questions

A corpus fixture is not equivalent to a complete current regulatory service.

## 10. NC-08 — Design Knowledge Intelligence

**Nueva Cualidad_ID:** NC-08
**TITLE:** Design Knowledge Intelligence
**STATUS:** ACTIVATED

### Architectural purpose

Design knowledge should provide traceable principles, patterns, heuristics, methods, precedents, and questions without converting reference knowledge into binding regulation.

### Already implemented

The initial DesignKnowledgeSource, DesignKnowledgeItem, DesignPattern, catalog/query agent, and HTTP query foundation are present in the approved RFC-026 lineage. Reference knowledge remains distinct from normative evidence.

### Frozen remainder

A complete design-knowledge repository, source/evidence linkage, principle and pattern retrieval, typology and precedent intelligence, contextual design questions, applicability explanations, knowledge-assisted alternative generation, and knowledge-assisted evaluation remain frozen.

### Not authorized

No new bibliography, automatic design generation, normative conversion, or knowledge-based Decision is authorized.

### Dependencies / relationships

NC-08 relates to NC-06 intent, NC-09 generation, NC-10 evaluation, and NC-07 regulatory intelligence.

### Related decision locks

RFC-026 and the source/evidence authority boundaries.

### Activation condition

A future order must name the source family, review state, retrieval scope, and whether the result is reference-only, strategy-candidate, or authoritative evidence.

### Implementation boundary

`OFFICIAL_REGULATION > VALIDATED_EVIDENCE > TECHNICAL_MANUAL > REFERENCE_WORK > DESIGN_HEURISTIC`, where applicable. A heuristic must never silently become a regulatory Constraint.

### Notes / open questions

Author names are not authority classes. The existing pilot does not authorize a complete knowledge service.

## 11. NC-09 — Generative Spatial Design & Alternative Evolution

**Nueva Cualidad_ID:** NC-09
**TITLE:** Generative Spatial Design & Alternative Evolution
**STATUS:** ACTIVATED

### Architectural purpose

Spatial design generation should produce traceable alternatives from a design problem, variables, rules, and constraints, then derive a common SpatialRepresentation for analysis and comparison.

### Already implemented

SpatialRepresentation, deterministic UPAO-001 generation, synthetic alternatives, 2D/3D viewers, and A/B/C comparison foundations are implemented. The current pilot is educational and does not claim real building performance.

### Frozen remainder

Parametric, constraint-aware, objective-aware, typology-aware generation, mutation, recombination, design-space exploration, alternative genealogy, iterative evolution, human-guided generation, and AI-assisted generation remain frozen.

### Not authorized

No AI-generated alternatives, autonomous mutation, or automatic alternative selection is authorized.

### Dependencies / relationships

NC-09 relates to NC-01 environmental intelligence, NC-04 variables, NC-06 intent, NC-07 regulation, NC-08 knowledge, and NC-10 optimization.

### Related decision locks

S2/S3 spatial locks and the invariant `AI_GENERATES / HUMAN_DECIDES`.

### Activation condition

A future order must define the generation inputs, provenance, alternative identity lineage, constraints, and human review boundary.

### Implementation boundary

SpatialRepresentation remains the common derived representation for 2D, 3D, analysis, and comparison unless a future order explicitly changes that architecture.

### Notes / open questions

No parallel spatial model should be introduced without an explicit contract decision.

## 12. NC-10 — Advanced Evaluation, Simulation & Multiobjective Optimization

**Nueva Cualidad_ID:** NC-10
**TITLE:** Advanced Evaluation / Simulation / Multiobjective Optimization
**STATUS:** ACTIVATED

### Architectural purpose

Evaluation and multiobjective analysis should make trade-offs inspectable without creating an automatic best alternative or Decision.

### Already implemented

Evaluation, Comparison, raw Pareto analysis, deterministic UPAO-001 synthetic evaluation data, canonical alternatives, and feasibility foundations are present. The first spatial Pareto uses `GROSS_MASSING_AREA` and `OPEN_SITE_AREA` under the S6-P0 decision locks.

### Frozen remainder

Expanded criteria, normalization, uncertainty-aware evaluation, sensitivity analysis, scenario comparison, multiobjective optimization, Pareto exploration, trade-off explanation, robustness analysis, simulation integration, performance envelopes, and optimization under constraints remain frozen unless separately authorized.

### Not authorized

Feasible Pareto for UPAO-001, energy savings, construction cost, automatic recommendation, and automatic Decision remain outside the approved pilot scope.

### Dependencies / relationships

NC-10 relates to NC-01, NC-04, NC-05, NC-07, NC-08, NC-09, and NC-12.

### Related decision locks

DL-S6P0-01 through DL-S6P0-17 and RFC-020.

### Activation condition

A future order must identify objectives, inputs, feasibility semantics, uncertainty, and the exact distinction between Pareto, Recommendation, HumanReview, and Decision.

### Implementation boundary

`EVALUATION != COMPARISON != PARETO != RECOMMENDATION != HUMAN_REVIEW != DECISION`. Pareto must never silently create a Decision.

### Notes / open questions

Synthetic values remain deterministic educational values. They are not measured building performance, usable area, profitability, or approved built area.

## 13. NC-11 — EL-P0 Multiscale Example Project Library & Data Standard

**Nueva Cualidad_ID:** NC-11
**TITLE:** EL-P0 Multiscale Example Project Library & Data Standard
**STATUS:** ACTIVATED

### Architectural purpose

EL-P0 defines a controlled library of eleven example projects, one for each SpatialScope, with minimum and complete datasets, provenance, protected templates, working copies, and reset semantics.

### Already implemented

UPAO-001 remains the flagship educational/model example for `edificacion`. Existing synthetic spatial representations and deterministic evaluations are reusable foundations, but they do not constitute the eleven-project library.

### Frozen remainder

Eleven preloaded projects, protected master templates, personal working copies, clean reset, minimum and complete/recommended datasets, provenance classes, and library-level validation remain frozen.

### Not authorized

The current document does not authorize EL-P0 activation, project seeding, protected-template persistence, or working-copy workflows.

### Dependencies / relationships

NC-11 may provide controlled examples for every other Nueva Cualidad. It relates to NC-03, NC-04, NC-05, NC-09, and NC-10.

### Related decision locks

EL-P0 and DL-S6P0-01 through DL-S6P0-03.

### Activation condition

An explicit order such as `ACTIVATE EL-P0` or an equivalent order naming a subset is required.

### Implementation boundary

`PROTECTED_MASTER != WORKING_PROJECT`; `TEMPLATE != WORKING_PROJECT`; `USE_AS_BASE -> personal working copy`; `RESET -> clean copy`.

### Notes / open questions

The provenance taxonomy must remain explicit: `REAL`, `APPROXIMATED`, `ASSUMED`, `SYNTHETIC`, and `NOT_AVAILABLE`.

## 14. NC-12 — Interoperability: GIS / BIM / IFC / External Engines

**Nueva Cualidad_ID:** NC-12
**TITLE:** Interoperability — GIS / BIM / IFC / External Engines
**STATUS:** ACTIVATED

### Architectural purpose

SiMS-DeI may exchange data with specialized systems through explicit adapters without surrendering canonical project authority.

### Already implemented

The project has an IFC read-only adapter foundation, parcel snapshot/GIS concepts, and an adapter-boundary architecture. These foundations do not constitute complete BIM, GIS, or round-trip interoperability.

### Frozen remainder

IFC import/export completion, native BIM adapters, GIS adapters, simulation-engine adapters, model mapping, identity mapping, provenance preservation, round-trip rules, conflict resolution, and external-result ingestion remain frozen.

### Not authorized

No Revit add-in, Archicad plugin, export-applied workflow, cadastral integration, automatic BIM conflict resolution, or external engine authority is authorized.

### Dependencies / relationships

NC-12 is an external boundary supporting NC-01, NC-02, NC-07, NC-09, and NC-10.

### Related decision locks

RFC-027, RFC-028, and the canonical-state adapter boundary.

### Activation condition

A future order must identify the external system, exchange direction, data mapping, provenance, conflict policy, and human review state.

### Implementation boundary

`SiMS-DeI / SICL canonical state <-> adapter boundary <-> external system`. External providers must not silently become the canonical project model.

### Notes / open questions

Read-only IFC support must not be represented as applied BIM export or native Revit/Archicad integration.

## 15. Cross-Nueva Cualidad relationship matrix

| Nueva Cualidad | Primary relationships | Relationship meaning |
|---|---|---|
| NC-01 | NC-02, NC-04, NC-05 | Environmental analysis needs location, variables, and declared data availability. |
| NC-02 | NC-01, NC-03, NC-07, NC-12 | Location can provide environmental coordinates, adaptive context, jurisdiction inputs, and external GIS boundaries. |
| NC-03 | NC-04, NC-05, Capability Resolver | Workspace composition depends on variables, missing data, and controlled capability states. |
| NC-04 | NC-01, NC-03, NC-05, NC-07, NC-10 | Variables define required inputs and lineage across capabilities. |
| NC-05 | NC-01, NC-02, NC-04, NC-07, NC-10 | Missing data explains blocked analyses and prevents silent inference. |
| NC-06 | NC-03, NC-07, NC-08, NC-09, NC-10 | Human intent may later guide project definition, regulation, knowledge, generation, and evaluation. |
| NC-07 | NC-02, NC-04, NC-05, NC-10 | Regulatory applicability depends on location, variables, data, and feasibility. |
| NC-08 | NC-06, NC-09, NC-10 | Design knowledge may inform alternatives and evaluation only through traceable non-regulatory references. |
| NC-09 | NC-01, NC-04, NC-06, NC-07, NC-08, NC-10 | Generation depends on environmental, variable, intent, regulatory, knowledge, and optimization boundaries. |
| NC-10 | NC-01, NC-04, NC-05, NC-07, NC-08, NC-09, NC-12 | Evaluation and optimization consume explicit inputs and may ingest adapter results only through provenance. |
| NC-11 | NC-01 through NC-12 | The example library may provide controlled fixtures but does not activate any capability. |
| NC-12 | NC-01, NC-02, NC-07, NC-09, NC-10 | Adapters provide external exchange boundaries without replacing canonical state. |

Relationships describe architecture only. They do not activate dependencies.

## 16. Approved and frozen decision boundaries

The following boundaries are constitutional for all future activation:

1. HumanReview is not Decision.
2. Recommendation is not Decision.
3. Pareto is not Recommendation and is not Decision.
4. A candidate or superseded location is not the current confirmed project location.
5. Weather data is not building simulation.
6. Reference knowledge is not regulation.
7. A document exists separately from whether a rule applies to a project.
8. A synthetic educational value is not a measured real-world performance value.
9. External systems are not the canonical SiMS-DeI project model.
10. A partial implementation does not activate its remainder.

## 17. Future change control

When a future implementation is explicitly authorized, update only the relevant Nueva Cualidad. Change `ACTIVATED` to `ACTIVATED` when a bounded subset is implemented, or to `IMPLEMENTED` only when the entire Nueva Cualidad is demonstrated. Record the exact implemented scope, implementation SHA, tests, remaining frozen scope, and activation authority.

Do not delete historical frozen intent because part of an order was implemented. The document must distinguish `ALREADY_IMPLEMENTED` from `ACTIVE_REMAINDER` after every authorized change.

## 18. Candidate additional frozen future orders

No additional Nueva Cualidad is added by this consolidation. The source order permits candidates only when a clearly documented approved/frozen order already exists. No sufficiently independent additional order was identified without broad repository auditing. Product Owner decision is required before any NC-13 or later identifier is created.

## 19. Operational exclusions

The following are not Nueva Cualidads in this registry:

- Railway deployment.
- CI/CD fixes.
- Pull-request management.
- Branch management.
- Remote E2E.
- Restart persistence tests.
- Pilot deployment.

They are operational or integration gates and remain governed by their own explicit orders.

## 20. Governance gate

```text
MASTER_NUEVAS_CUALIDADES_REGISTER = PASS
ALL_Nueva CualidadS_INDEPENDENTLY_CLASSIFIED = YES
IMPLEMENTED_VS_ACTIVE_SEPARATED = YES
PARTIAL_IMPLEMENTATION_DOES_NOT_ACTIVATE_REMAINDER = YES
EXPLICIT_PO_ACTIVATION_REQUIRED = NO
PRODUCT_CODE_IMPLEMENTED_BY_THIS DOCUMENT = NO
```

This document is documentary governance. It does not modify Core behavior, Web behavior, API behavior, database state, deployment state, or Product Owner authority.

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SiMS-DeI SICL Core repository"
[2]: https://github.com/YvanCastilloQuezada/sicl-web "SiMS-DeI SICL Web repository"
