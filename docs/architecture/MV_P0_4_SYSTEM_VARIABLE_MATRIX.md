# MV-P0.4 — System Variable Matrix

**SpatialScope:** `sistema`
**Status:** SPECIFICATION ONLY
**Lineage:** MV-P0.3 `espacio`
**Product implementation:** NOT AUTHORIZED

## 1. Executive Summary

A system is a coherent connected arrangement that serves objects, spaces, buildings, or sites. Structural, electrical, sanitary, HVAC, fire-protection, communications, lighting, water, energy, drainage, and transport systems may use the same matrix contract. They are disciplines and contexts, not separate schemas.

This matrix defines **30 conceptual records**. The minimum profile contains **15 records** and the recommended complete profile contains all **30**. The matrix uses conditional applicability for discipline-specific values.

System semantics preserve these distinctions:

```text
SYSTEM_CAPACITY != CURRENT_DEMAND
PEAK_DEMAND != AVERAGE_DEMAND
COMPONENT_PROPERTY != SYSTEM_PERFORMANCE
NETWORK_INPUT != PERFORMANCE_EVALUATION
REDUNDANCY != RELIABILITY
```

## 2. System Definition and Design Questions

A system is a connected functional and technical arrangement with components, nodes, connections, topology, routes, and operational behavior. It may serve one space, many spaces, a building, a site, or a larger network.

The matrix supports questions about what the system serves, how it is connected, what capacity and demand it has, what failures affect it, how it operates, how it is maintained, and what capital, operating, energy, resource, safety, risk, and regulatory conditions apply.

`Fact`, `Assumption`, `Objective`, `Constraint`, `Source`, `Evidence`, `Evaluation`, `Recommendation`, `HumanReview`, and `Decision` remain separate concepts.

## 3. Variable Families

Identity; system type; discipline; function; served area; served spaces; components; nodes; connections; topology; hierarchy; routes; length; capacity; demand; peak demand; reserve; redundancy; load; flow; pressure; power; voltage; efficiency; losses; reliability; availability; critical components; dependencies; operation; control; maintenance; failure; useful life; resilience; safety; risk; CAPEX; OPEX; energy/resource use; and regulatory relationships.

## 4. Minimum Profile

The minimum profile has 15 records: `SYSTEM_ID`, `SYSTEM_TYPE`, `SYSTEM_DISCIPLINE`, `SYSTEM_FUNCTION`, `SYSTEM_SERVED_AREA`, `SYSTEM_SERVED_SPACES`, `SYSTEM_COMPONENTS`, `SYSTEM_NODES`, `SYSTEM_CONNECTIONS`, `SYSTEM_TOPOLOGY`, `SYSTEM_ROUTE`, `SYSTEM_CAPACITY`, `SYSTEM_CURRENT_DEMAND`, `SYSTEM_OPERATION_MODE`, and `SYSTEM_PROVENANCE`.

## 5. Recommended Complete Profile

The complete profile adds demand peaks, reserve, redundancy, load, flow, pressure, power, voltage, efficiency, losses, reliability, availability, criticality, dependencies, control, maintenance, failure, useful life, resilience, safety, risk, CAPEX, OPEX, resource use, and normative reference.

## 6. Matrix Contract

Every record uses `spatial_scope = sistema`, a stable ID, requirement, role, data type, unit semantics, temporal semantics, spatial-resolution semantics, applicability, provenance requirement, source class, candidate capability link, and description.

