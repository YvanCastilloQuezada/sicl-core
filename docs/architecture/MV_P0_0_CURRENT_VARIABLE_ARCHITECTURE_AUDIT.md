# MV-P0.0 — Current Variable Architecture Audit

**Proyecto:** SiMS-DeI / SICL
**Tipo:** Auditoría de arquitectura y descubrimiento, solo lectura
**Baseline auditado:** `sicl-core/main@d1cec3222a04ccfd969b2dfb81c222bb97294767`
**Referencia S7-P0.5:** `4c2017957354bd40c035c5e5bd2cd2fab7efbc58`
**Estado:** MV-P0.0 AUDIT ONLY
**Implementación autorizada:** NO

> **Conclusión ejecutiva.** El Core actual ya contiene una arquitectura funcional de `ProjectVariable` y `SuggestedVariable` derivada de RFC-021. `ProjectVariable` se registra por proyecto, conserva actor, autoridad, tipo, valor, unidad, escala, fuente y versión, y se expone mediante CLI y HTTP. Sin embargo, no existe todavía un catálogo canónico independiente, un perfil de variable por escala, un modelo general de requerimiento por escala, una semántica tipada de unidades, una resolución espacial independiente de `SpatialScope` ni una provenance completa enlazada a `Source` y `Evidence`. La opción futura recomendada es una **capa híbrida de metadatos y perfiles sobre las entidades existentes**, después de una orden MV-P0.1 separada.

## 1. Executive Finding

La respuesta a la pregunta central de MV-P0.0 es: **una parte importante de la arquitectura futura puede reutilizar las entidades existentes, pero el catálogo multiescala completo todavía no existe**.

El código actual separa correctamente varios conceptos constitucionales. `Fact`, `Assumption`, `Objective`, `Constraint`, `Evaluation`, `Source`, `Evidence`, `Recommendation`, `HumanReview` y `Decision` no se han colapsado en una clase universal. RFC-021 añade `SuggestedVariable` como sugerencia y `ProjectVariable` como estado explícito del proyecto. Esta separación debe preservarse.

Los principales vacíos son de metadatos y aplicabilidad. `ProjectVariable.spatial_scope` es una cadena, no un perfil de aplicabilidad. `ProjectVariable.source` es una cadena, no un enlace estructurado a provenance, Source y Evidence. `VariableType` solo distingue `OBJECTIVE`, `CONSTRAINT` y `PARAMETER`; no expresa todos los roles epistemológicos futuros. Las unidades son texto libre. El valor es `Any` y no existe validación dimensional general.

## 2. Repository / Baseline

La auditoría fue realizada contra `main` de `sicl-core` en `d1cec3222a04ccfd969b2dfb81c222bb97294767`. No se modificó ese baseline durante la inspección.

El commit S7-P0.5 `4c2017957354bd40c035c5e5bd2cd2fab7efbc58` se examinó como referencia separada. Su módulo `src/sicl/capabilities.py` contiene `CapabilityResolution`, `ProjectCapabilityContext`, cuatro estados de applicability y el identificador de perfil `multiscale-capability-s7p05-v1`. Esa referencia no se asumió automáticamente como parte del `main` auditado.

## 3. Current Variable Architecture

La arquitectura de variables actual se encuentra principalmente en `src/sicl/feasibility.py`, con integración en `src/sicl/domain.py`, `src/sicl/cli.py`, `src/sicl/repository.py`, `api/schemas.py` y `api/routes/v1.py`.

`VariableType` contiene `OBJECTIVE`, `CONSTRAINT` y `PARAMETER`. `SuggestedVariable` contiene `suggestion_id`, `normalized_key`, `label`, `variable_type`, `spatial_scope` y `normative_reference`. `ProjectVariable` contiene `variable_id`, `project_id`, `normalized_key`, `variable_type`, `value`, `actor_id`, `authority`, `unit`, `spatial_scope`, `source`, `version`, `supersedes_variable_id` y `normative_reference`.

