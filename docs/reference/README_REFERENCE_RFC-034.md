# REFERENCIA DE CALIDAD — LÁMINAS DE PRESENTACIÓN (RFC-034)

**Documento:** `docs/reference/README_REFERENCE_RFC-034.md`
**Estado:** APPROVED — REFERENCE NORMATIVA
**Autoridad:** Product Owner (Arq. Wilfredo Yvan Castillo Quezada)
**Fecha:** 26 de septiembre de 2026
**Fixture:** `CASA_NIDO_DE_CAMPO_PRESENTATION.pdf`

## 1. Propósito

Este documento establece el estándar de calidad visual para las láminas de presentación generadas por ARKI en RFC-034. No sustituye el `README_REFERENCE.md` de RFC-030. Ambos coexisten y deben consultarse según el modo de salida.

## 2. Fixture

`CASA_NIDO_DE_CAMPO_PRESENTATION.pdf` representa una Casa Nido de Campo con paleta sobria crema/tierra, tipografía jerarquizada, narrativa visual, datos de proyecto, norte, escala gráfica o `ESCALA CONCEPTUAL` y disclaimer honesto. Es complemento del plano técnico: RFC-030 se entrega para municipalidad; RFC-034 se muestra al cliente.

## 3. Inventario

| Lámina | Título | Contenido |
|---|---|---|
| CN-01 | Planta Baja · Nivel 01 | Sala doble altura, cocina, comedor, baño, patio, dormitorio flexible, escalera, terraza |
| CN-02 | Planta Alta · Nivel 02 | Dormitorio principal, dormitorios 2 y 3, vestidor, galería, vacío sobre sala |
| CN-03 | Corte Longitudinal A-A | Doble altura, patio interior, ventilación cruzada, galería |
| CN-04 | Elevación Principal · Sur | Fachada, filtros solares, voladizos, materiales |
| CN-05 | Lámina de Síntesis | Datos consolidados del proyecto |

## 4. Permitido

- Fondo crema, oscuro o tierra.
- Paleta de color coherente.
- Tipografía display bold para títulos y sans-serif secundaria.
- Tarjetas, badges, callouts y anotaciones narrativas.
- Renders integrados como acompañamiento si están disponibles.
- Una narrativa por lámina.
- Disclaimer visible: `CONCEPTO PRELIMINAR · SUJETO A CAMBIOS` o `VERSIÓN PRESENTACIÓN`.

## 5. No permitido

- Presentar la lámina como documento municipal.
- Inventar áreas, dimensiones o capacidades.
- Ocultar que el material es conceptual.
- Colores neón, glow o degradados agresivos.
- Mezclar el namespace de RFC-030 (`/DRAWING`).
- Generar sin `output_mode = PRESENTATION`.

## 6. Comparación con RFC-030

| Aspecto | RFC-030 técnico | RFC-034 presentación |
|---|---|---|
| Fondo | Blanco `#FFFFFF` | Crema `#F5F0E8` u otra paleta autorizada |
| Texto | Negro `#000000` | Tierra o color de paleta |
| Acento | Ninguno | Terracota u otro acento autorizado |
| Tipografía | Arial técnica | Display + sans-serif |
| Densidad | Alta | Media |
| Ejes y cotas | Obligatorios | Opcionales |
| Cuadro de vanos | Obligatorio | No aplica |
| Narrativa | No | Sí |
| Namespace | `/DRAWING` | `/PRESENTATION` |

## 7. Aprobación

Firmado por Product Owner, arquitecto/revisor e implementador Manus. Versión 1.0 — RFC-034 Reference Approved.
