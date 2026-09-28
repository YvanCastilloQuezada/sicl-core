# ARKI-M1 — Reality Audit

**Baseline:** `51da21be1c36a83dc6e850c13b816c3f8c82823d`
**Branch:** `feat/arki-m1-vector-plan-pipeline`
**Current checkpoint:** Block 2 adapter plus adversarial hardening.

## REUSE

- ARE-002 `GraphicScene`, `GraphicEntity`, `GraphicTrace`, and `GraphicStyle`.
- ARE-003 `project_architectural_plan` as the only architectural projection source.
- ARKI-DRAW `Point`, `Rect`, `Circle`, `LineWeight`, `Viewport`, and `export_view_svg`.
- Existing SVG metadata for primitive identity, source reference, semantic role, and layer.

## ADAPT

- `scene_adapter.py` is the visible boundary from renderer-neutral GraphicScene intent to ARKI-DRAW vector state.
- Rectangle and circle geometry intents are adapted without changing dimensions.
- `GraphicStyle.line_weights` is the appearance authority; no element-kind appearance is hardcoded.
- PLAN_XY_MM uses an explicit translation to a deterministic bounding-box viewport with a fixed 10 mm margin at the selected scale.
- PLAN_Y_UP is explicitly serialized through the existing SVG Y-down convention.

## MISSING / DEFERRED

- Dimensions and dimension policy.
- Professional room labels.
- Material hatches.
- Door swing inference.
- Sheet composition, API, frontend, sections, elevations, axonometric views, and renders.

## DO_NOT_REUSE

- No D2 inspection inside the drawing backend.
- No IFC, SpatialRepresentation, synthetic room generator, or RFC-030 architectural fabrication.
- No inference of material, room use, adjacency, circulation, opening direction, dimensions, furniture, or professional symbols.

## INTERNAL RED-TEAM FINDINGS

| Finding | Classification | Resolution |
|---|---|---|
| Unsupported roles could fall through to style lookup | MATERIAL_FINDING | Explicit supported-role taxonomy; unknown roles block. |
| `UNKNOWN_VISIBILITY` / unresolved cut relation could be drawn | MATERIAL_FINDING | Require `VISIBLE` plus `CUT` or `BELOW_CUT`; otherwise block. |
| Malformed or missing GraphicTrace could reach the backend | MATERIAL_FINDING | Validate trace type before adaptation. |
| Non-finite, malformed, zero, or negative geometry | MATERIAL_FINDING | Numeric finite/positive validation with explicit adapter errors. |
| Style reference could disagree with scene style | MATERIAL_FINDING | Require entity style reference to equal scene GraphicStyle ID. |

All findings were corrected and retested. No material findings remain open within M1 scope.

## INVARIANTS

```text
GRAPHIC TRACEABILITY != H001 CAUSAL DERIVATION
REPRESENTATION != ARCHITECTURAL TRUTH
VIEW DEFINITION != VIEWPORT
GRAPHIC ENTITY != PRIMITIVE
DOOR EVIDENCE != DOOR SWING
MATERIAL EVIDENCE != HATCH
SPACE BOUNDARY != ROOM LABEL
GEOMETRY != DIMENSION POLICY
PLANO != IMAGEN
```
