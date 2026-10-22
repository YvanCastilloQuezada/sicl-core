# SICL Web — auditoría de ramas (lote 1: memoria, continuidad y Árbol Vivo)

**Referencia base:** `main@9ae8fe504bbb964d8b89d87709ee773e64cbbacb`.  
**Fecha de corte:** 2026-10-21.  
**Método:** comparación de refs contra main + metadatos de commit. No se ejecutaron tests. Las diferencias de archivos son cambios únicos reportados por compare API; si la comparación excede límites de GitHub, el inventario de archivos puede ser parcial.

## feat/arki-autonomy-memory-main-20261013

- **SHA:** `e7237c6f8c671a7a1325fdf87d18b70b6dfda4a8`
- **Último commit:** docs(arki): correct memory consolidation path from source audit
- **Fecha:** No recuperada
- **Commit:** https://github.com/YvanCastilloQuezada/sicl-web/commit/e7237c6f8c671a7a1325fdf87d18b70b6dfda4a8
- **Relación con main:** diverged; 8 commits exclusivos por delante, 59 por detrás; 8 commits en comparación; 4 rutas reportadas.
- **Cambios representativos:** added: docs/arki-master-map/ARKI_BRANCH_COMMIT_CATALOG_20261021.md (1502 líneas cambiadas); added: docs/arki-master-map/ARKI_SICL_WEB_BRANCH_CATALOG_20261021.md (147 líneas cambiadas); added: tools/maqueta-viva/arki-autonomy-memory.cjs (34 líneas cambiadas); added: tools/maqueta-viva/test-arki-autonomy-memory.cjs (9 líneas cambiadas)
- **Lectura / avance:** Introduce una implementación pequeña de memoria autónoma (módulo de 34 líneas y prueba de 9 líneas en el diff contra main); además arrastra un catálogo de ramas y commit. La comparación indica divergencia grande (8 commits exclusivos y 59 detrás): no asumir que contiene el estado más reciente de main.
- **Estado de pruebas:** no ejecutadas en esta auditoría. La existencia de tests/receipts en los archivos no equivale a una ejecución actual.
- **Recomendación:** conservar como fuente de diseño/implementación candidata; comparar módulo, contrato de eventos y persistencia contra MEMORY antes de portar.

## feat/arki-master-map-live-v1

- **SHA:** `2b7bfc8e13626c6cf7ae5da82f818ffabca0df4e`
- **Último commit:** docs(handoff): freeze ARKI continuity baseline before merge
- **Fecha:** No recuperada
- **Commit:** https://github.com/YvanCastilloQuezada/sicl-web/commit/2b7bfc8e13626c6cf7ae5da82f818ffabca0df4e
- **Relación con main:** behind; 0 commits exclusivos por delante, 67 por detrás; 0 commits en comparación; 0 rutas reportadas.
- **Cambios representativos:** No se reportan rutas únicas; revisar historial si se necesita conocer la intención histórica.
- **Lectura / avance:** La rama está 67 commits detrás de main y no aporta commits exclusivos según la comparación; es un antecedente histórico, no una candidata a merge sin una razón concreta.
- **Estado de pruebas:** no ejecutadas en esta auditoría. La existencia de tests/receipts en los archivos no equivale a una ejecución actual.
- **Recomendación:** conservar como antecedente; no fusionar sin un cambio exclusivo que justifique recuperación.

## feat/arki-integration-genealogy-20261013

- **SHA:** `b0a37f1b3f063b66c6f0fcf1ac2cc8ebb4c17ea4`
- **Último commit:** Add Ubuntu one-command SHA-pinned offline validation entrypoint
- **Fecha:** No recuperada
- **Commit:** https://github.com/YvanCastilloQuezada/sicl-web/commit/b0a37f1b3f063b66c6f0fcf1ac2cc8ebb4c17ea4
- **Relación con main:** behind; 0 commits exclusivos por delante, 18 por detrás; 0 commits en comparación; 0 rutas reportadas.
- **Cambios representativos:** No se reportan rutas únicas; revisar historial si se necesita conocer la intención histórica.
- **Lectura / avance:** Está 18 commits detrás de main sin commits exclusivos; el concepto parece absorbido o superado en main, sujeto a comprobar el contenido documental/historial.
- **Estado de pruebas:** no ejecutadas en esta auditoría. La existencia de tests/receipts en los archivos no equivale a una ejecución actual.
- **Recomendación:** conservar como antecedente; no fusionar sin un cambio exclusivo que justifique recuperación.

