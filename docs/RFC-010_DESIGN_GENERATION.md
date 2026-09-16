# RFC-010 — Design Generation

**Estado:** IMPLEMENTED; extendido por RFC-016.1
**Base:** `main@89c7b604`
**Alcance:** SICL 2.1–2.2 — generación explícita de alternativas candidatas.

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
| `evolutionary_v1` | Activo | Evolución determinista de una población declarada con semilla fija, mutación y crossover. Produce candidatos y estadísticas; no decide. |
| `llm_assisted_v1` | Definido, no configurado | Conserva el contrato mínimo para contexto, objetivos, constraints y cantidad de candidatos. Devuelve `LLM_NOT_CONFIGURED` hasta que exista un proveedor autorizado. |

### evolutionary_v1

El método requiere `base_alternatives` y `objectives`. Acepta `population_size` de 1 a 100, `generations` de 1 a 50, `mutation_rate` y `crossover_rate` entre 0 y 1. La semilla por defecto es fija y puede declararse explícitamente. La salida contiene `final_population`, `best_candidates`, `generation_log`, `convergence` y la semilla utilizada.

El orden estable de candidatos sirve para inspección reproducible. No representa una selección del arquitecto, no genera `Recommendation` y no crea `Decision`.

### llm_assisted_v1

El método acepta `context`, `objectives`, `constraints` y `num_candidates` de 1 a 10 como contrato de entrada. La implementación actual no invoca ningún modelo ni ejecuta comandos. Sin un proveedor configurado devuelve `LLM_NOT_CONFIGURED`. La integración real permanece sujeta a un contrato adicional, a procedencia de las afirmaciones y a confirmación humana.

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
6. `evolutionary_v1` es determinista con la misma semilla y solo propone candidatos.
7. `llm_assisted_v1` no ejecuta comandos ni afirma datos; sin proveedor devuelve `LLM_NOT_CONFIGURED`.
8. Las generaciones avanzadas no crean `Decision` ni `Recommendation`.

## Fuera de alcance

La integración real con LLM, la optimización multiobjetivo adicional, la decisión automática, la recomendación automática y los cambios en frontend o infraestructura permanecen fuera de alcance. RFC-016.1 solo implementa el contrato no configurado de `llm_assisted_v1` y el método determinista `evolutionary_v1`.
