# RFC-026 — Plan de persistencia SQLite y carga bibliográfica

## Propósito

Este plan define la siguiente fase de RFC-026: persistir `DesignKnowledgeSource`, `DesignKnowledgeItem` y `DesignPattern` en SQLite y cargar de forma estructurada un primer lote de fuentes teóricas. El plan conserva el piloto actual de Alexander, Ching y RNE-A.010 y no cambia la lógica del agente ni promueve heurísticas a normativa.

## Fase 1 — Esquema SQLite

Añadir tablas append-only:

- `design_knowledge_sources`.
- `design_knowledge_items`.
- `design_patterns`.
- `design_knowledge_events`.

Cada tabla debe incluir `version`, `review_status`, `created_at` y un hash estable. Las listas y objetos se almacenarán como JSON canónico con orden estable. Las claves de fuente, item y patrón serán únicas por identificador y versión.

El esquema debe incluir claves de procedencia hacia `sources` y `evidence` cuando el registro se vincule al proyecto. Las fuentes bibliográficas del catálogo global no deben depender de un `project_id`; el uso en un proyecto se registrará mediante una tabla de relación o mediante eventos de consulta.

Se crearán triggers que impidan actualización o eliminación destructiva. Una corrección generará una nueva versión y un evento `DESIGN_KNOWLEDGE_VERSION_CREATED`.

## Fase 2 — Repositorio

Añadir al repositorio:

```text
insert_design_knowledge_source
get_design_knowledge_source
list_design_knowledge_sources
insert_design_knowledge_item
get_design_knowledge_item
list_design_knowledge_items
insert_design_pattern
get_design_pattern
list_design_patterns
record_design_knowledge_event
```

Las operaciones de escritura deben validar:

- Fuente existente para cada item.
- Al menos una escala aplicable.
- Ausencia de escalas simultáneamente incluidas y excluidas.
- Estado de revisión permitido.
- Licencia declarada.
- Prohibición de convertir `THEORETICAL` o `HEURISTIC` en `LEGAL` sin revisión explícita.

## Fase 3 — Carga estructurada

La carga se realizará desde JSON versionado, no desde texto libre:

```text
data/design_knowledge/sources.json
 data/design_knowledge/items.json
 data/design_knowledge/patterns.json
```

Cada lote tendrá:

- `batch_id`.
- `schema_version`.
- `retrieved_at`.
- `reviewer`.
- `license_status`.
- `source_hash`.
- `status`.

El cargador debe ser idempotente. Repetir el mismo lote no debe duplicar registros.

## Fase 4 — Primer lote teórico

El primer lote conservará las fuentes ya presentes:

1. Christopher Alexander — `A Pattern Language`.
2. Francis D. K. Ching — `Architecture: Form, Space, and Order`.
3. Corpus RNE RFC-025 como fuente normativa separada.

No se añadirán nuevas fuentes bibliográficas en esta fase. Alexander se cargará como fuente `THEORETICAL` con patrones `PATTERN_REFERENCE`. Ching se cargará como fuente `THEORETICAL` con `DESIGN_PRINCIPLE` y `SPATIAL_RELATION`. RNE continuará con estado de verificación propio y no se copiará como patrón.

## Fase 5 — Revisión editorial y de licencia

Antes de marcar una fuente como `APPROVED`, una autoridad editorial debe comprobar:

- Identidad bibliográfica.
- Autoría y edición.
- Idioma.
- Licencia o permiso de extracción.
- Resumen propio frente a reproducción literal.
- Ubicación de referencia, capítulo o página.
- Escalas y tipologías aplicables.
- Limitaciones culturales o contextuales.

El contenido protegido no se almacenará íntegramente. Se conservarán metadatos, resúmenes propios y localizadores bibliográficos autorizados.

## Fase 6 — Integración del agente

El `DesignKnowledgeAgent` pasará de catálogo estático a repositorio consultable. Su contrato de salida no cambia. Debe continuar separando:

```text
normative_references
applicable_items
applicable_patterns
conflicts
open_questions
review_state
```

El agente deberá registrar `knowledge_query_id`, versión del catálogo, hashes y fuentes recuperadas para reproducibilidad.

## Fase 7 — Migración y compatibilidad

El catálogo estático actual se utilizará como lote inicial de migración. La migración no debe cambiar identificadores ni estados. Los endpoints existentes continuarán funcionando durante la transición.

## Fase 8 — Pruebas de aceptación

Se requerirán pruebas para:

- Persistencia tras reinicio.
- Idempotencia del cargador.
- Rechazo de fuente inexistente.
- Rechazo de escala inválida.
- Rechazo de item sin fuente.
- Rechazo de licencia ausente.
- Append-only y versionado.
- Separación RNE / teoría.
- Consulta en las 11 escalas.
- Reproducción de la misma respuesta con el mismo catálogo.
- Ausencia de `Decision` creada por el agente.

## Criterio de finalización

La fase estará completa cuando el catálogo inicial pueda cargarse en una base SQLite vacía, consultarse mediante los dos endpoints RFC-026, sobrevivir a un reinicio, conservar trazabilidad y producir el mismo estado de revisión que el piloto actual.
