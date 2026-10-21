# MEMORY — conciliación del inventario de ramas (2026-10-21)

**Consulta de refs GitHub:** 2026-10-21. Se consultó la API de ramas paginada hasta agotar resultados; todas las páginas devueltas tenían UTF-8 válido.

| Repositorio | Páginas | Ramas/referencias de rama devueltas |
|---|---:|---:|
| `YvanCastilloQuezada/sicl-web` | 1 (97) | 97 |
| `YvanCastilloQuezada/sicl-core` | 2 (100 + 9) | 109 |
| `YvanCastilloQuezada/arki-acs` | 1 (3) | 3 |
| **Total** | | **209** |

Los conteos coinciden con el inventario documental actual. El registro de Core incluye la rama de documentación MEMORY creada para esta auditoría; por eso el número puede ser superior a una fotografía tomada antes de crearla.

## Qué significa “auditoría de todas las ramas”

- Las 209 refs están registradas por nombre y SHA en los registros correspondientes.
- Los informes por lote comparan las refs contra el `main` observado de cada repositorio y dan una lectura de propósito, commits exclusivos/atraso y rutas únicas cuando la API de comparación las devuelve.
- No todas las ramas han tenido una revisión línea por línea de cada commit. Las ramas con divergencias grandes y las que afectan MEMORY, continuidad, orquestación, persistencia, autorización o seguridad requieren revisión profunda por archivo/PR/CI.
- “Behind” con cero commits exclusivos significa que la historia de esa rama ya está contenida en la línea base comparada; no implica que su idea sea irrelevante, pero no prueba que el comportamiento esté activo en main sin verificar los archivos actuales.
- “Diverged/ahead” no autoriza merge. Los informes no modifican ramas de producto.

## Hallazgos que requieren prioridad

1. **Web workflow de continuidad:** main conserva un workflow con permisos de escritura y commit/push automático; PR #68 propone solo lectura y sigue abierto/no fusionado según la consulta.
2. **MEMORY de Web:** el journal de eventos no persiste por sí solo; el adaptador de REVIVIR persiste en JSON local.
3. **Mapas Vivos:** es una proyección documental y no el Event Store canónico de Core.
4. **Core RFC-011:** existe una memoria institucional de proyectos cerrados, pero no se ha demostrado que cubra por sí sola la continuidad de trabajo activo ni el E2E con Web y ACS.
5. **ACS:** la documentación declara que contenedor/microVM no están implementados y que los límites CPU/RAM no están aplicados por IsolatedWorker.
6. **Cómics:** no se encontraron nombres de archivo que coincidan en los árboles de main de los tres repositorios; contenido de binarios/adjuntos/otras ramas sigue sin inspección completa.

## Condición de cierre de auditoría

La auditoría no se considerará completa hasta que: (a) cada rama tenga una clasificación de avance y relación con main; (b) las ramas críticas divergentes tengan sus archivos y dependencias contrastados; (c) los resultados de CI/test se verifiquen por SHA y logs; (d) se localicen los cómics/fuentes visuales pendientes; y (e) se escriba el contrato de integración MEMORY sin duplicar la autoridad de Core.

**No se ejecutaron tests ni se hicieron merges en esta actualización.**

## Revalidación de referencias remotas y PR — 2026-10-21

Se volvió a consultar la API de ramas de GitHub, incluyendo todas las páginas devueltas:

| Repositorio | Ramas remotas actuales observadas | SHA de `main` |
|---|---:|---|
| `YvanCastilloQuezada/sicl-web` | 97 | `9ae8fe504bbb964d8b89d87709ee773e64cbbacb` |
| `YvanCastilloQuezada/sicl-core` | 109 | `de43b6b833731c87fb6277834484545bd953d76a` |
| `YvanCastilloQuezada/arki-acs` | 3 | `1a48ed4426b958cb45be2599efc1e8d624baab80` |

Los 209 nombres de ramas de los registros coinciden con las referencias remotas observadas. No se encontraron ramas faltantes ni nombres obsoletos. En el registro de Core, el SHA consignado para la propia rama MEMORY es una fotografía de su punta antes del commit que actualizó ese registro; una referencia a la punta de la misma rama dentro de un archivo versionado queda necesariamente una revisión atrás cuando ese archivo se confirma.

### PR de Web reconsultados

- PR #68 — `fix(arki): make continuity workflow read-only`: **OPEN, no fusionado**, head `33f3cd5b7aa1fcdac9d967a264a7618d7eb9ed0a`, base `main@9ae8fe504bbb964d8b89d87709ee773e64cbbacb`. Sigue pendiente; no se ejecutó merge ni se verificaron independientemente los logs de CI.
- PR #58 — `ARKI: isolated autonomy memory and integrity tests (main integration 1)`: **OPEN, DRAFT, no fusionado**, head `e7237c6f8c671a7a1325fdf87d18b70b6dfda4a8`. No se debe tratar como integrado en Web main.

### Comparaciones críticas reconsultadas

- `sicl-core:rfc-011-institutional-memory` frente a Core main: `ahead=0, behind=249`; no presenta commits exclusivos respecto de main. La rama es histórica respecto de la base actual, pero el código y contrato de RFC-011 deben evaluarse en main, no atribuirse a una integración pendiente de esa rama.
- `sicl-web:feat/arki-autonomy-memory-main-20261013`: `ahead=8, behind=59`; cuatro rutas exclusivas reportadas, incluido el journal `arki-autonomy-memory.cjs` y su test. Continúa sin estar integrado en main.
- `sicl-web:fix/arki-continuity-workflow-readonly-20261021`: `ahead=7, behind=0`; modifica únicamente `.github/workflows/arki-continuity-map.yml` según la comparación. El cambio está propuesto en PR #68, aún abierto.

**Límite:** esta revalidación comprueba referencias, comparaciones y metadatos de PR; no ejecuta tests ni demuestra comportamiento desplegado. La revisión profunda de ramas divergentes y la evidencia de CI siguen abiertas.

