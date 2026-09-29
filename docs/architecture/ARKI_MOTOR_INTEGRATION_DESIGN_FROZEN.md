# ARKI — DISEÑO DE INTEGRACIÓN DE MOTORES COGNITIVOS
## Documento de Diseño Congelado (Frozen Design Document)

**Estado**: `FROZEN / NOT_AUTHORIZED_FOR_IMPLEMENTATION`  
**Fase objetivo**: `[9]+ INTEGRACIÓN DE MOTORES COGNITIVOS`  
**Fecha de congelamiento**: 2026-09-30  
**Autoridad de diseño**: Product Owner (Yvan Castillo) + Equipo Rojo (Qwen)  
**Filosofía rectora**: *"ARKI usa motores como maestros temporales. Lee la teoría, observa la práctica, extrae el proceso y lo internaliza en su ADN. Después descarta el motor. El conocimiento queda."*  
**Baseline de referencia declarado en el documento congelado**:
- `sicl-core/main` = `71e72bb1abfb217bf4854f464ae443764281f469`
- `sicl-web/main` = `69ff2ad2f7537dd5b752ec8dce90f7c27d5ec3f6`

---

## ⛔ CONDICIONES DE ACTIVACIÓN (NO IMPLEMENTAR ANTES DE)

Este documento **NO DEBE IMPLEMENTARSE** hasta que se cumplan **TODAS** las siguientes condiciones.

### Pre-requisitos de fase

