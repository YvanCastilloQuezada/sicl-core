# Glosario de SiMS-DeI y SICL

Este glosario define las entidades que aparecen en el Core 2.1. Cada entrada incluye nombre, definición, ejemplo, referencia RFC y estados posibles. Los estados no son equivalentes entre entidades; deben interpretarse según el contrato de cada una.

## Actor

**Definición:** Persona o agente humano identificado que participa en el proyecto y puede tener autoridad o intereses declarados.  
**Ejemplo:** `A-DEC`, arquitecto con autoridad `DECISIONAL`.  
**Referencia RFC:** RFC-012.  
**Estados:** `ACTIVE`, `INACTIVE`, `SUSPENDED`.

## ActorPosition

**Definición:** Posición explícita de un actor respecto de una entidad o asunto.  
**Ejemplo:** Un actor apoya una alternativa bajo la condición de respetar el presupuesto.  
**Referencia RFC:** RFC-012.  
**Estados:** `SUPPORT`, `OPPOSE`, `NEUTRAL`, `CONDITIONAL`.

## Alternative

**Definición:** Opción de diseño que puede ser parametrizada, evaluada, comparada o recomendada. No es una Decision.  
**Ejemplo:** `BIOCLIMATICA_B` con protección solar y menor consumo energético.  
**Referencia RFC:** Core Contract y RFC-005.  
**Estados:** `DRAFT`, `ACTIVE`, `PROMOTED`, `REJECTED`.

## Assumption

**Definición:** Premisa de trabajo que no tiene todavía el estado de hecho verificable.  
**Ejemplo:** `OCCUPANCY=80%` con basis `ESTIMACION`.  
**Referencia RFC:** Core Contract, B-001.  
**Estados:** `UNKNOWN`, `OBSERVED`, `CONFLICTING`, `INSUFFICIENT`.

## Comparison

**Definición:** Resultado que reúne alternativas y evaluaciones para mostrar diferencias y trade-offs.  
**Ejemplo:** Comparar `CONVENCIONAL_A` y `BIOCLIMATICA_B` en energía y coste.  
**Referencia RFC:** RFC-005.  
**Estados:** `DRAFT`, `COMPLETE`, `INSUFFICIENT`.

## Constraint

**Definición:** Condición que una alternativa debe cumplir. En el alcance vigente es una restricción `HARD`.  
**Ejemplo:** `HEIGHT <= 6 FLOORS`.  
**Referencia RFC:** Core Contract.  
**Estados:** `ACTIVE`, `VIOLATED`, `SATISFIED`, `UNKNOWN`.

## Decision

**Definición:** Registro de una decisión humana explícita. Requiere actor, authority y HumanReview aprobado.  
**Ejemplo:** Seleccionar `BIOCLIMATICA_B` después de revisar la comparación.  
**Referencia RFC:** Core Contract.  
**Estados:** `RECORDED`, `SUPERSEDED`, `REVOKED`.

## DesignPrinciple

**Definición:** Principio de diseño disponible como catálogo read-only para consulta. No es una regla normativa automática.  
**Ejemplo:** Consultar el principio de proporción para orientar una explicación.  
**Referencia RFC:** RFC-004.  
**Estados:** `AVAILABLE`, `UNAVAILABLE`, `UNVERIFIED`.

## Evaluation

**Definición:** Valoración de una alternativa respecto de un objetivo, con unidad, confianza y fuente cuando corresponda.  
**Ejemplo:** `ENERGY_SAVINGS=78 PERCENT` producido por un agente experto.  
**Referencia RFC:** RFC-005.  
**Estados:** `OBSERVED`, `ESTIMATED`, `CONFLICTING`, `INSUFFICIENT`.

## Evidence

**Definición:** Afirmación documentada con vínculo a una Source, tipo, fecha, método y estado.  
**Ejemplo:** Observación de que el sitio está en Trujillo, respaldada por una fuente identificada.  
**Referencia RFC:** RFC-002.  
**Estados:** `OBSERVED`, `UNKNOWN`, `CONFLICTING`, `INSUFFICIENT`.

## Fact

**Definición:** Dato registrado como hecho verificable en el contexto del proyecto.  
**Ejemplo:** `SITE_AREA=2000` con source `CATASTRO`.  
**Referencia RFC:** Core Contract y B-001.  
**Estados:** `OBSERVED`, `CONFLICTING`, `UNKNOWN`.

## GeneratedAlternative

