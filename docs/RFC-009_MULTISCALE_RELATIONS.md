# RFC-009 — Multiscale Relations and Objective Propagation

**Estado:** IMPLEMENTED — rama dedicada `rfc-009-multiscale-relations`

## Alcance

RFC-009 implementa la capacidad estructural mínima para modelar relaciones entre proyectos SICL en las once escalas canónicas de SiMS-DeI. El módulo no inventa datos territoriales, límites administrativos, normativa ni relaciones reales: solo registra relaciones explícitas proporcionadas por una autoridad o integración autorizada.

Las escalas reconocidas son `pais`, `macro_region`, `region`, `provincia_metropoli`, `distrito_ciudad`, `zona_barrio_sector`, `parcela_sitio`, `edificacion`, `sistema`, `espacio` y `objeto`. La jerarquía es consultable como catálogo determinista. `CONTAINS` exige scopes espaciales explícitos y una relación ancestro→descendiente; `OVERLAPS`, `INFLUENCES` y `DEPENDS_ON` no se infieren automáticamente.

## Entidades

`ScaleRelation` contiene `relation_id`, `parent_project_id`, `child_project_id`, `relation_type`, `description`, `created_by`, `created_at` y `version`. Las relaciones se almacenan en SQLite con triggers append-only. El evento `SCALE_RELATION_CREATED` conserva la trazabilidad de actor y fuente `USER_COMMAND` o la fuente server-side correspondiente.

`Objective.source_parent_objective_id` es opcional. Cuando un proyecto hijo importa un objetivo desde un proyecto ancestro mediante `/PROJECT IMPORT OBJECTIVE`, el objetivo nuevo conserva su identidad local y referencia explícitamente al objetivo de origen. No se convierte en el mismo registro ni se propaga automáticamente.

## Interfaces CLI

- `/SCALE PARENT <scope>`
- `/SCALE CHILDREN <scope>`
- `/SCALE RELATE <parent_project_id> <child_project_id> <relation_type> [description]`
- `/SCALE RELATIONS <project_id>`
- `/PROJECT IMPORT OBJECTIVE <source_project_id> <objective_id>`

## Interfaces HTTP v1

- `GET /v1/scales`
- `GET /v1/scales/{scope}/parent`
- `GET /v1/scales/{scope}/children`
- `POST /v1/projects/{project_id}/scale-relations`
- `GET /v1/projects/{project_id}/scale-relations`
- `POST /v1/projects/{project_id}/import-objective`

## Invariantes

1. Ningún proyecto puede relacionarse consigo mismo.
2. `CONTAINS` requiere `spatial_scope` explícito y compatibilidad ancestro→descendiente.
3. Las relaciones no se eliminan ni actualizan; solo se agregan nuevas versiones identificables.
4. La importación de objetivos requiere una relación `CONTAINS` explícita y conserva `source_parent_objective_id`.
5. La relación multiescala no crea decisiones, recomendaciones ni autoridad implícita.
6. El modelo no afirma que una relación exista en el mundo real hasta que un actor la registre.

## Fuera de alcance

Quedan fuera de RFC-009 la carga de un corpus geográfico real, GIS, geocodificación, inferencia de relaciones, sincronización territorial, propagación automática de restricciones, cascadas entre escalas, agentes y cualquier decisión automática.


## RFC-019 — Ejemplos con las escalas refinadas

La cadena canónica permite relaciones explícitas entre una `edificacion` y su `sistema`, y entre un `sistema` y un `espacio`. Por ejemplo, `BUILD-001` puede declarar `edificacion`, `SYSTEM-001` puede declarar `sistema` y `ROOM-001` puede declarar `espacio`. Las relaciones `CONTAINS` entre cada par solo son válidas cuando respetan la jerarquía inmediata o ancestral y han sido registradas explícitamente.

`macro_region` se sitúa entre `pais` y `region`. `distrito_ciudad` sustituye a `ciudad_distrito`, `zona_barrio_sector` sustituye a `barrio_sector` y `edificacion` sustituye a `edificio`. Los valores anteriores no son aliases HTTP; las bases se actualizan mediante la migración RFC-019.
