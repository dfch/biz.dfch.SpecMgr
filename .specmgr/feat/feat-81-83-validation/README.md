---
classification: null
created: '2026-09-03 12:38:25.338+02:00'
id: feat-81-83-validation
status: planning
type: feat
updated: '2026-09-03 17:00:00.000+00:00'
version: 1.0.0
---

# Feature: Consolidate Validation Tools and Fix Opaque Validation/List Failures (#81, #83)

## Plan

### Overview

GitHub issues #81 and #83 both concern how this repo's MCP tools report validation failures. Issue #81 asks for an inventory of the per-domain `validate_<d>` tools and a decision on how to consolidate them, plus whether `list_<d>` should return a document path (already true for `feat` via `FeatSummary.path`), so an agent can read/edit/validate a document with minimum token cost. There are actually thirteen `validate_<d>` tools today (not eleven, as an earlier draft of this plan assumed): twelve whole-body-domain tools sharing an identical `(content: str, full: bool = False) -> bool` signature, plus `validate_adr` (`id`-based, re-reads from disk, no `full` parameter) which differs structurally from the other twelve. Issue #83 reports two related problems: (a) a validation failure surfaces only as an opaque, uncaught exception rather than a structured, inspectable result, and (b) `list_<d>` silently reports `total: 0` when every document in a directory fails to parse, indistinguishable from an empty or misconfigured directory. Prior work already closed part of the "opaque" complaint: `feat-27-validation` made every validation exception's message actionable (field path, line, cause/fix hint), and `feat-67-70-71` confirmed the MCP transport forwards that full message to the client unabridged, with no truncation. What remains open is the delivery mechanism itself -- a dry-run check tool (`validate_<d>`) still only ever succeeds or raises, so a caller cannot get back a structured, inspectable `{valid, errors}` result -- plus `list_<d>`'s silent-zero problem, which no prior feature touched. This feature investigates whether issue #83's own two literal repro cases still reproduce against current HEAD (following the same investigate-first method `feat-67-70-71` used for issues #70/#71), then: (1) replaces twelve of the thirteen per-domain `validate_<d>` tools (all except `validate_adr`, which is kept unchanged) with one generic, type-dispatched `validate` tool (mirroring the existing `update`/`set_status`/`set_classification`/`delete` precedent, ADR 36905d5b-8057-4294-8665-c7eed5534db0) that always returns a structured `{valid, errors}` result instead of raising for a content-validation failure; (2) fixes `list_<d>` to report parse failures explicitly, via an `error_count` header field and inline failed-document entries in `results`; and (3) adds `list_<d>` summary `path`-field parity with `FeatSummary.path` across the other eleven whole-body domains, retrofitting `FeatSummary.path` itself to use a resolved (absolute) path in the same pass.

### Requirements

- REQ-001: Before any implementation, reproduce issue #83's two literal repro bodies (a `req` document with naive-isoformat `created`/`updated` timestamps; a `dec` document with an em dash instead of a hyphen in an `## Updates` sub-heading) against current HEAD through `validate_req`/`validate_dec`, and record in Design Notes whether the reported opaque-failure symptom still reproduces or was already resolved by `feat-27-validation`/`feat-67-70-71`.

- REQ-002: Produce an inventory (in Design Notes) of every current `validate_<d>` tool's signature, domain list, and behavior -- all thirteen, including `validate_adr` -- as issue #81 explicitly requests, before designing its replacement.

- REQ-003: Replace twelve of the thirteen per-domain `validate_<d>` tools (all except `validate_adr`, which keeps its distinct `id`-based, disk-touching signature and is excluded from consolidation) with one generic, type-dispatched `validate(type, content, full)` tool in `general/tools/`, mirroring the `update`/`set_status`/`set_classification`/`delete` precedent (ADR 36905d5b-8057-4294-8665-c7eed5534db0); the twelve consolidated per-domain tools are removed, not kept as wrappers, matching that precedent.

- REQ-004: The generic `validate` tool never raises for a content-validation failure; it always returns a structured result (`{valid: bool, errors: list[{message: str}]}` -- no `field` key), reusing `feat-27-validation`'s already-enriched, actionable message text verbatim as each error's `message` -- only a shape-mismatch on `full`/`type` (an already-actionable `ValueError` today) may still raise.

