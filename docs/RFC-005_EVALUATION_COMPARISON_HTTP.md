# RFC-005 — Evaluation / Comparison HTTP

**Estado:** IMPLEMENTED
**Base:** `integration-v2` (`1492c074`)

## Objetivo

Exponer por REST canónico `/v1/...` las entidades analíticas `Evaluation` y `Comparison`, sin convertirlas en Recommendation ni Decision.

## Estructuras existentes

`Evaluation` se define en `src/sicl/v11.py` con `evaluation_id`, `alternative_id`, `objective_id`, `value`, `unit`, `confidence`, `source` y `version`. Su relación es una Alternative y un Objective; la entidad no contiene actualmente campos separados de `method`, `inputs`, `provenance`, `contract_version` o `feasibility`. La procedencia disponible es `source`.

`Comparison` se define con `comparison_id`, `project_id`, `alternative_ids`, `evaluations`, `tradeoffs` y `version`. Relaciona dos o más Alternatives y contiene las Evaluations asociadas. No contiene actualmente una relación persistida con Objectives.

`Alternative` se define con `alternative_id`, `project_id`, `name`, `description`, `parameters`, `status`, `version` y `source`.

## Endpoints

| Método | Endpoint | Operación |
|---|---|---|
| `POST` | `/v1/projects/{project_id}/evaluations` | Registra una Evaluation mediante el handler CLI existente |
| `GET` | `/v1/projects/{project_id}/evaluations` | Lista y filtra por `alternative` u `objective` |
| `POST` | `/v1/projects/{project_id}/comparisons` | Crea una Comparison de al menos dos Alternatives |
| `GET` | `/v1/projects/{project_id}/comparisons` | Lista Comparisons del proyecto |

Todas las respuestas exitosas usan el envelope v1: `contract_version`, `status`, `code`, `message`, `project_id`, `observed_version` y `data`.

## Requests

Evaluation:

```json
{
  "alternative": "Alpha",
  "objective": "ENERGY_SAVINGS",
  "value": 82,
  "unit": "%",
  "confidence": "0.8",
  "source": "USER_INPUT"
}
```

Comparison:

```json
{
  "alternatives": ["Alpha", "Beta"],
  "objectives": ["ENERGY_SAVINGS"]
}
```

`objectives` se acepta como contexto de request, pero no se persiste porque el modelo actual de `Comparison` no contiene ese campo.

## Invariantes

Una Evaluation requiere Alternative, Objective y Value existentes. Las claves `(alternative_id, objective_id)` no se duplican. Una Comparison requiere al menos dos Alternatives distintas y no duplica el mismo conjunto.

La creación de Evaluation o Comparison produce únicamente su evento correspondiente. No crea Recommendation ni Decision. Recommendation continúa siendo una operación separada mediante `/RECOMMEND`; Decision mantiene autoridad humana y HumanReview.

Las entidades se persisten en SQLite y se recuperan después de reiniciar el repositorio. No se añadieron inferencias ni campos ausentes al modelo.