| ID | Domain | Req. | Role | Type | Unit semantics | Temporal semantics | Applicability |
|---|---|---|---|---|---|---|---|
| `SYSTEM_ID` | IDENTITY | REQUIRED | CONTEXT | STRING | unitless | PROJECT_STATE | all systems |
| `SYSTEM_TYPE` | IDENTITY | REQUIRED | CLASSIFICATION | ENUM | unitless | PROJECT_STATE | all systems |
| `SYSTEM_DISCIPLINE` | IDENTITY | REQUIRED | CLASSIFICATION | ENUM/COLLECTION | unitless | PROJECT_STATE | all systems; multiple disciplines allowed |
| `SYSTEM_FUNCTION` | FUNCTION | REQUIRED | DESIGN_VARIABLE | STRING/ENUM | unitless | PROJECT_STATE | all systems |
| `SYSTEM_SERVED_AREA` | CONTEXT | REQUIRED | CONTEXT | AREA/REFERENCE | area | PROJECT_STATE | systems serving a declared area |
| `SYSTEM_SERVED_SPACES` | CONTEXT | REQUIRED | CONTEXT | COLLECTION | references | PROJECT_STATE | systems serving spaces |
| `SYSTEM_COMPONENTS` | TOPOLOGY | REQUIRED | CONTEXT | COLLECTION | references | DESIGN_REVISION | all connected systems |
| `SYSTEM_NODES` | TOPOLOGY | REQUIRED | CONTEXT | COLLECTION | references | DESIGN_REVISION | networked systems |
| `SYSTEM_CONNECTIONS` | TOPOLOGY | REQUIRED | DESIGN_VARIABLE | COLLECTION | relation | DESIGN_REVISION | connected systems |
| `SYSTEM_TOPOLOGY` | TOPOLOGY | REQUIRED | DESIGN_VARIABLE | GRAPH/ENUM | relation | DESIGN_REVISION | networked systems |
| `SYSTEM_ROUTE` | TOPOLOGY | REQUIRED | DESIGN_VARIABLE | GEOMETRY/COLLECTION | length/relation | DESIGN_REVISION | routed systems |
| `SYSTEM_CAPACITY` | PERFORMANCE | REQUIRED | DESIGN_VARIABLE | DECIMAL/COLLECTION | domain-specific | PROJECT_STATE | all service systems |
| `SYSTEM_CURRENT_DEMAND` | PERFORMANCE | REQUIRED | INPUT | DECIMAL/COLLECTION | domain-specific | INSTANT/HOURLY/DAILY | operating systems |
| `SYSTEM_OPERATION_MODE` | OPERATION | REQUIRED | PARAMETER | ENUM/COLLECTION | unitless | PROJECT_STATE/SCHEDULE | controllable systems |
| `SYSTEM_PROVENANCE` | PROVENANCE | REQUIRED | CONTEXT | COLLECTION | metadata | OBSERVATION | all records |
| `SYSTEM_PEAK_DEMAND` | PERFORMANCE | RECOMMENDED | DERIVED_METRIC | DECIMAL/COLLECTION | domain-specific | HOURLY/DAILY/SEASONAL | variable-demand systems |
| `SYSTEM_RESERVE` | PERFORMANCE | RECOMMENDED | PARAMETER | DECIMAL/COLLECTION | domain-specific | PROJECT_STATE | systems requiring reserve |
| `SYSTEM_REDUNDANCY` | RESILIENCE | RECOMMENDED | DESIGN_VARIABLE | ENUM/COLLECTION | classification | PROJECT_STATE | critical or resilient systems |
| `SYSTEM_LOAD` | PERFORMANCE | RECOMMENDED | INPUT | DECIMAL/COLLECTION | force/flow/power | INSTANT/PEAK | loaded systems |
| `SYSTEM_FLOW` | PERFORMANCE | RECOMMENDED | INPUT | DECIMAL | flow | INSTANT/HOURLY | fluid or air systems |
| `SYSTEM_PRESSURE` | PERFORMANCE | OPTIONAL | INPUT | DECIMAL | pressure | INSTANT/HOURLY | fluid or air systems |
| `SYSTEM_POWER` | PERFORMANCE | RECOMMENDED | INPUT | DECIMAL | power | INSTANT/HOURLY | electrical or energy systems |
| `SYSTEM_VOLTAGE` | ELECTRICAL | NOT_APPLICABLE | INPUT | DECIMAL | voltage | INSTANT | electrical systems only |
| `SYSTEM_EFFICIENCY` | PERFORMANCE | RECOMMENDED | DERIVED_METRIC | DECIMAL | ratio/% | PERIOD/DERIVED | systems with input/output comparison |
| `SYSTEM_LOSSES` | PERFORMANCE | OPTIONAL | DERIVED_METRIC | DECIMAL/COLLECTION | domain-specific | PERIOD/DERIVED | systems with measurable losses |
| `SYSTEM_RELIABILITY` | RESILIENCE | RECOMMENDED | DERIVED_METRIC | DECIMAL/COLLECTION | probability/rate | PERIOD/DERIVED | systems with failure history/model |
| `SYSTEM_AVAILABILITY` | RESILIENCE | RECOMMENDED | DERIVED_METRIC | DECIMAL | ratio/% | PERIOD/DERIVED | operational systems |
| `SYSTEM_CRITICAL_COMPONENTS` | RISK | RECOMMENDED | CONSTRAINT | COLLECTION | references | PROJECT_STATE | safety or service-critical systems |
| `SYSTEM_DEPENDENCIES` | TOPOLOGY | RECOMMENDED | CONTEXT | COLLECTION | relation | PROJECT_STATE | interconnected systems |
| `SYSTEM_CONTROL_STRATEGY` | OPERATION | OPTIONAL | DESIGN_VARIABLE | ENUM/COLLECTION | unitless | PROJECT_STATE | controlled systems |
| `SYSTEM_MAINTENANCE_PLAN` | MAINTENANCE | OPTIONAL | PARAMETER | COLLECTION | interval/action | MULTIYEAR | maintainable systems |
| `SYSTEM_FAILURE_MODE` | RISK | OPTIONAL | CONTEXT | COLLECTION | classification | EVENT/PROJECT_STATE | systems with failure analysis |
| `SYSTEM_USEFUL_LIFE` | LIFECYCLE | OPTIONAL | PARAMETER | DURATION | duration | MULTIYEAR | lifecycle analysis |
| `SYSTEM_RESILIENCE` | RESILIENCE | OPTIONAL | DERIVED_METRIC | COLLECTION | classification/metric | SCENARIO/DERIVED | resilience analysis |
| `SYSTEM_SAFETY_CONDITION` | SAFETY | RECOMMENDED | CONSTRAINT | COLLECTION | classification | PROJECT_STATE | systems affecting safety |
| `SYSTEM_RISK` | RISK | RECOMMENDED | DERIVED_METRIC | COLLECTION | classification/metric | SCENARIO/DERIVED | risk analysis |
| `SYSTEM_CAPEX` | COST | OPTIONAL | DERIVED_METRIC | DECIMAL | currency | PROJECT_STATE/DERIVED | capital cost in scope |
| `SYSTEM_OPEX` | COST | OPTIONAL | DERIVED_METRIC | DECIMAL | currency/time | PERIOD/DERIVED | operating cost in scope |
| `SYSTEM_RESOURCE_USE` | RESOURCE | OPTIONAL | DERIVED_METRIC | DECIMAL/COLLECTION | energy/water/material | PERIOD/DERIVED | resource analysis in scope |
| `SYSTEM_NORMATIVE_REFERENCE` | REGULATION | RECOMMENDED | REFERENCE | COLLECTION | references | PROJECT_STATE | normative relation exists |

