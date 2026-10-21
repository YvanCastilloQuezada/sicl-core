# MEMORY — auditoría de integración ARKI

**Fecha de corte de esta primera entrega:** 2026-10-21 (Perú)  
**Estado:** auditoría documental inicial; NO es autorización de implementación ni declaración de integración terminada.  
**Rama de documentación:** `docs/memory-auditoria-integracion-20261021`  
**Repositorios examinados:** `YvanCastilloQuezada/sicl-web`, `YvanCastilloQuezada/sicl-core`, `YvanCastilloQuezada/arki-acs`.

## Propósito

Investigar cómo reunir **REVIVIR ARKI** (adaptador de auto-mejora operativa), **Mapas Vivos** (continuidad y contexto de trabajo) y la memoria institucional ya especificada en SICL Core bajo una arquitectura coherente denominada **MEMORY**, sin crear una segunda fuente canónica, sin elevar propuestas a hechos y sin modificar contratos protegidos.

## Cinco auditorías

1. [Fundamentos, doctrina y conocimiento preservado](01-fundamentos-doctrina-conocimiento.md)
2. [SICL Web, REVIVIR y Mapas Vivos](02-sicl-web-revivir-mapas-vivos.md)
3. [SICL Core y memoria institucional](03-sicl-core-memoria-institucional.md)
4. [ACS: laboratorio, experimentación y evidencia](04-acs-laboratorio-evidencia.md)
5. [Integración, seguridad, recuperación y plan de pruebas](05-integracion-seguridad-plan.md)

## Auditoría de ramas — inventario acumulativo

Se descubrieron 209 referencias: 97 en Web, 109 en Core (incluida esta rama documental) y 3 en ACS. Las comparaciones se hacen contra `main` del repositorio respectivo. “Behind” no significa necesariamente pérdida; puede significar que la historia de la rama está contenida en main. “Ahead/diverged” no autoriza merge.

### SICL Web
- [Registro de las 97 ramas y SHAs](branches/sicl-web-branch-register.md)
- [Lote 1 — memoria, continuidad y Árbol Vivo](branches/sicl-web-branch-audit-01.md)
- [Lote 2 — histórico, sincronización y auditorías](branches/sicl-web-branch-audit-02.md)
- [Lote 3 — CI y documentación](branches/sicl-web-branch-audit-03.md)
- [Lote 4 — RFC, ideas, ACS y AGK](branches/sicl-web-branch-audit-04.md)
- [Lote 5 — AGK, ensamblaje y vitalidad](branches/sicl-web-branch-audit-05.md)
- [Lote 6 — UI, puentes espaciales y F7–F8](branches/sicl-web-branch-audit-06.md)
- [Lote 7 — rendimiento, idioma y Mapas Vivos](branches/sicl-web-branch-audit-07.md)
- [Lote 8 — interfaz y pilotos espaciales](branches/sicl-web-branch-audit-08.md)
- [Lote 9 — visualización, promoción, correcciones y rendimiento](branches/sicl-web-branch-audit-09.md)
- [Lote 10 — red team, RFC y pruebas](branches/sicl-web-branch-audit-10.md)
- [Lote 11 — baseline y experimento Mapas Vivos](branches/sicl-web-branch-audit-11.md)

**Estado:** 97 nombres/SHAs registrados; análisis por lotes documentado. Algunas ramas requieren inspección de archivos/PR y verificación de CI antes de un dictamen final. Las ramas divergentes grandes tienen una lectura de alcance inicial, no una revisión exhaustiva de cada commit.

### SICL Core
- [Registro de las 109 ramas y SHAs](branches/sicl-core-branch-register.md)
- [Lote 1 — historia y documentación](branches/sicl-core-branch-audit-01.md)
- [Lote 2 — arquitectura y Mapas Vivos P0](branches/sicl-core-branch-audit-02.md)
- [Lote 3 — Mapas Vivos, operación y copilot](branches/sicl-core-branch-audit-03.md)
- [Lote 4 — proceso, manuales y A-002](branches/sicl-core-branch-audit-04.md)
- [Lote 5 — representación 3D y ARE](branches/sicl-core-branch-audit-05.md)
- [Lote 6 — persistencia, validación y promoción](branches/sicl-core-branch-audit-06.md)
- [Lote 7 — contrato de eventos y promoción](branches/sicl-core-branch-audit-07.md)
- [Lote 8 — recomputación, Mapas Vivos y RFC](branches/sicl-core-branch-audit-08.md)
- [Lote 9 — VSM, DAM y UPAO-001](branches/sicl-core-branch-audit-09.md)
- [Lote 10 — integración, despliegue y contexto ambiental](branches/sicl-core-branch-audit-10.md)
- [Lote 11 — mapa vivo y RFC 001–006](branches/sicl-core-branch-audit-11.md)
- [Lote 12 — RFC 006–013](branches/sicl-core-branch-audit-12.md)
- [Lote 13 — RFC 013–029](branches/sicl-core-branch-audit-13.md)
- [Lote 14 — GIS, pruebas y baseline](branches/sicl-core-branch-audit-14.md)

### ARKI-ACS
- [Registro de las 3 ramas y SHAs](branches/arki-acs-branch-register.md)
- [Auditoría de las tres ramas](branches/arki-acs-branch-audit.md)

**Precisión del alcance:** se han comparado las referencias de las 209 ramas contra `main` y documentado sus metadatos, estados de divergencia y lectura inicial por propósito. “Informe por rama” significa que cada rama tiene una sección identificada; no significa que se haya leído línea por línea cada commit histórico. Las ramas con commits exclusivos, diferencias de seguridad o potencial relación con MEMORY necesitan una segunda pasada de archivos/PR/CI antes de cerrar su dictamen.

