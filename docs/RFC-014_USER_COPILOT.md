# RFC-014 — User Copilot

**Estado:** DEFINITION ONLY — NO IMPLEMENTATION  
**Sistema:** SiMS-DeI 2.1  
**Lenguaje formal:** SICL — Spatial Intelligence Command Language  
**Baseline:** `main@006ee1a8678c5f4c4e96f5c2524e107c134c05f4`  
**Rama:** `docs/rfc-014-user-copilot`  
**Fecha:** 15 de septiembre de 2026

## 1. Propósito

Este RFC define el contrato conceptual y operativo futuro del User Copilot de SiMS-DeI. El documento no implementa entidades, endpoints, modelos de lenguaje, componentes de interfaz ni infraestructura. Su función es establecer límites verificables antes de cualquier decisión de implementación.

El User Copilot será una capa de interpretación y explicación situada entre la persona usuaria y SICL. No será una autoridad del proyecto. No sustituirá el Core, el registro de eventos, la revisión humana ni la decisión humana.

El Copilot podrá ayudar a comprender el estado de un proyecto y a preparar acciones posibles. Toda acción que modifique el estado canónico deberá continuar pasando por los mecanismos formales de SICL y por la autorización humana que corresponda.

## 2. Alcance

El alcance futuro incluye tres niveles progresivos de capacidad. El Nivel 1 utiliza reglas deterministas. El Nivel 2 traduce lenguaje natural a comandos SICL propuestos. El Nivel 3 añade conversación controlada mediante un modelo de lenguaje.

Los niveles son acumulativos en capacidad, pero no deben confundirse con niveles de autoridad. Ningún nivel puede registrar una Decision por sí mismo. Ningún nivel puede transformar una Recommendation en una Decision. Ningún nivel puede convertir una Assumption en un Fact sin evidencia nueva y evento auditable.

El RFC también define cuatro entidades propuestas: `CopilotSession`, `CopilotMessage`, `CopilotSuggestion` y `CopilotExplanation`. Estas entidades son contractuales y no forman parte del Core implementado por SICL 2.1.

## 3. Filosofía: el Compañero, no el Oráculo

La regla central es: **el Copilot es el Compañero, no el Oráculo**.

Un compañero ayuda a leer, ordenar, traducir e ilustrar información. No reclama autoridad sobre el proyecto. No presenta sus inferencias como hechos. No oculta incertidumbre. No ejecuta cambios irreversibles sin una confirmación explícita.

Un oráculo implicaría que el sistema conoce la respuesta correcta y puede imponerla. Ese modelo es incompatible con la autoridad humana, con la distinción Fact/Assumption y con la separación Recommendation/Decision. Por tanto, queda excluido de este RFC.

El Copilot debe declarar qué está haciendo en cada respuesta. Puede traducir una intención, explicar una entidad, identificar una carencia o proponer un siguiente paso. Debe distinguir entre datos recuperados, reglas aplicadas, sugerencias y decisiones humanas registradas.

## 4. Principios de diseño

### 4.1 Autoridad humana

La autoridad decisional permanece en actores humanos autorizados. El Copilot puede solicitar una confirmación, pero no puede emitirla en nombre del usuario.

### 4.2 Trazabilidad

Cada sugerencia, explicación o diagnóstico debe poder relacionarse con la sesión, el proyecto, la entrada recibida, las fuentes consultadas y la versión de las reglas o del modelo utilizado.

### 4.3 Incertidumbre explícita

La ausencia de información debe producir un estado explícito. El Copilot no debe rellenar silenciosamente un dato faltante.

### 4.4 Separación epistemológica

Un Fact es información registrada como hecho verificable dentro del contrato vigente. Una Assumption es una hipótesis o premisa de trabajo. El Copilot debe conservar la diferencia en sus mensajes y estructuras futuras.

### 4.5 Separación de funciones

Explicar no es recomendar. Recomendar no es decidir. Traducir no es ejecutar. Estas diferencias deben permanecer visibles para el usuario.

### 4.6 Reversibilidad

