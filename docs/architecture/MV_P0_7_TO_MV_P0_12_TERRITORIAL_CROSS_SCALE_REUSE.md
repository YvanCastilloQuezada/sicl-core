# MV-P0.7–MV-P0.12 — Territorial Cross-Scale Reuse Table

**Status:** SPECIFICATION ONLY

This lightweight table covers all eleven SpatialScopes. It is not the final MV-P0.13 deduplication and does not rename, merge, or create runtime aliases.

| Variable/concept | First scale | Other possible scales | Same semantic identity | Reason |
|---|---|---|---|---|
| POPULATION | zona_barrio_sector | distrito_ciudad, provincia_metropoli, region, macro_region, pais | UNRESOLVED | population subject, aggregation, time, and dataset resolution differ |
| AREA | zona_barrio_sector | all territorial scales | UNRESOLVED | bounded area is reusable only with explicit subject and CRS |
| DENSITY | zona_barrio_sector | distrito_ciudad, region, macro_region | NO | denominator, population subject, and aggregation change |
| HOUSING_DEFICIT | zona_barrio_sector | distrito_ciudad, region, pais | UNRESOLVED | definition may be quantitative or qualitative and must be declared |
| EMPLOYMENT | zona_barrio_sector | all territorial scales | UNRESOLVED | employment population and reference period differ |
| HEALTH_CAPACITY | distrito_ciudad | region, macro_region, pais | NO | facility capacity differs from network accessibility and coverage |
| ACCESSIBILITY | zona_barrio_sector | distrito_ciudad, region, pais | NO | accessibility target and network resolution differ |
| WATER | parcela_sitio | region, macro_region, pais | NO | site service, watershed availability, transfer, and national resource differ |
| ENERGY | sistema | region, macro_region, pais | NO | building/system demand is not territorial generation or matrix |
| SOLAR | parcela_sitio | region, macro_region, pais | UNRESOLVED | environmental input may be shared; derived design response is not |
| RISK | parcela_sitio | all territorial scales | UNRESOLVED | hazard type, exposure, vulnerability, and resolution differ |
| COST | sistema | edificacion, parcela_sitio, territorial scales | NO | CAPEX/OPEX/site/portfolio/public investment are distinct |
| PUBLIC_INVESTMENT | distrito_ciudad | region, macro_region, pais | NO | portfolio and policy investment are not project cost |
| TRANSPORT_CORRIDOR | distrito_ciudad | provincia_metropoli, region, macro_region, pais | UNRESOLVED | network hierarchy and flow scale differ |
| ECOSYSTEMS | parcela_sitio | region, macro_region, pais | UNRESOLVED | ecosystem subject and spatial resolution differ |
| CLIMATE | parcela_sitio | all territorial scales | NO | climate input is not building or project performance |
| AGRICULTURE | region | macro_region, pais | NO | productive sector subject and aggregation differ |
| MIGRATION | distrito_ciudad | region, macro_region, pais | UNRESOLVED | flow, origin-destination, and temporal semantics differ |
| PROVENANCE | objeto | all scales | YES | metadata concept is reusable with scale-specific content |
| SCENARIO | sistema | all scales | YES | scenario identity is reusable while variables and scope differ |

## Summary

`CROSS_SCALE_REUSE_CANDIDATES = 20`
`SEMANTIC_COLLISIONS = 0` in primary profiles
`UNRESOLVED_IDENTITY_CASES = 10`
`FINAL_MV_P0.13_DEDUPLICATION = NOT PERFORMED`

Same word does not imply the same semantic identity. Review requires subject, unit, temporal semantics, spatial resolution, derivation, provenance, and decision use.

## Common separation

```text
CURRENT STATE / CONTEXT
    != DESIGN / SCENARIO VARIABLE
    != CONSTRAINT
    != OBJECTIVE
    != DERIVED METRIC
    != EVALUATION
```

Environmental data remain separate from derived environmental performance. Regulation, Design Knowledge, Source, Evidence, HumanReview, and Decision remain separate concepts.
