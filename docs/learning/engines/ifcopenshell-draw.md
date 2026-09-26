# Maestro temporal — IfcOpenShell Draw

**Estado:** DISPONIBLE Y PROBADO
**Versión:** IfcOpenShell 0.8.5
**Módulo:** `ifcopenshell.draw`
**Rol:** Maestro temporal; no dependencia del runtime nativo final

## Prueba ejecutada

Entrada:

```text
docs/reference/RFC030_OUTPUT/EDIFICIO-YVAN-TRUJILLO-01.ifc
```

Configuración observada:

- Proyección automática de planta.
- Escala A3.
- Proyección de geometría IFC.
- Celdas vectoriales.
- Arcos de puertas habilitados.
- Nombres y áreas de espacios solicitados.

Salida de aprendizaje:

```text
docs/learning/engines/ifcopenshell_draw_probe.svg
```

Resultados medidos:

- Entidades IFC leídas: 1.094.
- Tamaño SVG: 62.135 bytes.
- Rutas SVG: 146.
- Etiqueta `P-1`: 1 aparición.
- Etiqueta `V-1`: 1 aparición.
- Etiqueta `NPT`: 0 apariciones.
- Etiqueta `ESCALERA`: 0 apariciones.

## Conocimiento observado

### Proyección

El motor recibe geometría IFC y produce una salida vectorial 2D. La salida no depende de coordenadas dibujadas manualmente para cada símbolo, sino de la geometría y los placements del modelo.

### Corte y oclusión

El motor dispone de parámetros para planta automática, sección automática, hidden-line rendering, proyección y eliminación de elementos excluidos. Esto confirma que el proyector nativo de ARKI debe trabajar sobre geometría 3D y no sobre listas independientes de símbolos.

### Serialización

La salida es SVG vectorial, lo que conserva líneas y curvas editables y permite aplicar una capa propia posterior de pesos, achurados y anotaciones.

## Limitaciones observadas

La salida directa no reproduce por sí sola el fixture profesional A-01 porque:

- El IFC de prueba no corresponde a la vivienda del fixture.
- Los nombres de ambientes no coinciden.
- No contiene el mobiliario específico de A-01.
- No contiene el cajetín ni la composición de cuatro plantas del fixture.
- No genera por sí solo las anotaciones NPT y nomenclaturas del fixture.

## Reglas que ARKI debe aprender

1. La geometría debe proyectarse desde el modelo 3D.
2. Los elementos deben clasificarse por profundidad y estado de corte.
3. La salida vectorial debe conservar segmentos y curvas.
4. La oclusión debe resolverse antes de aplicar estilo.
5. La composición de lámina debe estar separada del motor geométrico.
6. Las anotaciones arquitectónicas deben ser una capa propia y no confundirse con geometría BIM.

## Decisión de arquitectura

IfcOpenShell Draw se utiliza como **oráculo de aprendizaje y comparación**. El runtime final de ARKI no debe importar ni ejecutar `ifcopenshell.draw`.
