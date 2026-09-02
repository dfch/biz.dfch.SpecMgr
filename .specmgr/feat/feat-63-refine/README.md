---
classification: null
created: '2026-09-02 18:59:00.421+02:00'
id: feat-63-refine
status: planning
type: feat
updated: '2026-09-02 21:17:10.917+02:00'
version: 1.0.0
---

# Feature: Create Commands for Requirement Elicitation

## Plan

### Overview

This feature designs and implements a family of MCP prompts/commands for AI-supported requirements elicitation, following the workflow pioneered by the external `biz.dfch.IncoseIso25010Refiner` repository (which this feature lets us retire once its replacement commands are complete; recon of that repository is documented in this feature's QA transcript). The command family is broader than a single "refine" step. At a high level, the intended flow is: (a) `/refine` reads an existing `qa` document (or starts a new one) and asks additional questions across all or a specified subset of the 9 ISO 25010:2023 characteristics; (b) once a single `qa` document's answers are considered complete, `/resolve` reads that one `qa` document directly and creates the actual `req`/`dec`/`rsk`/`gol` (etc.) artifacts from its answered pairs -- with no intermediate document-inlined representation, and with one `qa` pair free to produce more than one artifact, including artifacts of different types (for example both a REQ and a DEC from the same answer); (c) a separate cross-check command reconciles any additional `qa` document against artifacts already created from earlier `qa` documents, to catch likely duplicates or conflicts before creating anything new from it; and (d) created artifacts get added to or referenced from a design document (for example a "sysrs" system requirements specification, itself still under separate, ongoing implementation and expected to land before this feature reaches its own implementation phases). All of this must work in multiple target languages (at minimum EN, DE, FR), with the EN version kept as the source of truth and written in ASD-STE100-controlled English via the `asdste100` MCP as-is -- that server owns and decides its own fixed vocabulary; there is no user- or agent-supplied vocabulary support. The existing `refine` prompt already in this repo has been reviewed as part of the design; the decision is to keep it, with small updates (see Decisions Made).

### Requirements

- REQ-001: Recon and document every capability/command the existing `biz.dfch.IncoseIso25010Refiner` repository provides (not only "refine", but also "resolve" and any others), before designing this repo's own commands.
- REQ-002: Provide a prompt/command (`/refine`) that reads an existing `qa` document (or starts a new one) and asks additional questions, across all or a specified subset of the 9 ISO 25010:2023 characteristics.
- REQ-003: Provide a prompt/command (`/resolve`) that operates on exactly one `qa` document and creates the actual REQ/DEC/RSK/GOL (etc.) artifacts directly from its answered pairs, with no intermediate document-inlined representation.
- REQ-004: A single `qa` pair may produce more than one artifact, and those artifacts may be of different types (for example a REQ and a DEC derived from the same answer).
- REQ-005: Provide a way to add or reference created REQ/DEC/RSK/GOL (etc.) documents in a design document (for example a "sysrs" system requirements specification, once that document type exists).
- REQ-006: Support producing elicitation output in multiple target languages (at minimum EN, DE, FR), while keeping the EN version as the source of truth.
- REQ-007: Enforce ASD-STE100 controlled English (via the `asdste100` MCP) for the EN source-of-truth text, using that server's vocabulary as-is -- there is no user- or agent-supplied vocabulary support.
- REQ-008: Review the existing `refine` prompt already in this repo as part of the design, and decide whether to keep, change, or retire it.
- REQ-009: Provide a separate prompt/command that cross-checks a `qa` document's content against artifacts already created from other `qa` documents, to catch likely duplicates or conflicts before creating new artifacts from it.
- REQ-010: When `/resolve` creates artifacts from a `qa` pair, it must add a leading comment directly in front of that pair, referencing every artifact created from it, so re-running `/resolve` does not create duplicates.

### Acceptance Criteria

- [x] ACC-001: The recon task has produced a written summary of every capability/command the existing `biz.dfch.IncoseIso25010Refiner` repository provides.
- [ ] ACC-002: A `/refine` prompt exists that reads an existing `qa` document (or starts a new one), can target all or a specified subset of the 9 ISO 25010:2023 characteristics, and results in a valid `qa` document (per `validate_qa`).
- [ ] ACC-003: A `/resolve` prompt exists that operates on exactly one `qa` document and creates one or more valid REQ/DEC/RSK/GOL documents directly from its answered pairs, with no intermediate document-inlined representation.
- [ ] ACC-004: A single `qa` pair can be exercised to produce more than one artifact, including artifacts of different types (for example a REQ and a DEC from the same pair).
- [ ] ACC-005: Created REQ/DEC/RSK/GOL documents can be added to or referenced from a design document (for example a "sysrs" system requirements specification).
- [ ] ACC-006: Elicitation output can be requested in EN, DE, or FR, with the EN version validated against ASD-STE100 rules.
- [x] ACC-007: The existing `refine` prompt has been reviewed, and a decision (keep/change/retire) is documented in this feature's Decisions Made.
- [ ] ACC-008: A cross-check prompt/command exists that compares a `qa` document's content against artifacts already created from other `qa` documents and flags likely duplicates or conflicts before any new artifact is created from it.
- [ ] ACC-009: Every artifact `/resolve` creates is referenced by a leading comment directly before its originating `qa` pair, listing every artifact created from that pair; re-running `/resolve` does not duplicate already-referenced artifacts.

### Scope

#### Included

- Design of the elicitation command family (recon, refine, resolve-to-artifacts, cross-check-against-existing-artifacts, add-to-design-document).
- Implementation of the elicitation command family once the design is decided -- this feature covers both design and implementation; see Decisions Made for the phasing rationale.
- Multi-language output (EN/DE/FR) with EN as source of truth.
- ASD-STE100 enforcement for the EN source-of-truth text, using the `asdste100` MCP server's own vocabulary as-is (no user-supplied vocabulary support).
- Reviewing, and if needed changing, the existing `refine` prompt.

#### Explicitly Out Of Scope

- Retiring/removing the external `biz.dfch.IncoseIso25010Refiner` repository itself -- that happens only after this feature's replacement commands are complete, per the issue.
- Any artifact-type (REQ/DEC/RSK/GOL/QA) schema changes not directly required by the elicitation workflow -- those are handled by their own domain features.
- Designing or implementing the "sysrs" system requirements specification document type itself -- it is being built separately and is expected to exist before this feature's implementation phases; this feature only adds/references it once available.
- Any access-control or configurability mechanism for ASD-STE100 vocabularies -- the `asdste100` MCP server's vocabulary is used as-is and is not user- or project-configurable.

### Dependencies

#### Depends On

- The external `biz.dfch.IncoseIso25010Refiner` repository (https://github.com/dfensgmbh/biz.dfch.IncoseIso25010Refiner) -- source of the workflow/approach being ported, and the recon target for Phase 1.
- The already-implemented `qa`, `req`, `dec`, `rsk`, and `gol` domain packages in this repo -- the artifact types the elicitation commands read from and create.
- The `asdste100` MCP server -- required for ASD-STE100 enforcement of the EN source-of-truth text.
- The "sysrs" system requirements specification document type -- being implemented separately; expected to be available before this feature's implementation phases begin (REQ-005/ACC-005).

### Design Notes

The full requirements-elicitation Q&A transcript backing this feature's Overview, Requirements, Scope, and Task List choices above is recorded in QA document `f58fe807-7485-4513-812d-37d8d1e9cdb1` ("feat-63-refine — Requirements Elicitation Q&A Transcript", status `active`) -- as of this update, every question in that transcript has an answer; there are no remaining open points. Phase 1 (Design) treated that document as its own working backlog while questions remained open, updating both that QA document and this feature's own sections as each point was resolved.

**Recon of `biz.dfch.IncoseIso25010Refiner` (completed 2026-09-02), so a future agent does not need to re-read that repository.** It is a `typer` CLI built around one artifact per session: a single `source.md` file at `<workspace>/<session-id>/source.md` that accumulates state across the whole cycle -- questions live inline as `>` block-quote lines, and a human types the answer directly below them, by hand.

Its command family: `init` creates a session and seeds `source.md` from `--input` (default characteristics = all 9 ISO 25010:2023 ones). `refine` sends the whole doc to an LLM, which classifies sentences against the 9 characteristics, generates N questions per characteristic with a completeness score, appends the new questions as `>` lines, and auto-translates stray non-English sentences to English (keeping the original in parens). `resolve` finds every question that already has an answer, sends each Q+A pair through a strict rewrite prompt (no passive voice, "must" not "shall", no "-ing", no Saxon genitive, no semicolons, force US English but preserve quoted foreign text), and replaces the Q+A pair in place, inside the same `source.md`, with the resulting single requirement sentence (`-k/--keep` preserves unanswered questions instead of deleting them). `checkpoint`/`restore`/`diff`/`show` are a bespoke version-control-lite for `source.md` (snapshot/revert/delta/print). `summary` restructures the whole resolved doc into a clean Markdown summary, pushing any still-unanswered questions to the end. `translate` is a separate, explicit step (EN summary -> `DE`/`FR`/`IT`/... via a dedicated translation-only LLM call) -- EN is implicitly the working language throughout refine/resolve/summary. `jira` parses the summary's Markdown sections and files one Jira issue per section. `list`/`info`/`erase` are session housekeeping. `replay` re-applies a previously saved raw LLM JSON response without a new LLM call. `query`/`vector`/`stub` are debug/testbed commands, not part of the end-user workflow. `validate` checks a file is valid JSON. `ui` is a TUI/GUI alternative to hand-editing `source.md` directly.

Why this mattered for our own design: their `Iso25010` enum's 9 characteristic strings are byte-identical to our own `qa` v2 schema's category names -- direct precedent, not a coincidence. Their `--language` CLI option (case-insensitive exact/prefix match against `EN`/`DE`/`FR`/`IT`, `REQ_LANGUAGE` env fallback) is a real precedent for our own language-parameter decision (see Decisions Made). Their `resolve` destroys the original Q&A text by design, because `source.md` is the only record they keep -- our `qa` documents never lose that text, which is exactly why we dropped their intermediate "resolve into a rewritten sentence, still inside the same document" step (see Decisions Made: two-step command design). Their `prompt-resolve.md`/`prompt-summary.md` style rules are a hand-rolled, partial reinvention of ASD-STE100 -- this directly validates REQ-007's plan to use the real `asdste100` MCP instead (used as-is, with no equivalent to their hand-rolled rule set). Their `checkpoint`/`restore`/`diff` versioning has no equivalent need in specmgr, since we already rely on git for that. Their closest analog to "create actual REQ/DEC/RSK/GOL documents" is `jira` (summary -> one Jira issue per section) -- they have no first-class document-creation step of their own to adapt from, so REQ-003/004/009/010 are a genuinely fresh design, not a port.

**Existing `refine` prompt review (Task 1.2, completed 2026-09-02).** `qa/prompts/refine.py` plus its packaged instructions (`qa/data/qa_refine_instructions.md`) already match the new design closely: it only appends new, unanswered `_(awaiting response)_` placeholder questions to an existing `qa` document, already supports targeting a named subset of the 9 ISO/IEC 25010:2023 characteristics (plus `Elicitation Context`) via its free-text `scope` parameter, grounds each question in the `specmgr://iso25010` resource, and already defers entirely to `/resolve` as the next step without attempting to run it. The decision (see Decisions Made) is to keep it with two small updates once `/resolve` exists: add target-language selection (EN/DE/FR, per the resolution order in Decisions Made), and update its final "next step" text to describe `/resolve`'s actual behavior (create artifacts directly, plus leading-comment traceability).

### Task List

#### Phase 1: Design

- [x] Task 1.1: Recon the existing `biz.dfch.IncoseIso25010Refiner` repository and document every capability/command it provides (not only "refine", but also "resolve" and any others).
- [x] Task 1.2: Review the existing `refine` prompt in this repo and assess whether/how it should change in light of the recon findings.
- [ ] Task 1.3: Decide the technical approach for `/refine` (reading an existing `qa` document, targeting all or a specified subset of the 9 ISO 25010:2023 characteristics) and `/resolve` (operating on exactly one `qa` document, creating REQ/DEC/RSK/GOL artifacts directly from its answered pairs with no intermediate document-inlined representation, supporting one pair producing more than one artifact of possibly different types).
- [x] Task 1.4: Design the cross-check command that reconciles an additional `qa` document against artifacts already created from other `qa` documents, and the leading-comment convention `/resolve` uses to reference every artifact created from a `qa` pair (for traceability and to prevent duplicate re-resolution). Also decide how created documents get added to a design document (e.g. "sysrs"), how multi-language (EN/DE/FR) output is produced and stored, and how ASD-STE100 enforcement (via the `asdste100` MCP) is wired into the EN source-of-truth text.
- [ ] Task 1.5: Document the chosen design in this feature's Design Notes (or a dedicated ADR, if the decision is architecture-level per this repo's ADR-vs-feature-log rule), and append the implementation phases to this feature's Task List.

## Progress

### Current Status

**As of 2026-09-02**: Design decisions are now recorded for every point raised during elicitation (see Decisions Made): single-feature phasing; per-conversation language selection via a shared parameter, with no cross-session persistence; a two-step `/refine`+`/resolve` command design with a separate cross-check command and comment-based traceability; `sysrs` treated as an external, not-yet-existing artifact type this feature only references, not designs; ASD-STE100 used as-is with no user-supplied-vocabulary support; and the existing `refine` prompt kept, with two small updates pending `/resolve`'s design. Tasks 1.1, 1.2, and 1.4 are done. The QA transcript (`f58fe807-7485-4513-812d-37d8d1e9cdb1`) has no remaining open points. Remaining open work for Phase 1: decide `/refine`/`/resolve` concrete technical mechanics (Task 1.3 -- e.g. how `/resolve` decides which artifact type(s) to create from a pair, how it drives the `create_req`/`create_dec`/etc. tools, and the exact leading-comment format), then document the final design and append implementation phases (Task 1.5).

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 21:15:00.000+02:00 - Remaining open points resolved; Tasks 1.2 and 1.4 done

Resolved every remaining open point in the QA transcript: `sysrs` is being built separately and will exist before this feature's implementation phases (treated as a "luxury wrapper" over REQ/DEC/etc. that this feature only references); ASD-STE100 vocabulary is used as-is from the `asdste100` MCP server, with no user- or project-configurable vocabulary support (closing both the `Security` and `Flexibility` open points); the `refine` prompt review outcome stays in this feature's own Decisions Made rather than a full ADR; and the existing `refine` prompt is kept, with two small updates (language selection, updated "next step" text), confirmed to already support targeting specific ISO/IEC 25010:2023 characteristics via its `scope` parameter. Updated REQ-007, the Scope/Dependencies sections, and ACC-007 (now checked) accordingly. Tasks 1.2 and 1.4 are now done; only Task 1.3 (concrete `/refine`/`/resolve` technical mechanics) and Task 1.5 (final write-up + implementation phases) remain in Phase 1.

#### 2026-09-02 20:56:34.418+02:00 - Recon complete; session wrap-up

Completed recon of the external `biz.dfch.IncoseIso25010Refiner` repository (see this feature's Design Notes for the full summary) and closed out Task 1.1/ACC-001 accordingly. This session is wrapping up here; Task 1.2 (review the existing `refine` prompt) and the remaining open points in the QA transcript (`Security`, `Maintainability`, `Flexibility`, and the `sysrs`/design-document-integration question under `Functional Suitability`) are next.

#### 2026-09-02 18:59:00.421+02:00 - Created

Feature created to track designing and implementing MCP commands for AI-supported requirements elicitation (recon, refine, resolve, create, and design-document integration), replacing the external `biz.dfch.IncoseIso25010Refiner` tool, per GitHub issue #63.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 21:15:00.000+02:00 - Keep the existing `refine` prompt, with two small updates

The existing `refine` prompt (`qa/prompts/refine.py`) is kept, not changed structurally or retired -- it already only appends unanswered questions to a `qa` document, already lets the caller target a specific named subset of the 9 ISO/IEC 25010:2023 characteristics (or all of them) via its `scope` parameter, and already defers entirely to `/resolve` as the next step. Two small updates are needed once `/resolve`'s own design (Task 1.3) is final: (1) add target-language selection (EN/DE/FR), per the language-resolution order decided below; (2) update its closing "next step" guidance to describe `/resolve`'s actual behavior (create artifacts directly from answered pairs, plus leading-comment traceability) rather than any stale wording. This is recorded here, in this feature's own Decisions Made, rather than as a full ADR, since it is not a repo-wide architecture decision.

#### 2026-09-02 21:10:00.000+02:00 - `sysrs` is an external dependency this feature only references, not designs; ASD-STE100 vocabulary is used as-is with no user-supplied-vocabulary support

Two related scope-narrowing decisions: (1) The "sysrs" system requirements specification mentioned in REQ-005 is being implemented as its own, separate effort and does not exist in this repo yet, but is expected to land before this feature reaches its implementation phases. Conceptually it is a "luxury wrapper" over REQ/DEC/etc. -- it aggregates and references already-created artifacts rather than duplicating their content -- so this feature's design-document-integration work treats it as an existing artifact type once available, and does not design `sysrs` itself. (2) ASD-STE100 enforcement uses the `asdste100` MCP server's vocabulary exactly as-is; the server itself decides which vocabulary it loads, and neither a user nor an agent can supply or change it. This removes the "user-supplied additional vocabularies" capability originally sketched in the raw GitHub issue text and REQ-007's first draft, and means there is no access-control/configurability question to design (no per-project/per-user/global vocabulary scope needed). REQ-005, REQ-007, the Overview, and the Scope/Dependencies sections have been updated accordingly. See QA document `f58fe807-7485-4513-812d-37d8d1e9cdb1`'s `Functional Suitability`, `Security`, and `Flexibility` sections for the full discussion.

#### 2026-09-02 20:53:03.623+02:00 - Two-step command design: `/refine` then single-document `/resolve`, plus a separate cross-check command

Based on recon of `biz.dfch.IncoseIso25010Refiner` (see this feature's QA transcript), the elicitation command family drops the refiner's intermediate "resolve into a rewritten sentence, still inside the same document" step entirely, since our `qa` documents never lose the original answer text the way the refiner's `source.md` does. The resulting design: `/refine` reads an existing (or new) `qa` document and asks more questions, across all or a specified subset of the 9 ISO 25010:2023 characteristics; `/resolve` operates on exactly one `qa` document and creates the actual REQ/DEC/RSK/GOL (etc.) artifacts directly from its answered pairs -- one `qa` pair may yield more than one artifact, including artifacts of different types (for example both a REQ and a DEC from the same answer). When more than one `qa` document needs to feed into the artifact set, a separate, later cross-check command reconciles the additional `qa` document against artifacts already created from earlier ones, rather than `/resolve` itself trying to span multiple documents. For traceability and to prevent duplicate re-resolution, `/resolve` adds a leading comment directly in front of each `qa` pair it resolves, referencing every artifact created from it; a later `/resolve` run treats an already-commented pair as already resolved.

#### 2026-09-02 19:42:41.110+02:00 - No cross-session persistence for elicitation-command language selection

Multi-language (EN/DE/FR) output selection for the elicitation commands resolves per-conversation only, via a shared language parameter (not a dedicated prompt per language) that an LLM agent interprets flexibly (e.g. "de", "DE", "Deutsch", "German" all resolve the same way): (1) a language explicitly given in the current command; (2) failing that, the last language explicitly specified earlier in the same conversation; (3) failing that, the language the user is currently writing in for that conversation turn. specmgr itself will not persist a separate "last used language" preference across separate conversations/sessions -- resolution relies entirely on the agent's own in-conversation context for (1) and (2). See QA document `f58fe807-7485-4513-812d-37d8d1e9cdb1`'s `Interaction Capability` section for the full discussion.

#### 2026-09-02 18:59:00.421+02:00 - Keep design and implementation in one feature; phase incrementally

Rather than opening a second feature once the design phase concludes, this feature keeps both design and implementation together, matching the existing convention of iteratively extending the Task List with new `#### Phase N: ...` entries as they become known (see `feat-38-39-41-43-44`, which folds four issues into one feature). Phase 1 (Design) is fully specified now; later implementation phases will be appended to this same feature's Task List, via the generic `update` tool, once Phase 1 concludes. A new, separate feature is only warranted if the design phase itself decides some piece of this work should become its own independently-tracked effort.
