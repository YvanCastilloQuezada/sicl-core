# BIMChangeSet Review — Ejemplo ejecutable

## Estado de seguridad

> **PREVIEW ONLY.** Este expediente no modificó el archivo IFC, Revit ni Archicad. La exportación está bloqueada hasta que exista una revisión humana aprobada y una orden de exportación separada.

## Identificación

| Campo | Valor |
|---|---|
| Proyecto | `IFC-HTTP` |
| Snapshot | `IFC-9b8f2a1c0d4e1122` |
| Change set | `CS-PREVIEW-001` |
| Archivo | `sample.ifc` |
| Fuente | `IfcOpenShell 0.8.5` |
| Hash | `sha256:demo-model-hash` |
| CRS | `EPSG:4326` |
| Unidades | `SI` |
| Solicitado por | `architect@example.org` |
| Estado | `HUMAN_REVIEW_REQUIRED` |

## Flujo

```text
IFC original ──lectura──> BIMModelSnapshot ──propuesta──> BIMChangeSet
     │                              │                         │
     │                              └── hash conservado        └── PREVIEW
     │                                                        │
     └────────────── sin escritura ◄── revisión humana ◄─────┘
```

## Cambios propuestos

| Nº | GlobalId | Entidad | Parámetro | Actual | Propuesto | Estado |
|---:|---|---|---|---:|---:|---|
| 1 | `2Hwall00000000002` | `IfcWall` | `Height` | `3.20 m` | `3.50 m` | `PENDING_REVIEW` |
| 2 | `2Hspace000000002` | `IfcSpace` | `Name` | `Sala` | `Sala principal` | `PENDING_REVIEW` |

## Validación RNE referencial

| Elemento | Norma candidata | Estado del fixture | Resultado | Interpretación |
|---|---|---|---|---|
| `IfcWall` | A.010 | `NO_VERIFICADA` | `REVIEW_REQUIRED` | No demuestra cumplimiento |
| `IfcWall` | E.030 | `NO_VERIFICADA` | `REVIEW_REQUIRED` | Requiere revisión estructural |
| `IfcWall` | E.060 | `NO_VERIFICADA` | `REVIEW_REQUIRED` | Requiere revisión de concreto |
| `IfcSpace` | A.010 | `NO_VERIFICADA` | `REVIEW_REQUIRED` | Requiere revisión arquitectónica |
| `IfcSpace` | IS.010 | `NO_VERIFICADA` | `REVIEW_REQUIRED` | Requiere revisión sanitaria |
| `IfcSpace` | EM.010 | `NO_VERIFICADA` | `REVIEW_REQUIRED` | Requiere revisión eléctrica |

El resultado no es una certificación ni una conclusión de cumplimiento. El corpus RNE se conserva como referencia no verificada hasta una promoción humana formal.

## Preguntas para autoridad humana

1. ¿El cambio de altura está respaldado por una decisión de diseño aprobada?
2. ¿La modificación afecta el cálculo estructural o la compatibilidad con otros elementos?
3. ¿El nombre del espacio coincide con la documentación oficial del proyecto?
4. ¿El CRS y las unidades son correctos para este modelo?
5. ¿Debe intervenir un especialista antes de autorizar una exportación?

## Resolución

```text
[ ] APPROVE_FOR_EXPORT
[ ] REJECT
[ ] REQUEST_CHANGES
[ ] ESCALATE
```

| Campo | Firma humana |
|---|---|
| Revisor | ______________________________ |
| Rol / autoridad | ______________________________ |
| Fecha UTC | ______________________________ |
| Comentario | ______________________________ |
| HumanReview ID | ______________________________ |

## Resultado técnico esperado

```json
{
  "change_set_id": "CS-PREVIEW-001",
  "mode": "PREVIEW",
  "applied": false,
  "human_review_required": true,
  "decision_created": false,
  "export_authorized": false
}
```