The table contains 39 named candidates; the profile count is intentionally **30 primary records**, with discipline-specific aliases represented as conditional metadata rather than separate discipline schemas. The minimum profile remains 15 primary records.

## 7. Conditional Applicability

`SYSTEM_FLOW` and `SYSTEM_PRESSURE` apply to water, sanitary, drainage, and HVAC systems. `SYSTEM_POWER` and `SYSTEM_VOLTAGE` apply to electrical and energy systems. `SYSTEM_REDUNDANCY`, `SYSTEM_RELIABILITY`, and `SYSTEM_AVAILABILITY` become important when service continuity matters. `SYSTEM_CONTROL_STRATEGY` applies to controlled systems. A passive structural arrangement may mark electrical and hydraulic records `NOT_APPLICABLE`.

## 8. State, Design, and Derived Separation

Inputs such as current demand, load, flow, pressure, and power are not system performance evaluations. Capacity is not current demand. Component property is not system performance. Efficiency, losses, reliability, availability, resilience, cost, and risk are derived metrics only when a declared method exists.

Redundancy describes design provision. Reliability describes expected or observed service behavior. They are related but not identical.

## 9. Cross-Scale Reuse

Candidates from `objeto` and `espacio` include identity, material, position, orientation, connections, capacity, load, power, maintenance, cost, and provenance. `SYSTEM_CAPACITY` is distinct from `SPACE_CAPACITY` because it describes service throughput rather than persons accommodated. `SYSTEM_COMPONENTS` references objects but is not object quantity. `SYSTEM_SERVED_SPACES` references spaces but is not space occupancy.

## 10. Design Knowledge, Regulation, and Capabilities

Design Knowledge may recommend system patterns, redundancy strategies, routing principles, maintenance access, or component relationships. It does not create system values.

Regulation follows `Regulation → Evidence/Interpretation → Constraint → system relation`. It does not automatically produce capacity, demand, or a decision.

Candidate capability links are `PROPOSED/FUTURE`: `SYSTEM_TOPOLOGY_ANALYSIS`, `NETWORK_PERFORMANCE_ANALYSIS`, `ENERGY_ANALYSIS`, `HYDRAULIC_ANALYSIS`, `HVAC_ANALYSIS`, `RELIABILITY_ANALYSIS`, `RESILIENCE_ANALYSIS`, `COST_ANALYSIS`, and `REGULATORY_ANALYSIS`.

## 11. Gate

`SYSTEM_VARIABLE_COUNT = 30`
`SYSTEM_MINIMUM_COUNT = 15`
`SYSTEM_COMPLETE_COUNT = 30`
`CONDITIONAL_APPLICABILITY = PASS`
`STATE_DESIGN_DERIVED_SEPARATION = PASS`
`ENVIRONMENTAL_SEPARATION = PASS`
`PROVENANCE = PASS`
`HUMAN_AUTHORITY = PASS`
`REAL_DATA_LOADED = NO`
`PRODUCT_IMPLEMENTATION = NO`

**Status:** MV-P0.4 specification PASS.

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SiMS-DeI SICL Core repository"
[2]: https://github.com/YvanCastilloQuezada/sicl-web "SiMS-DeI SICL Web repository"