Las operaciones de consulta, explicación y propuesta deben ser reversibles y no mutar el estado canónico. Las operaciones de ejecución requerirán confirmación y trazabilidad.

### 4.7 Minimización de datos

Una futura implementación debe utilizar solamente los datos necesarios para la sesión y el proyecto. No debe almacenar conversaciones indefinidamente por defecto.

### 4.8 Transparencia del proveedor

Si una respuesta utiliza un LLM, el sistema debe declararlo. Si utiliza reglas deterministas, debe declararlo. Si combina ambos mecanismos, debe identificar la contribución de cada uno.

## 5. Niveles del User Copilot

### 5.1 Nivel 1 — Sistema experto basado en reglas

El Nivel 1 es un sistema determinista. No utiliza LLM. Examina el snapshot, los eventos, los estados de conocimiento y las reglas aprobadas por SICL.

Su finalidad es explicar el estado actual, detectar insuficiencias y señalar próximos pasos posibles. Puede identificar que falta una Preference, que existe una Assumption sin respaldo suficiente o que dos fuentes presentan valores conflictivos.

El Nivel 1 no genera texto libre dependiente de un modelo probabilístico. Sus mensajes deben derivarse de reglas versionadas y de plantillas verificables.

El Nivel 1 puede explicar entidades del proyecto. Por ejemplo, puede describir qué significa una Constraint, qué fuente respalda un Evidence o qué autoridad se requiere para una Decision.

El Nivel 1 puede sugerir un próximo paso operativo. La sugerencia debe ser informativa y no debe ejecutar el paso.

### 5.2 Nivel 2 — Traductor de lenguaje natural a comandos SICL

El Nivel 2 recibe una intención expresada en lenguaje natural y produce un comando SICL propuesto. El comando es una representación formal de una posible acción, no una acción ejecutada.

El usuario debe poder inspeccionar el comando antes de confirmarlo. La confirmación debe ser explícita y asociarse al actor humano que la emitió.

El traductor puede utilizar un parser basado en reglas. También puede utilizar un LLM, pero debe indicarlo en la respuesta y registrar el proveedor o modelo conforme a la política que se apruebe.

Un comando ambiguo no debe ejecutarse. El traductor debe pedir aclaración cuando falte el proyecto, la entidad, el valor, la autoridad o cualquier otro dato requerido por el contrato SICL.

Un comando que produciría una Decision debe mostrar que requiere actor, authority y HumanReview cuando el Core lo exija. El traductor nunca puede completar esos campos por inferencia silenciosa.

### 5.3 Nivel 3 — Asistente conversacional con LLM controlado

El Nivel 3 permite una interacción conversacional más flexible. Puede resumir el estado del proyecto, explicar relaciones entre entidades y comparar interpretaciones disponibles.

El Nivel 3 seguirá siendo una capa propuesta. No tendrá autoridad para modificar el Core directamente. Sus salidas deberán diferenciar hechos recuperados, contexto aportado por el usuario, inferencias y propuestas.

El proveedor o modelo del Nivel 3 deberá ser una decisión explícita del Product Owner. Las alternativas pueden incluir un modelo local, como Llama o Mistral, o un proveedor de API. Esta elección no queda resuelta por este RFC.

El Nivel 3 deberá incorporar límites de contexto, protección de secretos, control de acceso, retención definida y mecanismos de evaluación. No se autoriza asumir que una conversación es una fuente normativa o una evidencia verificable.

## 6. Entidades propuestas

### 6.1 CopilotSession

`CopilotSession` representa una sesión de interacción entre un actor y el Copilot dentro de un proyecto.

Campos conceptuales mínimos:

- `session_id`.
- `project_id`.
- `actor_id`.
- `copilot_level`.
- `provider`.
- `model`.
- `status`.
- `created_at`.
- `closed_at`.
- `contract_version`.

Una sesión debe estar vinculada a un actor autenticado. No debe confundirse con una sesión de usuario de la plataforma ni con una sesión de decisión.

### 6.2 CopilotMessage

`CopilotMessage` representa una entrada o salida individual de una sesión.

Campos conceptuales mínimos:

- `message_id`.
- `session_id`.
- `direction`.
- `content`.
- `created_at`.
- `source_type`.
- `source_refs`.
- `model_metadata`.
- `status`.

Las entradas del usuario y las respuestas del Copilot deben distinguirse. El contenido generado no debe convertirse automáticamente en Fact, Assumption, Evidence ni Decision.

### 6.3 CopilotSuggestion

`CopilotSuggestion` representa una acción, interpretación o siguiente paso propuesto.

Campos conceptuales mínimos:

- `suggestion_id`.
- `session_id`.
- `project_id`.
- `kind`.
- `description`.
- `proposed_command`.
- `source_refs`.
- `confidence`.
- `requires_confirmation`.
- `status`.
- `created_at`.
- `confirmed_by`.
- `confirmed_at`.

Una sugerencia no es una Recommendation de SICL. El nombre y el contrato deben evitar que ambas entidades se confundan.

### 6.4 CopilotExplanation

`CopilotExplanation` representa una explicación orientada a comprensión humana.

Campos conceptuales mínimos:

- `explanation_id`.
- `session_id`.
- `subject_type`.
- `subject_id`.
- `text`.
- `source_refs`.
- `rule_refs`.
- `uncertainty`.
- `created_at`.

Una explicación debe poder indicar por qué no puede concluir algo. Una respuesta incompleta o conflictiva debe conservar ese estado.

## 7. Endpoints REST propuestos

Los siguientes endpoints son únicamente propuestos. Este RFC no los implementa.

- `POST /v1/copilot/sessions` crea una sesión propuesta.
- `GET /v1/copilot/sessions/{id}` recupera el estado de una sesión.
- `POST /v1/copilot/sessions/{id}/messages` registra o procesa un mensaje.
- `GET /v1/copilot/sessions/{id}/messages` recupera los mensajes autorizados.
- `POST /v1/copilot/suggest` genera una sugerencia no ejecutada.
- `POST /v1/copilot/explain` genera una explicación trazable.
- `POST /v1/copilot/diagnose` identifica estados insuficientes, desconocidos o conflictivos.

Toda futura superficie REST deberá conservar autenticación server-side, control de acceso por proyecto y trazabilidad de fuentes. Los endpoints no deben crear una ruta paralela que evite los comandos o las reglas del Core.

El endpoint de sugerencias debe devolver una propuesta distinguible de una Recommendation. El endpoint de explicación debe devolver fuentes y límites. El endpoint de diagnóstico debe devolver estados y causas, no decisiones.

## 8. Invariantes críticas

### INV-COP-001 — El Copilot no decide

El Copilot no puede crear, aprobar ni registrar una Decision. Una Decision solo puede registrarse mediante el mecanismo canónico y con la autoridad humana requerida.

### INV-COP-002 — El Copilot no recomienda

El Copilot no produce una Recommendation de SICL. Puede producir una `CopilotSuggestion`, que es una propuesta de interacción y no una recomendación del dominio.

### INV-COP-003 — El Copilot no ejecuta sin confirmación

Un comando traducido o sugerido nunca se ejecuta automáticamente. La confirmación debe ser explícita, atribuible y previa a la ejecución.

### INV-COP-004 — El Copilot no afirma sin fuente

Toda afirmación factual debe citar sus fuentes o indicar que no dispone de una fuente. El texto generado no es fuente por sí mismo.

### INV-COP-005 — El Copilot no infiere datos faltantes

Cuando falte un dato, el Copilot debe declarar la ausencia y pedirlo o sugerir cómo obtenerlo. No puede completar el dato silenciosamente.

### INV-COP-006 — Las sugerencias citan fuentes

Toda `CopilotSuggestion` debe incluir referencias de fuente, reglas o contexto. Una sugerencia sin trazabilidad debe marcarse como inválida o incompleta.

### INV-COP-007 — B-001 permanece vigente

La distinción Fact/Assumption, los estados UNKNOWN y CONFLICTING y la transición auditable por nueva evidencia no pueden relajarse por interacción conversacional.

### INV-COP-008 — Recommendation no es Decision

El Copilot debe mostrar ambas entidades como conceptos distintos. No puede presentar una Recommendation como decisión adoptada.

