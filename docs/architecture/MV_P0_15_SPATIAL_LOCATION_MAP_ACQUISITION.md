# MV-P0.15 — Spatial Location & Map Acquisition Architecture

**Status:** DOCUMENTARY ARCHITECTURE ONLY
**Map implementation:** NOT AUTHORIZED

## 1. SpatialLocation purpose

`SpatialLocation` is the project spatial reference/context used to locate, query, contextualize, and resolve spatially dependent variables and sources. It is not merely latitude/longitude and is not equivalent to cadastral certification.

## 2. Primary user experience

```text
SEARCH PLACE → MAP → USER SELECTS / MOVES LOCATION → CONFIRM → SpatialLocation
```

Manual coordinate entry is an advanced/fallback input. Normal users should not be required to type coordinates.

## 3. Documentary candidate fields

| Field | Meaning |
|---|---|
| `location_id` | Stable candidate identity |
| `geometry_type` | POINT, LINE, POLYGON, MULTI-AREA, or territorial boundary |
| `geometry` | Geometry in declared CRS |
| `centroid` | Derived display/query aid, not complete geometry |
| `latitude`, `longitude` | Optional point coordinates, never complete model |
| `CRS` | Coordinate reference system |
| `spatial_scope` | One of 11 canonical design scales |
| `place_label` | Human-readable selected label |
| `administrative_context` | Context, not automatic authority |
| `jurisdiction_context` | Possible regulatory/source filter |
| `source` | Origin/source relationship |
| `provenance` | Location-specific provenance linked to MV provenance |
| `accuracy` | Declared accuracy/uncertainty |
| `spatial_resolution` | Dataset/support resolution |
| `retrieval_time` | Acquisition time |
| `validation_status` | Candidate validation state |

No schema, migration, or runtime entity is created in this batch.

## 4. Geometry support by scale

| SpatialScope | Preferred acquisition geometry |
|---|---|
| `objeto` | POINT optional / containing context |
| `espacio` | POINT / containing building reference |
| `sistema` | POINT, LINE, NETWORK, or AREA depending on system |
| `edificacion` | POINT plus optional footprint/site polygon |
| `parcela_sitio` | POLYGON preferred |
| `zona_barrio_sector` | POLYGON / territorial geometry |
| `distrito_ciudad` | Administrative or functional boundary |
| `provincia_metropoli` | Territorial boundary / multi-area |
| `region` | Territorial boundary |
| `macro_region` | Multi-region geometry |
| `pais` | National boundary |

These are acquisition capabilities, not rigid ontology rules.

## 5. Mandatory separations

| Concept | Must remain separate from |
|---|---|
| Map engine | map data provider, tile provider, geocoder |
| Map data provider | GIS source, authoritative location |
| Geocoder | cadastral certification, regulatory authority |
| GIS dataset | project-adopted Evidence |
| Authoritative project location | user-selected or approximated location |
| Cadastral certification | generic map geometry |

The architecture is provider-neutral.

## 6. Technology direction

`MapLibre GL JS` is a **PROPOSED / REQUIRES TECHNICAL VALIDATION** initial web-map direction with interchangeable map/tile provider, geocoder, and GIS sources. OpenStreetMap-derived data may be considered where licensing and service conditions permit. Google Maps remains an optional future provider.

No MapLibre, Google Maps, geocoder, tile download, GIS integration, or external API call is implemented.

## 7. Location-driven source resolution

```text
SpatialLocation
  → coverage / jurisdiction / spatial resolution
  → Candidate Sources
  → SourceRequirement compatibility
  → Source / Evidence
```

Location may help identify climate, jurisdiction, regulatory context, risk, terrain, territorial statistics, and infrastructure sources. It does not determine truth automatically.

## 8. Location provenance

| Candidate provenance | Relationship to MV provenance |
|---|---|
| `USER_SELECTED` | generally `REAL` only after validation; otherwise explicit status |
| `SURVEYED` | evidence-backed `REAL` |
| `CADASTRAL` | authoritative only within certified scope |
| `GIS_DERIVED` | derived/approximated according to method |
| `DOCUMENT_DERIVED` | evidence-backed derivation |
| `APPROXIMATED` | MV `APPROXIMATED` |
| `SYNTHETIC` | MV `SYNTHETIC` |

Location-specific labels do not replace `REAL`, `APPROXIMATED`, `ASSUMED`, `SYNTHETIC`, or `NOT_AVAILABLE`.

`SPATIAL_LOCATION_MODEL = PASS`
`MAP_ACQUISITION_ARCHITECTURE = PASS`
`PROVIDER_NEUTRALITY = PASS`
`LOCATION_DRIVEN_SOURCE_RESOLUTION = PASS`
`POINT_SUPPORT = YES`
`LINE_SUPPORT = YES`
`POLYGON_SUPPORT = YES`
`TERRITORIAL_BOUNDARY_SUPPORT = YES`
