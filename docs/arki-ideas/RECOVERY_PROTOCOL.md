# ARKI — Banco experimental de recuperación (sicl-core)

Estado: BRANCH_CREATED / INVENTORY_PENDING / NO_CANONICAL_PROMOTION.

## Alcance
Core, AGK, D-2, geometría, contratos, inteligencia arquitectónica y aprendizaje.

## Contrato de extracción
- Inventariar todas las ramas accesibles y cada cambio exclusivo, incluidos documentos, código, tests, fixtures y workflows.
- Clasificar ideas individualmente; una rama puede producir muchas ideas y una idea puede tener varios orígenes.
- Registrar ID, nombre, problema, propuesta, SHA y ruta de origen, dependencias, líneas de código, pruebas, evidencia, limitaciones, madurez y relación con el canon.
- Copiar los artefactos a un laboratorio aislado y probarlos antes de declararlos preservados.
- Mantener la rama original hasta reconciliar todos sus archivos, referencias y PRs; nunca borrar basándose solo en coincidencia de nombres.
- No reescribir historia Git; la poda de ramas es posterior a la preservación demostrada.
- No fusionar automáticamente con main, ni cambiar contratos FROZEN, AGK único, autorización ACE88 o Delta 6.2.

## Estado actual
Rama experimental creada. Auditoría exhaustiva, extracción física, validación y poda pendientes. El catálogo global de sicl-web vive en `experiment/arki-ideas-mapa-vivo-20261015`.
