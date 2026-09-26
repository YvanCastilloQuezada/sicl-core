# RFC-034 — Architectural Presentation Sheets

**Estado:** DRAFT — REQUIRES PRODUCT OWNER APPROVAL
**Autor propuesto:** Yvan Castillo (Product Owner) + Asesor IA
**Implementador:** Manus
**Dependencias:** RFC-019 (escalas), RFC-026 (conocimiento), RFC-027 (BIM/IFC), RFC-030 (Drawing Foundation)
**Escala objetivo:** `edificacion`
**LOD objetivo:** 200, 300
**Salida:** PDF a color + PNG opcional
**Alcance:** Láminas para cliente, pitch y portafolio

## 1. Resumen

RFC-034 introduce el modo **Láminas de Presentación**, distinto del plano técnico de RFC-030. Comunica diseño a clientes, concursos, portafolio y presentaciones. No sustituye los planos técnicos ni se presenta ante municipalidades.

> Un plano técnico (RFC-030) se firma; una lámina de presentación (RFC-034) se muestra.

## 2. Motivación

Un arquitecto necesita dos lenguajes visuales: uno técnico para municipalidad, expediente y obra, y uno narrativo para cliente, pitch y concurso. RFC-034 separa ambos lenguajes y evita híbridos fallidos.

## 3. Alcance

Incluye:

- `PresentationSet`, `PresentationSheet`, `PresentationTemplate`, `PresentationPalette`, `PresentationBlock` y `PresentationView`.
- Plantillas de composición, tipografía, márgenes y paleta.
- Generación desde `BIMModelSnapshot`.
- Paletas clara, oscura, tierra, monocromática y blueprint.
- Tarjetas, callouts, badges y anotaciones explicativas.
- Exportación PDF a color y PNG opcional.
- Persistencia append-only con hash del PDF.
- Estado `DRAFT` hasta `HumanReview`.

Fuera de alcance: planos técnicos normalizados (RFC-030), renders fotorrealistas (RFC-035), video/animación y escalas distintas de `edificacion`.

## 4. Límites constitucionales

RFC-034 no modifica el Core determinista, no añade entidades a SC-005, no escribe en IFC, no sustituye RFC-030 y no sirve como documentación técnica, legal o municipal.

## 5. Entidades nuevas

| Entidad | Propósito |
|---|---|
| `PresentationSet` | Conjunto de láminas de presentación |
| `PresentationSheet` | Lámina individual de planta, corte, elevación o composición mixta |
| `PresentationTemplate` | Layout, tipografía y márgenes declarativos |
| `PresentationPalette` | Paleta visual controlada |
| `PresentationBlock` | Tarjeta, badge, callout o texto narrativo |
| `PresentationView` | Vista derivada de `DrawingView` con capa de estilo |

## 6. Invariantes constitucionales

1. Todo `PresentationSet` nace `DRAFT` y nunca `PUBLISHED` sin `HumanReview`.
2. Toda `PresentationSheet` declara `output_mode = PRESENTATION`.
3. La lámina declara escala numérica o `ESCALA CONCEPTUAL`.
4. Los datos cuantitativos son reales desde `BIMModelSnapshot` o `INSUFFICIENT_DATA`.
5. El cajetín muestra `NOT_FOR_MUNICIPAL_SUBMISSION`.
6. Toda lámina incluye `CONCEPTO PRELIMINAR · SUJETO A CAMBIOS` o `VERSIÓN PRESENTACIÓN`.
7. Paleta y tipografía deben coincidir con `PresentationTemplate`.
8. La aprobación exige `actor`, `authority` y `justification`.
9. `PresentationSet` es append-only; una nueva versión usa `supersedes_id`.
10. El hash del PDF se persiste.
11. La generación no modifica `BIMModelSnapshot`.
12. No se crea ninguna `Decision` automáticamente.

## 7. Paletas permitidas

| Paleta | Fondo | Texto | Acento | Uso |
|---|---|---|---|---|
| `CLASSIC_CREAM` | `#F5F0E8` | `#2A2A2A` | `#B8763D` | Portafolio arquitectónico |
| `MONOCHROME` | `#FFFFFF` | `#000000` | `#666666` | Presentación sobria |
| `EARTH_TONES` | `#EDE4D3` | `#3D2B1F` | `#A0522D` | Proyectos residenciales |
| `DARK_PREMIUM` | `#1A1A1A` | `#FFFFFF` | `#C9A96E` | Pitch de inversionistas |
| `BLUEPRINT` | `#1B2A4A` | `#FFFFFF` | `#4A90E2` | Conceptual técnico-lúdico |

Se prohíben neón, degradados agresivos, glow, sombras digitales y transparencias agresivas.

