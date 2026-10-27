# 00_START — ARKI / ARQUI · continuidad y auditoría
Fecha: 2026-10-12
Estado: BORRADOR DE RECUPERACIÓN EN RAMA EXPERIMENTAL; NO CANÓNICO; NO FROZEN
Propósito: punto de entrada verificable para el siguiente chat. No sustituye otros 00_START existentes fuera de esta rama.


## PRINCIPIO FUNDACIONAL PRIORITARIO — ARKI DETERMINISTA / SICL (declaración del Product Owner, 2026-10-12)
**Instrucción expresa del Product Owner:** «ARKI es determinista. Eso es lo que lo hace distinto». Identifica a «SILC, S-I-L-C» como motor de búsqueda determinístico. **No borrar ni reinterpretar esa denominación sin investigación**.
**Contraste con fuente fundacional:** `docs/ARKI_AND_SICL_FOUNDATIONS.md` define **SICL** (S-I-C-L, Spatial Intelligence Command Language) como lenguaje formal de operación verificable del Core, con validación y persistencia canónica en `sicl-core`; no lo define literalmente como motor de búsqueda. Por tanto, **SILC (motor de búsqueda, según Product Owner) vs SICL (lenguaje formal, según documento) = NOMENCLATURA / IDENTIDAD TÉCNICA POR RECONCILIAR**. No asumir que son lo mismo ni inventar un motor nuevo.
**Invariante objetivo de determinismo, pendiente de prueba:** ante idéntica versión de código, estado inicial, entradas, reglas, parámetros, semillas y fuentes fijadas, el camino canónico de ARKI debe producir resultados reproducibles y rastreables; toda aleatoriedad o IA externa debe registrarse/aislarse y no promocionarse como verdad canónica sin verificación. Este criterio es una propuesta operacional de prueba, **no una certificación de determinismo E2E ya alcanzado**.
**Autoridad única:** un sistema ARKI, una autoridad arquitectónica semántica D-2, una autoridad geométrica AGK, Core para estado/validación, y revisión humana para decisiones. Los maestros externos y ACS son laboratorios/adaptadores subordinados, nunca motores canónicos paralelos. NO_NEW_ENGINE; NO_AUTOMATIC_CANONIZATION.
**Fuentes recuperadas:** `docs/ARKI_AND_SICL_FOUNDATIONS.md`, `docs/arki-knowledge/fundamental-research/FKCG-02/FKCG-02_FUNDAMENTAL_KNOWLEDGE_PRESERVATION.md`, `sicl-core/docs/ARKI_CORE_FROZEN_v1.0.md`, `docs/arki-master-map/AGK_OCCT_EXECUTION_EVIDENCE_V1.md`, `sicl-core/docs/rfc/RFC-037-MULTI-ENGINE-ABSORPTION-DOCTRINE.md`.
**Inventario detallado:** `docs/arki-master-map/ARKI_SUPERPOWERS_AUDIT_2026-10-12.md` incluye cinco SP oficiales, AGK/OCCT y deltas, Dynamo/Grasshopper/Revit/IFC, leyes de autoridad y límites de ejecución.
**Próxima tarea:** localizar implementación, pruebas y genealogía de la búsqueda determinística SILC/SICL; comparar replay, orden de resultados, hashes, idempotencia y efectos de proveedores externos; registrar SHA exacto y CI. No declarar probado sin ejecutar.


