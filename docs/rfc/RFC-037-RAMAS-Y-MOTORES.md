# RFC-037 — Mapa de ramas y motores a absorber

**Documento asociado:** `RFC-037-MULTI-ENGINE-ABSORPTION-DOCTRINE.md`
**Estado:** FUNDACIONAL
**Regla:** cada motor es maestro temporal; ninguno es dependencia permanente de producción.

## 1. Mapa global

| Rama | Maestros temporales | Estado | Próximo entregable |
|---|---|---|---|
| Dibujo arquitectónico | IfcOpenShell Draw, FreeCAD TechDraw, BlenderBIM/Bonsai, ezdxf, LibreCAD | Fase 1 iniciada; solo IfcOpenShell disponible | Ground truth multi-maestro y reglas de dibujo |
| Estructuras | OpenSees, PyNite, anastruct, Ftool, SAP2000 API, ETABS API | No iniciado | Matriz de análisis estructural |
| Hidráulica | EPANET, SWMM, HEC-RAS | No iniciado | Ground truth de redes y cauces |
| Dinámica de fluidos | OpenFOAM, SU2, FEniCS, FiPy | No iniciado | Casos comparables de flujo |
| Geología / geotecnia | GemPy, PyGSLIB, Plaxis API, GeoStudio | No iniciado | Modelos de subsuelo y validación |
| Energía / building physics | EnergyPlus, OpenStudio, Radiance, Ladybug Tools, TRNSYS | No iniciado | Casos de energía, luz y confort |
| Acústica | Pyroomacoustics, I-Simpa | No iniciado | Casos de reverberación y transmisión |
| Monte Carlo / simulación | SALib, PyMC, OpenTURNS, Chaospy, scipy.stats | No iniciado | Suite de incertidumbre y sensibilidad |
| Optimización | OR-Tools, Pyomo, PuLP, CVXPY, pymoo, DEAP | No iniciado | Problemas benchmark y síntesis |
| GIS | GDAL, Shapely, GeoPandas, PostGIS, QGIS API | No iniciado | Casos geoespaciales reproducibles |
| BIM | IfcOpenShell, xBIM, web-ifc | Parcialmente iniciado | Lectura, normalización y validación BIM |
| LCA / carbono | Brightway2, OpenLCA | No iniciado | Inventarios y comparativa ambiental |
| Costos / presupuestos | Sin maestro dominante; oportunidad de motor propio | No iniciado | Modelo nativo de costos |
| Programación arquitectónica | Sin maestro dominante; oportunidad de motor propio | No iniciado | Motor de programa y requisitos |
| Análisis de sitio | Capacidades parciales de GIS; oportunidad de síntesis propia | No iniciado | Motor de diagnóstico de sitio |

## 2. Reglas de selección

No se instalará ni estudiará un motor únicamente por aparecer en esta tabla. Antes de cada rama se debe verificar disponibilidad, licencia, compatibilidad con el entorno y existencia de un fixture común.

Un motor no disponible se registra como `INSUFFICIENT_DATA`. No se le asigna una evaluación inventada ni se declara que aporta una regla hasta probarlo.

## 3. Orden sugerido de absorción

La secuencia recomendada, después de cerrar el aprendizaje de dibujo, es:

1. Estructuras.
2. Monte Carlo y simulación.
3. Optimización.
4. Energía y building physics.
5. GIS.
6. Hidráulica.
7. Dinámica de fluidos.
8. Geología y geotecnia.
9. Acústica.
10. LCA y carbono.
11. Costos.
12. Programación arquitectónica.

No se deben iniciar más de dos ramas en paralelo. Cada rama debe completar disponibilidad, ground truth, extracción, síntesis y graduación antes de abrir una tercera.

## 4. Entornos por rama

Cada rama debe conservar sus maestros y resultados en un namespace separado:

```text
/DRAWING
/STRUCTURES
/HYDRAULICS
/CFD
/GEOTECHNICS
/ENERGY
/ACOUSTICS
/SIMULATION
/OPTIMIZATION
/GIS
/BIM
/LCA
/COSTS
/PROGRAMMING
/SITE
```

La síntesis propia puede compartir utilidades deterministas comunes, pero no debe importar el motor externo de otra rama como dependencia de producción.

## 5. Criterio global de graduación

La absorción global solo puede declararse completa cuando cada rama activa tenga:

- Inventario de maestros.
- Ground truth reproducible.
- Reglas con fuente.
- Motor propio o decisión explícita de oportunidad de motor propio.
- Tests de independencia.
- Comparación y revisión humana.
- Registro de limitaciones y `INSUFFICIENT_DATA`.

## 6. Estado operativo actual

La única rama activa es Dibujo arquitectónico. Su Fase 1 está documentada, pero bloqueada para graduación porque únicamente IfcOpenShell Draw está disponible y el IFC de prueba no corresponde al fixture profesional A-01.

No se inicia Estructuras ni ninguna otra rama hasta que el Product Owner autorice continuar después del reporte de Fase 0.
