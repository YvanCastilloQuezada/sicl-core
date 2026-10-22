# RFC-026 — Design Knowledge and Multiscale Design Grammar

**Estado:** IMPLEMENTED ON MAIN — piloto funcional; aprobación del Product Owner pendiente para ampliar el corpus
**Fecha:** 16 de septiembre de 2026  
**Autor:** Manus AI  
**Sistema:** SiMS-DeI  
**Lenguaje formal:** SICL  
**Dependencias:** RFC-001, RFC-002, RFC-003, RFC-019, RFC-020, RFC-021, RFC-022, RFC-024 y RFC-025

> Este documento define una propuesta de arquitectura de conocimiento para que SiMS-DeI pueda apoyar el proceso de diseño espacial en cualquiera de sus once escalas. No autoriza todavía la incorporación masiva de libros, la extracción automática de reglas ni la promoción de heurísticas a obligaciones normativas.

### Registro de implementación

El piloto funcional implementa `DesignKnowledgeSource`, `DesignKnowledgeItem`, `DesignPattern`, `DesignKnowledgeQuery`, `DesignKnowledgeResponse` y `DesignKnowledgeAgent` en `src/sicl/design_knowledge.py`. También expone el catálogo y la consulta del agente mediante `GET /v1/design-knowledge/catalog` y `POST /v1/design-knowledge/query`.

El catálogo inicial contiene fuentes controladas de Alexander, Ching y el corpus RNE RFC-025; incluye patrones y principios revisados como `UNDER_REVIEW`. La consulta por escala reconoce las once instancias de `SpatialScope`. Las normas `NO_VERIFICADA`, `MODIFICADA` o `DEROGADA` se devuelven como `reference_only` y generan `HUMAN_REVIEW_REQUIRED`; no crean decisiones ni restricciones automáticas.

## 1. Resumen ejecutivo

SiMS-DeI debe operar un proceso de diseño común para las once escalas espaciales, desde país hasta objeto. El proceso común no implica que todas las escalas utilicen las mismas variables, restricciones o fuentes. Implica que todas recorran una gramática de diseño comparable: comprender el contexto, definir el problema, identificar objetivos, consultar conocimiento, formular estrategias, generar alternativas, evaluar consecuencias, filtrar factibilidad, documentar incertidumbres y solicitar autoridad humana cuando corresponda.

RFC-026 propone tres entidades centrales:

1. `DesignKnowledgeSource`, que identifica una fuente bibliográfica, técnica, normativa o experiencial.
2. `DesignKnowledgeItem`, que representa una unidad atómica de conocimiento extraída o registrada desde una fuente.
3. `DesignPattern`, que representa una solución recurrente contextualizada con problema, fuerzas, condiciones, solución, consecuencias y criterios de evaluación.

El RFC también define un **Agente de Conocimiento de Diseño**. Este agente no decide ni genera una recomendación por sí mismo. Recupera conocimiento aplicable, separa autoridad normativa de orientación heurística, vincula cada resultado con fuentes y evidencias, identifica conflictos de escala y entrega insumos trazables al generador, evaluador y agente crítico.

## 2. Problema que resuelve

La arquitectura actual de SiMS-DeI contiene generación paramétrica, variación basada en patrones, evaluación, factibilidad, agentes expertos, regulación y evidencia. Sin una capa formal de conocimiento de diseño, estas capacidades no comparten un registro común de principios, patrones, métodos, tipologías y criterios.

Esta ausencia produce cuatro riesgos:

- Un patrón teórico puede confundirse con una obligación legal.
- Una recomendación de un libro puede utilizarse fuera de su escala o contexto.
- El generador puede producir alternativas sin explicar qué conocimiento aplicó.
- Los agentes pueden consultar fuentes diferentes y generar resultados incompatibles.

RFC-026 establece una frontera explícita entre conocimiento, análisis y autoridad:

```text
Fuente
  → Unidad de conocimiento
    → Aplicabilidad por escala y contexto
      → Estrategia o patrón candidato
        → Alternativa
          → Evaluación y factibilidad
            → Recomendación
              → HumanReview
                → Decision humana
```

## 3. Objetivos

RFC-026 tiene los siguientes objetivos:

- Formalizar fuentes de conocimiento de diseño.
- Representar unidades de conocimiento atómicas y citables.
- Modelar patrones de diseño con condiciones de aplicabilidad.
- Mantener separadas las normas del RNE y la teoría de diseño.
- Permitir recuperación de conocimiento por escala, tipología, jurisdicción y objetivos.
- Conectar conocimiento con generación, evaluación y factibilidad.
- Mantener evidencia, procedencia, versión y estado de revisión.
- Hacer que el proceso de diseño sea común en las once escalas.
- Permitir que el Agente de Conocimiento de Diseño explique por qué recuperó cada unidad.
- Preservar la autoridad humana y la distinción entre Recommendation y Decision.

