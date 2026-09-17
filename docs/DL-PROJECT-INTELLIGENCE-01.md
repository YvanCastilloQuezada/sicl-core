# Decision Lock — Project Intelligence and Human Intent

**Identificador:** `DL-PROJECT-INTELLIGENCE-01`
**Proyecto:** SiMS-DeI / SICL
**Estado:** `APPROVED / FROZEN`
**Tipo:** Decisión arquitectónica documental
**Alcance:** Compatibilidad arquitectónica para el presente y futuras fases

## 1. Propósito

Este Decision Lock establece cómo SiMS-DeI debe distinguir las diferentes clases de información que entran en un proyecto. Su objetivo es evitar que una observación del mundo, una exigencia externa y una preferencia humana se conviertan accidentalmente en el mismo tipo de estado del proyecto.

La decisión es normativa para la arquitectura futura. No autoriza por sí misma una nueva implementación, una nueva entidad persistente ni un nuevo flujo de inteligencia artificial.

## 2. Tres clases primarias de inteligencia de proyecto

SiMS-DeI debe distinguir tres clases principales de entrada.

### 2.1 REAL_WORLD_CONDITION

`REAL_WORLD_CONDITION` describe lo que existe, ocurre o se observa en el mundo. Incluye, entre otros, clima, radiación solar, lluvia, humedad, viento, temperatura, topografía, suelo, agua, riesgos, infraestructura existente y condiciones espaciales o territoriales.

Estas condiciones no son automáticamente requisitos ni restricciones. Normalmente ingresan mediante las estructuras existentes `Fact`, `Source` y `Evidence`, o mediante otra estructura compatible que conserve su trazabilidad.

Una condición real puede informar un análisis. No puede transformarse silenciosamente en una obligación de diseño.

### 2.2 EXTERNAL_REQUIREMENT

`EXTERNAL_REQUIREMENT` describe aquello que el proyecto debe satisfacer debido a una autoridad o condición externa. Comprende regulación, zonificación, requisitos obligatorios de seguridad, accesibilidad, restricciones ambientales, servidumbres y límites técnicos vinculantes.

La relación normativa debe conservar la siguiente cadena:

```text
External Requirement
        ↓
Source
        ↓
Evidence
        ↓
Applicable Constraint
```

No debe crearse una restricción regulatoria sin autoridad aplicable y evidencia trazable. La existencia de un documento normativo no demuestra por sí sola que una regla sea aplicable a cualquier proyecto o escala.

### 2.3 HUMAN_INTENT

`HUMAN_INTENT` describe lo que un cliente, usuario, actor, comunidad, institución, especialista o autoridad humana quiere, necesita, prefiere, rechaza o propone.

La intención humana puede expresar diferentes roles semánticos:

- `OBJECTIVE`: resultado que se quiere alcanzar.
- `REQUIREMENT`: condición que se considera necesaria.
- `CONSTRAINT`: límite que debe respetarse tras su confirmación.
- `PREFERENCE`: prioridad que orienta la comparación sin ser necesariamente obligatoria.
- `NEGATIVE_PREFERENCE`: resultado que una persona quiere evitar.
- `DESIGN_IDEA`: solución o forma que alguien propone.

No debe asumirse que toda afirmación humana tiene el mismo rol semántico.

## 3. Invariantes constitucionales

La arquitectura debe preservar las siguientes distinciones:

```text
WHAT_EXISTS
    != WHAT_MUST_BE_SATISFIED
    != WHAT_HUMANS_WANT
```

También debe preservar:

```text
CLIENT_NEED        != CLIENT_DESIGN_IDEA
DESIGN_IDEA        != HARD_CONSTRAINT
PREFERENCE         != OBJECTIVE
OBJECTIVE          != CONSTRAINT
```

Estas diferencias son semánticas y no deben resolverse únicamente mediante etiquetas visuales. Cuando una futura implementación proponga una clasificación, la clasificación debe permanecer diferenciada del estado autoritativo confirmado.

