# ARKI — Expediente Maestro

**Fecha:** 2026-10-27
**Autor:** Yvan Castillo Quezada (Product Owner)
**Servidor:** Arki-001
**Estado:** Vigente al 27-oct-2026
**Repo:** `canonical/sicl-core` (HEAD `5dfd17a`)
**Ubicación:** `/home/arki/ARKI/canonical/sicl-core/00_ARKI_EXPEDIENTE_MAESTRO.md`

> Este documento es el índice navegable del proyecto ARKI al 27-oct-2026.
> No reemplaza a los documentos que enlaza; los organiza.
>
> **Regla de lectura:** fechas antes que nombres o versiones. Un archivo llamado "v2.0" puede ser más viejo que uno sin versión. La fecha de modificación y la fecha interna son el ancla.
>
> **Advertencia:** documentación no es implementación. Implementación no es demostración. Demostración no es generalización. Una mención no es conocimiento.

---

## Tabla de contenidos

- [Nivel 0 — Constitucional (Congelado)](#nivel-0--constitucional-congelado)
- [Nivel 1 — Auditoría y Estado Real](#nivel-1--auditoría-y-estado-real)
- [Nivel 2 — Arquitectura y Diseño](#nivel-2--arquitectura-y-diseño)
- [Nivel 3 — Implementación y RFCs](#nivel-3--implementación-y-rfcs)
- [Nivel 4 — Dominio y Aplicación](#nivel-4--dominio-y-aplicación)
- [Nivel 5 — Capacidades Críticas](#nivel-5--capacidades-críticas)
- [Nivel 6 — Evidencia Forense](#nivel-6--evidencia-forense)
- [Nivel 7 — Repositorios](#nivel-7--repositorios)
- [Nivel 8 — Decisiones Pendientes](#nivel-8--decisiones-pendientes)
- [Nivel 9 — Reglas de Navegación](#nivel-9--reglas-de-navegación)
- [Apéndice A — Cronología](#apéndice-a--cronología)
- [Apéndice B — Estado del servidor al 27-oct-2026](#apéndice-b--estado-del-servidor-al-27-oct-2026)

---

## Nivel 0 — Constitucional (Congelado)

**Estado:** Congelado. No cambia con las modas técnicas. Es la base de todo lo demás.

### Invariantes duros

| Invariante | Significado |
|---|---|
| **INV-000 (Ley Cero)** | El beneficio humano es condición necesaria y no negociable. Ninguna decisión de ARKI puede ignorarlo. |
| **RECOMMENDATION ≠ DECISION** | La IA recomienda. El humano decide. Nunca se automatiza la decisión profesional. |
| **UNKNOWN BEFORE INVENTING** | Si falta un dato, se marca `UNKNOWN`. No se rellena con datos inventados. |
| **SOURCE ≠ KNOWLEDGE** | Una fuente no es conocimiento canónico hasta pasar gates de validación humana. |
| **HUMAN AUTHORITY** | Ninguna decisión profesional se delega al sistema. La autoridad final es humana. |

### Documentos

| Documento | Ubicación | Estado |
|---|---|---|
| `ARKI_AND_SICL_FOUNDATIONS.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` | Vigente |
| `ARKI — PRINCIPIO FUNDACIONAL PF-H01.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` | Congelado |
| `ARKI Ciclo Cognitivo Core — FROZEN v1.0.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` | Congelado |
| `MANIFIESTO FUNDACIONAL DE SICL.docx` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` | Congelado |
| `ARKI_CORE_FROZEN_v1.0.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` | Congelado |

---

## Nivel 1 — Auditoría y Estado Real

**Estado:** Vigente al 23-oct-2026. Documenta qué está construido, qué no, y qué se corrigió.

### Documento de entrada

| Documento | Ubicación | Propósito |
|---|---|---|
| `_ESTADO_2026-10-23.md` | `/home/arki/ARKI/` (raíz del servidor) | Acta de cierre y auditoría forense del servidor. |
| `_REVISION_AUDITORIA_FORENSE_2026-10-23.md` | `/home/arki/ARKI/` (raíz del servidor) | Corrección de la auditoría original: las 5 capacidades que se decían inexistentes sí existen. |

### Complementarios

| Documento | Ubicación |
|---|---|
| `ARKI_POST_513_EXECUTIVE_SYNTHESIS.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` |
| `ARKI-C1C80-RECON-001 — Real Repository Reconciliation.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` |
| `Archi — Fase 0_ auditoría real del repositorio.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` |

### Estado al 27-oct-2026

| Métrica | Valor |
|---|---|
| Repos canónicos | 3 (`sicl-web`, `sicl-core`, `arki-acs`) |
| HEADs | `sicl-web` `5c03107c`, `sicl-core` `5dfd17a`, `arki-acs` `302f63d` |
| Fecha de los HEADs | 22-oct-2026 (excepto `sicl-core` con commit de hoy) |
| Documentación limpia | 607 archivos en `DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` |
| Evidencia forense preservada | 19 archivos en `HISTORIA_EVIDENCIA_2026-10/` |
| Espacio libre | 267 GB (40% de uso) |

---

## Nivel 2 — Arquitectura y Diseño

**Estado:** Vigente.

### Contratos

| Documento | Ubicación |
|---|---|
| `SICL Core Contract v1.0.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` + `canonical/sicl-core/docs/SICL_CORE_CONTRACT_v1.0.md` |
| `Glosario de SiMS-DeI y SICL.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` |
| `ARKI — Contrato corporativo de interfaz BIM.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` |
| `ARKI_CONTRATO_UI_BIM_CORPORATIVO_V2.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` |

### Decisiones de arquitectura (ADRs)

| ADR | Tema |
|---|---|
| `ADR-UI-001 — Transición de Home.tsx al ARKI BIM Workspace Shell.md` | Shell BIM |
| `ADR-UI2-016 — Taxonomía final de módulos.md` | 16 módulos canónicos |

### Órdenes maestras

| Documento | Ubicación |
|---|---|
| `ARKI_ORDEN_MAESTRA_POST_UI2_UI3_BIM_SUPERPODERES.docx` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` |
| `ARCHI — Orden Maestra Consolidada v3.0.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` |

---

## Nivel 3 — Implementación y RFCs

**Estado:** Parcialmente implementado. RFC-016 es hueco definitivo.

### Mapa de RFCs

| RFC | Estado | Ubicación |
|---|---|---|
| RFC-001 | ✅ Existe | `canonical/sicl-core/docs/RFC-001_MULTISCALE_MODEL.md` |
| RFC-002 | ✅ Existe | `canonical/sicl-core/docs/RFC-002_EVIDENCE_HTTP.md` |
| RFC-003 | ✅ Existe | `canonical/sicl-core/docs/RFC-003_REGULATORY_CORPUS.md` |
| RFC-004 | ✅ Existe | `canonical/sicl-core/docs/RFC-004_DESIGN_INTELLIGENCE_SCOPE.md` |
| RFC-005 | ✅ Existe | `canonical/sicl-core/docs/RFC-005_EVALUATION_COMPARISON_HTTP.md` |
| RFC-006 | ✅ Existe | `canonical/sicl-core/docs/RFC-006_SIMULATION_CONTRACT.md` |
| RFC-006.1 | ✅ Existe | `canonical/sicl-core/docs/RFC-006.1_MONTE_CARLO.md` |
| RFC-007 | ✅ Existe | `canonical/sicl-core/docs/RFC-007_MULTIOBJECTIVE_CONTRACT.md` |
| RFC-008 | ✅ Existe | `canonical/sicl-core/docs/RFC-008_PLANNING_INSTRUMENTS.md` |
| RFC-009 | ✅ Existe | `canonical/sicl-core/docs/RFC-009_MULTISCALE_RELATIONS.md` |
| RFC-010 | ✅ Existe | `canonical/sicl-core/docs/RFC-010_DESIGN_GENERATION.md` |
| RFC-011 | ✅ Existe | `canonical/sicl-core/docs/RFC-011_INSTITUTIONAL_MEMORY.md` |
| RFC-012 | ✅ Existe | `canonical/sicl-core/docs/RFC-012_MULTI_ACTOR_MODEL.md` |
| RFC-013 | ✅ Existe | `canonical/sicl-core/docs/RFC-013_TEMPORAL_CYCLES.md` |
| RFC-014 | ✅ Existe | `canonical/sicl-core/docs/RFC-014_USER_COPILOT.md` |
| RFC-015 | ✅ Existe | `canonical/sicl-web/docs/RFC-015_FRONTEND_V2.md` + auditoría en `canonical/sicl-core/docs/RFC_015_026_COHERENCE_AUDIT.md` |
| **RFC-016** | ❌ **HUECO DEFINITIVO** | **No existe como documento canónico. Las ramas `rfc-016-*` son fósiles sin trabajo pendiente.** |
| RFC-017 | ✅ Existe | `canonical/sicl-core/docs/RFC-017_CORE_CONTRACT_VERSIONING.md` |
| RFC-018 | ✅ Existe | `canonical/sicl-core/docs/RFC-018_RFC_PROCESS.md` |
| RFC-019 | ✅ Existe | `canonical/sicl-core/docs/RFC-019_MULTISCALE_REFINEMENT.md` + 3 variantes en `sicl-web` |
| RFC-020 | ✅ Existe | `canonical/sicl-core/docs/RFC-020_FEASIBILITY_FILTERING.md` |
| RFC-021 | ✅ Existe | `canonical/sicl-core/docs/RFC-021_PROJECT_VARIABLES.md` |
| RFC-022 | ✅ Existe | `canonical/sicl-web/docs/RFC-022_FRONTEND_GUIDED_INTERFACE.md` |
| RFC-023 | ✅ Existe | `canonical/sicl-web/docs/RFC-023_CORE_CONNECTIVITY_AND_DEPLOYMENT.md` |
| RFC-024 | ✅ Existe | `canonical/sicl-web/docs/RFC-024_SYSTEM_COMPLETION.md` |
| RFC-025 | ✅ Existe | `canonical/sicl-core/docs/RFC-025_PERUVIAN_REGULATORY_CORPUS.md` (+ 2 notas) |
| RFC-026 | ✅ Existe | `canonical/sicl-core/docs/RFC-026_DESIGN_KNOWLEDGE_AND_MULTISCALE_DESIGN_GRAMMAR.md` (+ plan) |
| RFC-027 | ✅ Existe | `canonical/sicl-core/docs/RFC-027_BIM_IFC_EXCHANGE_CONTRACT.md` |
| RFC-028 | ✅ Existe | `canonical/sicl-core/docs/RFC-028_GIS_CADASTRAL_PARCELA_SITIO.md` |
| RFC-029 | ✅ Existe | `canonical/sicl-core/docs/RFC-029_LOCAL_OLLAMA_COPILOT.md` |
| RFC-030 | ✅ Existe (más reciente) | `canonical/sicl-core/docs/rfc/RFC-030-ARCHITECTURAL-DRAWING-GENERATION-FOUNDATION.md` + código + tests (requiere pypdf) |
| RFC-031 a 033 | ❌ No existen | Hueco entre 030 y 034 |
| RFC-034, 034.1 | ✅ Existe | `canonical/sicl-core/docs/rfc/RFC-034-ARCHITECTURAL-PRESENTATION-SHEETS.md` |
| RFC-035 | ✅ Existe | `canonical/sicl-core/docs/rfc/RFC-035-PHOTOREALISTIC-RENDERS.md` |
| RFC-036 | ❌ No existe | Hueco entre 035 y 037 |
| RFC-037, 037.1 | ✅ Existe | `canonical/sicl-core/docs/rfc/RFC-037-MULTI-ENGINE-ABSORPTION-DOCTRINE.md` |

### Documentos de estado de implementación

| Documento | Ubicación |
|---|---|
| `SICL 0.6 — Avance porcentual y hoja de ruta ejecutiva.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` |
| `PROJECT_CLOSURE_REPORT.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` |
| `SICL 0.6 — A-002 Auditoría ejecutable y Freeze.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` |

---

## Nivel 4 — Dominio y Aplicación

**Estado:** Documentado.

| Documento | Ubicación |
|---|---|
| `ARKI_CATALOGO_MAESTRO_EXTENSO_TIPOLOGIAS.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` |
| `ARKI-E1-K-BLIND-LEARNING-EXAM-2026-09-20.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` |
| `Examen ciego de ARKI — Restaurante para 500 personas.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` |
| `ARKI-RESTAURANT-500-EXAM-2026-09-20.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` |
| `ARKI_IDEA_AND_DECISION_INVENTORY.md` | `_ARCHIVO/DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` |

---

## Nivel 5 — Capacidades Críticas

**Estado verificado al 27-oct-2026.**

| Capacidad | Estado | Ubicación | Nota |
|---|---|---|---|
| **PARTI** | ✅ Integrado en `canonical/sicl-web` | `server/arkiPartiContract.ts` (22 KB) | Integrado el 22-oct-2026. 17 copias redundantes en el servidor. |
| **Geometría avanzada** | ✅ Integrado en `canonical/sicl-web` | `server/arkiAdvancedGeometry.ts` (5.8 KB) | Integrado el 22-oct-2026. 17 copias redundantes. |
| **Motor paramétrico** | ✅ Integrado en `canonical/sicl-web` | `server/arkiParametricRuntime.ts` (6.1 KB) | Integrado el 22-oct-2026. 17 copias redundantes. |
| **Modelo predictivo** | ⚠️ **No integrado. Pendiente.** | `HISTORICAL_PUBLICACION/` (14 docs) + `_ARCHIVO/DOCS_LIMPIO/` (contrato `02`, 669 bytes) | Corpus de 14 documentos: contract, candidate, generation, scenario, prediction, validation, fidelity, failure, diversity, Pareto, opportunity, design explorer. |
| **`arkiContextGate`** | ⚠️ **No integrado. Preservado como evidencia.** | `_ARCHIVO/HISTORIA_EVIDENCIA_2026-10/context_gate/` (3 archivos) | Sistema de QR contextual A★. No concede autoridad ni contiene secretos. 11 copias byte-idénticas del módulo en el servidor. |

### Notas sobre las capacidades

- **PARTI, geometría avanzada, motor paramétrico** existen en 18 copias distribuidas por el servidor. La copia canónica es la de `canonical/sicl-web/`. Las 17 restantes son redundantes.
- **Modelo predictivo** existe en 7 copias del contrato `02` y 14 documentos del corpus completo. No se integró a `canonical/sicl-web`.
- **`arkiContextGate`** existe en 11 copias del módulo `.ts`. Se preservó una copia en `HISTORIA_EVIDENCIA_2026-10/context_gate/`. No está en `canonical/sicl-web`.

---

## Nivel 6 — Evidencia Forense

**Estado:** Preservada y recuperable.

### `HISTORIA_EVIDENCIA_2026-10/` (19 archivos, 4 ubicaciones)

| Subdirectorio | Contenido |
|---|---|
| `context_gate/` (3 archivos) | `arkiContextGate.ts`, `arkiContextGate.test.ts`, `ArkiContextGate.tsx` — módulo QR contextual A★ |
| `governance/` (4 archivos) | `ARKI_EVOLVABLE_CONTRACTS.md`, `ARKI_EVOLVABLE_IDEAS.md`, `ARKI_UNFREEZE_POLICY_20261015.md`, `ARKI_FROZEN_LEGACY_20261015.md` |
| `av036/` (5 archivos) | `AV036-15` a `AV036-19` — documentos del experimento ARKI Ideas |
| raíz (7 archivos) | `MANIFEST.md` + 6 escaneos de fases + inventarios S10 |

### `_ARCHIVO/validaciones-2026-10/` (622 MB, 16,058 archivos)

**Decisión del 27-oct-2026:** conservar tal cual. No se mueve a `_BASURA`.

Contiene: 1,950 imágenes, 36 logs, 253 JSONs de evidencia, 22 subdirectorios `output/evidence/result`.

### `_BASURA_2026-10-27/` (340 archivos + 4 directorios, 929 MB)

Recuperable. Contiene todo lo movido durante la limpieza del 27-oct-2026. Reversible con `mv` inverso.

### `0-Copia/` (intacta)

Backup completo del servidor. **No se toca.**

---

## Nivel 7 — Repositorios

**Estado al 27-oct-2026.**

| Repo | HEAD | Fecha | Estado |
|---|---|---|---|
| `canonical/sicl-web` | `5c03107cda3f8c4a1d74415610fe5efa67100079` | 22-oct-2026 19:34 | Clean |
| `canonical/sicl-core` | `5dfd17ae...` (con pypdf) | 27-oct-2026 (hoy) | Clean después de commit |
| `canonical/arki-acs` | `302f63d7c66126b248f03432fc402a4a1be6a7a6` | 22-oct-2026 20:31 | Clean |

**Nota:** el commit `5dfd17a` en `sicl-core` es el más reciente del proyecto. Añade `pypdf>=5.0` como dependencia del test `test_rfc030_content.py`, que valida el RFC-030 (planos arquitectónicos en PDF).

---

## Nivel 8 — Decisiones Pendientes

**Estado:** 5 decisiones abiertas que requieren tu decisión explícita.

| # | Decisión | Opciones | Recomendación |
|---|---|---|---|
| 1 | Integrar `arkiContextGate` a `canonical/sicl-web` | A) Integrar / B) Documentar como pendiente / C) Descartar | **B** (actual, 27-oct) |
| 2 | Integrar modelo predictivo (14 docs) a `canonical/` | A) Integrar a `sicl-web/docs/` / B) Integrar a `sicl-core/docs/` / C) Dejar en histórico | **C** (actual, 27-oct) |
| 3 | Redactar RFC-016 (hueco definitivo) | A) Redactar desde cero / B) Documentar como hueco / C) Ignorar | **B** (actual, 27-oct) |
| 4 | Desplegar Core a Cloud Computer (Fase 0-8 del 0.6) | A) Iniciar despliegue / B) Posponer / C) Cancelar | Pendiente |
| 5 | Mover `_ARCHIVO/validaciones-2026-10/` (622 MB) a `_BASURA` | A) Mover / B) Revisar antes / C) Conservar | **C** (actual, 27-oct) |

