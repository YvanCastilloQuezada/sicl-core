# SiMS-DeI — Master Handoff 01

**Fecha:** 18 de septiembre de 2026  
**Autor:** Manus AI  
**Autoridad:** Product Owner / Human Authority  
**Estado:** `AUTHORIZED / ACTIVE`  
**Alcance de esta entrega:** reconciliación, documentación y consolidación. No activa ARQUI P1 ni ninguna capacidad futura congelada.

## 1. Estado actual verificado

SiMS-DeI es el **Sistema de Inteligencia de Diseño Espacial Multiescala**. SICL es su lenguaje formal para representar, razonar y comunicar información espacial y de diseño. SiMS-DeI y SICL no son el mismo concepto: SICL está contenido dentro de SiMS-DeI.

El flujo vigente integra captura de campo, evidencia espacial, inteligencia visual acotada, revisión humana, estado de proyecto, inteligencia de diseño, alternativas, registro espacial y visualización AR contextual. La implementación debe entenderse como una cadena de capacidades canónicas, no como una colección de asistentes independientes.

### Repositorios y HEAD verificados

| Repositorio | Rama local verificada | HEAD actual | Estado de trabajo |
|---|---|---|---|
| `YvanCastilloQuezada/sicl-core` | `feat/weather-environmental-context-p1` | `ec0993974fccdac8fcb167a360474f5f963a1bfc` | limpio |
| `YvanCastilloQuezada/sicl-web` | `feat/spatial-pilot-media-studio-v1` | `b58dabc123103a0c7b67eb2e94174de43adf8b70` | limpio |

Los HEAD anteriores son los estados actuales de los worktrees auditados; no deben confundirse con los commits de cierre de cada capacidad.

## 2. Jerarquía de verdad

Cuando exista conflicto, se aplica este orden:

1. Código y commits actuales verificados.
2. Contratos canónicos y Decision Locks vigentes.
3. Evidencia de cierre de capacidades congeladas.
4. Arquitectura documentada más reciente.
5. Este handoff.
6. Informes históricos.
7. Conversación y planes antiguos.

La presencia de una documentación histórica no prueba que su rama siga siendo el HEAD actual. Un commit de capacidad tampoco equivale necesariamente al HEAD de una rama posterior.

## 3. Identidad, autoridad y epistemología

La identidad visible y canónica es:

> **SiMS-DeI**  
> Sistema de Inteligencia de Diseño Espacial Multiescala

La autoridad final permanece en el Product Owner y en la autoridad humana del proyecto. Ningún agente puede aprobar, rechazar, seleccionar un ganador, convertir una recomendación en decisión o crear una preferencia humana de forma silenciosa.

Se mantienen estas invariantes:

```text
NO EVIDENCE → NO FACT
NO APPLICABLE RULE → NO COMPLIANCE CLAIM
NO COMPUTATION → NO COMPUTED RESULT
NO OBSERVATION → NO OBSERVED RESULT
INTERPRETATION → REMAINS INTERPRETATION
HYPOTHESIS → REMAINS PROVISIONAL
UNKNOWN → VALID RESULT
UNCERTAINTY → PRESERVED
CONTRADICTION → NOT SILENTLY RESOLVED
DECISION → HUMAN AUTHORITY
```

En particular, `AI_PROPOSED` no es un hecho confirmado; `HumanReview` no es `Decision`; `Recommendation` no es `Decision`; Pareto no es “el mejor”; y AR no es verificación topográfica o de obra construida.

## 4. Arquitectura vigente resumida

La arquitectura combina un **Core determinista FastAPI/Python**, SQLite/Event Log y un **Web React/TypeScript** con Guided Shell, Project Workspace, cliente REST y puente server-side. Las fuentes, evidencias, observaciones, decisiones, ubicaciones, registros espaciales, representaciones, alternativas y media permanecen en sus modelos canónicos.

La política operacional es:

