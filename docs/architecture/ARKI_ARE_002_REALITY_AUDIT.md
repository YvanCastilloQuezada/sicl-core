# ARKI-ARE-002 — Reality Audit

**Baseline:** `e932ad1cc573d92614ee004cf2ec2d83b9ee37d1` (`main` after ARE-001 canonization)
**Scope:** executable representation foundation only; no projection, drawing, rendering, persistence, or external providers.

## REUSE

| Capability | Evidence | Decision |
|---|---|---|
| Canonical architectural identity | `src/sicl/archi/identity.py`, `ArchiElementId` | Reuse as source references; ARE does not recreate D2 identity. |
| Canonical architectural elements | `src/sicl/archi/model.py`, `ArchiElement`, `ArchiGeometry` | Treat as canonical source evidence; no mutation or duplication. |
| Derived spatial source | `src/sicl/spatial.py`, `SpatialRepresentation`, `SpatialElement` | Accept as a derived source only with explicit `SourceLineage`; derived identity is never conflated with canonical identity. |
| Stable canonical serialization | `src/sicl/spatial.py`, `canonical_json()` | Reuse the repository convention; ARE adds its own canonical serialization for its contracts. |
| Vector payload primitives | `src/sicl/drawing/primitives.py` | Reuse only as an optional payload type in future adapters; ARE-002 stays renderer-neutral. |
| A-002 sufficiency | `src/sicl/a002/` | Preserve boundary; ARE-002 does not turn A-002 into a generic graphic gate. |

## ADAPT

| Capability | Adaptation |
|---|---|
| Existing source fingerprints | Normalize them into immutable `SourceSnapshot` metadata without copying source models. |
| Existing frozen dataclasses | Add recursive freezing for mappings/sequences because ARE contracts must be immutable in practice. |
| Existing drawing concepts | Keep `GraphicStyle` and `AnnotationProfile` semantic contracts separate from ARKI-DRAW implementation. |

## DO_NOT_REUSE

| Capability | Reason |
|---|---|
| RFC-030 synthetic fallback behavior | It may invent architectural elements when evidence is absent; forbidden in ARE. |
| `DrawingView`, `Viewport`, `Sheet`, SVG exporter | These are output/backend concepts; ARE-002 produces no drawing or serialization backend output. |
| D2 mutation/transaction APIs | ARE is read-only and must not create H-001 derivations. |
| External renderers/providers | ARE is autonomous and renderer-neutral; no wrapper or provider dependency. |

## MISSING / CREATED BY ARE-002

- Immutable `SourceSnapshot` with source authority and provenance.
- Explicit freshness evaluation: `CURRENT`, `STALE`, `UNKNOWN`.
- Fail-closed source conflict detection.
- Immutable `ViewDefinition`, `RepresentationProfile`, `GraphicStyle`, and `AnnotationProfile`.
- Renderer-neutral immutable `GraphicScene`, entities, diagnostics, and traceability.
- Deterministic scene fingerprint independent of serialized backend fingerprint.
- Explicit lineage comparison against the canonical source; stale lineage blocks and unknown lineage remains explicit.
- Declared freshness is evidence metadata only; `build_scene()` verifies derived freshness against an explicit canonical context.
- A derived source cannot certify its own currentness. `STALE` is distinct from `SOURCE_CONFLICT`; conflict applies to incompatible derived results sharing the same lineage.
- Canonical view-family taxonomy and validation before scene construction.
- Required-evidence gating: unknown freshness may create only a diagnostic scene when the profile does not require validation evidence.

## Explicit non-goals

ARE-002 does not project geometry, create plans/sections/elevations, generate SVG or sheets, render, persist, call A-002 automatically, or modify D2/A-002/H-001–H-005/ARKI-DRAW.
