---
classification: null
created: '2026-09-04 23:25:55.412+02:00'
id: feat-99-list-item
status: planning
type: feat
updated: '2026-09-09 05:05:09.213+02:00'
version: 1.0.0
---

# Feature: Soft-Wrapped List Items Break create_feat/validate_feat (and Likely Other models/md Domains)

## Plan

### Overview

Soft-wrapped (lazy-continuation) list/checklist item text -- a bullet whose text continues onto an indented second physical line -- currently breaks the shared models/md parser used by create_feat/validate_feat and, likely, every other whole-body domain built on the same parser (req, uc, tsk, qa, prb, gol, rsk, dec, sop, vcr, sysrs). The failure surfaces to MCP callers only as an opaque "Error executing tool `<name>`" with no field path, line reference, or cause/fix hint, defeating the actionable-error contract feat-27-validation established. This feature investigates the scope of the problem across models/md consumers and closes the gap: either by teaching the parser to join soft-wrapped list item lines per standard CommonMark lazy-continuation semantics, or by explicitly rejecting them with an actionable error, plus stopping generic MCP tool error handling from swallowing the underlying exception message.

### Requirements

- REQ-001: Confirm the scope of the parser-level vs. feat-specific bug across all twelve models/md whole-body domains.
- REQ-002: The parser either supports CommonMark lazy-continuation list items (joining wrapped lines) or rejects them with an actionable error (field path, line reference, cause/fix hint).
- REQ-003: MCP tool error handling stops swallowing the underlying exception message for create_/validate_/update tools, surfacing the actionable detail to the client.
- REQ-004: The `get_<d>_template`/`get_<d>_example` outputs and AGENTS.md document the resulting behavior/constraint.

### Acceptance Criteria

- [x] ACC-001: A written summary confirms whether the bug is shared-parser-level (affecting all twelve whole-body domains) or feat-specific, based on reproduction against at least one other domain (e.g. req or tsk).
- [ ] ACC-002: A document with a soft-wrapped list item either parses/validates successfully with the wrapped text correctly joined, or fails with an AssertionError/ValidationError carrying a field path, a 1-based line reference, and a cause/fix hint -- never an opaque unhandled exception.
- [x] ACC-003: An MCP tool call that fails validation (e.g. create_feat) surfaces the underlying exception message to the client, not just "Error executing tool `<name>`".
- [ ] ACC-004: AGENTS.md and the affected `get_<d>_template`/`get_<d>_example` outputs reflect the resulting behavior/constraint on soft-wrapped list items.

### Scope

#### Included

- Reproducing and diagnosing the soft-wrap failure in the shared models/md list-item parsing path.
- Deciding and implementing either lazy-continuation joining or an explicit actionable rejection for soft-wrapped list items.
- Auditing (not necessarily deeply fixing) whether the same failure mode reproduces in at least one other models/md domain besides feat.
- Fixing the MCP error-handling layer so raised AssertionError/ValidationError messages reach the client instead of being replaced by a generic "Error executing tool `<name>`" message.
- Updating AGENTS.md and template/example resource content to document the resulting behavior.

#### Explicitly Out Of Scope

- A full rewrite of the models/md parser architecture.
- Fixing every other unrelated opaque-MCP-error case not tied to list-item parsing.
- Adding brand-new CommonMark features beyond lazy-continuation list items (e.g. nested sub-lists, loose vs. tight list semantics).
- Retroactively reformatting existing on-disk documents that happen to contain soft-wrapped list items.
- Fixing the analogous un-guarded single-line-regex pattern on `vcr.Verifies`/`vcr.Coverage` (`vcr/models/v1/body.py`) -- those are `MarkdownParagraph` fields, not `MarkdownListItem`s, so they share this bug's root cause but not its `MarkdownListItem`-scoped fix; tracked as a follow-up, not fixed here.

### Dependencies

#### Depends On

- feat-27-validation and feat-67-70-71's actionable-error conventions (field path, line reference, cause/fix hint), which this feature must remain consistent with.

### Design Notes

