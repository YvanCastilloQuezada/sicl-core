# ARKI Copilot CP-03 — Capability Registry and Orchestration

**Status:** Architecture proposal; registry implementation follows after CP-01 tests and CP-02 security decisions.
**Branch:** feat/arki-copilot-foundation-cp00-06

## Purpose

CP-03 is the controlled routing and orchestration layer. It maps a classified user goal to a registered capability, verifies prerequisites, obtains approval where needed, invokes the capability through an adapter, and records outcomes.

The Copilot model is not itself the execution authority. Neither natural-language confidence nor UI state can grant permissions.

## Flow

1. Receive user message and attachments (session layer CP-02).
2. Resolve bounded, authorized project context.
3. Classify intent (CP-01); mixed or ambiguous intent asks a clarification question.
4. Select capability by intent and capability registry metadata.
5. Check availability, prerequisites, input schema, permissions, risk class, and context requirements.
6. For execute-capable operations, evaluate the fail-closed action gate.
7. If confirmation is required, show a human-readable plan, inputs, expected effects, and risk.
8. Invoke through a capability adapter (not direct model-generated code or arbitrary shell).
9. Validate outputs against the capability's schema and safety rules.
10. Return a result summary, evidence/references, and next-step choices.
11. Persist outcome metadata and trace ID, avoiding secrets and unnecessary conversation payloads.

## Capability contract

Each registered capability needs:

- Stable capability ID and version.
- Human-readable name and description.
- Supported intent(s).
- Input schema and validation.
- Output schema and validation.
- Availability/health check.
- Project/context requirements.
- Permission requirements.
- Risk classification.
- Whether human confirmation is required.
- Timeout and resource limits.
- Idempotency support (where applicable).
- Evidence/trace expectations.
- Adapter implementation identifier.

The registry is static/configured and reviewed; user content must not register or modify capabilities.

## Proposed risk levels

- **R0 — Read-only/conversational:** answer, explain, summarize, inspect context.
- **R1 — Research/read:** external search, file read, bounded analysis.
- **R2 — Prepare:** produce a plan or draft without mutating ARKI project state.
- **R3 — Reversible mutation:** create/edit a draft or staging artifact, requiring scoped permission and usually confirmation.
- **R4 — High-impact mutation:** canonical geometry, project state, execution, exports, submissions, or irreversible operations; explicit confirmation, policy checks, validated inputs, and audit evidence required.

Risk is a property of the capability and action, not the wording or model confidence. The system must not downgrade risk to avoid confirmation.

## Capability families

Initial families (names are taxonomy, not implemented integrations):

- Conversation/context
- Research/search
- File/image/document analysis
- Field observation and location capture
- Architectural/urban reasoning
- Geometry and model generation
- Project workflow and phase operations
- Validation/review
- Export and delivery
- Administrative system operations

## Failure behavior

- Capability absent: explain unavailability and offer preparation/manual next step.
- Health check fails: do not invoke; report unavailable.
- Input validation fails: identify missing/invalid inputs and ask targeted clarification.
- Authorization fails: do not retry with alternate credentials or broaden scope.
- Timeout: report indeterminate state where applicable; do not blindly retry non-idempotent operations.
- Output validation fails: quarantine output; do not treat as accepted/canonical.
- Confirmation missing: return a plan, do not execute.
- Partial success: report precisely which substeps succeeded, failed, or remain uncertain.

## Separation of authorities

- LLM: language understanding, explanation, reasoning, proposals.
- Intent classifier: intent assessment only.
- Capability registry: defines available operations and constraints.
- Action gate: determines whether policy prerequisites are satisfied.
- AuthZ layer: decides actor and project permissions.
- Capability adapter: invokes a specific registered operation.
- AGK: remains sole authority for operational geometry.
- Validators/evidence runners: independently verify results.
- Session store: records conversations, not project truth.

## CP-03 acceptance criteria

1. Unknown capabilities cannot be invoked.
2. User messages cannot alter registry, permission, or risk metadata.
3. Capability availability is checked before action.
4. Inputs validated against declared schema before invocation.
5. Execution gate is evaluated independently from intent classifier.
6. Authorization is actor/project/action scoped.
7. Confirmation includes understandable action details.
8. Invocation is traced and outcome recorded.
9. Idempotency/retry policy is explicit per capability.
10. Output validation failure prevents canonical acceptance.


## CP-03 implementation checkpoint — 2026-11-26

Implemented a code-owned static catalog in `src/sicl/copilot_capabilities.py` with immutable runtime registry metadata, capability IDs/version, intent support, risk, availability, adapter ID, permission label, schema identifiers, timeout and idempotency flags. Routing returns candidate IDs only and always states `execution_authorized: false`. The execute operation is R4 and unavailable without an adapter. Tests were authored; they have not been run. This is not the full orchestrator: health checks, real schema validators, authorization binding, approval workflow, adapters, invocation, output validation and audit outcomes remain unimplemented.