## DECISIÓN DE DISEÑO PROPUESTA POR PRODUCT OWNER — FASE 1: ENCARGO ÚNICO (2026-10-12)
**Orden conceptual:** la jerarquía de diez fases debe comenzar en Fase 1 con recepción del encargo/intención del cliente. Ejemplo: «Diseñar un rascacielos de 120 pisos». El concepto de proyecto nace y se registra allí, no en una capa externa por encima de las diez fases. Fases 2–10 continúan el proceso interno conforme a sus definiciones oficiales (nombres y correspondencia por verificar; no inventar fases).
**Contrato propuesto de Fase 1:** solicitud original literal, intención/idea del cliente, escala y tipología, programa preliminar, sitio y jurisdicción conocidos o UNKNOWN, objetivos y preferencias, restricciones conocidas con fuentes, supuestos explícitos, conflictos/preguntas, identificación del proyecto, procedencia y versión, revisión humana requerida cuando aplique. Separar la idea recibida del concepto arquitectónico desarrollado y evaluado posteriormente.
**Flujo:** FASE 1 / ENCARGO → D-2 autoridad semántica → Project State / Core / trazabilidad → ejecución gobernada de FASES 2–10 → AGK único para geometría canónica → representaciones 2D/3D/BIM/IFC. SICL/SILC nomenclatura por reconciliar; determinismo de entradas, reglas, estado y resultados por demostrar E2E.
**No confundir:** «todo en Fase 1» significa **un punto de captura de toda la información disponible**, no ejecutar allí todas las actividades, ni declarar datos desconocidos como hechos, ni introducir motor adicional. Mantener fases como jerarquía, vertebra/espinas y dependencias actualizables; una nueva idea posterior se versiona y propaga mediante autoridad, no reinicia ni modifica FROZEN silenciosamente.
**Estatus:** DECISIÓN DE INTENCIÓN / PROPUESTA DE CONTRATO, NO IMPLEMENTADA NI VALIDADA. Auditar mapa de diez fases existente y su interfaz antes de cambiar código o numeración.


## LEY DE SELECCIÓN DE IDEAS — «La vida es dura para las ideas» (formulación oral aproximada; 2026-10-12)
**Descripción expresa del Product Owner:** desde el encargo de Fase 1 ARKI explora miles de ideas/posibilidades. Las restricciones verificadas y criterios de evaluación van descartando alternativas; el embudo existente conduce a **N → 16 → 4 → 1**. El encargo y el concepto inicial entran por Fase 1, no por un sistema superior separado. **El texto literal de la ley histórica sigue SIN LOCALIZAR; no presentar esta redacción como cita oficial ni atribuir autor.**
**Regla de ingeniería propuesta para preservar intención:** generación amplia (variación controlada) → filtros duros de inviabilidad sustentados en norma/autoridad/contexto → evaluación multiobjetivo de alternativas factibles → diversidad arquitectónica → 16 → 4 → 1 con decisión humana cuando proceda. Restricción sin aplicabilidad demostrada no debe eliminar definitivamente una idea: clasificar UNKNOWN/HOLD y solicitar evidencia. Registrar por candidato origen, seed/parámetros, estado, razón y prueba de descarte, puntuaciones y procedencia; permitir replay determinista. Probabilidad para explorar NO equivale a arbitrariedad en decisión canónica; semillas, versiones, fuentes y reglas se fijan para reproducibilidad.
**No eliminar ideas del historial:** rechazo/archivo reversible y trazable, no borrado de auditoría append-only. No declarar que miles de candidatos, todos los filtros o el funnel E2E estén verificados hoy; revisar implementación existente y sus pruebas antes de modificarla. No motor nuevo, D-2/AGK/Core como autoridades ya establecidas.
**Investigación externa:** no se halló fuente confiable para la frase exacta «La vida es dura para las ideas»; buscar en documentos históricos internos, especialmente `docs/arki-knowledge/preserved/03_ARKI_Historia_y_Evolucion_v1.0.xlsx` y genealogía del Design Funnel.


