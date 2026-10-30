# MEMORY — contrato de continuidad histórica permanente

**Estado:** DISEÑO AUTORIZADO PARA IMPLEMENTACIÓN; runtime E2E PENDIENTE.
**Fecha de decisión:** 2026-10-30.
**Autoridad:** SICL Core.
**Ámbito:** continuidad histórica de ARKI entre sesiones, chats, procesos y despliegues.

## 1. Objetivo

MEMORY debe conservar la historia operativa de ARKI de forma durable y recuperable. Cerrar un chat, reiniciar un proceso, desplegar una nueva versión o cambiar de equipo no debe borrar decisiones, contexto, evidencia, bloqueos ni trabajo pendiente.

La continuidad se considera completa únicamente cuando una sesión nueva puede reconstruir el estado autorizado y continuar desde la siguiente acción pendiente sin pedir al propietario que vuelva a explicar el proyecto.

"Histórica permanente" significa almacenamiento durable, append-only, respaldado y verificable. No significa conservar indiscriminadamente datos personales o secretos: credenciales, tokens, claves privadas y datos sensibles no se almacenan en MEMORY.

## 2. Autoridad única por clase de información

No se crea un Event Store paralelo.

| Clase | Autoridad | Función de MEMORY |
|---|---|---|
| Entidades, hechos, decisiones y eventos de proyecto | SICL Core | Referenciar y consultar el registro canónico |
| Evidencia técnica y resultados de pruebas | Artefacto original + SHA/URL + CI | Indexar referencias y estado verificado |
| Decisiones conversacionales autorizadas | Evento de continuidad confirmado por autoridad humana | Registrar decisión, alcance y procedencia |
| Observaciones y propuestas de REVIVIR | Adaptador REVIVIR | Enviar referencias; nunca promoverlas automáticamente |
| Experimentos | ARKI-ACS | Conservar recibos, resultados y hashes como evidencia |
| Roadmap y estado de trabajo | Proyección derivada de Core + evidencia | Calcular estado y siguiente acción |
| Mapa Vivo / Handoff | Proyección regenerable | Facilitar lectura humana; nunca fuente canónica |

RFC-011 sigue siendo la memoria institucional de conocimiento derivado de proyectos cerrados. No se amplía su significado para convertirlo en bitácora de sesiones. La continuidad operativa usa el registro de eventos existente de Core y sus contratos.

## 3. Ciclo automático

