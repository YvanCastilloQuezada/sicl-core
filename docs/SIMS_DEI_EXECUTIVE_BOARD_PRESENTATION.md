# Guion ejecutivo para junta directiva

## SiMS-DeI: del dato disperso a la decisión trazable

**Duración recomendada:** 12–15 minutos  
**Audiencia:** junta directiva, dirección de innovación, dirección técnica y responsables de diseño  
**Apoyo visual:** demo breve del Guided Mode y una diapositiva de arquitectura

## 1. Apertura — 60 segundos

**Texto sugerido**

> Hoy presentamos SiMS-DeI, un sistema para apoyar decisiones de diseño espacial en múltiples escalas. Su valor no está en reemplazar el criterio profesional. Está en hacer visible cómo se construye una recomendación, qué datos la sostienen, qué supuestos contiene y en qué punto una persona debe ejercer autoridad.
>
> SiMS-DeI convierte un proceso complejo en un proceso trazable. SICL, su lenguaje formal, permite que la interfaz, los formularios y los análisis terminen en operaciones verificables.

**Mensaje clave:** SiMS-DeI no automatiza la responsabilidad; organiza la inteligencia alrededor de ella.

## 2. El problema — 90 segundos

En los procesos de diseño, la información suele estar repartida entre conversaciones, hojas de cálculo, modelos BIM, mapas, normas y decisiones difíciles de reconstruir. Esa fragmentación genera tres riesgos: pérdida de contexto, mezcla entre hechos y opiniones y decisiones sin una línea clara de evidencia.

La pregunta directiva no es solamente “¿qué alternativa recomendamos?”. También es:

- ¿Qué información utilizamos?
- ¿Qué supusimos?
- ¿Qué restricciones eliminaron alternativas?
- ¿Quién revisó la recomendación?
- ¿Quién tomó la decisión y con qué autoridad?

SiMS-DeI responde esas preguntas como parte del proceso, no como una auditoría posterior.

## 3. La propuesta — 90 segundos

SiMS-DeI ofrece una gramática común para trabajar desde país hasta objeto. El proceso mantiene la misma lógica aunque cambien la escala y el tipo de información:

```text
Contexto → Objetivos → Restricciones → Alternativas → Evaluación → Revisión → Decisión → Auditoría
```

La interfaz presenta el proceso de forma guiada. SICL mantiene el contrato formal. El Core determinista valida estados y reglas. La autoridad humana permanece en el límite final.

## 4. El momento WOW — 2 minutos

**Demostración sugerida**

1. Abrir Guided Mode.
2. Mostrar el mapa de módulos y el siguiente paso.
3. Crear un proyecto sintético.
4. Registrar una Preference de confort y privacidad.
5. Mostrar dos alternativas.
6. Ejecutar una comparación.
7. Mostrar la frontera de Pareto con el filtro de factibilidad.
8. Crear una Recommendation.
9. Registrar HumanReview.
10. Registrar la Decision.
11. Abrir Audit.

**Texto sugerido**

> La experiencia es simple para quien empieza, pero el sistema no simplifica ocultando información. Cada paso conserva su tipo, su fuente, su actor y su estado. La recomendación es visible como recomendación. La decisión aparece únicamente después de una revisión humana.

## 5. Qué está implementado — 2 minutos

El baseline actual integra:

- Once escalas espaciales.
- Evidencia y fuentes trazables.
- Source HTTP.
- Simulación determinista, sensibilidad y Monte Carlo.
- Distribuciones Monte Carlo `NORMAL`, `UNIFORM` y `TRIANGULAR`.
- Factibilidad con restricciones duras, datos insuficientes y estados desconocidos.
- Frontera Pareto filtrada por factibilidad.
- Generación paramétrica, por patrones y evolutiva.
- Memoria institucional.
- Actores, posiciones y autoridad.
- Ciclos temporales, escenarios y evolución.
- Corpus piloto RNE.
- Design Knowledge Agent.
- Importación IFC de solo lectura.
- Snapshots BIM y GIS.
- GeoJSON y OGC API Features.
- Copiloto Ollama en modo `PREVIEW_ONLY`.
- Guided Interface, Command Bar, Help Center y ocho idiomas.

## 6. La garantía institucional — 90 segundos

**Texto sugerido**

> La arquitectura tiene una frontera constitucional. El sistema puede analizar, comparar, filtrar y proponer. No puede convertir un cálculo en una decisión humana. Una simulación no crea una recomendación. Una recomendación no crea una decisión. Un Copiloto no ejecuta comandos por sí solo.

Los estados más importantes son:

| Estado | Significado directivo |
|---|---|
| `FEASIBLE` | Cumple las restricciones duras evaluadas. |
| `INFEASIBLE` | Al menos una restricción dura fue violada. |
| `INSUFFICIENT_DATA` | No hay información suficiente para concluir. |
| `UNKNOWN` | La evaluación no puede determinarse de forma segura. |
| `HUMAN_REVIEW_REQUIRED` | Una persona debe revisar antes de avanzar. |
| `PREVIEW_ONLY` | Se muestra una propuesta, pero no se ejecuta. |

## 7. Integraciones avanzadas — 90 segundos

SiMS-DeI puede recibir contexto de modelos IFC en modo de solo lectura y trabajar con snapshots GIS en la escala `PARCELA_SITIO`. Los datos externos conservan fuente, hash, vigencia y estado de revisión.

El sistema no afirma que un archivo IFC sea correcto por el solo hecho de poder leerlo. Tampoco afirma que una fuente catastral sea vigente sin expediente. Revit y Archicad nativos requieren sus hosts y SDKs. La exportación BIM requiere una revisión humana aprobada.

El Copiloto local traduce lenguaje natural a SICL. El resultado muestra la intención, el comando canónico y la explicación. El Core sigue validando. El navegador nunca recibe el token de servicio.

## 8. El valor para la organización — 90 segundos

SiMS-DeI aporta cinco beneficios directivos:

1. **Trazabilidad:** cada recomendación puede relacionarse con fuentes, supuestos, evidencias y actores.
2. **Comparabilidad:** alternativas de escalas distintas pueden analizarse con una gramática común.
3. **Control del riesgo:** factibilidad y datos insuficientes se distinguen de una aprobación.
4. **Memoria institucional:** el conocimiento no depende únicamente de conversaciones informales.
5. **Adopción gradual:** Guided Mode permite comenzar sin aprender SICL y Expert Mode permite profundizar.

## 9. Estado de madurez y límites — 90 segundos

El código y la documentación están publicados. El Core tiene 241 pruebas pasando. El frontend tiene 126 pruebas pasando, typecheck correcto y build correcto.

El E2E remoto aún requiere una URL HTTPS real del Core, `SICL_CORE_SERVICE_TOKEN`, volumen persistente y Ollama accesible si se activa el Copiloto. Por transparencia, este estado no se presenta como “producción E2E verificada”.

Los add-ins nativos de Revit y Archicad también quedan condicionados a sus aplicaciones y SDKs. El sistema sí tiene contratos y adaptadores seguros, pero no debe declararse un plugin nativo sin probarlo en el host correspondiente.

## 10. Decisión solicitada a la junta — 60 segundos

Se solicita a la junta:

1. Reconocer SiMS-DeI/SICL como baseline funcional de investigación y operación controlada.
2. Autorizar el despliegue del Core remoto con persistencia y secretos server-side.
3. Autorizar una prueba E2E controlada con datos sintéticos.
4. Definir si la organización necesita integración nativa con Revit o Archicad.
5. Nombrar la autoridad responsable de aprobar fuentes normativas y decisiones.

## 11. Cierre — 30 segundos

> SiMS-DeI no intenta sustituir la decisión profesional. Hace algo más útil: permite que una organización vea cómo llegó a una decisión, qué puede defender, qué necesita revisar y qué debe mejorar. El sistema conserva la memoria; la autoridad permanece humana.

## Preguntas previsibles

### ¿Es una caja negra?

No. El sistema registra fuentes, evidencias, inputs, outputs, estados, versiones y actores. Los modelos de lenguaje solo pueden producir propuestas limitadas y visibles.

### ¿Puede decidir sin una persona?

No dentro del contrato constitucional. HumanReview debe preceder a Decision.

### ¿Puede usar normativa peruana?

Sí, mediante un corpus trazable y estados explícitos. La ingesta no equivale a vigencia jurídica. La promoción requiere revisión humana.

### ¿Está conectado ya a un Core remoto?

El código está preparado y verificado localmente. La declaración de E2E remoto requiere configurar la URL, el token, la persistencia y ejecutar el flujo contra el servicio real.

### ¿Qué ocurre si faltan datos?

El sistema usa `INSUFFICIENT_DATA` o `UNKNOWN`; no transforma la ausencia de información en factibilidad.

## Material de respaldo

- `SIMS_DEI_PROJECT_HANDOVER.md`.
- `SIMS_DEI_FIRST_CONTACT_MANUAL.md`.
- `SIMS_DEI_CURRENT_ARCHITECTURE_v2.11.md`.
- `RFC_015_026_COHERENCE_AUDIT.md`.
- `PRODUCTION_CORE_DEPLOYMENT_MANUAL.md`.

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SICL Core repository"
[2]: https://github.com/YvanCastilloQuezada/sicl-web "SiMS-DeI web repository"
[3]: https://docs.ollama.com/api/openai-compatibility "Ollama API compatibility documentation"