## feat/arki-live-readonly-pulse-20261013

- **SHA:** `9893dfdaabb2b0e47bfe06cc27c995a6110dbf4b`
- **Último commit:** Run ARKI read-only pulse tests on isolated branch and fail closed when unconfigured
- **Fecha:** No recuperada
- **Commit:** https://github.com/YvanCastilloQuezada/sicl-web/commit/9893dfdaabb2b0e47bfe06cc27c995a6110dbf4b
- **Relación con main:** diverged; 3 commits exclusivos por delante, 44 por detrás; 3 commits en comparación; 3 rutas reportadas.
- **Cambios representativos:** added: .github/workflows/arki-live-pulse.yml (31 líneas cambiadas); added: tools/maqueta-viva/arki-live-pulse.cjs (67 líneas cambiadas); added: tools/maqueta-viva/arki-live-pulse.test.cjs (34 líneas cambiadas)
- **Lectura / avance:** Añade workflow de pulso, script y tests, pero diverge y queda 44 commits detrás; rescatar selectivamente solo si el mecanismo sigue requerido y no está ya reemplazado.
- **Estado de pruebas:** no ejecutadas en esta auditoría. La existencia de tests/receipts en los archivos no equivale a una ejecución actual.
- **Recomendación:** no fusionar rama completa; separar capacidades, identificar PRs/commits ya integrados y validar cada bloque contra main.

## feat/arbol-vivo-precedencias-seguras-20261010

- **SHA:** `34e35e84656e75b301c44ac21cf79dd84430f1f0`
- **Último commit:** test(continuity): push smoke trigger for automatic root handoff refresh
- **Fecha:** No recuperada
- **Commit:** https://github.com/YvanCastilloQuezada/sicl-web/commit/34e35e84656e75b301c44ac21cf79dd84430f1f0
- **Relación con main:** diverged; 741 commits exclusivos por delante, 59 por detrás; 741 commits en comparación; 140 rutas reportadas.
- **Cambios representativos:** added: .github/workflows/arki-continuity.yml (37 líneas cambiadas); added: .github/workflows/arki-controlled-executor.yml (66 líneas cambiadas); added: .github/workflows/arki-f1-f10-evidence.yml (103 líneas cambiadas); added: .github/workflows/arki-research-trends.yml (65 líneas cambiadas); added: .github/workflows/av-ui-001-tree-twin.yml (61 líneas cambiadas); added: .github/workflows/maqueta-viva-smoke.yml (30 líneas cambiadas); added: ARKI-MAQUETA-VIVA.cmd (10 líneas cambiadas); added: ARKI-RESEARCH-WATCH.cmd (7 líneas cambiadas); added: ARKI_HANDOFF.md (34 líneas cambiadas); modified: README.md (1 líneas cambiadas); modified: client/index.html (12 líneas cambiadas); modified: client/src/App.tsx (12 líneas cambiadas); modified: client/src/components/ArkiFirstContact.tsx (2 líneas cambiadas); modified: client/src/pages/ArkiDesignFunnelPage.tsx (19 líneas cambiadas); modified: client/src/pages/ArkiSuperarchitectCommandCenterPage.tsx (31 líneas cambiadas); added: docs/architecture/ARKI_F1_F10_ORGANISM_PRECEDENCE_AUDIT_DRAFT.md (196 líneas cambiadas); added: docs/arki-master-map/AGK_DELTA_005_PERSISTENT_NAMING_CONTRACT_V1.md (56 líneas cambiadas); modified: docs/arki-master-map/AGK_OCCT_EXECUTION_EVIDENCE_V1.md (444 líneas cambiadas)
- **Lectura / avance:** Rama de gran alcance con árbol, contratos, AGK, evidencia F1–F10, UI y múltiples scripts/tests; 741 commits exclusivos y 59 detrás. No es un cambio aislado y no debe fusionarse de golpe; revisar por bloques/PR y evidencias exactas.
- **Estado de pruebas:** no ejecutadas en esta auditoría. La existencia de tests/receipts en los archivos no equivale a una ejecución actual.
- **Recomendación:** no fusionar rama completa; separar capacidades, identificar PRs/commits ya integrados y validar cada bloque contra main.

