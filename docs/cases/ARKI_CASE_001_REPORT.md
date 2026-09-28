# ARKI-CASE-001 — Controlled House E2E Validation

**Status:** `READY_FOR_HUMAN_VISUAL_REVIEW`

## RECIBIDO

```text
ORDER = ARKI-CASE-001
BASELINE = 71e72bb1abfb217bf4854f464ae443764281f469
TAG = arki-m1-block2-final-2026-09-28
BRANCH = feat/arki-case-001-controlled-house
HEAD_BEFORE = 71e72bb1abfb217bf4854f464281f469
WORKTREE_BEFORE = CLEAN
```

## MODEL

The fixture is a validation geometry, not an architectural recommendation or a normative design.

```text
SITE = 1
SPACES = 6
WALLS = 12
DOORS = 5
WINDOWS = 4
OPENINGS = 0
TOTAL_ELEMENTS = 28
```

All elements use `ArchiElement` with stable IDs, version `>= 1`, deterministic content hashes, and valid containment/hosting where applicable. The site is intentionally excluded from the ARE-003 plan input because the current projection path does not project `SITE` as a plan graphic entity.

## PIPELINE

```text
D2 = PASS — 28 valid ArchiElements created
ARE003 = PASS — 27 D2 elements supplied; 27 GraphicEntities emitted
GRAPHICSCENE = PASS — deterministic GraphicScene
ARKI_DRAW = PASS — GraphicScene adapted to 27 vector primitives
SVG = PASS — real output of graphic_scene_to_svg()
```

No canonical engine was modified.

## OUTPUT

```text
BASE_SVG = artifacts/arki-case-001/ARKI_CASE_001_BASE.svg
BASE_SHA256 = 700f69b3e3969c1328d05552d41ebc0ad3256cc1da8a41cc41256a570d75de50

MUTATED_SVG = artifacts/arki-case-001/ARKI_CASE_001_MUTATED.svg
MUTATED_SHA256 = 4a68e0fd548300af90de187214077627aaea895042acbd7ea9e79e558da6fd5a

SVG_DETERMINISM = PASS
VECTOR_ONLY = PASS
SVG_PARSEABLE = PASS
RASTER_IMAGES = 0
TRACE_METADATA_PRESENT = PASS
```

Two independent base executions produced identical SHA-256 output. The base and mutated outputs differ as required.

## GEOMETRIC ACCEPTANCE

```text
MODEL_ENVELOPE_WIDTH = 10,000 mm
SCALE = 1:50
REPRESENTED_GEOMETRY_WIDTH = 200 mm
MARGIN = 10 mm
Y_AXIS = PLAN_Y_UP → SVG_Y_DOWN
```

The SVG was parsed numerically. The represented geometry spans 200 mm at 1:50, with the declared 10 mm margins. No screenshot-based acceptance was used.

## MUTATION

```text
TARGET = WALL W07
DELTA = +600 mm X
PROPAGATION = PASS
BASE_SVG != MUTATED_SVG = PASS
UNAFFECTED_STABILITY = PASS for two sampled distant graphic entities and their stable IDs
```

The mutation was applied to the D2 fixture before re-running ARE-003 and Block 2. The SVG was never edited directly. The target retains its trace to `W07`; its geometry changes in the mutated output. Unaffected source-derived graphic entity and primitive IDs remain stable under the current identity contract.

## TRACEABILITY

Traceability is graphic traceability, not H-001 causal derivation.

```text
WALL_TRACE = PASS
SPACE_TRACE = PASS
DOOR_OR_WINDOW_TRACE = PASS
```

Each represented entity includes the following chain in `ARKI_CASE_001_TRACEABILITY.json`:

```text
D2 ELEMENT ID
→ D2 VERSION
→ GRAPHIC ENTITY ID
→ GRAPHIC TRACE
→ PRIMITIVE ID
→ SVG data-source-ref
→ SVG data-semantic-role
```

Observed semantic roles include `WALL_CUT`, `SPACE_BOUNDARY`, `DOOR_EVIDENCE`, and `WINDOW_EVIDENCE`.

## ADVERSARIAL

```text
ROLE_CONTRADICTION = PASS — GRAPHIC_TRACE_ROLE_MISMATCH; no primitive/SVG created
OPERATION_CONTRADICTION = PASS — GRAPHIC_TRACE_OPERATION_MISMATCH; no primitive/SVG created
```

## FABRICATION

The audit scans both real SVG outputs for prohibited markers rather than relying on a declaration.

```text
FABRICATION_PATH = NONE
FABRICATED_ITEMS = 0
FORBIDDEN_MARKERS_FOUND = []
```

