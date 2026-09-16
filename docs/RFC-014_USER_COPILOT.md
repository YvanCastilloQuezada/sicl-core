# RFC-014 — User Copilot

**Estado:** DEFINITION ONLY — NO IMPLEMENTATION  
**Sistema:** SiMS-DeI — Sistema de Inteligencia de Diseño Espacial Multiescala  
**Lenguaje formal:** SICL — Spatial Intelligence Command Language  
**Versión:** 2.1  
**Base:** `main@006ee1a8`  
**Rama documental:** `docs/rfc-014-user-copilot-llm`  
**Product Owner:** Usuario / arquitecto  
**Alcance:** contrato conceptual y operativo, sin código

> El Copiloto es un compañero de trabajo, no un oráculo. Puede traducir, explicar e ilustrar; no posee autoridad decisional.

## 1. Objetivo y alcance

RFC-014 define el contrato de un User Copilot para SiMS-DeI. El Copiloto será una capa de interacción que ayude a una persona a comprender el estado del proyecto, formular comandos SICL, identificar información faltante y leer resultados analíticos.

Este RFC establece tres niveles progresivos de capacidad:

1. Un sistema experto basado en reglas deterministas.
2. Un traductor de lenguaje natural a comandos SICL.
3. Un asistente conversacional con un LLM controlado.

Los niveles no cambian las invariantes del Core. Un nivel superior puede mejorar la interacción, pero no obtiene autoridad adicional sobre entidades, eventos, recomendaciones o decisiones.

Este documento define entidades propuestas, endpoints propuestos, límites, riesgos, dependencias, requisitos de operación y fases futuras. No implementa ninguna de estas piezas.

## 2. Qué problema resuelve

Un arquitecto que abre SiMS-DeI debe poder entender qué información ya existe, qué información es desconocida, qué conflictos están abiertos y cuál es el próximo paso útil. La interfaz formal SICL es rigurosa, pero puede exigir conocimiento de sintaxis.

El Copiloto reduce esa fricción sin ocultar la semántica del sistema. Explica el significado de una entidad, sugiere cómo registrar información y muestra el comando que una persona podría confirmar.

El Copiloto también debe ayudar a distinguir:

- un dato observado de una premisa de trabajo;
- una fuente de una afirmación;
- una evaluación de una recomendación;
- una recomendación de una decisión;
- una explicación de una certificación;
- una propuesta de una mutación ejecutada.

## 3. Filosofía: El Compañero, no el Oráculo

### 3.1 Compañero

El Copiloto acompaña el razonamiento del usuario. Puede hacer visible la estructura del proyecto y ayudar a preparar una operación.

El Copiloto debe expresarse con lenguaje claro, pero no debe simplificar hasta borrar distinciones ontológicas. Cuando una respuesta depende de una fuente o de una interpretación, debe decirlo.

### 3.2 No oráculo

El Copiloto no es una autoridad técnica, jurídica, normativa ni decisional. Una respuesta fluida no convierte una hipótesis en un hecho.

El Copiloto no debe presentar una inferencia como observación. No debe completar silenciosamente un campo faltante. No debe afirmar que una alternativa es correcta solo porque una evaluación tiene un valor superior.

### 3.3 Funciones permitidas

El Copiloto puede:

- traducir una pregunta a una explicación del estado del proyecto;
- mostrar entidades y relaciones existentes;
- detectar estados `UNKNOWN`, `CONFLICTING` e `INSUFFICIENT`;
- sugerir el próximo paso operativo;
- proponer un comando SICL para confirmación;
- explicar un comando antes de ejecutarlo;
- citar fuentes relacionadas;
- resumir evaluaciones y trade-offs;
- ayudar a localizar un evento o snapshot;
- explicar por qué una operación fue rechazada.

### 3.4 Funciones prohibidas

El Copiloto no puede decidir por el usuario, crear una decisión, aprobar una interpretación normativa, falsificar una fuente, modificar eventos históricos ni ocultar incertidumbre.

## 4. Tres niveles de Copiloto

