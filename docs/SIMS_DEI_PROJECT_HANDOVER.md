# Handover maestro del proyecto SiMS-DeI / SICL

**Fecha de transferencia:** 16 de septiembre de 2026  
**Sistema:** SiMS-DeI — Spatial Intelligence Design System  
**Lenguaje formal:** SICL — Spatial Intelligence Command Language  
**Repositorio Core:** `YvanCastilloQuezada/sicl-core`  
**Repositorio frontend:** `YvanCastilloQuezada/sicl-web`

## 1. Resumen ejecutivo

SiMS-DeI es un sistema de apoyo al diseño espacial multiescala. SICL es su lenguaje formal. El sistema organiza proyectos, contexto, objetivos, restricciones, evidencia, fuentes, alternativas, simulaciones, comparaciones, recomendaciones, revisiones humanas y decisiones auditables.

La regla constitucional es simple: **el sistema puede proponer y analizar; una persona conserva la autoridad para decidir**. Una simulación no crea una recomendación. Una recomendación no es una decisión. Una traducción generada por Ollama no ejecuta comandos.

El código está publicado en GitHub y las suites locales están verdes. El E2E remoto continúa condicionado a la configuración del Core productivo.

## 2. Baselines verificados

| Componente | Baseline | Estado |
|---|---|---|
| Core | `main@3fa1387f149cdf19047cc90083fe0fc43aad534e` | Publicado |
| Core release documental | `sims-dei-2.13-rfc015-026-audit` | Publicado |
| Frontend | `main@6abca7fe913c057372821048b61aeb4ad74e2983` | Publicado |
| Frontend checkpoint | `manus-webdev://6abca7fe` | Disponible |
| Core pruebas | 241/241 | PASS |
| Frontend pruebas | 126/126 | PASS |
| Frontend typecheck | — | PASS |
| Frontend build | — | PASS |

## 3. Mapa de RFCs

### RFC-001 a RFC-014

Estos RFCs establecen el dominio multiescala, contrato HTTP, evidencia y fuentes, regulación, simulaciones, multiobjetivo, generación, memoria institucional, actores, ciclos temporales y User Copilot.

### RFC-015 — Frontend v2

Frontend funcional y simple. Guided Mode es la experiencia inicial; Expert Mode es configurable. El frontend opera las entidades principales sin pretender ser la versión estética definitiva.

### RFC-016 — Source HTTP

Source dispone de endpoints HTTP para creación, consulta y listado. Evidence puede referenciar fuentes trazables.

### RFC-017 — Versioning Policy

La política MAJOR.MINOR.PATCH, compatibilidad, deprecación y cambios de contrato está documentada y activa en `main`.

### RFC-018 — RFC Process

El ciclo DRAFT → PROPOSED → UNDER REVIEW → APPROVED → IMPLEMENTED → DEPRECATED → REJECTED está formalizado y documentado.

### RFC-019 — Dos iniciativas distintas

En el Core, RFC-019 significa el refinamiento de 9 a 11 escalas espaciales. En el frontend, RFC-019 significa alias localizados para comandos. No deben mezclarse sus estados ni sus criterios de aprobación.

### RFC-020 — Feasibility Filtering

`FeasibilityResult` clasifica alternativas como `FEASIBLE`, `INFEASIBLE`, `INSUFFICIENT_DATA` o `UNKNOWN`. `feasible_pareto_front` retiene únicamente alternativas factibles. Las restricciones duras pueden eliminar alternativas; la ausencia de datos no se interpreta como aprobación.

### RFC-021 — Project Variables

`ProjectVariable` requiere clave normalizada, tipo, valor, actor y autoridad. `SuggestedVariable` es únicamente una sugerencia y no crea objetivos, restricciones ni decisiones.

### RFC-022 — Guided Interface

Incluye Guided Shell, catálogos, formularios, mapa interactivo, tour inicial, Help Center, búsqueda, Command Bar, ocho idiomas y modo experto opcional.

### RFC-023 — Core Connectivity

El frontend usa un proxy server-side. `SICL_CORE_URL` y `SICL_CORE_SERVICE_TOKEN` no deben exponerse en el navegador. La ausencia de configuración se reporta como infraestructura, no como error ontológico.

### RFC-024 — System Completion

Camino A validado localmente y con mocks. Health check, timeouts, correlation IDs y clasificación de errores están implementados. El E2E remoto queda pendiente de URL, token y persistencia reales.

### RFC-025 — Corpus normativo peruano

El piloto incluye RNE A.010 y normas estructurales, sanitarias y eléctricas de referencia. Las evidencias, URLs, estados y modificaciones se conservan con trazabilidad. La promoción de vigencia requiere revisión humana.

### RFC-026 — Design Knowledge Agent

El piloto implementa `DesignKnowledgeSource`, `DesignKnowledgeItem`, `DesignPattern`, `DesignKnowledgeQuery`, `DesignKnowledgeResponse` y `DesignKnowledgeAgent`. El catálogo inicial separa conocimiento teórico de referencia normativa.

### RFC-027 — BIM/IFC

