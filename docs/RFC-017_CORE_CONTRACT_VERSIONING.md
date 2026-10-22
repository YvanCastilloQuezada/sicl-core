# RFC-017 — Core Contract Versioning Policy

**Estado:** IMPLEMENTED ON MAIN — política activa; el encabezado histórico DRAFT se conserva en el registro de proceso
**Fecha:** 16 de septiembre de 2026
**Sistema:** SiMS-DeI
**Lenguaje formal:** SICL — Spatial Intelligence Command Language
**Repositorio:** `YvanCastilloQuezada/sicl-core`
**Rama:** `docs/rfc-017-versioning`
**Baseline vigente:** `main@f2c4d205198e6050cdfd50e228e8ba21d3d4c79f`
**Propietario del producto:** Product Owner / arquitecto responsable

## 1. Objetivo

Esta política define cómo evoluciona el Core Contract de SICL sin perder trazabilidad, compatibilidad ni autoridad humana. El Core Contract es la referencia normativa para entidades, invariantes, eventos, persistencia, comandos y superficie HTTP.

La política evita que una modificación de código se interprete como una modificación menor del contrato. Toda capacidad que cambie la interpretación de datos o el comportamiento observable debe declarar su impacto contractual.

El versionado identifica el contrato que un cliente consume. No identifica únicamente la versión del paquete Python ni el número de un commit. Un commit puede implementar varias partes de una versión, y una versión puede requerir más de un commit antes de recibir su tag.

El objetivo operativo es que un cliente pueda responder tres preguntas antes de ejecutar una operación: qué contrato está consumiendo, qué cambios son compatibles y qué acción debe realizar si una capacidad está deprecada.

## 2. Esquema MAJOR.MINOR.PATCH

El Core Contract utiliza tres componentes numéricos: `MAJOR.MINOR.PATCH`.

### 2.1 MAJOR

`MAJOR` aumenta cuando existe un cambio incompatible con clientes, datos, invariantes o semántica contractual anterior.

Se consideran cambios MAJOR:

1. Eliminar o cambiar el significado de una entidad existente.
2. Eliminar un endpoint o comando que un cliente aprobado consume.
3. Cambiar un campo obligatorio de forma que los clientes anteriores ya no puedan enviar datos válidos.
4. Cambiar el tipo o la semántica de un campo sin mantener una representación compatible.
5. Relajar una invariante constitucional de autoridad, trazabilidad, append-only o separación epistemológica.
6. Cambiar la estructura del envelope de forma que un cliente v1 no pueda interpretarlo.
7. Reinterpretar una `Recommendation` como `Decision` o permitir que un agente decida.

Un cambio MAJOR requiere una RFC específica, una estrategia de migración y una decisión explícita del Product Owner.

### 2.2 MINOR

`MINOR` aumenta cuando se añade capacidad compatible hacia atrás.

Se consideran cambios MINOR:

1. Añadir una entidad sin alterar entidades existentes.
2. Añadir un endpoint nuevo que no cambia el comportamiento de endpoints existentes.
3. Añadir un campo opcional con valor por defecto definido.
4. Añadir un comando que no modifica la interpretación de comandos existentes.
5. Añadir un método de simulación, generación o análisis con contrato explícito.
6. Añadir información descriptiva al envelope sin cambiar campos obligatorios existentes.

Una versión MINOR puede requerir actualización de documentación y tests, pero no debe obligar a un cliente compatible a cambiar para conservar su comportamiento anterior.

### 2.3 PATCH

`PATCH` aumenta cuando se corrige un defecto sin modificar el contrato observable.

Se consideran cambios PATCH:

1. Correcciones de validación que implementan una regla ya documentada.
2. Correcciones de serialización que restauran el formato aprobado.
3. Correcciones de errores internos que no cambian estados ni significados.
4. Mejoras de rendimiento sin cambio de resultados contractuales.
5. Correcciones de documentación que no cambian una regla vigente.

Si una corrección cambia lo que un cliente puede aceptar, producir o interpretar, no es PATCH aunque el cambio de código sea pequeño.

## 3. Reglas de incremento

El incremento se decide por impacto contractual, no por tamaño del diff.

Una revisión debe clasificar cada cambio como MAJOR, MINOR o PATCH antes del merge. Si un conjunto contiene cambios de varias clases, se usa la clase de mayor impacto.

El orden de impacto es:

`MAJOR` > `MINOR` > `PATCH`.