## LEY DEL EMBUDO — «LA VIDA ES DURA PARA LAS IDEAS» (reformulación precisa del Product Owner, 2026-10-12)
**Intención declarada:** ARKI es determinista, auditable, conoce el origen de cada resultado y **declara «NO CONOZCO / UNKNOWN»** cuando falta conocimiento o evidencia. Desde Fase 1 se capturan encargo y todas las restricciones disponibles; se eliminan tempranamente las ideas que incumplen restricciones **verificadas y aplicables**, y el resto sigue enfrentando restricciones/evaluaciones durante el diseño. La supervivencia progresiva conduce al embudo histórico **N → 16 → 4 → 1**. «La vida es dura para las ideas» es el lema oral aproximado; **«Ley del Embudo» es nombre de búsqueda propuesto**, no denominación documental confirmada.
**Distinciones obligatorias:** explorar posibilidades probabilísticamente no autoriza decisiones aleatorias opacas: fijar entradas, reglas, versión, semillas y procedencia para replay; **probabilidad de generación ≠ verdad/autoridad canónica**. Ideas inviables: REJECTED con causa, fuente, prueba y versión; ideas sin datos: UNKNOWN/HOLD, **no matar por desconocimiento**; ideas viables: ACTIVE/ADVANCED; mantener historial append-only y reversibilidad bajo cambio de restricciones. Selección final conforme autoridad D-2 y revisión humana aplicable. Un solo motor ARKI; no introducir sistemas paralelos.
**Pendiente de recuperación documental:** buscar expresiones «Ley del Embudo», «La vida es dura para las ideas», «ideas», «funnel» en genealogía del Design Funnel, mapa maestro, documentos fundacionales e historia XLSX. La búsqueda disponible no verificó la cita textual. **Estado: INTENCIÓN FUNDACIONAL PRESERVADA; REDACCIÓN ORIGINAL NO VERIFICADA; E2E NO EJECUTADO.**


## CORRECCIÓN PRIORITARIA DEL PRODUCT OWNER — RETENCIÓN DEL EMBUDO (2026-10-12)
**La regla correcta prevalece sobre los párrafos anteriores de «historial de cada idea»:** Si ARKI explora 10 000 ideas, las descartadas durante la exploración **NO SE GUARDAN individualmente**. **Solo se conservan las 16 ideas supervivientes** del primer corte N→16. Estas 16 continúan al proceso 16→4→1. No construir un archivo de miles de ideas muertas ni imponer trazabilidad individual para descartes efímeros.
**Determinismo sin almacenamiento masivo:** el proceso de generación/filtrado debe ser reproducible desde encargo, restricciones, versiones, reglas y semillas cuando aplique, pero reproducibilidad del proceso no significa persistencia de cada candidato descartado. La política de retención de metadatos agregados de ejecución queda por definir; no atribuir al usuario una obligación de guardarlos.
**Prioridad de lectura:** este apartado CORRIGE expresamente cualquier afirmación anterior de este 00_START que exigiera registrar por candidato rechazado, conservar su historial o permitir su recuperación individual. Preservar solo las 16 finalistas como ideas persistentes, conforme orden del Product Owner. No se han cambiado código, bases de datos ni FROZEN; implementar tras auditar contrato existente.


## FUENTE CANÓNICA LOCALIZADA — LEY «LA VIDA DE LAS IDEAS ES CRUEL» (2026-10-12)
**ENCONTRADA, YA NO PENDIENTE:** `YvanCastilloQuezada/sicl-core/docs/ARKI_LAW_LIFE_OF_IDEAS_IS_CRUEL.md`, rama `main`. https://github.com/YvanCastilloQuezada/sicl-core/blob/main/docs/ARKI_LAW_LIFE_OF_IDEAS_IS_CRUEL.md
**Nombre literal:** «LEY — LA VIDA DE LAS IDEAS ES CRUEL». **Fórmula:** «MUCHAS IDEAS NACEN... POCAS SOBREVIVEN». **Regla de oro:** «MATAR UNA IDEA ES BARATO. DESARROLLARLA ES CARO». **Ley del Embudo:** mecanismo operativo conceptual subordinado a la ley. No volver a marcar nombre/frase como no localizados.
**Secuencia doctrinal:** IDEAS → ALTERNATIVAS → GEOMETRÍAS → SIMULACIONES → SOLUCIONES → PROPUESTAS → OBJETO/ARQUITECTURA/ESPACIO. CHEAP VALIDATION BEFORE EXPENSIVE DEVELOPMENT; cómputo y fidelidad crecen conforme se reduce población. HARD FAIL demostrado → PODA; UNKNOWN → ESPERA/RESOLVER; TRADE-OFF → COMPARAR; PREFERENCIA → HUMAN AUTHORITY. PASS ONCE ≠ PASS FOREVER. Poda de mutación fallida preserva último estado válido.
**Estado declarado por el documento:** CANONICAL; RUNTIME_PRUNING_ENGINE, COMPUTE_BUDGET_ENGINE y SURVIVAL_PIPELINE = NOT_IMPLEMENTED; no autoriza implementación por sí solo. **No convertir doctrina en prueba E2E.**
**Contrato adicional explícito del Product Owner (2026-10-12):** durante exploración N (p. ej. 10 000), los descartados efímeros NO se guardan individualmente; solo se guardan las 16 supervivientes del primer corte. Distinguir de `docs/arki-predictive/DESIGN_FUNNEL_16_4_1.md`, que prescribe ARCHIVED para candidatos no seleccionados en el flujo de selección humana. **Reconciliación de alcance:** N→16 efímero sin archivo individual; 16→4→1 con archivo de alternativas ya persistidas según contrato existente, pendiente de confirmar con Product Owner si corresponde. No borrar ni alterar eventos canónicos existentes sin autorización.
**Referencias complementarias:** `docs/arki-predictive/DESIGN_FUNNEL_16_4_1.md`, `docs/arki-predictive/DESIGN_FUNNEL_EVENT_MODEL.md`, `docs/arki-knowledge/preserved/01_ARKI_Decisiones_y_Constitucion_v1.0.xlsx` (contenido XLSX aún pendiente de lectura). Corregir interpretaciones previas de este 00_START con prioridad de esta fuente canónica y la orden explícita de retención del Product Owner.