La arquitectura es project-scoped y explícita. No es todavía un catálogo universal, porque no existe una entidad persistente de definición canónica ni un registro de sugerencias consultable.

## 4. Existing Variable Entities

| Entidad | Archivo / ubicación | Propósito | Persistida | Versionada | Proyecto | SpatialScope | Temporal | Source | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| `SuggestedVariable` | `src/sicl/feasibility.py:22-30` | Sugerencia de catálogo, sin mutación de proyecto | No como entidad independiente | No | No | Parcial: string | No | No | No |
| `ProjectVariable` | `src/sicl/feasibility.py:32-46` | Estado explícito adoptado por proyecto | Sí, mediante Event Log y replay | Sí | Sí | Parcial: string | No | Parcial: string | No |
| `VariableType` | `src/sicl/feasibility.py:16-20` | Clasifica variable en tres tipos | No aplica | No | No | No | No | No | No |
| `FeasibilityResult` | `src/sicl/feasibility.py:65-84` | Resultado de comprobación de restricciones | Sí como evento | Sí por evento | Sí indirectamente | No | No | IDs de evidencia y supuestos vacíos en el flujo actual | No por defecto |

`ProjectVariable` exige `variable_id`, `project_id`, `normalized_key`, `actor_id` y `authority`. La unicidad se valida por `project_id + normalized_key`. El valor continúa siendo genérico (`Any`), por lo que el tipo semántico depende del uso.

## 5. Project / Knowledge Entities

El dominio existente contiene `Project`, `Stage` como campo de etapa, `SpatialScope`, `TemporalScope`, `Fact`, `Assumption`, `Objective`, `Constraint`, `Source`, `Evidence`, `Alternative`, `Evaluation`, `Comparison`, `Recommendation`, `HumanReview` y `Decision`.

También existen entidades de actores, ciclos temporales, escenarios, relaciones de escala, regulación, interpretaciones normativas y snapshots normativos. La arquitectura de Design Knowledge existe en `src/sicl/design_knowledge.py` y separa conocimiento, patrones y normativa. Site Intelligence existe en `src/sicl/site_intelligence.py` mediante `SiteObservation` y el adaptador Open-Meteo.

La conclusión de reutilización es favorable: el futuro catálogo debe añadir metadatos de definición y aplicabilidad sin reemplazar estas entidades.

## 6. Variable Roles

El código actual distingue correctamente varias funciones mediante entidades diferentes: `Fact` representa información declarada; `Assumption` representa supuestos; `Objective` representa una dirección de optimización; `Constraint` representa una restricción; `Evaluation` representa un valor evaluado para una alternativa; y `ProjectVariable` representa información explícita del proyecto.

`VariableType` solo cubre `OBJECTIVE`, `CONSTRAINT` y `PARAMETER`. No existe una enumeración general para `STATE`, `FACT`, `ASSUMPTION`, `INPUT`, `DESIGN_VARIABLE`, `EVALUATION_METRIC`, `DERIVED_METRIC`, `CONTEXT` y `REFERENCE`. No se debe forzar esa lista futura dentro de `VariableType`; la separación por entidades existente es parte del diseño a reutilizar.

**Soporte:** PARTIAL. **Riesgo:** introducir una clase universal duplicaría semánticas que ya están separadas.

## 7. Identity

La identidad de `ProjectVariable` es canónica dentro del proyecto mediante `variable_id` y `normalized_key`. La clave normalizada convierte mayúsculas, guiones y espacios, y la unicidad se valida por proyecto.

La identidad de `SuggestedVariable` es una sugerencia local con `suggestion_id` y `normalized_key`; no existe un catálogo persistente que garantice IDs estables entre proyectos. Las etiquetas están separadas de la clave, pero no se observa una capa de aliases localizada ni un `catalog_version`.

**Clasificación:** MIXED.
**Riesgos:** colisión entre una clave de proyecto y una futura definición canónica; reutilización de una misma palabra con significados distintos por escala; y dependencia de texto libre en lugar de IDs de catálogo.

## 8. Data Types