Un cambio que modifica una invariante constitucional siempre se trata como MAJOR, salvo que una RFC aprobada demuestre que la invariante se mantiene y solo se amplía su representación.

Un cambio de documentación que describe una capacidad ya implementada no incrementa por sí solo el contrato. Sin embargo, si la documentación corrige una afirmación normativa anterior, debe abrir una RFC o una enmienda contractual.

El número de versión debe aparecer en el documento de contrato, en los artefactos de release y en el envelope HTTP cuando la superficie lo requiera.

El commit de implementación no sustituye el tag de versión. La secuencia aprobada es: RFC, implementación, tests, revisión, merge, tag y publicación.

## 4. Compatibilidad y deprecación

### 4.1 Política de compatibilidad

La compatibilidad hacia atrás significa que un cliente que cumple el contrato anterior puede continuar operando sin reinterpretar silenciosamente sus datos.

La compatibilidad no autoriza a mantener una semántica ambigua. Si una operación anterior producía una autoridad implícita, la corrección debe cerrar esa autoridad y clasificarse por su impacto constitucional.

Las respuestas nuevas deben conservar los campos obligatorios anteriores durante el período de compatibilidad. Los campos añadidos deben ser opcionales, tener un valor por defecto o aparecer en una sección extensible de `data`.

La compatibilidad de datos exige que los registros históricos sigan siendo legibles. No se permite reescribir eventos o decisiones para simular una migración.

### 4.2 Período de gracia

Una capacidad deprecada debe permanecer disponible durante un período de gracia mínimo de una versión MINOR completa o noventa días calendario, lo que sea mayor, salvo un riesgo crítico de seguridad o autoridad.

Durante el período de gracia, el servidor debe aceptar la forma anterior y registrar la advertencia de deprecación cuando sea posible. La forma nueva debe estar documentada antes de iniciar el período.

El período puede ampliarse mediante decisión del Product Owner. La ampliación debe quedar registrada en la RFC, en el changelog y en la documentación del contrato.

Una capacidad marcada como `OBSOLETE` no debe recibir nuevas integraciones. Su retiro requiere un cambio MAJOR o una autorización excepcional documentada.

### 4.3 Anuncio de cambios

Cada cambio debe anunciarse en cuatro lugares cuando corresponda: la RFC, el Core Contract, el changelog del release y la documentación de uso.

El anuncio debe incluir la versión afectada, la fecha efectiva, el impacto, la alternativa recomendada, el período de gracia y la fecha prevista de retiro.

Los mensajes de deprecación deben ser accionables. Deben identificar el endpoint, comando, entidad o campo, indicar su reemplazo y evitar lenguaje ambiguo como “pronto” o “en el futuro”.

## 5. Endpoints

### 5.1 Versionado en URL

La superficie HTTP canónica utiliza el prefijo mayor en la URL: `/v1/...`, `/v2/...`.

El número de versión en la URL identifica la familia compatible del contrato. El envelope puede incluir una versión contractual más precisa, pero no debe contradecir la familia de URL.

Un cambio MINOR o PATCH permanece dentro de `/v1/...` si mantiene compatibilidad. Un cambio MAJOR requiere una nueva familia, por ejemplo `/v2/...`, salvo una decisión explícita que defina una transición distinta.

No se deben crear rutas paralelas con nombres ambiguos para ocultar incompatibilidades. La ruta antigua debe identificarse como activa, deprecada u obsoleta.

### 5.2 Deprecación de endpoints

Para deprecar un endpoint se debe publicar una RFC o una enmienda aprobada que contenga:

1. La ruta y el método HTTP afectados.
2. El motivo de la deprecación.
3. El reemplazo exacto.
4. La fecha de inicio del período de gracia.
5. La fecha prevista de retiro.
6. Las diferencias de request y response.
7. El plan de pruebas y migración.

El endpoint deprecado debe seguir respetando sus invariantes mientras permanezca activo. No se puede convertir en un alias silencioso de otro endpoint si eso cambia su semántica.

### 5.3 Reemplazo de endpoints

Un endpoint de reemplazo debe existir y estar probado antes de anunciar el retiro del endpoint anterior.

El reemplazo debe declarar si conserva los identificadores, versiones, eventos, errores y permisos. Cuando no los conserva, el cambio se clasifica como MAJOR.

La migración debe preferir nuevas escrituras con el endpoint nuevo. Las lecturas históricas deben continuar disponibles mediante la ruta adecuada y no deben duplicar eventos.