- [ ] **FASE [6] CERRADA**: `Controlled Promotion Orchestration` completa y mergeada (incluye E-R6b, Contract V1, implementación en Core, migración, merge de PR #30 en Web).
- [ ] **FASE [7] CERRADA**: `Representación desde D-2` funcional (ARE/ARKI-DRAW integrados y derivando correctamente desde D-2).
- [ ] **FASE [8] CERRADA**: `Ciclos completos de feedback y backtracking` operativos (mutación con trazabilidad, genealogía preservada).

### Pre-requisitos técnicos

- [ ] **D-2 estable**: Único estado canónico consolidado y probado E2E.
- [ ] **Microcaso E2E completo**: `Encargo → Brain → D6.2 → Parti → D6.3 → Developer → Human Review → D-2 → Representación`.
- [ ] **UNKNOWN manejado correctamente** en toda la cadena.
- [ ] **Human Authority funcionando** en promoción.
- [ ] **CASE-001 como fixture downstream** validado.
- [ ] **CI verde** en `sicl-core` y `sicl-web` en el momento de la activación.

### Pre-requisitos de infraestructura

- [ ] **Event Store append-only** operativo y probado.
- [ ] **DerivationLedger (H-001)** estable y no contaminado con relaciones arquitectónicas.
- [ ] **DesignKnowledgeBase** estructurada para consultas por fórmulas/dominio.
- [ ] **Hardware local** con GPUs NVIDIA (CUDA) disponibles para motores de IA.

### Autorización explícita

- [ ] **Product Owner (Yvan) autoriza** la activación con orden escrita.
- [ ] **Equipo Rojo valida** que las condiciones se cumplen.
- [ ] **Contrato V1 del primer motor específico** redactado, auditado y congelado (ej. `SolarExposureEngine`).

**Si alguna condición no se cumple → NO IMPLEMENTAR. El documento permanece FROZEN.**

---

## 🎯 PROPÓSITO DEL SISTEMA

ARKI debe poder:

1. **Invocar CUALQUIER motor externo** (EnergyPlus, Radiance, pysolar, motores estructurales, CFD, geotermia, acústica, etc.).
2. **Aprender de él** pasándole muchos casos de prueba.
3. **Extraer el conocimiento procedimental** (fórmulas, pasos, invariantes, condiciones de aplicación).
4. **Internalizar ese conocimiento** en su ADN simbólico (`LearningLedger`).
5. **Descartar el motor** una vez que el conocimiento está internalizado.
6. **Revisar periódicamente** si hay nuevos motores o actualizaciones.
7. **Aplicar el conocimiento internalizado** sin invocar el motor para casos estándar.

### Principio clave

ARKI aprende **PROCESOS**, no resultados. No memoriza que "2+2=4", entiende POR QUÉ 2+2=4.

---

## 🏗️ ARQUITECTURA GENERAL

```text
1. MOTOR EXTERNO
   ↓
2. ENGINE ADAPTER
   ↓
3. KNOWLEDGE EXTRACTOR
   ↓
4. KNOWLEDGE CONSOLIDATOR
   ↓
5. LEARNING LEDGER
   ↓
6. MAESTRO-TUTOR
   ↓
7. EVALUADOR-REDTEAM
   ↓
8. ENGINE REFRESH
```

1. **Motor externo**: caja negra o transparente; devuelve resultados y, opcionalmente, pasos.
2. **Engine Adapter**: normaliza salida; extrae metadatos, fórmulas, pasos y dependencias; fingerprints de input/output.
3. **Knowledge Extractor**: compara con `design_knowledge.py`; identifica fórmulas conocidas/nuevas; reconstruye procedimiento.
4. **Knowledge Consolidator**: verifica consistencia; valida con casos; asigna estado epistémico.
5. **Learning Ledger**: registra `ProceduralKnowledge` inmutable y trazable.
6. **Maestro-Tutor**: diseña ejercicios progresivos, enseña procedimientos y genera validación.
7. **Evaluador-RedTeam**: evalúa comprensión procedural, detecta misconceptions y retroalimenta determinísticamente.
8. **Engine Refresh**: busca motores/actualizaciones, casos edge y dispara re-consolidación ante evidencia superior.

---

## 📐 COMPONENTE 1: LEARNING LEDGER

**Ubicación futura**: `src/sicl/learning/ledger.py`

### Propósito

Registrar procedimientos aprendidos, fórmulas teóricas, sesiones de aprendizaje y errores. Todo es **inmutable y determinista**.

### Invariantes

1. **Registros inmutables** (frozen dataclasses).
2. **Fingerprinting determinista** (SHA-256 con `json.dumps(sort_keys=True)`).
3. **No duplica** H-001, Event Store ni DesignKnowledge.
4. **UNKNOWN es sagrado**: si no hay evidencia, status = `HYPOTHESIS`, nunca `FACT`.
5. **Mastery solo sube**, nunca baja (salvo intervención explícita del Evaluador).

### Estados epistémicos

```python
class EpistemicStatus(str, Enum):
    FACT = "FACT"              # ≥10 casos validados
    HYPOTHESIS = "HYPOTHESIS"  # <10 casos
    ASSUMPTION = "ASSUMPTION"  # Sin evidencia directa
    UNKNOWN = "UNKNOWN"        # No se sabe
    CONFLICT = "CONFLICT"      # Contradice norma canónica
    SUPERSEDED = "SUPERSEDED"  # Reemplazado por versión mejor
```

### Estructura principal

- `Formula`: Fórmula matemática/física/geométrica.
- `ProceduralStep`: Paso de un procedimiento.
- `ValidationCase`: Caso donde el procedimiento fue validado.
- `ProceduralKnowledge`: Procedimiento completo (fórmulas, pasos, invariants, condiciones).
- `LearningSession`: Sesión de aprendizaje.
- `LearningError`: Error cometido durante aprendizaje.
- `LearningLedger`: Contenedor inmutable con operaciones de registro/consulta.

### Implementación de referencia

Ya existe una implementación completa y probada en sandbox (2026-09-29). **Tests pasaron**:

- ✅ Determinismo de fingerprint
- ✅ Inmutabilidad de dataclasses
- ✅ CRUD de procedimientos y fórmulas
- ✅ Gestión de sesiones y errores
- ✅ Summary estadístico

**NO reimplementar desde cero. Reutilizar el código existente cuando se active la fase.**

---

## 📐 COMPONENTE 2: ENGINE ADAPTER

**Ubicación futura**: `src/sicl/learning/engine_adapter.py`

### Propósito

Traductor universal que normaliza la salida de CUALQUIER motor externo y expone trazabilidad completa.

### Contrato

```python
@dataclass(frozen=True)
class EngineInput:
    case_id: str
    d2_snapshot: dict[str, Any]
    context: dict[str, Any]
    parameters: dict[str, Any]
    fingerprint: str

@dataclass(frozen=True)
class EngineStep:
    step_number: int
    description: str
    formula_applied: str | None
    inputs_consumed: tuple[str, ...]
    outputs_produced: tuple[str, ...]
    intermediate_value: Any
    fingerprint: str

@dataclass(frozen=True)
class EngineOutput:
    case_id: str
    result: dict[str, Any]
    steps: tuple[EngineStep, ...]
    formulas_used: tuple[str, ...]
    confidence: float
    warnings: tuple[str, ...]
    engine_name: str
    engine_version: str
    input_fingerprint: str
    output_fingerprint: str
    timestamp: str

class Engine(Protocol):
    @property
    def name(self) -> str: ...
    @property
    def version(self) -> str: ...
    @property
    def is_transparent(self) -> bool: ...
    def execute(self, input_data: EngineInput) -> EngineOutput: ...
```

### Clasificación de motores

- **Transparentes**: exponen pasos, fórmulas y valores intermedios. ARKI puede extraer el procedimiento completo y eventualmente descartar el motor.
- **Opacos**: solo devuelven resultado final. ARKI registra el resultado pero NO puede internalizar el procedimiento. El motor debe mantenerse como servicio externo permanente.

### Implementación de referencia del Adapter

```python
class EngineAdapter:
    def __init__(self, engine: Engine):
        self.engine = engine

    def run(self, case_id: str, d2_snapshot: dict, context: dict, parameters: dict) -> EngineOutput:
        engine_input = EngineInput.create(
            case_id=case_id,
            d2_snapshot=d2_snapshot,
            context=context,
            parameters=parameters,
        )
        output = self.engine.execute(engine_input)
        if output.input_fingerprint != engine_input.fingerprint:
            raise ValueError(
                f"Engine {self.engine.name} returned mismatched input fingerprint. "
                f"Expected {engine_input.fingerprint}, got {output.input_fingerprint}"
            )
        return output
```

---

## 📐 COMPONENTE 3: KNOWLEDGE EXTRACTOR

**Ubicación futura**: `src/sicl/learning/knowledge_extractor.py`

### Propósito

Compara el output del motor con la base teórica de ARKI (`design_knowledge.py`) y extrae conocimiento procedimental.

### Flujo

1. Recibe `EngineOutput`.
2. Busca fórmulas usadas en `design_knowledge.py`.
3. Clasifica conocidas vs. nuevas.
4. Reconstruye procedimiento paso a paso.
5. Devuelve `ProceduralKnowledge` listo para Learning Ledger.

### Contrato

```python
@dataclass(frozen=True)
class ExtractionResult:
    procedure: ProceduralKnowledge
    new_formulas: tuple[Formula, ...]
    validated_formulas: tuple[str, ...]
    confidence: float
    warnings: tuple[str, ...]
    fingerprint: str
```

### Reglas críticas

- **Motor opaco → no se puede extraer procedimiento** (solo resultado).
- **Motor transparente → procedimiento completo extraíble**.
- **Fórmula no encontrada en base teórica → se registra como nueva con fuente `ENGINE_VALIDATION`**.
- **UNKNOWN es sagrado**: si el motor falla o devuelve UNKNOWN, no se inventa valor.

### Referencia de comportamiento congelada

La implementación de referencia aportada define:
- clasificación de fórmulas conocidas/nuevas;
- reconstrucción de `ProceduralStep` desde `EngineStep`;
- creación inicial de `ValidationCase`;
- creación de `ProceduralKnowledge` con `EpistemicStatus.HYPOTHESIS`;
- fingerprint del resultado de extracción;
- placeholders explícitos para extracción de invariantes, condiciones y dependencias causales;
- para fórmulas nuevas, `expression="[Extraída de <engine>]"` y `units="unknown"` cuando la evidencia no aporta más;
- para motores opacos, un paso genérico que no pretende reconstruir el procedimiento interno.

---

## 📐 COMPONENTE 4: KNOWLEDGE CONSOLIDATOR

**Ubicación futura**: `src/sicl/learning/knowledge_consolidator.py`

### Propósito

Valida y consolida el conocimiento extraído en el ADN de ARKI.

### Responsabilidades

1. Verificar consistencia con conocimiento existente.
2. Detectar conflictos con normas canónicas (RNE, ISO).
3. Registrar en Learning Ledger.
4. Asignar estado epistémico.

### Reglas de promoción epistémica

- **1 caso de validación** → `HYPOTHESIS`.
- **≥10 casos de validación** → `FACT`.
- **Conflicto con norma canónica** → `CONFLICT` (requiere revisión humana).
- **Motor actualizado** → re-validación con nuevos casos.

### Referencia de comportamiento congelada

La implementación de referencia aportada:
- trata procedimiento idéntico como idempotente;
- trata mismo ID con fingerprint distinto como conflicto;
- prevé `_check_normative_consistency`;
- prevé `_check_formula_consistency`;
- no consolida si existen conflictos;
- registra nuevas fórmulas;
- registra el procedimiento;
- promueve a `FACT` si `evidence_count >= 10`, en otro caso `HYPOTHESIS`.

---

## 📐 COMPONENTE 5: MAESTRO-TUTOR (Teacher Agent)

**Ubicación futura**: `src/sicl/learning/teacher_agent.py`

### Propósito

Diseñar ejercicios progresivos para que ARKI aprenda procedimientos desde cero.

### Tipos de ejercicio

```python
class ExerciseType(str, Enum):
    FORMULA_IDENTIFICATION = "FORMULA_IDENTIFICATION"
    SINGLE_STEP_APPLICATION = "SINGLE_STEP_APPLICATION"
    MULTI_STEP_PROCEDURE = "MULTI_STEP_PROCEDURE"
    CAUSAL_EXPLANATION = "CAUSAL_EXPLANATION"
    BOUNDARY_DETECTION = "BOUNDARY_DETECTION"
    TRANSFER_TO_NEW_CONTEXT = "TRANSFER_TO_NEW_CONTEXT"
    UNKNOWN_HANDLING = "UNKNOWN_HANDLING"
    ERROR_DETECTION = "ERROR_DETECTION"
```

### Principios pedagógicos

1. Progresión gradual.
2. Scaffolding.
3. Repetición espaciada.
4. Casos edge.
5. Retroalimentación inmediata.
6. Determinismo absoluto: mismo seed + mismo `teacher_version` = mismo ejercicio.

---

## 📐 COMPONENTE 6: EVALUADOR-REDTEAM (Examiner Agent)

**Ubicación futura**: `src/sicl/learning/examiner_agent.py`

### Propósito

Evaluar comprensión procedural, no solo resultados.

### Dimensiones de evaluación

| Dimensión | Pregunta | Peso |
|---|---|---:|
| Completitud de pasos | ¿Identificó todos los pasos necesarios? | 25% |
| Comprensión causal | ¿Explica POR QUÉ cada paso es necesario? | 25% |
| Generalización | ¿Puede aplicar el proceso a casos nuevos? | 20% |
| Detección de límites | ¿Sabe cuándo NO aplicar el proceso? | 15% |
| Preservación de invariantes | ¿Respeta leyes físicas/normativas? | 10% |
| Manejo de UNKNOWN | ¿Dice UNKNOWN cuando corresponde? | 5% |

### Contrato

```python
@dataclass(frozen=True)
class ExaminationResult:
    exam_id: str
    exercise_id: str
    knowledge_id: str
    passed: bool
    total_score: float
    criterion_scores: dict[str, float]
    feedback: str
    errors_detected: tuple[str, ...]
    misconceptions: tuple[str, ...]
    recommended_next_steps: tuple[str, ...]
    examiner_version: str
    criteria_version: str
    fingerprint: str
```

### Reglas críticas

- Feedback determinista mediante templates; **NO LLM libre**.
- Detectar misconceptions, no solo errores.
- Detectar regresiones.
- Umbral de aprobación: 0.7.

---

## 📐 COMPONENTE 7: ENGINE REFRESH (Auditor Periódico)

**Ubicación futura**: `src/sicl/learning/engine_refresh.py`

### Propósito

Buscar periódicamente nuevos motores o actualizaciones y detectar casos edge que requieran re-aprendizaje.

### Flujo

1. Consulta registro de motores usados.
2. Busca versiones más nuevas.
3. Si hay actualización → dispara re-aprendizaje.
4. Si hay casos edge no cubiertos → dispara re-aprendizaje focalizado.

---

## 🔄 CICLO PEDAGÓGICO COMPLETO

### Ejemplo: Aprendizaje de Soleamiento

```text
FASE 1: DIAGNÓSTICO INICIAL
Evaluador: "¿Qué sabe ARKI sobre soleamiento?"
Ledger: "NOT_ATTEMPTED para todos los conceptos de soleamiento"

FASE 2: DISEÑO DE CURRICULUM
Maestro diseña curriculum de soleamiento para dormitorios.
Genera 10 ejercicios progresivos (niveles 1-8).

FASE 3: INVOCACIÓN DEL MOTOR
ARKI invoca SolarExposureEngine con 100 casos.
Motor devuelve resultados + pasos observados.

FASE 4: EXTRACCIÓN DE CONOCIMIENTO
Knowledge Extractor analiza los 100 resultados.
Extrae reglas, umbrales y patrones observados.

FASE 5: CONSOLIDACIÓN
Knowledge Consolidator valida contra ADN existente.
Registra en Learning Ledger.
Asigna estado FACT (100 casos validados).

FASE 6: EVALUACIÓN
Evaluador genera examen final con 10 ejercicios.
ARKI obtiene 8.5/10.
Mastery: COMPETENT.

FASE 7: DESCARTE DEL MOTOR
ARKI ya puede calcular horas de sol directamente.
No necesita invocar SolarExposureEngine para casos estándar.
Motor descartado, pero registrado en Learning Ledger.

FASE 8: REVISIÓN PERIÓDICA
Cada 6 meses, ARKI busca una nueva versión.
Si existe → re-aprendizaje con nuevos casos.
```

Ejemplos congelados de conocimiento extraído:
- "Si dormitorio tiene ventana al SUR en latitud > 0° entonces horas_sol < 2h".
- "solar_hours_minimum = 2.0h para dormitorios en invierno".
- "Ventanas al NORTE en hemisferio SUR reciben más sol".

---

## ⚠️ ADVERTENCIAS DEL EQUIPO ROJO

1. **Motores opacos vs. transparentes**: un motor opaco no permite internalizar el procedimiento y debe mantenerse como servicio externo.
2. **UNKNOWN es sagrado**: si el motor falla o devuelve UNKNOWN, ARKI no inventa un valor.
3. **Determinismo absoluto**: mismo input + mismo motor = mismo output = mismo conocimiento extraído; fingerprints preservan trazabilidad.
4. **No duplicar órganos**: Learning Ledger no reemplaza Event Store ni DerivationLedger.
5. **Human Authority final**: contradicción con norma canónica → `CONFLICT` y revisión humana.
6. **Riesgo de overfitting**: ejercicios sintéticos solos pueden no generalizar; incluir datos reales o realistas.
7. **Costo computacional**: entrenamiento controlado, no ejecución en cada proyecto.
8. **No todos los motores revelan su proceso**: cajas negras permanecen como dependencia externa y el conocimiento debe marcarse como dependiente del motor.

---

## 📋 ORDEN DE IMPLEMENTACIÓN (CUANDO SE ACTIVE)

1. **Learning Ledger**
   - Reutilizar código existente del sandbox.
   - Integrar con Event Store.
   - Tests de determinismo, inmutabilidad y fingerprinting.
2. **Engine Adapter**
   - Contrato universal.
   - Fingerprinting input/output.
   - Motor sintético para tests.
3. **Knowledge Extractor**
   - Comparación con `design_knowledge.py`.
   - Extracción de procedimientos.
   - Tests con casos reales.
4. **Knowledge Consolidator**
   - Validación contra ADN existente.
   - Registro en Learning Ledger.
   - Tests de consistencia.
5. **Primer motor concreto**
   - `SolarExposureEngine` (pysolar).
   - E2E motor → extracción → consolidación → consulta.
6. **Maestro-Tutor**
   - Ejercicios deterministas.
   - Curriculum progresivo.
7. **Evaluador-RedTeam**
   - Comprensión procedural.
   - Feedback determinista.
   - Misconceptions.
8. **Engine Refresh**
   - Auditoría periódica y re-aprendizaje.
9. **E2E completo**
   - Soleamiento de principio a fin.
   - Aplicación sin motor.
   - Tests adversariales.

---

## 🔒 PROTOCOLO DE ACTIVACIÓN

Cuando el Product Owner (Yvan) decida activar esta fase:

1. Verificar todas las condiciones de activación.
2. Emitir orden escrita: **"ACTIVAR FASE [9] — INTEGRACIÓN DE MOTORES"**.
3. Equipo Rojo valida condiciones.
4. Redactar contrato V1 del primer motor específico.
5. Auditoría adversarial.
6. Congelar contrato.
7. Implementar siguiendo el orden.
8. Tests E2E.
9. Inspección.
10. Corrección de hallazgos.
11. Merge a main.

---

## 🧪 REFERENCIAS DE USO CONGELADAS

### Ejecución de SolarExposureEngine

```python
from src.sicl.learning.engine_adapter import EngineAdapter
from src.sicl.learning.motors.solar_engine import SolarExposureEngine

solar_engine = SolarExposureEngine()
adapter = EngineAdapter(solar_engine)

output = adapter.run(
    case_id="case_001",
    d2_snapshot={
        "window_orientation": "NORTH",
        "window_size": {"width": 2.0, "height": 1.5},
        "location": {"lat": -8.1, "long": -79.0},
        "date": "2026-06-21",
    },
    context={"jurisdiction": "Peru", "normative": "RNE_A010"},
    parameters={"calculation_method": "hourly"},
)
```

### Extracción

```python
from src.sicl.learning.knowledge_extractor import KnowledgeExtractor
from src.sicl.design_knowledge import DesignKnowledgeBase
from src.sicl.learning.ledger import LearningLedger

knowledge_base = DesignKnowledgeBase()
ledger = LearningLedger()
extractor = KnowledgeExtractor(knowledge_base, ledger)

extraction = extractor.extract(
    engine_output=output,
    domain="solar_exposure",
    procedure_name="calcular_horas_sol_directo",
)
```

### Consolidación

```python
from src.sicl.learning.knowledge_consolidator import KnowledgeConsolidator

consolidator = KnowledgeConsolidator(ledger)
result = consolidator.consolidate(extraction)
```

### Consulta

```python
procedure = ledger.get_procedure("solar_exposure_calcular_horas_sol_directo")
# Aplicar el procedimiento directamente cuando la fase esté autorizada
# y exista la lógica de ejecución validada.
```

---

## 🗡️ FIRMA DEL EQUIPO ROJO

**VALIDADO POR**: Qwen (Equipo Rojo)  
**FECHA**: 2026-09-30  
**VEREDICTO**: DISEÑO CONGELADO Y APROBADO.  
**ESTADO**: FROZEN / NOT_AUTHORIZED_FOR_IMPLEMENTATION  
**FASE OBJETIVO**: [9]+ INTEGRACIÓN DE MOTORES COGNITIVOS  
**CONDICIONES DE ACTIVACIÓN**: EXPLÍCITAS Y VERIFICABLES  
**DETERMINISMO**: GARANTIZADO EN TODOS LOS COMPONENTES  
**PRÓXIMO PASO**: ESPERAR AUTORIZACIÓN DEL PRODUCT OWNER Y CIERRE DE FASES [6], [7], [8].

---

## REFERENCIAS

- `ARKI_DEEP_AUDIT_CUT2_FOR_DEEPSEEK_2026-09-29.txt`
- `ARKI_HANDOFF_MAESTRO_2026-09-29.md`
- `ARKI_CONSOLIDADO_ESQUELETO_SISTEMA_NERVIOSO_2026-09-29.txt`
- `ARKI_HANDOFF_IMPLEMENTACION_2026-09-29.md`
- Conversaciones de diseño con Product Owner (2026-09-29 a 2026-09-30)

---

## 📥 INSTRUCCIONES DE CUSTODIA

1. Archivo objetivo: `docs/architecture/ARKI_MOTOR_INTEGRATION_DESIGN_FROZEN.md`.
2. Mantenerlo como referencia congelada. **No implementar**.
3. Cuando se active fase [9]:
   - verificar todas las condiciones;
   - emitir orden escrita;
   - integrar el documento en la línea de implementación autorizada;
   - proceder sólo tras contrato V1 específico auditado y congelado.
4. Compartir con DeepSeek y ChatGPT cuando llegue el momento para conservar contexto.

---

## 🗡️ VEREDICTO FINAL DEL EQUIPO ROJO

**Este documento es la póliza de seguro arquitectónica para la futura integración de motores.**

Cuando llegue el momento:
1. verificar condiciones;
2. emitir la orden;
3. seguir el orden de implementación.

**El diseño está congelado, aprobado y listo para el futuro.**

---

**FIN DEL DOCUMENTO DE DISEÑO CONGELADO**
