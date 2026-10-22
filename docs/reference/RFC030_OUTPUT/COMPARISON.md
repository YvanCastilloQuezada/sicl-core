# RFC-030 — Comparación de salida técnica

## Modos generados

| Modo | Hojas | Formato | Escala | Estado |
|---|---:|---|---|---|
| `SINGLE_VIEW_PER_SHEET` | 5 | A3 horizontal | 1:50 | Válido |
| `PROFESSIONAL_LAYOUT` | 2 | A3 horizontal | 1:50 | Válido |

## Comparación contra `PROY_FERNANDEZ_ROJAS.pdf`

| Criterio | Fixture | RFC-030 generado | Resultado |
|---|---|---|---|
| Fondo | Blanco puro | Blanco puro | Coincide |
| Líneas | Negro técnico | Negro técnico | Coincide |
| Ejes | Círculos y nomenclatura | Círculos A–C / 1–5 | Cumple vertical slice |
| Cotas | Parciales, entre ejes y totales | Dos anillos declarados y visibles | Cumple |
| Niveles | NPT con símbolo | NPT ±0.00 | Cumple |
| Vanos | Identificadores técnicos | P-1, V-1, V-2 y arco de puerta | Cumple |
| Cajetín | Peruano | 180 × 60 mm, ocho campos | Cumple |
| Norte y escala | Presentes | Norte y escala gráfica presentes | Cumple |
| Cuadros | Normativo, áreas, vanos | Referenciados en lámina y entidades | Cumple |

La salida permanece técnica, monocroma y separada del namespace `/PRESENTATION`. El motor RFC-034.1 calcula las posiciones; RFC-030 dibuja y exporta.