The parser is line-oriented so it can compute 1-based line references for actionable error messages. The original diagnosis pass (below) speculated that joining soft-wrapped list-item lines (standard CommonMark lazy continuation) might complicate that line-tracking, since a single logical item would then span multiple physical lines. **Correction (2026-09-09):** direct verification against this codebase shows that concern was moot -- `_line` already only ever names an item's own *first* physical line, even for fields that already span many lines today (e.g. `TaskItem.content`, or any multi-line `MarkdownSection`); joining would not have required any change to `_line`/`_offset` plumbing. Noted for the historical record; it did not end up driving the fix decision below.

Diagnosis (2026-09-04) narrowed the failure to `MarkdownListItem` subclasses that impose a structural marker/pattern check on their own text (`TaskItem`, `RequirementItem`, `AcceptanceCriterionItem`), not to free-form lists (e.g. `req`'s `## Tags`, which tolerates the same wrap without error). **Correction (2026-09-09):** the original wording attributed this to "the shared `models/md` list-item extent/extraction logic" itself -- that is inaccurate. Direct verification shows `MarkdownListItem.get_extent`/`.text` already correctly join a lazy-continuation line per CommonMark semantics (a soft-wrapped item's `.text` already returns the full, correctly-joined multi-line string); the actual break is one level up, in each domain's own structural regex applied to that already-correct `.text` (e.g. `TaskItem._MARKER_PATTERN = r"^\[( |x|X)\]\s*(?P<description>.*)$"`, used without `re.DOTALL` and relying on an unanchored `$` that cannot match past an embedded `\n`). The original diagnosis sentence is preserved here verbatim for history: "the bug sits in the shared `models/md` list-item extent/extraction logic before any domain-specific pattern is even applied."

**Fix decision (2026-09-09):** reject soft-wrapped list items with an actionable error rather than joining/accepting them -- lower risk, smaller diff, and consistent with feat-27-validation's preference for explicit rejection over silently different parsing semantics; also matches this feature's own "no new CommonMark features" scope note. The fix is a single shared helper on `MarkdownListItem` (`models/md/markdown_list_item.py`) that asserts an item's `.text` is a single physical line before any domain regex runs, called from every structurally-checked subclass rather than duplicated per domain.

**Audit (2026-09-09), REQ-001:** swept all twelve `models/md` whole-body domains (req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs) for `MarkdownListItem`/`TaskItem` subclasses with their own structural regex. Beyond the three already-confirmed classes (`TaskItem`, `RequirementItem`, `AcceptanceCriterionItem`), found exactly two more with the identical "always single-line, no DOTALL needed" assumption: `rsk.ThresholdItem` (`rsk/models/v1/risk_matrix.py`) and `rsk.StrategyItem` (`rsk/models/v1/tara.py`) -- both currently unaffected in practice only because their content happens to always be short/single-line today, not because they are structurally immune. Every other structural list-item check already uses `re.DOTALL` (`QuadrantItem`/`MitigationItem`/`StatusItem` in `rsk/models/v1/tara.py`; the EARS/DTAIS/RASCI items in `general/models/`; the `sysrs` cross-reference lists' shared `_validate_cross_reference_items()` helper), or is a heading-based check reading only `self.text.splitlines()[0]` (`dec.Option`, `sop.Step`, `vcr`'s heading items), or is genuinely free-form with no regex at all -- none of those need the new guard. See Explicitly Out Of Scope for the one related-but-deliberately-unfixed finding (`vcr.Verifies`/`vcr.Coverage`).

### Task List

#### Phase 1: Diagnosis

- [x] Task 1.1: Reproduce the failure with a minimal feat document containing one soft-wrapped list item.
- [x] Task 1.2: Bisect to confirm the failure is specifically the list-item lazy-continuation join, not something else.
- [x] Task 1.3: Check whether the same construct reproduces against one other models/md domain (e.g. req or tsk) to confirm shared-vs-local scope.

#### Phase 2: Fix