## 4. No objetivos

RFC-026 no pretende:

- Crear un arquitecto autónomo.
- Copiar libros completos al repositorio.
- Convertir patrones de Alexander o principios de Ching en normas legales.
- Interpretar automáticamente el RNE.
- Certificar cumplimiento arquitectónico, estructural, sanitario o eléctrico.
- Crear decisiones humanas de forma automática.
- Reemplazar a arquitectos, ingenieros, autoridades municipales o revisores legales.
- Determinar que una alternativa es universalmente buena.
- Reducir el diseño a una única métrica de optimización.

## 5. Principios constitucionales aplicables

### 5.1 Separación epistemológica

Cada unidad debe declarar si representa una norma, una guía técnica, una heurística, un hallazgo empírico, una teoría, una preferencia o una observación.

### 5.2 Recommendation no es Decision

El agente puede recuperar, organizar y explicar conocimiento. No puede registrar una `Decision`.

### 5.3 Fact no es Assumption

Los datos del sitio, las afirmaciones de una fuente y las hipótesis de diseño deben permanecer diferenciados.

### 5.4 Provenance obligatoria

Toda unidad utilizada para generar o evaluar una alternativa debe poder rastrearse a una fuente y, cuando corresponda, a una evidencia.

### 5.5 Aplicabilidad contextual

Una unidad de conocimiento no es aplicable solamente porque coincide con una palabra clave. Deben revisarse escala, tipología, jurisdicción, clima, usuarios, tiempo y condiciones declaradas.

### 5.6 No inferencia normativa

La presencia de una fuente del RNE no crea automáticamente una restricción. Una regla normativa requiere interpretación revisada, versión aplicable y alcance definido.

### 5.7 No autoridad de agentes

Los agentes producen análisis con fuente `EXPERT_SYSTEM`. No pueden aprobar una interpretación ni seleccionar una alternativa de forma vinculante.

### 5.8 Reversibilidad y versionado

Las correcciones de una unidad de conocimiento crean una nueva versión o un nuevo registro. No se reescribe el historial de uso.

## 6. Taxonomía de fuentes

`DesignKnowledgeSource` puede representar fuentes de distinto nivel de autoridad. La clasificación evita mezclar un reglamento con un libro de teoría o con una preferencia del usuario.

| `source_class` | Descripción | Ejemplos |
|---|---|---|
| `LEGAL_REGULATORY` | Fuente con efecto normativo aplicable | RNE, ordenanza, parámetro urbanístico |
| `OFFICIAL_TECHNICAL` | Manual o guía oficial | Manual sectorial, guía del MVCS |
| `PROFESSIONAL_GUIDANCE` | Manual profesional o estándar | Manual de diseño, estándar técnico |
| `EMPIRICAL_RESEARCH` | Estudio o investigación | Estudio climático, post-ocupación |
| `THEORETICAL` | Teoría o crítica de diseño | Alexander, Ching, Unwin, Pallasmaa |
| `HEURISTIC` | Regla práctica no obligatoria | Principio de composición o proceso |
| `PRECEDENT` | Caso o proyecto de referencia | Edificio, barrio, parque |
| `USER_PROVIDED` | Material aportado por el usuario | Brief, croquis, memoria |
| `SITE_OBSERVATION` | Observación del sitio | Open-Meteo, medición o inspección |

La clase de fuente no determina automáticamente su aplicabilidad. La aplicabilidad se evalúa por proyecto y escala.

## 7. Entidad DesignKnowledgeSource

### 7.1 Propósito

`DesignKnowledgeSource` identifica el origen bibliográfico, normativo, técnico o experiencial de una unidad de conocimiento.

### 7.2 Campos canónicos

| Campo | Tipo | Requisito | Descripción |
|---|---|---:|---|
| `source_id` | string | Sí | Identificador estable |
| `title` | string | Sí | Título de la fuente |
| `authors` | array[string] | Sí | Autores o entidad emisora |
| `source_class` | enum | Sí | Clase epistemológica |
| `source_type` | enum | Sí | Libro, norma, manual, artículo, web, observación o precedente |
| `language` | string | Sí | Idioma principal |
| `publication_year` | integer/null | No | Año de publicación |
| `publisher_or_authority` | string/null | No | Editorial o autoridad |
| `jurisdiction` | string/null | No | Jurisdicción, cuando corresponda |
| `edition_or_version` | string/null | No | Edición o versión |
| `isbn_or_legal_id` | string/null | No | ISBN, resolución u otro identificador |
| `url` | string/null | No | URL verificable |
| `license_status` | enum | Sí | Condición de uso |
| `bibliographic_reference` | string | Sí | Referencia legible |
| `content_hash` | string/null | No | Hash del archivo o captura autorizada |
| `retrieved_at` | datetime/null | No | Momento de recuperación |
| `review_status` | enum | Sí | Estado editorial y de revisión |
| `version` | integer | Sí | Versión del registro |

