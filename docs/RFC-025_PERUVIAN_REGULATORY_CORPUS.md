# RFC-025 — Corpus Normativo Peruano y Conocimiento de Diseño

**Estado:** IMPLEMENTED — Fases 1 y 2 en subconjunto de prueba  
**Fecha:** 16 de septiembre de 2026  
**Autor:** Manus AI  
**Dependencias:** RFC-002, RFC-003, RFC-019, RFC-020, RFC-021 y RFC-024

## 1. Resumen

RFC-025 define la integración controlada de fuentes normativas y manuales de diseño peruanos en SICL. El objetivo es que una observación, una regla normativa y una conclusión analítica puedan distinguirse y trazarse de manera reproducible.

Las Fases 1 y 2 de este RFC están implementadas con un subconjunto de prueba del RNE que incluye A.010, E.030, E.060, IS.010 y EM.010. El fixture conserva la URL oficial, la autoridad, la versión declarada, la fecha de recuperación, referencias de evidencia y un hash determinista del conjunto de datos.

El fixture se mantiene en estado `SAMPLE_UNVERIFIED`. No se presenta como un corpus completo, no certifica vigencia jurídica y no genera automáticamente restricciones ni decisiones.

## 2. Motivación

SICL ya dispone de entidades `Regulation`, `NormativeInterpretation`, `NormativeSnapshot`, `Source` y `Evidence`. También dispone de factibilidad, variables de proyecto, optimización de Pareto y Site Intelligence. Sin una estructura de ingesta explícita, esos componentes no podrían demostrar qué documento sustenta una regla, cuándo fue recuperado ni qué parte fue revisada por una persona autorizada.

RFC-025 establece un límite entre la **ingesta documental** y la **interpretación aplicable**. Cargar un documento no implica afirmar que está vigente. Registrar una evidencia no crea una restricción. Una interpretación normativa revisada tampoco crea una Decision.

## 3. Alcance

El RFC cubre el RNE, sus Normas Técnicas, instrumentos de planificación territorial y fuentes municipales o regionales que puedan ser incorporadas con autorización y revisión humana.

La primera implementación cubre:

1. Registro de fuentes oficiales y sus URLs.
2. Registro de metadatos de normas arquitectónicas, estructurales, sanitarias y eléctricas.
3. Registro y revisión de evidencias descriptivas con trazabilidad completa.
4. Validación de referencias entre fuentes, regulaciones y evidencias.
5. Hash determinista del fixture.
6. Simulación local del Camino A con Open-Meteo, Pareto y RFC-020.

## 4. Fuera de alcance

RFC-025 no descarga de forma masiva todo el RNE, no realiza scraping indiscriminado, no interpreta automáticamente artículos, no emite certificados de cumplimiento, no sustituye revisión profesional y no publica asesoría legal.

Tampoco convierte una URL municipal en una fuente oficial sin verificar autoridad, jurisdicción, vigencia y procedencia.

## 5. Modelo de procedencia

La cadena mínima de procedencia es:

```text
Source
  → Regulation o PlanningInstrument
    → Evidence
      → NormativeSnapshot
        → Project / Variable / Constraint
          → Evaluation / Feasibility
```

Cada transición debe conservar el identificador de la entidad anterior. El sistema debe poder responder qué fuente originó una evidencia y qué evidencia fue utilizada para una evaluación.

### 5.1 Source

`Source` representa el documento o página de origen. Sus campos mínimos son:

| Campo | Requisito |
|---|---|
| `source_id` | Identificador estable y único |
| `source_type` | `OFFICIAL`, `SECONDARY`, `USER_PROVIDED` o `UNKNOWN` |
| `title` | Título visible de la fuente |
| `url` | URL HTTP(S) verificable |
| `version` | Versión, resolución o identificador de publicación |
| `retrieved_at` | Fecha y hora de recuperación |
| `content_hash` | Hash del archivo o representación canónica |

### 5.2 Regulation

`Regulation` describe una norma sin afirmar automáticamente su vigencia. Debe conservar código, título, autoridad, jurisdicción, versión, fechas, fuente y escalas aplicables.

