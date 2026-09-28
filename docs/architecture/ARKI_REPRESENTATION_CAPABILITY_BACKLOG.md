# ARKI Representation Capability Backlog

**Contract:** ARKI-ARE-001  
**Status:** `CONTRACT_COMPLETE_PENDING_RED_TEAM`  
**Baseline:** `201397e15922ecd8cdcd9b980e6feaa8e3ea856f`  
**Runtime implementation authorized:** `NO`

This registry records current reality, dependencies, blockers, unlock conditions, and target fronts. A status of `IMPLEMENTED` means an existing repository capability exists; it does not mean ARE runtime is implemented.

## Status vocabulary

```text
IMPLEMENTED
PARTIAL
DECLARED_NOT_IMPLEMENTED
DEFERRED
BLOCKED_BY_CONTRACT
BLOCKED_BY_MODEL
BLOCKED_BY_TOOLING
FUTURE
```

## Capability registry

| Capability | Status | Existing evidence / scope | Depends on | Blocked by | Unlock condition | Target front |
|---|---|---|---|---|---|---|
| ViewDefinition contract | `BLOCKED_BY_CONTRACT` | Defined conceptually in ARE-001 only | source scope, view taxonomy | no runtime contract | Red Team + separate ARE core authorization | ARE Core Types |
| RepresentationProfile contract | `BLOCKED_BY_CONTRACT` | Defined conceptually in ARE-001 only | view family, fidelity policy | no runtime contract | approve profile schema and validation rules | ARE Core Types |
| GraphicStyle contract | `PARTIAL` | RFC-030 drawing rules and ARKI-DRAW styles exist | technical drawing standard | no cross-family contract | define immutable style registry boundary | ARE Core Types / ARKI-DRAW |
| AnnotationProfile contract | `PARTIAL` | RFC-030 annotations and dimensions exist | view definition, geometry references | radial/angular semantics incomplete | approve annotation contract and references | ARE Core Types |
| SheetDefinition contract | `PARTIAL` | ARKI-DRAW Sheet/Viewport and layout engine exist | viewports, title block, layout | no ARE composition contract | bind existing lower layer without changing it | ARE Core Types / Sheet Composition |
| GraphicScene | `BLOCKED_BY_CONTRACT` | No runtime type exists | source refs, view, profile, primitives | intermediate semantics not implemented | authorize ARE core and scene invariants | Graphic Scene |
| Knowledge views | `PARTIAL` | spatial/functional DTOs and diagrams exist in adjacent capabilities | functional knowledge, relationships | no unified ViewDefinition | authorize knowledge extraction contract | Knowledge Views |
| Relationship diagram | `PARTIAL` | relationship data exists; no ARE scene backend | knowledge view, graph semantics | no unified scene | define graph scene mapping | Knowledge Views |
| Flow/circulation diagram | `DECLARED_NOT_IMPLEMENTED` | No canonical ARE implementation | functional topology, graph layout | no view/scene runtime | source topology contract + scene backend | Knowledge Views |
| Zoning schematic | `DECLARED_NOT_IMPLEMENTED` | No canonical ARE implementation | functional zones, adjacency | no view/scene runtime | zoning semantics and source evidence | Knowledge Views |
| Adjacency view | `DECLARED_NOT_IMPLEMENTED` | No unified representation | relationship knowledge | no view/scene runtime | adjacency extraction contract | Knowledge Views |
| Functional topology view | `DECLARED_NOT_IMPLEMENTED` | Direction supported conceptually by RFC-026 | topology knowledge | no view/scene runtime | approve functional topology model | Knowledge Views |
| Architectural plan | `PARTIAL` | RFC-030 projector/composer generates technical plan evidence | geometry, view, profile, ARKI-DRAW | not a generalized ARE pipeline | ARE integration authorization and tests | Projection Engine / ARKI-DRAW |
| Section | `PARTIAL` | RFC-030 section projection exists | geometry, cut plane, annotations | no generalized ARE pipeline | cut-plane contract + projection authorization | Projection Engine |
| Elevation | `PARTIAL` | RFC-030 elevation projection exists | geometry, orientation, annotations | no generalized ARE pipeline | elevation contract + projection authorization | Projection Engine |
| Axonometric | `DECLARED_NOT_IMPLEMENTED` | Taxonomy only | 3D geometry, camera | no 3D projection contract | approve camera/3D source contract | 3D Representation |
| Analytical 3D | `DECLARED_NOT_IMPLEMENTED` | Spatial geometry can carry neutral volumes | analysis semantics, 3D source | no analytical scene contract | define analytical evidence contract | Analytical Representation |
| Advanced hatch clipping | `DECLARED_NOT_IMPLEMENTED` | Basic hatch/vector primitives exist | cut geometry, clipping rules | geometric clipping not implemented | geometry clipping contract + tests | ARKI-DRAW / Projection |
| Radial dimensions | `DECLARED_NOT_IMPLEMENTED` | API intentionally fail-closes | arc/circle references, annotation profile | insufficient approved reference semantics | approve circle/arc dimension semantics and implement separately | Annotation / ARKI-DRAW Block 2 |
| Angular dimensions | `DECLARED_NOT_IMPLEMENTED` | API intentionally fail-closes | arc/line references, annotation profile | insufficient approved reference semantics | approve angular reference semantics and implement separately | Annotation / ARKI-DRAW Block 2 |
| Plan generation | `PARTIAL` | RFC-030 technical plan path exists | IFC/D2 snapshot, projector, rules | not ARE-generalized | ARE pipeline contract + integration gate | Projection Engine |
| Section generation | `PARTIAL` | RFC-030 technical section path exists | cut plane, geometry, rules | not ARE-generalized | ARE pipeline contract + integration gate | Projection Engine |
| Elevation generation | `PARTIAL` | RFC-030 technical elevation path exists | orientation, geometry, rules | not ARE-generalized | ARE pipeline contract + integration gate | Projection Engine |
| Professional drawings | `PARTIAL` | RFC-030 PDFs and title blocks exist | plans/sections/elevations, sheet validation | quality remains fixture/profile-specific | acceptance profile and human review | Professional Documentation |
| Vector 2D / SVG | `IMPLEMENTED` | ARKI-DRAW deterministic SVG exporter | primitives, sheet, metadata | limited to existing Block 1.1 contract | maintain regression and future ARE adapter | ARKI-DRAW |
| Vector PDF | `DECLARED_NOT_IMPLEMENTED` | RFC-030 PDF path exists for technical drawings, no ARE-general backend | GraphicScene, sheet, PDF backend | ARE contract and backend scope | explicit backend authorization and tests | Output Backend |
| DXF | `DECLARED_NOT_IMPLEMENTED` | No canonical DXF runtime | GraphicScene, DXF mapping | tooling/backend contract | approve DXF backend and dependency policy | Output Backend |
| DWG | `FUTURE` | No canonical support | DXF/3D semantics, tooling | licensing/tooling | separate technology decision | Output Backend |
| 3D representation | `DECLARED_NOT_IMPLEMENTED` | neutral spatial geometry exists; no ARE 3D scene | 3D view, camera, scene | 3D contract absent | authorize 3D representation front | 3D Representation |
| Conceptual render | `DECLARED_NOT_IMPLEMENTED` | no ARE render engine | scene, materials/context | renderer not authorized | render contract and backend decision | Visualization |
| Photorealistic render | `FUTURE` | RFC-035 is a separate future namespace | 3D scene, materials, renderer | no ARE/render authorization | separate RFC/runtime gate | Visualization / RFC-035 |
| Hybrid sheets | `PARTIAL` | sheets can compose vector/text and documentation; raster integration not ARE-defined | SheetDefinition, vector/raster assets | no hybrid scene/profile contract | define asset provenance and composition contract | Sheet Composition |
| Graphic traceability | `PARTIAL` | source metadata exists in RFC-030 and ARKI-DRAW | source refs, scene primitives | no unified GraphicScene | approve traceability schema | ARE Core / Graphic Scene |
| Graphic selection | `DECLARED_NOT_IMPLEMENTED` | no canonical inverse lookup contract | traceability index | no UI/inspection contract | define read-only selection protocol | Interaction |
| Architectural mutation from selection | `BLOCKED_BY_CONTRACT` | D2 transaction exists separately | authorized D2 mutation | forbidden direct SVG mutation | explicit D2 transaction handoff only | D2 Boundary |
| Fidelity/compute policy | `PARTIAL` | law and cheapest-sufficient direction documented | stage, evidence, cost | no runtime funnel | separate funnel authorization | Policy |
| Render validation | `BLOCKED_BY_CONTRACT` | render is explicitly not validation | validation domain, evidence | human/validation separation | define independent validation workflow | Governance |

