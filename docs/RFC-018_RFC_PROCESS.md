# RFC-018 — RFC Process

**Estado:** DRAFT
**Fecha:** 16 de septiembre de 2026
**Sistema:** SiMS-DeI
**Lenguaje formal:** SICL — Spatial Intelligence Command Language
**Repositorio:** `YvanCastilloQuezada/sicl-core`
**Rama:** `docs/rfc-018-process`
**Baseline:** `main@0d8e278be469aad2678453036b280fd8019d7d24`
**Product Owner:** Usuario / arquitecto responsable

## 1. Objetivo

Este documento formaliza el proceso para proponer, revisar, aprobar, implementar, modificar y retirar RFCs de SICL y SiMS-DeI.

El proceso busca que toda capacidad significativa tenga un alcance explícito, una decisión humana identificable, una implementación verificable y una documentación que pueda ser revisada posteriormente.

Una RFC no es un sustituto del Core Contract. La RFC propone o describe un cambio; el Core Contract define las reglas que el Core debe cumplir cuando el cambio ha sido aprobado y consolidado.

El proceso también evita que una orden informal, un commit aislado o una pantalla del frontend se conviertan silenciosamente en una ampliación del sistema.

## 2. Qué es un RFC

RFC significa Request for Comments. En este proyecto es un documento técnico y de gobierno que describe una capacidad, una modificación contractual, una decisión arquitectónica o una política necesaria para la evolución del sistema.

Una RFC debe permitir que una persona que no participó en su redacción comprenda qué problema se resuelve, qué queda dentro del alcance, qué queda fuera, qué entidades y endpoints resultan afectados y cómo se verificará el resultado.

Una RFC puede ser:

1. Una propuesta de nueva capacidad.
2. Una modificación de una capacidad existente.
3. Una política de gobierno o versionado.
4. Una extensión de una RFC anterior.
5. Un registro de una decisión que requiere implementación posterior.

Una RFC no autoriza por sí sola el despliegue. Tampoco autoriza cambios fuera de su alcance, cambios en otra línea del producto ni decisiones que corresponden al Product Owner.

Las RFCs deben mantener la distinción entre hecho implementado, supuesto de diseño y preferencia de producto. Una afirmación de que algo existe debe poder verificarse en código, contrato, documentación o pruebas.

## 3. Ciclo de vida

El ciclo de vida canónico utiliza los estados siguientes:

`DRAFT` → `PROPOSED` → `UNDER REVIEW` → `APPROVED` → `IMPLEMENTED`.

Una RFC también puede pasar a `DEPRECATED` o `REJECTED` desde los estados aplicables.

### 3.1 DRAFT

`DRAFT` es un borrador de trabajo. Puede contener alternativas, preguntas abiertas, decisiones pendientes y riesgos todavía no resueltos.

Una RFC en `DRAFT` no debe utilizarse como base para afirmar que una capacidad está aprobada o implementada.

### 3.2 PROPOSED

`PROPOSED` significa que el autor considera completa la propuesta inicial y la presenta para revisión formal.

Antes de pasar a `PROPOSED`, la RFC debe incluir objetivo, alcance, exclusiones, impacto, invariantes, pruebas previstas y criterios de aceptación.

### 3.3 UNDER REVIEW

`UNDER REVIEW` significa que la propuesta está siendo examinada por las personas o agentes designados para revisar arquitectura, contrato, seguridad, datos y viabilidad.

Las observaciones deben quedar registradas. Una revisión no equivale a una aprobación; puede devolver la RFC a `DRAFT`.

### 3.4 APPROVED

`APPROVED` significa que el Product Owner aprobó el alcance y que las preguntas que bloqueaban la autorización fueron resueltas.

La aprobación debe identificar qué se autoriza y qué no se autoriza. No se debe interpretar como permiso para implementar funcionalidades no descritas.

### 3.5 IMPLEMENTED

`IMPLEMENTED` significa que la capacidad aprobada fue implementada, probada y documentada en el commit o tag indicado por la RFC.

La RFC debe declarar los tests ejecutados, la rama consolidada, el commit resultante y las limitaciones conocidas.

Una RFC no se marca como `IMPLEMENTED` solo porque exista código en una rama de trabajo.

### 3.6 DEPRECATED

`DEPRECATED` significa que la capacidad continúa disponible por un período de transición, pero no debe recibir nuevas dependencias.

La RFC debe identificar el reemplazo, la fecha de inicio de la deprecación y la fecha prevista de retiro. Las invariantes siguen vigentes durante la transición.

### 3.7 REJECTED

`REJECTED` significa que la propuesta no será implementada en su forma actual. La razón debe registrarse para evitar reabrir la misma propuesta sin información nueva.

Una RFC rechazada puede sustituirse por una nueva RFC si cambia el problema, el alcance o la evidencia disponible.

## 4. Numeración

Las RFC principales utilizan el formato `RFC-NNN`, donde `NNN` es un número entero de tres dígitos asignado de forma estable.

Una extensión compatible o acotada de una RFC existente utiliza `RFC-NNN.1`, `RFC-NNN.2` y así sucesivamente.

Una extensión debe declarar explícitamente la RFC base y explicar qué parte conserva, amplía o corrige.

El número no se reutiliza aunque la RFC sea rechazada, obsoleta o reemplazada. La continuidad numérica forma parte de la trazabilidad histórica.

