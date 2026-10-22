# Observaciones del maestro — Fase 1

## Conclusión ejecutiva

ARKI no debe copiar la interfaz de un motor. Debe aprender los principios comunes que producen documentación profesional. La prueba disponible confirma que el punto de partida correcto es la proyección desde geometría 3D, seguida de ocultamiento, unificación y anotación.

## Observaciones del fixture PROY_FERNANDEZ_ROJAS A-01

La lámina A-01 está compuesta como una hoja arquitectónica completa, no como una colección de símbolos. Presenta cuatro vistas coordinadas: planta primer piso, planta segundo piso, planta azotea y planta techo. Todas comparten ejes, cotas y una lógica de alineación vertical.

El fixture utiliza una jerarquía visual clara. Los muros cortados dominan la lectura, las líneas vistas son más finas, las líneas ocultas se diferencian y las anotaciones se mantienen fuera de la geometría principal. Las esquinas están cerradas y los espesores de muro son legibles.

Las puertas incluyen marco, hoja y arco de apertura. Las ventanas tienen marcos y líneas paralelas. Las escaleras muestran peldaños numerados o diferenciados y dirección. El mobiliario permite entender la función de cada espacio: comedor, sala, cocina, dormitorios, baños, escritorio, cochera y terraza. La vegetación se representa mediante siluetas reconocibles.

Las cotas se distribuyen en anillos exteriores y contienen números reales. Los ejes aparecen en círculos, con letras y números. Los niveles NPT se colocan cerca de las áreas correspondientes. El cajetín contiene proyecto, ubicación, propietario, responsable, escala, fecha, título y número de lámina.

## Conocimiento que ARKI debe internalizar

### Geometría y proyección

El proyector debe comenzar con sólidos, placements y materiales. Cada vista debe ser una consulta geométrica distinta: planta, corte, elevación o techo. No se debe reutilizar una planta como sustituto de todas las vistas.

### Profundidad

Los elementos cortados requieren una línea dominante. Los elementos visibles detrás del plano de corte deben ser más finos. Los elementos ocultos deben omitirse o expresarse con línea discontinua según su función.

### Topología

Los muros deben cerrar esquinas y fusionar segmentos contiguos. El achurado debe permanecer dentro de los polígonos cortados y no invadir ambientes, cotas ni cajetín.

### Símbolos

Una puerta profesional no es solo un arco. Requiere hoja, marco y eje. Una ventana requiere marco y líneas paralelas. Una escalera requiere peldaños, dirección y tratamiento de continuidad cuando atraviesa el plano de corte.

### Composición

La lámina debe separar área de dibujo, cotas, ejes, notas, escala gráfica, norte y cajetín. La composición es parte del conocimiento arquitectónico y debe ser un módulo posterior a la proyección.

### Datos faltantes

Si el modelo no contiene mobiliario, vegetación, materiales o información suficiente, ARKI debe declarar `INSUFFICIENT_DATA` y no inventar geometría como si fuera dato BIM confirmado.

## Estado de aprendizaje

La Fase 1 queda parcialmente completada: se probó el maestro disponible y se analizó el fixture. FreeCAD y BlenderBIM no pudieron evaluarse porque no están instalados. La información sobre esos motores queda pendiente y se marca como `INSUFFICIENT_DATA`.

## Regla de graduación

No se debe avanzar a replicación autónoma hasta que ARKI tenga reglas versionadas, un proyector propio separado de los maestros y una comparación visual repetible contra el fixture.
