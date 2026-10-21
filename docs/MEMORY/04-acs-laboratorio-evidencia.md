# Auditoría 4 — ACS, laboratorio y evidencia experimental

**Perspectiva:** aprendizaje técnico, aislamiento, reproducibilidad y promoción de capacidades.

## 1. Papel declarado de ACS

La arquitectura de `arki-acs` describe ACS (ARKI Capability Sandbox) como un laboratorio persistente para evaluar capacidades externas antes de decidir si pasan a ARKI. Define cuatro modos:
- **KNOW:** inspección estática, sin ejecución.
- **RUN:** ejecución aislada en un worker desechable.
- **UNDERSTAND:** caracterización de comportamiento.
- **EVOLVE:** seguimiento de versiones y análisis de diferencias.

El documento declara expresamente que ACS no es D-2, no es AGK, no puede modificar geometría canónica y no promueve código experimental automáticamente.

Fuente: [ACS Architecture](https://github.com/YvanCastilloQuezada/arki-acs/blob/main/docs/ARCHITECTURE.md).

## 2. Límite de seguridad explícito

El modelo de seguridad dice:
- nivel 0, proceso separado: IMPLEMENTED;
- nivel 1, contenedor: NOT IMPLEMENTED;
- nivel 2, microVM: NOT IMPLEMENTED/UNKNOWN;
- filesystem y red con política deny-by-default como intención, pero aislamiento completo de filesystem/red se declara limitación explícita sin contenedor;
- timeout y límites de CPU/RAM cuando el sistema operativo lo permite.

Fuente: [ACS Security Model](https://github.com/YvanCastilloQuezada/arki-acs/blob/main/docs/SECURITY_MODEL.md).

Por ello, no se debe describir ACS como sandbox de seguridad fuerte ni ejecutar artefactos no confiables basándose solo en el nombre “sandbox”. La madurez de aislamiento debe aparecer como dato visible en MEMORY.

## 3. Relación con REVIVIR

REVIVIR genera déficits y propuestas a partir de observaciones; para evaluar una propuesta puede exigir un recibo firmado y evidencia. ACS puede ser el lugar para caracterizar una capacidad experimental, pero la auditoría no demuestra todavía un contrato directo y seguro entre ambos.

Una integración futura debería vincular como mínimo:
- identificador estable de la propuesta;
- SHA exacto de código y artefacto;
- versión del worker/runtime y perfil de aislamiento;
- corpus de prueba y versión;
- comandos y parámetros;
- resultado bruto y resumen derivado;
- recibo firmado/fingerprint cuando corresponda;
- estado epistemológico (observado, reproducido, no reproducido, desconocido);
- aprobación humana antes de promoción.

## 4. No confundir evidencia con autoridad

Un experimento exitoso en ACS solo demuestra lo que el experimento cubre en su entorno. No demuestra por sí mismo que la capacidad sea segura, general, estable, apta para producción o autorizada para modificar Core. ACS debe producir evidencia con límites declarados; Core o la autoridad humana decide la promoción conforme al contrato aplicable.

## 5. Pendientes

- Leer y contrastar `docs/DATA_MODEL.md`, `docs/LIMITATIONS.md`, `docs/REPRODUCTION.md` y las pruebas reales.
- Determinar cómo se identifica y conserva cada artefacto y resultado.
- Verificar si la ejecución actual cumple los límites documentados en todos los sistemas operativos.
- Diseñar un formato de recibo compartido con REVIVIR, sin inventar un nuevo formato antes de revisar el existente.
- Comprobar si los recibos pueden ser validados por una autoridad fuera de ACS.

**Estado:** límites documentales localizados; ejecución y reproducibilidad no verificadas en esta auditoría.
