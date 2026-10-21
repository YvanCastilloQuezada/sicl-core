# Segunda pasada — ramas críticas para MEMORY: código y contratos concretos

**Fecha de revisión:** 2026-10-21  
**Alcance:** inspección directa de fuentes de Web/Core relacionadas con MEMORY y continuidad. Esta es una lectura estática de archivos de GitHub; no se ejecutaron tests ni se verificó un despliegue.

## 1. Web: `feat/arki-autonomy-memory-main-20261013`

- SHA de cabeza observado en la lista de ramas: `e7237c6f8c671a7a1325fdf87d18b70b6dfda4a8`.
- Comparación contra `sicl-web/main@9ae8fe504bbb964d8b89d87709ee773e64cbbacb`: `diverged`, 8 commits exclusivos, 59 por detrás; diff reporta cuatro rutas.
- El catálogo histórico `ARKI_BRANCH_COMMIT_CATALOG_20261021.md` contiene otro SHA de cabeza para la misma rama (`bdfefedb38a0a8cc1dfdbdea097b77594141777f`). Por tanto, ese catálogo está desfasado respecto de la cabeza que la API de ramas devolvió en esta auditoría. MEMORY debe conservar ambos como observación fechada y volver a consultar antes de confiar en el catálogo.

### `tools/maqueta-viva/arki-autonomy-memory.cjs`

El módulo declara un journal determinista, con hash SHA-256, cadena desde un hash génesis de 64 ceros y tipos de evento:
`OBSERVATION`, `DEFICIT`, `PROPOSAL`, `EXPERIMENT_RESULT`, `TEST_RESULT`, `HUMAN_DECISION`, `BLOCKED`, `REASSESSMENT`.

Cada evento exige secuencia, `previousHash`, sujeto, `sourceSha` de 40 caracteres hexadecimales, `evidenceRef`, payload y hash consistente. `validate` rechaza alteración, reordenamiento o falta de eventos. `record` devuelve una nueva lista en memoria. **`summarize` declara literalmente `storage: "NOT_PERSISTED_BY_THIS_MODULE"`** y `canonicalMutation: false`.

Conclusión precisa: el módulo es una primitiva de integridad de eventos, no un almacén persistente autónomo. La persistencia que sí aparece en Web está en el adaptador separado `arki-automejora-operativa.cjs`; no deben confundirse ambos archivos ni atribuir al módulo de journal el almacenamiento del adaptador.

### `test-arki-autonomy-memory.cjs`

Contiene cinco pruebas declaradas:
1. añadir y validar un evento;
2. replay determinista;
3. detectar manipulación de payload;
4. detectar reordenamiento/eventos ausentes;
5. rechazar procedencia inválida.

No se ejecutaron en esta revisión. La existencia de estas pruebas no es un resultado actual de ejecución.

## 2. Web: `feat/arbol-vivo-precedencias-seguras-20261010`

El archivo `tools/maqueta-viva/arki-living-memory.cjs` existe en esta rama y **no se encontró en main** durante la consulta directa. Su comentario la califica como experimental: event log append-only y read model determinista; sin hooks de GitHub, sin ingesta automática y sin mutación canónica.

Tipos admitidos: `COMMIT_OBSERVED`, `CI_OBSERVED`, `AUDIT_RECEIVED`, `DECISION_RECORDED`, `EXPERIMENT_REPORTED`, `TEST_OBSERVED`. Estados de evidencia: `DECLARED`, `VERIFIED`, `CONTRADICTED`, `UNKNOWN`. Los eventos requieren ID, fecha, fuente, resumen, sujeto, estado epistemológico y SHA nulo o de 40 hexadecimales.