`ProjectVariable.value` es `Any`. La implementación acepta valores numéricos y cadenas; el HTTP schema también permite un valor genérico. No existe un `VariableDataType` general para integer, float, decimal, boolean, string, enum, fecha, geometría, referencia o colección.

Los modelos especializados sí usan tipos concretos en sus propias entidades. Esa tipificación no se extiende automáticamente a variables.

**Soporte:** PARTIAL. **Acción futura:** definir un perfil de tipos sin alterar el valor histórico sin migración explícita.

## 9. Units

`ProjectVariable.unit` es `str | None`. `Constraint.unit` y `Evaluation.unit` también son cadenas. El Core conserva unidades textuales, pero no valida dimensionalidad ni compatibilidad de unidades.

**Estado:** FREE_TEXT / PARTIAL. No existe sistema de conversión ni validación general. Por tanto, no está permitido comparar automáticamente `m²`, `ha`, `km²`, porcentajes, moneda, potencia, energía o caudal sin una metodología posterior.

## 10. Spatial Applicability

El Core contiene exactamente un enum canónico `SpatialScope` en `src/sicl/domain.py:118-153`, con once valores: `pais`, `macro_region`, `region`, `provincia_metropoli`, `distrito_ciudad`, `zona_barrio_sector`, `parcela_sitio`, `edificacion`, `sistema`, `espacio` y `objeto`.

`ProjectVariable.spatial_scope` puede guardar un valor de escala, pero la arquitectura actual no representa una variable aplicable a múltiples escalas como relación de catálogo. Tampoco representa distintos requirement levels, cambios semánticos por escala o `NOT_APPLICABLE` por escala.

**Soporte:** PARTIAL para una instancia de proyecto; NO para un perfil multiescala.

## 11. Requirement Levels

No se encontró un modelo actual de requirement level para variables equivalente a `REQUIRED`, `RECOMMENDED`, `OPTIONAL` y `NOT_APPLICABLE`.

La referencia S7-P0.5 usa estados de capability: `AVAILABLE`, `REQUIRES_DATA`, `NOT_AVAILABLE` y `NOT_APPLICABLE`. Esos estados describen disponibilidad de una capacidad, no el requerimiento de una variable.

**VARIABLE_REQUIREMENT_MODEL:** MISSING.
**CAPABILITY_AVAILABILITY_MODEL:** IMPLEMENTED IN S7-P0.5 REFERENCE.
**SEMANTIC_SEPARATION:** PARTIAL, porque los dos conceptos existen como intención arquitectónica, pero el catálogo de variables aún no existe.

## 12. Temporal Semantics

`TemporalScope` existe en `src/sicl/domain.py:156-175` con `proyecto`, corto, mediano y largo plazo, además de escenarios 2030, 2040 y 2050. Se aplica al proyecto y no constituye un atributo temporal completo de `ProjectVariable`.

No hay en `ProjectVariable` separación explícita entre observation timestamp, reference date, measurement period, frequency, planning horizon, scenario year y retrieval timestamp.

**Soporte:** PARTIAL a nivel de proyecto; NO a nivel de variable.

## 13. Spatial Resolution

La arquitectura actual identifica una escala mediante `SpatialScope`, pero no una resolución espacial independiente. No se encontró un campo general para grid cell, unidad censal, watershed, corridor, parcel geometry o resolución de dataset.

Los módulos BIM, GIS y espacial pueden tener sus propias coordenadas o geometrías, pero no constituyen un `VariableSpatialResolution` común.

**Soporte:** PARTIAL para escala conceptual; MISSING para resolución de datos.

## 14. Provenance

`Source` contiene `source_id`, proyecto, tipo, título, URL y versión. `Evidence` contiene fuente opcional, statement, tipo, `captured_at`, `method_version`, URL, hash, estado y versión. Esta es una base útil y versionada para trazabilidad.

`ProjectVariable.source` es texto libre y `normative_reference` es metadata textual. No existe un enlace estructurado entre una variable y múltiples Sources/Evidence, ni un `dataset`, `dataset_version`, `retrieved_at`, `location`, `temporal_reference` o `derivation_method` general para variables.

