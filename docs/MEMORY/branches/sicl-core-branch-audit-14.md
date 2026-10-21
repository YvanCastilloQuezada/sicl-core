# SICL Core — auditoría de ramas (lote 14: GIS, pruebas y baseline)

Base: `main@de43b6b833731c87fb6277834484545bd953d76a`. No se ejecutaron pruebas.

## rfc-028-029-gis-ollama
- SHA: `56d7c8b7ed45ee86ba05868516f5d637a9801f1d`
- Último commit: feat: implement GIS parcel snapshots and local Ollama copilot (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/56d7c8b7ed45ee86ba05868516f5d637a9801f1d
- Comparación: behind; ahead 0, behind 194; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Integración GIS/Ollama; revisar separación entre recuperación de fuentes y razonamiento generado.
- Pruebas: no ejecutadas ahora.
- Recomendación: comprobar CI y fuentes asociadas; conservar el resultado como pendiente si no hay evidencia reproducible.

## rfc-028-gis-cadastral-ifc-adapter
- SHA: `db7b9ecfdeaf206e76e7769efa20757044363853`
- Último commit: feat: add physical IFC adapter and GIS RFC-028 (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/db7b9ecfdeaf206e76e7769efa20757044363853
- Comparación: behind; ahead 0, behind 196; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Adaptador GIS/catastro/IFC; validar jurisdicción, coordenadas, esquema y procedencia.
- Pruebas: no ejecutadas ahora.
- Recomendación: comprobar CI y fuentes asociadas; conservar el resultado como pendiente si no hay evidencia reproducible.

## test/microcase-dev-001-e2e
- SHA: `d974eba2d8c79d37d4f6ad89df780f71889c9fde`
- Último commit: test(archi): lock deterministic promotion order (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/d974eba2d8c79d37d4f6ad89df780f71889c9fde
- Comparación: behind; ahead 0, behind 7; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Microcaso E2E; verificar los pasos exactos y que el resultado se reproduzca en el SHA actual.
- Pruebas: no ejecutadas ahora.
- Recomendación: comprobar CI y fuentes asociadas; conservar el resultado como pendiente si no hay evidencia reproducible.

## main
- SHA: `de43b6b833731c87fb6277834484545bd953d76a`
- Último commit: Reconcile Core authority documentation with ARKI Live Map (#45)

* docs(core): mark legacy limitations ledger as historical pending reconciliation

* docs(core): establish cross-repo authority contract for F7 F8 (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/de43b6b833731c87fb6277834484545bd953d76a
- Comparación: identical; ahead 0, behind 0; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Baseline canónico Core; SHA de referencia de esta auditoría.
- Pruebas: no ejecutadas ahora.
- Recomendación: comprobar CI y fuentes asociadas; conservar el resultado como pendiente si no hay evidencia reproducible.

## docs/memory-auditoria-integracion-20261021
- SHA: `d17eb5bc5e2b38579f74d641f27474321d2764b7`
- Último commit: docs(memory): clarify ACS isolation and evidence limits (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/d17eb5bc5e2b38579f74d641f27474321d2764b7
- Comparación: ahead; ahead 35, behind 0; commits exclusivos 35; rutas 33.
- Rutas: docs/MEMORY/01-fundamentos-doctrina-conocimiento.md, docs/MEMORY/02-sicl-web-revivir-mapas-vivos.md, docs/MEMORY/03-sicl-core-memoria-institucional.md, docs/MEMORY/04-acs-laboratorio-evidencia.md, docs/MEMORY/05-integracion-seguridad-plan.md, docs/MEMORY/README.md, docs/MEMORY/branches/arki-acs-branch-audit.md, docs/MEMORY/branches/arki-acs-branch-register.md
- Lectura: Rama que contiene esta auditoría documental MEMORY; los cambios son documentación en docs/MEMORY y no código funcional.
- Pruebas: no ejecutadas ahora.
- Recomendación: comprobar CI y fuentes asociadas; conservar el resultado como pendiente si no hay evidencia reproducible.
