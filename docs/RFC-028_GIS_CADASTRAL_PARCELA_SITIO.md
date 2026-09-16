# RFC-028 — Integración GIS y Catastro para PARCELA_SITIO

**Estado:** DRAFT — propuesta técnica
**Sistema:** SiMS-DeI / SICL
**Fecha:** 16 de septiembre de 2026
**Dependencias:** RFC-019, RFC-020, RFC-021, RFC-024, RFC-025, RFC-027

## 1. Objetivo

RFC-028 define la integración de datos GIS y mapas catastrales reales con SICL para la escala canónica `PARCELA_SITIO`. El sistema podrá consultar geometrías y atributos publicados por fuentes autorizadas, conservar la procedencia de cada respuesta y presentar la información para revisión humana. La integración no afirmará propiedad, zonificación o edificabilidad sin una fuente y revisión suficientes.

OGC API Features proporciona una superficie interoperable para consultar colecciones y entidades geoespaciales, incluyendo GeoJSON, filtros espaciales, paginación y declaración de CRS [1]. OGC API Records puede utilizarse para descubrir y consultar metadatos de recursos geoespaciales [2].

## 2. Principios

El dato geográfico se trata como un snapshot temporal. Cada snapshot debe conservar fuente, fecha de consulta, CRS, hash de respuesta y jurisdicción. La geometría es un hecho espacial; no es por sí misma una decisión normativa ni una prueba de propiedad.

Los datos catastrales externos se registran como `Evidence` y `Fact`. Una fuente puede permanecer en estado `UNVERIFIED` o `REVIEW_REQUIRED`. El Core determinista nunca promoverá automáticamente una fuente a `VIGENTE`.

## 3. Entidades propuestas

### 3.1 ParcelSnapshot

Representa la geometría y atributos recibidos de una fuente en un momento concreto.

```json
{
  "parcel_id": "PE-TRU-001",
  "project_id": "P-001",
  "geometry": {"type": "Polygon", "coordinates": []},
  "source_url": "https://example.gob.pe/ogc/collections/parcels",
  "source_type": "OFFICIAL",
  "jurisdiction": "PE-TRUJILLO",
  "source_crs": "EPSG:4326",
  "analysis_crs": "EPSG:32717",
  "retrieved_at": "2026-09-16T23:00:00Z",
  "validity_date": null,
  "response_hash": "sha256:...",
  "review_state": "HUMAN_REVIEW_REQUIRED"
}
```

### 3.2 GeometryEvidence

Registra una afirmación espacial concreta, como área recibida, límite publicado o punto de acceso. Debe incluir referencia al `ParcelSnapshot` y no debe convertirse automáticamente en una restricción.

### 3.3 CadastralSource

Describe el servicio, organismo, licencia, colección, versión y condiciones de consulta. La fuente debe tener un estado de disponibilidad independiente del estado de validez legal.

### 3.4 ParcelBoundaryConflict

Registra discrepancias entre fuentes o entre geometría aportada por el usuario y geometría oficial. Un conflicto bloquea cualquier uso que dependa de límites no resueltos.

## 4. Flujo operativo

El usuario selecciona una parcela o define un polígono. El adaptador consulta la colección autorizada y solicita la representación GeoJSON con el CRS requerido. SICL valida la forma, la existencia de identificador, la correspondencia de jurisdicción y la trazabilidad de la respuesta. Después, el sistema crea un snapshot append-only y lo presenta en el mapa.

Una consulta puede contribuir a una evaluación solamente cuando el usuario confirma el mapeo. Si la fuente está caducada, incompleta o en conflicto, la evaluación debe devolver un estado de revisión requerido y no una conclusión de cumplimiento.

## 5. Contrato de consulta

```http
GET /collections/{collectionId}/items?bbox=...&crs=...
```

El adaptador debe soportar content negotiation para GeoJSON cuando la fuente lo ofrezca. La respuesta se guarda de forma canónica antes de calcular el hash. El sistema debe conservar los enlaces `next` para recorrer respuestas paginadas.

## 6. Validaciones

SICL debe comprobar que el GeoJSON contiene una geometría válida, que el CRS declarado coincide con el solicitado y que el identificador de parcela no está vacío. También debe comprobar que el recurso pertenece a la jurisdicción indicada y que la fecha de consulta está disponible.

La validación geométrica no equivale a la validación legal. Una geometría válida puede ser antigua o no representar el límite jurídico vigente.

## 7. Integración con escalas

`PARCELA_SITIO` es el nivel primario de RFC-028. Una parcela puede relacionarse con `ZONA_BARRIO_SECTOR`, `DISTRITO_CIUDAD`, `EDIFICACION` y `SISTEMA`, pero esas relaciones deben ser explícitas y trazables. El adaptador no inferirá automáticamente una escala superior a partir de la geometría.

## 8. Seguridad y operación

Las credenciales de servicios privados deben permanecer en el servidor. El navegador no debe recibir tokens de catastro. El sistema debe aplicar límites de tamaño, timeout, validación de tipos y control de URLs permitidas. Las respuestas grandes deben procesarse por páginas y no cargarse sin límite en memoria.

## 9. API propuesta

```http
POST /v1/projects/{project_id}/gis/parcel-snapshots
GET  /v1/projects/{project_id}/gis/parcel-snapshots
GET  /v1/projects/{project_id}/gis/parcel-snapshots/{parcel_id}
POST /v1/projects/{project_id}/gis/parcel-sources
GET  /v1/gis/catalogs
```

La primera versión debe ser de solo lectura para fuentes externas. La modificación de datos catastrales no pertenece a SiMS-DeI.

## 10. Estados

| Estado | Significado |
|---|---|
| `RECEIVED` | La respuesta se recibió y tiene hash. |
| `REVIEW_REQUIRED` | Falta confirmar fuente, vigencia o aplicabilidad. |
| `VERIFIED` | Una autoridad revisó la fuente y el snapshot. |
| `CONFLICTING` | Existen discrepancias entre fuentes. |
| `EXPIRED` | La vigencia declarada ya no es suficiente. |
| `REJECTED` | La respuesta no cumple el contrato o la fuente no es aceptable. |

## 11. Criterios de aceptación

La fase inicial se considerará aceptada cuando el sistema pueda consultar un servicio OGC de prueba, conservar un `ParcelSnapshot`, representar su geometría, reproducir el hash, detectar un CRS inválido, mantener el estado `REVIEW_REQUIRED` y demostrar que ningún snapshot crea una `Decision`.

## 12. Fases posteriores

La fase siguiente añadirá un catálogo de fuentes por jurisdicción y almacenamiento persistente. Después se incorporarán reglas de caducidad, reconciliación de límites y relaciones multiescala. La conexión con catastros privados se realizará únicamente después de aprobar credenciales, licencias y política de retención.

## References

[1]: https://ogcapi.ogc.org/features/overview.html "OGC API Features overview"
[2]: https://www.ogc.org/standards/ogcapi-records/ "OGC API Records standard"
