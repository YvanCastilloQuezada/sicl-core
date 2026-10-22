# ARKI-ACS — auditoría de todas las ramas

**Base:** `main@1a48ed4426b958cb45be2599efc1e8d624baab80`.  
**Fecha de corte:** 2026-10-21. No se ejecutaron pruebas en esta auditoría.

## main
- SHA: `1a48ed4426b958cb45be2599efc1e8d624baab80`
- Último commit: docs(arki): add ACS branch catalog for MEMORY audit (fecha desconocida) https://github.com/YvanCastilloQuezada/arki-acs/commit/1a48ed4426b958cb45be2599efc1e8d624baab80
- Comparación contra main: identical; ahead 0, behind 0; commits exclusivos 0; rutas reportadas 0.
- Rutas únicas: sin rutas únicas reportadas
- Avance e interpretación: Baseline canónico actual del laboratorio; es la referencia para evaluar propuestas, no evidencia por sí misma de que todo el aislamiento esté implementado.
- Evidencia: los documentos de ACS declaran aislamiento por proceso, pero contenedor y microVM no implementados; además, CPU/RAM no están aplicados por IsolatedWorker según LIMITATIONS. No se corrieron `dotnet test` en este trabajo.
- Recomendación: conservar el laboratorio aislado de la autoridad de Core; toda promoción requiere SHA, entorno, corpus, logs y revisión humana.

## experiment/arki-ideas-acs-20261015
- SHA: `507e0b18862e6cf13e1e72f559cca8f343411fc2`
- Último commit: docs(arki): enumerate all visible branches for controlled idea recovery (fecha desconocida) https://github.com/YvanCastilloQuezada/arki-acs/commit/507e0b18862e6cf13e1e72f559cca8f343411fc2
- Comparación contra main: diverged; ahead 2, behind 87; commits exclusivos 2; rutas reportadas 2.
- Rutas únicas: added docs/arki-ideas/BRANCH_INVENTORY_20261015.md, added docs/arki-ideas/RECOVERY_PROTOCOL.md
- Avance e interpretación: Rama de ideas experimentales ACS. Debe mantenerse como investigación separada: ideas y fixtures no son capacidad promovida; revisar ledger, recibos y diferencias exactas antes de incorporar algo.
- Evidencia: los documentos de ACS declaran aislamiento por proceso, pero contenedor y microVM no implementados; además, CPU/RAM no están aplicados por IsolatedWorker según LIMITATIONS. No se corrieron `dotnet test` en este trabajo.
- Recomendación: conservar el laboratorio aislado de la autoridad de Core; toda promoción requiere SHA, entorno, corpus, logs y revisión humana.

## feat/oece-arki-integration-v1
- SHA: `3fa4e4a799606e3595a29688223b0f50c1672ef8`
- Último commit: test(oece): persist bounded Yanahuara technical fragment (fecha desconocida) https://github.com/YvanCastilloQuezada/arki-acs/commit/3fa4e4a799606e3595a29688223b0f50c1672ef8
- Comparación contra main: behind; ahead 0, behind 2; commits exclusivos 0; rutas reportadas 0.
- Rutas únicas: sin rutas únicas reportadas
- Avance e interpretación: Integración OECE–ARKI: el nombre indica puente de búsqueda/inspección. Confirmar el contrato de evidencia, las dependencias externas y que la integración no pueda promocionar código experimental automáticamente.
- Evidencia: los documentos de ACS declaran aislamiento por proceso, pero contenedor y microVM no implementados; además, CPU/RAM no están aplicados por IsolatedWorker según LIMITATIONS. No se corrieron `dotnet test` en este trabajo.
- Recomendación: conservar el laboratorio aislado de la autoridad de Core; toda promoción requiere SHA, entorno, corpus, logs y revisión humana.
