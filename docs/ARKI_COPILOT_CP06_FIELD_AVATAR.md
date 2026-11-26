# ARKI Copilot CP-06 — Field Avatar, Multimodal Capture, and Mobile Continuity

**Status:** Design proposal.
**Branch:** feat/arki-copilot-foundation-cp00-06

## Product intent

The Avatar is the field-oriented Copilot experience on a mobile phone. It is not a separate assistant or a second memory. It is a mobile interaction mode connected to the same server-authoritative Copilot session/context as ARKI Office.

The Office Copilot is a floating desktop panel with text and optional microphone input. Avatar opens the field experience and closes it when dismissed. One active shared assistant/session identity; two surfaces optimized for different work environments.

## Interaction surfaces

### ARKI Field — Avatar

- Mobile-first, full-screen or focused overlay optimized for one-handed use.
- Large touch targets and minimal typing.
- Conversational voice interaction where supported.
- Capture one or multiple photos; attach to a message or observation.
- Preview, remove, reorder, and confirm photos before submission.
- Optional location capture only with explicit permission and visible indication.
- Field note text and voice transcription.
- Session/project selector or clear current-project context.
- Show upload progress and retry state.
- Show whether an item is captured locally, uploaded, attached, processed, or saved.
- Dismiss/close without losing unsent draft/captures; persistence behavior must be explicit.

### ARKI Office — Floating Copilot

- Persistent floating panel in desktop UI, not a dedicated navigation tab.
- Conversation history, text entry, optional microphone, file/image upload.
- Project context visible and switchable.
- Drag/resize/minimize/close behavior defined by UX; avoid blocking main design workspace.
- Keep context/session linked with Field mode.
- Tool/action approval cards and result/evidence cards appear in the conversation.

## Shared session behavior

- Both surfaces use the same authenticated session, project scope, and server-side conversation store.
- Channel metadata (FIELD/OFFICE) is observational, never a permission grant.
- Messages and attachments are ordered by server sequence.
- Idempotency keys prevent duplicate uploads/messages during network retries.
- Switching devices does not fork the conversation unless user explicitly starts a new session.
- Draft state may be device-local until submitted; label it clearly.
- Server acknowledgment distinguishes accepted message from pending processing and completed response.

## Capture lifecycle

1. User opens Avatar.
2. Confirm active project/session and context.
3. Capture photo(s), voice, or text.
4. Preview attachments and optional note.
5. Submit as one message with attachment references.
6. Upload attachments into staging with size/type validation and integrity hash.
7. Bind validated staged attachments to message atomically.
8. Copilot analyzes only after upload/binding succeeds.
9. Return analysis with observed/inferred/unknown distinctions and follow-up questions.
10. Save selected field observation to project knowledge only under explicit save/authorization policy.

## Field observation record

- observation ID and timestamp
- actor/user
- project ID (optional but validated)
- session ID/message ID
- attachment IDs
- location and precision, only if consented
- transcription/note
- observations with confidence/provenance
- inferences and questions
- review/approval status
- source capture metadata

## Offline/network behavior

- Do not claim server-side processing while offline.
- Queue unsent drafts/captures only if supported and protected by local storage policy.
- Display offline, queued, uploading, submitted, processing, and completed states distinctly.
- Retry only idempotent operations.
- Provide explicit user control to discard unsent capture.
- Avoid retaining sensitive photo/location data longer than necessary; retention and deletion controls must be implemented.

## CP-06 acceptance criteria

1. Avatar opens the Field surface and can be dismissed.
2. Mobile UI supports capture and preview of multiple images.
3. Images are not analyzed before successful upload and message acceptance.
4. Attachment validation and size limits enforced server-side.
5. Network retries do not duplicate messages/attachments.
6. Session continuity works with Office surface.
7. Voice capability is device/browser-tested and has visible fallback to text.
8. Location is opt-in, permission-based, and not silently collected.
9. User can identify draft vs sent vs processed content.
10. Field observation facts/inferences/questions are distinct and reviewable.
11. Session/project permissions apply equally across surfaces.
12. No mobile surface can bypass capability authorization or action gates.


## CP-06 implementation checkpoint — 2026-11-26

Added `src/sicl/copilot_field.py` capture metadata and lifecycle contract: local draft, upload, uploaded acknowledgement, message attachment, processing, completed, failed, and cancellation states. Invalid transitions fail; remote lifecycle states require remote asset/message IDs; location captures require explicit consent and valid coordinates. This is metadata only: mobile UI, offline queue, binary upload, server staging, image/audio processing, retry/backoff and synchronization are not implemented. Tests authored but not executed.
