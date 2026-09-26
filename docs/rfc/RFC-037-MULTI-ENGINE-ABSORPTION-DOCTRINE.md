# RFC-037 — Doctrina de Absorción Multi-Motor (DAM)

**Estado:** FUNDACIONAL
**Prioridad:** Máxima
**Ámbito:** Todas las ramas de SiMS-DeI / ARKI
**Fecha:** 26 de septiembre de 2026

## 1. Propósito

ARKI debe aprender de múltiples motores especializados, extraer lo mejor de cada uno y sintetizar un motor propio. No debe convertirse en un wrapper ni depender de un motor externo como servicio permanente de producción.

Los motores externos son maestros temporales. Se utilizan para producir ground truth, estudiar algoritmos, comparar resultados y validar la calidad de ARKI. La producción final debe ejecutarse con motores propios de ARKI.

> El motor externo enseña. ARKI aprende, replica, mejora y finalmente trabaja por sí mismo.

## 2. Seis principios constitucionales DAM

### Principio 1 — Todo motor es maestro, no dependencia

Ningún motor externo se integra como dependencia permanente de producción. Puede ser estudiado, ejecutado en un entorno de aprendizaje y utilizado como oráculo de comparación, pero el runtime final debe operar con el motor propio de ARKI.

### Principio 2 — Ningún motor se descarta por imperfecto

Cada motor puede resolver mejor una parte del problema. Las limitaciones de un motor no justifican descartar su conocimiento útil. ARKI debe separar capacidades, medir resultados y conservar lo que aporte valor.

### Principio 3 — Todo conocimiento tiene fuente

Cada regla aprendida debe registrar el motor, fixture, versión, prueba o revisión humana que la originó. Una regla sin fuente queda como hipótesis y no puede incorporarse al conocimiento graduado.

### Principio 4 — La síntesis pertenece a ARKI

El motor propio no será una copia ni una suma mecánica de motores externos. ARKI debe combinar, mejorar y superar las técnicas individuales. Las decisiones de síntesis deben documentarse como conocimiento propio.

### Principio 5 — Solo el motor propio corre en producción

Los maestros pueden existir en entrenamiento, benchmarking y validación. En runtime, ARKI debe dibujar, calcular, simular, optimizar, analizar y decidir mediante sus propios motores nativos.

### Principio 6 — Vigilancia y depuración continua

Toda rama que haya absorbido conocimiento de maestros externos debe ejecutar una Vigilancia Semanal de Maestros (VSM). El ciclo es:

```text
DETECTAR → EVALUAR → ABSORBER | DESCARTAR → PURGAR → REGISTRAR
```

Las nuevas versiones no se adoptan automáticamente. Una mejora relevante debe reproducir el ground truth y superar o igualar la versión anterior. Una regresión se conserva documentada y no se adopta. Si una regla propia se demuestra incorrecta, se elimina del código, los datos y los tests relacionados; no se deja comentada ni como código muerto. El procedimiento completo está en [`RFC-037.1-WEEKLY-MASTER-SURVEILLANCE.md`](RFC-037.1-WEEKLY-MASTER-SURVEILLANCE.md).

## 3. Ramas cubiertas

DAM aplica, como mínimo, a:

- Dibujo arquitectónico.
- Estructuras.
- Hidráulica.
- Dinámica de fluidos.
- Geología y geotecnia.
- Energía y building physics.
- Acústica.
- Monte Carlo y simulación.
- Optimización.
- GIS.
- BIM.
- LCA y carbono.
- Costos y presupuestos.
- Programación arquitectónica.
- Análisis de sitio.
- Cualquier nueva rama que incorpore motores externos.

El mapa de ramas y motores está en [`RFC-037-RAMAS-Y-MOTORES.md`](RFC-037-RAMAS-Y-MOTORES.md).

## 4. Metodología DAM por rama

Cada rama debe atravesar las siguientes fases, en orden:

### Fase A — Disponibilidad y estudio

