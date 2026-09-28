# ARKI-ARE-001 — Representation Architecture Contract

**Status:** `CONTRACT_COMPLETE_PENDING_RED_TEAM`  
**Authority:** Product Owner / Human Authority  
**Direction:** Model Once → Reason Once → Represent Many  
**Baseline:** `201397e15922ecd8cdcd9b980e6feaa8e3ea856f` (`main`)  
**Branch:** `feat/arki-are-001-contract`  
**Scope:** Documentation and contract definition only

> This document defines the contract between canonical architectural knowledge and future representations. It does **not** implement ARE runtime, a Projection Engine, ARKI-DRAW Block 2, exporters, renderers, APIs, schemas, or dependencies.

## 1. Purpose

ARE is the architectural boundary that derives multiple representations from one canonical source without creating a second architectural truth. It separates semantic knowledge, views, projections, graphic semantics, sheets, and output backends.

```text
ARCHITECTURAL KNOWLEDGE / ARCHIMODEL
              ↓
       VIEW DEFINITION
              ↓
   REPRESENTATION PROFILE
              ↓
       GRAPHIC SCENE
              ↓
       OUTPUT BACKEND
```

The permanent architectural invariants are:

```text
MODEL ≠ VIEW ≠ DRAWING ≠ RENDER
REPRESENTATION ≠ ARCHITECTURAL TRUTH
GRAPHIC TRACEABILITY ≠ CAUSAL DERIVATION
GRAPHIC SELECTION ≠ ARCHITECTURAL MUTATION
```

ARKI is not a wrapper around an external engine. Future capability follows **learn → replicate → improve**: observe useful external conventions, reproduce the validated semantics internally, then improve the autonomous ARKI contract. External tools may be explicit adapters or evidence sources; they are never the canonical authority or an implicit production dependency.

## 2. Non-goals and activation locks

This contract does not authorize:

- ARE runtime modules, endpoints, CLI commands, or persistence;
- a Projection Engine or View Engine;
- ARKI-DRAW Block 2;
- radial or angular dimension implementation;
- DXF/DWG/PDF runtime exporters or a render engine;
- new schemas, dependencies, frontend work, or external provider calls;
- changes to D1, D2, A-002, H-001–H-005, IFC, Bridge, or ARKI-DRAW Block 1.1;
- automatic H-001 derivations for graphic primitives;
- visual output being treated as approval, validation, or architectural truth.

`ARKI-ARE-000` remains historical architecture context. Its known-gap notes were recorded before Block 1.1; this contract does not rewrite that historical document. Current capability status is recorded in the companion backlog.

## 3. Current reality audit

The audit was performed against `main=201397e15922ecd8cdcd9b980e6feaa8e3ea856f`.

| Existing capability | Current evidence | Contract interpretation |
|---|---|---|
| D2 semantic model | `src/sicl/archi/model.py`: `ArchiElement`, `ArchiGeometry`, `ElementKind`, immutable semantic properties, content hash | Canonical semantic/geometry source when applicable; unchanged by ARE-001 |
| D2 transaction and provenance | `src/sicl/archi/transaction.py`, H-002..H-005 integration, IFC staging/publication | Source-side mutation/provenance boundary; ARE consumes results and never approves mutations |
| Spatial representation | `src/sicl/spatial.py`: validated `SpatialRepresentation` and `SpatialElement`, renderer-neutral geometry, stable IDs/fingerprints | Existing derived spatial DTO; a possible source for future geometric views, not a second truth |
| Spatial transport | `/v1/projects/{project_id}/spatial-representations`, explicitly read-only | Existing read-only transport; not an ARE endpoint |
| ARKI-DRAW primitives | `src/sicl/drawing/primitives.py`: vector primitives including line, polyline, arc, circle, text, dimension, hatch | Lower-level vector capability; no view extraction responsibility |
| ARKI-DRAW sheets/SVG | `drawing/sheet.py`, `drawing_entities.py`, `svg_export.py`, `title_block.py` | Existing serialization/composition backend; preserved as Block 1.1 |
| Drawing projection | `drawing/projector.py` and RFC-030 composer | Existing RFC-030 technical projection path; not generalized into ARE by this order |
| Layout | `src/sicl/layout/layout_engine.py`, zones, margins, collision/truncation validation | Existing sheet-layout calculation/validation; does not render or mutate BIM |
| IFC | D2 IFC export and RFC-030 synthetic/import snapshot path | Exchange/source boundary; IFC is not made the canonical truth by ARE |
| ARE types | No runtime `ViewDefinition`, `RepresentationProfile`, `GraphicScene`, or ARE package exists | Deliberately contract-only in this branch |
| Rendering | No canonical ARE render engine | Declared future/deferred; no silent fallback |