## MAPA DE RESPONSABILIDADES RECUPERADO — CORE / WEB / ACS Y CONTRATACIONES (2026-10-12)
**Aclaración del Product Owner:** ARKI Core = corazón normativo/canónico (leyes, constitución, contratos e invariantes); ARKI Web = operación, interfaz y orquestación; ARKI ACS/SLC (nombre verbal por reconciliar) = investigación/gemelo digital y módulo de búsqueda de contrataciones del Estado para oportunidades de ingresos. NO colapsar los repositorios ni confundir funciones. En GitHub están accesibles `YvanCastilloQuezada/sicl-core`, `sicl-web`, `arki-acs`. **«Arqui SLC» no se ha verificado como repositorio independiente; la implementación de contrataciones sí se encontró en arki-acs.**
**CORE evidencia directa:** `docs/ARKI_LAW_LIFE_OF_IDEAS_IS_CRUEL.md` (ley canónica), `docs/SICL_CORE_CONTRACT_v1.0.md` (ontología, eventos append-only, autoridad humana, restricciones y estados UNKNOWN), `docs/ARKI_CORE_FROZEN_v1.0.md` (invariantes FROZEN), `docs/RFC-020_FEASIBILITY_FILTERING.md` (filtro FEASIBLE/INFEASIBLE/INSUFFICIENT_DATA/UNKNOWN; analítico, no decide). El repositorio CORE contiene también RFCs y código ejecutable; «corazón normativo» es responsabilidad principal, no exclusión de ejecución Core.
**WEB evidencia directa:** `docs/arki-predictive/DESIGN_FUNNEL_16_4_1.md` y `shared/arkiDesignFunnel.ts`; UI `/arki-design-funnel`; `docs/ARKI_AND_SICL_FOUNDATIONS.md` delimita Core y frontend. La operación WEB no puede crear segunda autoridad.
**ACS evidencia directa de CONTRATACIONES:** `src/Acs.OeceCorpus/` (parsers, clientes, modelos, almacenamiento OECE), `src/Acs.OeceCorpus.Cli/Program.cs` (comandos `opportunities`, `opportunities-full`, `active-only`, `ingest-month`, `export-csv`), `src/Acs.OecePortal/Services/CorpusQueryService.cs` (SQLite, filtros por años/categoría/método/departamento/monto/texto, relevancia y sinónimos), `src/Acs.OecePortal/Components/Pages/Licitaciones.razor`, `Adjudicaciones.razor`, `Contratos.razor`, `Estadisticas.razor`; `tests/Acs.Tests.Integration/OeceCorpus/OeceCorpusEndToEndTests.cs` requiere dataset local `C:\\acs-v1\\test-artifacts\\oece-2026-09` y DB local. **Código hallado ≠ E2E actual probado ni servicio desplegado; no se ejecutaron pruebas en esta sesión.** `arki-acs/README.md` declara ACS laboratorio y NO runtime de producción, por lo que hay que investigar si la herramienta de contrataciones se ofrece como portal autónomo dentro de ACS y cómo se integra sin cambiar autoridad.
**Objetivo comercial declarado:** ARKI debe poder descubrir oportunidades de contrataciones públicas para generar ingresos; búsquedas y oportunidades ≠ ingresos obtenidos, adjudicación ni capacidad de postular automáticamente. Investigar elegibilidad, vigencia, procedencia, filtros, alertas y revisión humana.
**Pendiente:** auditoría profunda de leyes/constitución Core, ramas y genealogía; localizar gemelo digital en ACS vs WEB; identificar límites reales del portal OECE, datos, CI y despliegue; conciliar nomenclatura SLC/SICL/ACS con fuente y Product Owner. No cambiar FROZEN ni declarar «totalmente desarrollado» como verificado hasta prueba exacta.


