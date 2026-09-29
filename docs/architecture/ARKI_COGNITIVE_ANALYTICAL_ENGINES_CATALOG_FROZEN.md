# ARKI — CATÁLOGO CONGELADO DE MOTORES COGNITIVOS Y ANALÍTICOS

**Estado:** FROZEN / NOT_AUTHORIZED_FOR_IMPLEMENTATION  
**Fase:** [9]+ INTEGRACIÓN DE MOTORES COGNITIVOS  
**Documento padre:** `ARKI_MOTOR_INTEGRATION_DESIGN_FROZEN.md`  
**Naturaleza:** Anexo del sistema de Motores. No es una idea independiente ni backlog inmediato.

## Propósito

Catálogo disciplinario de motores que ARKI podrá invocar, observar y, cuando exista evidencia procedural suficiente, internalizar para apoyar el futuro **Super Expediente Técnico**.

## 1. Ambientales y bioclimáticos

- `SolarExposureEngine`: soleamiento, trayectoria solar y sombras. Referencias: pysolar / Ladybug Tools.
- `BioclimaticEngine`: confort térmico pasivo, ventilación y ganancias/pérdidas. Referencias: EnergyPlus / Open-Meteo.
- `WindAerodynamicsEngine`: presión de viento y confort eólico. Referencias: OpenFOAM / SimScale.
- `AcousticEngine`: aislamiento y reverberación. Referencias: CATT-Acoustic / Odeon.

## 2. Estructurales y geotécnicos

- `StructuralAnalysisEngine`: esfuerzos, deflexiones y predimensionamiento. Referencias: OpenSees / SAP2000 / MDSolids.
- `GeotechnicalEngine`: capacidad portante, asentamientos y selección preliminar de cimentación.
- `SeismicRiskEngine`: detección de irregularidades y riesgos de configuración estructural.

## 3. Seguridad y riesgo

- `EvacuationEngine`: rutas, distancias y cuellos de botella.
- `FireSafetyEngine`: carga de fuego, resistencia y compartimentación.
- `AccessibilityEngine`: comprobación geométrica de accesibilidad.

## 4. Económicos y de gestión

- `CostEstimationEngine`: metrados y presupuesto desde D-2.
- `MaintenancePlanEngine`: mantenimiento según vida útil e inspecciones.
- `SchedulingEngine`: secuencia, duración y ruta crítica de obra.

## 5. Urbanos y de impacto

- `UrbanRegulationEngine`: parámetros urbanísticos y zonificación.
- `LifeCycleAssessmentEngine`: huella de carbono e impacto ambiental.
- `HydraulicEngine`: dimensionamiento preliminar de redes y almacenamiento de agua.

## 6. Coordinación y representación

- `MEPCoordinationEngine`: interferencias y prioridades de coordinación.
- `DrawingValidationEngine`: consistencia entre planos, cotas, ejes, niveles y representación.

## Protocolo común

1. ARKI envía `EngineInput` con snapshot D-2 y contexto.
2. `KnowledgeExtractor` analiza la respuesta.
3. Motor transparente: permite observar fórmulas, pasos e invariantes.
4. Motor opaco: solo permite registrar resultado y dependencia; no autoriza afirmar conocimiento procedural interno.
5. `KnowledgeConsolidator` contrasta lo aprendido con el canon.
6. `LearningLedger` registra conocimiento procedural con trazabilidad.
7. La ejecución interna sin motor solo puede ocurrir después de validación suficiente y dentro de límites explícitos.

## Relación con el Super Expediente Técnico

```text
SUPER EXPEDIENTE TÉCNICO ARKI
        ↓
requiere análisis especializados
        ↓
MOTORES COGNITIVOS Y ANALÍTICOS
        ↓
observación + extracción + validación
        ↓
CONOCIMIENTO PROCEDURAL TRAZABLE
        ↓
mayor autonomía de ARKI
```

## Reglas congeladas

- UNKNOWN se preserva.
- D-2 continúa siendo estado canónico.
- Los motores no obtienen autoridad para mutar D-2 por existir.
- Learning Ledger no sustituye Event Store ni DerivationLedger.
- Resultado correcto no equivale a procedimiento comprendido.
- Motor opaco no equivale a conocimiento internalizado.
- Contradicciones normativas requieren tratamiento explícito y Human Authority.
- No activar ni implementar antes de cumplir las condiciones del documento padre.

## Activación

Este catálogo pertenece íntegramente a **[9]+**.

No implementar hasta:
- cierre de [6];
- cierre de [7];
- cierre de [8];
- cumplimiento de las condiciones técnicas del documento padre;
- contrato V1 específico del primer motor;
- auditoría y congelamiento del contrato;
- autorización escrita del Product Owner.

## Custodia

Este archivo debe permanecer junto a:

`docs/architecture/ARKI_MOTOR_INTEGRATION_DESIGN_FROZEN.md`

Ambos constituyen un único paquete documental congelado:

**ARKI — INTEGRACIÓN DE MOTORES COGNITIVOS [9]+**

No constituye autorización de implementación.
