# MEMORY — compatibilidad de esquemas entre REVIVIR, Mapas Vivos y Core

**Fecha:** 2026-10-21. Lectura estática de Web main y Core main; pruebas no ejecutadas.

## 1. Tres formatos diferentes

### REVIVIR / adaptador local
Fuente: `tools/maqueta-viva/arki-automejora-operativa.cjs`, blob SHA `7872af5135bf1705a574f140818b9890402d9553`.

- Almacén JSON con schema `ARKI-AUTOMEJORA-MEMORY-STORE-1`.
- Eventos tipados como `OBSERVATION`, `DEFICIT`, `PROPOSAL`, además de resultados de experimento, test y reevaluación.
- Exige ruta absoluta, lock exclusivo, validación del journal, referencias de evidencia, límite de tamaño, comprobación de symlink y escritura temporal + fsync + rename.
- El módulo `arki-autonomy-memory.cjs` valida hashes encadenados, pero por sí solo declara que no persiste; el adaptador es quien persiste localmente.
- La operación de observación devuelve `OBSERVATION_AND_PROPOSAL_ONLY`, `experimentExecuted=false`, `learningVerified=false`, `canonicalMutation=false`.

### Mapas Vivos
Fuentes:
- `ARKI_CONTINUITY_EVENTS.jsonl`, blob SHA `38f5cc7e94dcd7197860b3cdc60535e00616c01d`.
- `arki-continuity-snapshot.cjs`, blob SHA `d7c96ce1b04c30dabb25ae90c17962ac2969ba18`.
- `ARKI_MAPA_VIVO_CONTINUIDAD.md`, blob SHA `d9d866bea3ecc664f46aa6167b462b1d34049640`.

El ledger de continuidad usa `id`, `at`, `kind`, `summary`, `evidence`, `status` y campos opcionales. El snapshot valida JSON por línea, campos obligatorios, fecha e IDs únicos. No se observó cadena criptográfica de hashes por evento en este formato. El generador deriva una vista de Git + ledger y declara que no es Event Store Core ni valida CI/despliegue.

### Core
Fuentes:
- `docs/RFC-011_INSTITUTIONAL_MEMORY.md`, blob SHA `614839115403895188eef84083d74906bd126823`.
- `src/sicl/memory.py`, blob SHA `ce1dd164c029ca1f7dd2794e9e78a68480cc172b`.
- `src/sicl/repository.py`, blob SHA `baf65ae8b518f00f52a987331f83b69fa99ed4ec`.

Core mantiene eventos de dominio y una proyección institucional persistente/versionada. La memoria institucional deriva de proyectos cerrados; no es un ledger de todas las operaciones activas ni el almacenamiento de propuestas de REVIVIR.

## 2. Estado observado del Mapa Vivo en Web main

El snapshot consultado identifica como último commit sustantivo `a15597e2b2b51916d429afdec2ec4a8c77b72a20` (21 de octubre) y muestra Core/D-2/AGK como `NOT_VERIFIED`, CI/E2E como `NOT_VERIFIED`, y promoción como `NO_AUTORIZADA_POR_ESTE_MAPA`. Sin embargo, su ledger tiene diez eventos fechados el 13 de octubre; el último declara `IMPLEMENTED_AWAITING_LOCAL_EXECUTION`. Esto es un registro histórico que aún no refleja la auditoría MEMORY actual. No significa que la auditoría actual se haya incorporado automáticamente.

El protocolo de chat nuevo reconoce explícitamente que Git no captura conversaciones y que la automatización recurrente no garantiza que cada acción del chat sea incorporada. La recuperación automática entre chats sigue pendiente de prueba E2E.

## 3. No hay un contrato de interoperabilidad compartido demostrado

Los tres formatos no son intercambiables:
- REVIVIR registra observaciones, déficits y propuestas con hashes encadenados y persistencia JSON local.
- El ledger de continuidad registra declaraciones documentales con fecha y evidencia textual.
- Core registra eventos canónicos de dominio y memoria institucional versionada.

No se debe copiar todos los eventos de un formato al otro sin mapeo semántico. Un `PROPOSAL` de REVIVIR no se convierte en `Decision`; un `CI_OBSERVATION` declarativo no se convierte en CI verificado; una memoria institucional no se convierte en estado de ejecución actual.

## 4. Contrato mínimo pendiente para MEMORY

Cada registro unificado de continuidad debería referenciar, sin suplantar, su fuente original e incluir como mínimo:
- `record_id` estable y `record_type` de un vocabulario versionado;
- `source_system` y `source_record_id`;
- `source_sha` o versión del artefacto cuando aplique;
- timestamp y distinción entre fecha de concepción, observación, commit y verificación;
- estado epistemológico separado: `DECLARED`, `OBSERVED`, `VERIFIED`, `CONTRADICTED`, `UNKNOWN`;
- evidencia referenciada, no solo un resumen de texto;
- actor/authority cuando la operación es una decisión;
- relación `supersedes` o revocación sin borrar historia;
- idempotencia/deduplicación para importaciones repetidas;
- política de privacidad/retención y procedimiento de recuperación.

La proyección MEMORY debe ser reconstruible y mostrar conflictos, no elegir silenciosamente una fuente. La fuente canónica por clase de dato debe quedar explícita en el contrato.

## 5. Pruebas de aceptación faltantes

1. Registrar una observación en REVIVIR, reiniciar proceso y recuperar el mismo evento y hash.
2. Importar una referencia a la propuesta en ACS sin promoverla a hecho.
3. Verificar recibo firmado contra clave y SHA fijados; rechazar firma alterada o fuente distinta.
4. Registrar decisión humana en Core con actor/authority y verificar que la proyección la muestre sin duplicar autoridad.
5. Reconstruir el mapa desde ledger + Git y marcar diferencias frente a Core.
6. Abrir un chat limpio, leer MEMORY y recuperar decisiones, bloqueos y siguiente acción sin contexto previo.
7. Simular conflicto entre ledger, Core y Git; el resultado debe ser `CONFLICTED/UNKNOWN`, no verde.
8. Verificar que la automatización no puede hacer commit/push sin autorización; revisar PR #68 y sus checks.

**Estado:** arquitectura propuesta para revisión; no implementada; no se ejecutaron tests.
