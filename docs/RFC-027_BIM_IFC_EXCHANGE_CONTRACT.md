# RFC-027 — BIM/IFC Exchange Contract

**Estado:** IMPLEMENTED — lectura persistente y change sets en `PREVIEW`
**Sistema:** SiMS-DeI / SICL
**Fecha:** 16 de septiembre de 2026
**Dependencias:** RFC-019, RFC-020, RFC-021, RFC-024, RFC-026

## 1. Objetivo

RFC-027 incorpora una superficie canónica para recibir snapshots BIM provenientes de IFC, Revit o Archicad y producir change sets de exportación revisables. La primera implementación es deliberadamente conservadora: registra datos de modelos en SQLite, valida escala, unidades, CRS y procedencia, y nunca modifica un archivo BIM ni crea una decisión humana automáticamente.

## 2. Alcance implementado

Se implementan:

- `BIMElementReference`.
- `BIMModelSnapshot`.
- `BIMParameterMapping`.
- `BIMChangeSet`.
- Persistencia append-only en SQLite.
- Endpoints de creación y consulta de snapshots.
- Endpoint de creación de change sets únicamente en modo `PREVIEW`.
- Pruebas de reinicio, trazabilidad, duplicados y autoridad.
- Diagrama de arquitectura en `docs/RFC-027_ARCHITECTURE_FLOW.mmd`.

## 3. No objetivos

Esta versión no:

- Instala un add-in de Revit.
- Escribe en Revit o Archicad.
- Exporta directamente a RVT o PLN.
- Resuelve automáticamente conflictos de modelos.
- Interpreta normativa a partir de parámetros BIM.
- Convierte parámetros en constraints sin revisión.
- Usa un modelo de lenguaje para modificar el Core.

## 4. Entidades

### 4.1 BIMElementReference

Representa un elemento identificable dentro de un snapshot.

Campos principales:

- `global_id`.
- `entity`, por ejemplo `IfcWall`.
- `parameters`.
- `provenance`.

### 4.2 BIMModelSnapshot

Representa una captura inmutable del modelo en un momento concreto.

Campos principales:

- `exchange_id`.
- `format`: `IFC`, `REVIT` o `ARCHICAD`.
- `source_application`.
- `source_version`.
- `project_id`.
- `spatial_scope`.
- `coordinate_reference_system`.
- `units`.
- `model_hash`.
- `elements`.
- `review_state`.
- `version`.

### 4.3 BIMChangeSet

Representa un conjunto de cambios propuesto para exportación. En esta fase únicamente puede tener:

```text
mode = PREVIEW
```

Por tanto, su creación no modifica el modelo externo.

## 5. Persistencia

Se añadieron tablas append-only:

- `bim_model_snapshots`.
- `bim_change_sets`.

Cada tabla conserva versión, estado de revisión, fecha, hash o referencia de snapshot. Triggers SQLite bloquean `UPDATE` y `DELETE` destructivos.

## 6. HTTP API

### Crear snapshot

```http
POST /v1/projects/{project_id}/bim/snapshots
```

### Listar snapshots

```http
GET /v1/projects/{project_id}/bim/snapshots
```

### Obtener snapshot

```http
GET /v1/projects/{project_id}/bim/snapshots/{exchange_id}
```

### Crear change set preview

```http
POST /v1/projects/{project_id}/bim/change-sets
```

La request debe mantener:

```json
{
  "mode": "PREVIEW"
}
```

Cualquier otro modo es rechazado con `BIM_PREVIEW_ONLY`.

### Listar change sets

```http
GET /v1/projects/{project_id}/bim/change-sets
```

## 7. Invariantes constitucionales

1. Un snapshot BIM es evidencia de una fuente externa, no una decisión.
2. `model_hash` es obligatorio para trazabilidad.
3. La escala espacial debe ser una de las once escalas canónicas.
4. CRS y unidades son obligatorios.
5. Los snapshots son append-only.
6. Un change set no se aplica automáticamente.
7. La exportación requiere revisión humana posterior.
8. BIM no puede crear `Decision`.
9. BIM no puede promover una norma.
10. El Core SICL sigue siendo determinista.

## 8. Arquitectura

El flujo completo está documentado en el diagrama Mermaid:

```text
Fuentes BIM/GIS/Copiloto
  → Adaptadores
    → Contratos canónicos
      → Validación de esquema, ontología y procedencia
        → SICL Core determinista
          → Resultados, auditoría y change set preview
            → Exportación posterior con autorización humana
```

## 9. Siguiente fase

La siguiente fase puede añadir un adaptador IFC real, lectura de archivos y mappings revisables. La aplicación de cambios en Revit o Archicad requiere un RFC posterior, permisos explícitos, comparación antes/después y mecanismo de rollback.
