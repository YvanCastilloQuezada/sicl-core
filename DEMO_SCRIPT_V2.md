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
