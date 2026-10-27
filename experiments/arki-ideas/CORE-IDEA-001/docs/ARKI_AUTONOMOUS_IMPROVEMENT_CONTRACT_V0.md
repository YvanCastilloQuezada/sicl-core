# ARKI — Ciclo autónomo de detección y mejora (contrato propuesto V0)

**Estado:** PROPOSED / NOT IMPLEMENTED / NOT FROZEN. Esta especificación no concede permisos de mutación canónica.

## Misión

Encontrar una carencia → determinar alcance y jurisdicción → interpretar normas con evidencia → razonar alternativas → autoevaluarse → autocorregirse en sandbox → verificar → mejorar un proyecto → registrar aprendizaje → propagar dependencias → repetir.

## Modelo de estados

`DISCOVERED → TRIAGED → EVIDENCE_GATHERED → RULES_SCOPED → HYPOTHESES → SANDBOX_CANDIDATES → EVALUATED → VERIFIED → APPROVAL_GATE → PROMOTED | REJECTED | BLOCKED → LEARNED → PROPAGATED`.

Cada transición produce recibo auditable con timestamp, fuente, versión, dependencias, responsable lógico y estado epistemológico. `UNKNOWN` nunca se convierte en `PASS` por inferencia.

## Carencias detectables

1. **Proyecto:** incompatibilidad espacial, incumplimiento normativo, baja iluminación, confort, accesibilidad, circulación, costo, mantenimiento, desempeño ambiental.
2. **Conocimiento:** ausencia de norma, fuente desactualizada, incertidumbre jurisdiccional, contradicciones entre fuentes, falta de competencia demostrada.
3. **Sistema:** módulos sin pruebas, capacidades declaradas sin ejecución, rutas de bypass, cobertura insuficiente, regresiones, deuda técnica.
4. **Árbol Digital:** nodos huérfanos, dependencias inconsistentes, ideas pendientes, evidencia caducada, contratos FROZEN afectados.

## Principios obligatorios

- AGK único, 3D-First, multiescala desde objeto a territorio, relaciones y temporalidad explícitas.
- Aplicabilidad normativa determinada por escala, jurisdicción, fecha y tipo de intervención. Prohibida la extrapolación automática.
- Separar HECHOS, SUPUESTOS, OBJETIVOS, RESTRICCIONES, PREFERENCIAS y DECISIONES.
- PASSIVE FIRST; medir y justificar intervenciones antes de elegirlas.
- La geometría operacional canónica solo se modifica mediante API autorizada AGK.
- No editar directamente contratos FROZEN; crear propuesta de cambio con análisis de impacto.
- Aprendizaje candidato pasa por Delta 6.2 y pruebas de competencia antes de volverse conocimiento reutilizable.
- Promociones canónicas sujetas a autorización humana criptográfica ACE88 cuando corresponda.
- Rechazar cambios que degradan restricciones duras; optimización multiobjetivo y frente Pareto para los demás.
- Nunca usar autodiagnóstico como permiso para autodesplegarse, autopromocionarse o debilitar controles.

## Contrato mínimo por carencia

`deficit_id, project_id, scale, location/jurisdiction, observed_state, desired_state, source_refs, evidence_hashes, confidence, severity, dependencies, impacted_frozen, candidate_changes, tests, metrics_before, metrics_after, approval_state, decision_receipt, learning_delta, propagation_receipt`.

## Ejecución por capas

1. **Autoinspección:** inventario de módulos, pruebas, ramas, contratos y dependencias.
2. **Autodiagnóstico:** carencias reproducibles y contradicciones, sin inventar normativa.
3. **Investigación normativa:** fuentes versionadas, jerarquía, aplicabilidad y vigencia.
4. **Planificación:** hipótesis alternativas y efectos previstos.
5. **Experimentación:** ramas o estados aislados; AGK para mutaciones geométricas autorizadas.
6. **Autoevaluación:** pruebas funcionales, geométricas, normativas, seguridad y regresión; métricas antes/después.
7. **Propuesta de corrección:** revisión de impactos y aprobaciones; no autopromoción.
8. **Aprendizaje:** Delta 6.2, procedencia, competencia, anti-contaminación.
9. **Propagación:** Árbol Digital, Mapa Digital, Gemelo Digital, ideas, FROZEN y evidencias afectadas.
10. **Reevaluación:** repetir hasta criterios de parada o escalamiento por incertidumbre.

## Criterios de aceptación E2E (pendientes)

- Defecto real identificado con evidencia y reproducibilidad.
- Norma interpretada con fuente, fecha, jurisdicción, escala y contradicciones resueltas o marcadas UNKNOWN.
- Al menos dos alternativas y una descartada justificadamente.
- Ensayo aislado, métricas antes/después y cero mutaciones canónicas no autorizadas.
- Rechazo demostrado de firma ausente/falsificada/replay.
- Registro persistente de decisiones, aprendizaje y propagación.
- Regresión completa verde y auditoría independiente antes de FREEZE.

## Estado actual

ACE88: regresión funcional PASS informada en ARKI-02; seguridad independiente pendiente. Este documento **no** prueba que el ciclo autónomo esté implementado. La herramienta de inventario anexa es observacional, no un motor de autocorrección.
