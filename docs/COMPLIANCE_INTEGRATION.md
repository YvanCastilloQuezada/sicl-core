# Compliance Integration Guide — Pilar VIII

Este documento explica cómo integrar `sicl.compliance` con ARKI sin modificar el Core congelado H-001–H-004.

## Arquitectura

`ComplianceValidator` es una capa de gobernanza independiente que valida los contratos JSON antes de que los datos pasen al Core y valida los outputs antes de su promoción a `CANONICAL`.

```text
Laboratorio → ComplianceValidator → ARKI Core H-001..H-004 → ComplianceValidator → Luxa
```

El módulo no escribe en el ledger, no modifica SQLite y no concede autoridad automática a agentes o modelos. Es experimental y no constituye certificación legal.

## Uso básico

```python
import hashlib
from pathlib import Path
from sicl.compliance import ComplianceStatus, ComplianceValidator

validator = ComplianceValidator(Path("docs/schemas"))

profile = {
    "domain_id": "bio_longevity_v1",
    "risk_tier": "HIGH",
    "hard_constraints": ["somatic_only"],
    "aia_required": True,
}
result_41 = validator.validate_domain_profile(profile)
if result_41.status != ComplianceStatus.COMPLIANT:
    raise ValueError(result_41.message)

content = "generated output"
signature = {
    "generator_id": "LLM-Bio-Gen-v3",
    "timestamp": "2026-09-28T10:00:00Z",
    "content_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
    "hash_algorithm": "SHA256_HASH",
    "domain_profile_ref": "bio_longevity_v1",
}
result_42 = validator.validate_provenance_hash(content, signature)

assessment = {
    "assessment_id": "AIA-001",
    "target_output_ref": "OUTPUT-123",
    "bias_declaration": {"known_biases": [], "mitigation_steps": []},
    "harm_assessment_score": 25,
    "authority_approval_id": "AUTH-001",
    "status": "APPROVED",
}
result_43 = validator.validate_ethical_impact_assessment("OUTPUT-123", assessment, "HIGH")
```

## Reglas

- **Regla 41:** acepta `MINIMAL`, `LIMITED` y `HIGH` según sus restricciones; bloquea `UNACCEPTABLE` y exige `aia_required=True` para `LIMITED` y `HIGH`.
- **Regla 42:** recalcula SHA-256 sobre el contenido recibido y rechaza hashes inválidos, discrepantes o algoritmos no permitidos.
- **Regla 43:** para `LIMITED` y `HIGH` exige una AIA aprobada, autoridad humana, puntuación de daño en `[0, 100]` y referencia al output correcto. Una AIA pendiente devuelve `PENDING_REVIEW`.

## Integración con el Bridge

El Bridge puede invocar el validador antes de enviar una solicitud al Core y antes de promover un resultado. La integración debe conservar autenticación, fail-closed y read-only. No se deben aceptar rutas, comandos ni funciones arbitrarias desde el request.

## Integración con el Laboratorio

El generador debe calcular el hash del contenido antes de construir `provenance_hash`. Para perfiles `LIMITED` o `HIGH`, la AIA debe existir y contar con aprobación humana antes de promover el output a `CANONICAL`.

## Verificación

```bash
PYTHONPATH=src python -c "from sicl.compliance import ComplianceValidator; print('OK: compliance module imported')"
PYTHONPATH=src python -m pytest tests/test_compliance.py -v --tb=short
```

## Estado

EXPERIMENTAL v1.1 — 2026-09-28
Autoridad: Wilfredo Yvan Castillo Quezada

> Esta capa no modifica H-001, H-002, H-003 ni H-004.
