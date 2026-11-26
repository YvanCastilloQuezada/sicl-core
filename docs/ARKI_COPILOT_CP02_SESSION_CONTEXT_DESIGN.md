# ARKI Copilot CP-02 — Shared Session and Context Persistence

**Status:** Design proposal; implementation gated by auth, migration, and attachment-storage audit.
**Branch:** feat/arki-copilot-foundation-cp00-06

## Objective

Create server-authoritative conversation continuity between ARKI Field (Avatar/mobile) and ARKI Office (floating desktop Copilot). Both interfaces operate on the same session and project context; neither browser/device is the persistence authority.

## Findings from CP-00

- SICL-Core currently initializes a shared SQLiteRepository through api/deps.py.
- The database path is configured via SICL_DB_PATH, DATABASE_URL, or defaults to sicl.sqlite.
- The existing repository owns project state and event data.
- api/routes/continuity.py provides an authenticated append-only project continuity event API with idempotency keys, hashes, and event sequence numbers.
- The continuity event API is not a conversational store. Do not store message bodies, attachments, or conversation state in its event payloads as a shortcut.
- CopilotSession / CopilotMessage are described in RFC-014, but that RFC states these are proposals and not implemented.
- The current Core's API service authentication is not sufficient evidence of end-user authorization. CP-02 must audit and integrate actual user/project access control before exposing session APIs.

## Proposed storage boundary

Use a dedicated Copilot persistence module and dedicated Copilot tables in the same SQLite database file initially, with a separate schema version/migration mechanism. Avoid altering existing canonical SICL tables or the repository's current migration version. The exact migration strategy must be reviewed and tested on a copy of the database before implementation.

Candidate tables:

### copilot_sessions

- session_id — stable opaque identifier, primary key
- project_id — nullable project FK/reference; validate project existence when supplied
- owner_actor_id — authenticated actor/user identifier
- title — optional short title
- status — ACTIVE, ARCHIVED, or CLOSED
- created_at, updated_at — UTC timestamps
- last_message_at — UTC timestamp
- context_revision — optimistic revision counter
- contract_version — contract identifier/version
- client_origin — metadata such as FIELD/OFFICE; never authorization

### copilot_messages

- message_id — stable opaque identifier, primary key
- session_id — FK to session
- sequence — per-session monotonic order, unique
- role — architect, copilot, system, or tool
- content — text; attachment-only messages may be empty
- intent — nullable intent assessment label
- intent_confidence — nullable, bounded 0–1
- intent_ambiguous — boolean
- created_at — UTC timestamp
- metadata_json — allow-listed metadata only; no secrets

### copilot_attachments

- attachment_id — stable opaque ID, primary key
- message_id — nullable during upload staging; bind atomically when message accepted
- session_id — session reference
- owner_actor_id — authenticated actor
- storage_key — opaque key; never expose server filesystem path
- filename — sanitized display name
- media_type — validated server-side
- byte_size — validated size
- sha256 — integrity fingerprint
- created_at — UTC timestamp
- state — STAGED, ATTACHED, REJECTED, or DELETED

Binary media storage location remains a separate decision. Never store unbounded image/file blobs in message JSON. Storage must enforce quotas, allowed types, size limits, scanning, ownership, access checks, and retention/deletion policy.

## Context model

Context is assembled on demand from explicitly authorized sources and carries provenance. The initial resolver may return:

- Project identity and confirmed project metadata
- Current ARKI module/phase, if available and verified
- Recent conversation messages
- Confirmed facts, proposals, assumptions, decisions, and conflicts
- Relevant field observations/attachments
- Pending questions/tasks and references to evidence
- Explicit user-provided context

Do not indiscriminately include the entire project database or all prior conversations in every model prompt. Context should be bounded, relevant, inspectable, and versioned. Summaries are derived artifacts with provenance and must not overwrite source messages.

## API proposal (not yet implemented)

- POST /v1/copilot/sessions — create a session
- GET /v1/copilot/sessions — list sessions for authorized actor, optionally filtered by project
- GET /v1/copilot/sessions/{session_id} — session metadata
- PATCH /v1/copilot/sessions/{session_id} — title/status changes with validation
- GET /v1/copilot/sessions/{session_id}/messages — paginated messages
- POST /v1/copilot/sessions/{session_id}/messages — accept user message, optional attachment IDs, idempotency key
- POST /v1/copilot/sessions/{session_id}/attachments — staged attachment upload

All endpoints require verified actor authentication and project/session authorization. Session ownership and project membership are server-checked. Client-provided project IDs, actor IDs, context, or intent labels are never trusted as authorization.

## Reliability and security

- Per-session sequence allocation must be transactionally safe.
- Message submission requires an idempotency key to avoid duplicate sends on mobile retry.
- Session and message access must be ownership-scoped.
- Attachment staging and binding must be atomic or recoverable; orphan cleanup is required.
- Request and upload limits are mandatory.
- Content is treated as untrusted input. Prompt-injection text inside attachments cannot override system policy or tool permissions.
- Secrets and credentials are excluded from persisted metadata and model context.
- Audit events should record tool/action metadata and outcomes, not leak full private conversation text.
- Retention and deletion must be defined before shipping; archive/close alone is not deletion.
- Cross-device resume must be tested for authorization isolation.

## Migration safety

- Do not change the existing SICL schema version without a separate migration review.
- Copilot schema migrations must be additive, deterministic, idempotent, and reversible where possible.
- Test against: fresh database, legacy database, already-migrated database, malformed/partial Copilot schema, duplicate session/message requests, concurrent writes, and upgrade rollback.
- Back up the database and verify the backup before any migration against production.

## CP-02 acceptance criteria

1. Create a session with an optional project reference.
2. Reject project references that do not exist or cannot be accessed.
3. List and retrieve sessions only for the authorized actor.
4. Append messages in stable order with retry-safe idempotency.
5. Resume a session on a second device/browser without local-storage dependence.
6. Accept attachment-only messages through staged, validated attachment IDs.
7. Preserve provenance and distinguish user facts from AI proposals.
8. Context resolver returns only authorized, relevant, bounded context.
9. Tests prove unauthorized actor cannot read/write sessions, messages, or attachments.
10. Existing SICL migrations, event ledger, project commands, and geometry authority remain unchanged.

## Decision gate before coding persistence

Complete audit of authentication/actor identity in SICL-Web and SICL-Core, attachment handling/storage, database backup/migration behavior, and endpoint access pattern. If a dedicated Copilot DB is safer than additive tables, evaluate it against the same access-control and backup requirements; do not split databases merely for aesthetic modularity.
