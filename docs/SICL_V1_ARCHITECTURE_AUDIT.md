# SICL v1.0 — Auditoría de la Visión

**Línea:** `sicl-core-v1.0` (aislada de SICL 0.6)

**Estado:** DOCUMENTAL — NO IMPLEMENTADO

**Fuentes revisadas:** Engineering Reset & Controlled Implementation, SICL Frontend Specification v1.0, Core Contract v1.0 — Final Proposed, Semantic Consolidation + Core Contract v1.0, Architecture Consolidation Review v2 e Implementation Specification v1.0.

## Regla de aislamiento

Esta auditoría no audita ni modifica SICL 0.6, `sicl-web`, su frontend, su contrato tRPC/HTTP ni su checkpoint operativo. Las referencias a versiones históricas se usan únicamente para detectar procedencia y conflictos de la visión v1.0.

## Clasificación

| Elemento de la visión v1.0 | Clasificación | Observación |
|---|---|---|
| SICL como lenguaje declarativo de decisión espacial | VIGENTE | Identidad conceptual de esta línea. |
| Ontology First | VIGENTE | Principio rector, pendiente de contrato aprobado. |
| Arquitectura → Auditoría → Contrato → Código → Pruebas → Evidencia | VIGENTE | Gobernanza de desarrollo. |
| Autoridad humana final | VIGENTE | Invariante no negociable. |
| Project como raíz operativa | PROPUESTA VIGENTE | Requiere aprobación contractual. |
| Objective con dirección | PROPUESTA VIGENTE | `MAXIMIZE`/`MINIMIZE` requieren contrato cerrado. |
| Constraint con operador, valor y unidad | PROPUESTA VIGENTE | Hard/Soft y semántica avanzada requieren decisión. |
| Role como identificador de función | PROPUESTA VIGENTE | Actor, autoridad y responsabilidad no están cerrados. |
| Event estructurado | PROPUESTA VIGENTE | Atributos finales requieren decisión humana. |
| State separado de Event | VIGENTE | Distinción arquitectónica necesaria. |
| History como vista consultable | VIGENTE | No equivale a trazabilidad completa. |
| Traceability como red semántica futura | FUTURO | No debe simularse con un campo genérico. |
| Requirement independiente/formalizable | PENDIENTE | Afecta la ontología y compatibilidad futura. |
| Fact / Assumption | PENDIENTE | La visión los distingue, pero su contrato v1.0 no está aprobado. |
| Source / Evidence | PENDIENTE | La separación es recomendada, no congelada. |
| Alternative / Evaluation / Comparison | PENDIENTE | Forman parte de la visión, pero no del MVP CLI mínimo declarado. |
| Recommendation separada de Decision | VIGENTE | Invariante conceptual. |
| Decision humana explícita | VIGENTE | No se permite decisión automática. |
| Preference | PENDIENTE | Su posición respecto del MVP CLI debe decidirse. |
| Project DNA | INDETERMINADO | El concepto aparece en la instrucción, sin atributos ni límites definidos. |
| Evaluation Engine | FUTURO | Capacidad posterior; el MVP CLI no debe implementarlo implícitamente. |
| Feasibility Engine | FUTURO | Requiere contrato matemático y datos definidos. |
| Generative Engine | FUTURO | Fuera del MVP. |
| Site Intelligence | FUTURO | Fuera del MVP; no APIs externas. |
| Optimization / Pareto | FUTURO | Fuera del MVP. |
| Agents | FUTURO | No se implementan. |
| Clima, GIS, BIM, Digital Twin, NLP y APIs externas | FUTURO | Prohibidos en esta fase. |
| CLI `/COMANDO ENTIDAD` | PROPUESTA | La forma está fijada; semántica exacta pendiente. |
| `/PROJECT CREATE`, `/OPEN`, `/SHOW`, `/LIST` | PROPUESTA | MVP de interfaz, pendiente de contrato final. |
| `/STAGE SET`, `/OBJECTIVE SET`, `/CONSTRAINT SET`, `/ROLE ADD` | PROPUESTA | Mutaciones del MVP, pendientes de detalle. |
| `/STATUS`, `/HISTORY`, `/HELP`, `/EXIT` | PROPUESTA | Consultas/control de sesión. |
| SQLite inicial | PROPUESTA | Reversible, pero requiere decisión de persistencia. |
| State + Event atómicos | PROPUESTA VIGENTE | Recomendación fuerte; falta aprobación contractual v1.0. |
| Vertical slice UPAO-001 | PROPUESTA | No debe confundirse con el E2E web 0.6. |
| Certificado final UX | FUTURO | No pertenece al contrato CLI mínimo. |

## Contradicciones o riesgos de la visión

1. La numeración mezcla `Core Contract v1.0`, `Core 0.x` y referencias históricas 0.2.1. En esta línea se conserva la denominación **SICL Core v1.0** y el MVP se considera una primera implementación futura, no una modificación de 0.6.
2. El documento de Engineering Reset exige un MVP CLI reducido, mientras que los documentos semánticos incluyen Alternative, Evaluation, Conflict, Uncertainty, Recommendation y Decision. La frontera exacta requiere decisión.
3. `Fact`, `Assumption`, `Evidence`, `Source`, `Requirement`, `Preference` y `Project DNA` aparecen con importancia ontológica desigual y sin una tabla única de obligatoriedad.
4. `Role`, actor y authority se distinguen conceptualmente, pero no tienen un contrato de identidad y autorización cerrado.
5. La especificación UX/UI declara “aprobado para implementación”, pero esta Ruta C la trata como visión futura aislada; no autoriza cambios en 0.6 ni código v1.0 en esta fase.
6. La sintaxis `/COMANDO ENTIDAD` está fijada como forma, pero los argumentos, quoting, errores, versionado y compatibilidad no están completamente definidos.

## Elementos que requieren decisión humana

- Alcance semántico exacto del MVP CLI frente al MVP ampliado.
- Formalización de Requirement.
- Atributos y atomicidad de Event.
- Separación contractual Source/Evidence.
- Estatus de Fact/Assumption en el primer contrato ejecutable.
- Inclusión o postergación de Alternative/Evaluation/Comparison/Recommendation/Decision.
- Significado y alcance de Project DNA.
- Identidad de actor, Role y authority.
- Sintaxis completa y política de compatibilidad CLI.
- SQLite y persistencia inicial.

**Conclusión:** la visión v1.0 es suficientemente coherente para redactar un contrato propuesto, pero no para implementar código. El contrato siguiente es una propuesta congelable para revisión, no una aprobación implícita.
