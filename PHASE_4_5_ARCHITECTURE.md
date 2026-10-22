# SICL — Arquitectura propuesta para Fases 4 y 5

**Estado:** Documento de diseño; no autoriza implementación de agentes, optimización ni Pareto.

## 1. Agente bioclimático

El agente bioclimático debe consumir únicamente información explícita y trazable del proyecto: ubicación, hechos climáticos, radiación, vientos, orientación, objetivos, restricciones y evaluaciones existentes. Cada entrada debe conservar su `source`, timestamp y referencia al evento de origen. Los datos desconocidos no deben completarse silenciosamente; el agente debe devolver `REQUIRES_HUMAN_DECISION` cuando falte evidencia suficiente.

Su salida propuesta es una o más `Evaluation` asociadas con una `Alternative` y un `Objective`. Cada evaluación debe incluir valor, unidad, confianza y fuente. El agente recomienda o calcula; no registra `Decision` y no cambia hechos ni restricciones sin una operación humana explícita.

## 2. Debate multi-agente

El debate debe modelarse como una comparación de análisis independientes sobre la misma `Alternative` y los mismos `Objective` y `Constraint`. Por ejemplo, un agente económico puede producir evaluaciones de coste y un agente bioclimático evaluaciones de desempeño ambiental. Cada intervención debe identificarse por agente, versión, fuente y método.

El orquestador no debe promediar resultados heterogéneos sin una regla aprobada. Debe producir un expediente de comparación que muestre acuerdos, desacuerdos, datos faltantes y trade-offs. La salida es una `Recommendation` o un estado de insuficiencia; nunca una `Decision` automática.

## 3. Pareto básico

La primera versión de Pareto debe limitarse a objetivos numéricos con dirección explícita (`MAXIMIZE` o `MINIMIZE`) y unidades compatibles. Para cada alternativa, el algoritmo debe declarar si está dominada, no dominada o no evaluable por datos insuficientes. Debe conservar los valores de entrada, la versión del método y el conjunto exacto de alternativas comparadas.

No se debe mezclar Pareto con ponderaciones subjetivas ni convertir la frontera no dominada en ganador automático. Una recomendación puede presentar la frontera y explicar los trade-offs; la autoridad humana elige y registra la decisión.

## 4. Dependencias y límites

La Fase 4 requiere primero un contrato de fuentes y métodos, un catálogo de unidades, una política de datos faltantes y pruebas de no mutación de hechos. La Fase 5 requiere después la comparación multiobjetivo, el algoritmo Pareto determinista y evidencia reproducible.

Site Intelligence de la fase actual es un adaptador determinista y explícitamente simulado. No se debe presentar como consulta en tiempo real a SENAMHI, NASA POWER o la Municipalidad hasta implementar conectores, validación de respuestas, versionado y manejo de disponibilidad.