### 4.1 Nivel 1 — Sistema experto basado en reglas

El Nivel 1 utiliza reglas deterministas escritas y verificables. No utiliza LLM. Su objetivo es ofrecer ayuda predecible con coste operativo bajo.

Ejemplos de reglas:

- si un proyecto no está abierto, explicar cómo abrirlo;
- si existe una `Assumption` sin `Evidence` asociada, señalar la necesidad de verificación;
- si una evaluación carece de unidad, marcarla como insuficiente para una comparación;
- si una Decision no tiene HumanReview aprobado, bloquear la preparación del comando;
- si dos fuentes son incompatibles, mostrar `CONFLICTING`;
- si un proyecto está `CLOSED`, explicar que no acepta mutaciones.

El Nivel 1 puede explicar entidades y sugerir un próximo paso, pero solo puede ofrecer información derivada de reglas y datos disponibles.

### 4.2 Nivel 2 — Traductor de lenguaje natural a comandos SICL

El Nivel 2 acepta una petición en lenguaje natural y propone una traducción a SICL. La traducción no se ejecuta automáticamente.

Ejemplo:

> Usuario: “Registra que el terreno tiene 2000 metros cuadrados según catastro.”

Propuesta del Copiloto:

```text
/FACT SET SITE_AREA=2000 CATASTRO
```

Antes de presentar el comando, el traductor debe mostrar qué entidad cambiaría, qué evento produciría, qué fuente se registraría y qué campos siguen siendo inciertos.

La persona confirma o rechaza el comando. La confirmación debe ser inequívoca y debe quedar asociada a la operación que finalmente se ejecuta.

El traductor puede usar un parser basado en reglas. También puede usar un modelo estadístico o LLM, pero debe declararlo en la respuesta y someter la salida a validación determinista antes de proponerla.

### 4.3 Nivel 3 — Asistente conversacional con LLM controlado

El Nivel 3 permite una conversación contextual con un modelo de lenguaje. El modelo propuesto para la primera implementación es Phi-3 Mini de 3.8B parámetros, servido mediante Ollama.

El LLM genera texto y propuestas de interacción. No accede directamente a la base de datos sin una capa de control. No ejecuta comandos. No altera el repositorio. No tiene acceso a la autoridad decisional del usuario.

El Nivel 3 debe conservar las reglas del Nivel 1 y el flujo de confirmación del Nivel 2. La mayor expresividad conversacional no cambia las reglas ontológicas.

## 5. Entidades propuestas

Estas entidades son propuestas de RFC-014 y no están implementadas por este RFC.

### 5.1 CopilotSession

Representa una sesión de interacción entre un actor y el Copiloto. Debe identificar el proyecto, el actor, el nivel utilizado, la versión del contrato y el estado de la sesión.

Una sesión debe poder cerrarse y consultarse sin alterar el event log del proyecto de manera implícita. Las interacciones no deben confundirse con decisiones.

### 5.2 CopilotMessage

Representa un mensaje entrante o saliente de la sesión. Debe indicar autor, timestamp, contenido, tipo de mensaje y relación con una operación propuesta.

Los mensajes deben poder diferenciar texto del usuario, respuesta del sistema, explicación, error y confirmación.

### 5.3 CopilotSuggestion

Representa una sugerencia de próximo paso, comando SICL, consulta o fuente. Debe tener un estado que indique si fue presentada, confirmada, rechazada, ejecutada o expirada.

Una sugerencia confirmada no equivale por sí sola a una ejecución. La ejecución debe pasar por el intérprete y producir sus validaciones y eventos normales.

### 5.4 CopilotExplanation

Representa una explicación de una entidad, operación, resultado o error. Debe conservar las referencias que justifican la explicación y declarar sus límites.

Una explicación puede ser útil aunque el estado sea `UNKNOWN` o `INSUFFICIENT`; en ese caso debe explicar precisamente la insuficiencia.

## 6. Endpoints REST propuestos

Los siguientes endpoints son propuestas. No existen como consecuencia de este RFC.

