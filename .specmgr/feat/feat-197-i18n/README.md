---
classification: null
created: '2026-10-29T11:14:24.992+01:00'
id: feat-197-i18n
status: planning
type: feat
updated: '2026-10-29T11:14:31.085+01:00'
version: 1.0.0
---

# Feature: I18n: Multi-Language Support of the Same Artifact

## Plan

### Overview

specmgr artifacts currently live as a single file per id under `./docs/{type}/`, holding content in exactly one (implicitly English) language. This feature adds first-class support for multiple language variants of the *same* artifact: the same uuid is reused across every language copy, the document schema (frontmatter fields and body section structure) stays identical regardless of language, and only the prose content is translated. English (EN) remains the default/primary language and keeps its existing, unchanged location (`./docs/{type}/`); other languages are added as `./docs/{type}/{language}/` subfolders. The feature also adds command/skill/agent support for translating an artifact into a new language, detecting drift between a translation and its EN source (structural and staleness), and listing the languages available for a given artifact.

### Requirements

- REQ-001: A language variant of an artifact is stored at `./docs/{type}/{language}/`, using the exact same filename/id as its EN source; the existing `./docs/{type}/` location and its contents remain unchanged and continue to mean the default (EN) language.

- REQ-002: All language variants of the same artifact share the same `id` (uuid, or the domain's own id form for `feat`); the `id` is never language-qualified.

- REQ-003: The YAML frontmatter schema and the document's body section headings/order are structurally identical across every language variant of a given domain; only free-form prose content (and, where unavoidable, the literal heading text itself) differs between languages.

- REQ-004: A per-language heading-mapping table resolves a translated section heading back to its canonical English schema key, so parsers/validators keep working against one canonical key set regardless of the file's language.

- REQ-005: `get_<d>`/`list_<d>` (every whole-body domain: req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs) accept an optional `language` parameter (default `"en"`); omitting it preserves today's exact behavior and output.

- REQ-006: `create_<d>`/`update`/`set_status`/`set_classification`/`delete` accept the same optional `language` parameter, writing to (or acting on) the correct `./docs/{type}/{language}/` path for a non-default language while leaving the default-EN behavior unchanged when `language` is omitted.

- REQ-007: ADR is explicitly excluded from this feature's scope; `adr`-domain tools/resources are not modified.

- REQ-008: A new command/skill/agent provides a translation workflow: given an artifact's `type`/`id` and a target `language`, it produces a new (or updates an existing) language variant from the current EN (or other source-language) content.

- REQ-009: A new command/skill/agent (or tool) lists the languages currently available for a given artifact `type`/`id`.

- REQ-010: A new command/skill/agent (or tool) detects drift between a translated variant and its EN source: (a) structural drift -- a missing/extra/reordered section relative to the canonical EN schema, and (b) staleness -- the EN source's `updated` timestamp is newer than the translation's own `updated` timestamp.

### Acceptance Criteria

- [ ] ACC-001: Creating/reading a non-EN language variant resolves to `./docs/{type}/{language}/{id}.md` (or the domain's existing filename convention), while EN continues to resolve to the existing `./docs/{type}/{id}.md` path, unchanged.

- [ ] ACC-002: Two language variants of the same artifact have identical `id` values in their frontmatter.

- [ ] ACC-003: A translated document's section headings, even if rendered in the target language, resolve via the heading-mapping table to the same canonical schema keys the EN parser uses, and the document validates against the same Pydantic schema as its EN counterpart.

- [ ] ACC-004: Calling `get_<d>(id, language="de")` (for at least one pilot domain) returns the German variant's content; calling `get_<d>(id)` (no `language`) is unaffected and still returns the EN content exactly as before this feature.

- [ ] ACC-005: A drift-detection tool run against a deliberately out-of-sync translation reports both the structural mismatch and the staleness condition.

- [ ] ACC-006: A translation command run against an EN artifact produces a new, schema-valid language variant sharing the same id.

### Scope

#### Included

- Directory convention `./docs/{type}/{language}/` for non-default languages; EN stays at `./docs/{type}/`.

- Shared-uuid, shared-schema multi-language model for every whole-body domain (req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs).

- Per-language section-heading mapping table resolving translated headings to canonical schema keys.

- `language` parameter plumbed through the relevant read tools (`get_<d>`, `list_<d>`) and write tools (`create_<d>`, `update`, `set_status`, `set_classification`, `delete`).

- A translation command/skill/agent.

- A drift-detection command/skill/agent (structural + staleness).

- A language-listing command/skill/agent (or tool) for a given artifact.

#### Explicitly Out Of Scope

- The `adr` domain (ADR stays single-language, consistent with its existing exclusion from most other generic cross-cutting mechanisms in this codebase).

- Any guarantee of machine-translation quality, fluency, or semantic accuracy -- this feature provides the mechanism/plumbing, not a translation-quality assurance.

- RTL layout or any UI/rendering-level localization concern -- this is document-content i18n, not UI localization.

### Dependencies

#### Depends On

- (none identified yet)

### Design Notes

Open design questions to resolve during Phase 100 below:

- Exact on-disk filename for a language variant (same basename as EN, just under the `{language}` subfolder, is the working assumption).
- Exact shape and storage location of the per-language heading-mapping table (e.g. one mapping file per language under a shared config location, vs. embedded per-domain).
- Whether `language` codes follow a fixed vocabulary (e.g. ISO 639-1 two-letter codes) or are free-form.
- How `list_<d>` should behave when asked to list across all languages at once vs. a single language.

### Related Decisions

- (none yet -- an ADR may be warranted once the heading-mapping-table storage design is settled)

### Task List

#### Phase 100: Design -- Directory Layout, Heading-Mapping Table, Language Vocabulary

- [ ] Task 100.100: Finalize the on-disk filename/path convention for a language variant (`./docs/{type}/{language}/{id}.md`) and confirm it against every whole-body domain's existing path-resolution code (`general/tools/_doc_paths.py`, `feat/tools/_paths.py`).

- [ ] Task 100.110: Design the per-language heading-mapping table format and storage location, and how a parser resolves a translated heading back to its canonical schema key.

- [ ] Task 100.120: Decide the language-code vocabulary (e.g. ISO 639-1) and where it is validated.

- [ ] Task 100.130: Write an ADR capturing the directory-layout and heading-mapping-table design decisions.

#### Phase 110: Path Resolution & Read-Side Plumbing

- [ ] Task 110.100: Extend `general/tools/_doc_paths.py` (and `feat/tools/_paths.py`) to resolve a document path given `type`/`id`/optional `language`.

- [ ] Task 110.110: Add the optional `language` parameter to `get_<d>` for every whole-body domain, defaulting to `"en"` with unchanged behavior when omitted.

- [ ] Task 110.120: Add the optional `language` parameter to `list_<d>` for every whole-body domain.

- [ ] Task 110.130: Extend the markdown parser layer to apply the heading-mapping table when parsing a non-EN document.

#### Phase 120: Write-Side Plumbing

- [ ] Task 120.100: Add the optional `language` parameter to `create_<d>` for every whole-body domain.

- [ ] Task 120.110: Add the optional `language` parameter to the generic `update`, `set_status`, `set_classification`, and `delete` tools.

- [ ] Task 120.120: Extend `DocCache` keying to be language-aware so cache entries for different languages of the same id never collide.

#### Phase 130: Translation Command/Skill/Agent

- [ ] Task 130.100: Design and implement the translation command/skill (or MCP tool) that produces/updates a target-language variant from a source document.

- [ ] Task 130.110: Add an OpenCode skill and/or command surface for the translation workflow.

#### Phase 140: Drift Detection & Language Listing

- [ ] Task 140.100: Implement structural drift detection (missing/extra/reordered sections vs. the canonical EN schema).

- [ ] Task 140.110: Implement staleness detection (EN `updated` timestamp newer than the translation's `updated`).

- [ ] Task 140.120: Implement a language-listing tool/command for a given artifact `type`/`id`.

- [ ] Task 140.130: Add an OpenCode skill and/or command surface for drift-detection and language-listing.

#### Phase 150: Tests & Documentation

- [ ] Task 150.100: Unit tests for path resolution, read/write `language` plumbing, and cache keying across at least one pilot domain, then extended to all whole-body domains.

- [ ] Task 150.110: Unit tests for the translation, drift-detection, and language-listing workflows.

- [ ] Task 150.120: Update `AGENTS.md`, `README.md`, and generated docs (`specmgr docs`) to describe the new `language` parameter and i18n workflows.

## Progress

### Current Status

**As of 2026-10-29**: Feature drafted from GitHub issue #197; design not yet started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-29 11:14:24.992+01:00 - Created

Feature drafted from GitHub issue #197 ("I18n: multi-language support of the same artifact"). Directory layout `./docs/{type}/{language}/` locked in (EN unchanged at `./docs/{type}/`); shared-uuid/shared-schema model confirmed; ADR excluded from scope; translation, drift-detection (structural + staleness), and language-listing all confirmed in scope for this feature, with both read- and write-side `language` parameter support.

### Related PRs / Commits

- [Issue #197](https://github.com/dfch/biz.dfch.SpecMgr/issues/197): tracking issue for this feature.
