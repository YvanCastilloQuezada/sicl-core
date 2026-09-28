# ARKI-ARE-003 — Reality Audit and Projection Boundary

**Baseline:** `9b1da6763a9ad7039bf91b9d3424c531a3e72b75` (`arki-are-002-final-2026-09-28`)
**Branch:** `feat/arki-are-003-2d-projection`
**Scope:** deterministic orthographic `ARCHITECTURAL_PLAN` projection only.

## REUSE

| Capability | Evidence | Decision |
|---|---|---|
| Canonical D2 identity | `src/sicl/archi/identity.py`, `ArchiElementId` | Use as source entity identity; no duplicate IDs. |
| D2 element model | `src/sicl/archi/model.py`, `ArchiElement` | Consume immutable elements and their semantic/content hashes. |
| D2 geometry | `ArchiGeometry`, `ProfileSpec` | Support only `EXTRUDED_RECTANGLE` and `EXTRUDED_CIRCLE`. |
| D2 relationships | `hosted_in` / `contained_in`, versioned fields | Preserve hosting evidence; do not infer door swing. |
| ARE-002 source authority | `SourceSnapshot`, `canonical_d2_fingerprint` | Verify the supplied snapshot against the exact in-memory D2 state. |
| ARE-002 view/profile contracts | `ViewDefinition`, `RepresentationProfile` | Require geometric architectural plan and orthographic projection. |
| ARE-002 output contracts | `GraphicEntity`, `GraphicTrace`, `GraphicScene` | Produce renderer-neutral traceable entities only. |

## ADAPT

- Model-space D2 millimetres are mapped directly to plan view-space millimetres (`XY`); no centering, scaling, or decorative offset is applied.
- `cut_plane` is explicit as `z_mm=<finite number>` for the initial implementation.
- Entity identity is derived from source element, view, operation, semantic role, and projection version.
- Cut relation and view visibility are separate. Exact model-unit boundaries use `bottom <= cut <= top` for `CUT`; `BELOW_CUT` is visible with an explicit below-cut operation; `ABOVE_CUT` is `UNKNOWN_VISIBILITY` and is not emitted without a visibility policy/evidence.
- Plan direction is explicit: `view_direction="TOP"` is required by the initial engine.
- `DOOR_EVIDENCE` retains only geometric evidence and hosting trace; no swing arc or handing is fabricated.

## DO_NOT_REUSE

| Capability | Reason |
|---|---|
| `src/sicl/drawing/` | Backend/output responsibility; ARE-003 does not call ARKI-DRAW. |
| SVG/PDF/DXF/sheets/viewports | Serialization and composition are out of scope. |
| RFC-030 fallback generators | They may fabricate walls, rooms, openings, labels, or dimensions. |
| A-002 | Not a generic graphics-quality gate; runtime integration is deferred. |
| H-001 derivation APIs | Graphic traceability is not causal derivation; no ledger records are created. |
| SpatialRepresentation | It is a separate derived spatial DTO and is not duplicated or treated as D2. |

## SUPPORTED GEOMETRY

- `EXTRUDED_RECTANGLE`: emitted as neutral 2D rectangle geometry.
- `EXTRUDED_CIRCLE`: supported by the engine when a radius is present.
- Other geometry: fail closed with `UNSUPPORTED_GEOMETRY`.

## DEFERRED_WITH_REASON

- `SECTION`, `ELEVATION`, `AXONOMETRIC`: no runtime projection in ARE-003 initial scope.
- Materials and hatches: evidence and backend concerns are separate from projection.
- Dimensions, labels, professional symbols, door swing, and window conventions: no semantic evidence/policy in this engine.
- Columns, beams, slabs: semantic roles are reserved, but only emitted when their supported D2 geometry and view visibility are determinable.
- A-002 runtime integration: no operation-specific contract is required by this projection boundary yet.
- API/frontend/render integration: later application/backend fronts.
- `semantic_scope` is enforced as a project scope restriction; `filters`, `visibility`, and `level_scope` execution remain `DEFERRED_WITH_REASON` until ARE defines their operational semantics.

## ISOLATION INVARIANTS

ARE-003:

- does not mutate D2;
- does not write H-001 records;
- does not import or call ARKI-DRAW;
- does not generate SVG, PDF, DXF, sheets, or viewports;
- does not invent room names, areas, materials, dimensions, openings, or door arcs;
- produces only `GraphicScene`.