```text
POST /v1/copilot/sessions
GET  /v1/copilot/sessions/{id}
POST /v1/copilot/sessions/{id}/messages
GET  /v1/copilot/sessions/{id}/messages
POST /v1/copilot/suggest
POST /v1/copilot/explain
POST /v1/copilot/diagnose
```

### 6.1 Crear sesión

`POST /v1/copilot/sessions` iniciaría una sesión para un proyecto y actor concretos. La solicitud debería indicar el nivel solicitado y el idioma de interacción.

El Core debe verificar que el proyecto existe y que el actor está autorizado para consultar la información solicitada. Crear una sesión no debe crear una Decision ni una Recommendation.

### 6.2 Mensajes

`POST /v1/copilot/sessions/{id}/messages` recibiría una pregunta o instrucción. La respuesta debería incluir texto, estado epistemológico, fuentes, sugerencias y comandos candidatos, sin ejecutar mutaciones.

`GET /v1/copilot/sessions/{id}/messages` permitiría consultar el historial de conversación con los metadatos de trazabilidad correspondientes.

### 6.3 Sugerencias

`POST /v1/copilot/suggest` solicitaría un próximo paso o un comando candidato. Debe devolver la explicación, las precondiciones, los campos afectados y el texto exacto que requeriría confirmación.

### 6.4 Explicaciones

`POST /v1/copilot/explain` solicitaría una explicación de una entidad, resultado, evento, estado o error. No debe transformar una explicación en evidencia ni crear una entidad.

### 6.5 Diagnóstico

`POST /v1/copilot/diagnose` solicitaría un diagnóstico de bloqueos de flujo. El diagnóstico debe separar hechos observados, supuestos, errores de contrato y próximos pasos sugeridos.

## 7. Invariantes críticas

### INV-COP-001 — No decide

El Copiloto nunca crea ni registra una `Decision`. Solo una operación explícita del Core, con HumanReview aprobado, actor y authority, puede registrar una Decision.

### INV-COP-002 — No recomienda

El Copiloto no debe presentarse como el autor de una `Recommendation`. Puede explicar una Recommendation existente o sugerir que el usuario solicite un análisis, pero no sustituye el módulo analítico.

### INV-COP-003 — No ejecuta sin confirmación

El Copiloto no ejecuta comandos SICL ni mutaciones de proyecto sin una confirmación humana inequívoca. La confirmación debe ocurrir antes de la ejecución, no después.

### INV-COP-004 — No afirma sin fuente

Toda afirmación factual debe citar una Source o indicar explícitamente que proviene de una entrada humana no verificada.

### INV-COP-005 — No infiere datos faltantes

Cuando un campo es desconocido, el Copiloto debe conservar `UNKNOWN` o `INSUFFICIENT`. No debe inventar un valor plausible.

### INV-COP-006 — Cita fuentes

Cada sugerencia que dependa de información del proyecto debe incluir las sources utilizadas, sus estados y el alcance de la inferencia.

### INV-COP-007 — Preserva B-001

Fact y Assumption son entidades epistemológicamente diferentes. Un Copiloto no puede transformar automáticamente una Assumption en Fact.

### INV-COP-008 — Recommendation no es Decision

Una Recommendation puede ser explicada, revisada o rechazada, pero no se convierte en Decision por la existencia de una sugerencia conversacional.

### INV-COP-009 — HumanReview conserva autoridad

Una conversación con el Copiloto no constituye HumanReview. El usuario debe realizar la revisión explícita mediante el mecanismo contractual del Core.

### INV-COP-010 — Eventos append-only

La interacción no puede editar ni eliminar eventos existentes. Las confirmaciones y ejecuciones nuevas deben producir trazabilidad adicional.

### INV-COP-011 — Secretos server-side

El token de servicio, las credenciales del Core y cualquier secreto de Ollama deben permanecer en el servidor. El navegador nunca debe recibirlos.

### INV-COP-012 — No autoridad normativa

El Copiloto no certifica el cumplimiento legal y no puede presentar una interpretación como asesoramiento jurídico profesional.

