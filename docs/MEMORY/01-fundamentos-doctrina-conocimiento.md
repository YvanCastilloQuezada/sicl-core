# Auditoría 1 — Fundamentos, doctrina y conocimiento preservado

**Perspectiva:** identidad de ARKI, autoridad, conocimiento, precedentes y estado epistemológico.

## 1. Qué declara el fundamento de Web

El documento `docs/ARKI_AND_SICL_FOUNDATIONS.md` define ARKI como **Sistema de Inteligencia de Diseño Espacial Multiescala** y SICL como **Spatial Intelligence Command Language**. ARKI organiza información espacial, compara alternativas y documenta decisiones; SICL formaliza operaciones verificables sobre el modelo. El frontend es una superficie de interacción y Core es la superficie de dominio y persistencia.

El documento separa explícitamente:
- `Recommendation` de `Decision`.
- `Fact`, `Assumption` y `Preference`.
- Preview de mutación persistida.
- Ayuda de interfaz de sintaxis canónica.
- Autoridad analítica de autoridad humana.

El flujo mínimo declarado es `Project → Preference → Recommendation → HumanReview → Decision → Audit`. Una decisión requiere `HumanReview`, actor y authority. Los eventos de auditoría son append-only.

Fuente: [ARKI_AND_SICL_FOUNDATIONS.md](https://github.com/YvanCastilloQuezada/sicl-web/blob/main/docs/ARKI_AND_SICL_FOUNDATIONS.md), contenido consultado en `main` (SHA de archivo observado: `43f67d53ccd4c8aa0b0ec9d48fa65c1cbe112844`).

## 2. Consecuencia para MEMORY

MEMORY no puede ser un bloc de notas con autoridad implícita. Debe mantener tipos separados para:
- hechos observados y su evidencia;
- declaraciones o recuerdos procedentes de conversación;
- decisiones y aprobaciones humanas;
- supuestos, hipótesis y propuestas;
- ejecuciones de pruebas y recibos;
- estados inferidos o resúmenes generados;
- asuntos desconocidos o no verificados.

No se debe transformar un resumen en hecho, una propuesta en decisión ni una declaración de un registro en evidencia de ejecución. El contenido de continuidad debe indicar fuente, fecha, versión/commit, estado epistemológico y autoridad cuando corresponda.

## 3. Conocimiento fundamental preservado

La búsqueda encontró el conjunto `docs/arki-knowledge/fundamental-research/FKCG-02/` y su manifiesto. El README declara FKCG-02 como **PRESERVED / REVIEWED / NOT CANONIZED / NOT IMPLEMENTED**. Su propósito es conservar investigación fundamental como conocimiento documental; no crea por sí solo un sistema, motor, primitiva, esquema ni capacidad de runtime. El README menciona mapa de responsabilidades A–F, genealogía de fuentes, principios conservados, correcciones, UNKNOWN y brechas de demostración DG-01–DG-05.

Esto significa que MEMORY debe indexar y enlazar el conocimiento preservado sin elevarlo automáticamente a norma ejecutable. El estado de cada concepto debe mantenerse visible.

Fuentes:
- [Knowledge README](https://github.com/YvanCastilloQuezada/sicl-web/blob/main/docs/arki-knowledge/README.md)
- [FKCG-02 manifest](https://github.com/YvanCastilloQuezada/sicl-web/blob/main/docs/arki-knowledge/fundamental-research/FKCG-02/manifest.json)
- [FKCG-02 preservation](https://github.com/YvanCastilloQuezada/sicl-web/blob/main/docs/arki-knowledge/fundamental-research/FKCG-02/FKCG-02_FUNDAMENTAL_KNOWLEDGE_PRESERVATION.md)

## 4. Invariantes que MEMORY debe preservar

1. Una fuente canónica por dominio; los mapas/documentos son proyecciones, no otro Event Store.
2. Ninguna evidencia implica más de lo que realmente demuestra.
3. El estado UNKNOWN no se elimina para producir una apariencia de completitud.
4. Lo congelado o histórico se conserva con su condición; no se reactiva por indexarlo.
5. Una decisión requiere actor y autoridad humanos conforme al contrato de Core.
6. Una memoria puede ayudar a recuperar contexto, pero no decide ni ejecuta cambios canónicos por sí sola.
7. La procedencia debe ser navegable hasta el artefacto/commit/registro de origen.
8. Un conocimiento recuperado puede ser candidato, pero su promoción a conocimiento canónico requiere la compuerta humana pertinente.

El inventario de activos congelados e ideas/decisiones debe revisarse como fuente primaria adicional antes de declarar cerrado este dictamen:
- `docs/arki-inventory/ARKI_FROZEN_AND_HISTORICAL_ASSETS.md`
- `docs/arki-inventory/ARKI_IDEA_AND_DECISION_INVENTORY.md`

## 5. Cómics, viñetas y fundamentos visuales: estado de búsqueda

Las búsquedas iniciales en el código de `sicl-web` por `comic`, `cómic`, `historieta`, `storyboard` y `viñeta` no devolvieron resultados. Tampoco se localizaron cómics con la búsqueda inicial de la biblioteca de archivos consultada anteriormente. Eso solo permite afirmar **NO LOCALIZADOS EN LAS FUENTES EXAMINADAS**, no que hayan sido eliminados ni que no existan.

Para completar el requisito hace falta identificar dónde se guardaron: otro repositorio, carpeta de Drive/Library, conversación, imágenes adjuntas u otro sistema. No se debe inventar su contenido.

## 6. Conclusión y pendientes

La doctrina de ARKI exige que MEMORY sea una capa de continuidad trazable y no una autoridad nueva. El fundamento de Web y la memoria institucional de Core tienen fronteras compatibles en principio, pero la auditoría no demuestra aún una integración funcional extremo a extremo.

**Pendiente:** inventariar todos los documentos de fundamentos, los conceptos congelados/históricos, los manifests y los cómics originales; extraer el estado de cada elemento y sus relaciones sin cambiar sus estados.


## 6. Paquete preservado de conocimiento — verificación concreta

En sicl-web/main, docs/arki-knowledge/README.md y package-manifest-v1.0.json declaran un paquete documental v1.0 de 13 libros Excel preservados, con SHA-256 por archivo. La ingesta automática en runtime está deshabilitada; no se publica ni activa FFO automáticamente. El paquete conserva estas familias:

1. Constitución/decisiones.
2. Investigación/hallazgos y procedencia.
3. Historia/evolución.
4. Experimentos/evidencia A–AV.
5. Capacidades/madurez.
6. UNKNOWN, brechas y preguntas abiertas.
7. Arquitectura FROZEN/FUTURE (FFO/V1–V24).
8. Casos/precedentes arquitectónicos.
9. Fuentes/biblioteca arquitectónica.
10. Tipologías.
11. Ideas no implementadas.
12. Libro maestro de conocimiento arquitectónico.
13. Formato de investigación de IA externa.

Reglas expresas del paquete: RESEARCH ≠ CANONICAL KNOWLEDGE ≠ IMPLEMENTATION; HISTORICAL ≠ CURRENT; DOCUMENTED ≠ AUTHORIZED ≠ IMPLEMENTED ≠ INTEGRATED ≠ DEPLOYED; UNKNOWN BEFORE INVENTING. Los originales no deben reescribirse y el índice/corpus derivado no sustituye a los libros fuente.

Fuentes consultadas en Web main:
- [Índice del paquete](https://github.com/YvanCastilloQuezada/sicl-web/blob/main/docs/arki-knowledge/README.md) — blob SHA 449ccbc9eba7a329453a589030c10263b57de5a6.
- [Manifest v1.0](https://github.com/YvanCastilloQuezada/sicl-web/blob/main/docs/arki-knowledge/package-manifest-v1.0.json) — blob SHA 8a33b3cbde6b9d7d9da6476d523f2c2b12b6aeb8.
- [Inventario FROZEN/histórico, Delta 513](https://github.com/YvanCastilloQuezada/sicl-web/blob/main/docs/arki-inventory/ARKI_FROZEN_AND_HISTORICAL_ASSETS.md) — blob SHA 75efe4f6d2748336c932c6a6b204d6c5ec57b6bd.
- [Inventario de ideas/decisiones, Delta 515](https://github.com/YvanCastilloQuezada/sicl-web/blob/main/docs/arki-inventory/ARKI_IDEA_AND_DECISION_INVENTORY.md) — blob SHA 9e629f634a4912b2de98598b0c062b6b0ff70552. Atención: ese documento declara una base histórica main@a565a909... de septiembre, no el HEAD actual; usarlo como genealogía/inventario fechado, no como fotografía actual del sistema.

El inventario FROZEN insiste en que FROZEN significa preservado como evidencia/baseline, no motor activo. Entre otros ejemplos, clasifica UPAO-001 como fixture sintético y limita las afirmaciones sobre D6.2-M/D6.3-G a sus alcances conceptuales. Esto coincide con la regla de no convertir una etiqueta histórica en capacidad actual.

## 7. Cómics, historietas y storyboards — resultado de búsqueda

Se consultó el buscador de código de GitHub en las ramas por defecto de sicl-web, sicl-core y arki-acs para los términos comic, cómic, historieta, viñeta y storyboard. No se devolvieron resultados para esas consultas.

Esto no prueba que los cómics no existan. La búsqueda de código no cubre necesariamente archivos binarios, adjuntos, otras ramas ni archivos de conversaciones externas. Su ubicación y el inventario completo de cómics siguen como UNKNOWN / PENDIENTE DE LOCALIZACIÓN. No se fabricará un catálogo ni se marcará la revisión como completa hasta localizar las fuentes.


### Comprobación adicional por árbol Git (ramas por defecto)

Se inspeccionó el árbol recursivo de Git de main en los tres repositorios: sicl-web (1,602 rutas), sicl-core (419) y arki-acs (298); las respuestas no estaban truncadas. No hubo nombres de ruta que coincidieran con comic/cómic/historieta/viñeta/storyboard/cartoon/graphic novel. Sí existen archivos visuales y PDFs generales (Web: 180 rutas con extensiones visuales/documentales; Core: 14; ACS: 1), pero sus extensiones/nombres no bastan para clasificar su contenido como cómics. El contenido binario no se ha inspeccionado página por página y esta comprobación solo cubre main, no todas las ramas.

**Estado preciso:** búsqueda de nombres en main sin coincidencias; inventario de cómics completo todavía no demostrado. Próximo paso necesario: localizar carpeta, ZIP, PDF o adjunto fuente fuera de esas rutas, o inspeccionar visualmente los documentos potencialmente relevantes que el usuario identifique.