### INV-COP-009 — HumanReview conserva su función

Cuando el Core requiera HumanReview, una respuesta del Copilot no puede sustituirla. El usuario debe realizar la revisión formal.

### INV-COP-010 — Los eventos son trazables

Toda confirmación o ejecución futura debe producir los eventos canónicos correspondientes. La conversación no puede reemplazar el event log.

## 9. Contrato del Nivel 1

El sistema experto debe utilizar reglas deterministas, versionadas y verificables. Cada regla debe tener un identificador estable y una explicación legible.

Debe detectar `INSUFFICIENT`, `UNKNOWN` y `CONFLICTING`. Estos estados deben derivarse de entradas observables y no de una intuición del sistema.

Debe sugerir un próximo paso sin ejecutarlo. El próximo paso puede ser registrar una fuente, solicitar una revisión humana, resolver un conflicto o completar un campo requerido.

Debe explicar cada entidad usando el contrato de SICL. La explicación debe distinguir estado, versión, fuente y autoridad.

No debe usar LLM. Si una futura implementación combina el Nivel 1 con otro nivel, deberá indicar qué salida proviene de reglas y cuál proviene del traductor o asistente.

## 10. Contrato del Nivel 2

El traductor debe convertir lenguaje natural en una representación SICL propuesta. Debe preservar identificadores, valores, unidades y relaciones.

Debe mostrar el comando antes de ejecutarlo. El usuario debe poder corregirlo, cancelarlo o confirmarlo.

Debe detectar ambigüedad. Una frase como “elige la mejor opción” no es suficiente para registrar una Decision y debe generar una solicitud de aclaración.

Puede utilizar un LLM o un parser de reglas. Si utiliza un LLM, debe declararlo, conservar metadata mínima y aplicar controles de proveedor.

El traductor debe rechazar comandos que violen el Core Contract. No debe convertir lenguaje persuasivo en autoridad.

## 11. Contrato del Nivel 3

El asistente debe operar con un LLM controlado, límites de contexto y una política de fuentes.

Debe separar respuestas de consulta, explicaciones y propuestas. Cada una debe tener un tipo explícito.

Debe citar las fuentes utilizadas y declarar cuando no pueda verificarlas. No puede presentar una probabilidad lingüística como evidencia.

Debe proponer, no ejecutar. Una confirmación humana debe iniciar cualquier operación mutante y debe pasar por el Core.

Puede ejecutarse con un modelo local, como Llama o Mistral, o mediante una API. La selección del proveedor requiere una decisión específica del Product Owner.

## 12. Riesgos

El primer riesgo es la alucinación. Un LLM puede producir una afirmación plausible que no tenga respaldo.

El segundo riesgo es la violación de B-001. Una conversación puede borrar la diferencia entre hecho, supuesto, desconocido y conflictivo.

El tercer riesgo es la dependencia de terceros. Un proveedor externo puede cambiar el modelo, el precio, la disponibilidad o las políticas de retención.

El cuarto riesgo es el coste. El uso de una API puede generar costes variables por volumen, contexto y reintentos.

El quinto riesgo es la fuga de información. Una implementación incorrecta podría enviar tokens, datos privados o información de proyectos a un proveedor no autorizado.

El sexto riesgo es la autoridad implícita. Un texto con tono seguro podría interpretarse como una decisión aunque el sistema no la haya registrado.

## 13. Mitigaciones

La confirmación humana obligatoria evita la ejecución silenciosa. Debe existir antes de cualquier comando mutante.

Las citas de fuente obligatorias reducen afirmaciones sin respaldo. La ausencia de fuente debe ser visible.

Los logs de cada sugerencia permiten reconstruir qué se propuso y bajo qué contexto.

Los tests de alucinación deben verificar que el sistema no inventa datos, fuentes, autoridades ni resultados.

Una opción local puede reducir dependencia externa y facilitar el control de datos, aunque no elimina el riesgo de alucinación.

La protección server-side debe impedir que el navegador reciba tokens de proveedores o del Core.

Los límites de permisos deben impedir que una sesión consulte proyectos que el actor no puede ver.

