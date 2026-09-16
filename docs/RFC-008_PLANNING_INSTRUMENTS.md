# RFC-008 — Planning Instruments Model

**Estado:** IMPLEMENTED (estructura)
**Rama:** `rfc-008-planning-instruments`

## Objetivo

RFC-008 define la estructura canónica para representar instrumentos de planificación nacionales, regionales, provinciales, metropolitanos, urbanos, locales y sectoriales. Esta fase no carga instrumentos reales ni interpreta normativa.

## Distinción SC-005

> **MANDATORY REGULATION ≠ PLANNING INSTRUMENT ≠ DESIGN PRINCIPLE ≠ REFERENCE ≠ PREFERENCE**

`PlanningInstrument` representa un instrumento de planificación. No es una regulación obligatoria, un principio de diseño, una referencia documental ni una preferencia del usuario. Regulatory Intelligence permanece en RFC-003 y `DesignPrinciple` en RFC-004.

## Entidad

`PlanningInstrument` incluye `instrument_id`, `project_id` opcional, `instrument_type`, `name`, `jurisdiction`, `authority`, `approval_date`, `validity_period`, `scope_applicable`, `status`, `objectives`, `url`, `summary`, `source` y `version`.

Si no existe una fuente verificable, su estado es `UNKNOWN`. La fuente no se infiere y ningún instrumento produce automáticamente una Constraint, Recommendation, Preference o Decision.

## Tipos

`PLAN_NACIONAL`, `PLAN_REGIONAL`, `PLAN_PROVINCIAL`, `PLAN_METROPOLITANO`, `PLAN_URBANO`, `PLAN_LOCAL`, `PLAN_SECTORIAL`, `POLITICA_NACIONAL`, `INSTRUMENTO_TERRITORIAL` y `OTRO`.

Los estados son `DRAFT`, `ACTIVE`, `SUPERSEDED`, `REPEALED` y `UNKNOWN`.

## CLI

- `/PLANNING ADD <instrument_id> <instrument_type> <name> [jurisdiction] [url]`
- `/PLANNING LIST`
- `/PLANNING SHOW <instrument_id>`
- `/PLANNING TYPES`

La estructura `src/sicl/planning_catalog.py` permanece vacía hasta que el Product Owner autorice y proporcione un corpus verificable.

## HTTP `/v1`

- `GET /v1/planning/instruments` con filtros opcionales `instrument_type`, `jurisdiction` y `scope_applicable`.
- `GET /v1/planning/instruments/{instrument_id}`.
- `GET /v1/planning/types`.
- `POST /v1/projects/{id}/planning/instruments` con `{ "instrument_id": "..." }`.
- `GET /v1/projects/{id}/planning/instruments`.

Las respuestas HTTP usan el envelope canónico. El vínculo a un proyecto registra `PLANNING_INSTRUMENT_LINKED` con actor y timestamp.

## Persistencia e invariantes

Los instrumentos y vínculos se almacenan en SQLite con triggers append-only. Un proyecto puede vincular cero o más instrumentos. Vincular un instrumento no crea Constraints ni altera Facts, Assumptions, Preferences, Recommendations o Decisions.

La conversión explícita de un instrumento a una Constraint, si alguna vez se autoriza, requerirá una operación y evento propios; no forma parte de RFC-008.

## No cargado en esta fase

No se cargan planes, políticas, normas, URLs oficiales ni corpus regulatorios reales. No se modifica RFC-003, RFC-004, RFC-005, RFC-006 o RFC-007.