El estado inicial de una incorporación nueva es `NO_VERIFICADA`. Solo una revisión autorizada puede cambiar el estado a `VIGENTE`, `MODIFICADA` o `DEROGADA`.

### 5.3 Evidence

`Evidence` registra una afirmación capturada, su tipo, la fuente, la referencia de artículo, el método de captura y su hash. El estado de evidencia distingue información observada de información todavía no verificada.

### 5.4 NormativeSnapshot

`NormativeSnapshot` congela el conjunto de regulaciones e interpretaciones consideradas para un proyecto en una fecha de corte. No debe cambiar retrospectivamente cuando una regulación posterior recibe una nueva versión.

## 6. Fuentes oficiales iniciales

La fuente inicial corresponde al portal del Ministerio de Vivienda, Construcción y Saneamiento, que publica el Reglamento Nacional de Edificaciones y enlaza el documento de la Norma A.010 asociado a la RM N.° 191-2021-VIVIENDA.

El fixture contiene seis registros `Source`: el portal oficial del RNE y los PDF oficiales de A.010, E.030, E.060, IS.010 y EM.010. Todas las normas se registran como `NO_VERIFICADA` porque esta fase implementa la ingesta de prueba, no una certificación jurídica de vigencia.

## 7. Estructura del fixture

El archivo `data/regulatory/rne_a010_sample.json` contiene:

- `schema_version` para controlar compatibilidad.
- `corpus_status` con valor obligatorio `SAMPLE_UNVERIFIED`.
- `retrieved_at` para la fecha de captura.
- `sources` para las URLs oficiales.
- `regulations` para metadatos de A.010, E.030, E.060, IS.010 y EM.010.
- `evidence` para siete referencias descriptivas.
- `scope_applicable` para asociar las normas a `EDIFICACION`, `SISTEMA` y `ESPACIO`.

El cargador `sicl.regulatory_corpus.load_corpus_fixture` valida las claves, unicidad, tipos de fuente, URLs, referencias y estados. Después calcula `fixture_hash` con JSON canónico ordenado.

## 8. Fase 1 — Fuentes y alcance

La Fase 1 identifica la autoridad y el origen documental. Cada fuente debe pasar una revisión de autoridad, jurisdicción, fecha, versión, disponibilidad y condiciones de uso.

La incorporación de fuentes municipales debe conservar el municipio, provincia, región, órgano emisor, instrumento, fecha de aprobación y periodo de vigencia. Una URL sin estos metadatos es insuficiente para un resultado normativo.

La clasificación mínima por escala es:

| Escala | Ejemplos de fuentes |
|---|---|
| `PAIS` | RNE y políticas nacionales |
| `MACRO_REGION` | Instrumentos interregionales |
| `REGION` | Planes regionales |
| `PROVINCIA_METROPOLI` | Planes provinciales o metropolitanos |
| `DISTRITO_CIUDAD` | Planes urbanos y ordenanzas distritales |
| `ZONA_BARRIO_SECTOR` | Instrumentos sectoriales o planes específicos |
| `PARCELA_SITIO` | Parámetros urbanísticos aplicables al predio |
| `EDIFICACION` | A.010, A.020 y normas de edificación |
| `SISTEMA` | Instalaciones eléctricas, sanitarias y estructurales |
| `ESPACIO` | Requisitos espaciales y de accesibilidad |
| `OBJETO` | Elementos o componentes particulares |

## 9. Fase 2 — Ingesta controlada

La Fase 2 incorpora documentos y evidencias sin convertir todavía su contenido en reglas ejecutables. La ingesta debe conservar el archivo o una representación autorizada, calcular un hash, segmentar referencias y registrar el método usado.

El subconjunto usa resúmenes descriptivos en vez de copiar los documentos completos. Las frases no deben interpretarse como una transcripción exhaustiva del texto normativo.

Antes de una ingesta de producción se debe comprobar que la fuente puede almacenarse y procesarse conforme a su licencia y a la política del repositorio.

## 10. De evidencia a restricción

