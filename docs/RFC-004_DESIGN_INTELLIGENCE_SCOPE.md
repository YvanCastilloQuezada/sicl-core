# RFC-004 — Design Intelligence Scope

**Estado:** IMPLEMENTED — scope mínimo
**Base:** `integration-v2` (`b3789d85`)
**Rama:** `rfc-004-design-intelligence-scope`

## Objetivo

Definir una superficie consultable de principios de diseño dentro de SiMS-DeI/SICL. Esta fase entrega un catálogo estático, read-only y trazable. No implementa evaluación estética ni asigna puntuaciones de belleza.

## Definición

Design Intelligence es un vocabulario estructurado de principios que puede servir como referencia para arquitectos y futuras capacidades de análisis. Un principio no es una Preference: el principio es una categoría doctrinal general; la Preference es una expresión situada de un actor humano dentro de un proyecto.

El catálogo implementado contiene 15 principios: P-01 a P-15. Cada entrada contiene `principle_id`, nombre en español, categoría, descripción, escalas aplicables y fuente bibliográfica declarada. No hay entradas `PENDING_REFERENCE` en la superficie HTTP.

## Principios P-01 a P-12

- P-01 Proporción
- P-02 Escala
- P-03 Ritmo
- P-04 Jerarquía
- P-05 Equilibrio
- P-06 Contraste
- P-07 Unidad
- P-08 Secuencia
- P-09 Luz
- P-10 Materialidad
- P-11 Textura
- P-12 Lleno-vacío

## Principios adicionales del catálogo

- P-13 Integración
- P-14 Contexto
- P-15 Ergonomía

Las fuentes incluyen Ching, *Architecture: Form, Space, and Order*; Zumthor, *Atmospheres* y *Thinking Architecture*; Alexander et al., *A Pattern Language*; Norberg-Schulz, *Genius Loci*; y Neufert, *Architects' Data*. Las referencias se mantienen como trazabilidad bibliográfica, no como certificación normativa.

## Referentes

Se define la estructura `Referent` con identificador, autor, año, ubicación, disciplina, descripción, principios demostrados y fuente. No se cargan referentes reales en esta fase.

## HTTP v1

| Método | Endpoint | Función |
|---|---|---|
| `GET` | `/v1/design/principles` | Lista el catálogo público |
| `GET` | `/v1/design/principles?category=LUZ` | Filtra por categoría |
| `GET` | `/v1/design/principles/{principle_id}` | Recupera un principio |

Todas las respuestas incluyen `contract_version`. Son operaciones read-only y no requieren proyecto.

## CLI

```text
/DESIGN PRINCIPLES
/DESIGN PRINCIPLE <principle_id>
```

Los comandos son read-only y no generan eventos.

## Invariantes

Design Intelligence no decide, no recomienda y no evalúa automáticamente. No crea Decision ni Recommendation. No reemplaza el juicio profesional del arquitecto. El catálogo no muta por HTTP; toda entrada expuesta debe tener una fuente declarada.

## Fuera de alcance

Quedan fuera de RFC-004 la evaluación estética automática, el beauty score, un motor universal de belleza, la generación automática de alternativas, el aprendizaje de referentes y cualquier afirmación de validez profesional. Estas capacidades requieren RFC-004.1 o posterior.
