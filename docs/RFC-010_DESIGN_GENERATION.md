# RFC-010 — Design Generation

**Estado:** IMPLEMENTED en rama dedicada `rfc-010-design-generation`  
**Base:** `main@14e31987cff90f4cc93a7167e2d28c5f5cb8be9f`  
**Alcance:** SICL 2.1 — generación explícita de alternativas candidatas.

## Propósito

Design Generation produce conjuntos de candidatos a partir de entradas declaradas por el usuario. Es una capacidad analítica y propositiva: no decide, no recomienda y no filtra candidatos mediante criterios ocultos. Un `GeneratedAlternative` es distinto de una `Alternative` formal.

## Entidad

`GeneratedAlternative` contiene `generation_id`, `project_id`, `generator`, `generator_version`, `method`, `inputs`, `candidates`, `rationale`, `state`, `generation_hash`, `created_at` y `version`. El hash SHA-256 se calcula sobre las entradas y candidatos serializados canónicamente.

Los estados son `GENERATED`, `INSUFFICIENT` y `FAILED`. La generación insuficiente conserva el intento y explica qué entrada crítica falta.

## Métodos

| Método | Estado | Comportamiento |
|---|---|---|
| `parametric_grid_v1` | Activo | Producto cartesiano de parámetros declarados mediante listas, `values` o rangos `min`/`max`/`step`. |
| `pattern_variation_v1` | Activo | Aplica variaciones declaradas a un patrón de referencia declarado. |
| `llm_assisted_v1` | Catálogo, inactivo | Requiere un contrato explícito con IA; no se ejecuta. |
| `evolutionary_v1` | Catálogo, inactivo | Requiere contrato de población y función de aptitud; no se ejecuta. |

## CLI

```text
/GENERATE DESIGN <method> '<json_inputs>'
/GENERATE LIST
/GENERATE SHOW <generation_id>
/GENERATE METHODS
/ALTERNATIVE PROMOTE <generation_id> <candidate_index> <actor> <authority>
```

La promoción crea una `Alternative` formal con `source=DESIGN_GENERATION`, pero no crea `Recommendation` ni `Decision`. La promoción exige actor y authority explícitos.

## HTTP v1

```text
POST /v1/projects/{project_id}/generations
GET  /v1/projects/{project_id}/generations
GET  /v1/projects/{project_id}/generations/{generation_id}
POST /v1/projects/{project_id}/generations/{generation_id}/promote
GET  /v1/generations/methods
```

Las respuestas emplean el envelope canónico v1. Las generaciones y sus candidatos son append-only; una promoción es una mutación separada y auditable.

## Invariantes

1. `GeneratedAlternative != Alternative`.
2. Generation no decide ni recomienda.
3. No se aplican filtros ocultos: todos los valores declarados generan candidatos, salvo entradas inválidas o insuficientes.
4. La promoción requiere autoridad humana representada por `actor` y `authority`.
5. Las generaciones son persistentes y append-only.
6. Los métodos no activos no se ejecutan.

## Fuera de alcance

No se implementan generación asistida por LLM, evolución, optimización adicional, decisión automática, recomendación automática ni cambios en frontend o infraestructura.