**Soporte:** PARTIAL. La provenance está implementada para Source/Evidence, pero no integrada como contrato general de Variable.

## 15. Source / Evidence

Una variable puede guardar una referencia textual a source, pero no un enlace canónico requerido. Una `Source` puede ser referenciada por una o más `Evidence`. Evidence puede tener URL, hash, captura y versión. Varias evidencias pueden apoyar un mismo hecho a través de las entidades del proyecto.

La autoridad aparece en varias entidades, incluyendo `ProjectVariable.authority`, `Decision.authority` y estructuras regulatorias. La evidencia conflictiva se representa parcialmente mediante estados de conocimiento y múltiples evidencias, pero no mediante un modelo específico de conflicto de valores variables.

**Soporte:** Source linkage PARTIAL; Evidence linkage PARTIAL; authority PARTIAL; conflict representation PARTIAL.

## 16. Derived Lineage

La arquitectura puede conservar resultados derivados en `Evaluation`, simulaciones, resultados de factibilidad y análisis ambiental. En las evaluaciones actuales, `source` y `method` ofrecen parte de la trazabilidad; no existe un lineage general que enumere inputs, fórmula, versión del método y outputs para cualquier variable derivada.

Para el caso UPAO-001, `GROSS_MASSING_AREA` y `OPEN_SITE_AREA` pueden generarse determinísticamente desde la representación espacial S2 en las ramas de trabajo correspondientes. Esta relación es una implementación específica, no un catálogo general de derivación.

**Clasificación:** PARTIAL / MIXED. El lineage específico puede ser explícito; el lineage universal es implícito o faltante.

## 17. Design Knowledge

Design Knowledge está implementado y separado de los valores de variables. `DesignKnowledgeSource`, `DesignKnowledgeItem`, `DesignPattern` y el agente de conocimiento entregan orientación, patrones y preguntas abiertas. El agente mantiene la regla de que el conocimiento teórico no crea automáticamente una restricción, recomendación o decisión.

La vinculación futura adecuada es informativa: una variable puede recibir una fuente de conocimiento o una guía dimensional, pero `DesignKnowledgeItem` no debe convertirse en valor de variable.

**DESIGN_KNOWLEDGE_LINK_SUPPORT:** PARTIAL.
**Invariante preservada:** DESIGN KNOWLEDGE != VARIABLE VALUE.

## 18. Regulatory Intelligence

El Core contiene `Regulation`, `NormativeInterpretation` y `NormativeSnapshot`. Regulation identifica jurisdicción, autoridad, código, versión, fechas, estado, fuente, hash y escalas aplicables. NormativeInterpretation incluye intérprete, confianza, estado y disclaimer. NormativeSnapshot conserva el conjunto congelado de regulaciones e interpretaciones.

La relación conceptual correcta es fuente oficial, evidencia o snapshot, interpretación humana, y luego restricción o metadata de proyecto. El registro de `ProjectVariable.normative_reference` es trazabilidad, no interpretación automática.

**REGULATORY_LINK_SUPPORT:** PARTIAL / GOOD para entidades normativas; PARTIAL para Variable.

## 19. Site Intelligence

`SiteObservation` es una observación de sitio, no una variable universal. `src/sicl/site_intelligence.py` obtiene geocodificación y pronóstico de Open-Meteo y devuelve temperatura, viento, radiación, ubicación, fuente, respuesta cruda, versión de método y URLs de evidencia. Existe un fallback sintético para Trujillo.

Esta estructura es compatible con el futuro catálogo como fuente o input ambiental. No debe aplanarse en `ProjectVariable` sin conservar la diferencia entre observación, fuente externa y variable derivada.

**SITE_INTELLIGENCE_LINK_SUPPORT:** PARTIAL. El enlace se realiza por flujo y fuente, no por un catálogo de variables.

## 20. Environmental Analysis

