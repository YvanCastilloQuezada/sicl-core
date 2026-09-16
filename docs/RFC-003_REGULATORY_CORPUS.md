# RFC-003 — Regulatory Corpus Model

**Estado:** IMPLEMENTED (estructura)
**Rama:** `rfc-003-regulatory-corpus`

## Objetivo

RFC-003 define la estructura canónica para representar regulación obligatoria, interpretaciones normativas y snapshots normativos congelables. Esta fase no carga contenido real, no interpreta jurídicamente, no certifica vigencia y no certifica cumplimiento.

## Distinción SC-005

> **Regulation ≠ PlanningInstrument ≠ DesignPrinciple ≠ Reference ≠ Preference**

`Regulation` representa una fuente normativa obligatoria. `PlanningInstrument` pertenece a RFC-008; `DesignPrinciple` pertenece a RFC-004. Ninguna de estas categorías se convierte automáticamente en Constraint, Recommendation o Decision.

## Entidades

### Regulation

Incluye identificador, jurisdicción, autoridad, código oficial, título, versión, fechas de publicación y vigencia, estado, fuente, hash de evidencia, escalas aplicables, relación de modificación/derogación y resumen. Los estados son `VIGENTE`, `MODIFICADA`, `DEROGADA` y `NO_VERIFICADA`; el alta inicial queda en `NO_VERIFICADA` porque el sistema no asume vigencia.

### NormativeInterpretation

Incluye artículo, texto interpretativo, proyecto opcional, actor, fecha, confianza y estado. Toda interpretación contiene exactamente el disclaimer obligatorio:

> No constituye certificación legal ni reemplaza revisión profesional.

Una interpretación en estado `REVIEWED` requiere actor y autoridad en la operación de revisión. La revisión no crea una Constraint automáticamente.

### NormativeSnapshot

Representa el corpus normativo de un proyecto en una fecha de corte. Incluye las regulaciones e interpretaciones incluidas, estado y revisor. `FROZEN` es inmutable; cualquier cambio del corpus requiere otro snapshot.

## Comandos CLI

- `/REGULATION ADD <regulation_id> <code> <title> [jurisdiction] [source_url]`
- `/REGULATION LIST`
- `/REGULATION SHOW <regulation_id>`
- `/REGULATION STATUS <regulation_id> <status>`
- `/INTERPRET ADD <interpretation_id> <regulation_id> <article_reference> <interpretation_text>`
- `/INTERPRET LIST [regulation_id]`
- `/INTERPRET REVIEW <interpretation_id> <actor> <authority>`
- `/SNAPSHOT CREATE <snapshot_id> <project_id> <cut_date>`
- `/SNAPSHOT LIST <project_id>`
- `/SNAPSHOT FREEZE <snapshot_id> <reviewer>`

## Endpoints REST v1

- `POST /v1/regulations`
- `GET /v1/regulations`
- `GET /v1/regulations/{regulation_id}`
- `POST /v1/regulations/{regulation_id}/status`
- `POST /v1/regulations/{regulation_id}/interpretations`
- `GET /v1/regulations/{regulation_id}/interpretations`
- `POST /v1/interpretations/{interpretation_id}/review`
- `POST /v1/projects/{id}/normative-snapshots`
- `GET /v1/projects/{id}/normative-snapshots`
- `POST /v1/normative-snapshots/{snapshot_id}/freeze`

Todos usan el envelope HTTP v1. Las operaciones globales se vinculan a un proyecto de auditoría para mantener el event log append-only con `project_id`.

## Invariantes

1. Regulation no es PlanningInstrument, DesignPrinciple, Preference ni Evidence.
2. La ausencia de fuente oficial produce `NO_VERIFICADA`.
3. La ausencia de vigencia verificada no se interpreta como `VIGENTE`.
4. Regulation e Interpretation no crean Constraints automáticamente.
5. Interpretation requiere HumanReview/autoridad humana para considerarse aplicada.
6. El disclaimer es obligatorio y no puede omitirse.
7. Regulatory Intelligence no decide, recomienda ni certifica cumplimiento.
8. Los registros regulatorios y snapshots son append-only.
9. Un snapshot `FROZEN` no se actualiza; se crea uno nuevo.
10. Cambiar una Regulation no modifica snapshots anteriores.

## Catálogo

`src/sicl/regulatory_catalog.py` está deliberadamente vacío. No se cargan normas reales, fuentes oficiales, interpretaciones jurídicas ni afirmaciones de vigencia en RFC-003.
