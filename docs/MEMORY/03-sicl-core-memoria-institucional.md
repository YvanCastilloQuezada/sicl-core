# Auditoría 3 — SICL Core y memoria institucional

**Perspectiva:** modelo de dominio, persistencia canónica, autorización y compatibilidad.

## 1. La memoria ya existe como concepto en Core

En `sicl-core`, `docs/RFC-011_INSTITUTIONAL_MEMORY.md` describe `InstitutionalMemory` como una **proyección global** derivada de proyectos cerrados, no como entidad canónica de `Project`. Los tipos documentados son:
- `DECISION_PATTERN`
- `PREFERENCE_PATTERN`
- `EVALUATION_PATTERN`
- `GENERATION_PATTERN`
- `LESSON_LEARNED`

Los estados son `ACTIVE`, `SUPERSEDED`, `REVOKED`; confianza: `HIGH`, `MEDIUM`, `LOW`, `UNKNOWN`.

El RFC afirma persistencia append-only, una fila por versión, triggers SQLite que rechazan UPDATE/DELETE directos, revocación por nueva versión y prohibición de aplicar memorias revocadas. La extracción requiere proyecto `CLOSED`, `actor` y `authority` humanos. La aplicación registra `INSTITUTIONAL_MEMORY_APPLIED` y no crea una Decision ni altera automáticamente las entidades del proyecto destino.

Fuentes:
- [RFC-011](https://github.com/YvanCastilloQuezada/sicl-core/blob/main/docs/RFC-011_INSTITUTIONAL_MEMORY.md)
- [Contrato Core](https://github.com/YvanCastilloQuezada/sicl-core/blob/main/docs/SICL_CORE_CONTRACT_v1.0.md)
- [Repositorio de persistencia](https://github.com/YvanCastilloQuezada/sicl-core/blob/main/src/sicl/repository.py)

## 2. Diferencia importante entre rama RFC y main

El contenido consultado de RFC-011 en la rama `rfc-011-institutional-memory` y el contenido que devuelve la búsqueda para el SHA de `main` muestran que los documentos/código de memoria también están presentes en el árbol de main. Sin embargo, el encabezado del RFC identifica la rama histórica donde se implementó. La presencia en main no sustituye una comprobación de CI o una prueba actual de la API. El estado `IMPLEMENTED` es una declaración documental hasta validar comportamiento en el SHA objetivo.

## 3. Compatibilidad con REVIVIR y Mapas Vivos

RFC-011 tiene un propósito más estrecho que el MEMORY que el usuario está planteando:
- RFC-011 conserva patrones derivados de proyectos cerrados;
- REVIVIR registra observaciones operativas, déficits, propuestas y recibos de experimentos;
- Mapas Vivos conserva contexto de trabajo, genealogía Git, pendientes y handoff entre chats.

No conviene forzar todas estas entidades en el tipo `InstitutionalMemory`. Se necesita un mapa de correspondencias y un contrato de integración: qué entidad es canónica, qué evento se emite, qué referencia se conserva, qué se proyecta y qué requiere autorización.

## 4. Riesgos de diseño a revisar

- El extracto de `src/sicl/memory.py` construye un resumen concatenando texto de decisiones, preferencias, evaluaciones y generación. Debe verificarse que las políticas de anonimización y sensibilidad cubran también texto libre, identificadores dentro de frases y referencias de evidencia; no basta con anular `project_id_source`.
- El resumen se clasifica con un solo tipo mediante prioridad condicional (`_type_for`). Un proyecto con decisiones y preferencias puede quedar representado solo como `DECISION_PATTERN`; evaluar si se pierde información o si el esquema pretende un tipo primario único.
- El RFC declara referencias de evidencia/decisiones; se debe verificar integridad referencial y acceso posterior a esas fuentes.
- La extracción debe respetar autoridad humana, minimización de datos y revocación en todas las rutas (CLI, HTTP, servicios).
- La memoria institucional de proyectos cerrados no reemplaza el estado operativo de un proyecto activo ni una bitácora de recuperación entre sesiones.

Estos puntos son riesgos que se desprenden del diseño inspeccionado; requieren revisión de tests y rutas completas antes de declararse defectos.

## 5. Recomendación

Core debe seguir siendo autoridad canónica para entidades de dominio, decisiones y eventos institucionales. MEMORY debe consumir APIs/contratos del Core y guardar referencias, no escribir directamente sobre tablas ni crear un Event Store paralelo. El contenido documental de continuidad puede conservarse en Web como vista generada, pero el estado canónico debe poder reconstruirse desde Core y evidencia verificable.

**Estado:** análisis arquitectónico preliminar. No se ejecutaron tests ni se alteró Core.