### 7.3 Estados de fuente

```text
REGISTERED
BIBLIOGRAPHICALLY_VERIFIED
EXTRACTED
UNDER_REVIEW
APPROVED
DEPRECATED
REJECTED
```

`APPROVED` significa que la fuente está aprobada para el uso descrito en el proyecto. No significa que todas sus afirmaciones sean válidas para cualquier escala.

### 7.4 Licencias

```text
PUBLIC_DOMAIN
OPEN_LICENSE
LICENSE_REVIEW_REQUIRED
USER_AUTHORIZED
NO_REPRODUCTION
UNKNOWN
```

El sistema debe preferir metadatos, resúmenes propios y referencias a páginas o artículos. No debe almacenar libros completos sin autorización adecuada.

## 8. Entidad DesignKnowledgeItem

### 8.1 Propósito

`DesignKnowledgeItem` representa una unidad atómica que puede ser citada, revisada, recuperada y vinculada a una alternativa.

Una unidad debe expresar una sola afirmación o procedimiento principal. El registro no debe ser una copia de un capítulo completo.

### 8.2 Campos canónicos

| Campo | Tipo | Requisito | Descripción |
|---|---|---:|---|
| `knowledge_item_id` | string | Sí | Identificador estable |
| `source_id` | string | Sí | Fuente de origen |
| `item_type` | enum | Sí | Tipo de unidad |
| `title` | string | Sí | Nombre breve |
| `statement` | string | Sí | Afirmación o instrucción resumida |
| `description` | string | No | Explicación contextual |
| `epistemic_status` | enum | Sí | Fact, guidance, heuristic, theory u otro |
| `authority_level` | enum | Sí | Nivel de autoridad |
| `applicable_scales` | array[SpatialScope] | Sí | Escalas compatibles |
| `excluded_scales` | array[SpatialScope] | No | Escalas excluidas |
| `applicable_typologies` | array[string] | No | Tipologías compatibles |
| `jurisdictions` | array[string] | No | Jurisdicciones aplicables |
| `conditions` | object | No | Condiciones necesarias |
| `inputs` | array[string] | No | Datos requeridos |
| `outputs` | array[string] | No | Resultados esperados |
| `criteria` | array[string] | No | Criterios que puede informar |
| `evidence_ids` | array[string] | No | Evidencias de soporte |
| `citation_locator` | string/null | No | Página, artículo o sección |
| `review_status` | enum | Sí | Estado de revisión |
| `limitations` | array[string] | No | Límites conocidos |
| `version` | integer | Sí | Versión del registro |

### 8.3 Tipos de unidad

```text
DESIGN_PRINCIPLE
PATTERN_REFERENCE
HEURISTIC
METHOD
TYPOLOGY
DIMENSIONAL_GUIDANCE
SPATIAL_RELATION
EVALUATION_CRITERION
PRECEDENT
REGULATORY_RULE
EMPIRICAL_FINDING
DESIGN_QUESTION
```

### 8.4 Niveles de autoridad

```text
LEGAL
OFFICIAL_TECHNICAL
EMPIRICAL
PROFESSIONAL_GUIDANCE
THEORETICAL
HEURISTIC
EXPERIENTIAL
USER_PREFERENCE
```

Un `REGULATORY_RULE` proveniente del RNE puede tener `authority_level=LEGAL`, pero solo después de verificar versión, vigencia, jurisdicción, alcance e interpretación. Un patrón de Alexander normalmente tendrá `THEORETICAL` o `HEURISTIC`. Una descripción de Ching sobre forma, espacio u orden no se convierte en regla legal.

## 9. Entidad DesignPattern

### 9.1 Propósito

`DesignPattern` modela un problema recurrente de diseño y una familia de respuestas posibles bajo condiciones explícitas.

No representa una solución única ni una plantilla obligatoria. Representa una estructura de razonamiento que puede generar alternativas.

### 9.2 Campos canónicos

| Campo | Tipo | Requisito | Descripción |
|---|---|---:|---|
| `pattern_id` | string | Sí | Identificador estable |
| `source_ids` | array[string] | Sí | Fuentes del patrón |
| `name` | string | Sí | Nombre del patrón |
| `problem` | object | Sí | Problema que aborda |
| `context` | array[string] | Sí | Condiciones de uso |
| `forces` | array[string] | Sí | Tensiones que debe equilibrar |
| `solution_family` | object | Sí | Respuesta general propuesta |
| `consequences` | object | Sí | Efectos positivos y negativos |
| `applicable_scales` | array[SpatialScope] | Sí | Escalas compatibles |
| `applicable_typologies` | array[string] | No | Tipologías compatibles |
| `parameters` | object | No | Parámetros variables |
| `inputs` | array[string] | Sí | Información requerida |
| `outputs` | array[string] | Sí | Resultados generables |
| `positive_indicators` | array[string] | No | Indicadores favorables |
| `negative_indicators` | array[string] | No | Señales de riesgo |
| `regulatory_dependencies` | array[string] | No | Reglas que deben verificarse |
| `review_status` | enum | Sí | Estado de revisión |
| `version` | integer | Sí | Versión del patrón |