```text
PASSIVE FIRST
→ REUSE
→ TARGETED VERIFY
→ EXECUTE
→ PASS
→ CONTINUE
→ CONSOLIDATED VALIDATION
→ ONE REPORT
```

No se crea una entidad, API, motor, renderer, almacén o sistema paralelo si la semántica canónica existente es suficiente.

## 5. Matriz de capacidades congeladas

| capability_id | status | repository | capability commit | evidence level | observations | reexecution_required | dependencies | next_allowed_action |
|---|---|---|---|---|---|---|---|---|
| `FIELD-CAPTURE-01` | `CLOSED / FROZEN` | Web | `50cfe70` | L3 | Captura responsive con foto, observación, escala y punto opcional | No, salvo cambio de superficie | Evidence, media, project state | Reutilizar o extender solo con orden específica |
| `MEDIA-EVIDENCE-PERSISTENCE-01` | `CLOSED / PASS_WITH_OBSERVATIONS / FROZEN` | Core + Web | Core `71ce972`; Web `d7fe748` | L3 | Media persistida y recuperable por evidencia canónica | No, salvo cambio de almacenamiento | SQLite/Event Log, media storage | Reutilizar; no crear segundo almacén |
| `DIRECT-SPATIAL-INTERACTION-01` | `CLOSED / FROZEN` | Web | `320ebce` | L3 | Operaciones directas sobre el flujo espacial existente | No | SpatialOperations, GDI | Reutilizar |
| `SPATIAL-REGISTRATION-01` | `CLOSED / PASS_WITH_OBSERVATIONS / FROZEN` | Core | `8b36db8586428704de5acdcf3f30ad4a8de0d1ea` | L3 | Registro `MANUAL_TWO_POINT` persistido vía Event Log | No, salvo cambio de método | SpatialLocation, Project, HumanReview | Reutilizar; no redefinir control points |
| `GEOREFERENCED-DESIGN-AR-01` | `CLOSED / PASS_WITH_OBSERVATIONS / FROZEN` | Web | `49ead517cab162439e285d586cbdb4c5aefaf626` | L3 | AR contextual con fallback y limitaciones explícitas | No, salvo cambio del renderer o registro | SpatialRegistration, SpatialRepresentation | Reutilizar como view mode |
| `VISUAL-FIELD-INTELLIGENCE-P1` | `CLOSED / PASS_WITH_OBSERVATIONS / FROZEN` | Core + Web | Core `fdbc51d`; Web `b58dabc` | L3 | Foto → análisis server-side → `AI_PROPOSED` → HumanReview | No, salvo provider, contrato o privacidad nuevos | Field Capture, media, Evidence, HumanReview, server LLM | Reutilizar; runtime L4 requiere entorno autenticado |
| `RFC-022 Guided Interface` | `IMPLEMENTED / ACTIVE` | Web | main contiene `GuidedShell.tsx` y RFC | L3 | Guided Mode inicial, Expert Mode configurable, catálogos, tour, i18n y Command Bar | No para clasificar existencia | Project Workspace, i18n, Core proxy | Componer con capacidades existentes |
| `RFC-026 Design Knowledge Agent` | `IMPLEMENTED / ACTIVE` | Core | main contiene `design_knowledge.py` y RFC | L3 | Catálogo, consulta multiescala, Alexander/Ching/RNE y endpoints HTTP | No para clasificar existencia | Design Intelligence, SpatialScope, evidence/provenance | Reutilizar; ampliar corpus solo con autorización |
| `ARQUI P1` | `FROZEN / NOT AUTHORIZED` | — | UNKNOWN | L0 | Dirección de producto, no implementación | No ejecutar | Requiere orden futura | Esperar autorización específica |

**L3** significa implementación y pruebas locales verificadas. No equivale a validación remota, de sitio real o de dispositivo físico. El runtime multimodal real de VFI queda expresamente como observación hasta que exista un entorno autenticado que lo demuestre.