- [ ] Task 2.1: Add a shared single-physical-line guard to `MarkdownListItem` in `models/md/markdown_list_item.py` (e.g. a `single_line_text(self, *, expected: str) -> str` method), raising an actionable `AssertionError` (field path, 1-based line reference, explicit "soft-wrapped/lazy-continuation list items are not supported" cause, and a "join onto one physical line" fix hint) when a structurally-checked item's `.text` spans more than one physical line.
- [ ] Task 2.2: Wire the new guard into the five confirmed call sites: `tsk.TaskItem.checked`/`.description` (`tsk/models/v1/task_item.py`), `feat.RequirementItem.description` and `feat.AcceptanceCriterionItem.criterion_description` (`feat/models/v1/body.py`), `rsk.ThresholdItem` (`rsk/models/v1/risk_matrix.py`), and `rsk.StrategyItem` (`rsk/models/v1/tara.py`). Free-form `MarkdownListItem`/`MarkdownListItemWithNotes` usages (Tags, cross-ref lists, etc.) must keep tolerating soft-wraps unchanged.
- [ ] Task 2.3: Confirm (no code change expected) that the MCP tool error wrapper already surfaces the underlying exception message end-to-end, via one live `create_feat`/`validate` call against a soft-wrapped fixture, and check ACC-003/REQ-003 accordingly.

#### Phase 3: Documentation and Verification

- [ ] Task 3.1: Update AGENTS.md (and/or `.specmgr/conventions.md`) to document the single-physical-line constraint on structurally-checked list items, and confirm the `get_<d>_template`/`get_<d>_example` outputs for `tsk`/`feat`/`rsk` don't already contain soft-wrapped bullets (expected: they don't).
- [ ] Task 3.2: Add/extend unittest coverage: the shared guard itself (`tests/models/md/test_markdown_list_item.py`), each of the five call sites (`tests/tsk/models/v1/test_task_item.py`, `tests/feat/models/v1/test_body.py`, and the `rsk` risk-matrix/tara test files), and one end-to-end MCP tool test proving the actionable error reaches the client.
- [ ] Task 3.3: Run the full quality gate: `ruff format --check && ruff check`, `vulture`, `pytest -n auto`, and regenerate `specmgr docs`/`adr-toc` if any touched docstrings changed.

## Progress

### Current Status

**As of 2026-09-04**: Phase 1 diagnosis is complete. Reproduced against a minimal `feat` document (`### Requirements` REQ-NNN bullet) and independently against `tsk`'s shared `TaskItem` checklist, confirming this is a shared `models/md` parser-level bug, not `feat`-specific -- it affects any structural, marker/pattern-checked list item (`TaskItem`, `RequirementItem`, `AcceptanceCriterionItem`), while free-form bullet lists (e.g. `req`'s `## Tags`) are unaffected. Separately, an unrelated but closely-related parser fragility was also hit while drafting this very document: a bare `<word>`-shaped token (e.g. `<name>`, `<d>`) in prose is valid CommonMark inline raw HTML and is rejected -- this is expected CommonMark behavior, not a bug, but it shares the same "easy to trigger by accident, painful to diagnose" profile as the soft-wrap issue. Good news: as of today, both failure modes now produce **actionable** errors (field path + line reference, plus an explicit fix hint for the raw-HTML case) through both the disk-free `validate` tool and the real `create_feat` write path -- the opaque `"Error executing tool <name>"` failure mode described in the original issue no longer reproduces on this server, satisfying ACC-003 already. A live audit of this repository's own 40 `.specmgr/feat/*/README.md` documents via `list_feat` found 34 currently fail to parse: 16 are the soft-wrapped `REQ-NNN`/`ACC-NNN`/task-item bullets this feature targets, 3 are the bare-HTML-tag case (`</content>`, `<d>`, `<name>`), 2 are an adjacent timestamp-granularity mismatch in `### Updates`/`### Decisions Made` heading entries, and the remaining 13 are pre-existing, unrelated issues (invalid frontmatter timestamp formats, invalid `status` enum values, structural drift) explicitly out of this feature's scope.

