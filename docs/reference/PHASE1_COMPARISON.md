# Fase 1 — Comparación multi-maestro

**Fecha:** 26 de septiembre de 2026
**Fixture:** `docs/reference/PROY_FERNANDEZ_ROJAS.pdf`, página 2, A-01

## Disponibilidad y evidencia

| Maestro | Estado | Evidencia de esta sesión |
|---|---|---|
| IfcOpenShell Draw 0.8.5 | Disponible y probado | `docs/learning/engines/ifcopenshell_draw_probe.svg` |
| FreeCAD + TechDraw | No disponible | Import y ejecutable ausentes |
| BlenderBIM / Bonsai | No disponible | `bpy`, Blender y Bonsai ausentes |
| ezdxf | No disponible | Módulo Python ausente |
| LibreCAD | No disponible | Ejecutables ausentes |

## Evaluación honesta

| Aspecto | IfcOpenShell Draw | FreeCAD TechDraw | BlenderBIM | ezdxf | LibreCAD |
|---|---|---|---|---|---|
| Facilidad de generación | Bueno | INSUFFICIENT_DATA | INSUFFICIENT_DATA | INSUFFICIENT_DATA | INSUFFICIENT_DATA |
| Calidad de línea | Bueno | INSUFFICIENT_DATA | INSUFFICIENT_DATA | INSUFFICIENT_DATA | INSUFFICIENT_DATA |
| Calidad de achurado | Regular | INSUFFICIENT_DATA | INSUFFICIENT_DATA | INSUFFICIENT_DATA | INSUFFICIENT_DATA |
| Calidad de cotas | Regular | INSUFFICIENT_DATA | INSUFFICIENT_DATA | INSUFFICIENT_DATA | INSUFFICIENT_DATA |
| Calidad de simbología | Regular | INSUFFICIENT_DATA | INSUFFICIENT_DATA | INSUFFICIENT_DATA | INSUFFICIENT_DATA |
| Velocidad de generación | Bueno | INSUFFICIENT_DATA | INSUFFICIENT_DATA | INSUFFICIENT_DATA | INSUFFICIENT_DATA |
| Facilidad de extensión | Bueno | INSUFFICIENT_DATA | INSUFFICIENT_DATA | INSUFFICIENT_DATA | INSUFFICIENT_DATA |
| Soporte IFC nativo | Excelente | INSUFFICIENT_DATA | INSUFFICIENT_DATA | INSUFFICIENT_DATA | INSUFFICIENT_DATA |
| Composición de página | Regular | INSUFFICIENT_DATA | INSUFFICIENT_DATA | INSUFFICIENT_DATA | INSUFFICIENT_DATA |

## Resultado de reproducción del fixture

No se pudo generar una reproducción indistinguible de A-01 con IfcOpenShell Draw porque el IFC disponible corresponde a un modelo sintético distinto de la vivienda del fixture. No se evaluaron los otros cuatro maestros porque no están disponibles.

Por lo tanto, el criterio de Fase 1 — reproducción con al menos tres maestros y un PDF indistinguible — queda **NO CUMPLIDO**.

## Conocimiento aprovechable

IfcOpenShell Draw confirma que la proyección debe partir de geometría IFC 3D y que el motor debe resolver hidden lines, celdas y serialización vectorial. Los demás aportes quedan pendientes de prueba; no se inventan resultados.