**Definición:** Conjunto de candidatos generados por un método determinista o por patrones declarados. Requiere revisión humana antes de ser promovido.  
**Ejemplo:** Tres configuraciones paramétricas producidas para dos objetivos.  
**Referencia RFC:** RFC-010.  
**Estados:** `GENERATED`, `REVIEWED`, `PROMOTED`, `REJECTED`.

## HumanReview

**Definición:** Registro de revisión humana de una propuesta, evaluación o resultado antes de una operación decisional.  
**Ejemplo:** El arquitecto declara que revisó la comparación y la recomendación.  
**Referencia RFC:** Core Contract.  
**Estados:** `APPROVED`, `REJECTED`, `PENDING`, `REVOKED`.

## InstitutionalMemory

**Definición:** Conocimiento institucional versionado que puede extraerse, anonimizarse, revocarse y aplicarse con autoridad explícita.  
**Ejemplo:** Un patrón de decisión anonimizado extraído de un proyecto cerrado.  
**Referencia RFC:** RFC-011.  
**Estados:** `DRAFT`, `ACTIVE`, `REVOKED`, `APPLIED`.

## MultiobjectiveResult

**Definición:** Resultado descriptivo de una operación multiobjetivo, como Pareto o trade-offs.  
**Ejemplo:** Frente no dominado entre ahorro energético y coste de construcción.  
**Referencia RFC:** RFC-007.  
**Estados:** `COMPLETE`, `INSUFFICIENT`, `CONFLICTING`.

## NormativeInterpretation

**Definición:** Interpretación explícita de una Regulation aplicada a un contexto, con disclaimer y revisión.  
**Ejemplo:** Interpretar un artículo normativo para un proyecto concreto sin afirmar certificación legal.  
**Referencia RFC:** RFC-003.  
**Estados:** `DRAFT`, `REVIEWED`, `APPROVED`, `REJECTED`, `UNKNOWN`.

## NormativeSnapshot

**Definición:** Corte versionado de regulaciones e interpretaciones utilizadas en una fecha determinada.  
**Ejemplo:** Snapshot normativo del proyecto al 2026-09-15.  
**Referencia RFC:** RFC-003.  
**Estados:** `DRAFT`, `REVIEWED`, `FROZEN`.

## Objective

**Definición:** Resultado que el proyecto busca maximizar, minimizar o alcanzar.  
**Ejemplo:** Maximizar `ENERGY_SAVINGS` hasta un valor objetivo.  
**Referencia RFC:** Core Contract.  
**Estados:** `ACTIVE`, `SATISFIED`, `UNSATISFIED`, `UNKNOWN`.

## PlanningInstrument

**Definición:** Instrumento de planificación registrado con autoridad, jurisdicción, alcance y estado. El catálogo real puede estar vacío.  
**Ejemplo:** Instrumento municipal vinculado a un proyecto cuando exista una fuente verificable.  
**Referencia RFC:** RFC-008.  
**Estados:** `DRAFT`, `ACTIVE`, `EXPIRED`, `REVOKED`, `UNKNOWN`.

## Preference

**Definición:** Prioridad expresada por un actor. Es distinta de Fact, Assumption, Objective y Decision.  
**Ejemplo:** Preferir menor coste inicial frente a una mejora marginal de rendimiento.  
**Referencia RFC:** Core Contract y HTTP v1.  
**Estados:** `ACTIVE`, `SUPERSEDED`, `REVOKED`.

## Project

**Definición:** Contenedor principal de contexto, entidades, eventos, escalas y resultados de un caso de diseño.  
**Ejemplo:** `UPAO-001`, proyecto sintético de Plaza Center.  
**Referencia RFC:** RFC-001 y Core Contract.  
**Estados:** `DRAFT`, `ACTIVE`, `CLOSED`, `ARCHIVED`.

## Recommendation

**Definición:** Salida analítica que propone una alternativa o lectura de resultados. No es una Decision y no puede crearla.  
**Ejemplo:** Recomendar revisar `BIOCLIMATICA_B` por su mejor desempeño energético.  
**Referencia RFC:** Core Contract.  
**Estados:** `DRAFT`, `ISSUED`, `REVIEWED`, `SUPERSEDED`.

## Regulation

**Definición:** Registro estructural de una norma o referencia regulatoria, con fuente, jurisdicción y vigencia.  
**Ejemplo:** Norma municipal identificada por código y URL fuente.  
**Referencia RFC:** RFC-003.  
**Estados:** `DRAFT`, `ACTIVE`, `EXPIRED`, `REVOKED`, `UNKNOWN`.

## ScaleRelation

