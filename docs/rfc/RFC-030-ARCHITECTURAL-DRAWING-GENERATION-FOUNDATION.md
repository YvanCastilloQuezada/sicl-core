# RFC-030 — Architectural Drawing Generation Foundation

**Estado:** IMPLEMENTED — TECHNICAL DRAWING FOUNDATION
**Namespace CLI:** `/DRAWING`
**Namespace HTTP:** `/drawings`
**Output mode:** `TECHNICAL`
**Dependencia de composición:** RFC-034.1 — Sheet Composition & Layout Engine

## 1. Propósito

RFC-030 define la generación de planos arquitectónicos técnicos a partir de una fuente geométrica verificable. Su objetivo es producir documentación técnica monocroma, medible y auditable para revisión arquitectónica, expediente y coordinación de obra.

RFC-030 no genera láminas narrativas de presentación ni renders fotorrealistas. Esos usos pertenecen respectivamente a RFC-034 y RFC-035.

## 2. Alcance

El módulo técnico cubre:

- Importación o construcción de un modelo IFC verificable.
- Validación geométrica y de datos mínimos.
- Proyección de plantas, cortes y elevaciones.
- Ejes alfanuméricos y niveles NPT.
- Cotas exteriores e interiores con doble anillo.
- Nombres de espacios y áreas en m².
- Nomenclatura de puertas y ventanas.
- Simbología de puertas con hoja, arco de apertura y eje.
- Achurados por material.
- Norte y escala gráfica calibrada.
- Cuadros de áreas, vanos y notas técnicas.
- Cajetín técnico estándar peruano.
- Composición de hoja mediante RFC-034.1.
- Exportación PDF técnico y revisión contra fixture.

## 3. Modos de salida

### 3.1 `SINGLE_VIEW_PER_SHEET`

Genera una vista técnica principal por hoja, con cinco páginas mínimas para el vertical slice residencial:

1. Planta baja.
2. Planta alta.
3. Corte longitudinal.
4. Elevación principal.
5. Lámina técnica de síntesis o cuadro consolidado.

### 3.2 `PROFESSIONAL_LAYOUT`

Agrupa la documentación en dos láminas profesionales:

- A-01: plantas arquitectónicas.
- A-02: corte, elevación, cuadros y referencias.

La composición no se calcula manualmente: utiliza `SheetLayout`, zonas y bounding boxes de RFC-034.1.

## 4. Fixture técnico

El fixture normativo es:

```text
docs/reference/PROY_FERNANDEZ_ROJAS.pdf
```

El lenguaje gráfico de referencia es:

- Fondo blanco puro `#FFFFFF`.
- Líneas y texto negro `#000000`.
- Achurados grises controlados.
- Tipografía sans-serif técnica tipo Arial/Helvetica.
- Jerarquía de línea técnica 0.18 / 0.35 / 0.50 / 0.70 mm.
- Ejes circulares de 8 mm con letra o número.
- Cajetín peruano de 180 × 60 mm en hoja A3.
- Escala numérica real y escala gráfica calibrada.

## 5. Entidades

| Entidad | Propósito |
|---|---|
| `DrawingProject` | Proyecto técnico y metadatos de salida |
| `BIMModelSnapshot` | Fuente geométrica inmutable de generación |
| `DrawingView` | Planta, corte o elevación proyectada |
| `DrawingElement` | Muros, losas, puertas, ventanas y anotaciones |
| `DimensionChain` | Cadena de cotas interior o exterior |
| `TechnicalSymbol` | Ejes, norte, niveles y símbolos arquitectónicos |
| `TitleBlock` | Cajetín técnico y control documental |
| `DrawingSet` | Conjunto de vistas y láminas exportables |

## 6. Reglas constitucionales

1. RFC-030 usa exclusivamente los namespaces `/DRAWING` y `/drawings`.
2. El fondo técnico es blanco puro.
3. No se mezclan paletas, tarjetas ni narrativa de RFC-034.
4. No se incorporan renders de RFC-035 como geometría técnica.
5. Las escalas se declaran como valores reales o se marca `INSUFFICIENT_DATA`.
6. Las áreas y dimensiones provienen del snapshot o se marcan `INSUFFICIENT_DATA`.
7. `BIMModelSnapshot` no se modifica durante la generación.
8. La generación no crea `Decision` automáticamente.
9. El layout se calcula con RFC-034.1; RFC-030 conserva la responsabilidad de dibujar y exportar.
10. Una lámina con colisiones, márgenes violados o elementos truncados no puede marcarse como válida.

## 7. Calidad profesional mínima

Cada salida debe verificar:

- Escala numérica real.
- Ejes alfanuméricos.
- Doble anillo de cotas.
- Niveles NPT.
- Nombre de ambiente y área.
- V-1, V-2, P-1, P-2 y demás nomenclatura de vanos.
- Puertas con arco de apertura.
- Achurado por material.
- Cajetín estándar.
- Leyendas y notas.
- Norte y escala gráfica.
- Cuadros normativo, de áreas y de vanos.

## 8. CLI

```text
/DRAWING IFC IMPORT <file>
/DRAWING IFC VALIDATE <project_id>
/DRAWING GENERATE <project_id> --mode=SINGLE_VIEW_PER_SHEET|PROFESSIONAL_LAYOUT
/DRAWING SET SHOW <drawing_set_id>
/DRAWING SET EXPORT <drawing_set_id> --format=PDF
/DRAWING REVIEW SUBMIT <drawing_set_id> <actor> <authority> <justification>
/DRAWING REVIEW APPROVE <drawing_set_id>
/DRAWING REVIEW REJECT <drawing_set_id> <reason>
```

## 9. HTTP

```text
POST /v1/projects/{project_id}/drawings/import
POST /v1/projects/{project_id}/drawings/validate
POST /v1/projects/{project_id}/drawings/generate
GET  /v1/projects/{project_id}/drawings/sets
GET  /v1/projects/{project_id}/drawings/sets/{drawing_set_id}
GET  /v1/projects/{project_id}/drawings/sets/{drawing_set_id}/export?format=PDF
POST /v1/projects/{project_id}/drawings/sets/{drawing_set_id}/review/submit
POST /v1/projects/{project_id}/drawings/sets/{drawing_set_id}/review/approve
POST /v1/projects/{project_id}/drawings/sets/{drawing_set_id}/review/reject
```

## 10. Separación de RFCs

| Aspecto | RFC-030 | RFC-034 | RFC-035 |
|---|---|---|---|
| Uso | Técnico, expediente, obra | Cliente, pitch, portafolio | Render fotorrealista |
| Namespace CLI | `/DRAWING` | `/PRESENTATION` | `/RENDER` |
| Namespace HTTP | `/drawings` | `/presentations` | `/renders` |
| Fondo | Blanco | Paleta autorizada | Imagen/material PBR |
| Output | `TECHNICAL` | `PRESENTATION` | `PHOTOREALISTIC` |

Los tres módulos pueden coexistir, pero no comparten fixture, estado ni contrato visual.

## 11. Estado esperado

```text
TECHNICAL DRAWING FOUNDATION: IMPLEMENTED
LAYOUT COMPOSITION: RFC-034.1
FIXTURE: PROY_FERNANDEZ_ROJAS.pdf
CORE MODIFIED: NO
DECISION CREATED AUTOMATICALLY: NO
BIMModelSnapshot MODIFIED: NO
```
