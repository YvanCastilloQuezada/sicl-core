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
