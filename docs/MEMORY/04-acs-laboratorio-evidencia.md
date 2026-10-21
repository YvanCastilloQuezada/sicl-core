# Auditoría 4 — ACS, laboratorio y evidencia experimental

**Perspectiva:** aprendizaje técnico, aislamiento, reproducibilidad y promoción de capacidades.

## 1. Papel declarado de ACS

La arquitectura de `arki-acs` describe ACS (ARKI Capability Sandbox) como un laboratorio persistente para evaluar capacidades externas antes de decidir si pasan a ARKI. Define cuatro modos:
- **KNOW:** inspección estática, sin ejecución.
- **RUN:** ejecución en un worker desechable.
- **UNDERSTAND:** caracterización de comportamiento.
- **EVOLVE:** seguimiento de versiones y análisis de diferencias.

El documento declara expresamente que ACS no es D-2, no es AGK, no puede modificar geometría canónica y no promueve código experimental automáticamente.

Fuente: [ACS Architecture](https://github.com/YvanCastilloQuezada/arki-acs/blob/main/docs/ARCHITECTURE.md).

## 2. Límites de seguridad y madurez real documentada

El modelo de seguridad declara proceso separado como nivel 0 implementado; contenedor como nivel 1 no implementado; microVM como nivel 2 no implementado/UNKNOWN. La documentación de limitaciones es aún más explícita:
- Aislamiento de contenedor y microVM: no implementado.
- Denegación efectiva de red y filesystem: no garantizada sin contenedor.
- Límites CPU/RAM: definidos en `ResourceLimits.cs`, pero no aplicados por `IsolatedWorker`.
- Algunos inspectores y operaciones CRUD/CLI figuran como implementados pero aún no verificados.
- Parsing de Python basado en regex simplificado; parsing nativo incompleto.
- Equivalencia semántica entre capacidades y ciertos efectos laterales permanecen UNKNOWN.

Fuentes:
- [ACS Security Model](https://github.com/YvanCastilloQuezada/arki-acs/blob/main/docs/SECURITY_MODEL.md)
- [ACS Limitations](https://github.com/YvanCastilloQuezada/arki-acs/blob/main/docs/LIMITATIONS.md)
- [ACS Data Model](https://github.com/YvanCastilloQuezada/arki-acs/blob/main/docs/DATA_MODEL.md)

**Implicación:** no se debe describir ACS como sandbox de seguridad fuerte ni ejecutar artefactos no confiables basándose solo en el nombre “sandbox”. MEMORY debe exponer el nivel de aislamiento y las limitaciones verificadas, sin ocultarlas.

## 3. Evidencia y disposición son cosas distintas

El modelo de datos separa estados de evidencia (`DECLARED`, `INFERRED`, `OBSERVED`, `VERIFIED`, `UNKNOWN`) de la disposición recomendada (`OWN`, `BACKEND`, `DELTA`, `ORACLE`, `TEST_CORPUS`, `REFERENCE`, `FUTURE`, `REDUNDANT`, `NOT_RELEVANT`, `INCOMPATIBLE`, `UNSAFE`, `LEGAL_RESTRICTION`, `BROKEN`, `SUPERSEDED`, `UNKNOWN`). Esta separación es valiosa para MEMORY: describir lo que se sabe no es lo mismo que decidir qué hacer con ello.

## 4. Relación con REVIVIR

REVIVIR genera déficits y propuestas a partir de observaciones; para evaluar una propuesta puede exigir un recibo firmado y evidencia. ACS podría caracterizar una capacidad experimental, pero no se ha demostrado un contrato directo y seguro entre ambos.

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

## 5. Reproducción

`docs/REPRODUCTION.md` prescribe `.NET 8 SDK`, `dotnet restore`, `dotnet build` y `dotnet test`. La aceptación de ProtoGeometry depende de artefactos externos; si no están disponibles, el test falla con `INPUT_NOT_AVAILABLE`. Estas instrucciones son un protocolo documental; no se ejecutaron durante esta auditoría.

Fuente: [ACS Reproduction](https://github.com/YvanCastilloQuezada/arki-acs/blob/main/docs/REPRODUCTION.md).

## 6. Conclusión y pendientes

Un experimento exitoso en ACS solo demuestra lo que cubre en su entorno. No demuestra por sí mismo seguridad, generalidad, estabilidad, aptitud para producción o autorización para modificar Core. ACS debe producir evidencia con límites declarados; Core o la autoridad humana decide la promoción.

Pendientes:
- inspeccionar las pruebas reales y confirmar qué partes marcadas `IMPLEMENTED_AND_TESTED` están cubiertas por evidencia reproducible;
- determinar cómo se identifican y conservan artefactos y resultados;
- definir el contrato de recibo compartido con REVIVIR tras revisar el formato existente;
- comprobar si los recibos pueden validarse fuera de ACS.

**Estado:** límites documentales localizados; ejecución y reproducibilidad no verificadas en esta auditoría.
