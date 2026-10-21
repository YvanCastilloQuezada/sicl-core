# DAM-001 — ADN, Asesor y Profesor/Examinador

**Estado:** FOUNDATION IMPLEMENTED  
**Base doctrinal:** RFC-037 / RFC-037.1  
**Ámbito inicial:** Dibujo/Representación

## Regla constitucional

```text
MASTER != ADVISOR != EXAMINER != NATIVE_ENGINE
```

Los motores externos son maestros temporales y productores de evidencia. No forman parte del runtime final. El conocimiento que ARKI internaliza debe tener fuente, alcance y evidencia. El asesor interpreta y orienta la especialidad. El profesor/examinador evalúa sin enseñar durante el examen. El motor nativo ejecuta únicamente conocimiento graduado.

## Ciclo

```text
MAESTROS
  -> LABORATORIO / GROUND TRUTH
  -> EXTRACCION CON FUENTE
  -> CONOCIMIENTO ARKI
  -> MOTOR NATIVO / ADN
  -> ASESOR
  -> EXAMINADOR
  -> GRADUACION
  -> RUNTIME NATIVO
```

## Escala de graduación 0–10

| Nivel | Estado | Evidencia mínima |
|---:|---|---|
| 0 | UNKNOWN | reconoce ausencia de dominio |
| 1 | OBSERVATION | observación de maestro/fixture |
| 2 | COMPREHENSION | reglas con fuente y alcance |
| 3 | REPRODUCTION | reproduce casos conocidos |
| 4 | GENERALIZATION | resuelve casos no memorizados |
| 5 | ADVERSARIAL | resiste casos límite y datos incompletos |
| 6 | COMPARATIVE | comparación ciega contra maestros |
| 7 | RUNTIME_INDEPENDENCE | cero maestro externo en runtime |
| 8 | ARCHITECTURAL_INTEGRATION | integración trazable con arquitectura ARKI |
| 9 | PROFESSIONAL_EXAM | examen profesional independiente |
| 10 | GRADUATED_DNA | examen + revisión humana + independencia |

## Autoridades

- **Master:** evidencia de aprendizaje; nunca autoridad arquitectónica.
- **Advisor:** interpreta la disciplina, detecta límites y solicita evidencia.
- **Examiner:** construye y califica exámenes; no modifica el resultado para hacerlo pasar.
- **Native engine:** ejecuta capacidad ARKI; no se autogradúa.
- **Human authority:** conserva la aprobación final requerida por RFC-037.

## Fail-closed

No hay graduación nivel 10 si falta examen, revisión humana o existe una dependencia de maestro externo en runtime. Una regla sin evidencia es rechazada como `KNOWLEDGE_WITHOUT_SOURCE`.

## Primera escuela

Dibujo/Representación es la primera rama piloto porque ya dispone de fixture profesional, evidencia IfcOpenShell Draw, ARKI-DRAW, RFC-030 y ARE. Su estado histórico sigue sin graduar hasta completar los exámenes y criterios DAM; este foundation no altera ese hecho.

## Límites

Este bloque no instala FreeCAD, Bonsai, ezdxf ni LibreCAD; no inventa resultados de maestros no probados; no modifica D2; no crea Decisions; no promueve automáticamente conocimiento; no convierte ningún maestro en dependencia de producción.
