# SiMS-DeI/SICL — Índice documental vigente

**Baseline:** `sims-dei-2.11-deploy-e2e`

**Commit:** `e8dbcd999cbf6b6708e09bb73a7e7a192fbaafad`

## Orden de lectura

1. `PRODUCTION_CORE_DEPLOYMENT_MANUAL.md` explica la instalación y puesta en producción.
2. `USER_MANUAL.md` explica el uso completo del sistema.
3. `COMMANDS_REFERENCE.md` contiene la sintaxis CLI y sus contratos.
4. `SICL_CORE_CONTRACT_v1.0.md` define envelopes, invariantes y endpoints.
5. `SIMS_DEI_MASTER_ARCHITECTURE_v2.2.md` explica la arquitectura y el baseline histórico.
6. `OPERATIONS_MANUAL.md` describe operación, salud, persistencia y recuperación.
7. `RFC-027_BIM_IFC_EXCHANGE_CONTRACT.md` define BIM/IFC, PREVIEW y conflictos.
8. `RFC-028_GIS_CADASTRAL_PARCELA_SITIO.md` define GIS, snapshots y catastro.
9. `RFC-029_LOCAL_OLLAMA_COPILOT.md` define el copiloto local.
10. `tests/test_e2e_ollama_sicl.py` ejecuta la validación automatizada del flujo Ollama→SICL.

## Regla de coherencia

Las secciones históricas de versiones 2.0–2.2 describen sus respectivos alcances originales. Cuando exista una afirmación de “fuera de alcance” que contradiga RFC-027, RFC-028 o RFC-029, prevalecen las secciones de estado vigente añadidas al final de los manuales y el contrato actual.

## Estado operativo

El código y los documentos están publicados en GitHub. La suite vigente tiene 241 pruebas. El E2E remoto sigue condicionado a la configuración de `SICL_CORE_URL`, `SICL_CORE_SERVICE_TOKEN`, persistencia del proveedor y disponibilidad de Ollama.
