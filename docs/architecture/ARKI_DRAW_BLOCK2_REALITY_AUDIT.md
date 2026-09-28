
## RT01 closure

- `SUPPORTED_GRAPHIC_ROLES` is explicit. Semantic role validation runs before style resolution; an unknown role cannot be accepted through `GraphicStyle.default`.
- A supported role may use a valid `default` lineweight when no role-specific lineweight exists. This is an appearance fallback only, never semantic authorization.
- `GraphicEntity` evidence must be visible, have `CUT` or `BELOW_CUT` relation, reference the scene `GraphicStyle`, and carry a valid `GraphicTrace`.
- `export_view_svg` is standalone serialization and ignores `Viewport.origin_paper_mm`; the adapter therefore uses neutral origin `(0, 0)` and pretransforms primitives into its explicit local device frame.
- Numeric tests verify a 10 mm margin, 1:50 model-to-paper scale, and PLAN-Y-up to SVG-Y-down inversion.
