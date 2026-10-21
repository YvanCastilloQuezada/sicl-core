# SICL Core — reconciliación estática del contrato MEMORY (2026-10-21)

**Base inspeccionada:** `sicl-core/main@de43b6b833731c87fb6277834484545bd953d76a`. Lectura estática de documentos/código/tests; no se ejecutó pytest.

## 1. Archivos y SHA observados

| Archivo | SHA de blob |
|---|---|
| `docs/RFC-011_INSTITUTIONAL_MEMORY.md` | `614839115403895188eef84083d74906bd126823` |
| `src/sicl/memory.py` | `ce1dd164c029ca1f7dd2794e9e78a68480cc172b` |
| `tests/test_institutional_memory.py` | `6485382209b06950cfc4e6ecb9e0b30ec923b2c6` |
| `src/sicl/repository.py` | `baf65ae8b518f00f52a987331f83b69fa99ed4ec` |
| `docs/COMMANDS_REFERENCE.md` | `fa7b88a90f12d8044e940a4fdf3d775c7eb8f741` |
| `src/sicl/cli.py` | `d617b93687e4741516f1fb1bd8df48a72f39e79b` |
| `docs/SICL_CORE_CONTRACT_v1.0.md` | `be25dd622107c40455df431d0da8805be2613b97` |

## 2. Capacidad observada en código

- `extract_memory` rechaza proyectos cuyo stage no sea `CLOSED`.
- El CLI exige `project_id`, `actor` y `authority` para extraer y revocar; el evento registra actor y autoridad.
- La persistencia crea una tabla versionada `institutional_memory` y triggers que rechazan UPDATE/DELETE.
- Revocación crea una nueva versión; una memoria revocada no puede aplicarse.
- Aplicar memoria registra un evento y los tests verifican que no se modifiquen hechos/preferencias ni se cree una decisión.
- Los tests contienen casos para extracción/anónimo, proyecto abierto, list/show/types, autoridad para revocar, rechazo de revocada, aplicación sin cambio canónico, append-only/persistencia y endpoints HTTP. Son pruebas existentes, no resultados ejecutados en esta auditoría.

## 3. Conflicto documental confirmado

`docs/COMMANDS_REFERENCE.md` todavía documenta una sintaxis antigua:
- `/MEMORY EXTRACT <type> <title> <content>`
- `/MEMORY REVOKE <memory_id>`
- `/MEMORY APPLY <memory_id>`

Pero el RFC-011 y el CLI actual exigen para extracción `/MEMORY EXTRACT <project_id> <actor> <authority>`, y para revocación `/MEMORY REVOKE <memory_id> <actor> <authority>`. El CLI de aplicación recibe `<memory_id> <project_id>` y usa el actor de la sesión; el RFC lo describe así, mientras que otro documento de arquitectura enumera una forma distinta. Esto es una discrepancia documental verificable y puede inducir al operador a ejecutar comandos incorrectos.

**Acción recomendada:** reconciliar manuales y referencias con el CLI real, manteniendo la semántica constitucional del RFC. No se modificó el manual ni el código.

## 4. Riesgos de diseño a evaluar — no defectos confirmados

### 4.1 Anonimización del contenido

En `src/sicl/memory.py`, `anonymize=True` pone `project_id_source=None`, pero el resumen concatena texto libre de decisiones y preferencias, además de valores de evaluación. No se observa en esta función una sanitización de PII dentro de esos fragmentos. El nulo del identificador directo no garantiza anonimización del contenido. Se requiere un test adversarial con nombres, direcciones, teléfonos u otros identificadores dentro de los statements; registrar el resultado antes de afirmar fuga o seguridad.

### 4.2 Una sola categoría por proyecto

`_type_for` devuelve una sola categoría con prioridad decisiones > preferencias > evaluaciones > generación > lección. Un proyecto con varias clases de patrones queda clasificado por una sola. Puede ser una decisión de diseño válida, pero para MEMORY transversal debe evaluarse si pierde conocimiento útil o si conviene producir varias proyecciones independientes con trazabilidad.

### 4.3 Confianza automática

La implementación asigna `MEDIUM` si existen fragmentos, sin que esta función verifique por sí sola la calidad de la evidencia enlazada. Para MEMORY, la confianza debe distinguir presencia de texto, referencia de evidencia, verificación independiente y aplicabilidad. No elevar el valor de confianza sin revisar el contrato y los datos.

## 5. Consecuencia para la integración global

RFC-011 ofrece una base real de persistencia institucional, pero no debe confundirse con continuidad operativa de proyectos abiertos, ledger de eventos de REVIVIR o snapshot de Mapas Vivos. Antes de conectarlos se necesita definir:
1. qué tipo de evento de Web se puede proyectar en Core;
2. qué referencias de evidencia y SHA son obligatorias;
3. cómo se manejan conflictos, revocación y corrección sin borrar historial;
4. qué datos pueden salir del proyecto y bajo qué política de anonimización;
5. qué estado se recupera al iniciar una sesión limpia.

**Estado:** análisis documental/código; tests no ejecutados; sin cambios funcionales.
