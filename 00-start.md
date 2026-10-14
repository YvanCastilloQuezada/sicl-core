# 00-start — ARKI / ARQUI | Reanudación canónica de trabajo

**Actualizado:** 2026-10-14 (Perú)  
**Ámbito:** `sicl-core` / rama `feat/ace88-core-service-auth`  
**Propósito:** punto de entrada para el próximo chat; separar evidencia verificada de objetivos pendientes.

## 1. Identidad y reglas invariables

- ARKI/ARQUI es el proyecto actual; SICL y Vitruvio son nombres históricos del mismo sistema.
- Un solo núcleo geométrico AGK: hipótesis arquitectónica **OCCT + ARKI_DELTA**, enfoque **3D-First**, sin encadenar motores de geometría en runtime. No confundir hipótesis de diseño con implementación demostrada.
- Árbol Vivo, Árbol Gemelo Digital, Gemelo Predictivo y ARKI Autocorrectivo son vistas/capacidades de un sistema coherente; no crear motores paralelos.
- Política **CERO DEUDA**: no ocultar fallos, no rebajar controles, no declarar PASS/FREEZE sin evidencia.
- Las modificaciones canónicas y las capacidades FROZEN deben respetar precedencias, contratos, trazabilidad y autorización humana cuando aplique.
- Delta 6.2 es la vía prevista de adquisición/curaduría del conocimiento; verificar su implementación antes de afirmarla.
- El propietario aprueba decisiones sensibles; ARKI debe detectar, diagnosticar, simular y proponer con evidencias.

## 2. Último estado comprobado (14 de octubre de 2026)

**Repositorio GitHub:** https://github.com/YvanCastilloQuezada/sicl-core  
**Rama publicada:** `feat/ace88-core-service-auth`  
**SHA remoto verificado por `git ls-remote` en ARKI-02:** `9ca4a820dce7a7f6eb3a84d67f8f94d7260b7994`.  
**Commit ACE88 anterior:** `0592ede136e9126f7249fe73a5f089e11122de71`.

En ARKI-02, antes del push:
- Suite completa `pytest tests -q`: **PASS**, sin fallos.
- Prueba negativa de promoción sin firma: **PASS** (promoción rechazada).
- SQLite `PRAGMA quick_check`: **OK**.
- ACE88 Ed25519 para autorización humana de promoción Developer D2: **aprobación funcional**.
- Identidad del propietario real y auditoría independiente de seguridad: **PENDIENTES**. Las claves LAB no son prueba de identidad real.
- `SECURITY_FREEZE=PENDING_INDEPENDENT_AUDIT`. **NO declarar FREEZE.**
- El push HTTPS de la rama **se completó** y el SHA remoto coincidió.
- No se ha demostrado merge a `main`, despliegue público ni ciclo completo de arquitecto autónomo.
- Advertencia de Starlette/`httpx` en pruebas: registrar, no interpretar como fallo funcional.

**Atención:** este documento se incorpora mediante GitHub después del SHA indicado; por tanto, al retomarlo, consultar el HEAD remoto actualizado antes de operar.

## 3. Fuentes del repositorio para revisar al retomar

1. `docs/ace88/ACE88_ROOT_INTEGRATION.md` — alcance y seguridad de ACE88.
2. `docs/arki-automejora/ARKI_AUTONOMOUS_IMPROVEMENT_CONTRACT_V0.md` — contrato conceptual del ciclo.
3. `tools/arki_automejora_inventario.py` — inventario de solo lectura.
4. `src/sicl/developer_promotion.py`, `src/sicl/human_authority_crypto.py`, `src/sicl/repository.py`.
5. `api/routes/v1.py`, `api/schemas.py`.
6. `tests/test_ace88_*.py`, `tests/test_developer_promotion.py`, `tests/test_microcase_dev_001.py`.
7. Árbol completo, ramas, PR, CI, estado de trabajo local y contratos FROZEN antes de cualquier integración.

## 4. Ciclo autónomo prioritario de ARKI

**Detectar carencia → interpretar normas y jurisdicción → razonar causas y dependencias → generar al menos tres alternativas → simular en el Gemelo → autoevaluar con métricas → proponer autocorrección → solicitar aprobación cuando corresponda → aplicar con reversión → verificar → aprender por Delta 6.2 → propagar evidencias al Árbol Vivo → reevaluar.**

El ciclo debe aplicarse tanto a carencias internas del software como a carencias de proyectos arquitectónicos multiescala (objeto, interior, edificio, conjunto, ciudad, región, territorio). Nunca extrapolar normas entre escalas o jurisdicciones sin comprobar aplicabilidad.

**Estado real:** el contrato documental y el inventario de solo lectura existen en la rama. **No está demostrada** la ejecución autónoma integral ni la modificación geométrica autocorrectiva.

## 5. Próximas tareas ordenadas

1. Consultar HEAD, estado de PR, CI, ramas y diferencias frente a `main`; no asumir merge.
2. Auditar ACE88 de forma independiente: identidad, firma, payload canónico, expiración, nonce, replay, atomicidad, autorización, persistencia y pruebas adversariales.
3. Completar enrolamiento seguro de la identidad real del propietario antes de cualquier FREEZE de seguridad.
4. Inspeccionar el Árbol Vivo, dependencias, F1–F10, FROZEN y el Gemelo Digital desde evidencia del repositorio; identificar carencias sin inventar estado.
5. Implementar **un primer ciclo vertical E2E mínimo** de autodiagnóstico y mejora en entorno aislado, con tres alternativas, métricas, aprobación, rollback y trazabilidad; después extender a normativa y geometría AGK.
6. Ejecutar pruebas adversariales y regresión antes de integrar cambios. Conservar la distinción entre `PROPOSED`, `IMPLEMENTED`, `TESTED`, `APPROVED` y `FROZEN`.
7. Actualizar este `00-start.md` en cada hito **junto con** el cambio correspondiente, registrando SHA, evidencias, bloqueos, siguiente acción y enlaces a documentación.

## 6. Protocolo del siguiente chat

- Leer primero este archivo y los documentos enlazados; consultar el estado real de GitHub.
- No pedir al usuario que repita decisiones ya documentadas.
- Preferir acciones ejecutables y **macroórdenes únicas** para ARKI-02 cuando el trabajo local no sea accesible.
- No afirmar ejecución en ARKI-02 sin salida de terminal; no afirmar publicación sin SHA remoto.
- Si no existe acceso al entorno local, preparar script seguro, respaldos y un solo log de resultados.
- No introducir claves privadas, tokens, bases SQLite ni secretos en Git.
- No modificar `main` o declarar FREEZE sin verificación y autorización explícitas.

## 7. Última instrucción del propietario

> «Avanza con esto: llenar el 00-start para tu próximo chat, y eso hazlo automáticamente.»

Este archivo es el handoff inicial persistente. **La actualización futura automática no está programada ni implementada por este commit**: debe incorporarse como parte del flujo de entrega/CI, con validación y sin inventar evidencia.

## 8. Avance Mapa Vivo V1 (2026-10-14)

- Generador de grafo observacional añadido: `tools/arki_mapa_vivo.py`.
- Contrato de validación: `docs/arki-automejora/ARKI_MAPA_VIVO_V1.md`.
- Commit de documentación: `8f842f33d235cc12baa94164f975246d28584562`.
- Estado: código publicado en rama; ejecución local, cobertura real F1–F10 y mapa interactivo pendientes de validar.
- Próxima acción: `git pull --ff-only` en ARKI-02, ejecutar generador fuera del repositorio, comprobar salida y aportar evidencia; después implementar detector de ciclos y propagación.
