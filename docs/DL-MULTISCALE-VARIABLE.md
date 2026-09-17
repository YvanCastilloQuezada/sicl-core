# Decision Lock — Multiscale Variable Intelligence

**Identificador:** DL-MULTISCALE-VARIABLE-01..30
**Estado:** APPROVED / DOCUMENT AND FREEZE
**Autorización de ejecución:** NO
**Fecha:** 17 de septiembre de 2026
**Arquitectura relacionada:** DL-MULTISCALE-ADAPTIVE-01..15
**Orden de implementación vigente:** S7-P0.5 — Multiscale Capability & Adaptive Workspace Foundation

## 1. Propósito y alcance

Este Decision Lock define los principios arquitectónicos para un futuro **Multiscale Variable Catalog** que cubra los once `SpatialScope` canónicos de SiMS-DeI. El documento establece límites semánticos, requisitos de trazabilidad y relaciones futuras entre variables, capacidades, datos, análisis y espacios de trabajo adaptativos.

Este documento **no autoriza implementación**. No crea el catálogo, no carga variables, no incorpora datasets territoriales o socioeconómicos, no crea agentes, no modifica Pareto y no despliega el sistema. Su función es documentar y congelar decisiones de diseño para evitar que la implementación futura fragmente la ontología existente.

## 2. Principio del catálogo controlado

**DL-MULTISCALE-VARIABLE-01.** SiMS-DeI mantendrá un catálogo controlado de variables multiescala. Las variables no se tratarán como una lista plana universal. Su aplicabilidad y significado podrán depender de `SpatialScope`, tipología, contexto, etapa, jurisdicción, `TemporalScope`, datos disponibles y objetivos.

El catálogo futuro deberá conservar identidades estables, versionadas y neutrales respecto de la interfaz. Las etiquetas visibles y las traducciones no constituirán la identidad canónica de una variable.

## 3. Escalas canónicas

**DL-MULTISCALE-VARIABLE-02.** El catálogo deberá soportar exactamente los once valores canónicos siguientes, sin crear vocabularios alternativos:

1. `objeto`
2. `espacio`
3. `sistema`
4. `edificacion`
5. `parcela_sitio`
6. `zona_barrio_sector`
7. `distrito_ciudad`
8. `provincia_metropoli`
9. `region`
10. `macro_region`
11. `pais`

El orden de presentación no modifica la jerarquía canónica del Core. Cualquier migración futura deberá reutilizar `SpatialScope` y no introducir nombres paralelos.

## 4. Perfiles variables por escala

**DL-MULTISCALE-VARIABLE-03.** Cada escala tendrá eventualmente un perfil de variables. Los perfiles lógicos serán: `ObjectVariableProfile`, `SpaceVariableProfile`, `SystemVariableProfile`, `BuildingVariableProfile`, `SiteVariableProfile`, `NeighborhoodVariableProfile`, `CityVariableProfile`, `MetropolitanVariableProfile`, `RegionVariableProfile`, `MacroRegionVariableProfile` y `CountryVariableProfile`.

Estos perfiles son conceptos arquitectónicos. No requieren once modelos de datos independientes ni once aplicaciones. La implementación deberá preferir metadatos controlados, composición y reglas de aplicabilidad.

## 5. Identidad estable de variable

**DL-MULTISCALE-VARIABLE-04.** Una variable tendrá una identidad canónica estable e independiente del idioma y de la interfaz. El diseño futuro podrá incluir `variable_id`, dominio, nombre canónico, descripción, tipo de dato, unidad, escalas, aplicabilidad, nivel de requerimiento, rol, resolución temporal, resolución espacial, requisitos de fuente, requisitos de provenance, capacidades soportadas, evaluaciones soportadas, reglas de validación y versión de catálogo.

Estos campos son conceptuales. Sus nombres y cardinalidades deberán determinarse después de auditar las entidades existentes de Variable, `SuggestedVariable`, `ProjectVariable`, `Objective`, `Constraint`, `Fact`, `Assumption`, `Evidence`, `Source`, `Evaluation` y el modelo de capabilities de S7-P0.5. No se permite duplicar una arquitectura canónica existente.