### Audit conclusion

The repository has lower-level building blocks but no canonical intermediate representation contract. ARE-001 supplies that missing contract without duplicating or replacing any existing capability.

## 4. Architecture

```text
                 CANONICAL KNOWLEDGE
        D2 ArchiModel / functional knowledge
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
  KNOWLEDGE VIEW   GEOMETRIC VIEW   ANALYTICAL VIEW
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                  VIEW DEFINITION
                         ▼
              REPRESENTATION PROFILE
                         ▼
                   GRAPHIC SCENE
                         ▼
              ARKI-DRAW / 3D / RENDER
```

ARE is a transformation boundary, not an alternate model. A transformation must be deterministic for the same source snapshot, view definition, profile, style, annotation profile, and backend version. Any uncertainty or missing source evidence remains explicit.

## 5. View taxonomy

### 5.1 Knowledge / functional views

These can exist before formal geometry:

- `RELATIONSHIP_DIAGRAM`
- `FLOW_CIRCULATION_DIAGRAM`
- `ZONING_SCHEMATIC`
- `ADJACENCY_VIEW`
- `FUNCTIONAL_TOPOLOGY_VIEW`
- `DEPENDENCY_VIEW`

Source: functional knowledge, relationships, constraints, or topology. They must not pretend to be geometric plans.

### 5.2 Geometric projection views

These require sufficient geometry and coordinate context:

- `ARCHITECTURAL_PLAN`
- `SECTION`
- `ELEVATION`
- `AXONOMETRIC`
- `ANALYTICAL_3D`

Source: D2 geometry, an eligible `SpatialRepresentation`, or an explicitly declared exchange snapshot. Insufficient geometry yields `UNKNOWN`/`BLOCKED`, never a visually similar fallback.

### 5.3 Visualization views

These communicate appearance or experience:

- `CONCEPTUAL_RENDER`
- `MATERIAL_RENDER`
- `INTERIOR_RENDER`
- `EXTERIOR_RENDER`
- `AERIAL_RENDER`
- `NIGHT_RENDER`
- `PHOTOREALISTIC_RENDER`

A visualization is not validation. Photorealism is not architectural correctness.

## 6. Contract types

The following are normative conceptual interfaces. They are not Python runtime types in this order.

### 6.1 `ViewDefinition`

Expresses **what is observed**:

```text
view_id               stable identifier
view_family           KNOWLEDGE | GEOMETRIC | VISUALIZATION
source_scope          project / alternative / element scope
projection            NONE | ORTHOGRAPHIC | PERSPECTIVE | GRAPH
orientation           north/direction/camera orientation when applicable
cut_plane             section plane or null
visibility            visible semantic categories and defaults
filters               explicit inclusion/exclusion filters
semantic_scope        entities/relations/objectives being observed
scale_intent          conceptual / drawing scale intent / null
representation_purpose decision purpose
```

A knowledge view may have no geometry, cut plane, or scale. Fields are conditional by family; ARE must not force geometric fields on functional views.

### 6.2 `RepresentationProfile`

Expresses **how much information and fidelity, for what purpose**:

```text
profile_id
view_family
lod_intent
semantic_detail
geometric_fidelity
annotation_intent
validation_evidence_required
output_intent
cost_class
```

Initial plan profiles are `CONCEPTUAL`, `UNDIMENSIONED`, `DIMENSIONED`, `PROFESSIONAL`, `PRESENTATION`, `REGULATORY`, and `ANALYTICAL`. A profile cannot create source data that is absent.

### 6.3 `GraphicStyle`

Governs graphics only:

```text
lineweights, linetypes, fills, hatches, colors,
fonts, symbols, graphic hierarchy, tolerances
```

It cannot change geometry, semantics, applicability, validity, or architectural decisions. RFC-030 drawing rules remain its current technical source for technical drawings.

### 6.4 `AnnotationProfile`

