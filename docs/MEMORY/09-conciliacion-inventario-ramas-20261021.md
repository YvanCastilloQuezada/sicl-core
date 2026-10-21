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
