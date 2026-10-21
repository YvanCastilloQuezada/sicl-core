# Registro de ramas — arki-acs

**Fecha de inventario:** 2026-10-21  
**Rama por defecto:** `main`  
**Ramas descubiertas en GitHub:** 3  
**Objetivo:** registrar cada rama por su nombre exacto y SHA, compararla contra `main`, resumir sus cambios únicos, evidencia y destino posible. Esta lista no afirma que las ramas estén integradas ni que sus pruebas hayan pasado.

> Este registro es acumulativo. “Comparación inicial documentada; ver auditoría arki-acs-branch-audit.md” significa que solo se ha confirmado la existencia de la referencia y su SHA. La comparación contra main, commits y contenido debe incorporarse por lotes. No se eliminarán ramas ni se harán merges durante la auditoría.

| Rama | SHA actual observado | Estado de auditoría |
|---|---|---|
| `experiment/arki-ideas-acs-20261015` | `507e0b18862e6cf13e1e72f559cca8f343411fc2` | [Auditoría](arki-acs-branch-audit.md) |
| `feat/oece-arki-integration-v1` | `3fa4e4a799606e3595a29688223b0f50c1672ef8` | Comparación inicial documentada; ver auditoría arki-acs-branch-audit.md |
| `main` | `1a48ed4426b958cb45be2599efc1e8d624baab80` | Comparación inicial documentada; ver auditoría arki-acs-branch-audit.md |

## Criterios para cerrar cada rama

1. SHA y último commit exactos.
2. Diferencia contra main: ahead/behind/diverged/identical y archivos modificados.
3. Propósito y avances reales descritos por los cambios/commits.
4. Pruebas/evidencias presentes y si hay logs actuales verificables.
5. Relación con otras ramas/PR, duplicación, obsolescencia o trabajo pendiente.
6. Recomendación: integrar, rescatar selectivamente, conservar histórica, cerrar tras autorización o seguir investigando.

## Restricciones

No se infiere “mergeado” por similitud de código ni “probado” por la existencia de tests. No se hacen cambios a código funcional, main, ni ramas ajenas a esta auditoría.