Una evidencia puede proponer una regla candidata, pero nunca crea una restricción por sí sola. La transformación requiere:

1. Identificación de artículo o sección.
2. Revisión de autoridad competente.
3. Definición de variable y unidad.
4. Definición de operador y umbral.
5. Registro de si la restricción es dura o blanda.
6. Asociación del alcance espacial y temporal.
7. Registro de confianza, fecha y responsable.
8. Prueba de que no se creó una Decision automáticamente.

Una vez revisada, la regla puede alimentar RFC-020. Si faltan datos, el resultado debe ser `INSUFFICIENT_DATA` y no `FEASIBLE`.

## 11. Camino A de demostración

La simulación incluida en `scripts/rfc025_camino_a_demo.py` ejecuta el siguiente recorrido local:

```text
Open-Meteo
  → SiteObservation
  → alternativas sintéticas
  → evaluaciones de energía y costo
  → Pareto front
  → restricciones de inversión RFC-020
  → feasible_pareto_front
```

La observación de Trujillo se solicita a Open-Meteo. Las alternativas son sintéticas y sus evaluaciones se identifican como analíticas. El fixture A.010 se adjunta como referencia normativa no verificada, pero no se transforma automáticamente en una restricción.

El script informa explícitamente que no crea `Recommendation`, `HumanReview` ni `Decision`. Esto conserva la autoridad humana y evita presentar una optimización como aprobación normativa.

## 12. Integración con Open-Meteo

Open-Meteo aporta indicadores físicos descriptivos, como temperatura media, viento y radiación. Cada observación conserva URL, respuesta cruda, fecha, método y hash.

Estos indicadores pueden alimentar una evaluación bioclimática o una variable de proyecto. No demuestran por sí solos cumplimiento de A.010, de una ordenanza ni de un manual de diseño.

## 13. Integración con Pareto

Pareto utiliza objetivos explícitos. La demostración emplea desempeño energético a maximizar e inversión a minimizar. Una alternativa puede pertenecer a la frontera de Pareto y aun así ser inviable por una restricción dura.

La frontera analítica no constituye recomendación final. La recomendación, si se genera, debe conservar su justificación y pasar a `HumanReview` antes de una `Decision`.

## 14. Integración con RFC-020

RFC-020 evalúa restricciones con estado explícito. En la demostración se utiliza una restricción dura de inversión máxima. El resultado de factibilidad incluye comprobaciones individuales, restricciones fallidas y el método `constraint_filter_v1`.

La norma A.010 se conserva como evidencia de prueba. La restricción de inversión es un dato sintético de demostración, no una exigencia inferida de A.010.

## 15. Reglas de seguridad y autoridad

El corpus no puede:

- Crear decisiones implícitas.
- Convertir una interpretación en certificación legal.
- Cambiar una recomendación a decisión.
- Omitir al actor que revisa.
- Presentar un documento `NO_VERIFICADA` como norma vigente.
- Sustituir a una autoridad municipal o profesional.
- Escribir sobre el Event Log histórico.

## 16. Revisión y validación de evidencias

La revisión ejecutada sobre el fixture comprobó que cada evidencia tiene una fuente existente, una URL HTTP(S), un tipo de fuente, una referencia de artículo o documento, un método de captura y un estado permitido. También comprobó que todas las fuentes del lote son `OFFICIAL`, que no hay identificadores duplicados y que cada regulación apunta a una fuente del mismo lote.

El informe generado por `evidence_traceability_report` contiene una fila por evidencia y el campo `traceable`. El lote actual contiene siete evidencias y todas resultaron trazables. La validación no promueve ninguna evidencia a `REVIEWED` ni ninguna regulación a `VIGENTE`; esos cambios requieren revisión humana posterior.

## 17. Revisión lingüística y semántica

Las normas peruanas pueden contener términos jurídicos, técnicos y regionales. La ingesta debe conservar el texto original cuando esté autorizada, pero los resúmenes deben marcarse como derivados. Cualquier traducción o normalización debe registrar método y responsable.

## 18. Próximas fases