## feat/arbol-vivo-functional-repair-20261014

- **SHA:** `cad38bc314f9e8fa10d6ae542be888879cec1644`
- **Último commit:** revert premature dependency gate; restore baseline files
- **Fecha:** No recuperada
- **Commit:** https://github.com/YvanCastilloQuezada/sicl-web/commit/cad38bc314f9e8fa10d6ae542be888879cec1644
- **Relación con main:** diverged; 851 commits exclusivos por delante, 59 por detrás; 851 commits en comparación; 222 rutas reportadas.
- **Cambios representativos:** added: .github/workflows/arki-assembly-planner.yml (36 líneas cambiadas); added: .github/workflows/arki-controlled-executor.yml (66 líneas cambiadas); added: .github/workflows/arki-f1-f10-evidence.yml (103 líneas cambiadas); added: .github/workflows/arki-research-trends.yml (65 líneas cambiadas); added: .github/workflows/av-ui-001-tree-twin.yml (61 líneas cambiadas); added: .github/workflows/maqueta-viva-smoke.yml (30 líneas cambiadas); added: 00-START.md (95 líneas cambiadas); added: 00_CONTINUIDAD_AUTOENSAMBLAJE.md (28 líneas cambiadas); added: 00_START.md (166 líneas cambiadas); added: ARKI-MAQUETA-VIVA.cmd (10 líneas cambiadas); added: ARKI-RESEARCH-WATCH.cmd (7 líneas cambiadas); modified: client/index.html (12 líneas cambiadas); modified: client/src/App.tsx (12 líneas cambiadas); modified: client/src/components/ArkiFirstContact.tsx (2 líneas cambiadas); modified: client/src/pages/ArkiDesignFunnelPage.tsx (19 líneas cambiadas); modified: client/src/pages/ArkiSuperarchitectCommandCenterPage.tsx (31 líneas cambiadas); added: docs/architecture/ARKI_F1_F10_ORGANISM_PRECEDENCE_AUDIT_DRAFT.md (196 líneas cambiadas); added: docs/arki-master-map/AGK_DELTA_005_PERSISTENT_NAMING_CONTRACT_V1.md (56 líneas cambiadas)
- **Lectura / avance:** Rama de gran alcance que agrega más trabajo del Árbol Vivo y reparación funcional (851 commits exclusivos, 59 detrás). Hay solapamiento sustancial con precedencias seguras; comparar las dos antes de rescatar cambios.
- **Estado de pruebas:** no ejecutadas en esta auditoría. La existencia de tests/receipts en los archivos no equivale a una ejecución actual.
- **Recomendación:** no fusionar rama completa; separar capacidades, identificar PRs/commits ya integrados y validar cada bloque contra main.

## fix/arki-continuity-workflow-readonly-20261021

