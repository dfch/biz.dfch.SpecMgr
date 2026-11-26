---
classification: null
created: '2026-09-02 18:59:00.421+02:00'
id: feat-63-refine
status: planning
type: feat
updated: '2026-11-26 08:45:59.273+01:00'
version: 1.0.0
---

# Feature: Create Commands for Requirement Elicitation

## Plan

### Overview

This feature designs and implements MCP prompts (commands) for AI-supported requirements elicitation. It replaces the external `biz.dfch.IncoseIso25010Refiner` repository, which is retired once these commands are complete. The recon of that repository is in Design Notes.

The flow has three steps:

1. `/refine` reads an existing `qa` document (or starts a new one) and adds unanswered questions for all or a named subset of the 9 ISO/IEC 25010:2023 characteristics. This prompt already exists on `dev` and needs only small updates (see Decisions Made).
1. `/resolve` reads one `qa` document and creates `req`/`dec`/`rsk`/`gol` artifacts directly from its answered pairs. One pair can produce more than one artifact, of different types. Before it creates anything, every run checks each pair against the existing artifacts of all documents (duplicates, conflicts). There is no separate cross-check command. Each created artifact names its originating pair in its own `## Source` section.
1. `/resolve` then adds the created artifacts to a design document: a `sysrs` (cross-reference lists) and, optionally, a `set` that bundles everything one `qa` document produced.

The EN artifacts are the source of truth and use ASD-STE100 controlled English, checked with the `asdste100` MCP server when the host has it. DE/FR (and other) variants are made after that with the existing feat-197 machinery (`translate_artifact`, `check_translation_drift`).

### Requirements

- REQ-001: Recon and document every capability/command the existing `biz.dfch.IncoseIso25010Refiner` repository provides (not only "refine", but also "resolve" and any others), before designing this repo's own commands.
- REQ-002: Provide a prompt/command (`/refine`) that reads an existing `qa` document (or starts a new one) and asks additional questions, across all or a specified subset of the 9 ISO/IEC 25010:2023 characteristics.
- REQ-003: Provide a prompt/command (`/resolve`) that operates on exactly one `qa` document and creates the actual REQ/DEC/RSK/GOL (etc.) artifacts directly from its answered pairs, with no intermediate document-inlined representation.
- REQ-004: A single `qa` pair may produce more than one artifact, and those artifacts may be of different types (for example a REQ and a DEC derived from the same answer).
- REQ-005: `/resolve` adds the artifacts it creates to a design document: it adds their references to an existing `sysrs` document's matching cross-reference lists (generic `update(type="sysrs")`), and can bundle everything created from one `qa` document in a `set` (`create_set`).
- REQ-006: The EN artifacts are the source of truth. Variants in other languages (at minimum DE and FR) are produced from the EN source with feat-197's `translate_artifact` prompt and kept in sync with `check_translation_drift`. `/refine` and `/resolve` always write EN.
- REQ-007: The EN text that `/resolve` writes uses ASD-STE100 controlled English, checked with the `asdste100` MCP server's own vocabulary and rules as-is. There is no user- or agent-supplied vocabulary support.
- REQ-008: Review the existing `refine` prompt already in this repo as part of the design, and decide whether to keep, change, or retire it.
- REQ-009: Every `/resolve` run, including the first one and the run over the first `qa` document, checks each answered pair against all existing artifacts before it creates anything, and flags likely duplicates or conflicts. The user then chooses for each flagged pair: create new, link to the existing artifact only, or stop and resolve the conflict.
- REQ-010: Every artifact `/resolve` creates names its originating `qa` document and question number(s) in its own `## Source` section, using the shared reference vocabulary (`QA <uuid>`). `/resolve` does not write to the `qa` document. A later run finds already-resolved pairs from these references and skips them.

### Acceptance Criteria