`appendEvent` devuelve `APPENDED_LOCAL`, enlaza `previousHash) al hash del registro previo y no modifica el estado canónico. `deriveMemory` devuelve `DERIVED_EXPERIMENTAL`, lista elementos no verificados y fija `criticalPath: "UNKNOWN"`, `promotion: "BLOCKED"`, `execution: "BLOCKED"`, `canonicalMutation: false`.

Conclusión precisa: este read model tampoco demuestra persistencia durable; opera sobre un log pasado como argumento. Es un antecedente experimental de MEMORY y no se debe presentar como sistema integrado.

## 3. Web main: Mapas Vivos de continuidad

### `arki-continuity-snapshot.cjs`

- Usa Git como evidencia de commits, no de decisiones ni de CI.
- Lee `ARKI_CONTINUITY_EVENTS.jsonl`, valida JSON por línea, campos obligatorios, fecha y IDs duplicados.
- Genera una vista con SHA/branch, historial, eventos declarados, última acción y pendientes.
- Declara explícitamente que el mapa no es Event Store canónico de Core ni verifica CI, arquitectura o despliegue.
- Expone `--check` para comprobar si el snapshot generado está actualizado.

### `ARKI_MAPA_VIVO_CONTINUIDAD.md` en main

El snapshot observado muestra:
- estado de Core/D-2/AGK: `NOT_VERIFIED`;
- CI exacto y E2E: `NOT_VERIFIED`;
- promoción canónica: `NO_AUTORIZADA_POR_ESTE_MAPA`;
- continuidad automática y Mapa Vivo como prioridad P0 según una decisión declarada en el ledger;
- fallos de CI históricos y varias acciones que figuran como `IMPLEMENTED_NOT_VERIFIED` o `AWAITING_LOCAL_EXECUTION`.

No convertir esos estados históricos en estado actual sin consultar SHA y logs.

### `arki-continuity-local-verify.cjs`

Define un protocolo local que registra branch, HEAD, HEAD esperado, plataforma, comandos y salidas; ejecuta test de snapshot, generación y `--check`, y falla si el HEAD no coincide con el esperado. El código es un protocolo de validación, no evidencia de que se haya ejecutado ahora.

## 4. Web main: adaptador REVIVIR

`arki-automejora-operativa.cjs` requiere ruta absoluta del store, bloqueo exclusivo mediante archivo `.lock`, valida el esquema y los eventos, limita el tamaño a 10 MB, rechaza symlinks/no archivos regulares y persiste mediante temporal + `fsync` + `rename`. También valida referencias de evidencia. Esto es más que el módulo de journal en memoria, pero aún es un archivo local: no prueba almacenamiento compartido entre instancias ni integración con Core.

La respuesta del adaptador para observación declara `OBSERVATION_AND_PROPOSAL_ONLY`, `experimentExecuted: false`, `learningVerified: false`, `canonicalMutation: false`. Un resultado de propuesta no es un resultado de experimento.

## 5. Core main: RFC-011 Institutional Memory

El RFC define una proyección global derivada de proyectos cerrados; no reescribe hechos/decisiones ni reemplaza la fuente canónica. Requiere actor y autoridad humana para extracción/revocación, soporta estados ACTIVE/SUPERSEDED/REVOKED y exige versión nueva para revocación. La aplicación de memoria no altera las entidades canónicas del proyecto destino.

### Código `src/sicl/memory.py`

- Rechaza proyectos que no estén `CLOSED`.
- Compone un resumen concatenando decisiones, preferencias, evaluaciones y generación.
- Elige un solo tipo por prioridad: decisiones > preferencias > evaluaciones > generación > lección aprendida.
- `anonymize=True` anula `project_id_source`, pero el texto del resumen se compone de fragmentos libres de decisiones/preferencias. Debe verificarse si las políticas de privacidad también detectan datos personales dentro de ese texto; el nulo del ID no basta por sí solo.
- La clasificación de un solo tipo puede ocultar que el proyecto contiene varios patrones. Esto es una decisión del esquema que merece revisión, no un defecto confirmado sin contrastar intención y tests.

### Tests existentes

`tests/test_institutional_memory.py` cubre extracción/anónimo, rechazo de proyecto abierto, list/show/types, revocación con autoridad, rechazo de memoria revocada y aplicación sin cambio del estado canónico. No se ejecutó pytest durante esta auditoría.

## 6. Dictamen integrado de la segunda pasada

No hay evidencia de una única MEMORY integrada de extremo a extremo. Hay:
1. **Core RFC-011:** memoria institucional persistente/versionada de proyectos cerrados.
2. **Web REVIVIR:** observaciones/propuestas y un adaptador de persistencia local.
3. **Web continuity snapshot:** proyección documental regenerable de Git + ledger declarado.
4. **Living Memory experimental:** modelo de eventos/read model sin persistencia durable demostrada.
5. **ACS:** experimentación que debe aportar evidencia con límites explícitos.

El trabajo siguiente no es fusionar ramas enteras. Es especificar un contrato de continuidad común, conservar una autoridad por clase de dato, fijar los SHAs exactos y demostrar recuperación E2E en una sesión limpia. Ninguna prueba se declara aprobada aquí.