## 6. RFC-022 — reconciliación

RFC-022 se clasifica como **ACTIVE** en el estado de código verificado. El Core local y el Web local contienen las superficies esperadas. En el Web existen `GuidedShell`, `GuidedCatalogPanel`, `ProjectWorkspace`, `CommandBar`, catálogos localizados, recorrido inicial, selector de modo y pruebas asociadas.

La capacidad es reutilizable por ARQUI para navegación, explicación, identificación del siguiente paso y exposición de estados. No debe reemplazarse por un nuevo “Arqui Workspace”. El RFC conserva límites importantes: los catálogos no son hechos, el frontend no crea autoridad, la factibilidad no autoriza y el token del Core permanece server-side.

La documentación histórica de RFC-022 contiene varios baselines de `main`; este handoff usa los HEAD verificados arriba como estado operativo actual y no reescribe esos documentos históricos.

## 7. RFC-026 — reconciliación

RFC-026 se clasifica como **ACTIVE** en el estado de código verificado. El Core contiene `DesignKnowledgeSource`, `DesignKnowledgeItem`, `DesignPattern`, `DesignKnowledgeQuery`, `DesignKnowledgeResponse` y `DesignKnowledgeAgent`. También contiene:

- `GET /v1/design-knowledge/catalog`.
- `POST /v1/design-knowledge/query`.
- Consulta por las once escalas `SpatialScope`.
- Separación entre conocimiento teórico y fuentes normativas.
- RNE no verificado como `reference_only` y revisión humana requerida.
- Pruebas de agente, catálogo y endpoints.

RFC-026 es la base de conocimiento reutilizable por ARQUI. No es un agente autónomo que decide. Alexander y Ching son fuentes teóricas; RNE conserva su semántica normativa y su estado de vigencia. Ningún patrón se convierte automáticamente en requisito.

## 8. ARQUI — reconciliación de producto

ARQUI está clasificado como `REGISTERED / FROZEN / NOT YET IMPLEMENTATION-AUTHORIZED`. Su papel futuro es ser una interfaz contextual que orqueste capacidades existentes durante campo, oficina, diseño, análisis, comparación, revisión y presentación AR.

### Clasificación

```text
ARQUI_FOUNDATION = PARTIALLY_EXISTS
PRIMARY_STRATEGY = REUSE → COMPOSE → EXTEND
NEW_CANONICAL_SYSTEM = NO
NEW_CANONICAL_ENTITY = NOT AUTHORIZED
```

Ya existen piezas reutilizables:

```text
FieldCapture → Evidence
VFI → AI_PROPOSED Evidence → HumanReview
Site Intelligence → SpatialLocation
Design Intelligence → Alternatives / Evaluation
Design Knowledge Agent → Knowledge retrieval and provenance
SpatialRegistration → Registered frame relationship
AR → Contextual visual presentation
GuidedShell → Navigation and human-facing guidance
```

La composición futura requerirá una orden específica. Este handoff **no implementa ARQUI P1**, no crea `ArquiEvidence`, `ArquiDecision`, `ArquiLocation`, `ArquiMedia`, `ArquiDesign`, `ArquiHistory` ni `ArquiProjectState`.

## 9. Observaciones y limitaciones actuales

La implementación de VFI está preparada para análisis visual acotado, pero la evidencia L4 contra un proveedor real y un Core remoto autenticado todavía no está demostrada. AR muestra una representación contextual; no prueba survey-grade placement, SLAM, visual tracking, built-condition verification ni exactitud de obra.

SpatialRegistration usa inicialmente `MANUAL_TWO_POINT`. Dos puntos de control no equivalen a un levantamiento de límites del sitio. El Core remoto, el token de servicio, la persistencia tras reinicio y el entorno de proveedor deben configurarse antes de declarar E2E remoto.

RFC-022 y RFC-026 están implementados en las superficies verificadas, pero los documentos históricos pueden contener SHAs anteriores. Las afirmaciones operativas deben citar siempre el código y HEAD actual, no un baseline histórico sin reconciliación.