## Dependency graph

```text
D2 ArchiModel / Functional Knowledge
        │
        ├── source snapshots + fingerprints
        │             │
        │             ├── Knowledge Views
        │             │       └── GraphicScene ──┐
        │             │                           │
        │             └── Geometric Views        │
        │                     └── GraphicScene ──┤
        │                                         ▼
        │                               RepresentationProfile
        │                                         │
        │                                   GraphicStyle
        │                                         │
        │                                AnnotationProfile
        │                                         │
        │                                  SheetDefinition
        │                                         │
        │                    ┌────────────────────┼──────────────────┐
        │                    ▼                    ▼                  ▼
        │               ARKI-DRAW             3D backend       Visualization backend
        │                    │                    │                  │
        │                   SVG             future 3D          future raster/hybrid
        │
        └── D2 mutation/approval remains outside ARE and requires existing gates
```

## Explicit dependency rules

1. A view definition depends on a declared source scope; it never invents a source.
2. A geometric projection depends on sufficient geometry, coordinate system, and orientation/cut data.
3. A knowledge view does not depend on a ConstructionModel 3D object.
4. A GraphicScene depends on a view and profile and must retain source references.
5. GraphicStyle and AnnotationProfile may alter representation only, never source semantics.
6. A SheetDefinition depends on one or more views/scenes, not on a new architectural model.
7. A backend consumes a scene and reports unsupported operations; it must not silently substitute another backend.
8. H-001 causal derivation is not a dependency of every graphic primitive.
9. D2 mutation is not a consequence of graphic selection; explicit authority and D2 transaction are required.

## Current implementation sequence

```text
1. ARE-001 contract + Red Team closure
2. ARE core types (read-only, immutable, validated)
3. GraphicScene and traceability index
4. Knowledge views
5. Geometric Projection Engine
6. ARKI-DRAW Block 2 contract and separate gate
7. Plan / Section / Elevation integration
8. Professional documentation profiles
9. 3D representation
10. Visualization and render backends
11. DXF/DWG only after explicit tooling decisions
```

## Protection statement

This registry is documentary. It does not authorize any item above `IMPLEMENTED` or `PARTIAL` to be expanded in this branch. ARE runtime, Projection Engine, Block 2, render, DXF, and frontend remain unauthorized.
