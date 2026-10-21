# Auditoría 5 — Integración, seguridad, recuperación y plan de pruebas

**Perspectiva:** arquitectura transversal de las tres bases, fuente de verdad, operación y recuperación.

## 1. Problema arquitectónico

Los tres repositorios cubren responsabilidades diferentes:

| Base | Responsabilidad observada | No debe convertirse en |
|---|---|---|
| `sicl-core` | Dominio, validación, persistencia, decisiones, eventos y RFC-011 Institutional Memory | Una base secundaria escrita desde Web |
| `sicl-web` | UI, navegación, Mapas Vivos, continuidad y REVIVIR | Autoridad autónoma de decisiones o Event Store paralelo |
| `arki-acs` | Inspección y experimentación de capacidades con evidencia | Motor canónico, garantía de seguridad o promotor automático |

El nombre **MEMORY** puede representar la experiencia unificada y el contrato transversal, pero no debería borrar la distinción entre memoria institucional, estado operativo, evidencia de experimentos y proyección de continuidad.

## 2. Arquitectura objetivo propuesta (no implementada)

1. **Fuentes canónicas:** Core para entidades, decisiones y eventos de dominio; repositorios/artefactos versionados para código y contratos; ACS para artefactos/resultados experimentales bajo sus límites; registros de REVIVIR para observaciones y recibos según el contrato acordado.
2. **Contrato de evento de continuidad:** identificador estable, tipo, fecha, fuente, actor/autoridad cuando corresponda, referencia de evidencia, SHA/versiones, estado epistemológico, clasificación de sensibilidad y enlace al registro canónico. No duplicar todo el contenido si una referencia estable basta.
3. **Proyecciones:** Mapa Vivo y resumen para nuevo chat se generan desde fuentes canónicas y eventos de continuidad declarados. Cada dato indica si es observado, declarado, inferido, propuesto o no verificado.
4. **Recuperación:** una operación única “resume/reanuda” obtiene el estado canónico y los artefactos pendientes; la salida debe señalar SHA, rama, pruebas y siguiente acción verificable. Un resumen de texto no debe ser la única persistencia.
5. **Gobernanza:** ninguna promoción de conocimiento, decisión de diseño, cambio de FROZEN o modificación canónica ocurre automáticamente. Se requiere el gate humano definido por el dominio.
6. **Integridad:** validación de esquema, referencias, duplicados, orden, fechas, hashes, permisos, concurrencia, revocación y comportamiento fail-closed.
7. **Observabilidad:** separar prueba ejecutada de prueba declarada; adjuntar salida bruta, commit exacto, entorno, fecha y resultado.

## 3. Orden de implementación recomendado

**Fase A — Inventario y contratos**
- Fijar los SHAs de main de Web, Core y ACS.
- Inventariar las ramas relevantes y comparar diferencias, especialmente RFC-011, REVIVIR, Mapas Vivos y PRs de continuidad.
- Completar el inventario de fundamentos, conceptos congelados, cómics y artefactos visuales.
- Definir una matriz “dato → autoridad → persistencia → proyección → autorización”.

**Fase B — Contrato mínimo**
- Elegir un único esquema versionado de evento/referencia, compatible con el Event Store de Core.
- Aclarar si los eventos de REVIVIR se importan como observaciones/propuestas o se mantienen como artefactos externos referenciados.
- Definir expiración, retención, revocación, anonimización y restauración.
- No codificar antes de resolver la fuente de verdad.

**Fase C — Pruebas adversariales**
- Falta un archivo fuente o se corrompe el JSONL.
- Evento duplicado, referencia ausente, SHA inválido o hash inconsistente.
- Recibo falso, firmado por otra clave, clave/fingerprint incorrectos.
- Dos procesos escriben simultáneamente; lock abandonado; fallo entre escritura y rename.
- Memoria revocada o no autorizada que intenta aplicarse.
- Dato sensible en texto libre pese a anonimización declarada.
- Rama/commit desfasado respecto al que se afirma haber probado.
- Chat nuevo sin contexto previo: reconstrucción debe coincidir con los registros de origen.
- ACS sin contenedor: el sistema no debe afirmar aislamiento completo.
- Mapa documental difiere del ledger o de Core; debe fallar o marcar discrepancia, no ocultarla.

**Fase D — Integración vertical**
- Producir una observación de REVIVIR.
- Referenciar una propuesta en un experimento ACS con SHA/entorno/corpus exactos.
- Validar el recibo y registrar el resultado sin convertirlo automáticamente en hecho canónico.
- Exigir revisión humana para cualquier promoción.
- Reconstruir el Mapa Vivo y recuperar el caso en una sesión limpia.
- Verificar que Core no haya recibido mutaciones no autorizadas.

**Fase E — Aceptación**
- Tests automatizados con resultados reproducibles.
- CI verde del SHA exacto y evidencia guardada.
- Prueba E2E desde fuente hasta recuperación, con logs.
- Comparación del estado antes/después en Core.
- Revisión de privacidad, seguridad, retención y restauración.
- Aprobación del Product Owner antes de merge/promoción.

## 4. Bloqueadores actuales

- No hay evidencia reunida en esta auditoría de un E2E que conecte Core Institutional Memory + REVIVIR + ACS + Mapas Vivos.
- No se ha comprobado si el esquema de memoria institucional satisface continuidad de proyecto activo, ni debe suponerse que lo haga.
- El almacén local de REVIVIR y el ledger documental no son equivalentes al Event Store Core.
- No se localizaron los cómics; el inventario de fundamentos aún no está completo.
- ACS declara explícitamente límites de aislamiento.
- Los informes de esta rama son documentación inicial, no prueba de integración.

## 5. Regla de avance

Esta rama contiene documentación de auditoría. No se debe fusionar automáticamente. La implementación futura requiere contrato, pruebas y autorización explícita. Ningún test se marca como ejecutado sin logs del SHA exacto.


## 6. Gate de seguridad detectado en SICL Web

El workflow de continuidad en sicl-web/main tiene `contents: write`, checkout con credenciales persistentes y pasos que regeneran el mapa y hacen commit/push automático. PR #68 propone convertirlo en solo lectura; en la consulta, el PR seguía abierto y sin fusionar. El cuerpo del PR declara CI exitoso para un SHA concreto, pero ese resultado no se ha corroborado aquí con logs independientes.

Este hallazgo debe entrar en el gate de MEMORY: **no considerar segura la continuidad automatizada hasta que la política de escritura esté resuelta y validada por SHA/CI**. No se hizo merge ni se modificó el workflow.
