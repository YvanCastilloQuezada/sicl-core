# VSM — Revisión semanal de maestros (2026-09-26)

**Modo:** detección y reporte únicamente; no se actualizan paquetes, reglas ni runtime.

**Maestros registrados:** 52

## Resumen

| Clasificación | Cantidad |
|---|---:|
| Cambios detectados | 0 |
| Sin cambios | 1 |
| Candidatos a línea base | 35 |
| No consultables | 4 |
| Sin fuente configurada | 9 |
| Observados sin release | 3 |
| Potencialmente obsoletos | 0 |

## Maestros con nueva versión o candidato a línea base

| Maestro | Rama | Línea base | Observado | Acción VSM |
|---|---|---|---|---|
| FreeCAD + TechDraw | dibujo, estructuras | — | 1.1.3 | **No adoptar automáticamente; evaluar ground truth** |
| BlenderBIM / Bonsai | dibujo, bim | — | v3.4.0, bonsai-0.9.0-alpha2609250925 | **No adoptar automáticamente; evaluar ground truth** |
| ezdxf | dibujo | — | 1.4.4 | **No adoptar automáticamente; evaluar ground truth** |
| LibreCAD | dibujo | — | v2.2.1.5 | **No adoptar automáticamente; evaluar ground truth** |
| OpenSees | estructuras | — | 3.8.0.0, v3.8.0 | **No adoptar automáticamente; evaluar ground truth** |
| PyNite | estructuras | — | 3.2.0 | **No adoptar automáticamente; evaluar ground truth** |
| anastruct | estructuras | — | 1.7.0, release-v1.7.0 | **No adoptar automáticamente; evaluar ground truth** |
| SWMM | hidraulica | — | v5.2.4 | **No adoptar automáticamente; evaluar ground truth** |
| SU2 | dinamica_fluidos | — | v8.5.0 | **No adoptar automáticamente; evaluar ground truth** |
| FEniCS | dinamica_fluidos | — | v0.11.0.post0 | **No adoptar automáticamente; evaluar ground truth** |
| FiPy | dinamica_fluidos | — | 4.0.3, 4.0.3 | **No adoptar automáticamente; evaluar ground truth** |
| GemPy | geologia | — | 2026.0.3, v2026.1.0a3 | **No adoptar automáticamente; evaluar ground truth** |
| EnergyPlus | energia | — | v26.1.0 | **No adoptar automáticamente; evaluar ground truth** |
| OpenStudio | energia | — | v3.11.0 | **No adoptar automáticamente; evaluar ground truth** |
| Radiance | energia | — | 5.2 | **No adoptar automáticamente; evaluar ground truth** |
| Ladybug Tools | energia | — | 0.44.62, v1.10.56 | **No adoptar automáticamente; evaluar ground truth** |
| Pyroomacoustics | acustica | — | 0.10.1, v0.10.1 | **No adoptar automáticamente; evaluar ground truth** |
| SALib | simulacion | — | 1.6.0, v1.5.2 | **No adoptar automáticamente; evaluar ground truth** |
| PyMC | simulacion | — | 6.3.2, v6.3.2 | **No adoptar automáticamente; evaluar ground truth** |
| OpenTURNS | simulacion | — | 1.27.post1, v1.26 | **No adoptar automáticamente; evaluar ground truth** |
| Chaospy | simulacion | — | 4.3.21 | **No adoptar automáticamente; evaluar ground truth** |
| scipy.stats | simulacion | — | 1.18.1 | **No adoptar automáticamente; evaluar ground truth** |
| OR-Tools | optimizacion | — | 9.15.6755, v9.15 | **No adoptar automáticamente; evaluar ground truth** |
| Pyomo | optimizacion | — | 6.10.1, 6.10.1 | **No adoptar automáticamente; evaluar ground truth** |
| PuLP | optimizacion | — | 4.0.0, 4.0.0 | **No adoptar automáticamente; evaluar ground truth** |
| CVXPY | optimizacion | — | 1.9.3, v1.9.3 | **No adoptar automáticamente; evaluar ground truth** |
| pymoo | optimizacion | — | 0.6.2, 0.6.2 | **No adoptar automáticamente; evaluar ground truth** |
| DEAP | optimizacion | — | 1.4.4 | **No adoptar automáticamente; evaluar ground truth** |
| GDAL | gis | — | 3.13.3, v3.13.3 | **No adoptar automáticamente; evaluar ground truth** |
| Shapely | gis | — | 2.1.2, 2.1.2 | **No adoptar automáticamente; evaluar ground truth** |
| GeoPandas | gis | — | 1.1.4, v1.1.4 | **No adoptar automáticamente; evaluar ground truth** |
| QGIS API | gis | — | final-3_44_15 | **No adoptar automáticamente; evaluar ground truth** |
| xBIM | bim | — | XbimEssentials_master_6.0.517 | **No adoptar automáticamente; evaluar ground truth** |
| web-ifc | bim | — | 0.0.78, 0.78 | **No adoptar automáticamente; evaluar ground truth** |
| Brightway2 | lca | — | 4.7 | **No adoptar automáticamente; evaluar ground truth** |

