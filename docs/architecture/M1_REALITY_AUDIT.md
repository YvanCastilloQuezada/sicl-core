
## RT-M1 trace integrity closure

Block 2 validates the consistency observable without inspecting D2: `GraphicTrace.semantic_role` must equal `GraphicEntity.role`; `geometry_intent.cut_relation` must agree with the final operation token (`CUT_PROJECTION` or `BELOW_CUT_PROJECTION`); and `_CUT`/`_PROJECTED` roles must agree with that relation. A malformed trace, unresolved visibility, unresolved cut relation, style-reference mismatch, or invalid geometry fails closed.

`GraphicTrace.source_version` and `source_fingerprint` are preserved byte-for-byte. ARE-003 supplies element-level version/fingerprint values, while `GraphicScene.source_snapshot` supplies the model-level snapshot. There is no local contract that equates those two domains without inspecting D2 or introducing new authority. Therefore source version/fingerprint equivalence is **DEFERRED_WITH_REASON**, not guessed; an altered but structurally valid trace is preserved and serialized rather than falsely declared stale or current.

For standalone SVG, the adapter owns the pretransformed local coordinate frame and uses neutral viewport origin `(0, 0)`. Sheet placement remains the authority of `export_sheet_svg`; standalone `export_view_svg` does not consume sheet origin.