- [x] ACC-001: The recon task has produced a written summary of every capability/command the existing `biz.dfch.IncoseIso25010Refiner` repository provides.
- [ ] ACC-002: `/refine` reads an existing `qa` document (or starts a new one), can target all or a specified subset of the 9 ISO/IEC 25010:2023 characteristics, and leaves a document that passes `validate(type="qa", full=True)`.
- [ ] ACC-003: A `/resolve` prompt exists that operates on exactly one `qa` document and creates one or more valid REQ/DEC/RSK/GOL documents directly from its answered pairs, with no intermediate document-inlined representation.
- [ ] ACC-004: A single `qa` pair can be exercised to produce more than one artifact, including artifacts of different types (for example a REQ and a DEC from the same pair).
- [ ] ACC-005: `/resolve` adds the references of the artifacts it created to a `sysrs` document's matching sections, and the `sysrs` document still parses. When asked, it creates a `set` that lists every artifact created from the `qa` document.
- [ ] ACC-006: When the `asdste100` MCP server is available, `/resolve` checks every EN statement it writes with it, and reports each word or rule finding it could not fix. When the server is not available, `/resolve` still runs and says in its report that the ASD-STE100 check was skipped.
- [x] ACC-007: The existing `refine` prompt has been reviewed, and a decision (keep/change/retire) is documented in this feature's Decisions Made.
- [ ] ACC-008: For an answered pair that duplicates or conflicts with an existing artifact (seeded in a test fixture), `/resolve` reports the match and asks the user before creating anything. This is the case on the first run over a `qa` document too. When the `similarity` extra is not available, the prompt falls back to a title/statement comparison over `list_<d>` and says so.
- [ ] ACC-009: Every artifact `/resolve` creates has a `## Source` line that `list_references` resolves to the originating `qa` document. A second `/resolve` run over the same `qa` document creates no new artifact for an already-resolved pair.
- [ ] ACC-010: `translate_artifact` can produce DE and FR variants of a `req`/`dec`/`rsk`/`gol` created by `/resolve`, and `check_translation_drift` reports no structural drift for them. This needs an `fr` heading table (`general/data/headings/fr.json`) that passes the heading-table drift test.
- [ ] ACC-011: The `refine` prompt's closing "next step" text points at the real `/resolve` prompt and describes what it does.

### Scope

#### Included

- Design and implementation of the elicitation prompts: `/resolve` (with the built-in duplicate/conflict check and the design-document step), plus the updates to the existing `refine` prompt.
- OpenCode host surface for the new prompt (skill and command), following the repo's existing patterns.
- The `fr` heading table, so FR variants can be produced with the existing feat-197 tools.
- ASD-STE100 checking of the EN text with the `asdste100` MCP server's own vocabulary as-is.

#### Explicitly Out Of Scope

- Retiring/removing the external `biz.dfch.IncoseIso25010Refiner` repository itself -- that happens only after this feature's replacement commands are complete, per the issue.
- Any artifact-type (REQ/DEC/RSK/GOL/QA) schema changes not directly required by the elicitation workflow -- those are handled by their own domain features.
- Changes to the `sysrs` or `set` document types -- this feature only uses them.
- New translation machinery -- multi-language output uses feat-197's existing tools and prompt only.
- A specmgr dependency on the `asdste100` MCP server, or any way to configure its vocabulary -- it is an optional host server, used as-is.

### Dependencies

#### Depends On

