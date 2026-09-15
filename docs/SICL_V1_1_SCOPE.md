# SICL v1.1 — Scope e invariantes

**Estado:** IMPLEMENTED AND TESTED

## Alcance

SICL v1.1 agrega exclusivamente `Alternative`, `Evaluation`, `Comparison` y `Recommendation` al Core CLI v1.0. No agrega Agents, Optimization/Pareto, Site Intelligence, lenguaje natural, Conflict Engine avanzado, GIS, BIM ni UI.

## Invariantes

1. `Recommendation` nunca crea ni aprueba automáticamente una `Decision`; permanece `PENDING_APPROVAL` hasta una acción humana explícita mediante `/DECISION RECORD`.
2. Toda `Evaluation` tiene `source` explícito y válido: `USER_INPUT`, `AI_INFERENCE`, `SIMULATION`, `FACT` o `ASSUMPTION`.
3. Una `Alternative` solo puede evaluarse si el proyecto contiene al menos un `Objective`.
4. Una `Comparison` requiere al menos dos `Alternative`.
5. Fact, Assumption, Objective y Constraint conservan sus significados diferenciados.
6. Los eventos continúan siendo append-only y mantienen `source` obligatorio.

## Verificación

La suite completa del Core contiene 17 pruebas aprobadas, incluyendo seis pruebas específicas de v1.1:

- creación de Alternative;
- Evaluation contra Objective;
- Comparison con trade-offs y mínimo de dos alternativas;
- Recommendation separada de Decision;
- aprobación humana requerida;
- Evaluation basada en Fact y Assumption.

## Persistencia

Las cuatro entidades se almacenan en tablas SQLite separadas y se relacionan con `Project` mediante claves explícitas. Las mutaciones generan eventos y no alteran el event log histórico.