**Definición:** Relación explícita entre proyectos o entidades ubicadas en escalas espaciales o temporales relacionadas.  
**Ejemplo:** Una parcela `CONTAINS` un edificio.  
**Referencia RFC:** RFC-009.  
**Estados:** `DECLARED`, `REVIEWED`, `REVOKED`, `CONFLICTING`.

## ScenarioBranch

**Definición:** Rama de escenario que explora condiciones y objetivos alternativos dentro de un ciclo temporal. No sobrescribe otras ramas.  
**Ejemplo:** Escenario `S-A` de crecimiento adaptativo frente a `S-B` conservador.  
**Referencia RFC:** RFC-013.  
**Estados:** `PROPOSED`, `EVALUATED`, `SELECTED`, `DISCARDED`.

## Simulation

**Definición:** Ejecución reproducible de un método declarado sobre inputs registrados. Produce resultados descriptivos.  
**Ejemplo:** Sensibilidad de un escenario frente a un cambio de presupuesto.  
**Referencia RFC:** RFC-006.  
**Estados:** `REQUESTED`, `RUNNING`, `COMPLETE`, `FAILED`, `INSUFFICIENT`.

## SiteObservation

**Definición:** Observación de un sitio obtenida mediante una fuente y un método trazables. No es una obligación normativa.  
**Ejemplo:** Datos climáticos observados para Trujillo mediante una API declarada.  
**Referencia RFC:** Site Intelligence y Core Contract.  
**Estados:** `OBSERVED`, `UNKNOWN`, `CONFLICTING`, `INSUFFICIENT`.

## Source

**Definición:** Origen identificado de una afirmación, evidencia, evaluación u observación.  
**Ejemplo:** Registro `OPEN_METEO_API` o documento catastral.  
**Referencia RFC:** RFC-002.  
**Estados:** `DECLARED`, `VERIFIED`, `UNVERIFIED`, `REVOKED`.

## SpatialScope

**Definición:** Escala espacial declarada para un proyecto o relación.  
**Ejemplo:** `parcela_sitio` para un proyecto de terreno.  
**Referencia RFC:** RFC-001 y RFC-009.  
**Estados:** `DECLARED`, `VALIDATED`, `UNKNOWN`, `CONFLICTING`.

## Stage

**Definición:** Etapa del ciclo de trabajo del proyecto.  
**Ejemplo:** Un proyecto puede pasar de `DRAFT` a `ACTIVE` y luego a `CLOSED`.  
**Referencia RFC:** Core Contract.  
**Estados:** `DRAFT`, `ACTIVE`, `PRELIMINARY_DESIGN`, `DETAILED_DESIGN`, `CLOSED`.

## TemporalCycle

**Definición:** Horizonte temporal con fechas, supuestos, objetivos y actores involucrados. No modifica decisiones pasadas.  
**Ejemplo:** Ciclo `C-2030` iniciado el 2026-01-01.  
**Referencia RFC:** RFC-013.  
**Estados:** `DRAFT`, `ACTIVE`, `SUPERSEDED`.

## TemporalScope

**Definición:** Alcance temporal declarado de un proyecto o entidad.  
**Ejemplo:** `proyecto`, `ciclo_2030` o un horizonte temporal acordado.  
**Referencia RFC:** RFC-001 y RFC-013.  
**Estados:** `DECLARED`, `VALIDATED`, `UNKNOWN`, `CONFLICTING`.

## Estados transversales

Además de los estados específicos de cada entidad, el sistema utiliza estados epistemológicos que describen la calidad o suficiencia del conocimiento:

- `UNKNOWN`: no existe información suficiente para afirmar un valor.
- `CONFLICTING`: existen valores o fuentes incompatibles.
- `INSUFFICIENT`: existe información relacionada, pero no alcanza para ejecutar el análisis.
- `OBSERVED`: existe una observación o registro con fuente y trazabilidad.

Estos estados no deben reemplazarse silenciosamente por una afirmación positiva. La autoridad humana debe revisar los casos que puedan afectar una Recommendation o una Decision.

## Referencias

[1]: https://github.com/YvanCastilloQuezada/sicl-core/blob/main/docs/SICL_CORE_CONTRACT_v1.0.md "SICL Core Contract v1.0"
[2]: https://github.com/YvanCastilloQuezada/sicl-core/blob/main/docs/SIMS_DEI_MASTER_ARCHITECTURE_v2.md "SiMS-DeI Master Architecture v2"
[3]: https://github.com/YvanCastilloQuezada/sicl-core/tree/main/docs "SICL RFC documentation"
