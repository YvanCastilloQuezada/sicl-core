# SICL v2.0 — Guión de demostración para arquitectos

**Product Owner:** Arquitecto Wilfredo Yvan Castillo Quezada  
**Caso:** Edificio Yvan Trujillo  
**Objetivo:** demostrar inteligencia trazable sin sustituir la decisión profesional humana.

## Regla de la demostración

SICL calcula, registra evidencia y formula recomendaciones. **La decisión sigue perteneciendo al arquitecto.** Los agentes no crean decisiones y Pareto no elige un ganador automático.

## Preparación

Abrir SICL Core en una sesión limpia y crear el proyecto:

```text
/PROJECT CREATE EDIFICIO-YVAN-TRUJILLO-01 Edificio Yvan Trujillo
/OBJECTIVE SET ENERGY_SAVINGS MAXIMIZE 80
/OBJECTIVE SET CONSTRUCTION_COST MINIMIZE 100
/ALTERNATIVE CREATE CONVENCIONAL_A
/ALTERNATIVE CREATE BIOCLIMATICA_B
/ALTERNATIVE SET CONVENCIONAL_A facade vidrio simple
/ALTERNATIVE SET CONVENCIONAL_A orientation norte
/ALTERNATIVE SET BIOCLIMATICA_B facade doble piel
/ALTERNATIVE SET BIOCLIMATICA_B orientation sur
/EVALUATE CONVENCIONAL_A ENERGY_SAVINGS 70 score 0.9 USER_INPUT
/EVALUATE CONVENCIONAL_A CONSTRUCTION_COST 60 usd_m2 0.9 USER_INPUT
/EVALUATE BIOCLIMATICA_B ENERGY_SAVINGS 90 score 0.9 USER_INPUT
/EVALUATE BIOCLIMATICA_B CONSTRUCTION_COST 85 usd_m2 0.9 USER_INPUT
```

Si se quiere mostrar el fallback local, se puede ejecutar la demostración sin internet. El sistema debe indicar que los datos proceden del fixture, no de Open-Meteo.

## 1. Inteligencia del sitio

### Comando

```text
/SITE INTELLIGENCE "Trujillo, Peru"
```

### Qué debe decir el Product Owner

> “Ahora no voy a introducir manualmente todos los datos iniciales del sitio. SICL consulta una fuente pública, incorpora la ubicación y sus indicadores ambientales como hechos trazables, y conserva la procedencia de cada dato. Esto acelera el diagnóstico sin convertir una inferencia en una decisión.”

### Qué debe observar el arquitecto

- Se generan `Fact` y no `Assumption`.
- La respuesta muestra coordenadas, temperatura, viento y radiación.
- Con internet disponible, el `source` esperado es `OPEN_METEO_API`.
- Si la API no está disponible, el resultado debe declarar el fixture determinista `SITE_INTELLIGENCE_FIXTURE`.
- Los eventos conservan la misma fuente y quedan en el historial append-only.

### Pregunta clave de validación

> “¿La procedencia de cada dato es visible y suficiente para decidir si este hecho puede entrar al análisis del proyecto?”

## 2. Agente bioclimático

### Comando

```text
/AGENT RUN BIOCLIMATIC CONVENCIONAL_A
```

### Qué debe decir el Product Owner

> “El agente bioclimático no decide por nosotros. Lee los hechos del sitio y los parámetros de la alternativa. Si detecta un clima cálido y una fachada de vidrio simple, aplica una regla explícita, cuantificable y reproducible sobre el desempeño energético.”

### Qué debe observar el arquitecto

- Se crea una `Evaluation`, no una `Decision`.
- El resultado usa `source=EXPERT_SYSTEM`.
- La evaluación queda asociada a `ENERGY_SAVINGS` y a `CONVENCIONAL_A`.
- La penalización de fachada simple es visible en el valor calculado.
- El historial registra `AGENT_EVALUATION_RECORDED`.

### Pregunta clave de validación

> “¿La regla aplicada es comprensible, auditable y modificable por el equipo profesional sin ocultar el razonamiento detrás de una caja negra?”

## 3. Frente de Pareto

### Comando

```text
/PARETO ENERGY_SAVINGS CONSTRUCTION_COST
```

### Qué debe decir el Product Owner

> “SICL no reduce dos objetivos distintos a una sola puntuación arbitraria. Muestra qué alternativas no están dominadas y cuáles son dominadas, manteniendo visible el conflicto entre desempeño energético y costo de construcción.”

### Qué debe observar el arquitecto

- El resultado separa alternativas `non_dominated` y `dominated`.
- Las direcciones se respetan: energía se maximiza y costo se minimiza.
- Los datos incompletos aparecen separados, no se transforman en cero.
- El comando es read-only: no crea recomendación ni decisión.
- La frontera de Pareto informa el debate profesional; no selecciona automáticamente una alternativa.