## Maestros sin cambios

- **IfcOpenShell** (dibujo, bim): La versión observada confirma la línea base 0.8.5. Otras fuentes publican tags no equivalentes: bonsai-0.9.0-alpha2609250925; revisar manualmente.

## Maestros no consultables o sin fuente

- **Ftool**: `unavailable` — No se pudo consultar una fuente pública.
- **PyGSLIB**: `unavailable` — No se pudo consultar una fuente pública.
- **I-Simpa**: `unavailable` — No se pudo consultar una fuente pública.
- **OpenLCA**: `unavailable` — No se pudo consultar una fuente pública.
- **SAP2000 API**: `not_configured` — No hay fuente pública de versión configurada.
- **ETABS API**: `not_configured` — No hay fuente pública de versión configurada.
- **HEC-RAS**: `not_configured` — No hay fuente pública de versión configurada.
- **Plaxis API**: `not_configured` — No hay fuente pública de versión configurada.
- **GeoStudio**: `not_configured` — No hay fuente pública de versión configurada.
- **TRNSYS**: `not_configured` — No hay fuente pública de versión configurada.
- **Motor propio de costos ARKI**: `not_configured` — No hay fuente pública de versión configurada.
- **Motor propio de programación ARKI**: `not_configured` — No hay fuente pública de versión configurada.
- **Motor propio de análisis de sitio ARKI**: `not_configured` — No hay fuente pública de versión configurada.
- **EPANET**: `observed_without_release` — Fuente consultable, pero sin release/version formal; no se adopta nada.
- **OpenFOAM**: `observed_without_release` — Fuente consultable, pero sin release/version formal; no se adopta nada.
- **PostGIS**: `observed_without_release` — Fuente consultable, pero sin release/version formal; no se adopta nada.

## Maestros nuevos detectados

No se realizó una búsqueda automática de tendencias como absorción. Las propuestas nuevas requieren una revisión de rama y fixture antes de agregarse al registro.

## Obsolescencia

La detección de obsolescencia se basa en la fecha de release observada; no se marcó ningún maestro como obsoleto sin evidencia suficiente.

## Evidencia por maestro