El commit S7-P0.5 de referencia añade `EnvironmentalAnalysis` y análisis solar temporal. La arquitectura distingue inputs ambientales de resultados espaciales y usa `CapabilityResolution` para informar estados. En `capabilities.py`, `SOLAR_TEMPORAL_ANALYSIS` exige conceptualmente `location` y `environmental_data`; para `edificacion` puede ser `AVAILABLE` o `REQUIRES_DATA`, mientras que escalas superiores conceptualmente aplicables quedan `NOT_AVAILABLE` en S7-P0.5.

Esta capacidad confirma que el futuro catálogo debe relacionar variables ambientales, escala, datos requeridos y capability, pero no demuestra que exista todavía un catálogo de variables.

**ENVIRONMENTAL_LINK_SUPPORT:** PARTIAL en la referencia S7-P0.5; no sustituye el catálogo MV.

## 21. Evaluation / Pareto

`Evaluation` es un concepto separado de Variable. Contiene identidad de evaluación, alternativa, objetivo, valor, unidad, confianza, source y versión. El Core conserva evaluaciones append-only y las utiliza en Comparison y Pareto.

En el dataset espacial UPAO-001, las métricas canónicas auditadas son `GROSS_MASSING_AREA` y `OPEN_SITE_AREA`. Es correcto mantener Evaluation como resultado de una alternativa respecto de un objetivo. El catálogo futuro puede definir una variable que alimente una evaluación, pero no debe convertir Evaluation en una fila del catálogo universal.

**EVALUATION_LINK_SUPPORT:** GOOD como entidad separada; PARTIAL como relación a Variable.

## 22. Capability Architecture

S7-P0.5 define `CapabilityResolution`, `ProjectCapabilityContext`, `SpatialScope`, `typology`, `stage`, `available_data`, `objectives`, `context`, `required_data`, `missing_data`, `status`, `reason_code` y `profile_version`.

La arquitectura es adecuada como capa de applicability de capabilities. Puede recibir en el futuro IDs de variables en `required_data`, pero actualmente esos valores son strings y no requieren identidad de catálogo. No se debe reemplazar esa capa por una Variable universal durante MV-P0.0.

**CAPABILITY_LINK_SUPPORT:** GOOD para el modelo S7-P0.5 de referencia; NO para linkage a un catálogo aún inexistente.

## 23. Missing Data Semantics

El Core distingue `INSUFFICIENT_DATA` en factibilidad y `NOT_AVAILABLE` en capabilities, además de `UNKNOWN`, `ASSUMED` y estados de conocimiento en distintas entidades. Sin embargo, el valor `None`, una clave ausente, cero, una cadena vacía y un dato desconocido no tienen un contrato universal para `ProjectVariable.value`.

**Ambigüedad peligrosa:** con `value: Any`, cero puede ser un valor legítimo, `None` puede significar ausencia o un valor explícito, y `NOT_APPLICABLE` no está disponible como estado de variable. El invariante futuro debe ser `NOT_AVAILABLE != ZERO`, `NOT_AVAILABLE != ASSUMED` y `NOT_AVAILABLE != NOT_APPLICABLE`.

No se implementaron correcciones.

## 24. Domain Architecture

El Core ya contiene dominios especializados para arquitectura, regulación, design knowledge, BIM, GIS, ambiente y factibilidad, pero no se encontró un catálogo transversal formal con todos los dominios candidatos. `VariableType` no funciona como taxonomía de dominio.

**Soporte actual:** PARTIAL.
**Observación:** los dominios de `DEMOGRAPHY`, `ECONOMY`, `AGRICULTURE`, `FISHERIES`, `MINING`, `INDUSTRY` y otros territoriales no están implementados como catálogo de variables en el baseline auditado.

## 25. 11-Scale Support Matrix