### 9.3 Patrón, norma y preferencia

El patrón debe conservar tres fronteras:

```text
Pattern ≠ Regulation
Pattern ≠ UserPreference
Pattern ≠ Decision
```

Un patrón puede sugerir una estrategia. Una norma puede limitarla. Una preferencia puede priorizarla. La decisión final continúa siendo humana.

## 10. Integración de Alexander y Ching

### 10.1 Alexander

Las referencias a Alexander se incorporarán inicialmente como conocimiento teórico y heurístico sobre patrones y relaciones multiescalares.

Un patrón inspirado en Alexander debe registrar:

- Fuente bibliográfica.
- Ubicación de la referencia.
- Problema de diseño.
- Contexto.
- Fuerzas en conflicto.
- Solución como familia de configuraciones.
- Consecuencias.
- Escalas compatibles.
- Límites culturales, climáticos y tipológicos.
- Estado de revisión.

Ejemplo conceptual:

```yaml
pattern_id: PATTERN-PUBLIC-PRIVATE-GRADIENT-001
name: Gradiente público-privado
source_ids:
  - BOOK-ALEXANDER-PATTERN-LANGUAGE
item_type: PATTERN_REFERENCE
applicable_scales:
  - DISTRITO_CIUDAD
  - ZONA_BARRIO_SECTOR
  - EDIFICACION
  - ESPACIO
authority_level: THEORETICAL
legal_effect: false
inputs:
  - access_points
  - user_groups
  - public_private_program
outputs:
  - access_hierarchy
  - transition_sequence
  - privacy_gradient
review_status: UNDER_REVIEW
```

El sistema no debe presentar este patrón como requisito universal ni como una transcripción completa de la obra.

### 10.2 Ching

Las referencias a Ching pueden estructurarse como principios y relaciones de forma, espacio y orden:

```text
AXIS
HIERARCHY
DATUM
RHYTHM
TRANSFORMATION
SYMMETRY
CENTER
BOUNDARY
PATH
THRESHOLD
MASS_VOID
```

Cada unidad debe declarar si es una relación conceptual, un criterio de evaluación o una instrucción de generación. No debe generar dimensiones obligatorias sin una fuente técnica o normativa independiente.

Ejemplo:

```yaml
knowledge_item_id: ITEM-CHING-SPATIAL-HIERARCHY-001
source_id: BOOK-CHING-FORM-SPACE-ORDER
item_type: DESIGN_PRINCIPLE
statement: La jerarquía espacial puede expresarse mediante diferencias de posición, escala, luz, forma o accesibilidad.
authority_level: THEORETICAL
applicable_scales:
  - EDIFICACION
  - ESPACIO
  - OBJETO
criteria:
  - spatial_legibility
  - wayfinding
review_status: UNDER_REVIEW
```

## 11. Integración con el corpus normativo peruano

### 11.1 Separación de capas

El RNE y el conocimiento teórico deben vivir en capas relacionadas, pero no equivalentes:

```text
Corpus normativo peruano
  → Regulation
  → NormativeInterpretation
  → NormativeSnapshot
  → Constraint candidate

Corpus de diseño
  → DesignKnowledgeItem
  → DesignPattern
  → DesignPrinciple
  → Evaluation criterion
```

Una alternativa puede utilizar ambos corpus, pero debe conservar de forma separada qué parte es obligación, qué parte es recomendación técnica y qué parte es heurística.

### 11.2 Prioridad de resolución

Cuando existen conflictos, el agente debe aplicar esta prioridad provisional:

1. Norma oficial vigente y aplicable.
2. Instrumento municipal o territorial vigente y aplicable.
3. Evidencia física o factual del proyecto.
4. Guía técnica oficial.
5. Estándar o manual profesional.
6. Principio teórico.
7. Patrón heurístico.
8. Preferencia del usuario.

Esta prioridad no elimina la necesidad de revisar conflictos. Solo ordena la detección y la explicación.

### 11.3 Estado normativo

El agente debe distinguir:

```text
VIGENTE
MODIFICADA
DEROGADA
NO_VERIFICADA
APPLICABILITY_UNKNOWN
CONFLICTING
```

Una norma `NO_VERIFICADA` no puede producir una restricción dura automáticamente. Una norma `MODIFICADA` requiere identificar el texto aplicable y, cuando corresponda, régimen transitorio.

### 11.4 Ejemplo E.030

Si el proyecto utiliza E.030, el agente debe recuperar:

- La versión histórica registrada.
- Las resoluciones modificatorias.
- El texto técnico asociado.
- El estado de vigencia.
- El régimen transitorio.
- La jurisdicción.
- La fecha del proyecto.