## VISIÓN DEL PRODUCT OWNER — DOS GEMELOS Y AUTOENSAMBLAJE DEL ÁRBOL VIVO (2026-10-12)
**DOS DOMINIOS DIFERENTES:** (A) Gemelo Digital Vivo del propio ARKI: estado, capacidades, dependencias, evaluación de mejoras; prepara **TRES opciones de mejora** para selección/aprobación humana, no se autoaprueba. (B) Gemelo Digital Experimental: banco aislado para probar tecnologías/cambios antes de afectar ARKI; puede alojar gemelos digitales de edificios/obras para simular modificaciones sin tocar el activo real. No fusionar ambos conceptos ni asumir implementación E2E.
**METÁFORA DE ENSAMBLAJE:** tronco/columna vertebral = diez fases existentes (Product Owner declara que 1→10 ya funciona; **pendiente de regresión verificable**). Espinas/bolitas = capacidades, contratos, fuentes, conocimientos, herramientas, geometría, IFC, pruebas. Objetivo actual: **reconectar y ubicar capacidades ya existentes** en la fase y dependencia correcta; no construir motores nuevos ni duplicar órganos.
**OBJETIVO DE AUTONOMÍA:** ARKI identifica pieza → lee su contrato/evidencia → propone ubicación e interfaces → prueba en entorno experimental → compara resultados y riesgos → presenta 3 alternativas → humano autoriza → integra a través de D-2/Core/AGK y gates existentes → verifica regresión → registra patrón reutilizable como candidato de aprendizaje gobernado por Delta 6.2. Aprender no equivale a autopromoción. Todo fallo se declara UNKNOWN/BLOCKED con evidencia.
**GEOMETRÍA/IFC:** Product Owner señala fuerte avance en geometría y conocimiento de elementos como muros; verificar por separado entidad semántica, operaciones AGK, parametrización, relaciones, IFC export/import, round-trip y versiones exactas (p. ej. IFC4/IFC4X3; «IFC 3.4» es expresión oral a reconciliar, no nombre de esquema confirmado). No declarar autoría nativa de muros o round-trip completo sin prueba.
**Fuentes de contraste:** `docs/arki-master-map/ARKI_MASTER_MAP_LIVE.md` (ley epistemológica y contratos de conexión), `docs/arki-master-map/ARKI_CANONICAL_HANDOFF_2026-10-05.md` (dos dominios de twin, identidad canónica, fases, D-2/AGK/Delta 6.2). Estado: VISIÓN/ORDEN DE INTEGRACIÓN; no implementación nueva en este commit.

## Orden de trabajo
1. Auditar y conectar Maqueta Viva, Plano Vivo, Árbol Vivo y Árbol Gemelo Digital, con estado único y evidencia.
2. Auditar ADN de Mejora Continua: observación → déficit → hipótesis → alternativas → pruebas autorizadas → comparación → aprendizaje trazable. Sin autopromoción ni mutación FROZEN.
3. Cerrar continuidad: descubrir el 00_START original si existe fuera de GitHub, reconciliar este borrador, comprobar generación de handoff y lectura por otro chat.
4. Posponer recuperación gráfica hasta después del cierre de continuidad; no perder inventario histórico de capacidades.

