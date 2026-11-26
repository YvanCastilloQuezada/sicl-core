# ARKI COPILOT — Foundation Proposal (CP-00 to CP-06)

**Status:** Proposed foundation; implementation branch opened  
**Branch:** `feat/arki-copilot-foundation-cp00-06`  
**Doctrine:** Rebuild the Copilot experience from the approved concept. Existing components are candidates for absorption, not constraints. Reuse only when inspected, verified, and aligned.

## 0. Definition — What is ARKI Copilot?

ARKI Copilot is the architect's continuous, context-aware assistant across the complete architectural workflow: field work on a mobile device and office work at the desktop/server. It supports conversation, observation, research, interpretation, architectural reasoning, preparation of actions, and controlled execution through verified capabilities.

It is **one assistant and one authority model**, presented through two primary interfaces:

- **Avatar / Field (mobile):** optimized for camera, multiple photos, voice, quick notes, location context when authorized, field observations, and project continuity.
- **Copilot / Office (desktop):** a floating, non-tab conversational window over the ARKI workspace, optimized for text, voice, attachments, analysis, planning, tools, and design work.

The interfaces must not create separate assistants, separate memories, or duplicate project state. The server is the authority for shared sessions and data; clients are presentation/input surfaces.

## 1. Core purpose

The Copilot should help the architect:
1. Understand the current project and workflow phase using available, verified context.
2. Capture field information (photos, voice, text, documents, location if allowed) and preserve provenance.
3. Converse and reason without triggering project mutations.
4. Research and compare alternatives, including source-backed answers where appropriate.
5. Analyze architectural requirements, program, constraints, spatial relationships, and design options.
6. Prepare actions and explain inputs, missing data, dependencies, risks, and expected effects.
7. Execute only explicit, permitted, supported operations.
8. Verify results and report evidence, failures, uncertainty, and next steps.
9. Maintain continuity between field and office, across devices and sessions, without pretending to remember data that is unavailable.

## 2. Non-negotiable principles

- **Conversation is not execution.**
- **Interpretation is not authorization.**
- **Preparation is not execution.**
- Parameter extraction alone can never authorize generation or mutation.
- Missing information remains `MISSING`; ambiguous intent remains `AMBIGUOUS`; unconfirmed inference is explicitly marked as a proposal.
- Do not silently substitute default project facts (area, city, capacity, typology, family, variant, etc.).
- No capability may be advertised as available until registered and verified.
- Every tool/action has an explicit permission policy, risk class, input schema, and evidence/verification contract.
- No duplicate authority: geometry remains AGK-authoritative; existing specialized engines remain their own authorities.
- Reuse existing components only after audit; replace or remove unsuitable components rather than preserving them for sunk-cost reasons.
- No destructive or irreversible action without explicit confirmation and traceable outcome.
- Respect privacy, authorization, and project data boundaries; field images and documents remain attached to a clear project/session context.

## 3. Work packages

### CP-00 — Baseline audit and evidence inventory
Inventory the current code, endpoints, session/project persistence, auth, image/voice flows, tools, tests, and actual server connections. Separate documented, implemented, connected, tested, and verified capabilities. Deliver an evidence matrix and gap list. Audit is not complete until key claims have source paths and test/runtime evidence.

### CP-01 — Conversational contract and intent policy
Define message/session/action contracts and an intent taxonomy:
- `CONVERSE`
- `RESEARCH`
- `EXPLORE`
- `DESIGN_INTENT`
- `PREPARE_ACTION`
- `EXECUTE`
- `REVIEW`
- `CONTINUE`

Conversation, research, exploration, design intent, preparation, and review do not mutate project state. `EXECUTE` requires explicit intent, capability availability, validated inputs, policy approval, confirmation where required, and an execution record. Ambiguous commands ask one targeted clarification rather than guessing.

### CP-02 — Context and shared continuity
Implement server-authoritative context and persistence for sessions/messages/attachments and context references. Context is selectively resolved, not indiscriminately injected:
- project and project ID
- current workflow/module/phase
- confirmed goals, constraints, and parameters
- decisions and their provenance
- field observations and attachments
- pending tasks, risks, missing data
- relevant geometry/results/evidence references

Mobile and desktop can resume the same project/session. Session context must be inspectable, bounded, and updateable. Do not treat client local storage as the source of truth.

### CP-03 — Conversation orchestrator
The orchestration layer coordinates conversation, context resolution, intent classification, policy, capability routing, result/evidence handling, and response composition. It must not itself become a second geometry engine or generation authority. Establish clear service boundaries and deterministic policy checks around model outputs.

