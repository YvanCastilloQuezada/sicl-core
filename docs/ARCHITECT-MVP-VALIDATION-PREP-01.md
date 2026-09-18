# ARCHITECT-MVP-VALIDATION-PREP-01

## Estado y alcance

Este documento prepara una **validación controlada con arquitectos** sobre el estado cerrado del Architect MVP de SiMS-DeI. No autoriza nuevas capacidades de producto y no sustituye una decisión del Product Owner.

El paquete se basa en el estado siguiente:

```text
ARCHITECT-MVP-CLOSURE-01 = CLOSED / PASS_WITH_OBSERVATIONS
GDI_P1_P8 = CLOSED / FROZEN BASELINE
ARCHITECT_MVP = READY_WITH_FRICTION
ARCHITECT_PRODUCT_COHERENCE = B
CONTROLLED_ARCHITECT_MVP_VALIDATION = READY_WITH_LIMITATIONS
```

Este paquete no descarga libros, no ingiere fuentes Alexander/CES, no activa `DESIGN-KNOWLEDGE-CORPUS-01`, no modifica el Core Contract y no realiza despliegues.

## A. Architect Validation Protocol

### Objetivo

La validación debe determinar si un arquitecto puede comprender, explorar, modificar, comparar, evaluar, revisar y decidir sobre un diseño sin conocer la arquitectura interna del software.

La prueba no busca demostrar que el sistema produce una solución arquitectónica correcta. Busca comprobar que el sistema ofrece una experiencia trazable de exploración de diseño, mantiene visible la autoridad humana y no presenta sugerencias, consenso o Pareto como decisiones.

### Participantes y condiciones

La sesión debe realizarse con arquitectos o diseñadores con experiencia suficiente para interpretar planos, masas y alternativas espaciales. Se recomienda una sesión individual por participante para evitar que una persona guíe a otra.

Cada sesión debe utilizar el proyecto sintético **UPAO-001** y una copia de trabajo separada. El facilitador debe observar sin intervenir salvo cuando exista un bloqueo técnico o una instrucción de seguridad.

La persona participante debe recibir únicamente una explicación breve del producto: SiMS-DeI permite explorar alternativas espaciales, conservar trazabilidad y mantener la decisión bajo autoridad humana. No debe recibir una explicación previa de P3, P6, P8, GDI, candidate normalization ni de la arquitectura interna.

### Tareas reales

| ID | Tarea | Resultado observable esperado |
|---|---|---|
| T1 | Abrir UPAO-001 y localizar el proyecto activo | Identifica el proyecto, la escala y el diseño visible |
| T2 | Expresar una intención | Escribe una intención sobre apertura del sitio, compacidad, privacidad o relación espacial |
| T3 | Revisar la interpretación | Distingue entre sugerencia del sistema y decisión propia |
| T4 | Adoptar la intención | Selecciona y confirma explícitamente los elementos que desea conservar |
| T5 | Explorar el espacio de diseño | Genera o inspecciona alternativas controladas sin asumir que existe una alternativa ganadora |
| T6 | Generar una síntesis espacial | Localiza programa, zonas, circulación y alternativas visuales |
| T7 | Comparar A/B/C | Distingue forma, vacío, masas, métricas y diferencias espaciales |
| T8 | Cambiar una dirección de diseño | Ejecuta una variación controlada y reconoce padre, hijo y cambio realizado |
| T9 | Solicitar perspectivas | Entiende las salidas multiagente como perspectivas sobre el diseño |
| T10 | Revisar memoria | Consulta qué ocurrió, qué cambió y qué acción humana se registró |
| T11 | Revisar una alternativa | Ejecuta o inspecciona Human Review sin confundirla con una recomendación automática |
| T12 | Decidir | Si la interfaz lo permite, registra una decisión humana explícita; si no, clasifica la capacidad como limitada |

### Criterios de aceptación