## Repositorios y ramas inspeccionados (GitHub)
- WEB: YvanCastilloQuezada/sicl-web, main SHA ec6ede75a13e6a346816dfd96816272926a575b9, observado 2026-10-12.
- Rama experimental: feat/arbol-vivo-autoensamblaje-20261011, SHA de inspección 03438511975da868a94bcb17f30d3a30103c7907.
- CORE: YvanCastilloQuezada/sicl-core. Integración con WEB NO VERIFICADA en esta auditoría.
- No mezclar MiLukita; proyecto independiente.

## Evidencia real recuperada
- En main no se encontró tools/maqueta-viva ni 00_START en raíz. La rama experimental sí incluye tools/maqueta-viva, ARBOL-GEMELO-DIGITAL.md, scripts de descubrimiento, ADN y pruebas.
- tools/maqueta-viva/README.md: maqueta offline, estado local no canónico; no detecta ramas remotas automáticamente; exportación JSON requerida para respaldo.
- tools/maqueta-viva/ARBOL-GEMELO-DIGITAL.md: tres vistas documentales sincronizadas; la vista 3D es conceptual, no geometría AGK. Propagación documental, no causalidad runtime demostrada.
- tools/maqueta-viva/ARKI-ADN-MEJORA-CONTINUA-CONTRATO-PROPUESTO.md: ADN experimental A0/A1; observador local de JSON, no integrado al Core ni servicio autónomo persistente; promoción supervisada.
- docs/arki-master-map/AV_UI_001_ARBOL_VIVO_PREPARATION.md: interfaz unificada en estado PREPARATION_ONLY, sin aceptación canónica.
- GitHub Actions del SHA 0343851: ARKI Assembly Planner run 38192989124 FAILURE; ARKI Maqueta Viva smoke run 38192989034 FAILURE. NO VERDE.
- No se han ejecutado pruebas locales ni E2E en esta sesión; lectura estática + consulta CI solamente.

## Continuidad funcional buscada
Cambio real (código, ideas, evidencia, decisión) → descubrimiento incremental → clasificación con procedencia → dependencias y FROZEN → estado temporal y vista compartida → autodiagnóstico → propuesta de mejora → prueba aislada autorizada → resultado y registro → handoff verificable.
Cada flecha debe probarse; no suponer implementación por existir archivos o vistas.

## Inventario histórico y representación
- ARKI tiene capacidades históricas de programa, partido, geometría, validaciones, agentes y evaluación; su integración completa actual no está demostrada.
- HOUSE-A21: en commit histórico 0376f24, synthesizeHouseA21Configuration usa terreno fijo 24×18m y diez rectángulos con coordenadas explícitas. No demuestra diseño general autónomo.
- Se investigaban Torre/Vertical Aurora y Puente Ucayali/Pucallpa, sin expediente verificado aún.
- Funnel 16 variantes usa previews demo en versión investigada, no afirmar geometría generativa completa.
- Recuperación de representación gráfica queda en HOLD, no abandonada.
- AGK único, 3D-First, diseño multiescala, cero deudas, pruebas SHA exacto y revisión Qwen como reglas de trabajo.

## Próxima auditoría obligatoria
A. Localizar el 00_START original y fuente canónica del estado.
B. Analizar causas de ambos CI fallidos, ejecutar suites aisladas y registrar SHA, logs y cobertura.
C. Comprobar persistencia, replay, hashes, eventos, sincronización Maqueta/Plano/Árbol/Gemelo, actualizaciones de FROZEN y handoff.
D. Determinar si Plano Vivo tiene módulo real o es denominación de interfaz; UNKNOWN hasta localizarlo.
E. Verificar trigger autónomo, ciclo de aprendizaje repetido, seguridad, reversibilidad y autorización; NO declarar automejora verificada sin E2E.
F. Actualizar este documento tras pruebas; solicitar auditoría Qwen y autorización antes de promover cambios.

