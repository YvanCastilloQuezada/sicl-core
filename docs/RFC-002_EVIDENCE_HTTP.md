# RFC-002 — Evidence HTTP

**Estado:** IMPLEMENTED
**Base:** RFC-001 multiscale model plus RFC-002 Phase C HTTP v1

## Objetivo

Evidence es una entidad canónica de primera clase para registrar declaraciones capturadas desde documentos, observaciones, mediciones, referencias, testimonios o fuentes normativas.

## Entidades

`Evidence` contiene `evidence_id`, `project_id`, `source_id`, `statement`, `evidence_type`, `captured_at`, `method_version`, `evidence_url`, `evidence_hash`, `state` y `version`.

`Source` contiene `source_id`, `project_id`, `source_type`, `title`, `url` y `version`. La referencia a Source es opcional.

Los tipos de Evidence son `DOCUMENT`, `OBSERVATION`, `MEASUREMENT`, `REFERENCE`, `TESTIMONY`, `NORMATIVE` y `OTHER`. Los tipos de Source son `OFFICIAL`, `SECONDARY`, `USER_PROVIDED` y `UNKNOWN`.

Los estados de conocimiento admitidos son `OBSERVED`, `UNKNOWN`, `CONFLICTING` e `INSUFFICIENT`.

## Endpoints

| Método | Endpoint | Semántica |
|---|---|---|
| `POST` | `/v1/projects/{id}/evidence` | Crea Evidence append-only |
| `GET` | `/v1/projects/{id}/evidence` | Lista Evidence del proyecto |
| `GET` | `/v1/projects/{id}/evidence/{evidence_id}` | Recupera una Evidence |

Todas las respuestas exitosas usan el envelope v1 con `contract_version`, `project_id` y `observed_version`.

## Comandos CLI

- `/EVIDENCE ADD <evidence_id> <statement> <evidence_type> [source_id] [evidence_url]`
- `/EVIDENCE LIST`
- `/EVIDENCE SHOW <evidence_id>`

Cada creación produce exactamente un evento `EVIDENCE_ADDED` con actor y timestamp.

## Invariantes

Evidence registra lo que se declara y no infiere contenido. No se convierte automáticamente en Fact ni Assumption. Si no se recibe `evidence_hash`, se calcula como SHA-256 de `statement`. Evidence no se actualiza ni elimina; una futura sustitución deberá registrarse como una nueva Evidence relacionada mediante un mecanismo explícito.

## Persistencia

SQLite usa tablas `evidence` y `sources`. La clave primaria compuesta `(project_id, evidence_id)` evita duplicados dentro de un proyecto. La persistencia se conserva tras reiniciar el repositorio.