El agente no debe concluir simplemente “cumple E.030”. Debe producir una matriz de aplicabilidad y preguntas pendientes.

## 12. Las once escalas espaciales

El proceso de diseño es común, pero las unidades de conocimiento se filtran por escala.

| Escala | Pregunta de diseño | Fuentes dominantes | Resultados típicos |
|---|---|---|---|
| `PAIS` | ¿Qué estructura territorial y política orienta el proyecto? | Planes nacionales, políticas, teoría territorial | estrategias, objetivos, escenarios |
| `MACRO_REGION` | ¿Qué sistemas interregionales condicionan el diseño? | planificación regional, ecología, movilidad | relaciones, corredores, escenarios |
| `REGION` | ¿Qué clima, economía y territorio organizan el problema? | plan regional, clima, paisaje | estrategias territoriales |
| `PROVINCIA_METROPOLI` | ¿Qué estructura metropolitana debe coordinarse? | plan metropolitano, movilidad, infraestructura | centralidades, redes, conectividad |
| `DISTRITO_CIUDAD` | ¿Qué estructura urbana debe reforzarse? | plan urbano, teoría urbana, datos de uso | tejidos, bordes, densidades |
| `ZONA_BARRIO_SECTOR` | ¿Qué relaciones sociales y espaciales organizan el tejido? | participación, patrones urbanos, instrumentos locales | secuencias, espacios públicos, actores |
| `PARCELA_SITIO` | ¿Qué condiciones específicas del lugar existen? | observación, topografía, normativa, clima | implantación, accesos, orientación |
| `EDIFICACION` | ¿Cómo se organiza el edificio? | RNE, tipologías, patrones, estructura | programa, envolvente, volumetría |
| `SISTEMA` | ¿Cómo se integran estructura e instalaciones? | E.030, E.060, IS.010, EM.010, manuales | sistemas, compatibilización, riesgos |
| `ESPACIO` | ¿Cómo se experimenta y opera el espacio? | Ching, Unwin, Pallasmaa, ergonomía | recorridos, jerarquías, confort |
| `OBJETO` | ¿Cómo se resuelve el componente material? | detalle, materiales, accesibilidad, fabricación | componentes, prototipos, especificaciones |

Una unidad puede aplicarse a varias escalas, pero debe declarar si cambia de significado al escalarse. Un patrón urbano no debe trasladarse a un objeto sin una transformación explícita.

## 13. Gramática universal de diseño

### 13.1 Etapas

El flujo común para todas las escalas es:

```text
1. Inicializar Project y escala
2. Definir tipología y jurisdicción
3. Capturar contexto
4. Registrar Facts
5. Registrar Assumptions
6. Registrar Preferences
7. Identificar Actors
8. Definir Objectives
9. Definir Constraints
10. Recuperar normativa aplicable
11. Recuperar conocimiento de diseño
12. Formular Design Questions
13. Seleccionar Principles y Patterns
14. Construir Design Strategy
15. Generar Alternatives
16. Evaluar alternativas
17. Evaluar Factibilidad
18. Analizar conflictos y trade-offs
19. Emitir Recommendation
20. Ejecutar HumanReview
21. Registrar Decision, si corresponde
22. Registrar Event y auditar
```

### 13.2 Variación por escala

Las etapas no cambian. Cambian los inputs, las fuentes, los agentes, los parámetros y los criterios.

Un proyecto de ciudad puede utilizar conectividad, densidad y centralidad. Un proyecto de espacio puede utilizar proporción, luz, recorrido y materialidad. Ambos siguen el mismo flujo epistemológico.

## 14. Agente de Conocimiento de Diseño

### 14.1 Propósito

El Agente de Conocimiento de Diseño recupera y organiza conocimiento aplicable al problema. Su función es apoyar la formulación de estrategias y la generación o evaluación de alternativas.

No es un agente de autoridad. No aprueba normas, no certifica cumplimiento y no registra decisiones.

### 14.2 Entradas

El agente recibe un `DesignKnowledgeQuery` compuesto por:

```text
project_id
spatial_scope
parent_scopes
child_scopes
typology
jurisdiction
time_horizon
objectives
constraints
facts
assumptions
preferences
site_observations
actor_positions
requested_operation
```

`requested_operation` puede ser:

```text
PROBLEM_FRAMING
KNOWLEDGE_RETRIEVAL
PATTERN_SELECTION
STRATEGY_FORMULATION
ALTERNATIVE_EXPLANATION
EVALUATION_CRITERIA
CONFLICT_ANALYSIS
MISSING_INFORMATION
```

### 14.3 Salidas

El agente devuelve un `DesignKnowledgeResponse` con:

```text
query_id
applicable_items
applicable_patterns
normative_references
scale_relations
conflicts
assumptions
missing_inputs
suggested_questions
rationale
source_ids
evidence_ids
confidence
review_state
```

El agente debe distinguir entre:

```text
FACT
ASSUMPTION
PREFERENCE
NORMATIVE_RULE
DESIGN_GUIDANCE
HEURISTIC
UNKNOWN
CONFLICTING
```

### 14.4 Flujo detallado del agente

#### Paso 1 — Validar el contexto

Comprueba que existe escala, tipología o problema. Si faltan datos esenciales, devuelve `INSUFFICIENT_DATA` y formula preguntas. No rellena silenciosamente el contexto.

#### Paso 2 — Construir el perfil de escala

Determina:

- Escala principal.
- Escalas superiores relacionadas.
- Escalas inferiores afectadas.
- Relaciones `ScaleRelation` existentes.
- Tipo de intervención.

#### Paso 3 — Clasificar el problema

Clasifica la consulta en dimensiones como:

```text
territorial
urbana
social
ambiental
espacial
funcional
estructural
sanitaria
eléctrica
económica
temporal
sensorial
```

La clasificación no reemplaza el juicio del usuario. Es una ayuda de recuperación.

#### Paso 4 — Consultar fuentes normativas

Busca en el corpus RNE y en instrumentos aplicables. Para cada resultado informa:

- Código.
- Versión.
- Estado.
- Jurisdicción.
- Fecha.
- Fuente.
- Evidencia.
- Aplicabilidad conocida.
- Incertidumbres.

Si una norma está modificada o no verificada, la respuesta lo declara visiblemente.

#### Paso 5 — Consultar conocimiento de diseño

Busca `DesignKnowledgeItem` y `DesignPattern` por:

- Escala.
- Tipología.
- Problema.
- Objetivos.
- Condiciones.
- Clima.
- Actores.
- Resultados deseados.

La recuperación debe preferir unidades revisadas y limitar resultados fuera de escala.

#### Paso 6 — Comparar norma y heurística

El agente crea una matriz de separación:

| Elemento | Tipo | Autoridad | Aplicación |
|---|---|---|---|
| E.030 | Norma | Legal | Restricción o requisito tras validación |
| Patrón de Alexander | Heurística | Teórica | Estrategia o alternativa |
| Principio de Ching | Teórico | Conceptual | Criterio de composición |
| Preferencia del usuario | Preferencia | Humana | Objetivo o prioridad |

#### Paso 7 — Detectar conflictos

Identifica conflictos entre:

- Escalas.
- Normas.
- Principios.
- Patrones.
- Objetivos.
- Preferencias.
- Datos del sitio.
- Actores.

El agente no resuelve de forma oculta. Devuelve `CONFLICTING` y propone preguntas o rutas de revisión.

#### Paso 8 — Proponer Design Questions

En lugar de saltar directamente a una forma, formula preguntas como:

```text
¿Cómo debe graduarse el acceso público y privado?
¿Qué condición del sitio limita la orientación?
¿Qué exigencias del RNE afectan el sistema estructural?
¿Qué patrón mejora la relación entre recorrido y jerarquía?
¿Qué información municipal falta para evaluar la implantación?
```

#### Paso 9 — Formular estrategia

La estrategia combina principios y restricciones explícitas, pero mantiene su origen:

```text
normative_requirements
design_principles
selected_patterns
site_responses
actor_priorities
assumptions
open_questions
```

#### Paso 10 — Entregar al generador

El agente generador recibe una estrategia y un conjunto de referencias. No recibe una orden implícita de copiar un patrón.

#### Paso 11 — Entregar al evaluador

El agente propone criterios de evaluación, indicando si cada criterio procede de norma, guía, evidencia, teoría o preferencia.

#### Paso 12 — Entregar al crítico

El agente crítico verifica:

- Fuentes usadas.
- Escala correcta.
- Jurisdicción.
- Supuestos.
- Conflictos.
- Reglas normativas no verificadas.
- Aplicaciones fuera de contexto.

#### Paso 13 — Registrar trazabilidad

Cada respuesta se guarda con:

```text
query_id
source_ids
knowledge_item_ids
pattern_ids
evidence_ids
method_version
retrieved_at
response_hash
review_state
```

### 14.5 Estados del agente

```text
READY
INSUFFICIENT_CONTEXT
RETRIEVING
REVIEW_REQUIRED
CONFLICTING
RESPONDED
FAILED
```

## 15. Interacción con el RNE y Alexander/Ching

### 15.1 Caso de uso

Supóngase un proyecto en escala `EDIFICACION` con objetivo de mejorar confort y privacidad.

El agente puede recuperar:

```text
RNE A.010 → condiciones generales de diseño, estado y aplicabilidad
Open-Meteo → temperatura, viento y radiación del sitio
Alexander → gradiente público-privado como patrón heurístico
Ching → jerarquía, eje, recorrido y orden espacial
```

La salida debe separar:

```text
Requisito normativo pendiente de validación
Dato físico observado
Patrón heurístico
Principio teórico
Preferencia del usuario
```