## Disciplina
CLAIM ≠ IMPLEMENTED ≠ EXECUTED ≠ VERIFIED ≠ FROZEN.
Sin evidencia no hay verde. Este documento es memoria de trabajo, no certificación ni reemplazo automático de la fuente canónica.

## Auditoría histórica de tres repositorios — 2026-10-12
Inventario auxiliar guardado en `docs/arki-master-map/ARKI_SUPERPOWERS_AUDIT_2026-10-12.md` (commit `eb7ae3afbb25331e06f078bdcb413b0e0465b86e`). Tres pasadas documentales/estáticas: anatomía, genealogía mediante auditorías históricas y contraste epistemológico/CI. No implica recorrido exhaustivo de commits ni pruebas E2E. Cinco superpoderes formales SP-01..SP-05; otras capacidades WEB/CORE/ACS inventariadas. Leer junto con MASTER_MAP_LIVE y MASTER_MAP_STATE. CI de rama experimental continúa con fallos históricos sin causa diagnosticada.

## FUENTE HISTÓRICA PRIORITARIA — origen, evolución y visión futura de ARKI (2026-10-12)
**Archivo localizado en WEB main:** `docs/arki-knowledge/preserved/03_ARKI_Historia_y_Evolucion_v1.0.xlsx` (Git blob SHA `4ff13995f1ffad49a2c3d022488a12ea61067ffe`, 6349 bytes). Enlace: https://github.com/YvanCastilloQuezada/sicl-web/blob/main/docs/arki-knowledge/preserved/03_ARKI_Historia_y_Evolucion_v1.0.xlsx
**Declaración del Product Owner:** este documento recoge cómo nació ARKI y lo que debe llegar a ser. **IMPORTANTE: contenido de las hojas AÚN NO LEÍDO**; la herramienta GitHub disponible rechazó la extracción del XLSX binario. No inferir contenido ni declararlo auditado.
**Próxima acción obligatoria:** materializar/descargar XLSX con un mecanismo binario válido; leer todas las hojas, contrastar origen, decisiones, cambios de nombre SICL→Vitruvio→ARKI, visión futura, autoridad y determinismo; incorporar los hallazgos documentados aquí y al mapa maestro con referencia exacta de hoja/celda. Distinguir historia, intención, implementación y evidencia.
**Otra fuente de preservación:** `docs/arki-knowledge/preserved/01_ARKI_Decisiones_y_Constitucion_v1.0.xlsx`, también pendiente de lectura integral.

## Continuidad de validación offline — 2026-10-14
- GitHub Actions para PR #57 no asignó runner y terminó en segundos; causa de facturación/cuota plausible pero NO CONFIRMADA con acceso a billing.
- Rama `test/arki-autonomy-offline-ci-20261014`, PR #61 DRAFT, implementa `tools/maqueta-viva/Run-ARKI-Offline-CI.cjs` para 13 suites existentes sin dependencia de GitHub Actions. Node 22, SHA exacto, worktree limpio, reporte JSON y fallos explícitos. Último commit del runner: `c7744aba22ba801758d5bf612de0d9047641d880`.
- Procedimiento: `docs/arki-master-map/ARKI_OFFLINE_VALIDATION_20261014.md`. No se ha ejecutado en ARKI-02; NO reclamar PASS.
- PR #60 mantiene auditoría doble sin modificación de runtime. PR #57 es la autonomía ya existente; NO DUPLICAR.
- Próximo: ejecutar validación offline en clon experimental, reconciliar PR #57 con Árbol Vivo, verificar persistencia y ACE88. No merge ni FREEZE hasta evidencias.

## Continuidad adicional offline — 2026-10-14
- El runner local ahora enumera 15 archivos de pruebas, incluyendo verificador de journal y analizador de divergencia de ramas. No se han ejecutado en ARKI-02.
- Nuevos módulos read-only: `tools/maqueta-viva/Verify-ARKI-Journal.cjs`, `Reconcile-ARKI-Branches.cjs`, con pruebas adversariales independientes.
- Procedimiento actualizado: `docs/arki-master-map/ARKI_OFFLINE_VALIDATION_20261014.md`.
- PR #61 DRAFT. Evitar merge a main y no afirmar ACE88 integrado, persistencia durable ni AGK E2E.