- REQ-005: `parse_<d>`/`get_<d>` keep their existing raise-based contract unchanged -- this feature's structured-result change is scoped to `validate` only.

- REQ-006: `list_<d>` (all twelve whole-body domains) reports parse failures explicitly: an `error_count` field alongside `total`/`truncated`, with each failed document appearing inline within `results` -- `title` replaced by the fixed marker `"<failed to parse>"`, `ref` populated as `path.stem` (identical to every domain's existing successful-entry `ref` derivation, since a content-parse failure never prevents deriving the filename stem), and a new `error` field carrying the actual exception message -- rather than being silently omitted. Directory-listing/permission errors that could prevent even filename enumeration are out of scope.

- REQ-007: Add a `path: str` field (an absolute, `.resolve()`d filesystem path) to `list_<d>` summaries for the other eleven whole-body domains, matching and extending `FeatSummary.path`'s existing precedent; in the same pass, retrofit `FeatSummary.path` itself to use a resolved (absolute) path rather than its current unresolved `str(path)`, and revise `DocSummary.ref`'s docstring to drop its "must not read this off disk" policy language now that `path` makes direct reads a sanctioned, first-class option for every whole-body domain.

- REQ-008: Regression tests reproduce issue #83's two literal repro bodies end-to-end through the new generic `validate` tool, and a directory with a mix of valid and unparseable documents end-to-end through `list_<d>` for at least two domains.

### Acceptance Criteria

- [x] ACC-001: Verifies REQ-001 -- Design Notes records a confirmed-real-or-already-fixed verdict for both of issue #83's literal repro bodies, reproduced against current HEAD. Verdict: both reproduce as client-observed symptoms, root-caused to a client-side tool-error-rendering gap outside this repo's code, not a server-side regression -- see Design Notes.

- [ ] ACC-002: Verifies REQ-002 -- Design Notes contains a table/list of all thirteen current `validate_<d>` tools with signature and behavior.

- [ ] ACC-003: Verifies REQ-003/REQ-004 -- the generic `validate(type, content, full)` tool exists, dispatches to all twelve applicable domains, returns `{valid, errors}` without raising for a content-validation failure, and the twelve consolidated per-domain `validate_<d>` tools (all except `validate_adr`, which still exists unchanged) no longer exist.

- [ ] ACC-004: Verifies REQ-005 -- existing `parse_<d>`/`get_<d>` tests continue to pass unchanged (raise-based contract untouched).

- [ ] ACC-005: Verifies REQ-006 -- a `list_<d>` test with a directory containing both valid and unparseable documents asserts `error_count` is correct and each failed document appears in `results` with `ref`/marker/`error` populated.

- [ ] ACC-006: Verifies REQ-007 -- all eleven other whole-body domains' summary types gain an absolute, resolved `path: str` field with a passing test each; `FeatSummary.path` is retrofitted to resolved/absolute form with its existing tests updated accordingly; `DocSummary.ref`'s docstring no longer states callers must not read the file off disk directly.

- [ ] ACC-007: Verifies REQ-008 -- the regression tests described exist and pass.

### Scope

#### Included

- Investigation/reproduction of issue #83's two literal repro cases against current HEAD.

- Inventory of all thirteen current `validate_<d>` tools (issue #81's explicit ask).

- A new generic, type-dispatched `validate` tool in `general/tools/` returning a structured, non-raising `{valid, errors}` result.

- Removal of twelve per-domain `validate_<d>` tools (all except `validate_adr`) once the generic tool is live and tested.

- `list_<d>` fix: `error_count` header field plus inline failed-document entries in `results`, across all twelve whole-body domains.

- `list_<d>` summary `path`-field parity with `FeatSummary.path` across the other eleven whole-body domains, plus retrofitting `FeatSummary.path` to a resolved (absolute) path and revising `DocSummary.ref`'s docstring accordingly.

- Regression tests, docstring `Raises`/return-shape updates, `docs/api`/`docs/GENERATED.md`/`docs/MCP.md` regeneration, and an `AGENTS.md` update.

#### Explicitly Out Of Scope

- Consolidating `parse_<d>`/`get_<d>` into a generic dispatch tool -- per the recorded decision, only `validate` is consolidated; reads stay per-domain.

- Changing `parse_<d>`/`get_<d>`'s raise-based error contract -- already actionable per `feat-27-validation`, untouched here.

- Changing `validate_adr`'s `id`-based, disk-touching contract -- it is structurally different from the other twelve `validate_<d>` tools (no `full` parameter, always re-reads from disk) and stays a standalone tool, excluded from the generic `validate` tool.

- Handling directory-listing/permission errors in `list_<d>`'s failure reporting -- REQ-006/Task 3.1 only cover per-document content/parse failures, not enumeration failures.

- Filing or fixing the drafted OpenCode client-side bug report (`opencode-issue-mcp-tool-error-truncated.md`) -- it is outside this repo's control; the draft is saved as a courtesy artifact only.

- New exception types or a typed structural-error channel -- the generic `validate` tool's `{valid, errors}` result is built from the existing enriched exception messages, not a new channel.

- Re-litigating message content quality for `create_<d>`/`update`/`set_status` -- already addressed by `feat-27-validation`/`feat-67-70-71`; this feature only changes `validate`'s and `list_<d>`'s result shape.

- Wiring `validate`/`list_<d>` into CI/pre-commit over the repo's own `.specmgr`/`docs` documents -- tracked separately (ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73).

### Dependencies

#### Depends On

- `feat-27-validation` (done) -- supplies the actionable exception messages this feature's `validate` result reuses verbatim.

- `feat-67-70-71` (done) -- confirmed the MCP transport does not truncate/discard those messages, ruling out a transport-layer explanation for issue #83's reported symptom.

### Design Notes

**Phase 1 investigation finding (2026-09-03): the opaque-failure symptom reproduces, but its root cause is a client-side rendering gap, not a specmgr server-side regression.**

Both of issue #83's literal repro bodies were reproduced against current HEAD:

- The `req` naive-isoformat-timestamp repro (`created`/`updated` as `'2026-08-05T08:15:42'` instead of the required `'yyyy-MM-dd HH:mm:ss.fff' + Z/offset` variant), submitted to `validate_req(content, full=True)`.
- The `dec` em-dash-heading repro (an `## Updates` sub-heading using `### 2026-08-27 — Created` -- an em dash `—` -- instead of a hyphen `-`), submitted to `validate_dec(content, full=True)`.

In this agent session, calling either tool (or `validate_feat`, tested the same way while refining this very document) through the normal MCP tool-call interface surfaced only a bare, contentless `"Error executing tool <name>"` message -- exactly the opaque-failure symptom issue #83 describes, and exactly what this feature's REQ-003/004 remedy targets.

However, calling the *same* `validate_req` tool with the *same* input directly over raw MCP JSON-RPC (a standalone Python script using the `mcp` SDK's `stdio_client`/`ClientSession` to spawn `python -m biz.dfch.specmgr mcp` and inspect the wire-level `CallToolResult`, bypassing this session's own tool-calling harness entirely) shows the **full, actionable, `feat-27-validation`-enriched message present in `content[].text`**, e.g.:

```
Error executing tool validate_req: 2 validation errors for ReqFrontmatter
created
  req validate_req: req frontmatter block, field 'created' (document line 2): Value error, created/updated '2026-08-05T08:15:42' must be the date+time variant 'yyyy-MM-dd HH:mm:ss.fff' followed by 'Z' or a signed '+HH:mm'/'-HH:mm' offset [...]
updated
  req validate_req: req frontmatter block, field 'updated' (document line 6): Value error, created/updated '2026-08-06T03:27:27' must be the date+time variant 'yyyy-MM-dd HH:mm:ss.fff' followed by 'Z' or a signed '+HH:mm'/'-HH:mm' offset [...]
```

**Verdict**: `feat-67-70-71`'s conclusion -- "the MCP transport forwards that full message to the client unabridged, with no truncation" -- is confirmed correct at the wire level; this is not a regression. The `"Error executing tool <name>: "` prefix is the MCP/FastMCP framework's own standard formatting for a tool-raised exception, and the full enriched message follows it intact in the actual server response. The opacity this feature's own investigation (and issue #83's original report) observed happens one layer further out: in the *calling agent's own tool-invocation rendering*, which -- in this session, and evidently in whatever client issue #83's reporter used -- appears to discard `content[].text` beyond a short generic fragment whenever a `CallToolResult` has `is_error=true`. This is outside specmgr's own code and cannot be fixed by any change to this repository's server-side error-enrichment machinery.

This finding does not change any of this feature's REQ-003/004 design -- it reinforces why it is the right fix. A tool result's `is_error=true` path is, empirically, at the mercy of a client's own (possibly lossy) error-rendering behavior, uncontrollable from the server side. A tool result's ordinary *successful* return value, by contrast, has been observed in this same session to pass through completely and losslessly regardless of size or content (e.g. this session's own `list_feat` calls, and the large text bodies read via `get_<d>`/`parse_<d>` tools). Converting `validate` from raise-on-failure to always-returns-`{valid, errors}` therefore sidesteps the lossy client-side path entirely, independent of which MCP client is in use -- a strictly more robust fix than relying on every possible client to render `is_error=true` content faithfully.

A drafted (not filed) upstream bug report against the OpenCode client used in this investigation (version 1.18.27) is saved alongside this plan at `.specmgr/feat/feat-81-83-validation/opencode-issue-mcp-tool-error-truncated.md`, documenting the repro, the wire-level evidence above, and pointers into OpenCode's own `dev`-branch source (`packages/opencode/src/mcp/catalog.ts`, `packages/opencode/src/tool/code-mode.ts`) that -- as read -- should already preserve the full message, making the exact root cause still unpinned-down on OpenCode's side. This is tracked as a courtesy artifact only; filing it is explicitly out of scope for this feature (see Scope) and does not gate any of this feature's own tasks.

This reasoning -- that `validate`'s redesign is a workaround for an external defect, not an independently preferred design, and that the rationale generalizes beyond this one feature -- is formally recorded as ADR 519d1206-4d2a-4500-9046-6db635209996 rather than left only here, per this repo's own convention that a decision affecting more than one feature belongs in a full ADR (see `AGENTS.md`).

**Tool-count correction**: an earlier draft of this plan said "eleven" `validate_<d>` tools; that figure was stale (it predates `sysrs` and one other domain being added). There are thirteen `validate_<d>` tools total: twelve whole-body-domain tools sharing an identical `(content: str, full: bool = False) -> bool` signature, plus `validate_adr` (`id`-based, re-reads from disk, no `full` parameter). This correction is reflected throughout the rest of the plan.

Design questions resolved during plan refinement (2026-09-03), prior to Phase 1 kickoff, superseding the "open question"/"tentative" framing that predated a research pass over the existing generic-tool precedents:

- **Generic `validate`'s domain list**: excludes `adr`, matching `update`/`set_classification`/`delete`'s 12-way precedent (each of those three excludes `adr` for its own documented, domain-specific reason) rather than `set_status`'s 13-way exception. `validate_adr` is structurally the odd one out among the thirteen `validate_<d>` tools -- `id`-based and disk-touching, with no `full` parameter -- whereas all twelve whole-body domains share an identical `(content, full)` signature. `validate_adr` is therefore kept as its own standalone tool, unchanged, and excluded from consolidation.

- **`{valid, errors}` shape**: `errors` is `list[{message: str}]` -- no `field` key. No existing precedent for a non-raising structured result exists anywhere in the codebase (this is greenfield). `feat-27-validation`'s enrichment pipeline fuses field path, line number, and cause/fix hint into a single opaque message string before the error ever reaches a tool boundary; pydantic's structured `loc`/`msg` data (via `.errors()`) is used internally only to rebuild another exception, never exposed to a caller. A separate `field` key would require new, fragile extraction, and would be `None`/absent for `AssertionError`/YAML-sourced errors regardless, since no structured field data exists for those channels at all. Reusing the already-enriched message string verbatim as each error's sole content avoids both problems. `full=True`/`full=False` is preserved as a parameter on the generic tool, unchanged from today's per-domain tools.

- **Failed `list_<d>` entry marker / `ref` semantics**: `title` is replaced with the fixed marker `"<failed to parse>"`; `ref` is `path.stem` (the filename stem), identical to every domain's existing successful-entry `ref` derivation -- confirmed universal across every `list_<d>`/`list_adr` implementation: `ref` is always filename-derived, never frontmatter-`id`-first. A content-parse failure never prevents deriving `ref`, since reading a filename doesn't require successfully parsing the file's content. Directory-listing/permission errors that could prevent even filename enumeration are explicitly out of scope for this feature.

- **`list_<d>` `path`-field parity (REQ-007)**: `path` is added to all eleven other whole-body domains' summary types, as an absolute, `.resolve()`d path -- not left as an undecided "decide, and where warranted implement" question. `FeatSummary.path` is retrofitted in the same pass to also use a resolved path (a deliberate behavior change from its current unresolved `str(path)`), and `DocSummary.ref`'s docstring is revised to drop its "callers must not read this off disk themselves" policy language, since `path` now makes direct reads a sanctioned, first-class option for every whole-body domain rather than a `feat`-only divergence. This decision was made knowingly against the stricter, more conservative alternative (leaving `ref`'s policy intact and declining to add `path` to the other eleven domains, on the grounds that their architecture -- locking, id-based dispatch, validation-on-write -- assumes tool-only mutation, unlike `feat`'s sanctioned direct-editing convention); implementers should keep the tool-only mutation contract intact elsewhere (`path` is for reads/context, not a new direct-write path) even though direct reads are now explicitly sanctioned.

### Related Decisions

- ADR 36905d5b-8057-4294-8665-c7eed5534db0: established the one-generic-dispatch-tool-per-mutation convention (`update`/`set_status`/`delete`) this feature extends to `validate`.

- ADR 519d1206-4d2a-4500-9046-6db635209996: records that `validate`'s non-raising, structured `{valid, errors}` design (REQ-003/004) is fundamentally a workaround for a confirmed, external OpenCode 1.18.27 client-side defect (truncating `isError: true` MCP tool results down to a bare `"Error executing tool <name>"`), not an independently preferred design -- written up separately from this feature's own Design Notes because the rationale generalizes to any future tool in this repo facing the same need.

### Task List

#### Phase 1: Investigation and Inventory

- [x] Task 1.1: Reproduce issue #83's `req` naive-isoformat-timestamp repro against current HEAD via `validate_req`. Done -- see Design Notes.

- [x] Task 1.2: Reproduce issue #83's `dec` em-dash-heading repro against current HEAD via `validate_dec`. Done -- see Design Notes.

- [x] Task 1.3: Record a confirmed-real-or-already-fixed verdict for both, in Design Notes. Done -- verdict recorded, with a root-cause diagnosis that narrows this feature's fix rationale (see Design Notes).

- [ ] Task 1.4: Inventory all thirteen current `validate_<d>` tools (signature, domain, behavior) in Design Notes, per issue #81.

- [x] Task 1.5: Resolve the open design questions in Design Notes (generic `validate`'s domain list; `{valid, errors}` shape; failed-entry marker/`ref` semantics; `list_<d>` `path`-field parity) -- resolved 2026-09-03 during plan refinement, ahead of Phase 1 kickoff; see Design Notes and the Decisions Made log below.

#### Phase 2: Generic `validate` Tool

- [ ] Task 2.1: Implement the generic `validate(type, content, full)` tool in `general/tools/`, dispatching to each of the twelve applicable domains' existing validation logic (`adr` excluded), returning `{valid: bool, errors: list[{message: str}]}` without raising for a content-validation failure.

- [ ] Task 2.2: Migrate every caller/reference (prompts, docs, `AGENTS.md`) from the twelve consolidated per-domain `validate_<d>` tools to the generic tool; `validate_adr` references are left untouched.

- [ ] Task 2.3: Remove the twelve consolidated per-domain `validate_<d>` tool files (all except `validate_adr`, which remains).

- [ ] Task 2.4: Unit tests for the generic tool across all twelve applicable domains, plus the two regression fixtures from Phase 1.

#### Phase 3: `list_<d>` Failure Reporting

- [ ] Task 3.1: Add `error_count` and inline failed-document entries (`ref`/marker `title`/`error`) to `list_<d>`'s shared listing helper, across all twelve whole-body domains.

- [ ] Task 3.2: Regression tests with a mixed valid/unparseable directory for at least two domains.

#### Phase 4: `list_<d>` Path Field Parity

- [ ] Task 4.1: Add an absolute, `.resolve()`d `path: str` field to the other eleven whole-body domains' summary types and their `list_<d>` implementations (the loop's `path: Path` variable is already in scope at summary-construction time in every domain -- confirmed via `list_req.py`; mirrors `FeatSummary`'s existing one-line pattern).

- [ ] Task 4.2: Retrofit `FeatSummary.path`/`list_feat.py` to also use `path.resolve()` instead of the current unresolved `str(path)`; update any existing `feat` tests that assert on the old unresolved-path format.

- [ ] Task 4.3: Revise `DocSummary.ref`'s docstring to drop the "callers must not read this off disk themselves" policy language, since `path` now makes direct reads a sanctioned, first-class option for every whole-body domain.

- [ ] Task 4.4: Tests for the new `path` field (all eleven domains) and for `FeatSummary`'s changed, now-resolved `path` behavior.

#### Phase 5: Verification and Closeout

- [ ] Task 5.1: Full quality gate (`ruff format --check`, `ruff check`, `vulture`, full `unittest` suite).

- [ ] Task 5.2: Regenerate `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md`; update `AGENTS.md`.

- [ ] Task 5.3: Comment on GitHub issues #81 and #83 with the outcome; mark this feature done.

## Progress

### Current Status

**As of 2026-09-03**: Feature drafted from GitHub issues #81 and #83, then refined -- Task 1.5's design questions were resolved ahead of Phase 1, and Tasks 1.1-1.3 (reproducing issue #83's two literal repro cases) are now also done: both reproduce as client-observed symptoms, but root-caused to a client-side tool-error-rendering gap, not a specmgr server-side regression -- see Design Notes. No implementation started yet. Only Task 1.4 (the full tool inventory) remains before Phase 1 is complete.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-03 17:00:00.000Z - Recorded the client-side-defect workaround rationale as an ADR

Wrote ADR 519d1206-4d2a-4500-9046-6db635209996 ("Design `validate` as a non-raising, structured-result tool to work around client-side MCP error-content truncation"), formalizing the reasoning already captured in Design Notes: `validate`'s REQ-003/004 non-raising design exists because of a confirmed, external OpenCode 1.18.27 client-side defect, not as an independently preferred design -- a decision worth a full ADR since the rationale generalizes to any future tool in this repo facing the same need, not just this feature. Cross-referenced the ADR from Design Notes/Related Decisions and from the drafted, unfiled `opencode-issue-mcp-tool-error-truncated.md`.

#### 2026-09-03 16:00:00.000Z - Phase 1 Tasks 1.1-1.3 done: repro confirmed, root cause narrowed to a client-side rendering gap

Reproduced both of issue #83's literal repro bodies against current HEAD (`req` naive-isoformat timestamps via `validate_req`; `dec` em-dash `## Updates` sub-heading via `validate_dec`). In this agent session, both surfaced only as a bare, contentless `"Error executing tool <name>"` message through the normal MCP tool-call interface -- the opaque-failure symptom issue #83 describes. A follow-up raw MCP JSON-RPC inspection (bypassing this session's own tool-calling harness, via the `mcp` SDK's `stdio_client`) proved the specmgr server itself sends the full, `feat-27-validation`-enriched message in the wire-level `CallToolResult`; the truncation happens one layer further out, in the calling agent's own tool-result rendering. `feat-67-70-71`'s "transport forwards unabridged" conclusion is confirmed correct, not regressed. Full detail and rationale for how this reinforces (rather than changes) REQ-003/004's non-raising `validate` design are in Design Notes.

#### 2026-09-03 15:00:00.000Z - Plan refined: design questions resolved ahead of Phase 1

Refined the plan before starting implementation. Corrected a stale "eleven" `validate_<d>` tool count to the actual thirteen (twelve identical-signature whole-body tools plus the structurally-different `validate_adr`). Resolved all of Task 1.5's open design questions plus REQ-007's previously-conditional `path`-field decision -- see Design Notes and "Design questions resolved during plan refinement" below for the resolutions and rationale. Requirements, Acceptance Criteria, Scope, and the Task List were updated to reflect these resolutions.

#### 2026-09-03 14:27:36.412Z - Created

Created from GitHub issues #81 (consolidate validation tools) and #83 (opaque validation errors; `list_<domain>` silently reporting zero on parse failures). Combines both issues into one feature since #83 is referenced by #81 and both concern how validation failures/results are reported by this repo's MCP tools.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-03 17:00:00.000Z - Wrote a full ADR for the client-side-defect workaround rationale

Decided this feature's own Design Notes were not a sufficient home for the reasoning behind `validate`'s non-raising design, since that reasoning -- it exists to work around a confirmed external OpenCode defect, not as an independently preferred design -- generalizes beyond this one feature to any future tool in this repo that signals failure by raising. Wrote ADR 519d1206-4d2a-4500-9046-6db635209996 to record it as a full architectural decision, per this repo's own convention that decisions affecting more than one feature belong in a full ADR rather than a feature-local log.

#### 2026-09-03 16:00:00.000Z - No change to REQ-003/004's design after root-causing the opaque-failure symptom to a client-side gap

Decided not to broaden this feature's scope to "fix" the client-side tool-error-rendering gap that root-causes the opaque-failure symptom observed in Tasks 1.1-1.3, since it lives outside specmgr's own code (in the calling agent's tool-invocation harness) and specmgr has no way to control or detect which MCP client is in use. Decided instead that this finding is evidence *for* REQ-003/004 as already designed, not a reason to change it: since a tool's ordinary successful return value has been observed to pass through completely regardless of size/content, while an `is_error=true` result is empirically at the mercy of a client's own (possibly lossy) rendering, converting `validate` from raise-on-failure to always-returns-`{valid, errors}` sidesteps the lossy path entirely, independent of which client calls it.

#### 2026-09-03 15:00:00.000Z - Design questions resolved during plan refinement

Resolved, ahead of Phase 1, the four open design questions the plan had deferred: (1) the generic `validate` tool's domain list excludes `adr` (12-way, matching `update`/`set_classification`/`delete`'s precedent), since `validate_adr` is structurally different (`id`-based, disk-touching, no `full` parameter) from the twelve identical-signature whole-body `validate_<d>` tools -- `validate_adr` stays standalone and unchanged; (2) the `{valid, errors}` result shape is `errors: list[{message: str}]` with no `field` key, since no existing machinery separates field/line data back out of `feat-27-validation`'s already-fused enriched message strings, and a `field` key would be `None` for `AssertionError`/YAML-sourced errors regardless; (3) a failed `list_<d>` entry uses the fixed marker `title="<failed to parse>"` with `ref=path.stem` (identical to every domain's existing successful-entry derivation), with directory/permission enumeration errors left explicitly out of scope; (4) REQ-007's previously-conditional `path`-field decision is resolved to "yes, implement" for all eleven other whole-body domains, as an absolute/resolved path rather than `FeatSummary`'s current unresolved form -- `FeatSummary.path` itself is retrofitted to match, and `DocSummary.ref`'s "must not read this off disk" docstring policy is revised accordingly, since direct reads become a sanctioned, first-class option for every domain rather than a `feat`-only divergence. Also corrected a stale "eleven" `validate_<d>` tool count to the actual thirteen throughout the plan.

#### 2026-09-03 14:27:36.412Z - Scope and design decisions recorded at creation

Combined issues #81 and #83 into one feature (they cross-reference each other and both concern validation-result reporting). Decided the generic `validate` tool consolidates only `validate_<d>` (not `parse_<d>`/`get_<d>`), matching the existing precedent that only write-adjacent tools are consolidated into generic dispatch tools; the per-domain tools are removed outright once migrated, not kept as backward-compatible wrappers, matching the `update`/`set_status`/`delete` precedent. Decided `list_<d>`'s failure reporting adds an `error_count` header field and folds failed documents directly into `results` (marker `title` + `error` field) rather than a separate parallel array, so a caller sees failures without a second lookup. Decided to investigate first (Phase 1) whether issue #83's own two literal repro cases still reproduce against current HEAD, following the same method `feat-67-70-71` used for issues #70/#71, rather than assuming a code fix is still needed.