La Fase 3 normalizará artículos y definiciones con referencias estables. La Fase 4 incorporará reglas candidatas revisadas. La Fase 5 añadirá snapshots por proyecto y jurisdicción. La Fase 6 ampliará el corpus a normas urbanas, municipales y planes nacionales o regionales.

Cada ampliación debe ejecutarse como lote trazable. No se debe declarar el corpus completo mientras existan documentos faltantes o fuentes con estado `NO_VERIFICADA`.

## 19. Criterios de aceptación

RFC-025 Fases 1 y 2 se consideran implementadas cuando:

- Existe una fuente oficial identificada.
- Existe un fixture reproducible de A.010, E.030, E.060, IS.010 y EM.010.
- Las fuentes, regulaciones y evidencias tienen referencias consistentes.
- El cargador rechaza referencias rotas, estados inválidos y evidencias sin referencia o método.
- El informe de trazabilidad confirma que las siete evidencias del lote están enlazadas a fuentes oficiales.
- El fixture conserva hash determinista.
- Open-Meteo se combina con Pareto y RFC-020 en una simulación reproducible.
- La simulación no crea una Decision.
- La suite completa permanece verde.

## 20. Limitaciones conocidas

El fixture no contiene el RNE completo. No contiene todas las disposiciones de A.010, E.030, E.060, IS.010 o EM.010. No realiza validación jurídica. No contiene ordenanzas municipales. No incorpora todavía el Plan Estratégico de Desarrollo Nacional al 2050 ni manuales de diseño como reglas computables.

El resultado de Open-Meteo depende de la disponibilidad de la red y de la respuesta del proveedor. El fallback local debe aparecer como simulado y nunca debe mezclarse con datos observados.

## 21. Firma

**Manus AI:** implementación de Fases 1 y 2, ampliación del fixture, validación de evidencias y simulación.
**Product Owner / arquitecto:** revisión requerida para ampliar corpus y promover estados regulatorios.  
**Estado:** `IMPLEMENTED — SAMPLE ONLY; HUMAN REVIEW REQUIRED`.

## References

[1]: https://www.gob.pe/institucion/vivienda/informes-publicaciones/2309793-reglamento-nacional-de-edificaciones-rne "Reglamento Nacional de Edificaciones — Ministerio de Vivienda, Construcción y Saneamiento"

[2]: https://cdn.www.gob.pe/uploads/document/file/2366528/35%20A.010%20CONDICIONES%20GENERALES%20DE%20DISE%C3%91O%20-%20RM%20N%C2%B0%20191-2021-VIVIENDA.pdf?v=1636058378 "A.010 Condiciones Generales de Diseño — RM N.° 191-2021-VIVIENDA"

[4]: https://cdn.www.gob.pe/uploads/document/file/2366641/51%20E.030%20DISE%C3%91O%20SISMORRESISTENTE%20RM-043-2019-VIVIENDA.pdf?v=1677250657 "E.030 Diseño Sismorresistente — RM-043-2019-VIVIENDA"

[5]: https://cdn.www.gob.pe/uploads/document/file/2366660/55%20E.060%20CONCRETO%20ARMADO%20DS%20N%C2%B0%20010-2009.pdf?v=1677250657 "E.060 Concreto Armado — DS N.° 010-2009"

[6]: https://cdn.www.gob.pe/uploads/document/file/2366675/60%20IS.010%20INSTALACIONES%20SANITARIAS%20PARA%20EDIFICACIONES%20DS%20N%C2%B0%20017-2012.pdf?v=1677250657 "IS.010 Instalaciones Sanitarias para Edificaciones — DS N.° 017-2012"

[7]: https://cdn.www.gob.pe/uploads/document/file/2366690/62%20EM.010%20INSTALACIONES%20EL%C3%89CTRICAS%20INTERIORES%20-%20RM%20N%C2%B0%20083-2019-VIVIENDA.pdf?v=1677250657 "EM.010 Instalaciones Eléctricas Interiores — RM N.° 083-2019-VIVIENDA"

[3]: https://open-meteo.com/ "Open-Meteo API"
