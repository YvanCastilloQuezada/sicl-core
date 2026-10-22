# DEMO_SCRIPT_V3 — Design Knowledge Agent

## Objetivo

Demostrar que SiMS-DeI consulta conocimiento de diseño en una escala urbana, mantiene separadas las referencias normativas del RNE y los patrones teóricos, genera preguntas abiertas y no crea una decisión automática.

## Precondiciones

```bash
cd sicl-core
export PYTHONPATH=.:src
```

## Paso 1 — Catálogo por escala

```http
GET /v1/design-knowledge/catalog?scope=edificacion
```

La respuesta debe mostrar las once escalas en `data.scales` y devolver los items y patrones aplicables a `edificacion`.

## Paso 2 — Caso de diseño urbano

Caso: vivienda y espacio público de proximidad en Trujillo, escala `distrito_ciudad`, con objetivos de confort, privacidad y legibilidad urbana.

```http
POST /v1/design-knowledge/query
Content-Type: application/json

{
  "spatial_scope": "distrito_ciudad",
  "typology": "vivienda",
  "jurisdiction": "PE",
  "objectives": ["confort", "privacidad", "legibilidad urbana"],
  "problem_terms": ["publico", "privado", "barrio"],
  "requested_operation": "STRATEGY_FORMULATION",
  "facts": ["ubicación: Trujillo, Peru"],
  "assumptions": ["se requiere transición gradual entre calle y vivienda"],
  "preferences": ["priorizar confort y privacidad"]
}
```

## Paso 3 — Lectura esperada

La respuesta debe distinguir:

| Resultado | Clasificación esperada | Uso |
|---|---|---|
| RNE con estado `NO_VERIFICADA` | Normativo | `reference_only` |
| Patrón de Alexander | `THEORETICAL` | `strategy_candidate` |
| Principio de Ching | `THEORETICAL` | `evaluation_criterion` |
| Datos del caso | Fact / contexto | Insumo de consulta |
| Supuestos declarados | Assumption | Preguntas y revisión |

El agente debe emitir preguntas como:

```text
¿Qué requisitos normativos tienen aplicabilidad confirmada?
¿Qué supuestos deben convertirse en datos observados?
¿Qué tipología de intervención se está diseñando?
```

## Paso 4 — Autoridad humana

La respuesta debe confirmar:

```json
{
  "decision_created": false,
  "review_state": "HUMAN_REVIEW_REQUIRED"
}
```

La consulta no crea `Recommendation`, `HumanReview` ni `Decision`.

## Pregunta para la demostración

> ¿El agente organizó principios, patrones, normas y preguntas pendientes sin presentar una solución como decisión aprobada?

## Criterios PASS

- `distrito_ciudad` es aceptado.
- El agente devuelve estado `REVIEW_REQUIRED` o `CONFLICTING` cuando hay normativa no verificada.
- RNE permanece como `reference_only`.
- Alexander permanece como conocimiento teórico.
- Ching permanece como conocimiento teórico.
- Se muestran `open_questions` o `suggested_questions`.
- `decision_created` es `false`.
- No se produce promoción normativa automática.