Governs dimensions, labels, room names, areas, levels, axes, references, markers, notes, and legends. `RADIAL` and `ANGULAR` belong here but remain `DECLARED_NOT_IMPLEMENTED` until their geometric reference contract is approved.

### 6.5 `SheetDefinition`

A sheet is not a view. It composes one or more views and documentary elements:

```text
sheet_id, paper, orientation, margins,
viewports, title_block, legends, notes, revision_data
```

Existing ARKI-DRAW `Sheet`, `Viewport`, `DrawingSheet`, and layout zones are lower-level realizations that must remain compatible with this distinction.

### 6.6 `GraphicScene`

**Decision: adopt `GraphicScene` as the ARE intermediate contract.**

It prevents a rigid direct conversion from `Wall` to `SVG Line` and allows the same semantic source to feed vector, 3D, analytical, and visualization backends.

Conceptual fields:

```text
scene_id
source_snapshot_ref
view_id
profile_id
primitives[]
scene_warnings[]
backend_constraints
traceability_index
```

A scene primitive carries graphic intent, not architectural authority:

```text
primitive_id
source_entity_refs[]
view_id
layer
semantic_role
representation_role
geometry_intent
style_ref
annotation_ref
```

GraphicScene is derived and disposable. It is not persisted as a second canonical model unless a future order defines a controlled cache with provenance and invalidation.

## 7. Traceability and inverse direction

Every representable primitive should be traceable, when source evidence exists, to one or more semantic entity references. The minimum answer must be:

> What architectural or functional entity produced this representation?

This is **graphic traceability**, not H-001 causal derivation. A line, hatch, label, or render pixel must not automatically create a derivation record.

Inverse selection is permitted as a read-only lookup:

```text
GRAPHIC PRIMITIVE → SOURCE ENTITY REFERENCE
```

It supports inspection, highlighting, and future UI selection. It must never silently mutate D2. Any mutation follows the existing authorized D2 transaction and A-002/H-001..H-005 gates.

## 8. Contractual pipelines

### 8.1 General pipeline

```text
SOURCE KNOWLEDGE
      ↓
VIEW EXTRACTION
      ↓
REPRESENTATION TRANSFORMATION
      ↓
GRAPHIC SEMANTICS / GRAPHIC SCENE
      ↓
OUTPUT BACKEND
```

### 8.2 Vector pipeline

```text
D2 / FUNCTIONAL KNOWLEDGE
      ↓
VIEW DEFINITION
      ↓
PROJECTION OR KNOWLEDGE EXTRACTION
      ↓
GRAPHIC SCENE
      ↓
ARKI-DRAW
      ↓
SVG / FUTURE VECTOR PDF / FUTURE DXF
```

### 8.3 Visualization pipeline

```text
SOURCE KNOWLEDGE + GEOMETRY + MATERIAL/CONTEXT EVIDENCE
      ↓
VIEW DEFINITION + REPRESENTATION PROFILE
      ↓
3D/VISUALIZATION SCENE
      ↓
RASTER OR HYBRID BACKEND
```

No backend may silently substitute another view family. Backend unavailability is a declared capability failure.

## 9. Failure semantics

| Condition | Required result |
|---|---|
| Unsupported view | `FAIL_CLOSED` |
| Insufficient source data | `UNKNOWN` or `BLOCKED` |
| Unavailable backend | `BLOCKED_BY_TOOLING` |
| Unsupported representation | `NOT_IMPLEMENTED` |
| Missing geometric reference for radial/angular annotation | `BLOCKED_BY_MODEL` |
| Ambiguous source scope | `BLOCKED` with diagnostic |

Forbidden behavior:

```text
SILENT FALLBACK TO SOMETHING THAT LOOKS SIMILAR
```

A rendered, drawn, or serialized artifact is never implicitly `VALIDATED`, `APPROVED`, or `SELECTED`.

## 10. Fidelity and compute policy

`SURVIVAL_STAGE` is not a mandatory view type. It informs recommended fidelity and compute budget:

```text
IDEA        → low-cost diagram or knowledge view
ALTERNATIVE → low-fidelity vector/diagram
GEOMETRY    → precise vector projection
SIMULATION  → analytical representation
SOLUTION    → developed drawings + 3D
PROPOSAL    → professional documentation + high-fidelity visualization
```