La sesión se considera satisfactoria cuando la persona puede completar el recorrido principal sin asistencia arquitectónica del facilitador y puede explicar con sus propias palabras:

1. qué proyecto está utilizando;
2. qué alternativa está viendo;
3. qué escala espacial está activa;
4. qué cambió entre dos alternativas;
5. por qué una alternativa existe;
6. quién produjo una perspectiva;
7. qué evidencia respalda una observación;
8. qué necesita confirmación humana;
9. por qué consenso no equivale a verdad;
10. por qué la decisión final no pertenece al sistema.

### Preguntas posteriores a cada tarea

Las preguntas deben ser abiertas y no sugerir la respuesta. Se recomienda preguntar:

- ¿Qué cree que acaba de ocurrir?
- ¿Qué parte fue una propuesta del sistema y qué parte fue una acción suya?
- ¿Qué diferencia observa entre estas dos alternativas?
- ¿Qué evidencia utilizaría para explicar este cambio a otra persona?
- ¿Puede identificar la alternativa de origen y la alternativa derivada?
- ¿Qué información le falta para confiar en esta exploración?
- ¿Qué esperaría que ocurriera al volver a la memoria del proyecto?
- ¿Qué considera decisión y qué considera solamente perspectiva?

### Evidencia a recoger

La evidencia debe ser suficiente para reconstruir el recorrido sin registrar información personal innecesaria. Debe incluir:

- identificador de sesión;
- proyecto y alternativa utilizados;
- tarea ejecutada;
- tiempo aproximado por tarea;
- éxito, bloqueo o abandono;
- capturas de las vistas 2D y 3D cuando la persona compare alternativas;
- identificadores de padre e hijo cuando exista una evolución;
- eventos relevantes del Event Log;
- observaciones verbales de la persona;
- errores de interfaz;
- preguntas que la persona no pudo responder;
- evidencia de Human Review y Decision cuando corresponda.

No deben recogerse contraseñas, tokens, datos personales no necesarios ni información de proyectos reales sin autorización independiente.

### Clasificación de resultados

Cada tarea debe clasificarse como:

```text
PASS
PASS_WITH_ASSISTANCE
PARTIAL
BLOCKED
NOT_APPLICABLE
```

Un resultado `BLOCKED` debe distinguir entre un problema del producto, un problema de datos de prueba, una falla de entorno o una instrucción ambigua.

## B. Demonstration Project Package — UPAO-001

### Identidad

```text
PROJECT_ID = UPAO-001
PROJECT_TYPE = MODEL PROJECT / EDUCATIONAL EXAMPLE
DATA_CLASSIFICATION = SYNTHETIC / DETERMINISTIC_DERIVED / EDUCATIONAL
```

UPAO-001 no representa un edificio real ni afirma desempeño constructivo, regulatorio, económico o energético real.

### Alternativas canónicas

```text
UPAO-001-A = COMPACT
UPAO-001-B = COURTYARD / VOID
UPAO-001-C = ARTICULATED / SEPARATED MASSES
```

La identidad de las alternativas debe conservarse durante la interpretación, síntesis, comparación, evolución, memoria y revisión.

### Objetivos educativos

```text
GROSS_MASSING_AREA = MAXIMIZE / m²
OPEN_SITE_AREA = MAXIMIZE / m²
OPEN_SITE_AREA = site_area - footprint_area
```

Estas métricas son descriptivas y sintéticas. No significan área útil, rentabilidad, área aprobada, calidad del espacio público ni desempeño ambiental real.

### Recorrido de demostración recomendado

El facilitador debe mostrar primero la forma espacial y después los datos. El orden recomendado es:

```text
Proyecto
→ Intención
→ Interpretación
→ Confirmación humana
→ Exploración
→ Síntesis espacial
→ Comparación A/B/C
→ Evolución de una rama
→ Perspectivas de diseño
→ Memoria
→ Human Review
→ Decision humana
```

