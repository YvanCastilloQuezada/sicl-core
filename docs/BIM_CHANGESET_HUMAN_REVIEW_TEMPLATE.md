# Revisión humana de BIMChangeSet

> **Regla de seguridad:** este documento describe cambios propuestos. Ninguna línea de esta revisión aplica cambios en Revit, Archicad o IFC.

## Identificación

| Campo | Valor |
|---|---|
| Proyecto | `{{ project_id }}` |
| Snapshot BIM | `{{ snapshot_id }}` |
| Change set | `{{ change_set_id }}` |
| Modelo de origen | `{{ source_application }} {{ source_version }}` |
| Formato | `{{ format }}` |
| Hash del modelo | `{{ model_hash }}` |
| CRS | `{{ coordinate_reference_system }}` |
| Unidades | `{{ units }}` |
| Solicitado por | `{{ requested_by }}` |
| Modo | **PREVIEW** |
| Estado | `HUMAN_REVIEW_REQUIRED` |

## Resumen visual

```text
MODELO EXTERNO       SICL PREVIEW              APLICACIÓN EXTERNA
     [sin cambios] ──> [revisión humana] ──X──> [no ejecutado]
                              │
                              ├── Aprobar y exportar en una orden posterior
                              ├── Rechazar el change set
                              └── Solicitar correcciones
```

## Cambios propuestos

| Nº | GlobalId | Parámetro | Valor actual | Valor propuesto | Unidad | Riesgo | Estado |
|---:|---|---|---:|---:|---|---|---|
| 1 | `{{ global_id }}` | `{{ parameter }}` | `{{ from }}` | `{{ to }}` | `{{ unit }}` | `{{ risk }}` | `PENDING_REVIEW` |

## Evidencia y procedencia

Cada cambio debe vincularse con una evidencia o una razón explícita. Si no existe evidencia suficiente, la autoridad debe rechazar el cambio o devolverlo para completar la información.

| Cambio | Evidence ID | Fuente | Hash / versión | Estado de evidencia |
|---|---|---|---|---|
| `{{ change_id }}` | `{{ evidence_id }}` | `{{ source }}` | `{{ source_version }}` | `{{ evidence_state }}` |

## Validación normativa

La validación RNE incluida en esta etapa es referencial. Un resultado `REVIEW_REQUIRED` significa que el elemento coincide con una familia normativa potencial, pero no demuestra cumplimiento legal.

| Elemento | Norma candidata | Estado del corpus | Resultado | Acción humana |
|---|---|---|---|---|
| `{{ global_id }}` | `{{ regulation_code }}` | `NO_VERIFICADA` | `REVIEW_REQUIRED` | Confirmar aplicabilidad |

## Preguntas que debe responder la autoridad

1. ¿El modelo y el snapshot corresponden a la versión que debe revisarse?
2. ¿La unidad y el CRS son correctos?
3. ¿El parámetro propuesto está autorizado para exportación?
4. ¿La evidencia vinculada es suficiente y vigente?
5. ¿El cambio afecta una decisión, una restricción o una obligación normativa?
6. ¿Debe solicitarse revisión especializada antes de exportar?

## Decisión de la autoridad

Seleccione exactamente una opción:

```text
[ ] APPROVE_FOR_EXPORT — autoriza una orden posterior de exportación
[ ] REJECT — no autoriza el change set
[ ] REQUEST_CHANGES — devuelve el change set para corrección
[ ] ESCALATE — requiere revisión normativa o técnica especializada
```

### Firma

| Campo | Valor |
|---|---|
| Autoridad humana | `{{ reviewer }}` |
| Rol | `{{ role }}` |
| Fecha UTC | `{{ reviewed_at }}` |
| Comentario obligatorio | `{{ review_comment }}` |
| HumanReview ID | `{{ human_review_id }}` |

## Condiciones de exportación posterior

La exportación solo podrá iniciar si existe una `HumanReview` aprobada, el `BIMChangeSet` sigue siendo el snapshot revisado, el hash del modelo no cambió y no existe un conflicto pendiente. La aprobación no crea una `Decision` de proyecto ni certifica cumplimiento normativo.

## Registro técnico

```json
{
  "change_set_id": "{{ change_set_id }}",
  "mode": "PREVIEW",
  "applied": false,
  "human_review_required": true,
  "decision_created": false,
  "export_authorized": "{{ export_authorized }}"
}
```