| SpatialScope | Variable profile | Examples actuales | Scale filtering | Suggestions | Requirement by scale | Gaps |
|---|---|---|---|---|---|---|
| `objeto` | NO | Variables de proyecto con string de escala, sin perfil | PARTIAL | NO | NO | Sin catálogo de objetos |
| `espacio` | NO | `ProjectVariable.spatial_scope` puede contener el valor | PARTIAL | NO | NO | Sin semántica de espacio |
| `sistema` | NO | Valor aceptado por enum canónico | PARTIAL | NO | NO | Sin perfil de sistemas |
| `edificacion` | PARTIAL | UPAO/S7 solar y variables RFC-021 | YES/PARTIAL | NO | NO | Reglas no centralizadas |
| `parcela_sitio` | PARTIAL | Site Intelligence, BIM/GIS y variable RFC-021 | PARTIAL | NO | NO | Sin perfil de variables de sitio |
| `zona_barrio_sector` | NO | `SpatialScope` y relaciones de escala | PARTIAL | NO | NO | Sin variables urbanas catalogadas |
| `distrito_ciudad` | NO | Consultas de conocimiento por escala | PARTIAL | NO | NO | Sin perfil territorial |
| `provincia_metropoli` | NO | Enum y relaciones de escala | PARTIAL | NO | NO | Sin variables metropolitanas |
| `region` | NO | Enum y planificación normativa | PARTIAL | NO | NO | Sin dataset ni variables regionales |
| `macro_region` | NO | Enum canónico | PARTIAL | NO | NO | Sin flujos macroregionales |
| `pais` | NO | Enum canónico y planificación | PARTIAL | NO | NO | Sin catálogo nacional |

No se fabricaron conteos de variables. `SpatialScope` existe, pero no implica automáticamente soporte de perfil, sugerencias o requirements por escala.

## 26. Current Architecture Map

```text
Project
 ├── spatial_scope: SpatialScope
 ├── temporal_scope: TemporalScope
 ├── Facts / Assumptions
 ├── Objectives / Constraints
 ├── ProjectVariables  ── persisted through Event Log replay
 ├── Alternatives
 │    └── Evaluations ── source / unit / confidence
 ├── Sources ── Evidence
 ├── Design Knowledge ── advisory, no automatic decision
 ├── Regulation ── Interpretation ── NormativeSnapshot
 ├── SiteObservation ── Open-Meteo / fallback
 ├── Feasibility ── FeasibilityResult
 ├── Capabilities [S7-P0.5 reference]
 ├── HumanReview
 └── Decision
```

| Relación | Estado |
|---|---|
| Project → SpatialScope / TemporalScope | IMPLEMENTED |
| Project → ProjectVariable | IMPLEMENTED |
| ProjectVariable → Source / Evidence | PARTIAL, principalmente texto libre |
| Fact / Assumption → Evidence | IMPLEMENTED/PARTIAL según entidad y flujo |
| Alternative → Evaluation → Pareto | IMPLEMENTED |
| Design Knowledge → Variable value | MISSING intentionally; advisory separation |
| Regulation → Interpretation → Constraint/Variable | PARTIAL, con referencia normativa |
| SiteObservation → Environmental analysis | PARTIAL; S7-P0.5 reference |
| Capability → required data / missing data | IMPLEMENTED in S7-P0.5 reference |
| Variable catalog → profiles by scale | MISSING |
| HumanReview → Decision | IMPLEMENTED as separate invariant |

## 27. Gap Matrix

