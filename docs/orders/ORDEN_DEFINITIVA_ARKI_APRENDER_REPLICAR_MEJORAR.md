# ORDEN DEFINITIVA — ARKI APRENDE, REPLICA Y MEJORA EL DIBUJO ARQUITECTÓNICO

**Fecha:** 26 de septiembre de 2026  
**Autoridad:** Product Owner  
**Sistema:** ARKI / SiMS-DeI  
**Prioridad:** Máxima

---

## 1. Visión definitiva

ARKI no debe ser un wrapper de IfcOpenShell, FreeCAD, BlenderBIM, Bonsai, Rhino, AutoCAD ni de ningún otro motor externo.

Los motores externos serán **maestros temporales**. Se podrán utilizar para:

1. Generar resultados profesionales de referencia.
2. Comparar geometría, proyección, ocultamiento, composición y simbología.
3. Extraer reglas, patrones y conocimiento.
4. Validar la calidad de las salidas propias de ARKI.

Pero los motores externos **no deben formar parte del runtime normal de ARKI**.

La meta es que ARKI pueda dibujar de forma nativa, rápida y natural, sin preguntar al motor externo cómo dibujar cada muro, puerta, ventana o escalera.

> El dibujo arquitectónico debe convertirse en una capacidad interna de ARKI: rápida, consistente, automática e instintiva.

---

## 2. Principio constitucional

La arquitectura del sistema debe seguir esta regla:

```text
MOTOR EXTERNO = MAESTRO TEMPORAL DE APRENDIZAJE
ARKI          = MOTOR NATIVO FINAL DE PRODUCCIÓN
```

Los motores pueden existir en herramientas de entrenamiento, comparación y validación, pero nunca deben ser una dependencia obligatoria de producción.

---

## 3. Los tres estados del aprendizaje

ARKI debe avanzar secuencialmente por tres fases:

```text
APRENDER  →  REPLICAR  →  MEJORAR
```

No se debe declarar una fase completada por presencia de archivos o por tests superficiales. Cada fase requiere evidencia visual y pruebas de comportamiento.

---

# FASE 1 — APRENDER DEL MAESTRO

## 1.1 Objetivo

Usar todos los motores disponibles como maestros temporales para observar cómo producen documentación arquitectónica profesional.

Se deben evaluar, cuando estén disponibles:

- IfcOpenShell Draw.
- FreeCAD TechDraw.
- BlenderBIM / BonsaiBIM.
- Otros motores CAD o BIM compatibles autorizados.

No se debe asumir que un solo motor es la verdad absoluta. Cada motor debe aportar conocimiento específico.

## 1.2 Matriz de aprendizaje

Para cada motor se debe registrar:

| Área | Pregunta a responder |
|---|---|
| Proyección | ¿Cómo convierte geometría 3D en líneas 2D? |
| Corte | ¿Cómo intersecta muros, losas y escaleras con un plano? |
| Oclusión | ¿Qué oculta y qué deja visible? |
| Profundidad | ¿Qué peso asigna a elementos cortados, vistos y ocultos? |
| Unificación | ¿Cómo elimina líneas duplicadas y cierra esquinas? |
| Muros | ¿Cómo representa espesores y materiales? |
| Puertas | ¿Cómo calcula hoja, marco, arco y eje? |
| Ventanas | ¿Cómo genera marcos, vidrios y líneas paralelas? |
| Escaleras | ¿Cómo calcula peldaños, flecha y línea de corte? |
| Cotas | ¿Cómo organiza anillos, extensiones y textos? |
| NPT | ¿Cómo ubica símbolos y etiquetas de nivel? |
| Cajetín | ¿Cómo organiza información gráfica y normativa? |
| Mobiliario | ¿Cómo representa camas, mesas, sanitarios y cocina? |
| Vegetación | ¿Cómo diferencia árboles, arbustos y áreas verdes? |
| Exportación | ¿Cómo conserva escala, vectores, tipografías y grosores? |

## 1.3 Fixture maestro

El fixture principal será:

```text
docs/reference/PROY_FERNANDEZ_ROJAS.pdf
```

La página A-01 se utilizará como referencia principal de:

- Jerarquía gráfica.
- Plantas arquitectónicas.
- Cotas en doble anillo.
- Ejes.
- Muros.
- Puertas y ventanas.
- Escaleras.
- Mobiliario.
- Vegetación.
- Cajetín.

También podrán incorporarse fixtures adicionales para cortes, elevaciones, cubiertas y detalles constructivos.

## 1.4 Entregables de la Fase 1

Crear:

```text
docs/learning/engines/
├── ifcopenshell-draw.md
├── freecad-techdraw.md
├── blenderbim-bonsai.md
├── comparison-matrix.md
└── master-observations.md
```

Cada documento debe incluir:

- Motor y versión.
- Entrada utilizada.
- Salidas generadas.
- Capturas o referencias visuales.
- Ventajas.
- Limitaciones.
- Reglas observadas.
- Qué conocimiento puede internalizar ARKI.

