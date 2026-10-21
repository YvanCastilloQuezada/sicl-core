# Auditoría 2 — SICL Web, REVIVIR y Mapas Vivos

**Perspectiva:** aplicación, continuidad entre chats, adaptador de auto-mejora y límites de la evidencia.

## 1. Mapa Vivo de Continuidad

En `docs/arki-master-map/ARKI_MAPA_VIVO_CONTINUIDAD.md`, el propio documento advierte: se genera a partir de Git y eventos declarados; **no es el Event Store canónico de Core** y no verifica CI, arquitectura ni despliegue. El protocolo propone que un nuevo chat lea el mapa y el ledger, compruebe el SHA remoto y CI y continúe desde los pendientes.

El mapa registra una serie de acciones y estados, pero declara explícitamente estados como `NOT_VERIFIED`, `IMPLEMENTED_NOT_VERIFIED`, `BLOCKED` y `AWAITING_LOCAL_EXECUTION`. Esa diferenciación es útil y debe conservarse.

Fuente: [ARKI_MAPA_VIVO_CONTINUIDAD.md](https://github.com/YvanCastilloQuezada/sicl-web/blob/main/docs/arki-master-map/ARKI_MAPA_VIVO_CONTINUIDAD.md).

## 2. Generador del snapshot

`tools/maqueta-viva/arki-continuity-snapshot.cjs`:
- lee historia Git y un ledger JSONL;
- valida estructura básica de cada evento, fecha y duplicación de IDs;
- genera una vista documental con estado, últimos commits, última acción y pendientes;
- admite `--check` para comparar el snapshot actual con el generado.

El código incluye una advertencia explícita de que Git demuestra commits, no decisiones ni CI. La generación del snapshot no convierte eventos declarados en hechos de dominio y el archivo generado no es un event store.

Fuente: [arki-continuity-snapshot.cjs](https://github.com/YvanCastilloQuezada/sicl-web/blob/main/tools/maqueta-viva/arki-continuity-snapshot.cjs).

## 3. REVIVIR / adaptador operativo

`tools/maqueta-viva/arki-automejora-operativa.cjs` requiere una ruta absoluta para el almacén, usa bloqueo exclusivo, valida el esquema/eventos, limita el tamaño, rechaza ciertos targets inseguros y persiste mediante archivo temporal y rename. La operación `observe` produce eventos de observación, déficit y propuesta, y devuelve de forma expresa:
- `execution: "OBSERVATION_AND_PROPOSAL_ONLY"`
- `experimentExecuted: false`
- `learningVerified: false`
- `canonicalMutation: false`

El flujo de evaluación posterior exige referencia de evidencia y clave pública/fingerprint para validar el recibo experimental. Esto es una barrera útil entre proponer y afirmar que una mejora funcionó.

Fuente: [arki-automejora-operativa.cjs](https://github.com/YvanCastilloQuezada/sicl-web/blob/main/tools/maqueta-viva/arki-automejora-operativa.cjs). Archivo consultado en `main`, blob SHA `7872af5135bf1705a574f140818b9890402d9553`.

## 4. Límite central encontrado

Hay dos mecanismos con formas de persistencia distintas:
- el adaptador REVIVIR guarda un almacén JSON local, con eventos validados;
- el Mapa Vivo construye una proyección a partir de Git y un ledger JSONL documental;
- el mapa dice expresamente que debe reconciliarse con Event Store Core sin duplicarlo.

No se ha demostrado en esta auditoría que el almacén de REVIVIR sea accesible de forma compartida entre instancias, que Core lo consuma o que un nuevo chat pueda recuperar automáticamente su estado completo. La persistencia local de un módulo no equivale a memoria institucional compartida.

## 5. Riesgos a comprobar en el código completo y la ejecución

- Ubicación, copias de seguridad, restauración y permisos del JSON de REVIVIR.
- Comportamiento ante caída entre creación de archivo temporal y rename; recuperación de locks abandonados.
- Política de concurrencia y deduplicación entre procesos/hosts.
- Vínculo de recibos con SHA, pruebas, entorno, actor y propuesta exacta.
- Integridad del ledger JSONL frente a edición/borrado; la validación de formato no equivale por sí sola a una cadena criptográfica inmutable.
- Si workflows pueden escribir artefactos en ramas/base sin autorización; revisar permisos y eventos de push.
- Si el mapa distingue commit observado, CI real, despliegue y aprobación humana en cada presentación.
- Recuperación completa en un chat limpio sin depender del contexto conversacional previo.

Estas son comprobaciones pendientes, no fallos confirmados.

## 6. Recomendación

Mantener Mapas Vivos como **proyección de lectura/regenerable**; mantener REVIVIR como **productor de observaciones, déficits, propuestas y recibos**; trasladar al modelo canónico de Core solo eventos de dominio que cumplan su contrato. MEMORY debe ser la experiencia/arquitectura de recuperación común, no un cuarto almacén paralelo.

**No se ejecutaron pruebas durante esta auditoría documental.** Los estados de prueba citados en el mapa son históricos hasta que se comprueben contra un SHA exacto y sus logs.
