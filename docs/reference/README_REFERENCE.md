# REFERENCIA DE CALIDAD — PLANOS TÉCNICOS RFC-030

**Namespace CLI:** `/DRAWING`
**Namespace HTTP:** `/drawings`
**Output mode:** `TECHNICAL`

Este documento fija el estándar de referencia para planos arquitectónicos técnicos: fondo blanco, líneas negras, achurados grises, escala numérica real, ejes, cotas, niveles NPT, vanos, simbología arquitectónica, norte, escala gráfica y cajetín técnico.

El fixture principal es `docs/reference/PROY_FERNANDEZ_ROJAS.pdf`. RFC-030 no se mezcla con los modos narrativo o fotorrealista.

## 1. Referencias cruzadas

Este documento fija el estándar de RFC-030 — planos técnicos. Otros documentos de referencia:

- `README_REFERENCE_RFC-034.md` — Láminas de presentación.
- `../rfc/RFC-034-ARCHITECTURAL-PRESENTATION-SHEETS.md` — Especificación RFC-034.
- `../rfc/RFC-035-PHOTOREALISTIC-RENDERS.md` — Renders fotorrealistas futuros.
- `RFC-035/` — Carpeta reservada para fixtures de renders.

Un proyecto puede tener salidas técnicas y de presentación sin conflicto. Cada una mantiene su propio namespace, fixture, estado y estándar:

| Modo | CLI | HTTP | Uso |
|---|---|---|---|
| RFC-030 técnico | `/DRAWING` | `/drawings` | Expediente, obra, municipalidad |
| RFC-034 presentación | `/PRESENTATION` | `/presentations` | Cliente, pitch, portafolio |
| RFC-035 render | `/RENDER` | `/renders` | Comunicación fotorrealista futura |
