# Matriz de aprendizaje de motores

| Motor | Disponibilidad | Prueba en esta fase | Aporte confirmado | Uso final |
|---|---|---|---|---|
| IfcOpenShell Draw 0.8.5 | Disponible | Ejecutada sobre IFC sintético | Proyección 3D→2D, hidden lines, SVG vectorial, celdas y control de planta | Maestro temporal; no runtime |
| FreeCAD TechDraw | No disponible | No ejecutable | Pendiente: TechDraw, vistas ortográficas y secciones | Maestro temporal futuro |
| BlenderBIM / BonsaiBIM | No disponible | No ejecutable | Pendiente: cámaras, BIM, materiales y documentación | Maestro temporal futuro |

## Lectura de la matriz

Cada motor aporta una parte del conocimiento. IfcOpenShell Draw ofrece la prueba actual de que el camino correcto comienza con geometría 3D, proyección y ocultamiento. FreeCAD TechDraw queda como referencia futura para vistas ortográficas y plantillas. BlenderBIM/Bonsai queda como referencia futura para cámaras, materiales y documentación BIM.

La ausencia de FreeCAD y BlenderBIM se registra como **INSUFFICIENT_DATA**, no como una regla inventada sobre su comportamiento.

## Reglas comunes que ARKI debe conservar

| Conocimiento | Razón de internalización |
|---|---|
| Proyectar desde geometría 3D | Evita diagramas de elementos independientes |
| Resolver cortes antes del estilo | Permite distinguir cortado, visto y oculto |
| Unificar segmentos | Cierra muros y elimina líneas duplicadas |
| Separar geometría de anotación | Mantiene el modelo y la lámina desacoplados |
| Emitir SVG/PDF vectorial | Conserva escala, edición y calidad de impresión |
| Aplicar estilos después de proyectar | El RuleSet embellece; no inventa geometría |