Inventariar motores, versiones, licencias, entradas, salidas y capacidades. Probar los motores disponibles sobre un fixture común. Los motores no disponibles se registran como `INSUFFICIENT_DATA`.

### Fase B — Ground truth multi-maestro

Generar el mismo problema con cada maestro disponible. Mantener constantes la geometría de entrada, unidades, condiciones, hipótesis y criterios de salida. Guardar archivos, hashes, logs y mediciones.

### Fase C — Extracción de conocimiento con fuente

Identificar qué hace cada maestro, por qué funciona, qué limitaciones tiene y qué reglas pueden generalizarse. Toda regla debe incluir fuente, evidencia, confianza y alcance.

### Fase D — Síntesis en motor propio

Implementar un motor nativo de ARKI que combine las mejores reglas. El motor propio debe leer los datos necesarios, pero no llamar al maestro externo para ejecutar el trabajo de producción.

### Fase E — Graduación

Comparar el motor propio contra los maestros y fixtures. La rama se gradúa únicamente cuando el resultado es técnicamente válido, reproducible, trazable y aceptado por revisión humana, sin maestros externos en runtime.

## 5. Criterios de graduación por rama

Una rama DAM se gradúa cuando cumple todos estos criterios:

1. Existe inventario de maestros y disponibilidad.
2. Se generaron ground truths comparables con los maestros disponibles.
3. Se documentaron las fortalezas y limitaciones de cada maestro.
4. Cada regla interna tiene fuente y evidencia.
5. Existe un motor propio de ARKI.
6. Existen tests que demuestran independencia de runtime.
7. Las salidas del motor propio son reproducibles.
8. Las salidas son técnicamente comparables o superiores al maestro.
9. Se declara `INSUFFICIENT_DATA` donde corresponda.
10. La revisión humana aprueba la salida final.

No se permite declarar graduación por la mera existencia de archivos o por tests de presencia.

## 6. Separación de entornos

### Entorno de aprendizaje

Puede contener adaptadores, scripts y dependencias de los maestros externos:

```text
training/
learning/
benchmarks/
fixtures/
```

### Runtime de producción

Debe contener únicamente motores propios de ARKI y las bibliotecas de lectura estrictamente necesarias. Un maestro externo no debe ser importado ni ejecutado desde un flujo normal de producción.

## 7. Prohibiciones

- No convertir ARKI en wrapper de un motor.
- No dejar motores externos como servicios permanentes de producción.
- No copiar una salida 1:1 sin entenderla y sintetizarla.
- No declarar reglas sin fuente.
- No declarar éxito sin ground truth y comparación.
- No inventar evaluaciones de motores no probados.
- No iniciar más de dos ramas DAM en paralelo.
- No modificar el Core determinista sin autorización específica.
- No crear Decisions automáticamente.
- No mezclar namespaces entre ramas.

## 8. Estado actual

| Rama | Estado DAM |
|---|---|
| Dibujo arquitectónico | Fase 1 iniciada; solo IfcOpenShell Draw disponible |
| BIM | Parcialmente iniciado |
| Estructuras | No iniciado |
| Hidráulica | No iniciado |
| Demás ramas | No iniciado |

La continuación inmediata será completar la disponibilidad del aprendizaje de dibujo y documentar los bloqueos antes de iniciar otra rama.

## 9. Invariantes globales

```text
CORE_CHANGED = NO
DECISION_CREATED = NO
EXTERNAL_ENGINE_RUNTIME_DEPENDENCY = NO
KNOWLEDGE_WITHOUT_SOURCE = FORBIDDEN
UNSUPPORTED_ENGINE_CLAIMS = FORBIDDEN
MAX_PARALLEL_DAM_BRANCHES = 2
WEEKLY_MASTER_SURVEILLANCE = REQUIRED
AUTO_ABSORPTION = FORBIDDEN
INCORRECT_RULES_MUST_BE_PURGED = TRUE
```