### 15.2 Ejemplo de respuesta esperada

```json
{
  "status": "REVIEW_REQUIRED",
  "scale": "EDIFICACION",
  "normative": [
    {
      "code": "A.010",
      "state": "NO_VERIFICADA",
      "use": "reference_only"
    }
  ],
  "design_knowledge": [
    {
      "id": "PATTERN-PUBLIC-PRIVATE-GRADIENT-001",
      "type": "PATTERN",
      "authority": "THEORETICAL",
      "use": "strategy_candidate"
    },
    {
      "id": "ITEM-CHING-SPATIAL-HIERARCHY-001",
      "type": "DESIGN_PRINCIPLE",
      "authority": "THEORETICAL",
      "use": "evaluation_criterion"
    }
  ],
  "open_questions": [
    "¿Cuál es el parámetro urbanístico municipal aplicable?",
    "¿Qué nivel de privacidad requiere cada grupo de usuarios?"
  ],
  "decision_created": false
}
```

## 16. Integración con generación

Los métodos de generación existentes pueden recibir una estrategia de diseño enriquecida.

### 16.1 Parametric grid

Utiliza parámetros declarados explícitamente. Debe conservar qué parámetros proceden de norma, guía, patrón, evidencia o preferencia.

### 16.2 Pattern variation

Aplica variaciones de un patrón, pero debe registrar:

- Patrón de origen.
- Condiciones que justifican su selección.
- Variaciones generadas.
- Consecuencias esperadas.
- Criterios de descarte.

### 16.3 Evolutionary generation

Puede explorar combinaciones de parámetros, pero cada candidato debe mantener trazabilidad hacia la estrategia, objetivos y restricciones.

### 16.4 LLM-assisted generation

Si se habilita en el futuro, deberá exigir:

- Modelo y versión.
- Prompt o referencia de entrada.
- Fuentes utilizadas.
- Salida estructurada.
- Hash.
- Estado de revisión.
- Prohibición de crear Decision.

## 17. Integración con evaluación y factibilidad

### 17.1 Evaluación

Los criterios pueden incluir:

```text
spatial_legibility
public_private_gradient
thermal_comfort
solar_response
structural_coherence
sanitary_system_compatibility
electrical_system_compatibility
urban_continuity
accessibility
actor_acceptance
```

Cada evaluación debe declarar su fuente.

### 17.2 Factibilidad

El patrón o principio no crea automáticamente una restricción dura. Para utilizar RFC-020 se requiere una regla explícita con:

- Variable.
- Unidad.
- Operador.
- Umbral.
- Fuente.
- Evidencia.
- Estado.
- Actor o autoridad, cuando corresponda.

### 17.3 Pareto

El uso de un criterio teórico puede convertirse en un objetivo analítico, pero la frontera de Pareto no decide por sí misma. El resultado debe mostrar compromisos entre objetivos y restricciones.

## 18. Integración con las once escalas

### 18.1 Propagación de conocimiento

Una unidad recuperada en una escala superior puede informar una escala inferior mediante una relación explícita:

```text
knowledge_item
  INFORMS
scale_relation
  APPLIES_TO
child_scope
```

No debe propagarse como una obligación automática.

### 18.2 Traducción de escala

Cuando un principio se aplica a una escala distinta, el agente debe registrar:

```text
source_scale
target_scale
translation_rule
preserved_meaning
changed_meaning
new_inputs
new_outputs
review_status
```

### 18.3 Conflictos de escala

Ejemplos:

- Una estrategia de densidad metropolitana puede perjudicar confort en el espacio.
- Un requerimiento de seguridad de edificación puede limitar un patrón de apertura urbana.
- Una preferencia de objeto puede contradecir mantenimiento del sistema.

El agente debe mostrar estos conflictos antes de generar una recomendación.

## 19. Proceso editorial y de revisión

### 19.1 Incorporación de fuente

1. Registrar metadatos.
2. Verificar bibliografía o autoridad.
3. Comprobar licencia.
4. Registrar URL o identificador.
5. Asignar clase epistemológica.
6. Crear estado `REGISTERED`.

### 19.2 Extracción de unidades

1. Seleccionar una sección autorizada.
2. Crear unidad atómica.
3. Registrar referencia de página, artículo o sección.
4. Declarar resumen propio o cita autorizada.
5. Asignar escalas y tipologías candidatas.
6. Registrar limitaciones.

### 19.3 Revisión humana

El revisor comprueba:

- Fidelidad al origen.
- No sobreinterpretación.
- Aplicabilidad declarada.
- Separación entre teoría y norma.
- Licencia.
- Traducción.
- Escalas.
- Conflictos.

### 19.4 Aprobación

Una unidad aprobada puede ser recuperada por el agente. La aprobación no garantiza que sea adecuada para cualquier proyecto.

## 20. Seguridad intelectual y derechos de autor