La interfaz debe mostrar los detalles técnicos bajo demanda y no convertir el recorrido en una lectura de JSON o de identificadores internos.

## C. Architect Experience Checklist

| Área | Pregunta de verificación | Estado esperado |
|---|---|---|
| Proyecto | ¿El usuario identifica el proyecto activo? | PASS |
| Diseño | ¿La geometría domina la primera lectura? | PASS |
| Escala | ¿El usuario distingue escala de zoom? | PASS |
| Intención | ¿La sugerencia se distingue de la decisión? | PASS |
| Generación | ¿Se entiende qué se generó y desde qué padre? | PASS_WITH_OBSERVATIONS |
| Comparación | ¿A/B/C se distinguen visualmente? | PASS |
| Cambio | ¿Se entiende qué cambió? | PASS_WITH_OBSERVATIONS |
| Perspectivas | ¿Se entiende quién observa y con qué evidencia? | PASS |
| Memoria | ¿Se puede reconstruir la historia? | PASS_WITH_OBSERVATIONS |
| Revisión | ¿La revisión humana es explícita? | PASS |
| Decisión | ¿La decisión queda bajo autoridad humana? | PASS |
| Terminología | ¿La interfaz evita depender de P3/P6/P8? | PASS_WITH_OBSERVATIONS |
| Datos | ¿El JSON técnico está bajo demanda? | PASS |
| Retorno | ¿El usuario puede volver al diseño después de revisar datos? | PASS |

## D. Design Knowledge readiness

### Arquitectura existente

La arquitectura actual ya contiene los puntos de integración necesarios para una futura base de conocimiento de diseño:

```text
Human Intent
→ Design Knowledge Agent
→ Controlled Exploration
→ Spatial Synthesis
→ Evaluation / Trade-offs
→ Perspectives
→ Human Review
→ Decision
```

La familia de conocimiento todavía no es la teoría del producto. El sistema debe conservar pluralismo, atribución de fuentes y separación entre conocimiento, evidencia, sugerencia y decisión.

### Puntos P3/P6/P8

| Punto | Uso actual | Estado para Design Knowledge |
|---|---|---|
| P3 Spatial Synthesis | Programa, espacios, relaciones, circulación y forma conceptual | Punto de aplicación espacial |
| P6 Advanced Evolution | Mutación, herencia, distancia, búsqueda y ramas | Punto de exploración controlada |
| P8 Multi-Agent Design | Perspectivas, crítica, debate y estrategias | Punto de interpretación plural |

Estos puntos deben recibir conocimiento trazable sin crear un segundo motor generativo, un segundo modelo de alternativas o una segunda memoria.

### Límite de esta preparación

```text
BOOK_INGESTION = NOT PERFORMED
SOURCE_DOWNLOAD = NOT PERFORMED
ALEXANDER/CES_CORPUS = FROZEN
```

No se han ingerido libros, no se han extraído patrones y no se han transformado ideas de Alexander/CES en requisitos, reglas obligatorias o decisiones automáticas.

## E. Alexander/CES Source Inventory Plan

Este inventario es únicamente un plan de preparación. No autoriza descarga, extracción ni implementación.

### Familia prioritaria

| Fuente | Papel futuro | Estado |
|---|---|---|
| *The Timeless Way of Building* | Teoría y fundamento generativo | Registrada / no ingerida |
| *A Pattern Language* | Patrones y relaciones de patrones | Registrada / no ingerida |
| *The Oregon Experiment* | Proceso participativo e implementación | Registrada / no ingerida |
| PREVI — Lima | Caso de estudio trazable | Candidata / no ingerida |
| *Houses Generated by Patterns* | Fuente candidata asociada a PREVI | Candidata / no ingerida |
| *The Nature of Order* | Familia futura posterior | Congelada / fuera del primer piloto |

### Plan de revisión futura

La activación futura debería seguir este orden:

1. verificar identidad bibliográfica, edición, procedencia y derechos;
2. registrar la fuente y su estado de verificación;
3. definir qué dimensiones de conocimiento se buscan;
4. separar teoría, principio, patrón, relación, proceso, evidencia y caso;
5. registrar citas y provenance antes de cualquier uso exploratorio;
6. probar una cadena pequeña y conectada;
7. comparar la influencia Alexander/CES con otras tradiciones;
8. someter los resultados a revisión humana.

### Cadena conceptual prevista

```text
THEORY
→ PATTERN
→ RELATIONSHIP
→ IMPLEMENTATION PROCESS
→ PROJECT CONTEXT
→ HUMAN INTENT
→ DESIGN EXPLORATION
→ VISIBLE ALTERNATIVE
```

La cadena no debe convertir a Alexander/CES en doctrina ni en autoridad automática.

## F. Next Product Roadmap

### 1. MVP validation

**Estado:** preparado para activación controlada.

El siguiente paso recomendado es ejecutar sesiones con arquitectos utilizando UPAO-001, registrar evidencia y clasificar fricciones reales. No se debe ampliar el producto antes de observar el uso real.

### 2. Design Knowledge

**Estado:** preparado arquitectónicamente, congelado operativamente.

La futura activación debe comenzar con la estructura de fuentes, provenance y una cadena de conocimiento pequeña. La trilogía Alexander/CES es prioritaria, pero todavía no está autorizada su descarga o ingestión.

### 3. Regulatory Intelligence

**Estado:** futuro y congelado.

Requiere corpus normativo verificable, jurisdicción, aplicabilidad, extracción de requisitos, evidencia y revisión humana. No debe mezclarse automáticamente con patrones teóricos.

### 4. Simulation

**Estado:** profundidad selectiva futura.

Las métricas actuales de UPAO-001 son sintéticas y educativas. Comfort, daylight, energy, hydrology, CFD, carbon y resilience requieren inputs, modelos y validación propios. No deben presentarse como disponibles por el solo hecho de existir métricas espaciales.

### 5. GIS/BIM

**Estado:** interoperabilidad parcial y futura expansión.

El sistema ya cuenta con fundamentos visuales y espaciales reutilizables. La expansión debe adaptarse a la escala, los datos disponibles y la semántica de cada representación. BIM no debe fabricarse a partir de una masa conceptual.

### 6. Infrastructure

**Estado:** diferida.

Deployment, Core remoto, tokens, observabilidad, E2E remoto, persistencia de reinicio y hardening quedan fuera de esta preparación.

## Decisiones de no activación

Este paquete no activa:

- `DESIGN-KNOWLEDGE-CORPUS-01`;
- `DESIGN-KNOWLEDGE-CORPUS-01-A`;
- descarga o extracción de libros;
- ingesta Alexander/CES;
- PREVI como fuente operativa;
- Regulatory Intelligence;
- Simulation avanzada;
- GIS avanzado;
- BIM authoring;
- Railway;
- deployment;
- nuevas entidades canónicas;
- nuevas dependencias.

## Estado final del paquete

```text
ARCHITECT-MVP-VALIDATION-PREP-01 = READY
UPAO-001_DEMONSTRATION_PACKAGE = READY
ARCHITECT_EXPERIENCE_CHECKLIST = READY
DESIGN_KNOWLEDGE_READINESS = READY_WITHOUT_INGESTION
ALEXANDER_CES_SOURCE_INVENTORY = PLAN_ONLY
NEXT_PRODUCT_ROADMAP = DOCUMENTED / NOT ACTIVATED
```

## References

[1]: https://github.com/YvanCastilloQuezada/milukita "SiMS-DeI project repository selected for project integration"

Internal source documents used for this preparation include `docs/RFC-026_DESIGN_KNOWLEDGE_AND_MULTISCALE_DESIGN_GRAMMAR.md`, `docs/SIMS_DEI_CURRENT_ARCHITECTURE_v2.11.md`, the frozen future-orders register, and the closed Architect MVP validation evidence.