| Concern | Current support | Reuse potential | Gap | Future action |
|---|---|---|---|---|
| Canonical variable identity | PARTIAL | ProjectVariable IDs and keys | No global definition catalog | Audit and profile layer |
| Project variable instance | YES | `ProjectVariable` | Limited value semantics | Reuse |
| Scale applicability | PARTIAL | SpatialScope | No multi-scope profile | Add metadata layer later |
| Variable role | PARTIAL | Objective, Constraint, Evaluation, Fact | Only three VariableType values | Preserve separate entities |
| Requirement level | NO | Capability states are separate | No variable requirement enum | Define later |
| Data type | PARTIAL | Typed domain entities | `value: Any` | Add typed metadata later |
| Units | FREE_TEXT | Existing unit fields | No dimensional validation | Define separately |
| Temporal semantics | PARTIAL | TemporalScope | No variable period/frequency | Add temporal metadata later |
| Spatial resolution | NO | SpatialScope | No dataset resolution | Define after GIS audit |
| Provenance | PARTIAL | Source, Evidence, hashes, URLs | Not linked generically to variables | Add references later |
| Source linkage | PARTIAL | `ProjectVariable.source` | String, not Source ID | Avoid breaking migration |
| Evidence linkage | PARTIAL | Evidence entity | No variable evidence collection | Add relation later |
| Derived lineage | PARTIAL | Evaluation and method fields | No generic DAG/formula | Define derivation contract later |
| Validation | PARTIAL | Required identity and uniqueness | Generic values weakly typed | Add profile validation later |
| Versioning | PARTIAL | Event Log and version fields | No catalog version | Define catalog version later |
| Domain taxonomy | PARTIAL | Specialized modules | No cross-scale vocabulary | Audit first |
| Project adoption | YES | ProjectVariable | No suggested catalog | Reuse and extend |
| Customization | PARTIAL | Project-local keys | No canonical override policy | Define governance later |
| Missing-data semantics | PARTIAL | Feasibility/capability states | Generic value ambiguity | Define explicit states later |
| `NOT_APPLICABLE` | Capability only | S7-P0.5 | Missing for variables | Keep dimensions separate |
| Capability linkage | GOOD in S7 reference | CapabilityResolution | required_data strings | Map IDs later |
| Design Knowledge linkage | PARTIAL | Design knowledge agent | No variable relationship | Advisory metadata later |
| Regulatory linkage | PARTIAL | Regulations and snapshots | Normative reference text | Preserve human review |
| Site Intelligence linkage | PARTIAL | SiteObservation | No canonical variable mapping | Define carefully |
| Environmental linkage | PARTIAL in S7 reference | EnvironmentalAnalysis | Not catalog-backed | Extend only after audit |
| Evaluation linkage | GOOD as separate entity | Evaluation/Pareto | No formal variable metric ID | Reuse Evaluation |

## 28. Future Architecture Options

**Option A — One universal Variable entity.** Rejected as the primary design. It would risk collapsing facts, assumptions, inputs, design variables, objectives and evaluations.

**Option B — Extend existing Variable architecture.** Viable for project instances, but insufficient alone because `ProjectVariable` is not a global definition catalog.

**Option C — Metadata/profile layer over existing canonical entities.** Strong fit for applicability, requirement level, domains, provenance requirements and scale-specific semantics without duplicating Objective, Constraint, Fact, Evidence or Evaluation.

**Option D — Hybrid architecture.** Recommended. Reuse `ProjectVariable` for explicit project adoption, add a future canonical definition/profile layer only where the audit proves a gap, and preserve existing entities for facts, assumptions, objectives, constraints and evaluations.

**Option E — Insufficient evidence.** Not the final conclusion because the current audit identifies an implementable direction, but MV-P0.1 must still inspect all current lineage before schema decisions.

**RECOMMENDED_ARCHITECTURE_OPTION:** D — Hybrid architecture, implemented conservatively as a metadata/profile layer over existing entities.

## 29. Three-Layer Pattern Assessment

```text
VariableDefinition
        ↓
ScaleVariableProfile
        ↓
ProjectVariable
```

**PATTERN_FIT:** PARTIAL to GOOD.

`ProjectVariable` already exists as the project-specific adoption/value/state layer. `VariableDefinition` is missing as a global canonical semantic definition. `ScaleVariableProfile` is missing as the applicability, requirement and role layer. The pattern fits the existing separation, but its exact names and fields must not be implemented before a lineage audit of current branches and main.

**REUSE_EXISTING_ENTITIES:** `ProjectVariable`, `SuggestedVariable`, `SpatialScope`, `Objective`, `Constraint`, `Fact`, `Assumption`, `Source`, `Evidence`, `Evaluation` and S7-P0.5 `CapabilityResolution`.

**NEW_CONCEPTS_POTENTIALLY_REQUIRED:** a definition/profile metadata layer, not necessarily new runtime entities or database tables. The need for persistence is unresolved until MV-P0.1.

