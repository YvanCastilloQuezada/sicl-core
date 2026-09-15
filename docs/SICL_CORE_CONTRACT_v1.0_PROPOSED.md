# SICL Core Contract v1.0 — Proposed

**Línea:** `sicl-core-v1.0` independiente de SICL 0.6

**Estado:** `PROPOSED — REQUIRES FINAL HUMAN APPROVAL`

**Código:** No implementado.

## 1. Alcance contractual

Este contrato define una propuesta de núcleo CLI/Ontología. No modifica el contrato web/tRPC/HTTP de SICL 0.6. La implementación queda bloqueada hasta la revisión y aprobación del Product Owner.

El MVP operativo candidato es deliberadamente pequeño:

```text
/PROJECT CREATE
/PROJECT OPEN
/PROJECT SHOW
/PROJECT LIST
/STAGE SET
/OBJECTIVE SET
/CONSTRAINT SET
/ROLE ADD
/STATUS
/HISTORY
/HELP
/EXIT
```

Alternative, Evaluation, Comparison, Recommendation y Decision permanecen preservadas conceptualmente, pero su inclusión ejecutable en este MVP requiere decisión explícita.

## 2. Sintaxis

La forma canónica es:

```text
/COMMAND ENTITY [ARGUMENTS]
```

Ejemplos de forma, aún sujetos a cierre de gramática:

```text
/PROJECT CREATE <project_code> <name>
/PROJECT OPEN <project_code>
/PROJECT SHOW
/PROJECT LIST
/STAGE SET <stage>
/OBJECTIVE SET <key> <direction> <value>
/CONSTRAINT SET <key> <operator> <value> [unit]
/ROLE ADD <role>
/STATUS
/HISTORY
/HELP
/EXIT
```

`/PROJECT_SHOW` no es sintaxis canónica. Los argumentos con espacios, escape, quoting, mayúsculas/minúsculas y extensiones de versión requieren aprobación adicional.

## 3. Entidades y value objects candidatos

| Tipo | Identidad mínima | Estado |
|---|---|---|
| Project | `project_code`, `name`, `stage`, `version` | PROPUESTO |
| Stage | valor controlado | PROPUESTO |
| Objective | `key`, `direction`, `value/target`, `unit?` | PROPUESTO |
| Constraint | `key`, `operator`, `value`, `unit?`, `hardness?` | REQUIRES_HUMAN_DECISION |
| Role | `role_code`, `label` | PROPUESTO |
| Event | `event_id`, `project_id`, `timestamp`, `operation`, `command?`, `status`, `data` | REQUIRES_HUMAN_DECISION |
| State | snapshot actual del Project | PROPUESTO |
| History | vista ordenada de Event | PROPUESTO |
| Command | entrada textual original | PROPUESTO |
| Operation | intención semántica normalizada | PROPUESTO |
| Response | resultado observable | PROPUESTO |
| Error | código estable y detalle seguro | PROPUESTO |

## 4. Relaciones mínimas

```text
Project contains Stage, Objective, Constraint, Role
Operation changes Project State
Event records Operation
History orders Event
Response reports Operation result
```

Relaciones adicionales —`Requirement formalizes_as Objective/Constraint/Preference`, `Source provides Evidence`, `Alternative evaluated_by Evaluation`, `Decision responds_to Analysis`— quedan preservadas como ontología v1.0, pero no se activan automáticamente por el MVP CLI reducido.

## 5. Estados e invariantes

Estados candidatos de Project: `OPEN`, `CLOSED`. La máquina completa y si `STAGE` es estado o atributo requieren decisión.

Invariantes obligatorias propuestas:

1. Cada Project tiene identidad estable dentro de la línea v1.0.
2. No se crean dos proyectos con el mismo `project_code`.
3. No se modifica un Project inexistente.
4. Objective conserva dirección explícita; no existe dirección por defecto.
5. Constraint no se reduce silenciosamente a texto; `hardness` queda pendiente si se exige.
6. Queries no generan mutaciones ni eventos salvo decisión explícita.
7. Cada mutación aceptada genera un Event estructurado.
8. State y Event de una mutación se confirman atómicamente.
9. History no reemplaza Traceability.
10. Ninguna recomendación o evaluación futura crea automáticamente una Decision.
11. El núcleo no inventa Facts, Evidence, fuentes ni autoridad.
12. Los comandos desconocidos devuelven `UNKNOWN_COMMAND`.
13. Capacidades reconocidas pero fuera de alcance devuelven `FUTURE_NOT_IMPLEMENTED`.

## 6. Respuesta

```json
{
  "status": "OK | ERROR",
  "code": "STABLE_CODE",
  "message": "Human-readable explanation",
  "data": {}
}
```

Códigos candidatos:

```text
OK
INVALID_COMMAND
UNKNOWN_COMMAND
FUTURE_NOT_IMPLEMENTED
PROJECT_NOT_FOUND
PROJECT_ALREADY_EXISTS
INVALID_ARGUMENT
INVALID_STATE
PERSISTENCE_ERROR
TRANSACTION_ERROR
DECISION_REQUIRED
REQUIRES_HUMAN_DECISION
```

El conjunto final de códigos y sus envelopes requiere aprobación contractual.

## 7. Persistencia e historial

La propuesta utiliza un adaptador local sustituible. SQLite es una opción, no una definición ontológica. Una mutación sigue:

```text
parse → validate → prepare → persist State + Event → commit → Response
```

Si State o Event falla, la operación completa debe revertirse. El event log es append-only a nivel contractual; la política de corrección, borrado lógico y migración requiere decisión.

## 8. Compatibilidad y versionado

El contrato CLI se identifica como `sicl-core-v1.0`. No se reutilizan nombres ni endpoints del web 0.6 por compatibilidad implícita. Toda interoperabilidad futura requiere un adaptador explícito y una matriz de mapeo aprobada.

## 9. Decisiones bloqueantes

- ¿El MVP CLI incluye solo las operaciones enumeradas o también Context, Requirement, Alternative, Evaluation, Comparison, Recommendation y Decision?
- ¿`Constraint` tiene `hard/soft` en v1.0?
- ¿Cuál es el modelo final de Fact/Assumption y Source/Evidence?
- ¿Cuál es el Event mínimo y qué significa append-only?
- ¿`project_code` es suficiente o se requiere `project_id` técnico separado?
- ¿Qué significa exactamente Project DNA?
- ¿Cómo se modelan actor, Role y authority?
- ¿Cuál es la gramática completa de argumentos y errores?

**STOP:** No implementar código, CLI, SQLite, tests ni adaptadores hasta que este documento sea aprobado y las decisiones bloqueantes estén resueltas.
