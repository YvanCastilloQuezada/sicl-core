# ARKI Copilot CP-05 — Architectural and Urban Intelligence

**Status:** Design proposal; no generation engine integration implied.
**Branch:** feat/arki-copilot-foundation-cp00-06

## Goal

Build a reasoning framework that supports the architect through programming, urban/architectural analysis, design alternatives, assessment, and preparation of generation requests. CP-05 does not replace AGK, specialized geometry engines, project phases, regulatory validation, or professional judgment.

## Problem representation

A design problem is represented as a structured, versioned brief:

- Project type and use(s)
- Location and site boundary/reference, if known
- Site dimensions, area, slope, orientation, climate and context, each with provenance/status
- User and operational needs
- Capacity and population assumptions
- Program and area targets
- Spatial adjacencies and circulation
- Constraints (confirmed, proposed, unknown)
- Applicable regulations and references
- Budget/time/material constraints, when supplied
- Design priorities and trade-offs
- Evaluation criteria
- Unresolved questions
- Brief version and change history

Missing information is not silently defaulted. Suggested defaults are explicitly labelled proposals and require approval where they materially affect outcomes.

## Reasoning operations

- Intake: turn conversation, files, photos and measurements into candidate brief entries.
- Normalize: units, labels and categories without losing original values.
- Detect: missing inputs, contradictions, infeasible constraints, scope drift.
- Program: develop spaces, capacities, relationships and area ranges.
- Analyze: site/context, climate, access, circulation, functional and urban relationships.
- Explore: generate strategies/alternatives at a level the current capability supports.
- Evaluate: compare using explicit criteria and weights; weights are proposed, not hidden.
- Critique: identify weaknesses, risks, opportunities and counterarguments.
- Prepare: convert approved brief into a typed engine request.
- Review: independently check output and trace it to brief/constraints.

## Design alternatives

Every alternative should have:

- Stable ID and version
- Clear strategy description
- Explicit assumptions
- Program/area summary
- Relationship/circulation logic
- Site/context response
- Pros, cons, risks and trade-offs
- Evaluation scores with rationale and criteria
- Supporting evidence, if sourced
- What changed relative to prior alternative

Scores must not create false precision. A numeric score is only meaningful when criteria, weighting, data and method are visible.

## Integration boundaries

- Copilot proposes and interprets design intent.
- A typed adapter converts approved design briefs into requests for registered capabilities.
- Specialized engines perform their supported operations.
- AGK remains the single operational geometry authority.
- Validation/evidence systems independently evaluate results.
- Canonical project state is updated only through authorized project operations.

## CP-05 acceptance criteria

1. Brief data is structured and versioned.
2. Each fact carries status/provenance.
3. No hidden assumptions are inserted.
4. Conflicts and missing inputs are reported.
5. Alternatives are traceable to the brief.
6. Evaluation criteria/weights are explicit.
7. Design intent is not mistaken for geometry execution.
8. Engine requests are typed and validated.
9. Geometry authority is not duplicated.
10. Outputs can be independently reviewed and reproduced where supported.


## CP-05 implementation checkpoint — 2026-11-26

Added structured `DesignBrief`, `DesignCriterion`, `DesignAlternative`, and `AlternativeScore` contracts. Criteria require unique IDs and weights summing to 1; TARGET criteria require explicit targets; alternatives may only score registered criteria; normalized scores are bounded; facts retain epistemic status and provenance through CopilotFact. No design generation, weighted-score calculation, spatial optimization, CAD/AGK/OCCT/Manifold invocation, or project mutation is included. Tests authored but not executed.
