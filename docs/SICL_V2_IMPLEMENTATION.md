# SICL v2.0 — Site Intelligence, Agents and Pareto

## Estado

Implementado en una rama aislada y sujeto a revisión mediante Pull Request. La suite completa pasa con 46 pruebas.

## Site Intelligence

`/SITE INTELLIGENCE <LOCATION>` intenta consultar Open-Meteo Geocoding y Weather sin API key. Registra coordenadas, temperatura media, viento y radiación como `Fact`, manteniendo `source=OPEN_METEO_API`. Si no hay red, la respuesta es inválida o el lugar no está disponible, Trujillo usa un fixture determinista con `source=SITE_INTELLIGENCE_FIXTURE`; otras ubicaciones devuelven `REQUIRES_HUMAN_DECISION`.

Las pruebas mockean la red. Ninguna prueba depende de disponibilidad externa.

## Agente bioclimático

`/AGENT RUN BIOCLIMATIC <ALTERNATIVE>` ejecuta reglas deterministas y registra una `Evaluation` con `source=EXPERT_SYSTEM`. El agente requiere un objetivo `ENERGY_SAVINGS`, puede penalizar una fachada de vidrio simple en clima cálido y aplicar un ajuste explícito de orientación. No crea `Decision`.

## Pareto

`/PARETO <OBJECTIVE_1> <OBJECTIVE_2>` calcula alternativas no dominadas, alternativas dominadas y datos incompletos. Solo usa objetivos con dirección explícita y evaluaciones existentes. Es una operación read-only: no crea `Recommendation`, `Decision` ni eventos.

## Límites

No se utilizan LLMs. No se crean decisiones automáticas. Los agentes y Pareto no sustituyen la autoridad humana. Las integraciones de datos reales deben conservar fuente, valores, unidad, fecha y evidencia de la respuesta externa antes de considerarse producción.