## Operational completion for controlled validation

The following operational definition completes the compact T1–T12 sequence above and adds the missing T9–T15 tasks. It is the authoritative execution detail for the future participant session. It uses architect-facing language and does not expose internal implementation labels.

| TASK_ID | ARCHITECT-FACING INSTRUCTION | PURPOSE | EXPECTED OBSERVABLE BEHAVIOR | EVIDENCE TO CAPTURE | FACILITATOR INTERVENTION RULE | PASS / PARTIAL / FAIL |
|---|---|---|---|---|---|---|
| T1 | Open UPAO-001 and identify the project, active design and spatial scope. | Establish orientation. | Participant names the project and points to the active design and scope. | Screen evidence and participant wording. | None unless technically blocked. | Pass if all three are identified; partial if one requires help; fail if orientation is not recovered. |
| T2 | Describe a design intention in your own words. | Test natural design entry. | Participant states a spatial goal or preference without being given a command. | Exact participant text and timestamp. | Do not suggest vocabulary. | Pass if an intention is expressed; partial if facilitator must reformulate it; fail if the task cannot start. |
| T3 | Review the system interpretation and explain what it is suggesting. | Test interpretability. | Participant distinguishes suggested structure from personal intent. | Selected suggestions and verbal explanation. | Ask what they think it means; do not explain the answer. | Pass if the distinction is understood; partial if corrected once; fail if suggestion is treated as an automatic decision. |
| T4 | Select what you want to keep and confirm it. | Test human adoption. | Participant selects intent items and performs explicit confirmation. | Confirmation event and selected IDs. | Do not choose items for the participant. | Pass if confirmation is intentional; partial if navigation help is needed; fail if adoption is mistaken for automatic acceptance. |
| T5 | Explore the available alternatives and describe one difference. | Test controlled exploration. | Participant opens alternatives and identifies a meaningful variation. | Selected alternatives, screen evidence and statement. | Do not name the difference first. | Pass if a visual difference is identified; partial if raw data is required; fail if alternatives cannot be distinguished. |
| T6 | Generate or inspect the spatial synthesis. | Test program-to-space comprehension. | Participant identifies spaces, zones, circulation and the synthetic nature of the layout. | Screen evidence and comprehension note. | Explain only after technical blockage. | Pass if the spatial result is understood; partial if the participant sees only metrics; fail if the synthesis is inaccessible. |
| T7 | Compare alternatives A, B and C. | Test visual comparison. | Participant describes compact massing, courtyard/void and separated masses. | A/B/C selection sequence and comparison statement. | Do not tell the participant which alternative has which strategy. | Pass if all three are distinguished; partial if two are distinguished; fail if comparison is not possible. |
| T8 | Change one design direction and inspect the resulting child. | Test reversible evolution. | Participant identifies the parent, the changed direction and the resulting child. | Parent/child IDs, changed direction and screen evidence. | Do not explain lineage unless technically blocked. | Pass if the change is understood; partial if the child is found only with help; fail if origin or change is lost. |
| T9 | Navigate from the current scale to another relevant spatial scale and return. | Test scale comprehension. | Participant changes scope and understands that scale is not merely camera zoom. | Scope before/after, navigation path and statement. | Do not provide the destination unless navigation is technically blocked. | Pass if the semantic scope change is understood; partial if the participant confuses it with zoom; fail if return is impossible. |
| T10 | Ask for design perspectives on the visible alternative. | Test source-separated professional viewpoints. | Participant identifies perspectives as observations or readings, not decisions. | Perspective result and participant interpretation. | Do not translate agent terminology unless blocked. | Pass if perspective is distinguished from decision; partial if one correction is needed; fail if the system is believed to decide. |
| T11 | Use Challenge or explore an agent-supported direction. | Test disagreement and challenge comprehension. | Participant inspects a challenge, disagreement or strategy and decides whether it is useful. | Challenge result, selected action and reasoning. | Observe first; do not recommend a strategy. | Pass if challenge is treated as input to review; partial if the participant needs clarification; fail if challenge is treated as an instruction. |
| T12 | Inspect Design Memory and reconstruct how the current design was reached. | Test traceability. | Participant finds history, lineage or a replay/explanation action. | History view, selected branch and verbal reconstruction. | Do not narrate the history before the participant attempts it. | Pass if origin is reconstructed; partial if only current state is found; fail if history is inaccessible. |
| T13 | Compare the parent and child before and after the change. | Test evolution comprehension. | Participant explains what was preserved and what changed. | Before/after selections, comparison evidence and statement. | Do not point out the changed parameter first. | Pass if preservation and change are both identified; partial if only one is identified; fail if the relationship is unclear. |
| T14 | Perform Human Review on the alternative. | Test review authority. | Participant records or prepares a review without assuming approval is automatic. | Review action, actor and resulting status. | Explain only a technical submission constraint. | Pass if review is understood as a human act; partial if review and recommendation are conflated; fail if review is attributed to the system. |
| T15 | Perform an explicit Human Decision where the current product supports it. | Test decision authority and final boundary. | Participant can state whether to accept, reject or defer and understands that the system did not decide. | Decision payload/status, actor and participant wording. | Do not suggest the decision. | Pass if human authority is explicit; partial if the participant can decide but cannot explain the boundary; fail if system output is treated as the decision. |

