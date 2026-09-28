# ARKI-DRAW Block 1.1 — Reality Audit

**Branch:** `feat/arkidraw-block1`  
**Audit baseline:** `4d932c2c2f884aa47982d6eca6358455beb1a314`  
**Scope:** Block 1 vector foundation only. D2, ARE, A-002, H-001–H-005 and Block 2 are excluded.

## Reality map

| Area | Evidence in code | Audit result |
|---|---|---|
| Public API | `sicl.drawing` exports primitives, scales, paper, sheets and SVG exporters | Implemented |
| Vector primitives | `Point`, `Line`, `Polyline`, `Rect`, `Text`, `Hatch`, `Dimension`; now `Arc` and `Circle` | Implemented and tested |
| SVG pipeline | `export_view_svg()` and `export_sheet_svg()` | Runtime verified |
| Viewport | `Viewport` with scale and paper origin | Implemented; collision checked at sheet export |
| Sheet/title block | `Sheet`, `PaperSpec`, `TitleBlock` | Implemented; collision fail-closed |
| Dimensions | Linear chain/overall/between-axes geometry with separate extensions, dimension segments, arrows/ticks and text | Runtime verified; radial/angular explicitly fail-closed |
| Hatch | SVG pattern definitions and polygon-bounded patterned fills | Runtime verified |
| Layers | Deterministic SVG `<g>` groups and `data-layer` attributes | Runtime verified |
| Semantic metadata | `primitive_id`, `semantic_role`, `source_ref` as `data-*` attributes | Runtime verified |
| Determinism | Repeated complete-sheet exports compared byte-for-byte and SHA-256 | Runtime verified |
| Unsupported primitives | Renderer raises `TypeError` instead of silently dropping input | Fail-closed verified |

## Findings and disposition

| ID | Finding | Classification | Disposition |
|---|---|---|---|
| B1-01 | Dimension kind was metadata-only and extension lines overlapped the measured geometry | `MATERIAL_FINDING` | Linear kinds now project measured points to a distinct dimension line; chain/overall/between-axes have distinct geometry. Radial/angular raise `DIMENSION_KIND_NOT_IMPLEMENTED` because the current model lacks radius/angle data |
| B1-02 | Hatch representation required runtime confirmation | `MATERIAL_FINDING` | Existing vector patterns retained; complete runtime hatch output verified |
| B1-03 | No `Arc` primitive or SVG serialization | `MATERIAL_FINDING` | Added validated `Arc` primitive and SVG path serialization |
| B1-04 | No `Circle` primitive or SVG serialization | `MATERIAL_FINDING` | Added validated `Circle` primitive and SVG circle serialization |
| B1-05 | Primitive identity/semantic/source metadata was not preserved in SVG | `MATERIAL_FINDING` | Added immutable metadata fields and deterministic `data-*` output |
| B1-06 | Layer values were not represented as logical SVG groups | `MATERIAL_FINDING` | Added deterministic layer groups and element layer attributes |
| B1-07 | Viewport/title-block overlap was not detected | `MATERIAL_FINDING` | Added fail-closed collision validation during sheet export |
| B1-08 | Invalid finite/degenerate geometry could enter the model | `MATERIAL_FINDING` | Added finite and positive-dimension validation for affected primitives |

## Improvements

- None required for Block 1.1 beyond the material corrections above.

## Deferred enhancements

- Full CAD constraint solving.
- Hatch clipping algorithms beyond SVG polygon fill semantics.
- Advanced dimension routing and collision avoidance.
- DXF/native BIM interoperability.
- ARE, automatic projection and render engines.

These are explicitly outside Block 1.1 and do not block this delivery.

## Runtime evidence

The complete vector runtime case constructs a sheet containing wall geometry, a concrete hatch, an arc, a circle, a dimension and semantic metadata. The generated SVG is parsed with Python's standard-library XML parser and exported twice for byte/SHA-256 determinism.

Unsupported element instances raise `TypeError`; they do not disappear silently.

## Protection boundaries

This audit and correction do not modify `src/sicl/archi/`, D2, D1, A-002, H-001–H-005, ARE or Block 2.