## 8. Contrato del sistema experto — Nivel 1

### 8.1 Entradas

El sistema experto recibe el snapshot, el historial relevante, el estado de las entidades y las reglas de diagnóstico versionadas.

### 8.2 Salidas

La salida debe contener:

- una descripción del estado observado;
- los estados epistemológicos encontrados;
- las fuentes utilizadas;
- la regla activada;
- el próximo paso sugerido;
- las precondiciones para ese paso;
- una indicación de que no se ejecutó ninguna mutación.

### 8.3 Reglas mínimas

El sistema experto debe detectar `INSUFFICIENT`, `UNKNOWN` y `CONFLICTING`. Debe explicar cada entidad consultada y proponer el próximo paso más pequeño que permita avanzar sin ocultar incertidumbre.

Si una regla no puede justificar su salida con datos presentes en el snapshot, debe devolver una respuesta insuficiente en lugar de completar información.

### 8.4 Sin LLM

El Nivel 1 no utiliza LLM. Es el nivel de referencia para las pruebas de seguridad y para comparar el comportamiento de niveles superiores.

## 9. Contrato del traductor — Nivel 2

### 9.1 Traducción propuesta

El traductor convierte lenguaje natural en una propuesta de comando, nunca en una ejecución silenciosa.

La propuesta debe mostrar:

- texto recibido;
- comando SICL propuesto;
- entidad afectada;
- campos afectados;
- fuentes citadas;
- evento esperado;
- precondiciones;
- advertencias;
- solicitud de confirmación.

### 9.2 Validación

El comando propuesto debe pasar por un parser y por las validaciones del Core antes de ser presentado. El traductor no puede crear una sintaxis privada que evite el intérprete SICL.

### 9.3 Confirmación humana

La interfaz debe pedir una confirmación explícita. Una frase ambigua como “hazlo” solo es válida si el sistema muestra exactamente qué operación está siendo confirmada y no existe más de una operación pendiente.

### 9.4 LLM opcional

El Nivel 2 puede implementarse con reglas, con un LLM o con una combinación. Si se usa un LLM, la respuesta debe declararlo y la salida debe ser validada de forma determinista.

## 10. Contrato del asistente conversacional — Nivel 3

### 10.1 Modelo

El modelo inicial propuesto es **Phi-3 Mini**, versión de aproximadamente 3.8B parámetros. Esta elección es una hipótesis de despliegue y debe validarse empíricamente antes de considerarse una decisión de infraestructura.

### 10.2 Runtime

El runtime propuesto es **Ollama**. Ollama ejecutaría el modelo localmente y ofrecería una interfaz local para el Core.

### 10.3 Host

El host propuesto es un **Mac Pro 2013 con Ubuntu Server 22.04**. La orden de despliegue debe verificar arquitectura, memoria, instrucciones de CPU, disponibilidad de AVX2 y capacidad térmica antes de instalar el modelo.

### 10.4 Topología

```text
Frontend Manus WebDev
        |
        | HTTPS / API protegida
        v
Core SiMS-DeI en Mac Pro
        |
        | llamada server-side local
        v
Ollama en Mac Pro:11434
```

El frontend nunca habla directamente con Ollama. El Core actúa como frontera de seguridad, aplica límites de contexto, valida entradas y filtra salidas.

### 10.5 Ollama local

Ollama escucharía en el puerto local `11434`. La interfaz debe estar restringida al host o a una red privada. No debe publicarse directamente a Internet.

El Core debe llamar a Ollama desde el servidor. El nombre del modelo, los parámetros y el timeout deben ser configuración server-side, no datos controlados libremente por el navegador.

### 10.6 Propuesta, no ejecución

El Nivel 3 genera explicaciones, preguntas y comandos candidatos. No ejecuta comandos. Para ejecutar una operación, el usuario debe revisar el payload exacto y confirmar mediante el mecanismo definido por la aplicación.

### 10.7 Citas y evidencia