---

## Nivel 9 — Reglas de Navegación

### Cómo buscar por nivel vs tema

- **Por nivel:** seguir la tabla de contenidos. Cada nivel agrupa documentos por función, no por tema.
- **Por tema:** usar `grep -r` en `_ARCHIVO/DOCS_LIMPIO/` o en `canonical/`.
- **Por fecha:** seguir el Apéndice A. Las fechas son el ancla real del proyecto.

### Cómo agregar nuevos documentos

1. Si el documento es **nuevo y canónico**: va en `canonical/sicl-core/docs/` (para Core) o `canonical/sicl-web/docs/` (para Web).
2. Si el documento es **nuevo y no canónico** (experimento, propuesta): va en `HISTORIA_EVIDENCIA_2026-10/` con fecha.
3. Si el documento es **derivado** (misma información, otro formato): va junto al canónico, con sufijo que lo identifique.
4. Actualizar el Índice Maestro con la nueva entrada.

### Cómo distinguir canónico, derivado e histórico

| Tipo | Definición | Dónde vive |
|---|---|---|
| **Canónico** | La versión oficial, la que el sistema usa. | `canonical/sicl-*/docs/` |
| **Derivado** | Misma información que el canónico, otro formato (`.docx`, `.pdf`, `.txt`). | Junto al canónico o en `DOCS_LIMPIO/` |
| **Histórico** | Versión anterior, experimento, propuesta no integrada. | `HISTORIA_EVIDENCIA_2026-10/`, `_ARCHIVO/validaciones-2026-10/`, `HISTORICAL_PUBLICACION/` |
| **Basura recuperable** | Duplicado exacto, archivo vacío, log, temporal. | `_BASURA_2026-10-27/` |