## 4. Idea de diseño frente a intención subyacente

SiMS-DeI debe distinguir entre lo que una persona quiere lograr y la solución que actualmente imagina para lograrlo.

Por ejemplo, la afirmación “quiero un patio central” puede descomponerse en una intención subyacente de disponer de un espacio social compartido y una idea de diseño concreta denominada patio central.

La idea concreta no debe bloquear automáticamente alternativas como una terraza, un espacio común lineal, un atrio, una plaza elevada o varios espacios comunes distribuidos. Estas alternativas deben poder evaluarse cuando satisfacen la intención u objetivo subyacente.

La separación permite que el sistema compare soluciones sin invalidar la voz humana. También evita que una primera imagen mental se convierta accidentalmente en una restricción dura.

## 5. Confirmación humana

La futura clasificación asistida por inteligencia artificial o procesamiento de lenguaje natural puede sugerir una interpretación de una afirmación humana. No puede establecer silenciosamente un `Constraint`, `Objective`, `Requirement`, `Preference` o `Decision` autoritativo.

El flujo conceptual aprobado es:

```text
RAW HUMAN STATEMENT
        ↓
SEMANTIC INTERPRETATION
        ↓
SUGGESTED CLASSIFICATION
        ↓
HUMAN CONFIRM / MODIFY
        ↓
PROJECT INTENT MODEL
```

La confirmación humana debe preceder a cualquier efecto que modifique el estado normativo, objetivo, restrictivo o decisional del proyecto. La sugerencia de un agente no equivale a una revisión humana ni a una decisión.

## 6. Aplicación multiescala

La distinción entre condición real, requisito externo e intención humana se aplica a las once escalas espaciales. El proceso canónico permanece estable, pero cambian las variables, la resolución, las fuentes, la evidencia, las normas, los actores y las capacidades aplicables.

```text
SpatialScope
    ↓
Real-World Conditions
+
External Requirements
+
Human Intent
    ↓
Design Problem
    ↓
Objectives / Constraints / Preferences /
Design Variables / Evaluation Criteria
    ↓
Alternatives
    ↓
Analysis
    ↓
Evaluation
    ↓
Trade-offs / Pareto
    ↓
HumanReview
    ↓
Decision
```

No deben crearse once sistemas de intención independientes. Debe existir una arquitectura común con resolución y aplicabilidad adaptadas a cada `SpatialScope`.

## 7. Ejemplo multiescala: dominio WATER

Un mismo dominio no implica que exista una misma variable canónica en todas las escalas. La semántica y la resolución deben comprobarse antes de reutilizar una identidad.

| Escala | Ejemplo de lectura del dominio WATER |
|---|---|
| `objeto` | Exposición a humedad o agua |
| `espacio` | Humedad y condensación |
| `sistema` | Demanda, flujo y drenaje |
| `edificacion` | Consumo, captación de lluvia y drenaje |
| `parcela_sitio` | Escorrentía e infiltración |
| `zona_barrio_sector` | Drenaje urbano |
| `distrito_ciudad` | Infraestructura urbana de agua |
| `provincia_metropoli` | Cuenca, demanda y contexto de red |
| `region` | Disponibilidad de agua |
| `macro_region` | Contexto interregional de cuencas y sistemas |
| `pais` | Seguridad y contexto nacional del agua |

Las identidades canónicas solo deben reutilizarse cuando la semántica realmente coincide. La similitud nominal del dominio no es suficiente.

## 8. Relación con las estructuras actuales

No se crea una segunda arquitectura de estado del proyecto. La futura inteligencia de intención debe integrarse con las estructuras constitucionales existentes cuando sean adecuadas:

`Fact`, `Assumption`, `Objective`, `Constraint`, `Source`, `Evidence`, `SuggestedVariable`, `ProjectVariable`, `Evaluation`, `Recommendation`, `HumanReview` y `Decision`.

Estas estructuras no se reemplazan. La futura capacidad debe aportar interpretación, sugerencias y trazabilidad sin crear una autoridad paralela.