La generación conversacional debe recibir únicamente el contexto permitido por el Core y debe devolver referencias a sources. Cuando no exista una fuente, debe responder que no puede afirmar el dato.

Una cita creada por el LLM no es una Source válida. Las sources deben existir o ser registradas por una operación explícita.

### 10.8 Rendimiento esperado

Como hipótesis inicial se espera un rendimiento aproximado de 2 a 5 tokens por segundo en un Xeon E5 v2 equivalente. Este valor no está verificado por RFC-014.

La evaluación debe medir latencia inicial, tokens por segundo, consumo de memoria, temperatura, estabilidad y calidad de respuesta bajo contexto SICL.

### 10.9 Alternativas

Si Phi-3 Mini no alcanza los objetivos, pueden evaluarse Phi-3 Small, Llama 3.2 3B o una API externa como Groq. La sustitución requiere una comparación documentada y una decisión de gobernanza; no es automática.

## 11. Seguridad y límites operativos

El Copiloto debe operar con el mínimo privilegio. Una sesión de explicación puede tener acceso read-only al snapshot. Una propuesta de comando no implica permiso de escritura.

El servidor debe separar credenciales del modelo, token del Core, identidad del usuario y contexto de proyecto. Ninguno debe exponerse en HTML, Local Storage, logs del navegador o payloads innecesarios.

Las entradas del usuario deben tratarse como datos no confiables. Un texto que solicite ignorar el contrato, revelar secretos o saltarse la confirmación debe ser rechazado como instrucción fuera de autoridad.

Las salidas del LLM deben considerarse no confiables hasta ser validadas. El Core nunca debe ejecutar Python, SQL, shell ni comandos SICL construidos directamente desde texto generado.

## 12. Riesgos

### 12.1 Alucinaciones

El LLM puede inventar fuentes, valores, endpoints o relaciones. Esto puede contaminar el razonamiento del usuario si la respuesta no separa hechos, hipótesis y sugerencias.

### 12.2 Violación de B-001

Una respuesta conversacional puede presentar una suposición como hecho. El sistema debe mostrar el estado epistemológico y bloquear la transformación implícita.

### 12.3 Recomendación implícita

Una respuesta como “la mejor opción es X” puede funcionar como recomendación aunque el módulo no cree una Recommendation. El contrato de salida debe preferir “las evaluaciones muestran…” y explicar los trade-offs.

### 12.4 Rendimiento bajo

El hardware propuesto puede ofrecer una latencia que haga incómoda la conversación. El sistema debe tener timeouts, mensajes de espera y una ruta degradada al Nivel 1.

### 12.5 Compatibilidad CPU

La falta de AVX2 u otras instrucciones puede impedir o degradar el runtime. Esto debe verificarse antes de considerar viable el host.

### 12.6 Exposición de Ollama

Publicar el puerto 11434 directamente expondría una superficie de ataque y permitiría saltarse el contrato del Core. Ollama debe ser local o privado.

### 12.7 Fuga de datos

El contexto enviado al modelo puede contener información sensible del proyecto. Deben existir límites de selección de contexto, retención y eliminación conforme a la gobernanza.

### 12.8 Prompt injection

La evidencia, documentos y mensajes pueden contener instrucciones maliciosas. El Copiloto debe distinguir datos citados de instrucciones de control y no permitir que el contenido externo cambie las reglas del sistema.

## 13. Mitigaciones

1. Confirmación humana obligatoria antes de toda mutación.
2. Citas de source obligatorias para afirmaciones.
3. Validación determinista de comandos propuestos.
4. Logs de cada sugerencia, confirmación y rechazo.
5. Tests de alucinación y de separación Fact/Assumption.
6. Tests de Recommendation ≠ Decision.
7. Tests de HumanReview y authority.
8. Restricción server-side de tokens y secretos.
9. Ollama accesible solo desde el Core.
10. Timeouts y límites de contexto.
11. Fallback explícito al Nivel 1 cuando el LLM no esté disponible.
12. Plan B: evaluar Phi-3 Small, Llama 3.2 3B o Groq si el rendimiento no alcanza.
13. Revisión humana profesional para toda interpretación normativa.
14. Retención y anonimización controladas para InstitutionalMemory.
15. Monitoreo de latencia, errores y consumo de recursos.