## 1.5 Graduación de la Fase 1

La fase se completa cuando:

- Cada motor disponible fue probado o declarado no disponible con evidencia.
- Se identificaron reglas comunes entre motores.
- Se identificaron diferencias y decisiones de diseño.
- Se documentó qué comportamiento debe aprender ARKI.
- No se incorporó ningún motor como dependencia permanente de runtime.

---

# FASE 2 — REPLICAR CON EL MOTOR NATIVO DE ARKI

## 2.1 Objetivo

Implementar un motor propio que replique el conocimiento extraído de los maestros sin llamar a sus APIs de dibujo durante la producción.

ARKI podrá leer geometría IFC mediante IfcOpenShell, pero la proyección, el corte, la oclusión y la representación gráfica deben ser algoritmos propios.

## 2.2 Motor nativo

Crear:

```text
src/sicl/drawing/arki_projector.py
```

El módulo debe implementar:

1. Corte horizontal a una altura configurable.
2. Corte vertical por eje X o Y.
3. Proyección ortográfica frontal.
4. Proyección de cubierta.
5. Oclusión delante y detrás del plano de corte.
6. Clasificación de elementos cortados, vistos y ocultos.
7. Unificación de segmentos contiguos.
8. Eliminación de líneas duplicadas.
9. Cierre automático de esquinas.
10. Aplicación de espesores según profundidad.
11. Aplicación de achurados según material.
12. Generación de puertas, ventanas y escaleras.
13. Generación de cotas y niveles.
14. Composición de lámina y cajetín.

## 2.3 Regla de no dependencia

El motor nativo no debe importar ni llamar:

```python
ifcopenshell.draw
FreeCAD
TechDraw
bpy
BlenderBIM
Bonsai
```

Se permite utilizar IfcOpenShell únicamente para:

- Abrir IFC.
- Leer entidades.
- Leer placements.
- Leer representaciones geométricas.
- Leer materiales.
- Leer propiedades.

La transformación de geometría 3D a documentación 2D debe pertenecer a ARKI.

## 2.4 Reglas internas aprendidas

Crear:

```text
data/drawing_knowledge/arki_learned_rules.json
```

El archivo debe codificar, como mínimo:

- Muros cortados y vistos.
- Cierre de esquinas.
- Achurado por material.
- Puertas y arcos.
- Ventanas y marcos.
- Escaleras y flechas.
- Doble anillo de cotas.
- Colocación de NPT.
- Pesos de línea.
- Oclusión.
- Unificación de segmentos.
- Mobiliario.
- Vegetación.
- Cajetín.

Cada regla debe contener:

```json
{
  "rule": "nombre_de_la_regla",
  "source": "fixture_or_engine_observation",
  "why": "explicación arquitectónica",
  "algorithm": "cómo la implementa ARKI",
  "confidence": 0.0
}
```

## 2.5 Graduación de la Fase 2

La fase se completa cuando:

- ARKI genera planta, corte, elevación y techo sin usar motores externos para dibujar.
- Las cuatro vistas son diferentes.
- El IFC se utiliza solo como fuente de geometría.
- Los tests verifican que no existen imports de motores externos en el runtime nativo.
- Las salidas se comparan visualmente con las del maestro.
- Las reglas aprendidas están documentadas y versionadas.

---

# FASE 3 — MEJORAR Y GRADUARSE

## 3.1 Objetivo

ARKI debe dejar de limitarse a copiar al maestro. Debe producir documentación mejor, más consistente, más rápida y más adaptable.

La mejora debe conservar las normas arquitectónicas y no alterar arbitrariamente la información del proyecto.

## 3.2 Capacidades de mejora

ARKI debe poder:

- Detectar colisiones entre cotas y textos.
- Elegir automáticamente el mejor anillo de cotas.
- Ajustar símbolos sin superponer ambientes.
- Cerrar esquinas con continuidad de achurado.
- Diferenciar profundidad mediante pesos de línea.
- Simplificar geometría sin perder información.
- Mantener escala y legibilidad.
- Adaptar el cajetín al formato requerido.
- Reconocer cuándo faltan datos.
- Usar `INSUFFICIENT_DATA` en lugar de inventar.
- Comparar su salida contra fixtures maestros.
- Medir similitud gráfica y legibilidad.
- Aprender de revisiones humanas aprobadas.

## 3.3 Aprendizaje de revisión humana

Toda observación de un arquitecto debe registrarse como conocimiento revisable:

```text
docs/learning/reviews/
```

Cada revisión debe incluir:

- Archivo revisado.
- Fecha.
- Actor.
- Observación.
- Regla afectada.
- Corrección propuesta.
- Decisión de incorporación.
- Evidencia antes/después.

ARKI no debe cambiar sus reglas automáticamente sin registrar la revisión y mantener trazabilidad.

## 3.4 Graduación final

ARKI se considera graduado cuando:

- Puede dibujar sin `ifcopenshell.draw`, FreeCAD, BlenderBIM o cualquier motor CAD externo en runtime.
- Produce láminas técnicamente coherentes.
- Mantiene pesos, escalas, cotas, NPT, símbolos y cajetines.
- Sus vistas son claramente distintas según el tipo de proyección.
- Puede explicar las reglas que utiliza.
- Puede mejorar una salida sin inventar datos.
- Un arquitecto puede revisar y aprobar el resultado.

---

# 4. Arquitectura de dependencias

## 4.1 Entorno de aprendizaje

Los motores externos pueden utilizarse aquí:

```text
training/
comparison/
fixtures/
benchmarks/
```

## 4.2 Runtime de ARKI

El runtime de producción debe depender únicamente de:

- Núcleo determinista de ARKI.
- Lectura IFC.
- Motor nativo `arki_projector.py`.
- DrawingRuleSet.
- Reglas aprendidas versionadas.
- Exportadores propios.

## 4.3 Prohibición

Ningún módulo de producción debe ejecutar un motor externo para completar una solicitud normal de planos.

Si se necesita un maestro externo para una nueva investigación, debe ejecutarse explícitamente en modo de aprendizaje y quedar fuera del flujo de producción.

---

# 5. Namespaces

Los namespaces deben mantenerse separados:

```text
/DRAWING      Planos técnicos
/PRESENTATION Láminas de presentación
/CONCEPTUAL   Anteproyectos conceptuales
/LEARNING     Aprendizaje y comparación de motores
```

El conocimiento extraído puede alimentar `/DRAWING`, pero los artefactos de aprendizaje no deben confundirse con entregables técnicos.

---

# 6. Invariantes constitucionales

1. ARKI no es un wrapper de ningún motor externo.
2. Los motores externos son maestros temporales.
3. El runtime normal no depende de motores CAD externos.
4. El conocimiento aprendido debe quedar documentado.
5. No se crean Decisions automáticamente.
6. No se modifica el Core determinista.
7. No se modifica el BIM snapshot durante la proyección.
8. No se inventan datos.
9. Las salidas conceptuales no se presentan como planos técnicos.
10. Toda graduación requiere comparación visual y revisión humana.
11. No se declara éxito por presencia de archivos solamente.
12. Cada cambio debe tener tests, evidencia y trazabilidad.

---

# 7. Tests mínimos

Crear y mantener tests para:

- Aprendizaje de cada motor disponible.
- Carga de reglas aprendidas.
- Proyección horizontal.
- Proyección vertical.
- Oclusión.
- Unificación de segmentos.
- Cierre de esquinas.
- Muros con espesores reales.
- Puertas con arco, hoja y eje.
- Ventanas con líneas paralelas y marco.
- Escaleras con peldaños y flecha.
- Cotas en doble anillo.
- NPT triangulares.
- Mobiliario.
- Vegetación.
- Diferenciación entre planta, corte, elevación y techo.
- Ausencia de imports externos en runtime.
- No creación automática de Decisions.
- No modificación del BIM snapshot.
- Separación de namespaces.

---

# 8. Entregables finales

```text
docs/rfc/RFC-030.1-ARKI-DRAWING-INTELLIGENCE.md
data/drawing_knowledge/arki_learned_rules.json
src/sicl/drawing/arki_projector.py
src/sicl/drawing/arki_geometry.py
src/sicl/drawing/arki_occlusion.py
src/sicl/drawing/arki_symbols.py
src/sicl/drawing/arki_dimensions.py
tests/test_arki_projector.py
tests/test_arki_no_external_runtime.py
docs/reference/PHASE1_MASTER_OUTPUT/
docs/reference/PHASE2_LEARNED_KNOWLEDGE/
docs/reference/PHASE3_ARKI_OUTPUT/
```

---

# 9. Reporte obligatorio por fase

Antes de avanzar de una fase a la siguiente se debe reportar:

- Estado de la fase.
- Motores utilizados.
- Archivos creados.
- Tests ejecutados.
- Comparación visual.
- Hashes de las salidas.
- Reglas aprendidas.
- Limitaciones.
- Bloqueadores.
- Confirmación de `CORE_CHANGED`.
- Confirmación de `DECISION_CREATED`.
- Confirmación de independencia del runtime.

Si una fase falla, se debe detener el proceso y reportar el bloqueo. No se debe saltar automáticamente a la siguiente fase.

---

# 10. Orden de ejecución

Ejecutar en este orden:

1. Inventariar motores disponibles.
2. Probar cada maestro temporal.
3. Analizar fixtures profesionales.
4. Documentar las reglas observadas.
5. Crear `arki_learned_rules.json`.
6. Implementar el motor nativo de ARKI.
7. Ejecutar tests de independencia.
8. Generar salidas propias.
9. Comparar contra los maestros.
10. Registrar revisiones humanas.
11. Mejorar reglas y algoritmos.
12. Declarar graduación solo con evidencia visual y aprobación humana.

> Objetivo final: que ARKI no piense “qué motor debo llamar”, sino que simplemente sepa dibujar.