## 6. Entidades y campos

### 6.1 Añadir campos

Un campo nuevo debe ser opcional durante la primera versión que lo introduce, salvo que la RFC justifique que el valor es indispensable para preservar una invariante.

Todo campo nuevo debe definir tipo, unidad, valores permitidos, valor por defecto, estado epistemológico cuando corresponda, procedencia y comportamiento de ausencia.

Añadir un campo no autoriza a inferir su valor desde otro campo. La ausencia debe permanecer distinguible de `UNKNOWN`, `INSUFFICIENT` o `CONFLICTING` cuando la ontología lo requiera.

### 6.2 Deprecar campos

Un campo deprecado debe conservarse durante el período de gracia. La respuesta debe documentar su reemplazo y no debe cambiar su significado mientras permanezca activo.

El servidor puede dejar de producir un campo deprecado en una nueva versión MAJOR, pero no debe eliminarlo de eventos históricos ni de registros append-only.

Si el campo contiene autoridad, fuente o trazabilidad, nunca debe eliminarse mediante una migración destructiva. Debe existir una representación histórica legible.

### 6.3 Renombrar campos

Renombrar un campo es un cambio potencialmente incompatible. La forma preferida es introducir el campo nuevo, mantener el anterior como alias durante la gracia y documentar una equivalencia exacta.

El alias no debe aceptar valores contradictorios. Si ambos aparecen en una request, el servidor debe rechazar el conflicto o aplicar una regla documentada y auditable.

Un renombrado que también cambia tipo, unidad o significado se clasifica como MAJOR aunque conserve una ruta de compatibilidad.

### 6.4 Entidades append-only

Las entidades históricas y los eventos no se actualizan ni se eliminan. Una corrección produce una nueva versión o un nuevo evento que explique la corrección.

Las entidades nuevas deben indicar si forman parte del estado canónico, de una proyección, de una recomendación, de una evaluación o de un registro histórico.

Añadir una entidad no permite añadir autoridad implícita. Toda relación con `Decision` debe mantener `HumanReview`, actor y authority cuando sean requeridos.

## 7. Proceso de cambio

### 7.1 RFC obligatorio

Toda modificación de contrato requiere una RFC o una actualización formal de una RFC existente. La RFC debe incluir objetivo, alcance, entidades, endpoints, invariantes, compatibilidad, tests, documentación y clasificación MAJOR/MINOR/PATCH.

Una orden de implementación no reemplaza el análisis de impacto. El análisis debe comprobar Core, persistencia, HTTP, CLI, frontend consumidor y pruebas relevantes.

### 7.2 Aprobación del Product Owner

El Product Owner debe aprobar los cambios que modifiquen semántica, autoridad, entidades canónicas, endpoints públicos o invariantes constitucionales.

La aprobación debe ser explícita y referenciar la RFC. Una aprobación conceptual no autoriza cambios fuera del alcance indicado.

La implementación debe detenerse si una decisión requerida permanece pendiente. No se debe inferir una autorización a partir de silencio.

### 7.3 Verificación antes del merge

Antes del merge se debe ejecutar la suite completa, la compilación, la validación de formato y las pruebas específicas de compatibilidad.

La revisión debe confirmar que `Recommendation != Decision`, que `HumanReview != Decision` y que ningún agente o automatismo adquiere autoridad decisional.

La revisión también debe confirmar que los eventos críticos siguen siendo append-only y que Fact, Assumption, Preference y Evidence no se mezclan por conveniencia.

### 7.4 Tag después del merge

El tag de release se crea después del merge en la rama objetivo y después de completar la verificación sobre el commit exacto que se etiquetará.

El tag debe ser anotado e incluir versión, alcance, RFCs implementadas y resultado de tests. No se debe mover un tag publicado para corregir una discrepancia; se debe crear un tag posterior.

## 8. Estados del contrato

### 8.1 DRAFT

`DRAFT` es una propuesta en discusión. Puede contener alternativas, preguntas abiertas y campos pendientes. No autoriza implementación ni integración como contrato estable.

### 8.2 APPROVED

`APPROVED` significa que el Product Owner aceptó el alcance y las reglas de la RFC. La implementación puede comenzar dentro de los límites aprobados.

`APPROVED` no significa que la capacidad esté desplegada. La implementación debe demostrar tests, documentación y un release identificable.

### 8.3 DEPRECATED

`DEPRECATED` significa que la capacidad sigue disponible por un período de gracia, pero no debe recibir nuevas dependencias. Debe existir un reemplazo o una explicación formal de por qué no existe.