## 8. Namespace CLI

```text
/PRESENTATION TEMPLATE LOAD <template_id>
/PRESENTATION TEMPLATE SHOW <template_id>
/PRESENTATION TEMPLATE LIST
/PRESENTATION PALETTE SET <palette_id>
/PRESENTATION GENERATE <project_id> <bim_snapshot_id> --sheet-type=FLOOR-PLAN --level=N1 --lod=300 --scale=1:100
/PRESENTATION GENERATE <project_id> <bim_snapshot_id> --sheet-type=SET --lod=300 --scale=1:100
/PRESENTATION SET SHOW <presentation_set_id>
/PRESENTATION SET LIST <project_id>
/PRESENTATION SET EXPORT <presentation_set_id> --format=PDF|PNG
/PRESENTATION REVIEW SUBMIT <presentation_set_id> <actor> <authority> <justification>
/PRESENTATION REVIEW APPROVE <presentation_set_id>
/PRESENTATION REVIEW REJECT <presentation_set_id> <reason>
```

## 9. Namespace HTTP

```text
POST /v1/projects/{project_id}/presentations/templates
GET  /v1/projects/{project_id}/presentations/templates
GET  /v1/projects/{project_id}/presentations/templates/{template_id}
POST /v1/projects/{project_id}/presentations/generate
GET  /v1/projects/{project_id}/presentations/sets
GET  /v1/projects/{project_id}/presentations/sets/{presentation_set_id}
GET  /v1/projects/{project_id}/presentations/sets/{presentation_set_id}/export?format=PDF|PNG
POST /v1/projects/{project_id}/presentations/sets/{presentation_set_id}/review/submit
POST /v1/projects/{project_id}/presentations/sets/{presentation_set_id}/review/approve
POST /v1/projects/{project_id}/presentations/sets/{presentation_set_id}/review/reject
```

## 10. Vertical slice demostrable

**Caso:** CASA NIDO DE CAMPO.
**Salida:** cinco láminas de presentación.

1. Planta Baja · Nivel 01.
2. Planta Alta · Nivel 02.
3. Corte Longitudinal A–A.
4. Elevación Principal · Sur.
5. Lámina de Síntesis.

Cada lámina incluye título, subtítulo, norte, escala gráfica o `ESCALA CONCEPTUAL`, áreas reales en m², paleta consistente, cajetín minimalista y `VERSIÓN PRESENTACIÓN · NO PARA TRÁMITE MUNICIPAL`.

## 11. Fixtures

```text
docs/reference/
├── PROY_FERNANDEZ_ROJAS.pdf              (RFC-030 técnico)
├── CASA_NIDO_DE_CAMPO_PRESENTATION.pdf   (RFC-034 presentación)
└── RFC-035/
    ├── torres_exterior.png               (RFC-035 render)
    └── torres_interior.png               (RFC-035 render)
```

## 12. Tests requeridos

Los 18 tests se agrupan en ocho estructurales, seis constitucionales y cuatro de calidad: carga de plantilla, paleta, output mode, escala, append-only, hash, snapshot inmutable, marcador municipal, ausencia de Decision automática, revisión con autoridad, datos cuantitativos, disclaimer, violación de paleta, jerarquía, norte/escala, áreas y exportación PDF/PNG.

## 13. Estado esperado

```text
PRESENTATION FOUNDATION: IMPLEMENTED
VERTICAL SLICE (5 sheets): DEMONSTRABLE
SCALES: edificacion
LOD: 200, 300
OUTPUT: PDF (color), PNG
HUMAN REVIEW: REQUIRED BEFORE PUBLISHED
CORE MODIFIED: NO
RFC-030 COEXISTENCE: GUARANTEED
```

## 14. Aprobación requerida

Antes de implementar, el Product Owner debe aprobar la separación RFC-030/RFC-034, las seis entidades, las 12 invariantes, las cinco paletas, el vertical slice de cinco láminas, los fixtures y que los renders fotorrealistas quedan en RFC-035.

## 15. Relación con RFC-030

| Aspecto | RFC-030 | RFC-034 |
|---|---|---|
| Uso | Municipalidad, expediente, obra | Cliente, pitch, portafolio |
| Fondo | Blanco puro | Paleta predefinida |
| Color | Negro y gris | Color controlado |
| Tipografía | Sans-serif técnica | Display + sans-serif |
| Ejes y cotas | Obligatorios | Opcionales |
| Output mode | `TECHNICAL` | `PRESENTATION` |
| CLI | `/DRAWING` | `/PRESENTATION` |
| HTTP | `/drawings` | `/presentations` |

**RFC-030, RFC-034 y RFC-035 mantienen namespaces, fixtures y estados independientes.**
