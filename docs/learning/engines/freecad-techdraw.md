# Maestro temporal — FreeCAD TechDraw

**Estado:** NO DISPONIBLE EN EL ENTORNO ACTUAL

## Inventario

- Import `FreeCAD`: no disponible.
- Ejecutable `FreeCAD`: no encontrado.
- Prueba de importación: `ModuleNotFoundError`.

## Consecuencia

No se ejecutó una prueba geométrica con FreeCAD TechDraw en esta Fase 1. Esto no se interpreta como fallo del motor; es una limitación de disponibilidad del entorno.

## Conocimiento esperado a incorporar posteriormente

Cuando el motor esté disponible, ARKI debe comparar:

- Proyección ortográfica.
- Vistas TechDraw.
- Secciones con línea de corte.
- Diferencia entre geometría visible y oculta.
- Composición SVG/PDF.
- Configuración de grosores y plantillas.

## Regla de arquitectura

FreeCAD TechDraw podrá incorporarse como maestro temporal futuro, pero nunca como dependencia obligatoria del runtime de ARKI.