## 9. Relación con Missing Data Intelligence

La inteligencia de datos faltantes debe conservar la diferencia entre incertidumbres semánticamente distintas:

```text
missing environmental fact
    != missing regulatory requirement
    != unresolved human preference
```

Los mensajes futuros deben explicar la causa de la falta de información. Ejemplos válidos son “faltan datos climáticos”, “el límite normativo aplicable aún no está establecido” y “la preferencia del cliente aún no ha sido confirmada”.

No debe presentarse toda ausencia como un único error genérico. Sin embargo, esta decisión no obliga a ampliar el MVP de Missing Data si la distinción todavía no está implementada.

## 10. Capacidad futura reservada

Se reserva el concepto `HUMAN INTENT INTELLIGENCE` como futura capacidad dentro de Guided Project Setup. `CLIENT INTENT` puede existir como subconjunto de `HUMAN INTENT`, porque SiMS-DeI puede incorporar a clientes, arquitectos, usuarios, comunidades, instituciones, especialistas, autoridades y otros actores.

No debe crearse una aplicación separada. La capacidad futura debe integrarse en el flujo del proyecto y conservar las fronteras de autoridad humana.

## 11. Relación con Design Intelligence

El objetivo futuro es conectar afirmaciones humanas con generación y evaluación de alternativas sin confundir una solución propuesta con la intención que la motiva:

```text
HUMAN STATEMENTS
        ↓
Human Intent Intelligence
        ↓
Objectives / Requirements / Constraints /
Preferences / Negative Preferences / Design Ideas
        ↓
Design Intelligence
        ↓
Alternative Generation
        ↓
Evaluation against underlying intent
```

Una alternativa debe poder evaluarse frente a la intención subyacente aunque difiera de la solución inicialmente imaginada por la persona.

## 12. Límites de implementación actuales

Este Decision Lock no autoriza todavía:

- un modelo completo de `Human Intent`;
- una interfaz de entrevista con clientes;
- un clasificador NLP;
- creación automática de restricciones;
- creación automática de objetivos;
- creación automática de decisiones;
- una nueva aplicación de intención humana;
- una modificación del Core Contract;
- una ampliación del alcance B2.

La decisión tampoco retrasa las capacidades ya autorizadas de B2: `SpatialLocation`, `Location Picker` y `Missing Data MVP`.

## 13. Estado y gobernanza

**Estado:** `APPROVED / FROZEN`.

Cualquier implementación futura deberá presentar una especificación propia, indicar qué estructuras actuales reutiliza, identificar qué afirmaciones requieren confirmación humana y demostrar que no convierte ideas de diseño en restricciones duras por defecto.

La clasificación sugerida por un agente debe permanecer auditable. La autoridad humana debe conservar la capacidad de confirmar, modificar o rechazar la interpretación.

## 14. Decisión final

SiMS-DeI distingue formalmente:

1. `REAL_WORLD_CONDITION`.
2. `EXTERNAL_REQUIREMENT`.
3. `HUMAN_INTENT`.

Dentro de `HUMAN_INTENT`, distingue `OBJECTIVE`, `REQUIREMENT`, `CONSTRAINT`, `PREFERENCE`, `NEGATIVE_PREFERENCE` y `DESIGN_IDEA`.

Las ideas de diseño del cliente o de cualquier actor no se convierten automáticamente en restricciones duras. La diferencia entre intención subyacente y solución imaginada debe preservarse. La confirmación humana es obligatoria antes de que una clasificación sugerida se convierta en estado autoritativo del proyecto.

## Referencias

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SiMS-DeI SICL Core repository"

[2]: https://github.com/YvanCastilloQuezada/sicl-core/blob/main/docs/RFC-021_PROJECT_VARIABLES.md "RFC-021 Project Variables"

[3]: https://github.com/YvanCastilloQuezada/sicl-core/blob/main/docs/RFC-022_FRONTEND_GUIDED_INTERFACE.md "RFC-022 Frontend Guided Interface"
