# MV-P0 Batch A2 — Cumulative Cross-Scale Reuse Table

**Status:** SPECIFICATION ONLY
**Scales:** `objeto`, `espacio`, `sistema`, `edificacion`, `parcela_sitio`
**Purpose:** lightweight reuse review; not MV-P0.13 deduplication

| Variable/concept | First scale | Other possible scales | Same semantic identity | Reason |
|---|---|---|---|---|
| identity | objeto | espacio, sistema, edificacion, parcela_sitio | YES | Stable subject identity can be reused with scope-specific subject |
| length | objeto | espacio, edificacion, parcela_sitio | UNRESOLVED | Dimension meaning may remain, but reference frame and aggregation differ |
| width | objeto | espacio, edificacion, parcela_sitio | UNRESOLVED | Same dimensional family; scope semantics require later review |
| height | objeto | espacio, edificacion, sistema | UNRESOLVED | Vertical extent may describe different bounded subjects |
| orientation | objeto | espacio, edificacion, parcela_sitio | NO | Reference frame and design use differ materially |
| position | objeto | espacio, edificacion, parcela_sitio | NO | Object placement differs from space/building/site location |
| material | objeto | espacio, edificacion, sistema | UNRESOLVED | Object material, finish, assembly, and building material roles differ |
| geometry | objeto | espacio, sistema, edificacion, parcela_sitio | NO | Geometry representation has different subject and spatial support |
| area | objeto | espacio, edificacion, parcela_sitio | NO | Surface, floor, gross, and parcel area are materially distinct |
| volume | objeto | espacio, edificacion | UNRESOLVED | Volume subject and derived method differ by scale |
| occupancy | espacio | edificacion | NO | Space occupancy is not building occupancy aggregation |
| capacity | espacio | sistema, edificacion | NO | Persons accommodated differs from service throughput and building capacity |
| adjacency | objeto | espacio, sistema, edificacion, parcela_sitio | UNRESOLVED | Relation type and graph level differ |
| access | espacio | edificacion, parcela_sitio, sistema | UNRESOLVED | Access subject and network context differ |
| circulation | espacio | edificacion, parcela_sitio | NO | Internal movement differs from site/building networks |
| egress | espacio | edificacion | UNRESOLVED | Same safety intent but different aggregation and regulatory context |
| opening | objeto | espacio, edificacion | NO | Component property differs from space/building effect |
| maintenance | objeto | sistema, edificacion, parcela_sitio | UNRESOLVED | Action semantics may be shared, but owner and asset subject differ |
| cost | objeto | sistema, edificacion, parcela_sitio | NO | Cost aggregation and economic meaning differ |
| power | objeto | sistema, edificacion, parcela_sitio | NO | Component power differs from system demand and site service |
| temperature | espacio | edificacion, parcela_sitio | UNRESOLVED | Observation may be reusable; derived performance is not |
| solar radiation | espacio | edificacion, parcela_sitio | YES | Environmental input may be shared when resolution and time are explicit |
| solar exposure | objeto | espacio, edificacion, parcela_sitio | NO | Derived exposure has different geometry and aggregation |
| water demand | sistema | edificacion, parcela_sitio | NO | Service demand is not space sanitary demand or site resource condition |
| risk | sistema | edificacion, parcela_sitio | NO | Risk domain and hazard scale require distinct semantic identities |

## Summary

- `CROSS_SCALE_REUSE_CANDIDATES = 25`
- `SEMANTIC_COLLISIONS = 0` in the proposed primary profiles.
- `UNRESOLVED_IDENTITY_CASES = 10`.
- `FULL_MV_P0_13_DEDUPLICATION = NOT PERFORMED`.

The table is advisory. It does not rename IDs, merge records, create aliases, or alter runtime contracts. Candidate reuse requires later review of meaning, dimension, measurement method, spatial support, temporal semantics, derivation, and decision use.

## Separation Rule

Across all five scales, preserve:

```text
INPUT / STATE
    != DESIGN-CONTROLLABLE VARIABLE
    != CONSTRAINT
    != OBJECTIVE
    != DERIVED METRIC
    != EVALUATION
```

Environmental observations remain distinct from environmental performance. Design Knowledge remains distinct from project values. Regulation remains distinct from project values. Human Authority remains preserved.

## Gate

`CUMULATIVE_SCALES_DEFINED = objeto, espacio, sistema, edificacion, parcela_sitio`
`STATE_DESIGN_DERIVED_SEPARATION = PASS`
`ENVIRONMENTAL_SEPARATION = PASS`
`HUMAN_AUTHORITY = PASS`
`PRODUCT_IMPLEMENTATION = NO`