## 6. Requirement frente a capability

**DL-MULTISCALE-VARIABLE-05.** La aplicabilidad de una variable utilizará semántica controlada. Como mínimo deberá distinguir `REQUIRED`, `RECOMMENDED`, `OPTIONAL` y `NOT_APPLICABLE`.

Esta dimensión es distinta de la disponibilidad de una capability. La capability utiliza `AVAILABLE`, `REQUIRES_DATA`, `NOT_AVAILABLE` y `NOT_APPLICABLE`. El sistema no debe confundir el requerimiento de una variable con la disponibilidad operativa de un análisis.

## 7. Roles epistemológicos y de diseño

**DL-MULTISCALE-VARIABLE-06.** El modelo futuro distinguirá, como mínimo, los roles `STATE`, `FACT`, `ASSUMPTION`, `INPUT`, `DESIGN_VARIABLE`, `CONSTRAINT`, `OBJECTIVE`, `EVALUATION_METRIC`, `DERIVED_METRIC`, `CONTEXT` y `REFERENCE`.

Una variable podrá desempeñar más de un rol solamente cuando la definición canónica lo establezca de forma explícita. Un indicador estadístico no se convertirá automáticamente en variable de diseño.

## 8. Distinciones obligatorias

**DL-MULTISCALE-VARIABLE-07.** Se preservarán las siguientes diferencias:

- Variable de estado no equivale a variable de diseño.
- Variable de diseño no equivale a objetivo.
- Objetivo no equivale a restricción.
- Restricción no equivale a métrica de evaluación.

Por ejemplo, población regional es una variable de estado o contexto. La ubicación de un corredor logístico propuesto es una variable de diseño. La pérdida máxima de ecosistema protegido es una restricción. La reducción del tiempo medio de accesibilidad es un objetivo. El cambio medido en ese tiempo es una métrica de evaluación.

Los ejemplos son ilustrativos y no congelan métricas canónicas.

## 9. Dominios estables

**DL-MULTISCALE-VARIABLE-08.** El catálogo organizará las variables mediante conceptos de dominio estables. Los candidatos incluyen identidad, geometría, geografía, programa, función, material, factores humanos, accesibilidad, relación espacial, estructura, sanitario, eléctrico, energía, ambiente, clima, agua, suelo, paisaje, movilidad, infraestructura, demografía, vivienda, salud, educación, economía, empleo, agricultura, pesca, minería, industria, turismo, logística, conectividad, uso de suelo, ecosistemas, riesgos, inversión pública, costo, regulación y gobernanza.

Esta lista es una taxonomía candidata. No queda congelada como vocabulario final y no debe implementarse sin una auditoría específica del catálogo.

## 10. Fuentes y autoridades

**DL-MULTISCALE-VARIABLE-09.** Los ministerios y organismos públicos no serán la taxonomía fundamental. La dirección conceptual será:

```text
DOMAIN
  ↓
VARIABLE
  ↓
SOURCE REQUIREMENT
  ↓
CURRENT RESPONSIBLE AUTHORITY / DATA PROVIDER
```

Las instituciones y sus responsabilidades pueden cambiar. El dominio de inteligencia de diseño debe permanecer estable y asociarse a las autoridades mediante fuentes, evidencias y provenance.

## 11. Significado dependiente de escala

**DL-MULTISCALE-VARIABLE-10.** Una variable puede cambiar de relevancia y significado según la escala. El concepto solar, por ejemplo, puede representar exposición de vanos en `espacio`, exposición de fachada y cubierta en `edificacion`, potencial de implantación en `parcela_sitio`, sombreado urbano en `zona_barrio_sector` y recurso energético territorial en `region` o `pais`.

Estas expresiones no deben colapsarse en una única capability idéntica. La relación entre variable, capacidad y escala será explícita.

## 12. Variables ambientales y resultados derivados