The output contains no room labels, area labels, dimensions, door swings, material hatches, furniture, sanitary fixtures, north arrow, axes, section markers, or elevation markers. This is recorded as absence, not as proof that those capabilities are unnecessary.

PNG inspection package:

```text
PNG = NOT_GENERATED
REASON = NO EXISTING LOCAL SVG→PNG TOOL; NEW DEPENDENCY PROHIBITED
SVG = PRIMARY EVIDENCE
```

## ARCHITECTURAL REPRESENTATION DEFICITS

| ID | Description | Observed in case | Why it matters | Current state | Dependency | Proposed future block | Material current case? | Material professional drawing? |
|---|---|---|---|---|---|---|---|---|
| DEF-CASE001-01 | Room labels and area labels are absent | Yes | A professional plan must identify spaces and areas | Not implemented in current Block 2 contract | Annotation/profile and sheet composition | Future annotation block | No — prohibited by case | Yes |
| DEF-CASE001-02 | Dimensions are absent | Yes | Dimensional verification and construction communication require them | Not implemented | Dimension policy and vector dimension primitives | Future annotation/dimension block | No — prohibited by case | Yes |
| DEF-CASE001-03 | Door swings and window/door symbols are absent | Yes | Openings cannot be documented professionally from rectangles alone | Not implemented | Opening-symbol semantics and drawing rules | Future architectural-symbol block | No — prohibited by case | Yes |
| DEF-CASE001-04 | Material hatches are absent | Yes | Material communication and graphic hierarchy are incomplete | Not implemented | Hatch/material mapping | Future drawing-standard block | No — prohibited by case | Yes |
| DEF-CASE001-05 | Sheet composition, title block, axes, north, sections and elevations are absent | Yes | A single standalone viewport is not a complete drawing sheet set | Not implemented in this case pipeline | Sheet composition and view-family orchestration | Future sheet/view block | No — prohibited by case | Yes |
| DEF-CASE001-06 | Site element is not projected into the plan scene | Yes | Site context is not represented by the current ARE-003 supported roles | `NOT_APPLICABLE` for current projection, not a silent loss | Explicit site projection semantics | Future site/context projection block | No — recorded limitation | Possibly |

These are **DEFERRED_ENHANCEMENT** observations, not material findings, because the current engine does not claim to implement them. No unsupported feature was fabricated.

## CLASSIFICATION

```text
MATERIAL_FINDINGS = 0
IMPROVEMENTS = 0
DEFERRED_ENHANCEMENTS = 6
CANONICAL_BEHAVIOR_CONTRADICTIONS = 0
TRACEABILITY_BREAK = 0
NONDETERMINISTIC_OUTPUT = 0
```

## TESTS

```text
CASE001_TESTS = 5 PASS
BLOCK2_TESTS = 12 PASS
ARKI_DRAW_TESTS = 68 PASS
ARE003_TESTS = 10 PASS
ARE002_TESTS = 24 PASS
D2_TESTS = 42 PASS
CORE_TESTS = 135 PASS
GLOBAL_TESTS = PASS
COMPILEALL = PASS
git diff --check = PASS
```

The global suite completed with exit code `0`. Existing non-blocking `ifcopenshell` cleanup warnings were observed; no test failure resulted.

## PROTECTED CONTRACTS

```text
D2_DIFF = EMPTY
A002_DIFF = EMPTY
H001_H005_DIFF = EMPTY
ARE001_DIFF = EMPTY
ARE002_DIFF = EMPTY
ARE003_DIFF = EMPTY
ARKI_DRAW_BLOCK1_DIFF = EMPTY
ARKI_DRAW_BLOCK2_DIFF = EMPTY
RFC030_DIFF = EMPTY
```

## ENTREGADO

```text
artifacts/arki-case-001/ARKI_CASE_001_BASE.svg
artifacts/arki-case-001/ARKI_CASE_001_MUTATED.svg
artifacts/arki-case-001/ARKI_CASE_001_EVIDENCE.json
artifacts/arki-case-001/ARKI_CASE_001_TRACEABILITY.json
docs/cases/ARKI_CASE_001_REPORT.md
scripts/arki_case_001.py
tests/test_case_001.py
```

## DIVERGENCIA

```text
DIVERGENCIA = NO
```

## FALTA

```text
FALTA = NADA
```

## FINAL VERDICT

```text
ARKI_CASE_001 = READY_FOR_HUMAN_VISUAL_REVIEW
NO MERGE
NO TAG
```

The evidence is ready for external architectural inspection. No canonical engine change was made and no merge or tag is authorized by this case order.