- **SHA:** `33f3cd5b7aa1fcdac9d967a264a7618d7eb9ed0a`
- **Último commit:** test(arki): restore transient macro-order contract pending consolidation
- **Fecha:** No recuperada
- **Commit:** https://github.com/YvanCastilloQuezada/sicl-web/commit/33f3cd5b7aa1fcdac9d967a264a7618d7eb9ed0a
- **Relación con main:** ahead; 7 commits exclusivos por delante, 0 por detrás; 7 commits en comparación; 1 rutas reportadas.
- **Cambios representativos:** modified: .github/workflows/arki-continuity-map.yml (42 líneas cambiadas)
- **Lectura / avance:** Rama acotada: 7 commits exclusivos, main no está detrás, solo cambia el workflow de mapa de continuidad. Es la candidata de menor alcance para revisión específica; sigue sin estar mergeada según la información histórica disponible, confirmar PR/estado actual antes de actuar.
- **Estado de pruebas:** no ejecutadas en esta auditoría. La existencia de tests/receipts en los archivos no equivale a una ejecución actual.
- **Recomendación:** revisar diff y permisos del workflow; decidir luego si PR acotado es seguro.

## audit/mapa-arbol-gemelo-reconciliacion-20261014

- **SHA:** `01ace0fbd8c521ef2cc78a93ee53288dd01eeab0`
- **Último commit:** docs(arki): preserve audit findings in canonical 00_START handoff
- **Fecha:** No recuperada
- **Commit:** https://github.com/YvanCastilloQuezada/sicl-web/commit/01ace0fbd8c521ef2cc78a93ee53288dd01eeab0
- **Relación con main:** diverged; 706 commits exclusivos por delante, 59 por detrás; 706 commits en comparación; 138 rutas reportadas.
- **Cambios representativos:** added: .github/workflows/arki-assembly-planner.yml (27 líneas cambiadas); added: .github/workflows/arki-controlled-executor.yml (66 líneas cambiadas); added: .github/workflows/arki-f1-f10-evidence.yml (103 líneas cambiadas); added: .github/workflows/arki-research-trends.yml (65 líneas cambiadas); added: .github/workflows/av-ui-001-tree-twin.yml (61 líneas cambiadas); added: .github/workflows/maqueta-viva-smoke.yml (30 líneas cambiadas); added: 00_CONTINUIDAD_AUTOENSAMBLAJE.md (28 líneas cambiadas); added: 00_START.md (140 líneas cambiadas); added: ARKI-MAQUETA-VIVA.cmd (10 líneas cambiadas); added: ARKI-RESEARCH-WATCH.cmd (7 líneas cambiadas); modified: client/index.html (12 líneas cambiadas); modified: client/src/App.tsx (12 líneas cambiadas); modified: client/src/components/ArkiFirstContact.tsx (2 líneas cambiadas); modified: client/src/pages/ArkiDesignFunnelPage.tsx (19 líneas cambiadas); modified: client/src/pages/ArkiSuperarchitectCommandCenterPage.tsx (31 líneas cambiadas); added: docs/architecture/ARKI_F1_F10_ORGANISM_PRECEDENCE_AUDIT_DRAFT.md (196 líneas cambiadas); added: docs/arki-master-map/AGK_DELTA_005_PERSISTENT_NAMING_CONTRACT_V1.md (56 líneas cambiadas); modified: docs/arki-master-map/AGK_OCCT_EXECUTION_EVIDENCE_V1.md (444 líneas cambiadas)
- **Lectura / avance:** Rama de reconciliación amplia del mapa/árbol/gemelo, con 706 commits exclusivos y 59 detrás; alto solapamiento con otras ramas del Árbol Vivo, exige selección por commits y no merge completo.
- **Estado de pruebas:** no ejecutadas en esta auditoría. La existencia de tests/receipts en los archivos no equivale a una ejecución actual.
- **Recomendación:** no fusionar rama completa; separar capacidades, identificar PRs/commits ya integrados y validar cada bloque contra main.


## Hallazgo transversal de este lote

Las ramas de Árbol Vivo/precedencias/reconciliación son muy divergentes y con cientos de commits exclusivos. Por conteo, no son ramas pequeñas que puedan integrarse de forma segura como una unidad. MEMORY debe inventariar sus commits únicos y dependencias antes de decidir qué recuperar. En cambio, la rama de workflow read-only presenta una diferencia acotada, aunque aún requiere validar permisos, efectos de CI y estado de PR.