## 10. Capacidades futuras congeladas

Permanecen congeladas y no se activan mediante este handoff:

- ARQUI P1.
- `DOCUMENT-CAPTURE-INTELLIGENCE-01`.
- `SPATIAL-RECONSTRUCTION-01`.
- `LIVE-DESIGN-SESSION-01`.
- `ARCHITECT-WORKSPACE-V2`.
- Infraestructura de producción.
- Aplicación móvil nativa.
- Inteligencia continua de cámara o vídeo.
- SLAM, fotogrametría y reconstrucción LiDAR.
- Nuevos proveedores pagados.
- Nuevos modelos canónicos sin REAL GATE.

## 11. Protocolos de ejecución y REAL GATE

Para una futura orden autorizada, Manus debe leer este handoff, identificar la superficie afectada, reutilizar evidencia congelada, inspeccionar solo el código necesario, implementar el alcance autorizado, ejecutar validación proporcional, crear commit si corresponde y devolver un único informe consolidado.

Un REAL GATE existe ante una entidad canónica nueva, cambio material del Core Contract, cambio de autoridad humana, proveedor externo pagado, compromiso nuevo de privacidad, modelo de seguridad nuevo, decisión arquitectónica irreversible, expansión material de infraestructura o expansión material de alcance.

Ante REAL GATE se debe detener la implementación gated y devolver: razón, insuficiencia de arquitectura existente, decisión mínima requerida y opciones técnicamente necesarias. No son REAL GATE: decisiones ordinarias de implementación, pequeños cambios de UI, nombres menores, organización de tests o adaptadores reversibles dentro del alcance autorizado.

## 12. Contrato de retorno de Manus

Toda ejecución sustancial debe reportar `CAPABILITY`, `STATUS`, repositorio, baseline, archivos modificados, implementación, reutilización, cambios canónicos, resultado de autoridad humana, resultado epistemológico, tests, runtime evidence, evidence level, commit, HEAD, estado del worktree, push, PR, merge, deployment, observaciones, deferred items, REAL GATE status y next authorization point.

No se deben reclamar tests no ejecutados ni validación real de sitio, dispositivo o proveedor sin evidencia. Se debe distinguir siempre implementación local de runtime L4/L5.

## 13. Contrato de revisión ChatGPT

ChatGPT debe tratar el código verificado como verdad técnica, reutilizar evidencia congelada, no repetir auditorías sin superficie cambiada, distinguir L3/L4/L5, identificar REAL GATE, preparar decisiones acotadas y preservar autoridad humana. No debe inventar commits, tests, runtime, decisiones ni capacidad. Tampoco debe confundir AR visual con colocación topográfica, ni una propuesta AI con un hecho.

## 14. Próximo punto de autorización

El próximo punto de autorización es una decisión del Product Owner sobre si activar un **subconjunto acotado de composición ARQUI**, únicamente después de confirmar que la composición propuesta reutiliza GuidedShell, FieldCapture, VFI, Evidence, HumanReview, Project State, Design Knowledge, SpatialRegistration y AR sin crear sistemas canónicos paralelos.

Hasta esa decisión:

```text
ARQUI_P1 = FROZEN
PRODUCT_CODE_CHANGE_FOR_ARQUI = NO
PUSH = NO
PR = NO
MERGE = NO
DEPLOYMENT = NO
```

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SICL Core repository"
[2]: https://github.com/YvanCastilloQuezada/sicl-web "SiMS-DeI web repository"
[3]: docs/SIMS_DEI_CURRENT_ARCHITECTURE_v2.11.md "SiMS-DeI current architecture document"
[4]: docs/RFC-026_DESIGN_KNOWLEDGE_AND_MULTISCALE_DESIGN_GRAMMAR.md "RFC-026 Design Knowledge and Multiscale Design Grammar"