## Integración ACE88 — continuidad 2026-10-14
- Contrato propuesto en `docs/arki-master-map/ARKI_ACE88_WEB_CORE_BOUNDARY_20261014.md` (commit `ccd4cc8b19019b9b8d0ebd67f435a5106ddc5484`).
- Fuente Core `docs/ace88/ACE88_ROOT_INTEGRATION.md`: declara regresión local PASS al 14/10; auditoría independiente y SECURITY_FREEZE siguen pendientes. No inferir aprobación desde clic UI.
- Se optimizó `Reconcile-ARKI-Branches.cjs` para evitar ejecutar un proceso Git por cada ruta (commit `d1568d766627ef959a22c365f289f1e87c028b74`).
- Próximo: inspeccionar API ACE88 real y escribir adaptador fail-closed con pruebas, sin promover cambios canónicos antes de validación E2E.

## ACE88 Web-Core adapter — 2026-10-14
- Preflight y transporte inyectable implementados: `tools/maqueta-viva/arki-ace88-preflight-adapter.cjs`, `arki-ace88-core-transport.cjs`.
- Ruta Core verificada en código: POST `/v1/projects/{project_id}/developer-promotions`; servicio requiere Bearer; no almacenar tokens.
- Suites ACE88 incluidas en runner offline: 17 archivos de pruebas totales; ejecución real NO DEMOSTRADA.
- Contrato y advertencias E2E: `docs/arki-master-map/ARKI_ACE88_ADAPTER_IMPLEMENTATION_20261014.md`.
- No usar proyecto canónico para pruebas de promoción; falta cliente HTTP servidor real, verificación independiente y SECURITY_FREEZE.

## Árbol Vivo — propagación segura de antecedentes (2026-10-14)
- `arki-arbol-vivo-auto.cjs` ahora consume el gate `arki-dependency-coverage.cjs`, marca `prerequisiteStatus` y propaga bloqueos a descendientes sin cambiar el registro canónico.
- Registro histórico de 51 elementos: ninguno declara `dependencies`; su ruta de precedencias permanece `BLOCKED_UNVERIFIED`, aunque el orden topológico histórico se conserve para inspección.
- `arki-arbol-vivo-auto.test.cjs` añade pruebas de bloqueo propagado y antecedentes declarados. Ejecutar offline; no se afirma PASS hasta recibir evidencia.
- El estado `DECLARED_NOT_COMPETENCE_VERIFIED` tampoco habilita ejecución: falta validación de competencias, evidencia y ACE88.

## Aprendizaje relacional Árbol Vivo — 2026-10-14
- Nuevo generador de relaciones candidatas `tools/maqueta-viva/arki-relational-learning.cjs`: REQUIRES, INFORMS, FEEDBACK, trazabilidad declarada y detección de ciclos. No promociona ni muta el registro.
- Suite `arki-relational-learning.test.cjs` incorporada al runner offline (19 archivos en total), pruebas no ejecutadas.
- Documentación `docs/arki-master-map/ARKI_RELATIONAL_LEARNING_20261014.md`.
- Próximo paso: extracción y verificación automática de evidencia desde los tres repositorios y conexión a UI Árbol Vivo, sin inventar precedencias.

## Descubrimiento automático de relaciones — 2026-10-14
- `arki-relational-discovery.cjs` recorre documentación versionada y reconoce declaraciones explícitas `ARKI_RELATION: A REQUIRES B` (o INFORMS/FEEDBACK).
- `arki-relational-evidence.cjs` comprueba citas contra Git SHA exacto; no verifica semántica ni permite promoción.
- Nuevas suites `arki-relational-discovery.test.cjs` y `arki-relational-evidence.test.cjs` integradas en runner offline (21 archivos), ejecución aún pendiente.
- Instrucciones y límites: `docs/arki-master-map/ARKI_AUTONOMOUS_RELATION_DISCOVERY_20261014.md`.
- Pendiente: ampliar extracción de relaciones no estructuradas, revisar evidencias y conectar grafo aprobado a UI y aprendizaje Delta 6.2; respetar ACE88.