## Participant brief

SiMS-DeI is a design-intelligence system for exploring spatial alternatives, comparing them and preserving the reasoning around a project. Today you will use a synthetic educational project called UPAO-001. There is no expected correct design. We are evaluating the product experience, not your architectural judgment. System suggestions and perspectives are not decisions. You remain the design authority, and your comments about the experience are more important than completing every task.

## Facilitator guide

The facilitator must observe first. The participant should attempt each task without a tutorial. Intervene only when a technical block prevents continuation, when consent or safety requires intervention, or when the session would otherwise stop. Every intervention must be recorded with one of these classifications: `NONE`, `MINOR_PROMPT`, `NAVIGATION_HELP`, `TECHNICAL_RECOVERY`, or `TASK_EXPLANATION`.

A task that requires substantial explanation must not be reported as an unqualified pass. The facilitator must record the exact wording used, the task affected and whether the participant could continue independently afterward. The facilitator must not interpret participant intent during the session; interpretation belongs in the post-session analysis.

## Think-aloud prompts

Use short prompts at natural pauses rather than continuously interrupting. Suitable prompts include: “What do you think you are seeing?”, “What do you expect this control to do?”, “Why did you choose that alternative?”, “What changed?”, “Who made that decision?”, and “What would you look for next?”. Record participant wording as evidence, not as a system conclusion.

## Participant record template

```yaml
participant_id: ARCH-___
professional_role: ""
experience_band: ""
bim_cad_familiarity: ""
generative_design_familiarity: ""
session_date: ""
session_duration_minutes: null
consent_recorded: false
tasks: []
facilitator_interventions: []
observed_friction: []
participant_comments: []
unexpected_behavior: []
critical_incident: null
overall_comprehension: ""
```

Do not collect names, contact information, credentials, health information or other personal data unless a separate approved protocol requires it.

## Evidence model and result schema

Evidence must preserve the distinction between observation and interpretation. The following classes are available: `OBSERVED_ACTION`, `PARTICIPANT_STATEMENT`, `TASK_RESULT`, `FACILITATOR_INTERVENTION`, `SCREEN_EVIDENCE`, `TECHNICAL_EVENT`, `PRODUCT_DEFECT`, `UX_FRICTION`, `DESIGN_COMPREHENSION`, and `AUTHORITY_COMPREHENSION`.

