# RFC-001 — Multiscale Model

**Estado:** IMPLEMENTED
**Baseline:** `sicl-core@76f0d345`
**Rama:** `rfc-001-multiscale-model`

## Objetivo

Formalizar en `Project` la escala espacial canónica y el alcance temporal de SiMS-DeI sin inferir una escala cuando el proyecto no la declara.

## SpatialScope

| Valor de código | Etiqueta | Escala |
|---|---|---|
| `pais` | País | País |
| `region` | Región | Región |
| `provincia_metropoli` | Provincia / Metrópoli | Provincia / Metrópoli |
| `ciudad_distrito` | Ciudad / Distrito | Ciudad / Distrito |
| `barrio_sector` | Barrio / Sector | Barrio / Sector |
| `parcela_sitio` | Parcela / Sitio | Parcela / Sitio |
| `edificio` | Edificio | Edificio |
| `espacio` | Espacio | Espacio |
| `objeto` | Objeto | Objeto |

## TemporalScope

Los valores mínimos son `proyecto`, `corto_plazo`, `mediano_plazo`, `largo_plazo`, `escenario_2030`, `escenario_2040` y `escenario_2050`. El valor por defecto es `proyecto`.

## Semántica constitucional

`Project.spatial_scope` es opcional y su valor por defecto es `null`. `null` significa que el proyecto todavía no ha declarado una escala espacial; el sistema no debe inferirla desde el nombre, la ubicación, los hechos ni las observaciones. `Project.temporal_scope` siempre tiene un valor controlado y comienza en `proyecto`.

La creación puede declarar ambos scopes. El comando `/PROJECT SET SCOPE` modifica el proyecto abierto y registra un evento append-only `SCOPE_CHANGED` con actor y timestamp. Un valor inválido produce `INVALID_SCOPE`.

## Relación con el Decision Register

El modelo implementa el mapa canónico de nueve escalas descendentes aprobado para SiMS-DeI: País, Región, Provincia/Metrópoli, Ciudad/Distrito, Barrio/Sector, Parcela/Sitio, Edificio, Espacio y Objeto. Esta RFC no crea nuevas entidades ni modifica la autoridad humana, los eventos ni las capacidades HTTP v1 existentes.