### CP-04 — Research, files, and tools
Create a verified capability registry. For each capability record: ID, description, owning service/engine, status (planned/unavailable/connected/tested/verified), input/output schema, permissions, risk/reversibility, evidence contract, and tests. Research, RNE/regulatory lookup, document reading, images, file ingestion, and external web tools are integrated only through real, tested adapters. UI entries cannot imply a connected tool.

### CP-05 — Architectural intelligence
Integrate specialized ARKI capabilities through the registry and orchestrator:
- architectural programming and typology reasoning
- feasibility and requirements analysis
- spatial/functional relationships
- exploration and comparison
- F3/F4/F5 intelligence (after verified audit of current contracts)
- AGK geometric authority
- MDE and other specialized engines, as applicable and verified

The Copilot proposes, explains, checks, and routes work; specialized engines remain authoritative for their domains. Do not duplicate geometry or engine logic in the conversational layer.

### CP-06 — Field interface, multimodal intake, and controlled autonomy
Build the mobile Avatar surface and integrate multimodal input:
- capture or select multiple photos
- send photos with voice/text in a single message
- dictate observations and questions
- file/document attachments where supported
- contextual field record and location only when explicitly available/authorized
- analyze images with uncertainty and evidence
- register observations as proposals pending architect review

Autonomy levels:
- L0: answer
- L1: recommend
- L2: prepare/validate
- L3: execute reversible, explicitly authorized operations
- L4: controlled autonomous workflows only after capability-specific safeguards and evidence

Begin at L0-L2. L3 only for capability-specific, reversible actions with explicit authorization. L4 is not part of the initial implementation.

## 4. UX contract

### Field — Avatar
Mobile-first assistant surface, opened by the Avatar control. Prioritize camera/photo capture, multi-image selection, voice, quick notes, and project context. It should not navigate away from the project. Closing the surface does not destroy the session.

### Office — floating Copilot
Desktop Copilot opens as a floating overlay from the right-side Copilot control, not as a tab and not as a permanent layout column. It must not resize or obstruct the main workspace unnecessarily. It supports conversation, mic, attachments, context, tool results, prepared action previews, and explicit approval. Minimize/close retains the session.

## 5. First vertical slice and acceptance criteria

First working vertical slice: **CP-01 + minimum CP-02**.

User asks a project question or sends field photos and notes. Copilot:
1. Resolves authenticated user, project/session, and available context.
2. Classifies intent without mutation.
3. Responds conversationally or asks a targeted clarification.
4. Marks missing, inferred, and confirmed facts distinctly.
5. Persists the conversation and attachments server-side.
6. Resumes the same session from desktop/mobile.
7. Does not start the F1–F10 generation pipeline unless a later explicit EXECUTE action is authorized.
8. Emits auditable events for any tool call or action.
9. Verifies the outcome before claiming success.

## 6. Existing assets: candidates, not assumptions

Audit and consider absorbing:
- `CopilotPanel.tsx` — desktop conversation UI candidate.
- `CommandBar.tsx` — conversational intake, voice, visual capture/analysis, and observation flow candidate.
- `useSpeech` — voice input candidate.
- RFC-029 / `copilot.py` — NL-to-SICL preview translator, retained as a specialized translator, not the general conversation brain.
- RFC-014 — conceptual user-copilot reference; verify which portions are implemented before adoption.
- Existing upload, visual-analysis, project-context, and tool handlers — reuse only after endpoint, permission, persistence, and test verification.

No assumption that an existing component is advanced enough to retain. No mass deletion before an inventory and dependency audit.

## 7. Development sequence

1. **CP-00 audit completion:** evidence-based inventory of current implementations and gaps.
2. **CP-01 contract:** types/schemas, intent policy, conversation-vs-action guard, tests.
3. **CP-02 minimum context:** server-authoritative sessions/messages and project linkage; attachment persistence and multi-device continuation.
4. **Desktop floating surface:** wire existing UI candidate or replace, according to audit.
5. **Mobile Avatar surface:** mobile-specific UI using same API/session.
6. **Capability registry and tool adapters:** only verified capabilities.
7. **Architectural intelligence integration:** specialized engines and evidence.
8. **Field/autonomy expansion:** image, location, voice, action safeguards and staged autonomy.

Each phase is isolated, tested, reviewed, and evidence-recorded. No merge to main, no AGK changes, and no changes to canonical generation pipeline as part of this foundation work.

## 8. Definition of success

A Copilot that can reliably answer: “Review this project and tell me where we are, what is incomplete, what risks exist, what evidence we have, and what next action you recommend” using verified project state—not invented defaults—and continue the same work when the architect moves from field to office.

---