**DL-MULTISCALE-VARIABLE-11.** Las variables ambientales se separarán de los análisis espaciales derivados. La radiación de onda corta de Open-Meteo es una variable de entrada ambiental. La exposición solar de una fachada es un resultado espacial derivado. La exposición anual es una métrica derivada agregada temporalmente. Un objetivo solar, si se autoriza, pertenece a una evaluación o a Pareto separado.

El sistema no deberá presentar un dato ambiental como simulación del edificio ni convertir automáticamente una entrada en una decisión.

## 13. Inteligencia territorial y socioeconómica

**DL-MULTISCALE-VARIABLE-12.** Las escalas `region`, `macro_region` y `pais` deberán poder representar variables territoriales y socioeconómicas cuando sean relevantes. Las familias futuras pueden incluir demografía, economía, estructura productiva, empleo, ingreso, pobreza, vivienda, salud, educación, agricultura, frontera agrícola, pesca, acuicultura, minería, industria, turismo, energía, agua, transporte, logística, conectividad digital, ambiente, ecosistemas, clima, riesgos, inversión pública y equidad territorial.

Estos son requisitos futuros. No se autoriza cargar datasets ni integrar INEI, MEF, CEPLAN u otros organismos mediante este Decision Lock.

## 14. Macro-región como sistema de relaciones

**DL-MULTISCALE-VARIABLE-13.** `macro_region` no se modelará únicamente como suma aritmética de regiones. Sus variables futuras deberán poder representar flujos interregionales, migración, corredores económicos, cadenas productivas, logística, flujos energéticos, sistemas hídricos, ecosistemas compartidos, riesgos compartidos, redes de servicios e infraestructura estratégica.

Las relaciones y los flujos son requisitos analíticos de primera clase para esa escala.

## 15. País como sistema nacional

**DL-MULTISCALE-VARIABLE-14.** `pais` no se modelará simplemente como una región más grande. La inteligencia nacional puede requerir variables macroeconómicas, estructura territorial, disparidades regionales, sistemas nacionales de infraestructura y servicios, seguridad energética, seguridad hídrica, logística nacional, corredores estratégicos, sistemas ambientales, riesgos nacionales y escenarios de largo plazo.

La lista canónica nacional deberá definirse mediante una orden posterior.

## 16. Provenance

**DL-MULTISCALE-VARIABLE-15.** Toda variable respaldada por datos deberá conservar provenance adecuada a su autoridad y uso. El modelo futuro deberá poder identificar fuente, autoridad, dataset, versión del dataset, fecha de observación o referencia, fecha de recuperación, cobertura geográfica, resolución espacial, resolución temporal, unidad, metodología, evidencia y clase de provenance.

Un número no trazable no podrá presentarse como dato autoritativo del proyecto.

## 17. Clasificación epistemológica

**DL-MULTISCALE-VARIABLE-16.** Cuando corresponda, el catálogo distinguirá `REAL`, `APPROXIMATED`, `ASSUMED`, `SYNTHETIC` y `NOT_AVAILABLE`.

`NOT_AVAILABLE` no equivale a `ASSUMED`, no equivale a cero y no equivale a `NOT_APPLICABLE`. La interfaz y los agentes deberán preservar esas diferencias.

## 18. Datos faltantes como estado

**DL-MULTISCALE-VARIABLE-17.** Los datos faltantes se tratarán como inteligencia controlada. El sistema deberá poder indicar qué datos existen, cuáles faltan, cuáles son requeridos, qué análisis están bloqueados y qué fuentes adicionales podrían satisfacer el requisito.

`MISSING DATA` es un estado del sistema. No es una invitación a fabricar valores.

## 19. Relación con capabilities y workspace

**DL-MULTISCALE-VARIABLE-18.** La relación conceptual futura será:

```text
Multiscale Variable Catalog
        +
Scale Capability Profile
        +
Project Context
        +
Available Project Data
        ↓
Capability Resolver
        ↓
Adaptive Workspace
```