- The external `biz.dfch.IncoseIso25010Refiner` repository (https://github.com/dfensgmbh/biz.dfch.IncoseIso25010Refiner) -- source of the workflow/approach being ported, and the recon target for Phase 100.
- The `qa`, `req`, `dec`, `rsk`, and `gol` domains -- what the commands read and create. Their mandatory `## Source` section carries the traceability (REQ-010).
- `sysrs` (feat-32-sysrs) and `set` (feat-173-req-iso29148-level-set) -- the design-document targets of REQ-005.
- `find_similar_text` / `find_related` (feat-134-related-artifact-similarity) -- the duplicate/conflict check of REQ-009. They are in the optional `similarity` extra, so the prompt needs a fallback.
- `list_references` and the `QA` reference tag (feat-144) -- how re-runs find already-resolved pairs (REQ-010).
- feat-197-i18n -- `translate_artifact`, `check_translation_drift`, the `docs/{type}/{language}/` variants and the heading tables (REQ-006).
- feat-156-qa-numbering -- the `**<d>.<NNNN>**: ` question numbers that `## Source` lines cite, and the `TODO: ` placeholder convention.
- The `asdste100` MCP server -- optional on the host; used for the ASD-STE100 check when present (REQ-007).

### Design Notes

The Q&A transcript behind this plan is QA document `f58fe807-7485-4513-812d-37d8d1e9cdb1` ("feat-63-refine — Requirements Elicitation Q&A Transcript"). The 2026-11-26 review added three new pairs to it (1.0100, 1.0110, 4.0030). They settle the maintainer's open note on 1.0060 and move the plan onto what `dev` now provides. Every question in the transcript has an answer. The open work is the mechanics of Task 100.120, which are tracked in the Task List, not in the transcript.

**Recon of `biz.dfch.IncoseIso25010Refiner` (completed 2026-09-02), so a future agent does not need to re-read that repository.** It is a `typer` CLI built around one artifact per session: a single `source.md` file at `<workspace>/<session-id>/source.md` that accumulates state across the whole cycle -- questions live inline as `>` block-quote lines, and a human types the answer directly below them, by hand.

Its command family: `init` creates a session and seeds `source.md` from `--input` (default characteristics = all 9 ISO 25010:2023 ones). `refine` sends the whole doc to an LLM, which classifies sentences against the 9 characteristics, generates N questions per characteristic with a completeness score, appends the new questions as `>` lines, and auto-translates stray non-English sentences to English (keeping the original in parens). `resolve` finds every question that already has an answer, sends each Q+A pair through a strict rewrite prompt (no passive voice, "must" not "shall", no "-ing", no Saxon genitive, no semicolons, force US English but preserve quoted foreign text), and replaces the Q+A pair in place, inside the same `source.md`, with the resulting single requirement sentence (`-k/--keep` preserves unanswered questions instead of deleting them). `checkpoint`/`restore`/`diff`/`show` are a bespoke version-control-lite for `source.md` (snapshot/revert/delta/print). `summary` restructures the whole resolved doc into a clean Markdown summary, pushing any still-unanswered questions to the end. `translate` is a separate, explicit step (EN summary -> `DE`/`FR`/`IT`/... via a dedicated translation-only LLM call) -- EN is implicitly the working language throughout refine/resolve/summary. `jira` parses the summary's Markdown sections and files one Jira issue per section. `list`/`info`/`erase` are session housekeeping. `replay` re-applies a previously saved raw LLM JSON response without a new LLM call. `query`/`vector`/`stub` are debug/testbed commands, not part of the end-user workflow. `validate` checks a file is valid JSON. `ui` is a TUI/GUI alternative to hand-editing `source.md` directly.

Why this mattered for our own design: their `Iso25010` enum's 9 characteristic strings are byte-identical to our own `qa` v2 schema's category names -- direct precedent, not a coincidence. Their separate, explicit `translate` step over an EN working text is the same model feat-197 now gives us (see Decisions Made: EN first, then translate). Their `resolve` destroys the original Q&A text by design, because `source.md` is the only record they keep -- our `qa` documents never lose that text, which is exactly why we dropped their intermediate "resolve into a rewritten sentence, still inside the same document" step (see Decisions Made: two-step command design). Their `prompt-resolve.md`/`prompt-summary.md` style rules are a hand-rolled, partial reinvention of ASD-STE100 -- this directly validates REQ-007's plan to use the real `asdste100` MCP instead (used as-is, with no equivalent to their hand-rolled rule set). Their `checkpoint`/`restore`/`diff` versioning has no equivalent need in specmgr, since we already rely on git for that. Their closest analog to "create actual REQ/DEC/RSK/GOL documents" is `jira` (summary -> one Jira issue per section) -- they have no first-class document-creation step of their own to adapt from, so REQ-003/004/009/010 are a genuinely fresh design, not a port.

**Existing `refine` prompt review (Task 100.110, completed 2026-09-02; re-checked against `dev` 2026-11-26).** `qa/prompts/refine.py` and its instructions (`qa/data/qa_refine_instructions.md`) already fit the design. The prompt only appends unanswered questions with the `**<d>.<NNNN>**: ` number prefix and a `TODO: answer pending` placeholder (feat-156). It can target a named subset of the 9 ISO/IEC 25010:2023 characteristics (plus `Elicitation Context`) through its free-text `scope` parameter, it takes its questions from the `specmgr://iso25010` resource, and it does not run `/resolve` itself. One defect exists on `dev` now: its closing text (`qa_refine_instructions.md:116-119`, `refine.py:43`) tells the user to run `/resolve`, which does not exist yet. Task 120.100 fixes this.

**ASD-STE100 check (REQ-007, ACC-006).** The `asdste100` MCP server is an optional host server, not a specmgr dependency, so the check lives in the `/resolve` prompt's instructions only. When its tools are present, the agent checks each EN statement it drafts (word lookup against the approved vocabulary, rule matching), rewrites what it can, and lists the remaining findings in its report. When they are absent, the agent says in its report that the check was skipped. No specmgr tool calls the server.

**Duplicate/conflict check (REQ-009, ACC-008).** For each answered pair, `/resolve` drafts the artifact statement(s), then calls `find_similar_text` with that text over the `req`/`dec`/`rsk`/`gol` types. It shows the user each hit above a score threshold (to be set in Task 100.120) and asks: create new, link only, or stop on a conflict. When the `similarity` extra is not available (`available: false`), the prompt compares against `list_<d>` titles instead and says so.

### Task List

#### Phase 100: Design

- [x] Task 100.100: Recon the existing `biz.dfch.IncoseIso25010Refiner` repository and document every capability/command it provides (not only "refine", but also "resolve" and any others).
- [x] Task 100.110: Review the existing `refine` prompt in this repo and assess whether/how it should change in light of the recon findings.
- [ ] Task 100.120: Decide the open `/resolve` mechanics: how it decides which artifact type(s) to create from a pair; the exact `## Source` line format (`QA <uuid>: <title> (<question numbers>)`) and how a re-run finds resolved pairs from it; the `find_similar_text` score threshold and what counts as a conflict; how it picks the target `sysrs` section per artifact type and when it offers a `set`; and the prompt's parameters (`qa` id, optional `sysrs` id, optional target languages to translate into afterwards).
- [x] Task 100.130: Settle the cross-cutting design: the duplicate/conflict check is part of every `/resolve` run (no separate command); traceability lives in the created artifact's `## Source` section, not in the `qa` document; created artifacts go into `sysrs` and optionally a `set`; EN is written first and the other languages come from feat-197's `translate_artifact`; the ASD-STE100 check uses the optional `asdste100` MCP as described in Design Notes. (First settled 2026-09-02; revised 2026-11-26, see Decisions Made.)
- [ ] Task 100.140: Write the Task 100.120 outcome into Design Notes (or a DEC, if it is architecture-level per this repo's DEC-vs-feature-log rule), then refine Phases 110-140 below to match.

#### Phase 110: `/resolve` prompt

- [ ] Task 110.100: Add the `resolve` prompt and its packaged instructions in the `qa` domain (`qa/prompts/`, `qa/data/`), following the `refine` prompt's structure: read the `qa` document with `get_qa`, find the answered pairs, skip pairs already cited in some artifact's `## Source`, draft the artifacts per pair, run the duplicate/conflict check, ask the user, create with `create_req`/`create_dec`/`create_rsk`/`create_gol`, report.
- [ ] Task 110.110: Write the ASD-STE100 step and the "check skipped" degrade path into the instructions (ACC-006).
- [ ] Task 110.120: Write the `similarity`-unavailable fallback into the instructions (ACC-008).
- [ ] Task 110.130: Register the prompt and update `server.py`'s module docstring; regenerate `docs/MCP.md` with `specmgr mcp-docs`.
- [ ] Task 110.140: Tests: the prompt registers and its text names every tool it relies on; a fixture `qa` document plus a seeded duplicate covers ACC-003, ACC-004, ACC-008 and ACC-009 at the instruction level.

#### Phase 120: `refine` updates and design-document step

- [ ] Task 120.100: Update the `refine` prompt's closing "next step" text to describe `/resolve` (ACC-011).
- [ ] Task 120.110: Add the `sysrs` step to `/resolve`: add references to the matching `sysrs` sections with `update(type="sysrs")`, and optionally create a `set` with `create_set` (ACC-005).
- [ ] Task 120.120: Add the optional translate step to `/resolve`'s report: for each requested language, point at `translate_artifact` per created artifact; do not translate inside `/resolve` itself (REQ-006).

#### Phase 130: FR heading table

- [ ] Task 130.100: Add `general/data/headings/fr.json` with the full model-derived heading set, and make the heading-table drift test pass for it.
- [ ] Task 130.110: Check ACC-010 with a DE and an FR variant of one `req`/`dec`/`rsk`/`gol` each.

#### Phase 140: Host surface and close-out

- [ ] Task 140.100: Add the OpenCode skill and `/resolve` command under `.opencode/`, plus their test under `tests/opencode/`; regenerate the harness bundle with `specmgr harness-bundle`.
- [ ] Task 140.110: Run `/refine` and `/resolve` end to end over this feature's own QA transcript (or a smaller fixture) and record the result in Updates.
- [ ] Task 140.120: Update `AGENTS.md`'s `qa/` bullet and `CHANGELOG.md`; regenerate docs with `specmgr docs`.

## Progress

### Current Status

**As of 2026-11-26**: Phase 100 (Design). Tasks 100.100, 100.110 and 100.130 are done. The 2026-11-26 review revised Task 100.130 to match the maintainer's note on QA 1.0060 and what `dev` now provides: the duplicate/conflict check is part of every `/resolve` run, traceability is in the created artifact's `## Source`, and other languages come from feat-197. Phases 110-140 are drafted. Next: Task 100.120 (the `/resolve` mechanics), then Task 100.140. No code exists yet.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-26 08:45:59.273+01:00 - Plan refreshed against current `dev`

Reviewed PR #268 against current `dev` and refreshed the plan. The cross-check is now part of every `/resolve` run, which settles the maintainer's open note on QA 1.0060; REQ-009, ACC-008 and Task 100.130 were rewritten to match. Traceability moved from a leading comment in the `qa` document to the created artifact's `## Source` section (REQ-010, ACC-009), because a QA pair has only one comment slot and this transcript already uses it. Multi-language output now uses feat-197 (REQ-006, new ACC-010, FR heading table in Phase 130), replacing the per-conversation language decision. Also: `sysrs` and `set` exist now (REQ-005, ACC-005), ACC-006 is now testable, and `validate_qa`/ADR references were updated to `validate(type="qa")`/DEC. Added the missing dependencies and drafted implementation Phases 110-140. Recorded the dangling `/resolve` pointer in the shipped `refine` prompt (Task 120.100, ACC-011). Added pairs 1.0100, 1.0110 and 4.0030 to the QA transcript.

#### 2026-09-02 21:15:00.000+02:00 - Remaining open points resolved; Tasks 100.110 and 100.130 done

Resolved every remaining open point in the QA transcript: `sysrs` is being built separately and will exist before this feature's implementation phases (treated as a "luxury wrapper" over REQ/DEC/etc. that this feature only references); ASD-STE100 vocabulary is used as-is from the `asdste100` MCP server, with no user- or project-configurable vocabulary support (closing both the `Security` and `Flexibility` open points); the `refine` prompt review outcome stays in this feature's own Decisions Made rather than a full ADR; and the existing `refine` prompt is kept, with two small updates (language selection, updated "next step" text), confirmed to already support targeting specific ISO/IEC 25010:2023 characteristics via its `scope` parameter. Updated REQ-007, the Scope/Dependencies sections, and ACC-007 (now checked) accordingly. Tasks 100.110 and 100.130 are now done; only Task 100.120 (concrete `/refine`/`/resolve` technical mechanics) and Task 100.140 (final write-up + implementation phases) remain in Phase 100.

#### 2026-09-02 20:56:34.418+02:00 - Recon complete; session wrap-up

Completed recon of the external `biz.dfch.IncoseIso25010Refiner` repository (see this feature's Design Notes for the full summary) and closed out Task 100.100/ACC-001 accordingly. This session is wrapping up here; Task 100.110 (review the existing `refine` prompt) and the remaining open points in the QA transcript (`Security`, `Maintainability`, `Flexibility`, and the `sysrs`/design-document-integration question under `Functional Suitability`) are next.

#### 2026-09-02 18:59:00.421+02:00 - Created

Feature created to track designing and implementing MCP commands for AI-supported requirements elicitation (recon, refine, resolve, create, and design-document integration), replacing the external `biz.dfch.IncoseIso25010Refiner` tool, per GitHub issue #63.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-26 08:45:59.273+01:00 - EN first, then translate with feat-197

`/refine` and `/resolve` always write EN, the source of truth, with the ASD-STE100 check. Other languages come afterwards from feat-197's `translate_artifact` prompt, as separate variant files with the same id, and `check_translation_drift` keeps them in sync. A language given to a command only sets the language the agent talks to the user in and which variants it offers to create afterwards. This supersedes the 2026-09-02 per-conversation language decision below, which was made before feat-197 existed. FR needs a new heading table (Phase 130). See QA 4.0030.

#### 2026-11-26 08:45:59.273+01:00 - Traceability in the created artifact's `## Source`, not in the `qa` document

Each artifact `/resolve` creates names its `qa` document and question number(s) in its mandatory `## Source` section (`QA <uuid>` reference). `/resolve` does not write to the `qa` document. Reasons: a QA pair has exactly one optional leading comment, and this transcript already uses it for "Resolved" notes; a `QA <uuid>` reference is resolved by `list_references` and drawn by the reference-graph tools with no extra work. This supersedes the leading-comment convention in the 2026-09-02 two-step decision below. See QA 1.0110.

#### 2026-11-26 08:45:59.273+01:00 - The duplicate/conflict check is part of every `/resolve` run

There is no separate cross-check command. Every `/resolve` run, including the first one over the first `qa` document, checks each answered pair against all existing artifacts with `find_similar_text` before creating anything, and asks the user what to do with each match. This follows the maintainer's note on QA 1.0060 ("Even the first `/resolve` must examine existing artifacts") and supersedes the separate cross-check command in the 2026-09-02 two-step decision below. See QA 1.0100.

#### 2026-09-02 21:15:00.000+02:00 - Keep the existing `refine` prompt, with two small updates

The existing `refine` prompt (`qa/prompts/refine.py`) is kept, not changed structurally or retired -- it already only appends unanswered questions to a `qa` document, already lets the caller target a specific named subset of the 9 ISO/IEC 25010:2023 characteristics (or all of them) via its `scope` parameter, and already defers entirely to `/resolve` as the next step. Two small updates are needed once `/resolve`'s own design (Task 100.120) is final: (1) add target-language selection (EN/DE/FR), per the language-resolution order decided below; (2) update its closing "next step" guidance to describe `/resolve`'s actual behavior (create artifacts directly from answered pairs, plus leading-comment traceability) rather than any stale wording. This is recorded here, in this feature's own Decisions Made, rather than as a full ADR, since it is not a repo-wide architecture decision.

(2026-11-26: update (1) is superseded by "EN first, then translate with feat-197" -- `refine` keeps writing EN. Update (2) stands, but now describes `## Source` traceability instead of a leading comment; see Task 120.100. The ADR domain was later removed, and the rule is now DEC vs. the feature's Decisions Made.)

#### 2026-09-02 21:10:00.000+02:00 - `sysrs` is an external dependency this feature only references, not designs; ASD-STE100 vocabulary is used as-is with no user-supplied-vocabulary support

Two related scope-narrowing decisions: (1) The "sysrs" system requirements specification mentioned in REQ-005 is being implemented as its own, separate effort and does not exist in this repo yet, but is expected to land before this feature reaches its implementation phases. Conceptually it is a "luxury wrapper" over REQ/DEC/etc. -- it aggregates and references already-created artifacts rather than duplicating their content -- so this feature's design-document-integration work treats it as an existing artifact type once available, and does not design `sysrs` itself. (2) ASD-STE100 enforcement uses the `asdste100` MCP server's vocabulary exactly as-is; the server itself decides which vocabulary it loads, and neither a user nor an agent can supply or change it. This removes the "user-supplied additional vocabularies" capability originally sketched in the raw GitHub issue text and REQ-007's first draft, and means there is no access-control/configurability question to design (no per-project/per-user/global vocabulary scope needed). REQ-005, REQ-007, the Overview, and the Scope/Dependencies sections have been updated accordingly. See QA document `f58fe807-7485-4513-812d-37d8d1e9cdb1`'s `Functional Suitability`, `Security`, and `Flexibility` sections for the full discussion.

(2026-11-26: `sysrs` has since shipped (feat-32-sysrs), and so has `set`; REQ-005 now uses both.)

#### 2026-09-02 20:53:03.623+02:00 - Two-step command design: `/refine` then single-document `/resolve`, plus a separate cross-check command

Based on recon of `biz.dfch.IncoseIso25010Refiner` (see this feature's QA transcript), the elicitation command family drops the refiner's intermediate "resolve into a rewritten sentence, still inside the same document" step entirely, since our `qa` documents never lose the original answer text the way the refiner's `source.md` does. The resulting design: `/refine` reads an existing (or new) `qa` document and asks more questions, across all or a specified subset of the 9 ISO 25010:2023 characteristics; `/resolve` operates on exactly one `qa` document and creates the actual REQ/DEC/RSK/GOL (etc.) artifacts directly from its answered pairs -- one `qa` pair may yield more than one artifact, including artifacts of different types (for example both a REQ and a DEC from the same answer). When more than one `qa` document needs to feed into the artifact set, a separate, later cross-check command reconciles the additional `qa` document against artifacts already created from earlier ones, rather than `/resolve` itself trying to span multiple documents. For traceability and to prevent duplicate re-resolution, `/resolve` adds a leading comment directly in front of each `qa` pair it resolves, referencing every artifact created from it; a later `/resolve` run treats an already-commented pair as already resolved.

(2026-11-26: the two-step `/refine` + `/resolve` design stands. The separate cross-check command and the leading-comment traceability are superseded by the two 2026-11-26 decisions above.)

#### 2026-09-02 19:42:41.110+02:00 - No cross-session persistence for elicitation-command language selection

Multi-language (EN/DE/FR) output selection for the elicitation commands resolves per-conversation only, via a shared language parameter (not a dedicated prompt per language) that an LLM agent interprets flexibly (e.g. "de", "DE", "Deutsch", "German" all resolve the same way): (1) a language explicitly given in the current command; (2) failing that, the last language explicitly specified earlier in the same conversation; (3) failing that, the language the user is currently writing in for that conversation turn. specmgr itself will not persist a separate "last used language" preference across separate conversations/sessions -- resolution relies entirely on the agent's own in-conversation context for (1) and (2). See QA document `f58fe807-7485-4513-812d-37d8d1e9cdb1`'s `Interaction Capability` section for the full discussion.

(2026-11-26: superseded by "EN first, then translate with feat-197". The resolution order and the no-persistence rule still apply, but only to the language the agent talks to the user in.)

#### 2026-09-02 18:59:00.421+02:00 - Keep design and implementation in one feature; phase incrementally

Rather than opening a second feature once the design phase concludes, this feature keeps both design and implementation together, matching the existing convention of iteratively extending the Task List with new `#### Phase NNN: ...` entries as they become known (see `feat-38-39-41-43-44`, which folds four issues into one feature). Phase 100 (Design) is fully specified now; later implementation phases will be appended to this same feature's Task List, via the generic `update` tool, once Phase 100 concludes. A new, separate feature is only warranted if the design phase itself decides some piece of this work should become its own independently-tracked effort.

### Related PRs / Commits

- PR #268 -- this plan and its QA transcript (planning only, no implementation).
