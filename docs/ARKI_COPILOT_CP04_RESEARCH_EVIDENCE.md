# ARKI Copilot CP-04 — Research, Documents, Evidence, and Sources

**Status:** Design proposal.
**Branch:** feat/arki-copilot-foundation-cp00-06

## Goal

Give Copilot a reliable research and document-analysis capability for architecture, urban planning, projects, regulations, and field evidence. The capability must separate what a source says from interpretation and recommendation.

## Research request lifecycle

1. Clarify scope and geographic jurisdiction where necessary.
2. Resolve source classes and required freshness (regulation, official, academic, precedent, product, user-provided).
3. Search through approved connectors/providers.
4. Collect source metadata and retrieval timestamp.
5. Extract text/tables/visual content where supported.
6. Normalize without altering source meaning.
7. Store source references and fingerprints; avoid duplicating full copyrighted content.
8. Build evidence records with exact quoted spans only where allowed.
9. Analyze and synthesize across sources.
10. Present findings with citations, conflicts, limitations, and confidence.
11. Preserve selected evidence as project-linked knowledge only after user approval or explicit save.

## Evidence record

Each evidence record should include:

- evidence_id
- project_id/session_id association (optional)
- source_type (official, regulation, academic, web, user_file, field_capture, other)
- source_locator (URL, file reference, page/section, or capture ID)
- source_title and author/publisher if available
- retrieved_at and publication/effective date when available
- content fingerprint
- extracted claim(s)
- excerpt/span locator
- verification status
- relevance rationale
- known limitations
- linked fact/proposal/decision IDs

Do not mark a source as verified solely because a search result snippet exists. Verification levels should reflect actual inspection.

## Regulation handling

- Detect jurisdiction and regulation date/version.
- Prefer official primary sources for legal/normative claims.
- Extract relevant articles/sections and preserve locator.
- Distinguish binding requirements, guidance, proposals, and standards.
- Do not assume applicability until project type, location, use, and other necessary facts are confirmed.
- Flag contradictions, superseded versions, and missing information.
- If the applicable version is uncertain, ask or report the uncertainty.

## Document and image analysis

Input types (subject to actual available tool support):

- PDF, DOCX, XLSX, PPTX
- text and structured reports
- photos, screenshots, drawings, plans
- voice transcriptions
- scanned pages

Analysis outputs:

- document summary with source/page references
- extracted entities, requirements, quantities, dates, constraints
- table extraction with confidence and review status
- observed visual features versus inferred features
- missing information and contradictions
- action items and candidate project facts

Never silently convert a low-confidence visual inference into a confirmed fact. OCR and vision output are evidence-derived, not authoritative by default.

## Search and synthesis modes

- **Quick answer:** bounded sources, concise answer and citations.
- **Research brief:** question, method, findings, sources, limitations.
- **Comparison:** criteria table and source-level support.
- **Regulatory check:** jurisdiction, applicable provisions, facts needed, preliminary status.
- **Precedent study:** context, strategy, spatial/urban response, transferability, caveats.
- **Project document review:** findings by section, risks, omissions, contradictions, and actions.

## CP-04 acceptance criteria

1. Claims derived from sources have source references.
2. Source and retrieval dates are recorded where available.
3. User-uploaded sources are attributed to the upload.
4. Search snippets alone are not treated as inspected evidence.
5. Conflicting sources are surfaced, not collapsed.
6. Regulatory version and jurisdiction are explicitly handled.
7. Inferences are labelled separately from observations and sourced facts.
8. Missing/uncertain inputs remain visible.
9. Saved project knowledge retains provenance.
10. Tests cover stale source, conflict, unsupported claim, missing citation, and unverified visual inference.
