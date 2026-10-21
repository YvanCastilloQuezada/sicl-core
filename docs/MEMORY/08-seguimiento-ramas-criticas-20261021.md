# Seguimiento crítico de ramas — MEMORY (2026-10-21)

**Rama documental:** `docs/memory-auditoria-integracion-20261021`  
**Base Web:** `main@9ae8fe504bbb964d8b89d87709ee773e64cbbacb`  
**Base Core:** `main@de43b6b833731c87fb6277834484545bd953d76a`  
**Alcance:** segunda lectura de diferencias de ramas críticas y control de escritura del workflow. Lectura estática de GitHub; no se ejecutaron pruebas.

## 1. SICL Web — ramas críticas reconsultadas

| Rama | Ahead | Behind | Rutas únicas | Dictamen de auditoría |
|---|---:|---:|---:|---|
| `feat/arki-autonomy-memory-main-20261013` | 8 | 59 | 4 | Divergente. Añade el journal de eventos con hash y tests, además de dos catálogos históricos. No es la base de continuidad ni persiste por sí mismo. |
| `feat/arbol-vivo-precedencias-seguras-20261010` | 741 | 59 | 140 | Divergencia muy grande. Incluye workflows, interfaz y documentación de Árbol/Gemelo. No rescatar como bloque; revisar por contrato y dependencia. |
| `feat/arki-autonomy-orchestrator-20261013` | 915 | 59 | 264 | Divergencia muy grande. El módulo leído es planificador/gate y declara ejecución y mutación canónica desactivadas. |
| `feat/arki-operational-vitality-mo05-20261015` | 958 | 59 | 300 | Divergencia muy grande. Motor experimental de déficits/candidatos; no demuestra ejecución ni aprendizaje. |
| `experiment/arki-ideas-mapa-vivo-20261015` | 62 | 57 | 46 | Rama experimental con ledger de extracción, recibos y pruebas pendientes; no es integración productiva. |

Los contadores son comparaciones contra el SHA de Web main indicado arriba, no medidas de calidad ni evidencia de tests. Una rama puede contener trabajo útil y a la vez tener una base antigua; el número de commits exclusivos no justifica fusionarla.

## 2. Workflow de continuidad — riesgo de escritura

El workflow de continuidad de Web main declara `contents: write`, checkout con `persist-credentials: true`, regenera el snapshot y puede hacer commit/push automático. Por tanto, el propio workflow tiene una ruta de mutación remota.

PR #68, `fix(arki): make continuity workflow read-only`, se consultó como `OPEN`, `merged=false`, `mergeable=true`. El cambio propuesto reduce permisos a `contents: read`, desactiva credenciales persistentes y elimina los pasos de commit/push. El cuerpo del PR afirma que CI fue exitoso en el SHA `33f3cd5b7aa1fcdac9d967a264a7618d7eb9ed0a`; no se verificaron independientemente los logs citados. No se hizo merge.

**Prioridad recomendada:** resolver este control antes de automatizar la actualización de MEMORY o del Mapa Vivo. No asumir que el riesgo ya está corregido mientras el PR no esté integrado y verificado.

## 3. Integridad del catálogo de ramas

La cabeza observada de `feat/arki-autonomy-memory-main-20261013` es `e7237c6f8c671a7a1325fdf87d18b70b6dfda4a8`, pero el catálogo `ARKI_BRANCH_COMMIT_CATALOG_20261021.md` conserva otra SHA (`bdfefedb38a0a8cc1dfdbdea097b77594141777f`). Es una discrepancia concreta entre catálogo y API de refs. MEMORY debe registrar ambos con fecha/fuente y refrescar el catálogo; no seleccionar silenciosamente uno como si fueran equivalentes.

## 4. Consecuencia para MEMORY

1. Core sigue siendo la autoridad para eventos y decisiones de dominio.
2. REVIVIR registra observaciones/propuestas/recibos; su adaptador local no demuestra almacenamiento compartido.
3. Mapas Vivos es una proyección reconstruible, no Event Store.
4. Living Memory experimental no prueba persistencia durable ni autenticidad independiente.
5. ACS aporta resultados de laboratorio; su documentación declara límites de aislamiento.
6. Ninguna promoción debe depender solo de una rama, un documento, un nombre de test o un estado declarado.

## 5. Pendientes explícitos

- Confirmar estado actual de PR #68 y sus checks con logs del SHA exacto.
- Revisar cada commit exclusivo de las ramas grandes de Árbol/orquestación/vitalidad antes de seleccionar componentes.
- Ejecutar la suite pertinente en entorno controlado y guardar los logs/recibos; no se hizo en esta auditoría.
- Localizar los cómics fuera de la búsqueda de código de las ramas por defecto; continúan `UNKNOWN`.
- Demostrar recuperación E2E desde una sesión limpia, incluyendo conflicto de datos, revocación, restauración y bloqueo de mutaciones no autorizadas.

**Estado:** análisis y documentación; no implementación, no merge, no publicación de software.
