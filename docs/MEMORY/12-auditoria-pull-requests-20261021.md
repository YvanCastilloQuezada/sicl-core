# Auditoría de Pull Requests — SICL Core y relación con MEMORY

**Fecha de consulta:** 2026-10-21. **Método:** API GitHub para PR, base/head, estado merge, y checks de CI sobre el merge commit de MEMORY. No se fusionó ni cerró ningún PR durante esta inspección.

## 1. Estado actual del PR de documentación MEMORY

[PR #47 — Docs/memory auditoria integracion 20261021](https://github.com/YvanCastilloQuezada/sicl-core/pull/47) figura **MERGED a main**. Su merge commit es `bfd5449813e17481883641bd22aa2497e0fa4aac`, y la carpeta `docs/MEMORY/` se observa efectivamente dentro de main. El directorio contiene los cinco informes iniciales, registros de ramas, seguimiento de ramas críticas y análisis de contrato/esquemas.

**CI sobre ese SHA:** GitHub Actions muestra `test (3.11)` y `test (3.12)` con conclusión `success`. Esto acredita el resultado de CI para ese commit documental; no equivale a un E2E que integre REVIVIR, Mapas Vivos y ACS, ni demuestra despliegue.

## 2. PR abiertos de SICL Core

| PR | Estado observado | Base / head | Lectura y criterio |
|---|---|---|---|
| [#42 Core promotion concurrency guarantee](https://github.com/YvanCastilloQuezada/sicl-core/pull/42) | OPEN / DRAFT | base `main`; head `feat/core-promotion-concurrency-guarantee@d4370ba914d4c781bc591a6cf1838dda0321eb34` | El propio PR dice **no fusionar hasta cerrar todos los gates**. Incluye cambios de concurrencia/idempotencia, errores de wire y estados de promoción. Requiere confirmar todos los gates definidos en su secuencia, no asumir cierre por mergeable=true. |
| [#43 DAM foundation](https://github.com/YvanCastilloQuezada/sicl-core/pull/43) | Cerrado como merged, pero sobre rama apilada | base `feat/core-promotion-concurrency-guarantee`; head `feat/dam-dna-advisor-examiner-foundation@f16c329bcc410cbfef1ab43a3291a5bdc58ef945` | No se fusionó directamente en `main`: su base es la rama de PR #42. Aunque GitHub lo marca merged, la capacidad DAM no debe afirmarse como integrada en main hasta que el cambio base llegue a main y se compruebe el nuevo SHA. Define roles de maestro/asesor/examinador/motor nativo, niveles de graduación 0–10 y gates fail-closed. |
| [#22 RFC-030 IFC regeneration](https://github.com/YvanCastilloQuezada/sicl-core/pull/22) | OPEN | base `main`; head `feat/rfc-030-ifc-regeneration@9d2b4ade66439a6237b9fc4a4f61e33e9a14f4e3` | Añade reglas declarativas y artefacto IFC. Debe verificarse procedencia del IFC, reproducibilidad, alcance del exportador y los tests del SHA exacto. Las tablas de comparación del body no son por sí mismas validación normativa. |
| [#21 RFC-034.1 sheet composition/layout engine](https://github.com/YvanCastilloQuezada/sicl-core/pull/21) | OPEN | base `main`; head `feat/rfc-034-1-layout-engine@a6f727f2b3088e3ff416b937d7d4c92d2dbc55db` | El body declara 16 tests específicos, suite, compileall y diff-check PASS, además de 5 láminas A3 y cero colisiones. Esta auditoría no reprodujo los comandos. La consulta de metadata devolvió `mergeable=false`; revisar el motivo antes de evaluar. El PR limita el cambio a composición/cálculo, no renderizado/PDF. |
| [#1 Railway editable-install revert](https://github.com/YvanCastilloQuezada/sicl-core/pull/1) | OPEN | base `main`; head `fix/revert-railway-editable-install@1af6802f0956b6b01e4afdf7f169b1e336677198` | PR antiguo y conflictivo temporalmente con la historia de despliegue: PR #2 ya figura fusionado y resolvió el problema de Railway de otra forma. No aplicar una reversión antigua sin leer main actual, el diff y el despliegue presente. Metadata devuelve `mergeable=false`. |

## 3. PR recientes cerrados relevantes

- [#45 Reconcile Core authority documentation with ARKI Live Map](https://github.com/YvanCastilloQuezada/sicl-core/pull/45): **merged a main**. Su propósito es preservar Core como autoridad canónica del estado de proyecto y marcar un ledger antiguo como histórico/requiere reconciliación.
- [#46 0-Historical](https://github.com/YvanCastilloQuezada/sicl-core/pull/46): cerrado sin merge. No inferir que su contenido esté absorbido.
- [#47 MEMORY audit](https://github.com/YvanCastilloQuezada/sicl-core/pull/47): merged, ver sección 1.

## 4. Implicaciones para el inventario por rama

El estado de PR y el estado de una rama son dimensiones diferentes. Por ejemplo, PR #43 está marcado merged pero su `base` es una rama feature, no `main`; en cambio PR #47 sí tiene base `main` y su merge commit coincide con la cabeza actual de Core main. Cada ficha de rama debe registrar:
1. SHA de head observado.
2. SHA de base y base ref.
3. estado de PR (open/closed/merged).
4. si el PR fue integrado a `main` o sólo a otra rama.
5. merge commit SHA, si existe.
6. checks de CI para el SHA pertinente.
7. evidencia de ejecución independiente, si existe.

## 5. No resuelto

- No se ha reproducido localmente el test suite ni el E2E transversal MEMORY.
- No se ha verificado el estado actual de despliegue de Core.
- El riesgo del workflow de continuidad de Web requiere reconsulta de PR #68 en `sicl-web`; esta auditoría no modifica ni resuelve ese PR.
- Un check verde de tests para el commit documental de MEMORY no cierra estas brechas.

**Dictamen:** PR #47 está incorporado a Core main y CI de Python 3.11/3.12 reporta éxito para su merge SHA. PR #42, #22, #21 y #1 continúan abiertos en la consulta; PR #43 está merged en una rama apilada, no directamente en main. No se tomó ninguna acción mutante sobre PR ni código de producto.