---

## Apéndice A — Cronología

**Fechas clave del proyecto, ordenadas de más antigua a más reciente.**

| Fecha | Hito | Estado |
|---|---|---|
| 2026-08-24 | SICL 0.6 Release Candidate local (82.5% ponderado) | Verificado localmente |
| 2026-09-16 | Cierre del frontend (118 tests) | Preview funcionando, dominio público roto |
| 2026-09-20 | Exámenes ciegos (E1-K, restaurante) | `DEMONSTRATED_PARTIAL` |
| 2026-09-22 | Inventario completo de mejoras (34 mejoras, 13 bloqueos) | Documentado |
| 2026-09-23 | Auditorías Fase 0 (`pnpm check`, `pnpm build` PASS) | Verificado |
| 2026-09-26 | RFC-037.1 VSM (vigilancia semanal de maestros) | Contrato |
| 2026-09-29 | Consolidado esqueleto + sistema nervioso (D-2) | Documentado |
| 2026-10-22 | HEADs de los 3 repos canónicos | `sicl-web` `5c03107c`, `sicl-core` `934c0e5`, `arki-acs` `302f63d` |
| 2026-10-23 | Acta de cierre + revisión forense | Foto consolidada del servidor |
| 2026-10-27 | Auditoría + limpieza + verificación | **Hoy.** 607 docs limpios, 19 archivos de evidencia, 4 capacidades verificadas, RFC-016 documentado como hueco. |

