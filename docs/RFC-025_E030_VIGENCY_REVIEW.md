# Revisión de vigencia — Norma Técnica E.030

**Expediente:** RFC-025 / E.030  
**Código:** E.030  
**Título:** Diseño Sismorresistente  
**Autoridad emisora:** Ministerio de Vivienda, Construcción y Saneamiento  
**Estado propuesto por el sistema:** `MODIFICADA — HUMAN_REVIEW_REQUIRED`  
**Estado automático permitido:** No promover a `VIGENTE`

## 1. Resumen ejecutivo

La versión inicial del fixture registraba E.030 como `RM-043-2019-VIVIENDA`. La revisión oficial encontró la Resolución Ministerial N.° 183-2026-VIVIENDA, publicada el 28 de abril de 2026, que modifica la Norma Técnica E.030 y publica un texto técnico E.030 2026.

La página oficial de RM 183 también indica una modificación posterior mediante la Resolución Ministerial N.° 217-2026-VIVIENDA, publicada el 2 de junio de 2026. RM 217 modifica la disposición transitoria de RM 183. Por tanto, el estado correcto del expediente no es `VIGENTE` simple, sino **modificada con revisión de vigencia y régimen transitorio pendiente de firma humana**.

## 2. Fuentes verificadas

| Fuente | Tipo | Resultado |
|---|---|---|
| Portal de RM 183 | Oficial MVCS | HTTP 200; identifica E.030 y RM 183 |
| PDF RM 183 | Oficial MVCS | Descargado y extraído |
| PDF NT E.030 2026 | Oficial MVCS | Descargado y extraído |
| Portal de RM 217 | Oficial MVCS | HTTP 200; identifica modificación posterior |
| PDF RM 217 | Oficial MVCS | Descargado y extraído |

## 3. RM N.° 183-2026-VIVIENDA

La resolución fue publicada el **28 de abril de 2026**.

Su artículo 1 modifica la Norma Técnica E.030 “Diseño Sismorresistente”, contenida en el numeral III.2 Estructuras del Título III Edificaciones del RNE aprobado por el Decreto Supremo N.° 011-2006-VIVIENDA.

La propia resolución expone como objetivos de la modificación:

1. Incrementar la seguridad estructural de las edificaciones.
2. Mejorar la clasificación de perfiles de suelo.
3. Incorporar parámetros sísmicos adicionales.
4. Reforzar el análisis simultáneo en dos direcciones ortogonales.
5. Actualizar criterios para muros de ductilidad limitada.
6. Establecer lineamientos mínimos para estudios de microzonificación sísmica.

## 4. Cambios técnicos identificados en RM 183

### 4.1 Clasificación de perfiles de suelo

Se incorporan criterios basados en:

- Velocidad de propagación de ondas de corte `Vs`.
- Número de golpes corregido `N60`.
- Resistencia al corte no drenada `Su`.

Estos criterios buscan representar de forma más adecuada el comportamiento dinámico de los depósitos de suelo.

### 4.2 Periodo predominante del terreno

Se incorpora el periodo predominante de vibración del terreno `Ts` como parámetro obligatorio para edificaciones de categorías A y B ubicadas en la zona sísmica Z4, junto con su metodología de cálculo.

### 4.3 Acción sísmica simultánea

La modificación incorpora el análisis considerando la acción sísmica simultánea en ambas direcciones ortogonales.

### 4.4 Muros de ductilidad limitada

Se actualizan criterios relacionados con:

- Número máximo de niveles.
- Coeficiente básico de reducción `R₀`.
- Límites de distorsión máxima de entrepiso.

### 4.5 Microzonificación sísmica

Se incorporan lineamientos mínimos para la ejecución de estudios de microzonificación sísmica, con el objetivo de reducir variabilidad entre estudios técnicos.

## 5. Régimen transitorio original de RM 183

La disposición complementaria transitoria original permitía que ciertos proyectos en trámite o ejecución continuaran bajo el texto anterior de E.030 hasta su culminación.

El sistema no debe aplicar esta regla sin revisar, como mínimo:

- Fecha de entrada en vigencia.
- Estado del expediente técnico.
- Estado del trámite de licencia.
- Modalidad de inversión.
- Estado de ejecución.
- Existencia de un régimen transitorio posterior.

## 6. RM N.° 217-2026-VIVIENDA

RM 217 fue publicada el **2 de junio de 2026** y modifica la disposición complementaria transitoria de RM 183.

El texto extraído amplía los supuestos de proyectos que pueden regirse por la norma anterior hasta su culminación. Incluye proyectos que, al entrar en vigencia la resolución, tengan expediente técnico en elaboración o aprobado, licencia en trámite o aprobada, anteproyecto en consulta presentado ante la autoridad competente y, para Asociaciones Público-Privadas, proyectos desde la etapa de estructuración. También incluye saldos de obra derivados de expedientes aprobados antes de la vigencia de la modificatoria.

Este régimen transitorio es material para cualquier evaluación de aplicabilidad. No basta con consultar el documento técnico E.030 2026.

## 7. Estado del registro RFC-025

| Campo | Estado actual recomendado |
|---|---|
| `code` | `E.030` |
| `historical_version` | `RM-043-2019-VIVIENDA` |
| `latest_reviewed_modification` | `RM-183-2026-VIVIENDA` |
| `subsequent_modification` | `RM-217-2026-VIVIENDA` |
| `status` | `MODIFICADA` |
| `effective_date` | Pendiente de confirmación humana/documental |
| `applicability` | Depende del proyecto y régimen transitorio |
| `automatic_promotion` | Prohibida |
| `human_review` | Requerida |

## 8. Reglas de no automatización

El sistema no debe:

- Marcar E.030 como `VIGENTE` solo por encontrar el PDF.
- Aplicar E.030 2026 a todos los proyectos sin revisar transición.
- Aplicar E.030 2019 a todos los proyectos antiguos sin revisar el expediente.
- Convertir los cambios descritos en una certificación estructural.
- Sustituir el cálculo, memoria o revisión de un profesional competente.
- Crear una Decision de proyecto.

## 9. Evidencias requeridas para cerrar la revisión

La autoridad humana debe verificar:

- Publicación oficial en El Peruano.
- Fecha exacta de entrada en vigencia.
- Texto consolidado aplicable.
- Relación entre RM 183 y RM 217.
- Aplicación temporal al tipo de proyecto.
- Estado del expediente y licencia.
- Competencia del revisor.
- Fuente y hash de los PDFs almacenados.

## 10. Decisión de la autoridad humana

**Decisión propuesta:** `MODIFICADA — NO PROMOVER A VIGENTE TODAVÍA`

**Fundamento:** se verificó una modificación de E.030 y una modificación posterior de su régimen transitorio. La vigencia y aplicabilidad dependen del texto consolidado, la fecha de entrada en vigor y la situación del proyecto.

**Actor revisor:** ____________________________________

**Cargo / autoridad:** __________________________________

**Fecha de revisión:** __________________________________

**Estado firmado:**

- [ ] `VIGENTE`
- [ ] `MODIFICADA`
- [ ] `DEROGADA`
- [ ] `NO_VERIFICADA`
- [ ] `VIGENTE CON RÉGIMEN TRANSITORIO`

**Observaciones:**

__________________________________________________________________

__________________________________________________________________

**Firma:** ____________________________________

## References

[1]: https://www.gob.pe/institucion/vivienda/normas-legales/8081915-183-2026-vivienda "Resolución Ministerial N.° 183-2026-VIVIENDA"

[2]: https://cdn.www.gob.pe/uploads/document/file/9902956/8081915-rm-183-2026-vivienda-modifica-norma-tecnica-e-030.pdf?v=1777909402 "RM 183-2026-VIVIENDA — Modifica Norma Técnica E.030"

[3]: https://cdn.www.gob.pe/uploads/document/file/9902957/8081915-nt-e-030-diseno-sismorresistente-2026.pdf?v=1777909403 "NT E.030 Diseño Sismorresistente 2026"

[4]: https://www.gob.pe/institucion/vivienda/normas-legales/8219609-217-2026-vivienda "Resolución Ministerial N.° 217-2026-VIVIENDA"