La base debe conservar metadatos y resúmenes autorizados. El sistema debe evitar la reproducción masiva de libros protegidos.

Cada fuente debe tener un estado de licencia. Si el estado es `UNKNOWN` o `LICENSE_REVIEW_REQUIRED`, la fuente puede permanecer en el catálogo bibliográfico, pero sus contenidos no deben ser redistribuidos automáticamente.

## 21. Pruebas y validación

RFC-026 requerirá pruebas de:

- Validación de campos obligatorios.
- Fuentes inexistentes.
- Referencias rotas.
- Aplicación fuera de escala.
- Confusión entre `Regulation` y `DesignPattern`.
- Uso de una norma `NO_VERIFICADA` como restricción dura.
- Propagación de un principio entre escalas.
- Conflictos entre RNE y patrón.
- Reproducibilidad de recuperación.
- Ausencia de Decision creada por el agente.
- Trazabilidad completa de alternativas generadas.

## 22. Piloto inicial propuesto

El piloto no debe comenzar con los 100 libros. Debe comenzar con una selección pequeña:

| Fuente | Uso inicial |
|---|---|
| Christopher Alexander | Patrones y relaciones multiescalares |
| Francis D. K. Ching | Forma, espacio, orden y relaciones espaciales |
| Ernst Neufert | Guía dimensional, no norma |
| Simon Unwin | Lectura de elementos y secuencias arquitectónicas |
| Juhani Pallasmaa | Experiencia corporal y sensorial |
| Jane Jacobs | Vida urbana y diversidad |
| Kevin Lynch | Legibilidad e imagen urbana |
| Jan Gehl | Vida pública y escala peatonal |
| RNE y normas relacionadas | Restricciones y requisitos oficiales |

El piloto debe producir como máximo:

```text
10 DesignPrinciples
10 DesignPatterns
5 DesignMethods
5 EvaluationCriteria
3 Typologies
3 ScaleRelations
```

Cada unidad debe tener revisión humana antes de usarse en generación.

## 23. Criterios de aceptación

RFC-026 podrá pasar de `DRAFT` a `PROPOSED` cuando:

- Las tres entidades estén definidas.
- Se haya aprobado la taxonomía de autoridad.
- Se haya aprobado la separación RNE / teoría / heurística.
- Se haya definido el contrato del Agente de Conocimiento de Diseño.
- Se haya definido la integración con las once escalas.
- Se haya definido el proceso editorial.
- Se haya definido el piloto inicial.
- Se haya definido el control de derechos de autor.

Podrá pasar a `APPROVED` cuando el Product Owner confirme:

- Fuentes iniciales.
- Escalas.
- Taxonomía.
- Estados de revisión.
- Alcance del piloto.
- Autoridad humana responsable.

Podrá pasar a `IMPLEMENTED` cuando exista una implementación probada con trazabilidad completa.

## 24. Limitaciones conocidas

RFC-026 no incorpora todavía los 100 libros del catálogo. El catálogo requiere verificación bibliográfica, clasificación y revisión de licencia.

Los patrones de Alexander y los principios de Ching se tratan inicialmente como conocimiento teórico y heurístico. No son reglas normativas.

La integración del RNE todavía depende del estado de vigencia, las resoluciones modificatorias, el régimen transitorio y la aplicabilidad al proyecto.

El Agente de Conocimiento de Diseño no sustituye el juicio profesional ni la autoridad humana.

## 25. Decisiones pendientes del Product Owner

1. ¿Se aprueba la creación de RFC-026 como RFC formal?
2. ¿Se autoriza el piloto inicial de diez principios y diez patrones?
3. ¿Qué fuentes tienen licencia suficiente para extracción?
4. ¿Quién revisará las unidades de conocimiento?
5. ¿Qué tipologías se priorizan?
6. ¿Qué escalas se implementan primero en el piloto?
7. ¿Qué fuentes peruanas y latinoamericanas deben añadirse al conjunto inicial?
8. ¿Qué estado mínimo se exige antes de usar una unidad en generación?
9. ¿Se permite que una unidad `THEORETICAL` informe objetivos de Pareto?
10. ¿Qué reportes debe firmar la autoridad humana?

## 26. Firma del RFC

**Product Owner:** ____________________________________  
**Fecha:** ____________________________________  
**Decisión:** `DRAFT / PROPOSED / APPROVED / REJECTED`  
**Observaciones:**

__________________________________________________________________

__________________________________________________________________

## References

[1]: https://www.gob.pe/institucion/vivienda/informes-publicaciones/2309793-reglamento-nacional-de-edificaciones-rne "Reglamento Nacional de Edificaciones — Ministerio de Vivienda, Construcción y Saneamiento"

[2]: https://open-meteo.com/ "Open-Meteo API"

[3]: https://www.coachingarquitectos.com/libros-de-arquitectura/ "Libros de arquitectura — fuente bibliográfica suministrada para el catálogo inicial"
