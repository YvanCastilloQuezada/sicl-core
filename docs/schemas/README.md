# ARKI JSON Schemas — Contratos de Datos

Este directorio contiene los contratos JSON que materializan las Reglas del Pilar VIII (Compliance & Sovereignty) de LAB-000.

## Archivos

| Archivo | Regla | Propósito |
|---|---|---|
| `domain_profile.json` | Regla 41 | Clasificación dinámica de riesgo (EU AI Act) |
| `provenance_signature.json` | Regla 42 | Hash de integridad de proveniencia (sin firma criptográfica; nombre histórico) |
| `ethical_impact_assessment.json` | Regla 43 | Evaluación de Impacto Algorítmico obligatoria |

## Uso

Estos schemas son **contratos obligatorios** que:

1. El **Laboratorio** debe cumplir al generar outputs.
2. La **capa experimental de Compliance** valida para aceptar o rechazar datos; H-001–H-004 permanecen independientes.
3. **Luxa** expone al usuario final como evidencia de cumplimiento.

## Validación

Los schemas siguen JSON Schema Draft-07 y pueden validarse con:

```bash
pip install jsonschema
python -c "import jsonschema; jsonschema.Draft7Validator.check_schema(json.load(open('docs/schemas/domain_profile.json')))"
```

## Estado

EXPERIMENTAL v1.1 — 2026-09-27
Autoridad: Wilfredo Yvan Castillo Quezada
