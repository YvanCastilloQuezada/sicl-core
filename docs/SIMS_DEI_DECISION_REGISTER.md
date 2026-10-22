# SiMS-DeI — Decision Register

**Estado:** registro documental de decisiones del baseline RFC-019

## SC-004 — Escala espacial declarada

`Project.spatial_scope` debe utilizar una de las once escalas canónicas: `pais`, `macro_region`, `region`, `provincia_metropoli`, `distrito_ciudad`, `zona_barrio_sector`, `parcela_sitio`, `edificacion`, `sistema`, `espacio` u `objeto`. El Core no infiere una escala desde nombres, ubicaciones, hechos u observaciones.

## SC-006 — Criterio formal de escala

Una escala espacial del modelo debe tener una entidad o alcance propio, decisiones de modelado propias y una semántica normativa o de aplicación propia. La inclusión de una escala no afirma relaciones territoriales reales; esas relaciones requieren registros explícitos mediante `ScaleRelation`.

## PO-012 — Aprobación de RFC-019

RFC-019 — Multiscale Refinement queda aprobado para actualizar el Core de nueve a once escalas canónicas, añadir `macro_region` y `sistema`, renombrar los valores heredados y ejecutar una migración explícita. La decisión no autoriza modificaciones del frontend, despliegues ni la implementación de RFC-020, RFC-021 o RFC-022.

**Estado:** APPROVED / IMPLEMENTED en `rfc-019-multiscale-refinement`.