### Pregunta clave de validación

> “¿La frontera representa de forma suficientemente clara los trade-offs para que el arquitecto pueda ejercer su juicio profesional?”

## Cierre recomendado

Ejecutar:

```text
/STATUS
/HISTORY
```

El Product Owner debe cerrar diciendo:

> “SICL ha producido hechos trazables, una evaluación experta y una frontera de alternativas. Ninguno de esos resultados reemplaza la autoridad humana. La siguiente acción válida es revisar la evidencia, discutir los trade-offs y registrar una decisión humana explícita con actor y autoridad.”

## Criterios de aceptación de la reunión

| Criterio | PASS esperado |
|---|---|
| Fuente de Site Intelligence | `OPEN_METEO_API` o fallback explícito `SITE_INTELLIGENCE_FIXTURE` |
| Separación epistemológica | `Fact` distinto de `Assumption` |
| Agente | Produce `Evaluation` con `EXPERT_SYSTEM` |
| Autoridad | El agente no crea `Decision` |
| Pareto | Devuelve no dominadas, dominadas e incompletas |
| Mutabilidad | Site Intelligence, agente y Pareto conservan historial append-only |
| Decisión | Solo un actor humano puede registrar `Decision` |

## 4. Generación paramétrica de alternativas

### Comando

```text
/GENERATE CONVENCIONAL_A ENERGY_SAVINGS,CONSTRUCTION_COST
```

### Qué debe decir el Product Owner

> “A partir de la evidencia registrada y de las evaluaciones de los agentes, SICL puede proponer variaciones paramétricas para explorar soluciones. Estas propuestas no son decisiones ni recomendaciones: son alternativas nuevas, deterministas y trazables que el arquitecto puede aceptar, descartar o evaluar posteriormente.”

### Qué debe observar el arquitecto

- Se crean una o más alternativas nuevas con estado `PROPOSED`.
- La fuente aparece como `GENERATIVE_OPTIMIZER`.
- Ante sobrepresupuesto, la regla puede reducir el número de pisos o el área.
- Ante bajo desempeño energético, la regla puede proponer una fachada de doble piel.
- Se registra `ALTERNATIVE_GENERATED` en el historial append-only.
- La respuesta indica explícitamente `decision_created=false` y `recommendation_created=false`.
- No se utiliza LLM: la propuesta procede de reglas deterministas auditables.

### Pregunta clave de validación

> “¿La propuesta generada es suficientemente transparente para que el arquitecto pueda identificar qué evidencia y qué regla produjeron cada cambio antes de incorporarla a su proceso profesional?”

## 5. Matriz automatizada de trade-offs

### Comando

```text
/TRADEOFF_MATRIX ENERGY_SAVINGS CONSTRUCTION_COST
```

### Qué debe decir el Product Owner

> “Ahora comparamos todas las alternativas, incluidas las propuestas generadas. SICL muestra los valores de cada objetivo, calcula los deltas respecto de la alternativa base y señala cuáles pertenecen al frente de Pareto. La herramienta organiza el conflicto; no decide cuál solución debe construirse.”

### Qué debe observar el arquitecto

- La matriz incluye alternativas originales y generadas.
- Cada fila muestra los valores de `ENERGY_SAVINGS` y `CONSTRUCTION_COST`.
- Los deltas se expresan de forma explícita y porcentual respecto de la alternativa base.
- El frente de Pareto aparece identificado sin convertirlo en un ganador automático.
- Las alternativas con datos insuficientes permanecen visibles como incompletas o sin evaluación.
- El comando es read-only y no crea `Recommendation` ni `Decision`.

### Pregunta clave de validación

> “¿La matriz y sus deltas permiten comprender el costo de cada mejora energética, y son suficientes para que el arquitecto decida qué trade-off desea priorizar?”

## 6. Validación constitucional específica de la Fase 5

| Criterio | PASS esperado |
|---|---|
| Determinismo | La misma alternativa y las mismas evaluaciones producen la misma transformación paramétrica, salvo identificadores técnicos nuevos. |
| Estado inicial | Toda alternativa generada inicia como `PROPOSED`. |
| Procedencia | Toda alternativa generada conserva `source=GENERATIVE_OPTIMIZER`. |
| Trazabilidad | Cada generación registra `ALTERNATIVE_GENERATED`. |
| Autoridad humana | La generación no crea `Recommendation` ni `Decision`. |
| Inmutabilidad | Los eventos de generación son append-only. |
| Comparación | `TRADEOFF_MATRIX` incluye originales, propuestas, deltas y Pareto. |
| Alcance | No se utilizan LLMs ni agentes autónomos para generar alternativas. |

La demostración debe terminar con una revisión humana explícita de las alternativas propuestas. Ninguna alternativa generada debe presentarse como aprobada, seleccionada o decidida automáticamente.