Existe importación IFC física de solo lectura, snapshots BIM, BIMChangeSet en PREVIEW, conflictos BIM y contratos de exportación condicionados a HumanReview. Revit y Archicad nativos requieren sus hosts y SDKs.

### RFC-028 — GIS/Catastro

Existe soporte GeoJSON, consulta OGC API Features, persistencia de ParcelSnapshot, catálogo por jurisdicción, caducidad y `ParcelBoundaryConflict`. Las fuentes catastrales reales requieren registro, licencia y validación.

### RFC-029 — Copiloto local

Ollama puede traducir lenguaje natural a una propuesta de comando SICL. La respuesta es `PREVIEW_ONLY`, `executed: false` y `decision_created: false`. Ollama no debe publicarse directamente a Internet.

## 4. Capacidades analíticas vigentes

El catálogo de simulación contiene:

- `deterministic_basic_v1`.
- `sensitivity_linear_v1`.
- `monte_carlo_v1`.

Monte Carlo admite `NORMAL`, `UNIFORM` y `TRIANGULAR`, conserva semilla, inputs, outputs y hash canónico, y limita las iteraciones a 10.000.

El catálogo de generación contiene:

- `parametric_grid_v1`.
- `pattern_variation_v1`.
- `evolutionary_v1`.
- `llm_assisted_v1`.

`llm_assisted_v1` permanece no configurado si no existe un proveedor autorizado. Ningún método analítico crea automáticamente una decisión.

## 5. Flujo Camino A

El flujo recomendado es:

```text
Project → Preference → Recommendation → HumanReview → Decision → Audit
```

Los módulos complementarios son Context/Site, Objectives & Constraints, Alternatives & Evaluation, Evidence, Evaluations, Comparisons, Council/Recommendation y Build Governance.

La revisión humana debe existir antes de una decisión. La revisión debe conservar actor, versión de recomendación, confirmación y fundamento.

## 6. Seguridad

El token del Core únicamente vive en variables server-side. No debe utilizarse como `VITE_*`, guardarse en GitHub, aparecer en logs ni incluirse en bundles.

El frontend debe clasificar por separado:

- `CORE_UNAVAILABLE`.
- `CORE_UNAUTHORIZED`.
- Error de contrato.
- Error ontológico.
- Error de servicio.

Ollama debe ser local o privado. Un LLM no puede modificar proyectos, registrar decisiones ni saltarse HumanReview.

## 7. Operación y despliegue

Consulte `docs/PRODUCTION_CORE_DEPLOYMENT_MANUAL.md`. La configuración mínima del Core productivo es:

```text
SICL_CORE_SERVICE_TOKEN=<secreto>
SICL_DB_PATH=/data/sicl/sicl.sqlite
SICL_CORS_ORIGINS=https://<origen-real-del-frontend>
OLLAMA_BASE_URL=<solo-si-se-usa>
OLLAMA_MODEL=<modelo-aprobado>
```

El servicio arranca mediante `Procfile`:

```text
web: uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

La publicación no debe declararse E2E verificada hasta comprobar health, CORS, smoke test, persistencia después de reinicio, proxy server-side y Camino A remoto.

## 8. Pruebas de transferencia

Core:

```bash
PYTHONPATH=.:src pytest -q -ra
python3 -m compileall -q src api tests
 git diff --check
```

Frontend:

```bash
pnpm test -- --run
pnpm check
pnpm build
git diff --check
```

Copiloto y GIS:

```bash
PYTHONPATH=.:src pytest -q tests/test_e2e_ollama_sicl.py -ra
```

## 9. Documentos de referencia

- `docs/DOCUMENTATION_BASELINE_2.11.md`.
- `docs/SIMS_DEI_CURRENT_ARCHITECTURE_v2.11.md`.
- `docs/RFC_015_026_COHERENCE_AUDIT.md`.
- `docs/PRODUCTION_CORE_DEPLOYMENT_MANUAL.md`.
- `docs/SICL_CORE_CONTRACT_v1.0.md`.
- `docs/USER_MANUAL.md`.
- `docs/OPERATIONS_MANUAL.md`.
- `docs/COMMANDS_REFERENCE.md`.
- `sicl-web/docs/SIMS_DEI_FIRST_CONTACT_MANUAL.md`.
- `sicl-web/docs/DOCUMENTATION_COHERENCE_2.11.md`.

## 10. Pendientes reales

El siguiente responsable debe desplegar el Core y obtener una URL HTTPS real. Después debe configurar los secretos en WebDev y ejecutar el E2E remoto. También debe decidir si se instalarán los SDKs nativos de Revit y Archicad.

No se debe declarar como terminado lo que dependa de esos recursos externos.

## 11. Criterio de aceptación del handover

La transferencia se considera completa cuando el nuevo responsable puede clonar ambos repositorios, localizar los baselines, ejecutar las suites, configurar un entorno seguro, distinguir capacidades implementadas de capacidades pendientes y continuar desde el manual de producción sin depender de conocimiento oral.

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SICL Core repository"
[2]: https://github.com/YvanCastilloQuezada/sicl-web "SiMS-DeI web repository"
[3]: https://docs.railway.com/ "Railway documentation"
[4]: https://docs.ollama.com/api/openai-compatibility "Ollama API compatibility documentation"
