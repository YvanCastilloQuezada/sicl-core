# ARKI Copilot CP-00 — Evidence-Based Initial Audit

**Branch:** feat/arki-copilot-foundation-cp00-06
**Audit date:** 2026-11-26
**Scope:** SICL-Core and SICL-Web GitHub main branch source review. No server runtime tests or repository modifications on main.

## Verified source observations

### SICL-Core
- api/main.py registers projects, commands, v1, continuity, and gis_copilot routers.
- api/deps.py creates one shared SQLiteRepository and reads its path from SICL_DB_PATH, then DATABASE_URL for SQLite, otherwise defaults to sicl.sqlite.
- src/sicl/repository.py is the main SQLite repository and contains schema state detection and migration logic. Its schema versioning currently recognizes the existing core schema states; avoid adding Copilot tables directly to the core schema migration without a migration review.
- api/routes/continuity.py is a project-scoped continuity event API. It requires SICL_CORE_SERVICE_TOKEN, verifies project existence, stores canonicalized continuity events in the existing events ledger, fingerprints content with SHA-256, and uses event IDs/idempotency keys. It is append-only.
- api/routes/gis_copilot.py and src/sicl/copilot.py are specialized GIS/SICL translator paths, not the general conversational session API.
- RFC-014 proposes CopilotSession, CopilotMessage, CopilotSuggestion, CopilotExplanation and API routes but explicitly says these entities/endpoints are not implemented in that RFC.

### SICL-Web
- client/src/components/CopilotPanel.tsx exists as the desktop conversational UI candidate.
- client/src/components/CommandBar.tsx contains separate conversational-intake and multimodal candidate flows.
- client/src/pages/ArkiCockpitPage.tsx currently connects Copilot messages to a translation/generation flow; CP-01 must separate conversation from execution.
- The existing components are candidates for reuse, not design constraints.

## Classification

| Capability | Status based on source review |
|---|---|
| Desktop chat surface | Implemented UI candidate |
| Voice input | UI capability candidate; integration must be runtime verified |
| Multimodal intake | Separate existing flow candidate |
| General conversation API | Not verified as implemented |
| Server-authoritative Copilot sessions | Not verified as implemented |
| Shared mobile/desktop session | Not verified as implemented |
| Copilot attachment storage lifecycle | Not verified as implemented |
| End-user/project authorization for Copilot session endpoints | Not verified as implemented |
| Conversation/execution separation | Gap identified in current web flow |
| Execution fail-closed contract | New CP-01 policy module and tests added on working branch; not yet locally executed |

## CP-00 follow-up requirements

1. Complete user/actor auth audit in Web and Core before implementing session endpoints.
2. Inspect attachment storage and upload policies, including file type/size, ownership, access, retention, and deletion.
3. Inspect backup/restore and migration procedures.
4. Establish server-side project membership/authorization contract.
5. Keep continuity event ledger separate from conversation messages.
6. Verify current Copilot UI, microphone, image capture, and endpoints with local runtime evidence before reuse.

## Boundaries

This audit does not claim the code was executed, tests were run, or mobile/Desktop runtime behavior was verified. It is a GitHub source inspection only.