---

## Apéndice B — Estado del servidor al 27-oct-2026

### Documentación

| Ubicación | Archivos | Estado |
|---|---|---|
| `DOCS_LIMPIO/ARKI_DOCS_LAPTOP/` | 607 | Corpus limpio |
| `HISTORIA_EVIDENCIA_2026-10/` | 19 | Evidencia forense |
| `_ARCHIVO/validaciones-2026-10/` | 16,058 archivos (622 MB) | Conservado por decisión |
| `_BASURA_2026-10-27/` | 340 + 4 directorios (929 MB) | Recuperable |
| `0-Copia/` | Intacta | Backup |

### Repositorios

| Repo | HEAD | Fecha |
|---|---|---|
| `canonical/sicl-web` | `5c03107c` | 22-oct-2026 |
| `canonical/sicl-core` | `5dfd17a` | 27-oct-2026 (hoy) |
| `canonical/arki-acs` | `302f63d` | 22-oct-2026 |

### Espacio

| Métrica | Valor |
|---|---|
| Disco total | 468 GB |
| Usado | 178 GB |
| Libre | 267 GB |
| Uso | 40% |

### Documentos del Colegio de Biólogos

Conservados en `DOCS_LIMPIO/ARKI_DOCS_LAPTOP/`:
- `01 - ANEXOS TÉCNICOS DEL PLAN MAESTRO.docx` (529 KB)
- `Con lo que hemos incorporado ahora.docx` (28 KB) — análisis legal del caso Alfredo (Exp. 6418-2005)