### Segunda pasada — código de MEMORY y continuidad
- [06 — Hallazgos directos en ramas críticas de MEMORY](06-segunda-pasada-ramas-memory-criticas.md)
- [07 — Árbol Vivo, orquestación y experimentos](07-segunda-pasada-arbol-orquestacion-experimentos.md)

Esta segunda pasada ya lee directamente el módulo de journal de REVIVIR, el adaptador persistente, el Living Memory experimental, el generador de Mapas Vivos y el código/tests de RFC-011 en Core. Detectó también que el catálogo histórico de ramas de Web tiene una cabeza de rama MEMORY desfasada frente a la lista actual de refs de GitHub.

## Dictamen preliminar

Los repositorios ya contienen **tres capacidades relacionadas pero distintas**:

- **Memoria institucional de Core (RFC-011):** proyección versionada derivada de proyectos cerrados; append-only; requiere actor/autoridad humana para extraer y revocar; no toma decisiones ni aplica contenido automáticamente.
- **REVIVIR ARKI en Web:** adaptador operativo que persiste observaciones, déficits y propuestas en un almacén JSON local protegido por bloqueo, escritura atómica y validación de eventos; la respuesta declara explícitamente que observar/proponer no ejecuta experimentos ni verifica aprendizaje.
- **Mapas Vivos en Web:** snapshot documental generado desde Git y un ledger JSONL de eventos declarados. El propio documento aclara que no es el Event Store canónico de Core ni verifica CI, arquitectura o despliegue.

ACS es un laboratorio de evaluación de capacidades, no el sistema canónico ni una frontera de seguridad completa. Por tanto, MEMORY no debe consistir en concatenar los tres mecanismos ni en tratar sus registros como equivalentes.

## Propuesta de dirección (no aprobada ni implementada)

Definir MEMORY como **arquitectura de continuidad con una única autoridad por clase de dato**, capaz de recuperar estado, decisiones autorizadas, evidencia, experimentos, pendientes y siguiente acción. Core conserva la autoridad sobre entidades/eventos de dominio; Web presenta y orquesta; el mapa vivo es una proyección legible y regenerable; REVIVIR aporta observaciones/propuestas/recibos; ACS aporta evidencia experimental con procedencia. Cualquier promoción debe ser explícita, validada y auditable.

## Límites de esta entrega

- Los hallazgos citados provienen de los archivos de los repositorios indicados. No se ejecutaron pruebas de código en esta auditoría documental.
- Las etiquetas `IMPLEMENTED` de documentos son declaraciones de esos documentos, no una verificación independiente de CI ni del comportamiento desplegado.
- No se localizaron cómics/historietas en las búsquedas de código realizadas hasta ahora. Esto **no demuestra que no existan** en otros repositorios, carpetas, conversaciones o archivos.
- La revisión de fundamentos y cómics permanece abierta hasta inventariar las fuentes completas.
- No se modificó `main`, no se hizo merge, no se publicó software y no se cambió código funcional. Solo se creó esta rama documental y se escriben informes en ella.

## Fuentes principales

- Web: [Fundamentos ARKI/SICL](https://github.com/YvanCastilloQuezada/sicl-web/blob/main/docs/ARKI_AND_SICL_FOUNDATIONS.md)
- Web: [Mapa Vivo de Continuidad](https://github.com/YvanCastilloQuezada/sicl-web/blob/main/docs/arki-master-map/ARKI_MAPA_VIVO_CONTINUIDAD.md)
- Web: [Snapshot de continuidad](https://github.com/YvanCastilloQuezada/sicl-web/blob/main/tools/maqueta-viva/arki-continuity-snapshot.cjs)
- Web: [Adaptador REVIVIR](https://github.com/YvanCastilloQuezada/sicl-web/blob/main/tools/maqueta-viva/arki-automejora-operativa.cjs)
- Core: [RFC-011 Institutional Memory](https://github.com/YvanCastilloQuezada/sicl-core/blob/main/docs/RFC-011_INSTITUTIONAL_MEMORY.md)
- ACS: [Arquitectura](https://github.com/YvanCastilloQuezada/arki-acs/blob/main/docs/ARCHITECTURE.md), [modelo de seguridad](https://github.com/YvanCastilloQuezada/arki-acs/blob/main/docs/SECURITY_MODEL.md)

## Próxima actualización

Completar el inventario de fundamentos, catálogos de conceptos congelados/históricos, artefactos visuales/cómics y referencias cruzadas; después comparar contra la implementación de `main` y los branches de RFC/REVIVIR sin asumir que una rama experimental ya está integrada.


## Actualización de fundamentos y fuentes visuales — 2026-10-21

La auditoría 01 se amplió con el paquete de preservación de conocimiento de Web main: 13 libros Excel versionados, con manifest y hashes SHA-256; ingesta automática de runtime deshabilitada. También se revisaron el inventario FROZEN/histórico y el inventario de ideas/decisiones (este último corresponde a una base histórica de septiembre, no al HEAD actual).

**Cómics/historietas:** se consultó la búsqueda de código de GitHub en las ramas por defecto de los tres repositorios para `comic`, `cómic`, `historieta`, `viñeta` y `storyboard`; no hubo resultados. El inventario de cómics permanece `UNKNOWN / PENDIENTE DE LOCALIZACIÓN`: la búsqueda no cubre necesariamente binarios, adjuntos, otras ramas ni archivos externos. No declarar completa esa parte de la auditoría hasta localizar las fuentes.

**Siguiente trabajo:** seguir la segunda pasada por ramas divergentes y registrar diferencias verificables por SHA/PR/CI; después completar el inventario de conceptos congelados, antecedentes y cómics que no estén en el código de las ramas por defecto.
