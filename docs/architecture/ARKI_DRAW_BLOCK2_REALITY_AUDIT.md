# ARKI-DRAW Block 2 — Reality Audit

**Baseline:** `51da21be1c36a83dc6e850c13b816c3f8c82823d`
**Branch:** `feat/arkidraw-block2-scene-adapter`
**Scope:** GraphicScene adapter, vector primitives, deterministic viewport, SVG E2E.

## REUSE

| Existing capability | Decision |
|---|---|
| `Point`, `Rect`, `Circle` | Reused as vector primitives. |
| `LineWeight` | Reused as the drawing appearance authority. |
| `Viewport` | Reused as the composition container, distinct from ARE `ViewDefinition`. |
| `export_view_svg` | Reused as the existing deterministic SVG serializer. |
| SVG metadata attributes | Reused for `data-primitive-id`, `data-source-ref`, and `data-semantic-role`. |
| ARE `GraphicScene`, `GraphicEntity`, `GraphicTrace` | Consumed as the sole graphic authority. |

## ADAPT

- `scene_adapter.py` is an explicit boundary: `GraphicScene → ARKI-DRAW primitives → Viewport → export_view_svg`.
- `rectangle` intent maps to `Rect`; `circle` intent maps to `Circle`.
- `GraphicStyle.line_weights[role]` maps to `LineWeight`; missing or invalid style evidence fails closed.
- Primitive IDs derive from GraphicEntity ID, semantic role, ordinal, and adapter version.
- Primitive metadata preserves the GraphicEntity ID and semantic role; `AdaptedGraphicScene.primitive_sources` closes the runtime trace back to `GraphicEntity`, whose `GraphicTrace` closes it to D2.
- Coordinates remain in `PLAN_XY_MM` until an explicit adapter translation establishes a fixed viewport margin. The serializer then applies the declared `1:scale` and SVG Y-axis inversion.

## DO_NOT_REUSE

- No D2 inspection, IFC import, SpatialRepresentation input, or architectural reasoning occurs in Block 2.
- No RFC-030 synthetic walls, rooms, labels, doors, windows, dimensions, materials, or hatches are used.
- No ARE-003 projection logic is duplicated in the drawing backend.
- No door swing, material hatch, room label, dimension, or professional symbol is fabricated.

## MISSING / DEFERRED

- Automatic dimensions remain outside Block 2.
- Room labels, material hatches, door swing and sheet composition remain outside the initial block.
- SVG metadata preserves the GraphicEntity reference; the full `GraphicTrace` remains available through `AdaptedGraphicScene.graphic_entities` rather than being re-encoded as architectural reasoning in the serializer.

## POLICIES

```text
GRAPHICSCENE_INPUT = required
UNKNOWN_ROLE_OR_GEOMETRY = BLOCK
EMPTY_SCENE = explicit error
NEW_DEPENDENCIES = NONE
VECTOR_ONLY = yes
RASTER_FALLBACK = no
AUTO_FIT = no
VIEWPORT_BOUNDS = deterministic scene bounds + fixed margin
Y_AXIS = PLAN_Y_UP -> SVG_Y_DOWN
```
