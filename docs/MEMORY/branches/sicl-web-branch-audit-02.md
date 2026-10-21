# SICL Web — auditoría de ramas (lote 2: histórico, sincronización y auditorías)

Base de comparación: `main@9ae8fe504bbb964d8b89d87709ee773e64cbbacb`. No se ejecutaron pruebas. La rama `0-Historical` se trata como histórica por su nombre, no como evidencia de que todo su contenido esté obsoleto.

## 0-Historical
- SHA: `461b30c4ad5361071e566c8f6073a60fa6660e39`
- Último commit: docs(history): archive seven historical collections with originals and extracted files (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/461b30c4ad5361071e566c8f6073a60fa6660e39
- Diferencia contra main: diverged; ahead 2, behind 49, total commits exclusivos 2; rutas reportadas 300
- Rutas únicas representativas: added HISTORICAL_README.md, added historical/01_Historia_gobierno_y_documentos_generales/00-START/00_original/00-START.txt, added historical/01_Historia_gobierno_y_documentos_generales/ARCHI_—_Especificación_propia_de_controles_funcionales_para_los_16_módulos/00_original/ARCHI_—_Especificación_propia_de_controles_funcionales_para_los_16_módulos.pdf, added historical/01_Historia_gobierno_y_documentos_generales/ARKI-PROJECT-ORGANIGRAM/00_original/ARKI-PROJECT-ORGANIGRAM.pdf, added historical/01_Historia_gobierno_y_documentos_generales/ARKI_A1_0B_DIAGNOSTIC_PACKAGE(2)/00_original/ARKI_A1_0B_DIAGNOSTIC_PACKAGE(2).zip, added historical/01_Historia_gobierno_y_documentos_generales/ARKI_A1_0B_DIAGNOSTIC_PACKAGE(2)/01_extraido/00_A1_0B_EXECUTIVE.md, added historical/01_Historia_gobierno_y_documentos_generales/ARKI_A1_0B_DIAGNOSTIC_PACKAGE(2)/01_extraido/01_TARGET_14_ROUTES.md, added historical/01_Historia_gobierno_y_documentos_generales/ARKI_A1_0B_DIAGNOSTIC_PACKAGE(2)/01_extraido/02_ROUTE_SETTLEMENT_MATRIX.md, added historical/01_Historia_gobierno_y_documentos_generales/ARKI_A1_0B_DIAGNOSTIC_PACKAGE(2)/01_extraido/03_TIMING_MATRIX.md, added historical/01_Historia_gobierno_y_documentos_generales/ARKI_A1_0B_DIAGNOSTIC_PACKAGE(2)/01_extraido/04_NETWORK_EVIDENCE.md
- Lectura: Baseline histórico. Debe leerse como antecedente y contrastarse con main; no usarlo como estado actual.
- Estado de pruebas: no ejecutadas ahora; verificar logs/CI por SHA.
- Siguiente paso: revisar PRs y commits exclusivos, identificar solapamiento con main y etiquetar como integrada, antecedente, candidata a rescate o pendiente.

## ace85/local-sync-20261011T233918Z
- SHA: `1544b977ad34e84dc1c97b1f8f66f1a5acbf4d4b`
- Último commit: ACE85: synchronize validated local changes (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/1544b977ad34e84dc1c97b1f8f66f1a5acbf4d4b
- Diferencia contra main: behind; ahead 0, behind 58, total commits exclusivos 0; rutas reportadas 0
- Rutas únicas representativas: sin rutas únicas recuperadas
- Lectura: Sincronización local fechada; revisar si contiene commits de trabajo local no presentes en main y si sus cambios ya se trasladaron a otra rama.
- Estado de pruebas: no ejecutadas ahora; verificar logs/CI por SHA.
- Siguiente paso: revisar PRs y commits exclusivos, identificar solapamiento con main y etiquetar como integrada, antecedente, candidata a rescate o pendiente.

## ace87/remove-qr
- SHA: `6fa1fb16a5c952f50776d546e9caf8c36a68ec44`
- Último commit: test(mo29): track project resolver and secure core test fixtures (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/6fa1fb16a5c952f50776d546e9caf8c36a68ec44
- Diferencia contra main: behind; ahead 0, behind 51, total commits exclusivos 0; rutas reportadas 0
- Rutas únicas representativas: sin rutas únicas recuperadas
- Lectura: Rama funcional de interfaz (el nombre sugiere retirada de QR); verificar alcance UI y PR asociado antes de rescatar.
- Estado de pruebas: no ejecutadas ahora; verificar logs/CI por SHA.
- Siguiente paso: revisar PRs y commits exclusivos, identificar solapamiento con main y etiquetar como integrada, antecedente, candidata a rescate o pendiente.

## audit/arbol-vivo-continuidad-20261011
- SHA: `6b08799b6e339dfefe6f3e59032a42225038c3fa`
- Último commit: docs: establish living ARKI continuity entrypoint for existing tree (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/6b08799b6e339dfefe6f3e59032a42225038c3fa
- Diferencia contra main: diverged; ahead 439, behind 59, total commits exclusivos 439; rutas reportadas 91
- Rutas únicas representativas: added .github/workflows/arki-controlled-executor.yml, added .github/workflows/arki-f1-f10-evidence.yml, added .github/workflows/arki-research-trends.yml, added .github/workflows/maqueta-viva-smoke.yml, added 00_INICIO_ARKI.md, added ARKI-MAQUETA-VIVA.cmd, added ARKI-RESEARCH-WATCH.cmd, modified client/index.html, modified client/src/App.tsx, modified client/src/components/ArkiFirstContact.tsx
- Lectura: Auditoría de continuidad del Árbol Vivo; distinguir diagnóstico/documentación de cambios funcionales.
- Estado de pruebas: no ejecutadas ahora; verificar logs/CI por SHA.
- Siguiente paso: revisar PRs y commits exclusivos, identificar solapamiento con main y etiquetar como integrada, antecedente, candidata a rescate o pendiente.

## audit/arki-continuity-daily-20261014
- SHA: `ff4bd1df4f78e135ded5cb4ddb26ff43f23c3e14`
- Último commit: docs(arki): reconcile continuity map with audited events and verified GitHub state (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/ff4bd1df4f78e135ded5cb4ddb26ff43f23c3e14
- Diferencia contra main: diverged; ahead 2, behind 18, total commits exclusivos 2; rutas reportadas 2
- Rutas únicas representativas: modified docs/arki-master-map/ARKI_CONTINUITY_EVENTS.jsonl, modified docs/arki-master-map/ARKI_MAPA_VIVO_CONTINUIDAD.md
- Lectura: Auditoría diaria de continuidad; verificar si sus hallazgos ya están reflejados en el mapa vivo de main.
- Estado de pruebas: no ejecutadas ahora; verificar logs/CI por SHA.
- Siguiente paso: revisar PRs y commits exclusivos, identificar solapamiento con main y etiquetar como integrada, antecedente, candidata a rescate o pendiente.

## audit/deepseek-f5-f9-redteam-v1
- SHA: `4e8c6cc12d5bc9bf50ce6b7488784a06bf34b4b5`
- Último commit: docs(audit): add F5-F9 offline red-team evidence pack (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/4e8c6cc12d5bc9bf50ce6b7488784a06bf34b4b5
- Diferencia contra main: diverged; ahead 75, behind 59, total commits exclusivos 75; rutas reportadas 31
- Rutas únicas representativas: modified client/index.html, modified client/src/App.tsx, modified client/src/components/ArkiFirstContact.tsx, modified client/src/pages/ArkiSuperarchitectCommandCenterPage.tsx, added docs/arki-master-map/AGK_DELTA_005_PERSISTENT_NAMING_CONTRACT_V1.md, modified docs/arki-master-map/AGK_OCCT_EXECUTION_EVIDENCE_V1.md, added docs/arki-master-map/ARKI_CAPABILITY_INSERTION_MAP_FROM_BUSINESS_PUBLIC_WORKS_V1.md, added docs/arki-master-map/ARKI_F5_F9_PRE_IMPLEMENTATION_RED_TEAM_DOSSIER_V1.md, added docs/arki-master-map/ARKI_F5_F9_RED_TEAM_OFFLINE_EVIDENCE_PACK_V1.md, added docs/arki-master-map/ARKI_F6_AGK_INTEGRAL_CLOSURE_GATE_V1.md
- Lectura: Rama de pruebas adversariales F5–F9; su evidencia solo vale para el SHA, casos y entorno documentados.
- Estado de pruebas: no ejecutadas ahora; verificar logs/CI por SHA.
- Siguiente paso: revisar PRs y commits exclusivos, identificar solapamiento con main y etiquetar como integrada, antecedente, candidata a rescate o pendiente.

## audit/l04-agk-only-trigger
- SHA: `94170fa14c568d54bda8f04098e23c4e35d02e31`
- Último commit: Audit L-04 AGK-only workflow trigger (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/94170fa14c568d54bda8f04098e23c4e35d02e31
- Diferencia contra main: diverged; ahead 104, behind 88, total commits exclusivos 104; rutas reportadas 51
- Rutas únicas representativas: added .github/workflows/compas-capability.yml, added docs/ARKI_OPERATIONAL_ARCHITECTURE_FREEZE_1_0.md, added requirements-compas.txt, added server/agk/familyCompiler.test.ts, added server/agk/familyCompiler.ts, modified server/agk/regeneration.ts, modified server/agk/types.ts, modified server/arkiGeometryKernel.test.ts, modified server/arkiGeometryKernel.ts, added server/capabilityFabric/architecturalCapabilityRepository.test.ts
- Lectura: Auditoría sobre el disparador AGK; la variante v2 debe compararse con la original para determinar correcciones, no asumir que v2 sustituye formalmente a la primera.
- Estado de pruebas: no ejecutadas ahora; verificar logs/CI por SHA.
- Siguiente paso: revisar PRs y commits exclusivos, identificar solapamiento con main y etiquetar como integrada, antecedente, candidata a rescate o pendiente.

## audit/l04-agk-only-trigger-v2
- SHA: `a56a5581b57afc153b0c190e14b7e0a0e816d7dc`
- Último commit: Audit L-04 AGK-only workflow trigger (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-web/commit/a56a5581b57afc153b0c190e14b7e0a0e816d7dc
- Diferencia contra main: diverged; ahead 12, behind 88, total commits exclusivos 12; rutas reportadas 7
- Rutas únicas representativas: added .github/workflows/compas-capability.yml, added server/agk/familyCompiler.test.ts, added server/agk/familyCompiler.ts, modified server/agk/regeneration.ts, modified server/agk/types.ts, modified server/arkiGeometryKernel.test.ts, modified server/arkiGeometryKernel.ts
- Lectura: Auditoría sobre el disparador AGK; la variante v2 debe compararse con la original para determinar correcciones, no asumir que v2 sustituye formalmente a la primera.
- Estado de pruebas: no ejecutadas ahora; verificar logs/CI por SHA.
- Siguiente paso: revisar PRs y commits exclusivos, identificar solapamiento con main y etiquetar como integrada, antecedente, candidata a rescate o pendiente.