### 8.4 OBSOLETE

`OBSOLETE` significa que la capacidad ya no debe utilizarse. Las lecturas históricas pueden permanecer disponibles si son necesarias para trazabilidad, pero no se deben crear nuevos registros mediante la capacidad obsoleta.

## 9. Ejemplos históricos

### 9.1 De v0.3 a v1.0

La transición de HTTP v0.3 a Core Contract v1.0 separó una superficie operacional previa de un contrato ontológico explícito. La versión v1.0 introdujo persistencia SQLite, entidades Fact y Assumption separadas, eventos append-only y decisiones con actor y authority.

El cambio no debía presentarse como una simple corrección PATCH porque la semántica y las invariantes cambiaron. Un cliente v0.3 requería adaptación, y la superficie compatible debía identificarse por separado.

### 9.2 De v1.0 a v2.0

La transición a v2.0 incorporó el modelo multiescala, el contrato HTTP `/v1/...`, Evidence, Source, Evaluation, Comparison, simulaciones, multiobjetivo, instrumentos de planificación, regulación y relaciones multiescala.

Aunque parte de la superficie utilizó `/v1/...`, el contrato de capacidades se amplió mediante RFCs y releases etiquetados. La compatibilidad se evaluó por capacidad, entidad e invariante, no únicamente por el nombre de la URL.

### 9.3 De v2.0 a v2.2

La transición de v2.0 a v2.2 incorporó generación de diseño, memoria institucional, modelo multi-actor, ciclos temporales, User Copilot, Source HTTP y Monte Carlo. Las capacidades ampliaron el sistema sin permitir que recomendaciones, agentes, memoria o simulaciones tomaran decisiones humanas.

RFC-016.1 añadió `evolutionary_v1` como método activo y dejó `llm_assisted_v1` definido pero no configurado. Esta diferencia ilustra que catalogar una capacidad no equivale a habilitarla.

RFC-013.1 añade evolución de escenarios como entidad append-only. La aplicación registra actor y authority, pero no reescribe ciclos, escenarios ni decisiones históricas.

## 10. Firma y responsabilidad

Este documento define una política de gobierno del Core Contract. No sustituye la aprobación del Product Owner, las RFC específicas ni la revisión técnica del cambio.

La autoridad para decidir el alcance del producto permanece en el Product Owner humano. SICL puede registrar, validar, analizar y explicar; no puede atribuirse la decisión humana.

**Firma del baseline:**

- Product Owner: pendiente de firma formal para pasar de `DRAFT` a `APPROVED`.
- Arquitecto/orquestador: ChatGPT.
- Implementador: Manus AI.
- Revisor independiente: DeepSeek, cuando se solicite.

## 11. Checklist de implementación

Antes de aprobar una nueva versión del contrato, verificar:

- [ ] Existe RFC identificable.
- [ ] La clasificación MAJOR/MINOR/PATCH está justificada.
- [ ] El Product Owner aprobó el alcance.
- [ ] Las entidades nuevas tienen semántica y procedencia definidas.
- [ ] Los cambios de campos tienen estrategia de compatibilidad.
- [ ] Los endpoints deprecados tienen reemplazo y fecha de retiro.
- [ ] Los eventos históricos siguen siendo append-only.
- [ ] Fact, Assumption, Preference, Evidence y Decision permanecen separados.
- [ ] Recommendation no se convierte en Decision.
- [ ] HumanReview precede a Decision cuando el contrato lo exige.
- [ ] La suite completa pasa.
- [ ] La documentación está actualizada.
- [ ] El merge y el tag apuntan a commits identificables.

## Referencias

[1]: https://github.com/YvanCastilloQuezada/sicl-core/blob/main/docs/SICL_CORE_CONTRACT_v1.0.md "SICL Core Contract v1.0"
[2]: https://github.com/YvanCastilloQuezada/sicl-core/blob/main/docs/SIMS_DEI_MASTER_ARCHITECTURE_v2.md "SiMS-DeI Master Architecture v2"
[3]: https://github.com/YvanCastilloQuezada/sicl-core/blob/main/docs/RFC-013_TEMPORAL_CYCLES.md "RFC-013 Temporal Cycles"
[4]: https://github.com/YvanCastilloQuezada/sicl-core/blob/main/docs/RFC-016.1_DESIGN_GENERATION_EXTENDED.md "RFC-016.1 Design Generation Extended"