---

*Fin del Expediente Maestro al 27-oct-2026.*

*Este documento es un índice. No reemplaza a los documentos que enlaza. Se actualiza a medida que el proyecto avanza. La versión `.docx` se genera con `pandoc` para presentación formal.*

---

## Cambios del 27-oct-2026 (post-cierre del índice)

- `av023-arbol-vivo` restaurado de `_BASURA_2026-10-27/VALIDACIONES_DIRS_2026-10-27/` a `/home/arki/ARKI/av023-arbol-vivo`.
- Confirmado: `c0a82dae` existe en `canonical/sicl-web` (NO en `sicl-core`).
- Confirmado: `av023-arbol-vivo/00-START.md` (14-oct-2026, 8.6 KB) documenta continuidad con misión pendiente.
- Confirmado: `av023-arbol-vivo/arki-arbol-vivo.cjs` existe.
- Conteos reales: 608 docs limpios, 19 archivos de evidencia forense (recursivo), 341 entradas en `_BASURA`.
- `00-START.txt` de la raíz actualizado para apuntar a `00_LEER_PRIMERO.md` y al HEAD real de `sicl-core` (`5dfd17a`).

*Nota: el commit `c0a82dae` y el commit `48c8e2c7` (mencionado en `av023-arbol-vivo/00-START.md`) son anclas distintas de continuidad. El primero es de `sicl-web`, el segundo es el HEAD del web aislado `validacion-f6-descongelada` al 14-oct-2026.*