> ARKI uses the least costly representation that provides the evidence necessary for the current decision.

This preserves **La Vida de las Ideas es Cruel** without implementing a runtime funnel in ARE-001.

## 11. Human Authority boundaries

```text
RENDERED ≠ VALIDATED
DRAWN ≠ APPROVED
REPRESENTED ≠ SELECTED
SELECTED ≠ HUMAN APPROVED
```

ARE may prepare evidence and alternatives. Only the authorized human/authority workflow can approve, reject, or authorize consequential architectural decisions.

## 12. D2 boundary

D2 remains the semantic/geometric source when applicable. ARE may read D2 snapshots and declared derived representations. ARE must not modify `src/sicl/archi/`, D2 identities, mutations, transactions, provenance, or IFC semantics.

A future ARE implementation must declare:

- source snapshot/version and content fingerprint;
- required semantic and geometric evidence;
- whether a view is functional, geometric, analytical, or visual;
- read-only traceability back to source entities;
- failure status when data is insufficient.

## 13. ARKI-DRAW boundary

```text
ARKI-DRAW ⊂ ARKI REPRESENTATION ARCHITECTURE
```

ARKI-DRAW Block 1.1 remains the lower-level vector drawing and serialization capability: primitives, SVG, sheets, dimensions, metadata, and layout-related output. It is not ARE, does not define architectural truth, and does not decide compliance or human approval.

ARE must consume ARKI-DRAW through an explicit backend boundary. It must not reimplement or silently replace Block 1.1. Block 2 remains unauthorized by this contract.

## 14. Autonomous ARKI direction

ARE follows the project-wide autonomous direction:

1. **Learn:** inspect validated conventions and external-tool outputs as evidence, without adopting their runtime authority.
2. **Replicate:** encode the useful semantics in ARKI-owned contracts and deterministic transformations.
3. **Improve:** optimize the internal pipeline while preserving source truth, traceability, failure semantics, and human authority.

This is not a wrapper architecture. Adapters may exist later, but the canonical model, reasoning, profiles, scenes, and decisions remain ARKI-owned.

## 15. Acceptance criteria for this contract

A Red Team reviewer must be able to verify:

- two documents exist at the authorized paths;
- no runtime ARE module, endpoint, dependency, exporter, or frontend was added;
- D1, D2, A-002, H-001–H-005, IFC, and ARKI-DRAW B1.1 are byte-for-byte unchanged by this branch;
- the reality audit distinguishes implemented, partial, and future capabilities;
- functional views are separated from geometric projections and visualizations;
- `ViewDefinition`, `RepresentationProfile`, `GraphicStyle`, `AnnotationProfile`, `SheetDefinition`, and `GraphicScene` have explicit responsibilities;
- traceability is separated from causal derivation and inverse selection from mutation;
- unsupported and insufficient cases fail closed;
- the backlog and dependency graph are complete for the required capabilities;
- implementation remains unauthorized until a separate order.

## 16. Proposed implementation sequence after future authorization

The sequence is intentionally future-facing:

```text
ARE CONTRACT + RED TEAM CLOSURE
        ↓
ARE CORE TYPES (read-only, validated)
        ↓
GRAPHIC SCENE CONTRACT / DETERMINISTIC TRANSFORM
        ↓
KNOWLEDGE VIEWS
        ↓
GEOMETRIC PROJECTION ENGINE
        ↓
ARKI-DRAW BLOCK 2 CONTRACT (separate gate)
        ↓
PLAN / SECTION / ELEVATION
        ↓
PROFESSIONAL DOCUMENTATION
        ↓
3D REPRESENTATION
        ↓
VISUALIZATION / RENDER
```

This ordering puts the intermediate contract before projection and preserves the lower-level ARKI-DRAW boundary. It does not authorize any step beyond this document.

## 17. State

```text
ARKI_ARE_001                 = CONTRACT_COMPLETE_PENDING_RED_TEAM
ARE_RUNTIME_IMPLEMENTATION   = NOT_AUTHORIZED
ARKI_DRAW_BLOCK2             = NOT_AUTHORIZED
D2_DIFF                      = EMPTY
CORE_DIFF                    = EMPTY
ARKI_DRAW_RUNTIME_DIFF       = EMPTY
HUMAN_AUTHORITY              = PRESERVED
```
