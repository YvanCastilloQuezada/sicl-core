# Design Knowledge Multisource Pilot

## Estado

**IMPLEMENTED LOCALLY — CONTROLLED PILOT**. El piloto amplía el catálogo existente de `DesignKnowledgeSource` y `DesignKnowledgeItem`; no crea un agente paralelo, no ingiere libros y no convierte referencias bibliográficas en normativa o decisiones.

## Fuentes y tratamiento

| Familia | Fuente | Tratamiento | Estado epistemológico |
|---|---|---|---|
| Alexander/CES | Christopher Alexander / CES, catálogo existente | Referencia teórica y patrones ya registrados | `SOURCE_DERIVED` / interpretación estructurada |
| PREVI | *The Experimental Housing Project (PREVI), Lima: The Making of a Neighbourhood* | Caso metadata-only, sin planos ni imágenes ingeridos | `CASE_METADATA` |
| Ching | Francis D. K. Ching, *Architecture: Form, Space, and Order*, 5th ed., Wiley, 2023, ISBN 978-1-119-85338-1 | Ítems estructurados de forma-espacio, circulación y proporción; sin reproducción de texto protegido | `SIMS_DEI_DERIVED_INTERPRETATION` |
| Neufert | Ernst Neufert / Johannes Kister, *Architects' Data / Bauentwurfslehre* | Metadata-only; preguntas de revisión dimensional y funcional | `SOURCE_METADATA_ONLY` |
| Edward T. White | *Site Analysis: Diagramming Information for Architectural Design*, Architectural Media, 1983, ISBN 9781928643043 | Ítems estructurados de lectura del sitio; sin reproducción de diagramas | `SIMS_DEI_DERIVED_INTERPRETATION` |

La ficha de Ching fue contrastada con Wiley [1]. La historia editorial y el tratamiento de Neufert se contrastaron con Neufert Stiftung [2]. PREVI se registra con la metadata bibliográfica de Wiley [3]. White se registra con metadata bibliográfica pública de Google Books [4].

## Relaciones entre fuentes

Las relaciones se expresan como contribuciones complementarias, no como consenso autoral:

`PATTERN_RELATIONAL` + `PRECEDENT_CASE` + `FORM_SPACE_ORDER` + `DIMENSIONAL_FUNCTIONAL` + `SITE_ANALYSIS`

Cada relación incluye provenance, estado epistemológico y `human_review_required=true`. Las contribuciones no crean `Objective`, `Constraint`, `Recommendation` ni `Decision` automáticamente.

## Flujo operativo

1. Human Intent se interpreta determinísticamente.
2. La consulta recupera coincidencias lexicales y, en el piloto, añade un representante aplicable por familia ausente, marcado como candidato contextual.
3. El agente devuelve fuentes, ítems, limitaciones y posibles direcciones.
4. El razonamiento semántico proyecta fuerzas, tensiones, relaciones e hipótesis provisionales.
5. Las familias se combinan como preguntas de exploración; no se atribuye a un autor una síntesis que no esté en la fuente.
6. La generación, evaluación, comparación, revisión y decisión siguen separadas. La decisión permanece bajo autoridad humana.

## Límites epistemológicos

Neufert permanece estrictamente `REFERENCE_ONLY`, `NOT_REGULATORY` y `NO_REPRODUCTION`. No se reproducen medidas, tablas, diagramas o fragmentos protegidos. Ching y White se usan como referencias estructuradas de SiMS-DeI, no como citas literales ni reglas universales. PREVI se mantiene como caso candidato/documental y no como solución transferible automáticamente. Chimbote no se activa como caso; permanece `CASE_CANDIDATE` hasta contar con evidencia fiable específica.

## Validación

- Core: **357 passed**, 1 warning.
- Pruebas focalizadas multisource, semántica y piloto Alexander/CES: **11 passed**.
- Compilación `src`, `api` y `tests`: **PASS**.
- `git diff --check`: **PASS**.
- Web: typecheck, suite completa, build y `git diff --check`: **PASS**; no se modificó el Web porque reutiliza el contrato semántico existente.
- Decisión creada: **false**.
- Recomendación creada: **false**.
- Confirmación humana requerida: **true**.

## Referencias

[1]: https://www.wiley.com/en-us/Architecture%3A+Form%2C+Space%2C+and+Order%2C+5th+Edition-p-9781119853381 "Wiley — Architecture: Form, Space, and Order, 5th Edition"
[2]: https://www.neufert-stiftung.de/en/bauentwurfslehre "Neufert Stiftung — Bauentwurfslehre"
[3]: https://onlinelibrary.wiley.com/doi/abs/10.1002/ad.1234 "Wiley — The Experimental Housing Project (PREVI), Lima"
[4]: https://books.google.com/books/about/Site_Analysis.html?id=m2PRoAEACAAJ "Google Books — Site Analysis by Edward T. White"