| ID | Estado registrado | Clasificación | Fuentes consultadas | Evidencia |
|---|---|---|---|---|
| `ifcopenshell` | `absorbido` | `unchanged` | https://pypi.org/project/ifcopenshell/; https://github.com/IfcOpenShell/IfcOpenShell/releases/tag/bonsai-0.9.0-alpha2609250925 | La versión observada confirma la línea base 0.8.5. Otras fuentes publican tags no equivalentes: bonsai-0.9.0-alpha2609250925; revisar manualmente. |
| `freecad` | `no_instalado` | `baseline_candidate` | https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.3; pypi | Versión disponible 1.1.3; el registro aún no tiene línea base. |
| `blenderbim` | `no_instalado` | `baseline_candidate` | https://github.com/ThatOpen/engine_components/releases/tag/v3.4.0; https://github.com/IfcOpenShell/IfcOpenShell/releases/tag/bonsai-0.9.0-alpha2609250925 | Versión disponible v3.4.0, bonsai-0.9.0-alpha2609250925; el registro aún no tiene línea base. |
| `ezdxf` | `no_instalado` | `baseline_candidate` | https://pypi.org/project/ezdxf/; https://github.com/mozman/ezdxf | Versión disponible 1.4.4; el registro aún no tiene línea base. |
| `librecad` | `no_instalado` | `baseline_candidate` | https://github.com/LibreCAD/LibreCAD/releases/tag/v2.2.1.5 | Versión disponible v2.2.1.5; el registro aún no tiene línea base. |
| `opensees` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/openseespy/; https://github.com/OpenSees/OpenSees/releases/tag/v3.8.0 | Versión disponible 3.8.0.0, v3.8.0; el registro aún no tiene línea base. |
| `pynite` | `no_iniciado` | `baseline_candidate` | pypi; https://github.com/JWock82/Pynite/releases/tag/3.2.0 | Versión disponible 3.2.0; el registro aún no tiene línea base. |
| `anastruct` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/anastruct/; https://github.com/anastruct/anaStruct/releases/tag/release-v1.7.0 | Versión disponible 1.7.0, release-v1.7.0; el registro aún no tiene línea base. |
| `ftool` | `no_iniciado` | `unavailable` | github | No se pudo consultar una fuente pública. |
| `sap2000_api` | `no_iniciado` | `not_configured` | — | No hay fuente pública de versión configurada. |
| `etabs_api` | `no_iniciado` | `not_configured` | — | No hay fuente pública de versión configurada. |
| `epanet` | `no_iniciado` | `observed_without_release` | https://github.com/USEPA/EPANET | Fuente consultable, pero sin release/version formal; no se adopta nada. |
| `swmm` | `no_iniciado` | `baseline_candidate` | https://github.com/USEPA/Stormwater-Management-Model/releases/tag/v5.2.4 | Versión disponible v5.2.4; el registro aún no tiene línea base. |
| `hec_ras` | `no_iniciado` | `not_configured` | — | No hay fuente pública de versión configurada. |
| `openfoam` | `no_iniciado` | `observed_without_release` | https://github.com/OpenFOAM/OpenFOAM-dev | Fuente consultable, pero sin release/version formal; no se adopta nada. |
| `su2` | `no_iniciado` | `baseline_candidate` | https://github.com/su2code/SU2/releases/tag/v8.5.0 | Versión disponible v8.5.0; el registro aún no tiene línea base. |
| `fenics` | `no_iniciado` | `baseline_candidate` | pypi; https://github.com/FEniCS/dolfinx/releases/tag/v0.11.0.post0 | Versión disponible v0.11.0.post0; el registro aún no tiene línea base. |
| `fipy` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/FiPy/; https://github.com/usnistgov/fipy/releases/tag/4.0.3 | Versión disponible 4.0.3, 4.0.3; el registro aún no tiene línea base. |
| `gempy` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/gempy/; https://github.com/gempy-project/gempy/releases/tag/v2026.1.0a3 | Versión disponible 2026.0.3, v2026.1.0a3; el registro aún no tiene línea base. |
| `pygslib` | `no_iniciado` | `unavailable` | pypi; github | No se pudo consultar una fuente pública. |
| `plaxis_api` | `no_iniciado` | `not_configured` | — | No hay fuente pública de versión configurada. |
| `geostudio` | `no_iniciado` | `not_configured` | — | No hay fuente pública de versión configurada. |
| `energyplus` | `no_iniciado` | `baseline_candidate` | https://github.com/NatLabRockies/EnergyPlus/releases/tag/v26.1.0 | Versión disponible v26.1.0; el registro aún no tiene línea base. |
| `openstudio` | `no_iniciado` | `baseline_candidate` | https://github.com/NatLabRockies/OpenStudio/releases/tag/v3.11.0 | Versión disponible v3.11.0; el registro aún no tiene línea base. |
| `radiance` | `no_iniciado` | `baseline_candidate` | https://github.com/NatLabRockies/Radiance/releases/tag/5.2 | Versión disponible 5.2; el registro aún no tiene línea base. |
| `ladybug_tools` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/ladybug-core/; https://github.com/ladybug-tools/lbt-grasshopper/releases/tag/v1.10.56 | Versión disponible 0.44.62, v1.10.56; el registro aún no tiene línea base. |
| `trnsys` | `no_iniciado` | `not_configured` | — | No hay fuente pública de versión configurada. |
| `pyroomacoustics` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/pyroomacoustics/; https://github.com/LCAV/pyroomacoustics/releases/tag/v0.10.1 | Versión disponible 0.10.1, v0.10.1; el registro aún no tiene línea base. |
| `isimpa` | `no_iniciado` | `unavailable` | github | No se pudo consultar una fuente pública. |
| `salib` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/SALib/; https://github.com/SALib/SALib/releases/tag/v1.5.2 | Versión disponible 1.6.0, v1.5.2; el registro aún no tiene línea base. |
| `pymc` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/pymc/; https://github.com/pymc-devs/pymc/releases/tag/v6.3.2 | Versión disponible 6.3.2, v6.3.2; el registro aún no tiene línea base. |
| `openturns` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/openturns/; https://github.com/openturns/openturns/releases/tag/v1.26 | Versión disponible 1.27.post1, v1.26; el registro aún no tiene línea base. |
| `chaospy` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/chaospy/; github | Versión disponible 4.3.21; el registro aún no tiene línea base. |
| `scipy_stats` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/scipy/ | Versión disponible 1.18.1; el registro aún no tiene línea base. |
| `ortools` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/ortools/; https://github.com/google/or-tools/releases/tag/v9.15 | Versión disponible 9.15.6755, v9.15; el registro aún no tiene línea base. |
| `pyomo` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/pyomo/; https://github.com/Pyomo/pyomo/releases/tag/6.10.1 | Versión disponible 6.10.1, 6.10.1; el registro aún no tiene línea base. |
| `pulp` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/PuLP/; https://github.com/coin-or/pulp/releases/tag/4.0.0 | Versión disponible 4.0.0, 4.0.0; el registro aún no tiene línea base. |
| `cvxpy` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/cvxpy/; https://github.com/cvxpy/cvxpy/releases/tag/v1.9.3 | Versión disponible 1.9.3, v1.9.3; el registro aún no tiene línea base. |
| `pymoo` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/pymoo/; https://github.com/anyoptimization/pymoo/releases/tag/0.6.2 | Versión disponible 0.6.2, 0.6.2; el registro aún no tiene línea base. |
| `deap` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/deap/; https://github.com/DEAP/deap | Versión disponible 1.4.4; el registro aún no tiene línea base. |
| `gdal` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/GDAL/; https://github.com/OSGeo/gdal/releases/tag/v3.13.3 | Versión disponible 3.13.3, v3.13.3; el registro aún no tiene línea base. |
| `shapely` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/shapely/; https://github.com/shapely/shapely/releases/tag/2.1.2 | Versión disponible 2.1.2, 2.1.2; el registro aún no tiene línea base. |
| `geopandas` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/geopandas/; https://github.com/geopandas/geopandas/releases/tag/v1.1.4 | Versión disponible 1.1.4, v1.1.4; el registro aún no tiene línea base. |
| `postgis` | `no_iniciado` | `observed_without_release` | https://github.com/postgis/postgis | Fuente consultable, pero sin release/version formal; no se adopta nada. |
| `qgis_api` | `no_iniciado` | `baseline_candidate` | https://github.com/qgis/QGIS/releases/tag/final-3_44_15 | Versión disponible final-3_44_15; el registro aún no tiene línea base. |
| `xbim` | `no_iniciado` | `baseline_candidate` | https://github.com/xBimTeam/XbimEssentials/releases/tag/XbimEssentials_master_6.0.517 | Versión disponible XbimEssentials_master_6.0.517; el registro aún no tiene línea base. |
| `web_ifc` | `no_iniciado` | `baseline_candidate` | https://www.npmjs.com/package/web-ifc; https://github.com/ThatOpen/engine_web-ifc/releases/tag/0.78 | Versión disponible 0.0.78, 0.78; el registro aún no tiene línea base. |
| `brightway2` | `no_iniciado` | `baseline_candidate` | https://pypi.org/project/bw2data/; https://github.com/brightway-lca/brightway2-data | Versión disponible 4.7; el registro aún no tiene línea base. |
| `openlca` | `no_iniciado` | `unavailable` | github | No se pudo consultar una fuente pública. |
| `costos_arki` | `oportunidad_propia` | `not_configured` | — | No hay fuente pública de versión configurada. |
| `programacion_arki` | `oportunidad_propia` | `not_configured` | — | No hay fuente pública de versión configurada. |
| `sitio_arki` | `oportunidad_propia` | `not_configured` | — | No hay fuente pública de versión configurada. |

## Invariantes

```text
AUTO_ABSORPTION = FORBIDDEN
AUTO_UPDATE = FORBIDDEN
CORE_CHANGED = NO
DECISION_CREATED = NO
NAMESPACE_MIXED = NO
```
