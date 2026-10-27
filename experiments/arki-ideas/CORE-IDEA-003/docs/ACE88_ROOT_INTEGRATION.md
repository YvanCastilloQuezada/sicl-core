# ACE88 — Integración funcional en ARKI Core

Estado: `FUNCTIONAL_APPROVED / REGRESSION_PASS / SECURITY_FREEZE_PENDING`.

## Contrato de seguridad

La promoción canónica Developer D2 requiere una prueba de autorización humana criptográficamente verificable y vinculada al proyecto, propuesta, fingerprint, actor, revisión, clave, decisión, tiempo y nonce. Se debe rechazar una promoción sin firma válida; no se autoriza un bypass.

## Evidencia local previa

- Regresión completa: PASS en ARKI-02, 14/10/2026.
- Prueba adversarial de revisión APPROVED sin firma: PASS (rechazo).
- Integridad de SQLite: OK.
- HTTP firmado, idempotencia y persistencia tras reinicio: PASS.
- Auditoría independiente: pendiente; no declarar `SECURITY_FREEZE`.

## Restricciones

- No incluir claves privadas, bases SQLite operativas ni secretos en Git.
- No promover automáticamente LAB a identidad real del propietario.
- Toda actualización debe mantener pruebas de rechazo, atomicidad, idempotencia y replay.
- La integración en rama no equivale a merge a `main` ni despliegue.