## 30. Cross-Scale Reuse

A meteorological `shortwave_radiation` input may be reusable across scales as a source variable when its time and spatial resolution are preserved. It is not identical to `FacadeSolarExposure`, which is a derived spatial result. Neither is identical to `RegionalSolarResourcePotential`, which has a different scale, aggregation and meaning.

`population` may reuse a canonical semantic definition with different spatial aggregation and reference periods. `building geometry` and `regional land-use geometry` should not share an identity merely because both are geometry. `accessibility time` may be reused only when mode, origin-destination definition, network version and spatial unit are compatible.

These are evidence-backed semantic examples, not final IDs.

## 31. Risks

The principal risks are semantic duplication, collision between free-text keys and future catalog IDs, accidental conversion of statistical indicators into design variables, unit incompatibility, loss of temporal reference, loss of source/evidence traceability, use of `NOT_AVAILABLE` as zero, overloading `TemporalScope`, treating capability availability as variable requirement, and automatic normative mutation of project state.

A further risk is branch divergence: RFC-021 is present in the audited `main`, while S7-P0.5 was inspected at a separate authorized commit. Any future integration must verify ancestry before assuming the two surfaces are co-deployed.

## 32. Decisions Required Before MV-P0.1

Before implementation, Product Owner approval is required for: the canonical definition/profile boundary; whether profiles are persisted; catalog ownership and versioning; value typing; unit semantics; temporal and spatial resolution; provenance relations; domain governance; localization rules; project customization; migration strategy; historical analysis compatibility; and the relationship between variable requirements and capability availability.

MV-P0.1 must also verify the final branch ancestry of RFC-019 through RFC-024 and S7-P0.5, without restoring historical code merely because documentation references it.

## 33. Evidence Appendix

| Evidence | Location | Finding |
|---|---|---|
| Canonical scales | `src/sicl/domain.py:118-153` | Exactly eleven `SpatialScope` values |
| Variable entities | `src/sicl/feasibility.py:16-46` | `VariableType`, `SuggestedVariable`, `ProjectVariable` |
| Project storage | `src/sicl/domain.py:254-291` | `project_variables` is project-scoped |
| Persistence replay | `src/sicl/repository.py:556-560` | Variables replay from append-only events |
| HTTP create/list | `api/routes/v1.py:888-910` | POST and GET project variables |
| CLI | `src/sicl/cli.py:1370-1403` | `/VARIABLE ADD` and `/VARIABLE LIST` |
| RFC-021 | `docs/RFC-021_PROJECT_VARIABLES.md` | Current contract and invariants |
| Source/Evidence | `src/sicl/domain.py:593-624` | Versioned provenance primitives |
| Site Intelligence | `src/sicl/site_intelligence.py:66-118` | Open-Meteo and deterministic fallback |
| Regulation | `src/sicl/domain.py:532-590` | Regulation, interpretation, snapshot |
| S7 capabilities | commit `4c201795...`, `src/sicl/capabilities.py` | Applicability model reference |

## Final Gate

MV_P0_0_AUDIT = PASS

CURRENT_ARCHITECTURE_MAPPED = YES

REUSE_BEFORE_CREATION = PASS

11_SCALE_GAPS_IDENTIFIED = YES

S7_P0_5_CAPABILITY_RELATIONSHIP_AUDITED = YES

VARIABLE_MODEL_IMPLEMENTED = NO

VARIABLE_DATA_LOADED = NO

READY_FOR_MV_P0_1 = NO — requires explicit authorization and decisions listed in section 32.

PRODUCT_CODE_CHANGED = NO
WEB_CHANGED = NO
DATABASE_CHANGED = NO
API_CHANGED = NO
NEW_DEPENDENCIES = NO
MAIN_MODIFIED = NO
DEPLOYED = NO

**STOP.**

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SiMS-DeI SICL Core repository"
[2]: https://github.com/YvanCastilloQuezada/sicl-web "SiMS-DeI SICL Web repository"