1. **Captura:** las operaciones de ARKI/SICL que cambian estado generan eventos mediante los servicios de dominio de Core. La integración conversacional envía un evento estructurado cuando una decisión o pendiente queda identificado y confirmado.
2. **Validación:** validar esquema, actor, proyecto, tipo, fuente, timestamp, referencias y política de datos. Rechazar eventos incompletos o secretos.
3. **Idempotencia:** cada evento externo incluye \`event_id\` estable e \`idempotency_key\`; reintentos no duplican historia.
4. **Persistencia:** insertar en el registro append-only de Core dentro de la transacción de la operación. No escribir directamente desde Web en tablas de Core.
5. **Procedencia:** conservar actor, origen, fecha de ocurrencia, fecha de registro, SHA del código, referencia de evidencia y correlación de sesión cuando existan.
6. **Proyección:** actualizar automáticamente índices, roadmap, bitácora y Mapa Vivo desde eventos canónicos y evidencia consultable.
7. **Recuperación:** al iniciar una sesión, leer el último checkpoint, eventos posteriores, decisiones vigentes, FROZEN, bloqueos, pruebas y siguiente acción.
8. **Verificación:** comprobar integridad, continuidad de secuencia, referencias rotas, eventos sin proyección y proyecciones desactualizadas.
9. **Respaldo:** exportación incremental cifrada y restauración probada, con retención y control de acceso documentados.

## 4. Contrato mínimo de evento

Cada evento de continuidad debe incluir:

- \`event_id\`: identificador global único.
- \`event_type\`: \`SESSION_OPENED\`, \`SESSION_CLOSED\`, \`DECISION_RECORDED\`, \`TASK_STARTED\`, \`TASK_UPDATED\`, \`TASK_BLOCKED\`, \`TASK_COMPLETED\`, \`EVIDENCE_ATTACHED\`, \`ROADMAP_CHANGED\`, \`HANDOFF_CREATED\` o \`CORRECTION_RECORDED\`.
- \`project_id\` y \`workstream_id\`.
- \`occurred_at\` y \`recorded_at\` en UTC.
- \`actor\` y \`authority_ref\` cuando aplique.
- \`source_system\`: \`SICL_WEB\`, \`SICL_CORE\`, \`ARKI_ACS\`, \`CHAT_INTEGRATION\` u otro adaptador registrado.
- \`source_sha\` y \`evidence_refs\` cuando existan.
- \`payload\` validado, sin secretos ni datos sensibles innecesarios.
- \`idempotency_key\`, \`correlation_id\` y \`supersedes_event_id\` cuando aplique.

Los eventos históricos no se editan ni se borran para corregir errores. Se añade un evento de corrección que referencia el evento anterior. Las revocaciones son nuevos eventos con motivo y autoridad.

## 5. Estado recuperable

La proyección de continuidad debe poder reconstruir:

- identidad y objetivo del proyecto;
- hechos confirmados, hipótesis y UNKNOWN;
- decisiones del propietario y límites FROZEN;
- roadmap F1–F10, dependencias y estado por evidencia;
- tareas abiertas, responsables, bloqueos y siguiente acción exacta;
- cambios por repositorio, rama y SHA;
- PR, CI, pruebas y artefactos de evidencia;
- propuestas de REVIVIR y resultados ACS, diferenciados de decisiones;
- historial cronológico y checkpoints de recuperación.

Cada elemento debe conservar su estado epistemológico. \`DECLARED\`, \`IMPLEMENTED\`, \`EXECUTED\`, \`VERIFIED\`, \`BLOCKED\` y \`UNKNOWN\` no son intercambiables. No se infiere PASS por la existencia de un test o un commit.

## 6. Automatizaciones obligatorias

| Disparador | Acción automática | Condición de cierre |
|---|---|---|
| Operación de dominio | Evento Core en la misma transacción | Evento persistido e idempotente |
| Decisión conversacional confirmada | Enviar evento estructurado a Core | Actor, alcance y fuente validados |
| Inicio de sesión | Construir paquete de recuperación | Último checkpoint + delta de eventos |
| Cierre de sesión | Crear checkpoint y handoff | Pendientes y próxima acción explícitos |
| Cambio de evento/roadmap | Regenerar proyecciones | Proyección consistente con Core |
| Cada noche | Auditoría de integridad y backup incremental | Reporte firmado/hasheado |
| Restauración de backup | Prueba aislada de recuperación | Conteo, hashes y secuencia coinciden |

Las automatizaciones no autorizan decisiones, promoción de propuestas, cambios geométricos, mutaciones FROZEN ni aplicación de memoria institucional.

## 7. Límites reales de captura conversacional

Un repositorio GitHub no recibe automáticamente el contenido de los chats de ChatGPT. La captura completa de conversaciones requiere una integración explícita que entregue eventos estructurados y autorizados a SICL Core.

Hasta que esa integración exista y supere una prueba E2E, el sistema debe declarar \`CHAT_CAPTURE = NOT_CONNECTED\` y no afirmar que todas las conversaciones se guardan automáticamente. Se permite capturar decisiones confirmadas y handoffs mediante una acción explícita del usuario o una integración habilitada.

## 8. Seguridad y durabilidad

- Append-only para eventos históricos.
- Idempotencia ante reintentos y concurrencia.
- Autenticación de servicio y autorización por proyecto.
- Cifrado en tránsito y en reposo para almacenamiento y backups.
- Secret scanning y exclusión de credenciales.
- Exportación verificable, política de retención y restauración ensayada.
- Observabilidad de errores de captura; no descartar silenciosamente eventos.
- Si Core no está disponible, mantener una cola local cifrada y limitada, con reintento e indicador \`PENDING_SYNC\`; nunca declarar persistencia canónica hasta recibir confirmación de Core.

## 9. Criterios de aceptación — no negociables

1. Un evento escrito en Core sobrevive cierre de proceso y reinicio del servicio.
2. Repetir la misma petición no duplica eventos.
3. Dos escritores concurrentes no pierden eventos ni rompen la secuencia.
4. Una corrección conserva el evento original y añade su referencia.
5. Una sesión nueva reconstruye decisiones, FROZEN, roadmap, evidencia y pendientes.
6. Una decisión confirmada en la integración conversacional aparece en Core y en la proyección.
7. Una caída de Core se detecta y deja eventos pendientes visibles; no hay pérdida silenciosa.
8. El backup se restaura en un entorno aislado y se verifican hashes y conteos.
9. Ninguna propuesta de REVIVIR/ACS se convierte en decisión sin autoridad humana.
10. No se declara \`PERMANENT_CONTINUITY = VERIFIED\` hasta que todos los criterios estén probados en SHA y entorno identificados.

## 10. Implementación por etapas

- **M0 — Contrato:** este documento y matriz de autoridades.
- **M1 — API de continuidad Core:** escritura idempotente de eventos en el registro canónico existente; lectura incremental y checkpoint. Sin tabla/event store paralelo.
- **M2 — Adaptador Web:** envío autenticado de eventos; cola temporal cifrada y reintentos.
- **M3 — Proyecciones:** bitácora, roadmap, evidencias, Mapa Vivo y handoff derivados de Core.
- **M4 — Integración conversacional:** captura de decisiones confirmadas y cierre de sesión, con autorización explícita.
- **M5 — Operación:** backup, restauración, monitoreo, prueba de recuperación entre chats y auditoría adversarial.

**Estado actual:** M0 documentado. M1–M5 NO IMPLEMENTED / NO VERIFIED. Este documento no declara que la continuidad permanente ya funcione.

## 13. Implementación directa en GitHub — corte 2026-10-30

Esta sección distingue código incorporado de operación validada. Los commits no sustituyen la ejecución de pruebas ni la prueba de restauración.

### M1 — API canónica de continuidad en Core

**Estado:** IMPLEMENTED_NOT_VERIFIED.

- `POST /v1/projects/{project_id}/continuity/events`: registra eventos estructurados en la tabla `events` existente.
- `GET /v1/projects/{project_id}/continuity/events?after_id=N`: recuperación incremental por secuencia.
- `GET /v1/projects/{project_id}/continuity/checkpoint`: checkpoint de proyecto y cursor.
- La API falla cerrada con `503 CONTINUITY_AUTH_NOT_CONFIGURED` si no existe `SICL_CORE_SERVICE_TOKEN`; exige Bearer token válido.
- `continuity_event_keys` es exclusivamente un índice de idempotencia que apunta a `events.id`; no es un segundo Event Store. Sus registros son append-only.
- La repetición con el mismo evento y contenido devuelve `DUPLICATE`; reutilizar `event_id` o `idempotency_key` con contenido distinto devuelve `409`.

Commits en `sicl-core/main`: `9c9961b`, `02ee596`, `0eec797`, `9f2be89`, `98b65e2` y `96e3e36`.

### M2 — Adaptador Web y outbox

**Estado:** IMPLEMENTED_ON_BRANCH; MIGRATION_AND_RUNTIME_NOT_VERIFIED.

- Se incorporó `arki_continuity_outbox` en MySQL, con claves únicas, estados `PENDING_SYNC`, `SYNCED` y `BLOCKED`, intentos y secuencia Core.
- El contenido de los eventos se cifra con AES-256-GCM. La clave se obtiene exclusivamente de `ARKI_CONTINUITY_ENCRYPTION_KEY` (base64 de 32 bytes); no se almacena en Git.
- Los identificadores de evento se derivan de propietario, proyecto e idempotency key para conservar identidad entre reintentos.
- El worker intenta sincronizar al recibir un evento y cada 60 segundos. Core conserva la autoridad final y aplica su propia idempotencia.
- Sin MySQL o clave de cifrado, la captura falla cerrada; no usa memoria volátil como sustituto.

### M3 — Proyecciones

**Estado:** IMPLEMENTED_ON_BRANCH; WORKFLOW_NOT_EXECUTED.

- `scripts/arki-memory-core-projection.mjs` consulta checkpoint y páginas de eventos de Core.
- Genera JSON y Markdown derivados, con SHA, secuencias y referencias; anonimiza el identificador del actor.
- El workflow `arki-memory-core-projection.yml` es de solo lectura y publica artefactos; no escribe en `main`.
- Requiere configurar secretos `SICL_CORE_URL`, `SICL_CORE_SERVICE_TOKEN` y variable `ARKI_MEMORY_PROJECT_IDS`.

### M4 — Captura conversacional autorizada

**Estado:** IMPLEMENTED_ON_BRANCH; END_TO_END_NOT_VERIFIED.

- `POST /api/continuity/projects/{projectId}/events` captura eventos estructurados autenticados.
- `DECISION_RECORDED` exige usuario administrador propietario, confirmación explícita `confirmedByOwner=true` y `authorityRef`.
- No se captura ni se promete captura automática de transcripciones completas. Los eventos contienen decisiones y acciones estructuradas, no el chat entero.
- Lectura incremental y checkpoint se exponen por rutas autenticadas del adaptador Web.

### M5 — Backup y restauración aislada

**Estado:** IMPLEMENTED_NOT_EXECUTED.

- `scripts/arki_memory_backup.py backup` crea backup SQLite consistente, cifrado con Fernet y manifiesto SHA-256.
- `scripts/arki_memory_backup.py restore-verify` restaura en una ruta nueva, rechaza sobrescrituras y verifica integridad SQLite, hash, versión, cantidad/último evento y triggers append-only.
- Requiere `SICL_BACKUP_FERNET_KEY`; la clave no se guarda en Git.
- No se ha ejecutado todavía un backup real ni una restauración aislada de la base de producción.

### Bloqueos operativos para declarar CERO DEUDA

1. Ejecutar suite Core, incluida `tests/test_continuity_api.py` y `tests/test_memory_backup.py`, sobre SHA exacto.
2. Configurar `SICL_CORE_SERVICE_TOKEN` en Core y `SICL_CORE_URL`/`SICL_CORE_SERVICE_TOKEN` en Web con el mismo secreto.
3. Aplicar la migración Drizzle `0005_arki_memory_continuity.sql` en una ventana controlada; no asumir que el esquema de producción ya cambió.
4. Configurar `ARKI_CONTINUITY_ENCRYPTION_KEY` y probar reintento, caída temporal de Core y recuperación posterior.
5. Ejecutar el workflow de proyección con secretos/variables reales y revisar el artefacto.
6. Ejecutar backup cifrado y restauración aislada; conservar manifiesto y SHA.
7. Abrir y cerrar una sesión real, registrar una decisión confirmada por el propietario, reiniciar Web/Core y recuperar el estado desde Core.
8. No marcar M1–M5 como VERIFIED hasta que cada evidencia anterior exista y esté asociada al SHA, entorno y fecha exactos.

### M5 — instalación del backup diario en Ubuntu

Los archivos systemd incluidos son plantillas de despliegue. No se activan solos al hacer merge.

1. Instalar cryptography en el entorno virtual de Core (ya declarado en pyproject.toml).
2. Crear /etc/sicl-core/backup.env, accesible solo por root y el usuario de servicio, con SICL_DB_PATH y SICL_BACKUP_FERNET_KEY. La clave debe generarse y custodiarse fuera de Git.
3. Crear /var/backups/sicl-core con propietario sicl:sicl y permisos 0700.
4. Instalar deploy/systemd/sicl-core-backup.service y deploy/systemd/sicl-core-backup.timer en /etc/systemd/system/.
5. Ejecutar systemctl daemon-reload && systemctl enable --now sicl-core-backup.timer.
6. Ejecutar una primera vez systemctl start sicl-core-backup.service y revisar journalctl -u sicl-core-backup.service.
7. Probar restauración en un directorio aislado con restore-verify. No apuntar el destino a la base activa.

El timer está programado para las 03:20 hora local del servidor. El huso horario del servidor debe verificarse; no se asume que sea Perú.