Each task uses one of: `PASS`, `PARTIAL`, `FAIL`, `BLOCKED_TECHNICAL`, or `NOT_ATTEMPTED`. Friction severity uses `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`. Issue type uses `BLOCKING_DEFECT`, `MVP_FRICTION`, `LEARNABILITY_FRICTION`, `VISUAL_COMPREHENSION_FRICTION`, `TERMINOLOGY_FRICTION`, `NAVIGATION_FRICTION`, `ACCEPTABLE_MVP_LIMITATION`, or `FUTURE_CAPABILITY_REQUEST`.

A participant statement is not automatically a fact. A facilitator inference is not a participant statement. A technical event can corroborate an action but cannot replace the participant’s understanding of that action.

## Session metrics

Collect only metrics that answer a product question:

- `TASK_COMPLETION`;
- `TIME_TO_FIRST_MEANINGFUL_ACTION`;
- `FACILITATOR_INTERVENTIONS`;
- `NAVIGATION_ERRORS`;
- `REVERSALS_BACKTRACKS`;
- `MISINTERPRETATIONS`;
- `VISIBLE_DESIGN_REFERENCES`;
- `RAW_DATA_DEPENDENCE`;
- `COMPARISON_SUCCESS`;
- `AUTHORITY_COMPREHENSION`.

Do not convert these measures into a fabricated overall score. Qualitative statements such as “I understand what changed,” “Where is the design?” and “Did the system choose this?” should be preserved verbatim where possible.

## Architect experience scorecard

Use the following observational scale for each dimension: `CLEAR`, `CLEAR_WITH_MINOR_FRICTION`, `UNCLEAR_WITH_RECOVERY`, `UNCLEAR`, or `NOT_OBSERVED`.

```text
PROJECT_ORIENTATION
DESIGN_VISIBILITY
SPATIAL_COMPREHENSION
2D_3D_COMPREHENSION
DESIGN_MODIFICATION
ALTERNATIVE_IDENTITY
PARENT_CHILD_COMPREHENSION
COMPARISON
TRADE_OFF_COMPREHENSION
MULTISCALE_NAVIGATION
DESIGN_PERSPECTIVES
DESIGN_MEMORY
TRACEABILITY
DATA_ON_DEMAND
HUMAN_AUTHORITY
OVERALL_PRODUCT_COHERENCE
```

## Post-session interview

1. What did you understand SiMS-DeI was helping you do?
2. When did you feel you were working with a design rather than with software controls?
3. Which part was easiest to understand visually?
4. Which part was hardest to understand?
5. Were the differences between alternatives clear?
6. Could you understand why an alternative existed?
7. How did you interpret the Design Perspectives?
8. Did you ever think the system had made a design decision for you?
9. What information did you need but could not find?
10. What information was shown that you did not need?
11. Would you use this during conceptual or early design?
12. What would need to improve before using it on a real project?

## Reproducible UPAO-001 session package

```text
CORE_HEAD = 6dd35d343b2450d4774eea7677b1513a0c2cce3a
WEB_HEAD = 14c8b2980e43af5975a270871ccd757a5f27d9ed
PROJECT_ID = UPAO-001
PROJECT_TYPE = MODEL PROJECT / EDUCATIONAL EXAMPLE
DATABASE = EXISTING LOCAL/TEST UPAO-001 SOURCE USED BY THE VALIDATION ENVIRONMENT
AUTHENTICATION = EXISTING LOCAL AUTHENTICATED SESSION OR APPROVED TEST SESSION
STARTING_WORKSPACE = UPAO-001 PROJECT WORKSPACE / PROJECT MODULE
```

The facilitator must record the actual database path or approved source used for the session, the authentication method, the starting URL and the reset action. Production must not be modified. Metrics, geometry and objectives remain synthetic; agent perspectives are not decisions; some children may remain transient; multiscale visual continuity remains partial.

### Reset strategy

Each participant must receive a clean working copy or a disposable local/test state created through an existing safe mechanism. Before a session, verify that UPAO-001, its canonical A/B/C alternatives and its synthetic spatial representations are available. After a session, discard the working copy or restore the approved test fixture. Do not introduce a new persistence architecture and do not reuse another participant’s events.

