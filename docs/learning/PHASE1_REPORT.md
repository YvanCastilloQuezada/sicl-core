# ARKI — Reporte de Fase 1: estudio comparativo multi-maestro

**Fecha:** 26 de septiembre de 2026
**Estado:** BLOQUEADA PARA GRADUACIÓN — estudio inicial documentado; solo un maestro disponible

## 1. Maestros definidos por la orden

| Maestro | Estado | Prueba |
|---|---|---|
| IfcOpenShell Draw 0.8.5 | Disponible y probado | SVG vectorial generado |
| FreeCAD + TechDraw | No disponible | No instalado |
| BlenderBIM / Bonsai | No disponible | No instalado |
| ezdxf | No disponible | Módulo no instalado |
| LibreCAD | No disponible | Ejecutable no encontrado |

Los motores no disponibles se registran como `INSUFFICIENT_DATA`. No se inventan evaluaciones sobre ellos.

## 2. Fixture analizado

Archivo:

```text
docs/reference/PROY_FERNANDEZ_ROJAS.pdf
```

Página analizada: 2, lámina A-01.
Formato: A3 vertical.
Páginas totales: 12.
SHA-256:

```text
3867523efba38be10c1cf3703c5cfbbda628a80e0e29c620a8e47c1a6e01815d
```

Imagen archivada:

```text
docs/learning/fixtures/PROY_FERNANDEZ_ROJAS_A01.png
```

La lámina contiene cuatro plantas coordinadas, ejes, cotas parciales y totales, muros cerrados, puertas, ventanas, escaleras, mobiliario, vegetación, NPT y cajetín profesional.

## 3. Prueba del maestro disponible

Entrada:

```text
docs/reference/RFC030_OUTPUT/EDIFICIO-YVAN-TRUJILLO-01.ifc
```

Salida de aprendizaje:

```text
docs/learning/engines/ifcopenshell_draw_probe.svg
```

Resultados:

| Medición | Resultado |
|---|---:|
| Entidades IFC leídas | 1.094 |
| Tamaño SVG | 62.135 bytes |
| Rutas SVG | 146 |
| `P-1` detectado | Sí |
| `V-1` detectado | Sí |
| `NPT` generado | No |
| `ESCALERA` generada | No |

SHA-256 del SVG:

```text
9eb1c2ed6fb82d36643afa7c8970f0c6ac75915156c0a66f367eb2fada28ae0c
```

## 4. Pruebas iniciales

| Prueba | Resultado |
|---|---|
| Importar IfcOpenShell | PASS |
| Importar `ifcopenshell.draw` | PASS |
| Abrir IFC sintético | PASS |
| Leer 1.094 entidades | PASS |
| Generar SVG vectorial | PASS |
| Obtener geometría proyectada | PASS |
| FreeCAD disponible | FAIL — no instalado |
| BlenderBIM disponible | FAIL — no instalado |
| ezdxf disponible | FAIL — no instalado |
| LibreCAD disponible | FAIL — no instalado |
| Reproducir A-01 indistinguiblemente | FAIL — IFC diferente |
| Reproducir con al menos tres maestros | FAIL — solo uno disponible |

## 5. Reglas extraídas de la observación

1. La documentación profesional empieza con geometría 3D, no con elementos independientes.
2. La proyección debe ejecutarse antes de aplicar el estilo.
3. El corte, la oclusión y la profundidad son operaciones geométricas.
4. Las líneas contiguas deben unificarse y las esquinas cerrarse.
5. Las puertas, ventanas y escaleras requieren simbología compuesta.
6. Cotas, NPT, ejes y cajetín forman una capa de documentación separada.
7. Mobiliario y vegetación comunican uso y contexto.
8. El SVG vectorial es una salida adecuada para conservar líneas y curvas.
9. La ausencia de datos debe expresarse como `INSUFFICIENT_DATA`.
10. Cada maestro puede aportar una especialidad distinta; no se debe depender de uno solo.
11. Ningún maestro externo debe quedar como dependencia del runtime propio de ARKI.

## 6. Estado de graduación

La Fase 1 está **iniciada y documentada**, pero no graduada. Se probó IfcOpenShell Draw y se analizó el fixture. Los otros cuatro maestros no están disponibles y el IFC actual no corresponde a la vivienda A-01.

No se avanza a la extracción comparada ni a la síntesis del motor propio hasta disponer de al menos tres maestros operativos o hasta que el Product Owner autorice cambiar el criterio.

## 7. Invariantes

```text
CORE_CHANGED = NO
DECISION_CREATED = NO
EXTERNAL_ENGINE_RUNTIME_DEPENDENCY = NO
NAMESPACE_MIXED = NO
PHASE1_GRADUATED = NO
```