La arquitectura S7-P0.5 deberá permanecer compatible con esta relación, pero no necesita implementar todavía el catálogo multiescala.

## 20. Comportamiento del workspace futuro

**DL-MULTISCALE-VARIABLE-19.** El workspace adaptativo deberá usar variables y capabilities para determinar qué preguntar al usuario, qué datos buscar, qué datos faltan, qué módulos mostrar, qué análisis son posibles, qué agentes son relevantes, qué fuentes son pertinentes, qué visualizaciones son pertinentes, qué evaluaciones se pueden realizar y qué no es aplicable.

La lógica deberá proceder de un modelo controlado, no de condicionales dispersos en el frontend.

## 21. Unidades y dimensiones

**DL-MULTISCALE-VARIABLE-20.** El catálogo futuro soportará unidades y semántica dimensional. Entre los ejemplos se encuentran metros, metros cuadrados, metros cúbicos, grados, personas, personas por kilómetro cuadrado, hectáreas, kilómetros, kilómetros cuadrados, metros cúbicos por segundo, kWh, MW, W/m², moneda, moneda por persona, porcentaje, índice, toneladas, toneladas por año, horas y minutos.

No se podrán comparar ni agregar unidades incompatibles sin metodología explícita.

## 22. Semántica temporal

**DL-MULTISCALE-VARIABLE-21.** La semántica temporal será explícita. Los tipos candidatos incluyen `STATIC`, `PROJECT_STATE`, `INSTANT`, `HOURLY`, `DAILY`, `MONTHLY`, `QUARTERLY`, `ANNUAL`, `MULTIYEAR` y `SCENARIO_YEAR`.

La geometría del edificio puede ser `PROJECT_STATE`. La radiación solar puede ser horaria. La población puede referirse a un año de referencia. Una proyección de población para 2050 es un escenario. El sistema no comparará silenciosamente periodos incompatibles.

## 23. Resolución espacial

**DL-MULTISCALE-VARIABLE-22.** La resolución espacial será explícita cuando sea relevante. Puede corresponder a objeto, espacio, edificio, parcela, celda de grilla, unidad censal, distrito, provincia, región, cuenca, corredor o país.

Un agregado nacional no será tratado automáticamente como válido para una evaluación regional o local.

## 24. Observación frente a escenario

**DL-MULTISCALE-VARIABLE-23.** El catálogo distinguirá variables observadas o históricas de variables proyectadas o de escenario. Por ejemplo, `population_2025_observed` no equivale a `population_2050_projected`; una carretera existente no equivale a un corredor propuesto.

Los datos reales y los escenarios no se mezclarán sin semántica explícita.

## 25. Identidad de diseño

**DL-MULTISCALE-VARIABLE-24.** En escalas superiores, SiMS-DeI conservará su identidad como sistema de inteligencia de diseño y no se convertirá en un dashboard estadístico. La información territorial deberá conectar estado actual, problema u oportunidad, objetivos, restricciones, variables espaciales o de política, escenarios alternativos, evaluación, trade-offs o Pareto cuando corresponda, revisión humana y decisión.

La cadena no crea autoridad automática. Mantiene la revisión humana antes de la decisión.

## 26. Variables controlables en escalas superiores

**DL-MULTISCALE-VARIABLE-25.** Los futuros ejemplos de `region`, `macro_region` y `pais` deberán contener variables controlables de escenario o diseño, además de indicadores descriptivos. Los ejemplos conceptuales incluyen ubicación de infraestructura, configuración de corredores, distribución de redes de servicios, estrategia de áreas protegidas, estrategia de crecimiento urbano, expansión de riego, infraestructura energética, nodos logísticos, configuración de redes sanitarias e inversión.

Estos ejemplos no son variables canónicas y no autorizan implementación.

## 27. Matriz ampliada de capability y datos

**DL-MULTISCALE-VARIABLE-26.** El trabajo futuro EL-P0 deberá ampliar la matriz de dataset mínimo y completo a una **Multiscale Capability & Data Matrix** para las once escalas. Cada fila de escala deberá considerar:

1. dataset mínimo;
2. dataset completo o recomendado;
3. perfil de variables;
4. dominios aplicables;
5. capabilities aplicables;
6. variables requeridas por capability;
7. análisis aplicables;
8. visualizaciones aplicables;
9. agentes aplicables;
10. regulaciones aplicables;
11. fuentes candidatas;
12. requisitos de provenance;
13. requisitos temporales;
14. requisitos de resolución espacial;
15. capabilities no aplicables.

## 28. Reutilización y diferenciación

**DL-MULTISCALE-VARIABLE-27.** Una variable semánticamente idéntica entre escalas reutilizará una definición canónica con metadatos de aplicabilidad por escala. Una variable cuyo significado cambie sustancialmente tendrá una identidad canónica distinta.

Por ejemplo, población puede reutilizarse con diferente agregación espacial. `FacadeSolarExposure` y `RegionalSolarResourcePotential` no son la misma variable solo porque ambas se relacionen con radiación solar.

## 29. Versionado histórico

**DL-MULTISCALE-VARIABLE-28.** El catálogo futuro será versionable. Los proyectos y análisis deberán poder identificar la versión del catálogo, la versión de la definición de variable y la versión del perfil de capability.

Una actualización posterior no podrá reinterpretar silenciosamente un análisis histórico.

## 30. Auditoría obligatoria antes de implementar

**DL-MULTISCALE-VARIABLE-29.** Antes de implementar el catálogo se auditarán los repositorios actuales para reutilizar, en lugar de duplicar, las entidades y capacidades existentes: Variable, `SuggestedVariable`, `ProjectVariable`, `Objective`, `Constraint`, `Fact`, `Assumption`, `Evidence`, `Source`, `SpatialScope`, `TemporalScope`, Design Knowledge, Regulatory Intelligence, Site Intelligence, Evaluation y el modelo de capabilities de S7-P0.5.

**DL-MULTISCALE-VARIABLE-30.** La autorización de ejecución actual es **NONE**. No se implementará el catálogo, no se cargarán cientos de variables, no se crearán datasets territoriales, no se integrarán INEI, MEF, CEPLAN o ministerios, no se crearán dashboards regionales, no se implementará análisis macroeconómico, no se crearán once workspaces, no se crearán agentes nuevos, no se modificará Pareto, no se implementará EL-P0 y no se desplegará.

## 31. Compatibilidad con S7-P0.5

Este Decision Lock es compatible con la fundación de capabilities de S7-P0.5, pero no la modifica. S7-P0.5 mantiene su modelo de estados `AVAILABLE`, `REQUIRES_DATA`, `NOT_AVAILABLE` y `NOT_APPLICABLE`. El futuro catálogo añadirá una dimensión distinta de requirement variable: `REQUIRED`, `RECOMMENDED`, `OPTIONAL` y `NOT_APPLICABLE`.

La separación entre ambas dimensiones queda congelada como requisito arquitectónico.

## 32. Estado de implementación

| Elemento | Estado |
|---|---|
| Decision Lock DL-MULTISCALE-VARIABLE-01..30 | Documentado y congelado |
| Multiscale Variable Catalog | No implementado |
| Datos territoriales | No implementados |
| Datos macroeconómicos | No implementados |
| Nuevos agentes | No implementados |
| Once workspaces adaptativos | No implementados |
| Modificación S7-P0.5 por este lock | No |
| Implementación autorizada | No |
| Despliegue | No autorizado |

## 33. Firma y condición de parada

Este documento registra una decisión de arquitectura aprobada para documentación y congelamiento. No constituye autorización de ejecución técnica. Cualquier implementación futura requerirá una orden independiente que incluya auditoría de modelos existentes, alcance, archivos permitidos, pruebas, revisión humana y autorización explícita.

**STOP.**

## Referencias

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SiMS-DeI SICL Core repository"
[2]: https://github.com/YvanCastilloQuezada/sicl-web "SiMS-DeI SICL Web repository"
