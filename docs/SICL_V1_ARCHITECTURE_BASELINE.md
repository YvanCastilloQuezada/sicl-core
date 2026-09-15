# SICL v1.0 — Architecture Baseline

**Estado:** PROPUESTA — REQUIRES HUMAN REVIEW

## 1. Identidad

SICL v1.0 es un núcleo ontológico y una interfaz CLI para representar problemas espaciales, sus objetivos, restricciones, roles, operaciones, estado e historial, preservando la autoridad humana. No es un CRUD genérico ni un motor autónomo.

## 2. Fronteras

### Núcleo contractual candidato

`Project`, `Stage`, `Objective`, `Constraint`, `Role`, `Event`, `State`, `History`, `Response`, `Error`, `Command`, `Operation` e `Interpreter`.

### Ontología preservada, no necesariamente ejecutable en el MVP inicial

`Context`, `Requirement`, `Preference`, `Fact`, `Assumption`, `Source`, `Evidence`, `Alternative`, `Evaluation`, `Comparison`, `Conflict`, `Uncertainty`, `Recommendation` y `Decision`.

### Arquitectura futura

`Project DNA`, perfiles completos, motores de evaluación/feasibility/generative/site intelligence/optimization, agentes, GIS, BIM, Digital Twin, NLP, APIs externas y grafos semánticos persistentes.

## 3. Capas

```text
CLI / Interface
      ↓
Interpreter + Application
      ↓
Domain: entities, relations, invariants
      ↓
Ports: repository, history, transaction
      ↓
Adapters: SQLite/filesystem, only after approval
```

La CLI expresa comandos; no define por sí sola la ontología. El dominio no depende de SQLite, red, IA ni proveedores externos.

## 4. Flujo mutante

```text
Command → parse → validate → Operation → domain validation
→ atomic State + Event persistence → Response
```

Una mutación no puede confirmar estado nuevo sin el evento correspondiente. Las consultas no mutan el estado.

## 5. Autoridad

El núcleo puede representar y preparar análisis, pero no concede autoridad profesional a la CLI, a un motor ni a un agente. Toda futura Decision deberá identificar actor, rol, autoridad, base y justificación; la inclusión exacta queda pendiente.

## 6. Regla de evolución

No se crearán clases vacías para motores futuros ni se colapsarán conceptos distintos en un diccionario genérico. Toda nueva entidad debe tener identidad, semántica, relaciones, invariantes y pruebas aprobadas.

**No se implementa código en esta fase.**