## 14. Qué no implementa este RFC

RFC-014 no crea ninguna entidad en Python, SQLite o HTTP.

No implementa `CopilotSession`, `CopilotMessage`, `CopilotSuggestion` ni `CopilotExplanation`.

No implementa endpoints `/v1/copilot/*`.

No instala Ollama.

No descarga Phi-3 Mini ni ningún otro modelo.

No cambia el frontend.

No cambia el Core Contract vigente.

No modifica el event log.

No crea un sistema de autenticación nuevo.

No habilita ejecución automática de comandos.

No crea recomendaciones automáticas ni decisiones automáticas.

## 15. Fases de implementación propuestas

### Fase A — Sistema experto

Se implementaría después de UPAO-001. El primer objetivo sería explicar estados, precondiciones y próximos pasos con reglas deterministas.

La Fase A debe incluir pruebas de entidades, fuentes, estados, comandos inválidos y autoridad humana. Debe funcionar sin LLM.

### Fase B — Traductor

Se implementaría después de validar el Nivel 1. El segundo objetivo sería traducir preguntas a comandos SICL candidatos con confirmación humana.

La Fase B debe comparar parser de reglas y traducción asistida, siempre con validación determinista antes de presentar la propuesta.

### Fase C — Conversacional

Se implementaría después de validar los niveles anteriores y UPAO-001. El objetivo sería añadir contexto conversacional con Phi-3 Mini y Ollama, manteniendo la misma frontera de autoridad.

La Fase C requiere pruebas de rendimiento, seguridad, citas, prompt injection, alucinación, límites de contexto y recuperación ante caída de Ollama.

## 16. Dependencias

La infraestructura propuesta requiere Ubuntu Server 22.04 en el Mac Pro 2013, Docker instalado si se elige ese modo de ejecución, Ollama instalado, el modelo Phi-3 Mini descargado y el Core SiMS-DeI 2.1 operativo.

También requiere conectividad segura entre el frontend y el Core, un mecanismo de autenticación server-side, observabilidad, almacenamiento de logs y una política de retención.

Estas dependencias son requisitos futuros. Su presencia no se asume ni se crea mediante este RFC.

## 17. Criterios de aceptación futuros

Antes de implementar el Nivel 1, debe comprobarse que el Copiloto nunca muta el estado sin una llamada explícita del usuario.

Antes de implementar el Nivel 2, debe comprobarse que una traducción incorrecta se rechaza y que todo comando propuesto se muestra antes de ser confirmado.

Antes de implementar el Nivel 3, debe comprobarse que Phi-3 Mini responde dentro de los límites de latencia acordados, que las fuentes son citables y que no se filtran secretos.

Cada nivel debe mantener una suite de regresión que cubra Recommendation ≠ Decision, Fact ≠ Assumption, HumanReview, append-only y autoridad humana.

## 18. Referencias y decisiones relacionadas

- B-001 — Distinción epistemológica entre Fact y Assumption.
- Decision Register de SiMS-DeI.
- `docs/SIMS_DEI_MASTER_ARCHITECTURE_v2.md`.
- `docs/SICL_CORE_CONTRACT_v1.0.md`.
- RFC-002 — Evidence HTTP.
- RFC-005 — Evaluation / Comparison HTTP.
- RFC-006 — Simulation Contract.
- RFC-007 — Multiobjective Contract.
- RFC-011 — Institutional Memory.
- Documento anterior de especificación del User Copilot, archivado como referencia conceptual.

## 19. Estado de RFC-014

RFC-014 queda definido como contrato documental pendiente de implementación. La implementación del Copiloto permanece diferida hasta después de la validación de UPAO-001 y requiere una nueva orden de gobernanza.

Ninguna de las propuestas de este documento debe interpretarse como endpoint existente, entidad implementada, autorización de infraestructura o decisión de producto.