La evaluación humana debe permanecer disponible para corregir o descartar una sugerencia.

## 14. Qué no implementa este RFC

Este RFC no crea ninguna entidad en el dominio ejecutable.

Este RFC no crea ningún endpoint REST.

Este RFC no integra ningún LLM.

Este RFC no modifica el Core Contract ejecutable.

Este RFC no modifica `main`, el frontend, SQLite ni la infraestructura.

Este RFC no crea una Recommendation.

Este RFC no crea una Decision.

Este RFC no crea HumanReview.

Este RFC no autoriza la apertura de una sesión de Copilot en producción.

## 15. Fases de implementación propuestas

### Fase A — Sistema experto

La Fase A implementaría únicamente reglas deterministas de lectura y explicación. Incluiría diagnóstico de estados y sugerencias de próximos pasos.

La aceptación exigiría pruebas de estados UNKNOWN, CONFLICTING e INSUFFICIENT. También exigiría demostrar que ninguna consulta muta el proyecto.

### Fase B — Traductor

La Fase B añadiría la traducción controlada de lenguaje natural a comandos SICL propuestos.

La aceptación exigiría mostrar el comando antes de ejecutarlo, exigir confirmación humana y probar ambigüedad, cancelación y rechazo de comandos inválidos.

### Fase C — Conversacional

La Fase C añadiría el asistente con LLM controlado después de resolver proveedor, retención, privacidad, costes y evaluación.

La aceptación exigiría pruebas de citas, ausencia de secretos, abstención ante datos faltantes y preservación de la autoridad humana.

## 16. Gobernanza y decisiones pendientes

Este RFC no decide el proveedor del Nivel 3. Esa elección queda pendiente del Product Owner.

Este RFC no decide la política final de retención de mensajes. Debe definirse antes de cualquier uso productivo.

Este RFC no decide si el Copilot tendrá acceso a todos los proyectos o a un subconjunto autorizado. La política de autorización debe ser explícita.

Este RFC no decide si las sugerencias se conservarán como artefactos auditables por defecto. La decisión deberá considerar privacidad y trazabilidad.

El Product Owner deberá aprobar cada fase de implementación por separado. La aprobación documental de este RFC no autoriza código.

## 17. Criterios de aceptación futuros

Una futura implementación debe demostrar que una conversación no puede crear una Decision automáticamente.

Debe demostrar que una Recommendation nunca aparece como Decision.

Debe demostrar que los comandos propuestos pueden inspeccionarse antes de confirmarse.

Debe demostrar que una fuente ausente produce una respuesta de incertidumbre y no una afirmación inventada.

Debe demostrar que el navegador no recibe secretos server-side.

Debe demostrar que una respuesta del Copilot no sustituye un HumanReview.

Debe demostrar persistencia y trazabilidad según el contrato aprobado para cada entidad que se implemente.

## 18. Referencias

Este RFC se interpreta junto con las decisiones y contratos vigentes de SiMS-DeI y SICL.

[1]: https://github.com/YvanCastilloQuezada/sicl-core/blob/main/docs/SICL_CORE_CONTRACT_v1.0.md "SICL Core Contract v1.0"
[2]: https://github.com/YvanCastilloQuezada/sicl-core/blob/main/docs/SIMS_DEI_MASTER_ARCHITECTURE_v2.md "SiMS-DeI 2.0 Master Architecture"
[3]: https://github.com/YvanCastilloQuezada/sicl-core/blob/main/docs/RFC-011_INSTITUTIONAL_MEMORY.md "RFC-011 Institutional Memory"
[4]: https://github.com/YvanCastilloQuezada/sicl-core/blob/main/docs/RFC-012_MULTI_ACTOR_MODEL.md "RFC-012 Multi-Actor Model"
[5]: https://github.com/YvanCastilloQuezada/sicl-core/blob/main/docs/RFC-013_TEMPORAL_CYCLES.md "RFC-013 Temporal Cycles"

La decisión B-001 y el Decision Register se consideran documentos de gobernanza del proyecto. Este RFC no los reemplaza ni modifica.