Una RFC de política puede utilizar el mismo esquema numérico que una RFC técnica. El título y el tipo deben dejar claro si define código, contrato, proceso o documentación.

El nombre del archivo debe seguir el patrón `docs/RFC-NNN_TITULO.md`. Para extensiones, el número decimal debe conservarse en el nombre cuando la plataforma lo permita.

## 5. Estructura de una RFC

Toda RFC debe incluir, como mínimo, las secciones siguientes:

1. Título, estado, fecha, autoría y baseline.
2. Objetivo.
3. Problema o motivación.
4. Alcance.
5. Exclusiones explícitas.
6. Modelo de entidades afectadas.
7. Endpoints, comandos o interfaces afectadas.
8. Invariantes y reglas de autoridad.
9. Persistencia y migración.
10. Compatibilidad y deprecación.
11. Tests y criterios de aceptación.
12. Riesgos y limitaciones.
13. Plan de implementación.
14. Referencias y firma.

Una RFC de documentación puede omitir código, pero debe describir qué documentación se considera fuente normativa y cómo se verificará su consistencia.

Una RFC de proceso debe describir responsables, estados, evidencias y condiciones de transición.

## 6. Aprobación

La aprobación requiere que el Product Owner haya revisado el objetivo, el alcance, las exclusiones, los riesgos y las decisiones que afectan al producto.

La aprobación debe quedar expresada en un mensaje, registro o documento que identifique la RFC exacta. La aprobación de una RFC no se extiende automáticamente a otra RFC relacionada.

Las decisiones que afecten autoridad humana, ontología epistemológica, persistencia append-only, privacidad, infraestructura o publicación externa deben señalarse explícitamente.

Si una RFC contiene preguntas con impacto material sin respuesta, debe permanecer en `DRAFT` o `UNDER REVIEW`.

La revisión técnica puede recomendar cambios, pero no sustituye la aprobación del Product Owner cuando esta sea requerida.

## 7. Implementación

La implementación debe comenzar desde el baseline declarado por la RFC. La rama de trabajo debe tener un nombre que permita identificar el número y propósito de la RFC.

Solo se pueden modificar los archivos autorizados. Si durante la implementación aparece una necesidad fuera del alcance, se debe detener el cambio, abrir una extensión o solicitar una nueva autorización.

La implementación debe incluir pruebas unitarias, de integración o de contrato según el impacto. Los tests deben demostrar también las invariantes negativas, como rechazar autoridad ausente o impedir mutaciones append-only.

La implementación debe actualizar los documentos contractuales afectados. Un endpoint sin documentación o una entidad sin reglas explícitas no se considera completa.

Antes del merge se debe ejecutar la suite pertinente, la suite completa cuando el cambio afecte el Core, compilación, validación de formato y revisión del diff.

## 8. Modificación de una RFC

Una RFC aprobada no se modifica silenciosamente. Las correcciones editoriales sin impacto semántico pueden registrarse como cambios de documentación.

Un cambio de alcance, una nueva entidad, una nueva invariante o una modificación de compatibilidad requiere una nueva versión de la RFC o una RFC de extensión.

La extensión debe indicar qué texto reemplaza, qué texto conserva y qué comportamiento histórico sigue vigente.

Si una implementación demuestra que la propuesta original no es viable, la RFC debe volver a `DRAFT` o abrir una RFC correctiva. No se debe marcar como `IMPLEMENTED` algo diferente a lo aprobado.

Los cambios posteriores al merge deben usar un nuevo commit y, si el contrato cambia, el proceso de versionado definido por RFC-017.

## 9. Documentos relacionados

El Core Contract es la fuente normativa para invariantes, entidades y reglas contractuales.

La Master Architecture describe la posición de SiMS-DeI, las escalas y la relación entre el sistema superior y SICL.

Los RFCs de implementación describen una capacidad concreta y sus criterios de aceptación.

El User Manual describe el uso operativo de capacidades ya disponibles. No puede convertir una capacidad de `DRAFT` en una capacidad aprobada.

El Glossary define vocabulario común. Si una definición del glosario contradice el Core Contract, debe abrirse una corrección documental.

El changelog y los tags permiten reconstruir qué capacidades existían en cada release.

## 10. Firma

Esta RFC define el proceso de gobierno de RFCs; no aprueba por sí misma nuevas capacidades.

**Product Owner:** pendiente de aprobación formal.

**Arquitecto/orquestador:** ChatGPT.

**Implementador:** Manus AI.

**Revisor independiente:** DeepSeek, cuando se solicite.

La firma debe asociarse a una versión concreta del documento. Cambiar el alcance después de firmar requiere una nueva revisión.

## 11. Checklist de transición

- [ ] El problema está definido.
- [ ] El alcance y las exclusiones están explícitos.
- [ ] La numeración es única.
- [ ] Las entidades y relaciones están descritas.
- [ ] Los endpoints y comandos están definidos.
- [ ] Las invariantes constitucionales están identificadas.
- [ ] La compatibilidad está evaluada.
- [ ] La persistencia y migración están descritas.
- [ ] Los tests tienen criterios verificables.
- [ ] El Product Owner aprobó el alcance.
- [ ] La implementación permanece dentro de los archivos autorizados.
- [ ] La documentación relacionada fue actualizada.
- [ ] El commit y el tag están identificados.
- [ ] Las limitaciones restantes están publicadas.