**Update 2026-09-09**: the Phase 2/3 plan has been refined into concrete tasks based on a deeper code-level read of the actual parser and every domain (see Design Notes): the true root cause is each affected domain's own non-`DOTALL` structural regex, not the shared extent/extraction logic as originally diagnosed; the fix will be a single shared `MarkdownListItem` guard (reject, not join) wired into five confirmed call sites (`TaskItem`, `RequirementItem`, `AcceptanceCriterionItem`, `rsk.ThresholdItem`, `rsk.StrategyItem`), found via a full twelve-domain audit. No source code has changed yet -- this update is planning/documentation only; Phase 2/3 implementation remains outstanding.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-09 03:03:32.000Z - Phase 2 plan refined: reject decision, shared-helper design, full domain audit

Refined the Phase 2/3 task list based on a deeper code-level investigation: confirmed the root cause is each domain's own non-DOTALL structural regex applied to an already-correctly-joined `.text`, not the shared extent/extraction logic as originally diagnosed; confirmed the line-tracking concern raised in the original Design Notes was moot (`_line` already only ever names an item's first physical line, regardless of how many physical lines its text spans). Audited all remaining ten `models/md` whole-body domains and found two more affected classes (`rsk.ThresholdItem`, `rsk.StrategyItem`) beyond the three already confirmed (`TaskItem`, `RequirementItem`, `AcceptanceCriterionItem`); everything else is either free-form, already `re.DOTALL`-guarded, or a heading-only check immune by construction. Corrected the Design Notes paragraph that had misdiagnosed the root cause. No source code changed in this pass -- planning/documentation only.

#### 2026-09-04 21:40:47.000Z - Phase 1 diagnosis complete; error-swallowing already appears fixed

Reproduced the soft-wrap failure against a minimal `feat` document (`REQ-NNN` bullet) and confirmed it is a shared `models/md` parser-level issue, not `feat`-specific, by also reproducing it against `tsk`'s `TaskItem` checklist (fails the bare checkbox-marker check itself, before any domain-specific regex is applied); a free-form bullet list with no structural field check (`req`'s `## Tags`) tolerated the same wrap without error. Separately reproduced the unrelated bare-`<word>`-as-raw-HTML case (`<name>`, `<d>`) that was also hit opaquely while first drafting this document. Both failure modes now surface fully actionable errors (field path, line reference, and -- for the raw-HTML case -- an explicit fix hint) through the `validate` tool and through `create_feat` itself; the opaque `"Error executing tool <name>"` message described in issue #99 no longer reproduces on the current server. A live audit of this repository's own 40 feature documents found 34 currently fail to parse, 16 of them via exactly this soft-wrap pattern and 3 via the bare-HTML-tag pattern, with the remaining 15 being unrelated pre-existing issues.

#### 2026-09-04 21:22:24.000Z - Created

Feature drafted from GitHub issue #99, which reported that soft-wrapped (lazy-continuation) list items break create_feat/validate_feat with an opaque, unhelpful error.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-09 03:03:32.000Z - Reject (not join) soft-wrapped list items, via one shared models/md helper, after auditing all twelve domains first

Decided, with user confirmation, to (1) reject soft-wrapped/lazy-continuation list items with an actionable error rather than join/accept them -- lower risk, smaller diff, consistent with feat-27-validation's preference for explicit rejection over silently different parsing semantics; (2) implement the guard once as a shared `MarkdownListItem` helper rather than duplicating per-domain regex tweaks, to avoid the same fix being written three-plus times; and (3) audit all twelve `models/md` whole-body domains before implementing, rather than fixing only the two originally-confirmed cases (`feat`, `tsk`) and treating the rest as an unstarted follow-up. The audit (see Design Notes) found two additional affected classes beyond `TaskItem`/`RequirementItem`/`AcceptanceCriterionItem`: `rsk.ThresholdItem` and `rsk.StrategyItem`. Also decided to correct this document's own Design Notes paragraph, which had misdiagnosed the root cause as the shared extent/extraction logic rather than each domain's own structural regex.

### Related PRs / Commits

- [Issue #99](https://github.com/dfch/biz.dfch.SpecMgr/issues/99): tracking issue for this feature.