## Result matrices

### Participant matrix

| Task | ARCH-001 | ARCH-002 | ARCH-003 | ARCH-004 | ARCH-005 | Observations |
|---|---|---|---|---|---|---|
| T1–T15 |  |  |  |  |  |  |

No participant result is populated by this document.

### Issue consolidation

| ISSUE_ID | OBSERVED_BY | TASK | EVIDENCE | FREQUENCY | SEVERITY | TYPE | PRODUCT_SURFACE | POSSIBLE_CAUSE | REQUIRES_PRODUCT_CHANGE | REQUIRES_ARCHITECTURE_CHANGE | RECOMMENDED_NEXT_ACTION |
|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |  |

### Future product gate

```text
ARCHITECT_USER_VALIDATION = NOT_ASSIGNED
ARCHITECT_MVP_AFTER_USER_VALIDATION = NOT_ASSIGNED
```

These classifications must be assigned only after real architect sessions. No automated test, internal review or agent run counts as participant evidence.

## Design Knowledge readiness map

The existing architecture provides reusable concepts in `src/sicl/design_knowledge.py`, including `DesignKnowledgeSource`, `DesignKnowledgeItem`, `DesignPattern`, `DesignKnowledgeQuery`, `DesignKnowledgeResponse` and `DesignKnowledgeAgent`. The existing HTTP surface exposes catalog and query behavior in `api/routes/v1.py`. These are readiness points, not authorization to ingest new material.

Future integration should reuse the existing flow:

```text
Human Intent
→ Knowledge Match
→ Architect Inspection
→ Possible Spatial Synthesis Direction
```

```text
Current Design
→ Knowledge Match
→ Possible Evolution Direction
→ Human Confirmation
→ Existing Design Evolution
```

```text
Visible Design
→ Source-Grounded Knowledge
→ Agent Interpretation
→ Critique / Challenge
→ Human Confirmation
→ Existing Design Evolution
```

The following invariants remain binding:

```text
KNOWLEDGE MATCH ≠ DECISION
SOURCE ≠ AGENT
AUTHOR ≠ AGENT
AGENT INTERPRETATION ≠ SOURCE CLAIM
```

No schema, endpoint, UI, ingestion pipeline, embedding, vector database, source download or corpus record was added by this preparation.

## Alexander/CES inventory readiness

The Alexander/CES family remains registered and frozen. The plan contains the following future entries without downloading or extracting sources:

```text
FOUNDATIONAL KNOWLEDGE FAMILY #1
- The Timeless Way of Building — theory / generative foundation
- A Pattern Language — pattern / design knowledge
- The Oregon Experiment — implementation / participatory process
- PREVI — Lima — case candidate
- Houses Generated by Patterns — associated source candidate
- The Nature of Order, Books 1–4 — future family
```

Future inventory fields include source identity, title, authors, edition, publication data, source type, official reference, provenance, rights status, rights evidence, allowed processing status, OCR status, page reliability, knowledge categories, applicable spatial scopes, related sources, case-study relationship, review status and notes.

```text
SOURCE_DOWNLOADS = 0
SOURCE_EXTRACTIONS = 0
CORPUS_RECORDS_CREATED = 0
```

The following invariants are preserved: tribute is not doctrine; influence is not authority; pattern is not requirement; Alexander is not SiMS-DeI theory; a public URL is not public domain; and source availability is not a license to ingest.


## References

[1]: https://github.com/YvanCastilloQuezada/milukita "SiMS-DeI project repository selected for project integration"

Internal source documents used for this preparation include `docs/RFC-026_DESIGN_KNOWLEDGE_AND_MULTISCALE_DESIGN_GRAMMAR.md`, `docs/SIMS_DEI_CURRENT_ARCHITECTURE_v2.11.md`, the frozen future-orders register and the closed Architect MVP validation evidence.
