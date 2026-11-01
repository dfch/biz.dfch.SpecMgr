---
classification: null
created: '2026-10-02T13:15:57.269+02:00'
id: feat-180-updates
status: done
type: feat
updated: '2026-10-07T06:21:40.914Z'
version: 1.0.0
---

# Feature: Allow Any Markdown Content in Updates/Decisions Made Entries

## Plan

### Overview

Relax `UpdateEntry.content` (and `feat`'s own `DecisionEntry.content`)
across the six domains that carry an "Updates"/"Recent Updates"/"Decisions
Made" section (`vcr`, `feat`, `dec`, `sop`, `sysrs`, `tsk`), so each entry
accepts any markdown content -- multiple paragraphs, lists, code blocks,
block quotes -- not just a single CommonMark paragraph. Today,
`MarkdownParagraph.get_extent()` requires the entry body to form exactly
one paragraph block; a second blank-line-separated paragraph, a bullet
list, or a fenced code block under an update heading fails with a hard
`AssertionError` ("text left over after processing all fields"). The fix
follows the already-shipped `qa/models/v2/body.py`'s
`IntroductionBody(MarkdownStr)` idiom from `feat-114-qa-introduction-any-markdown`:
a new per-domain leaf class (`UpdateEntryContent`, plus `feat`'s
`DecisionEntryContent`) subclassing the base `MarkdownStr` engine class
directly, whose un-overridden `get_extent` swallows everything remaining
regardless of shape. Tracked by
[GitHub issue #180](https://github.com/dfch/biz.dfch.SpecMgr/issues/180).

### Requirements

- REQ-001: `UpdateEntry.content` (`vcr`, `feat`, `dec`, `sop`, `sysrs`, `tsk`) accepts any markdown content verbatim (multiple paragraphs, lists, code blocks, block quotes), not just a single CommonMark paragraph.
- REQ-002: `feat`'s `DecisionEntry.content` (`### Decisions Made`) receives the identical relaxation, since it shares the exact same restriction and shape as `UpdateEntry`.
- REQ-003: `content` remains a mandatory (non-optional) field on every `UpdateEntry`/`DecisionEntry`; a heading with no body content (blank/whitespace-only) still fails to parse, preserving today's "Mandatory" semantics without any new validator code -- the engine's existing mandatory-field zero-extent check already enforces this for the new leaf type, exactly as it does for `MarkdownParagraph` today.
- REQ-004: The new leaf field's content remains reachable through `model_dump()`/`model_dump_json()` (not just `str()`), matching every other opaque leaf field in this engine.
- REQ-005: Every previously-valid single-paragraph Updates/Decisions Made entry continues to parse and round-trip unchanged (strict superset relaxation, no regression).
- REQ-006: The packaged `<domain>_schema.json` (both `docs/` and `<domain>/data/` copies), `docs/api/` docstring exports, and `CHANGELOG.md` all reflect the new shape for every one of the 6 affected domains.

### Acceptance Criteria

- [x] ACC-001: An `UpdateEntry`/`DecisionEntry` containing only a plain paragraph still parses and round-trips identically to today, in all 6 domains (no regression).
- [x] ACC-002: An `UpdateEntry`/`DecisionEntry` containing multiple blank-line-separated paragraphs parses and round-trips successfully, in all 6 domains.
- [x] ACC-003: An `UpdateEntry`/`DecisionEntry` containing a bullet/numbered list parses and round-trips successfully, in all 6 domains.
- [x] ACC-004: An `UpdateEntry`/`DecisionEntry` containing a fenced code block parses and round-trips successfully, in all 6 domains.
- [x] ACC-005: An `UpdateEntry`/`DecisionEntry` with blank/whitespace-only content under its heading still fails to parse with an `AssertionError` (non-blank requirement preserved), in all 6 domains.
- [x] ACC-006: `model_dump()` on a parsed document surfaces the new leaf field's real text content for a non-paragraph body, not an empty object.
- [x] ACC-007: The full test suite passes after every phase below, not just at the end.
- [x] ACC-008: Each of the 6 phases ends with a passing full quality gate (`ruff format --check`, `ruff check`, `vulture`, full test suite) before that phase's own commit -- not just a single check against the final state.
- [x] ACC-009: Every affected domain's packaged `schema.json` (both copies) and `docs/api/` are regenerated and committed in sync with the model change (no drift).
- [x] ACC-010: `CHANGELOG.md` carries an entry describing the relaxation under `[Unreleased]`.
- [x] ACC-011: The upstream merge of `origin/dev` (8e23fed) lands as a single merge commit whose `CHANGELOG.md` is a pure union -- every `[Unreleased]` entry of both parents preserved byte-verbatim, no other content in the file modified -- and PR #182's GitHub `mergeable` state moves from `CONFLICTING` to `CLEAN`.
- [x] ACC-012: A `feat-reviewer` pass over the merged branch completes against this plan's REQ-001..006 and ACC-001..011; every reported finding is fixed and re-gated before closeout; every met ACC box is checked in this README with a dated review entry.

### Scope

#### Included

- New `UpdateEntryContent` (and `feat`'s `DecisionEntryContent`) leaf classes, and the `content` field retype, in `vcr`/`feat`/`dec`/`sop`/`sysrs`/`tsk`'s `models/v1/body.py`.
- Test additions in each domain's `tests/<domain>/models/v1/test_body.py`, plus a check (and update only if needed) of each domain's `tests/<domain>/models/v1/test_parser.py` for paragraph-specific fixtures/assertions. `tsk`'s `test_create_tsk.py` requires no change (its only `## Recent Updates` fixture is a single paragraph, verified) and is explicitly excluded.
- Regenerated `docs/*_schema.json` and each domain's packaged `<domain>/data/<domain>_schema.json`, plus `docs/GENERATED.md`/`docs/api/`.
- A `CHANGELOG.md` entry under `[Unreleased]`.
- A separate commit after each of the 6 phases' own passing quality gate, rather than one final commit for the whole feature.

#### Explicitly Out Of Scope

- Any change to example/template markdown files (`*_example.md`/`*_template.md`) -- left unchanged (still single-paragraph, which remains valid).
- Any new validator code for "non-blank content" -- preserved for free by keeping `content` a mandatory field (see Design Notes).
- Any change to heading structure, the `@alias` timestamp-title pattern, `min_length=1` on the `updates`/`decisions` collection, or the existing newest-first `_validate_newest_first` ordering check.
- Any change to the shared `models/md` engine itself.
- A new `vcr/models/v2` (or equivalent) schema version for any of the 6 domains -- this stays an in-place `v1` field-type relaxation, per the project's established precedent (e.g. PRB's `problem_statement`, DEC's RASCI/Source additions).

### Dependencies

#### Depends On

- None -- builds on the already-shipped `feat-114-qa-introduction-any-markdown` precedent (the `IntroductionBody` idiom), but has no hard dependency on it.

#### Blocks

- None known.

### Design Notes

`UpdateEntryContent`/`DecisionEntryContent` are leaf classes (no declared
fields) applying no `@markdown` type/tag restriction of their own --
unlike `MarkdownParagraph`/`MarkdownSection*`/`MarkdownComment`, each of
which restricts `get_extent`'s match to one specific token type. Because
of that, their `get_extent`/`from_text` fall back to the unmodified
`MarkdownStr` base implementation, which simply consumes everything
remaining in the given text regardless of its shape. Since `content` is
always declared as the sole/last field on `UpdateEntry`/`DecisionEntry`
(nothing follows it before the next heading), "everything remaining" is
exactly correct -- no custom stop-condition override is needed, unlike
`qa`'s own `QaAnswer` (which needs one because further adjacent Q&A pairs
can follow it within the same enclosing section).

Note this extends the `feat-114` idiom into new territory, rather than
being a byte-for-byte mirror of it: `IntroductionBody`
(`qa/models/v2/body.py`) is declared `Optional` and never exercises the
mandatory-field code path. `UpdateEntryContent`/`DecisionEntryContent` are
the first use of this leaf-class idiom as a *mandatory* field -- verified
to work via `process_field`'s existing `assert extent > 0` check
(`models/md/markdown_str.py:360`), see below.

Each new class adds a `text` computed property (`return self._value`),
mirroring `IntroductionBody.text`/`QaAnswer.text` verbatim. This is
required, not cosmetic: `MarkdownStr` itself declares zero pydantic
fields (`_value` is a private attribute, invisible to `model_dump()`) --
without a `text` computed property, a bare `MarkdownStr`-typed field would
serialize to an empty `{}` object over `model_dump()`/`model_dump_json()`,
exactly the MCP-transport path this server uses for every tool response.
The `.text` property is also required for call-site compatibility, not
just serialization: existing positive-path tests already read
`.content.text` directly on the current `MarkdownParagraph` field (e.g.
`tests/feat/models/v1/test_body.py:582`), and those call sites must keep
working unchanged after the retype.

No new validator code is needed to preserve the "mandatory, non-blank"
rule. `@field_validator("_value")` is structurally impossible (`_value`
is a private attribute, not a `model_fields` entry -- pydantic rejects
this at class-definition time; a dead, commented-out attempt already
exists at the bottom of `models/md/markdown_str.py` proving this was
already tried and abandoned). `@model_validator(mode="after")` also does
not work for a leaf class: it fires during `cls()` construction, strictly
before `from_text` mutates `instance._value = text` onto the
already-built instance, so it can never see the real content. Instead,
`content` stays a mandatory (non-`Optional`) field, and the engine's
generic field-distribution code (`process_field` in `markdown_str.py`)
already asserts `extent > 0` for mandatory fields; the base
`MarkdownStr.get_extent` returns `0` for blank text (no tokens found),
exactly the same zero-extent behavior `MarkdownParagraph.get_extent` has
for blank input today. So the non-blank requirement is preserved for
free, purely by keeping `content` mandatory.

None of the 6 domains' existing `UpdateEntry`/`DecisionEntry` negative-path
tests assert on specific error-message text today -- they all use bare
`assertRaises(AssertionError)`/`assertRaises(ValidationError)` (e.g.
`tests/dec/models/v1/test_body.py:907-909`,
`tests/feat/models/v1/test_body.py:629-636`). Since the new leaf type's
`get_extent` returns `0` for blank text exactly like
`MarkdownParagraph.get_extent` does, these existing tests require no
changes -- only confirmation that they still pass unmodified. Phase 110's
tasks below are therefore purely additive (new positive tests), not
corrective.

Each phase's quality-gate task (`ruff format --check`/`ruff check`/
`vulture`/full test suite) is run manually before that phase's own commit
even though this repo's installed pre-commit hooks already re-enforce the
identical checks -- plus the `specmgr-schema`/`specmgr-schema-*-package`
drift hooks and `specmgr docs` -- automatically on every `git commit`
touching `src/**/*.py`/`tests/**/*.py` (see `AGENTS.md`). The manual run
is not redundant busywork: it is purely for fast local feedback, catching
a failure before attempting the commit rather than discovering it
mid-commit and having to fix-then-retry.

### Related Decisions

- `feat-114-qa-introduction-any-markdown` (feat): established the `IntroductionBody(MarkdownStr)` leaf-class idiom this feature reuses for `UpdateEntryContent`/`DecisionEntryContent`.

### Task List

#### Phase 100: Model change

- [x] Task 100.100: In `vcr/models/v1/body.py`, add `UpdateEntryContent(MarkdownStr)` with a `text` computed property; retype `UpdateEntry.content`. Do NOT drop the `MarkdownParagraph` import -- it stays in use by `CrossReference.value`/`.notes`, `Coverage.value`, and `AcceptanceCriterion.description` in this same file.
- [x] Task 100.110: In `feat/models/v1/body.py`, add `UpdateEntryContent(MarkdownStr)`; retype `UpdateEntry.content`.
- [x] Task 100.120: In `feat/models/v1/body.py`, add `DecisionEntryContent(MarkdownStr)`; retype `DecisionEntry.content`; drop the now-unused `MarkdownParagraph` import if nothing else in the module uses it.
- [x] Task 100.130: In `dec/models/v1/body.py`, add `UpdateEntryContent(MarkdownStr)`; retype `UpdateEntry.content`. Do NOT drop the `MarkdownParagraph` import -- it stays in use by `DecisionOutcome.statement` in this same file.
- [x] Task 100.140: In `sop/models/v1/body.py`, add `UpdateEntryContent(MarkdownStr)`; retype `UpdateEntry.content`; drop the now-unused `MarkdownParagraph` import if nothing else in the module uses it.
- [x] Task 100.150: In `sysrs/models/v1/body.py`, add `UpdateEntryContent(MarkdownStr)`; retype `UpdateEntry.content`; drop the now-unused `MarkdownParagraph` import if nothing else in the module uses it.
- [x] Task 100.160: In `tsk/models/v1/body.py`, add `UpdateEntryContent(MarkdownStr)`; retype `UpdateEntry.content`; drop the now-unused `MarkdownParagraph` import if nothing else in the module uses it.
- [x] Task 100.165: Correct the 24 pre-existing test incompatibilities the retype surfaced and regenerate the stale artifacts so the phase-end full suite is green before the commit: (a) the 21 scalar (+10 tuple) `.content.text`/`model_dump()` expected values in the 6 domains' `test_body.py`/`test_parser.py`/`tests/tsk/tools/test_parse_tsk.py` that pin the old `MarkdownParagraph.text` stripped form gain the new leaf type's raw trailing newline (mechanical expected-value update only); (b) `tests/regression/test_issue_27.py`'s `TestFeat7Task029StrayListMarkerRegression` (3 tests) is deleted together with its trigger-2 fixtures -- the pinned trigger (a `+`-prefixed continuation line inside a `## Recent Updates` entry) is now valid any-markdown content by design (issue #180, ACC-003); the same actionable "text left over" message stays pinned at engine level in `tests/models/md/test_validation_error_baseline.py`, and the module docstring notes the supersession (user-approved decision); (c) regenerate the 6 affected domains' `docs/<d>_schema.json` and packaged `<d>/data/<d>_schema.json` copies plus `specmgr docs` -- greens the 5 `test_matches_fresh_generate_*_schema_output` drift tests (note: `tsk`'s resource test file carries no drift test, a pre-existing asymmetry left untouched; the pre-commit `specmgr-schema-tsk-package` hook still enforces its packaged copy).
- [x] Task 100.170: Phase-end quality gate: `uv run --frozen ruff format --check && uv run --frozen ruff check`; `uv run --frozen vulture src/ whitelist.py --min-confidence 60`; run the full test suite. All must pass before moving to Phase 110.
- [x] Task 100.180: Commit Phase 100's changes (the 6 domains' `body.py` model retypes) before starting Phase 110.

#### Phase 110: New test coverage

- [x] Task 110.100: In `tests/vcr/models/v1/test_body.py`, add multi-paragraph/list/code-block positive tests for `UpdateEntry.content` (existing negative tests use bare `assertRaises`, not message-specific assertions, so they need no fix -- confirm they still pass unmodified).
- [x] Task 110.110: In `tests/feat/models/v1/test_body.py`, do the same for both `UpdateEntry` and `DecisionEntry`.
- [x] Task 110.120: In `tests/dec/models/v1/test_body.py`, do the same.
- [x] Task 110.130: In `tests/sop/models/v1/test_body.py`, do the same; also check `tests/sop/models/v1/test_parser.py` for any paragraph-specific fixtures/assertions and update only if needed.
- [x] Task 110.140: In `tests/sysrs/models/v1/test_body.py`, do the same; also check `tests/sysrs/models/v1/test_parser.py` for any paragraph-specific fixtures/assertions and update only if needed.
- [x] Task 110.150: In `tests/tsk/models/v1/test_body.py`, do the same; also check `tests/tsk/models/v1/test_parser.py` for any paragraph-specific fixtures/assertions and update only if needed. `tests/tsk/tools/test_create_tsk.py` needs no edit (its only `## Recent Updates` fixture is a single paragraph) -- confirm it still passes unmodified rather than editing it.
- [x] Task 110.155: For parity with Tasks 110.130/110.140/110.150's `test_parser.py` check, also check `tests/vcr/models/v1/test_parser.py`, `tests/feat/models/v1/test_parser.py`, and `tests/dec/models/v1/test_parser.py` for any paragraph-specific fixtures/assertions and update only if needed.
- [x] Task 110.160: Add/confirm `model_dump()` assertions covering the non-paragraph content case (ACC-006).
- [x] Task 110.170: Phase-end quality gate: `uv run --frozen ruff format --check && uv run --frozen ruff check`; `uv run --frozen vulture src/ whitelist.py --min-confidence 60`; run the full test suite. All must pass before moving to Phase 120.
- [x] Task 110.180: Commit Phase 110's changes (the new/updated tests) before starting Phase 120.

#### Phase 120: Regenerate build artifacts

- [x] Task 120.100: Run `specmgr schema` for each of the 6 domains -- two separate invocations per domain (`--output-dir docs/` and `--output-dir src/biz/dfch/specmgr/<domain>/data`), 12 invocations total, unless relying on the corresponding `specmgr-schema`/`specmgr-schema-<domain>-package` pre-commit hooks to regenerate both automatically on commit.
- [x] Task 120.110: Run `specmgr docs` to regenerate `docs/GENERATED.md`/`docs/api/` for the changed docstrings.
- [x] Task 120.120: Phase-end quality gate: `uv run --frozen ruff format --check && uv run --frozen ruff check`; `uv run --frozen vulture src/ whitelist.py --min-confidence 60`; run the full test suite. All must pass before moving to Phase 130.
- [x] Task 120.130: Commit Phase 120's changes (the regenerated schema/docs artifacts) before starting Phase 130.

#### Phase 130: CHANGELOG and final verification

- [x] Task 130.100: Add a `CHANGELOG.md` entry under `[Unreleased]` -> `### Changed` (backward-compatible field-type relaxation, not a new feature) describing the relaxation across the 6 domains.
- [x] Task 130.110: `uv run --frozen ruff format --check && uv run --frozen ruff check`.
- [x] Task 130.120: `uv run --frozen vulture src/ whitelist.py --min-confidence 60`.
- [x] Task 130.130: Run the full test suite one final time.
- [x] Task 130.140: Review `git status`/`git diff` for completeness, then commit.

#### Phase 140: Upstream dev merge (CHANGELOG conflict)

- [x] Task 140.100: `uv sync --all-extras --frozen` to pick up dev's uv.lock bump (776c13d, the uv group) that the merge will land.
- [x] Task 140.110: `git merge origin/dev` (local `origin/dev` at 8e23fed already matches the remote, verified via `git ls-remote`) -- expect exactly one conflict, `CHANGELOG.md`, the only file both sides touched (our 37 changed files intersect their 197 in one).
- [x] Task 140.120: Resolve the `CHANGELOG.md` conflict in `[Unreleased]` -> `### Changed` as a union of both bullets, ours first (the feat-153 merge precedent): keep this feature's #180 entry (timestamped entries' `content` accepts any markdown), then dev's #177 entry (`list_references` gains the `FEAT` tag); nothing else in the file touched.
- [x] Task 140.130: Verify the resolution is a pure union (ACC-011): `git diff HEAD^1..HEAD -- CHANGELOG.md` and `git diff HEAD^2..HEAD -- CHANGELOG.md` each show only added lines -- no modification or deletion of either parent's content, every entry byte-verbatim against its parent.
- [x] Task 140.140: `git add CHANGELOG.md && git commit` with the default merge message (the pre-commit hook did run -- for a conflicted-merge commit it checked only the merge-conflict file; see the Phase 140 progress entry below).
- [x] Task 140.150: Regenerate the derived docs to a fixed point -- `uv run --frozen specmgr docs`, `uv run --frozen specmgr mcp-docs`, `uv run --frozen specmgr adr-toc` -- and confirm zero drift (feat-180 touched no tool docstrings); commit only if any changed.
- [x] Task 140.160: Phase-end quality gate: `uv run --frozen ruff format --check && uv run --frozen ruff check`; `uv run --frozen vulture src/ whitelist.py --min-confidence 60`; run the full test suite. All must pass before the push.
- [x] Task 140.170: `git push`, then poll `gh pr view 182 --json mergeable` (without `--watch`, repeating as needed) until it reports `CLEAN`, clearing the current `CONFLICTING`.

#### Phase 150: Review and closeout

- [x] Task 150.100: Run the `feat-reviewer` subagent over the merged branch, checking code/tests/docs against this plan's REQ-001..006 and ACC-001..011.
- [x] Task 150.110: If the review reports findings, fix them and re-run the Task 140.160 full gate before proceeding; if it reports none, record that explicitly in the review entry (ACC-012).
- [x] Task 150.120: Check off every met ACC box in this README's `### Acceptance Criteria` and add a dated review entry to `### Updates` recording the outcome.
- [x] Task 150.130: Review `git status`/`git diff` for completeness, then commit (bookkeeping only, unless Task 150.110 landed fixes) and push.

## Progress

### Current Status

**As of 2026-10-02**: All four phases are COMPLETE, each with its own
passing-gate commit. Phase 100 (Model change, b6492cd) landed the
per-domain `UpdateEntryContent`/`DecisionEntryContent` leaf retypes
plus the approved Task 100.165 fix-up (21 scalar (+10 tuple)
trailing-newline expected-value updates, the superseded feat-7 Task
0.29 regression
class deleted, 6x2 schema copies + `specmgr docs` regenerated;
`3900 passed, 2688 subtests passed` gate). Phase 110 (New test
coverage, ebf4f17) added 39 new positive/confirmation tests across the
6 domains' `test_body.py` files (multi-paragraph/bullet/numbered/
code-block/block-quote bodies parse and round-trip byte-identically,
`.content.text` carries the raw body including the trailing `"\n"`,
`model_dump()` surfaces the real text per ACC-006, blank-content
negatives confirmed or added per ACC-005; all 6 domains'
`test_parser.py` files checked with no change needed, and
`tests/tsk/tools/test_create_tsk.py` confirmed passing unmodified;
`3939 passed, 2698 subtests passed` gate). Phase 120 (Regenerate build
artifacts, f6c9f9b) was a verification pass with zero drift (all 13
`specmgr schema` invocations (12 per-domain + 1 all-types) reported
`(unchanged)`, `specmgr docs`/`specmgr mcp-docs` reported no drift,
plus this README's own newest-first entry ordering fixed; `3939
passed, 2698 subtests passed` gate). Phase 130 (CHANGELOG and final
verification) added the `[Unreleased]` -> `### Changed`
`CHANGELOG.md` entry and re-ran the final full gate green (`3939
passed, 0 failed`). Implementation finished: the feature's status was
set to `review` (c096158) and PR #182 opened against `dev`.

**As of 2026-10-03**: PR #182 is open with all CI checks green
(builds 3.11/3.12/3.13, CodeQL, Analyze) but GitHub reports
`mergeable: CONFLICTING` -- upstream `dev` advanced 6 commits past
this branch's merge base (fac70948), and a read-only `git merge-tree`
confirms the merge would conflict in exactly one file, `CHANGELOG.md`
(the only file both sides touched). No review has happened yet
either: zero GitHub reviews, empty `reviewDecision`, no `feat-
reviewer` pass recorded, all ACC boxes unchecked. Phases 140 (the
upstream merge + pure-union CHANGELOG resolution per the feat-153
precedent) and 150 (the `feat-reviewer` pass + ACC check-off) were
therefore added to the plan as unchecked; status stays `review` --
the new phases are review-stage work, not implementation.

**As of 2026-10-03**: Phase 140 (upstream dev merge) is COMPLETE:
`origin/dev` (818a2e9, one docs-only feat-185 plan commit past the
plan's stated 8e23fed) merged as a single merge commit (48c0a74)
whose `CHANGELOG.md` resolution is the verified pure union -- our
#180 any-markdown entry first, dev's #177 `FEAT`-tag entry after,
both byte-verbatim against their parents, both parent-diffs
added-lines-only (ACC-011). Zero derived-docs drift, the full
post-merge phase-end gate green (`4052 passed, 0 failed`), the
branch pushed, and PR #182 now reports `mergeable: MERGEABLE` /
`mergeStateStatus: CLEAN` -- it merges cleanly into `dev`. Status
stays `review`: Phase 150 (the `feat-reviewer` pass + ACC
check-off) is the remaining work.

**As of 2026-10-03**: Phase 150 (Review and closeout) is COMPLETE:
the `feat-reviewer` pass (all 11 ACCs MET, no code defects) reported
6 findings (1 major + 2 minor + 3 nit), all fixed and re-gated (12
prompt-instruction files reworded to the new any-markdown `Field`
descriptions, multi-entry non-paragraph pin added in dec's
`TestUpdatesContainer`, whitespace-only `subTest` variants in
vcr/sysrs/tsk, three plan-README nits), the full gate re-run green
(`4052 passed, 0 failed`; serial `2773 subtests passed`), and all 12
ACC boxes (ACC-001..012) checked. Feature closeout done; PR #182
reports `mergeable: MERGEABLE` / `mergeStateStatus: CLEAN` with all
CI checks green.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-03T14:18:17.000Z - Phase 150 (Review and closeout) completed; feat-reviewer findings fixed, all 12 ACCs met

Implemented Tasks 150.100-150.120 (Task 150.100, the `feat-reviewer`
pass, was run by the orchestrator before this phase started; its
findings are the complete set -- it was not re-run here). Review
verdict: all 11 ACCs (ACC-001..011) MET against REQ-001..006, no code
defects, but 6 findings to fix and re-gate before closeout per
ACC-012: 1 major (F1), 2 minor (F2, F4), 3 nit (F3, F5, F6). All six
fixed:

- F1 (major): the 12 packaged `*_create_instructions.md`/
  `*_update_instructions.md` files in the 6 affected domains still
  told the authoring LLM each Updates/Decisions Made entry is
  "followed by a mandatory lead paragraph" (tsk: "a short paragraph
  of update text") -- contradicting the schema's own new `Field`
  descriptions this feature landed. Reworded only the stale shape
  clause in each file to mirror that domain's `UpdateEntry.content`/
  `DecisionEntry.content` `Field` description ("the entry's own update
  text directly under the H3 heading (any markdown content -- multiple
  paragraphs, lists, code blocks, block quotes, not just a single
  paragraph), which is mandatory"; feat: "update/decision text" under
  the H4 heading). `*_example.md`/`*_template.md` files and the DEC
  `Decision Outcome` `statement` lead-paragraph references untouched
  (out of scope per the plan).
- F2 (minor): no test pinned a multi-entry collection whose first
  entry carries non-paragraph content (the load-bearing "consume
  everything remaining stops at the next entry's heading"
  assumption). Extended the pre-existing multi-entry test in
  `tests/dec/models/v1/test_body.py`'s `TestUpdatesContainer`
  (`test_parses_multiple_entries_in_document_order`) with a bullet-list
  first entry; fixture verified mdformat-stable; asserts parse +
  byte-identical round-trip + per-entry `.content.text` values
  (`"- item one\n\n- item two\n"` / `"First entry text.\n"`).
- F3 (nit): ACC-005's "whitespace-only" half was unpinned (the new
  blank-content negatives pin heading-with-nothing-after only). Added
  a whitespace-only (`"   \n"` -- mdformat-normalizes to nothing)
  `subTest` variant to the three Phase 110 blank-content tests in
  `tests/vcr/models/v1/test_body.py`, `tests/sysrs/models/v1/
  test_body.py`, and `tests/tsk/models/v1/test_body.py` (+6 subtests);
  dec/sop/feat's pre-existing blank negatives left unmodified.
- F4 (minor): Task 140.140's stale parenthetical ("no pre-commit hooks
  are installed in this worktree, so nothing runs automatically")
  replaced with a pointer to the Phase 140 progress entry (the hook
  DID run; for a conflicted-merge commit it checked only the
  merge-conflict file).
- F5 (nit): the Task 100.165 "21 `.content.text`/`model_dump()`
  expected values" count undercounted (21 scalar assertions + 5
  list-comprehension assertions carrying 10 tuple values = 26 changed
  assertions / 31 changed value strings; nothing missed, verified).
  Amended to "21 scalar (+10 tuple)" in the task line and all its
  Progress-section echoes (the 2026-10-02 Current Status entry, the
  17:40:00 and 14:30:00 Updates entries); the 14:30:00 Decisions Made
  entry's own "21" stays byte-for-byte per its F6 append-only
  treatment.
- F6 (nit): the 2026-10-02T14:30:00 Decisions Made entry's superseded
  sequencing sentence ("the 24 non-schema test corrections move into
  Phase 110" / "Phase 100's commit ... sequenced after Phase 110's
  corrections land") now carries an appended one-line supersession note
  pointing at the 17:40:00 entry (the corrections landed in Phase 100's
  own commit via in-between Task 100.165); original text otherwise
  byte-for-byte (append-only log convention).

Re-run full gate (Task 150.110, the Task 140.160 gate): `uv run
--frozen ruff format --check` green (1788 files already formatted),
`uv run --frozen ruff check` green (all checks passed), `uv run
--frozen vulture src/ whitelist.py --min-confidence 60` green (exit 0,
no output), `uv run --frozen pytest -n auto --cov=src --cov-report=`
green: **4052 passed in 78.97s (0:01:18), 0 failed** -- unchanged test
count from the Phase 140 baseline (F2/F3 extended pre-existing test
methods, adding no new ones); serial confirmation `uv run --frozen
pytest -n 0` green: **4052 passed, 3 deselected, 2773 subtests passed
in 319.30s** (the +6 subtests are exactly F3's three 2-iteration
`subTest` loops; the remainder of the delta vs Phase 120's 2698 is
dev's merge-side subtests).

All 12 ACC boxes (ACC-001..012) are now checked in the Acceptance
Criteria (ACC-012 by this closeout itself), Tasks 150.100-150.120 are
checked off, and the Current Status section gained its Phase 150
paragraph. This README re-parses cleanly under the worktree's own
feat-180 code (`parse_feat` over the raw file text). Task 150.130: the
two commits (the F1-F3 fix commit, then this plan-README bookkeeping
commit) and the push follow this entry.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-03T08:48:14.000Z - Track the upstream sync and the review pass as Phases 140/150 of this feature; resolve the CHANGELOG conflict as a union per the feat-153 precedent

Considered tracking the `origin/dev` merge in a separate feature
folder, or doing it ad hoc without plan entries. Rejected: the merge
exists solely to make THIS PR mergeable, and the repo's own precedent
(feat-153-off-by-n's Phase 0, "git merge origin/dev, never force")
folds upstream syncs into the feature's own task list. Chose to append
two new phases after the four implementation phases -- 140 = the
merge, 150 = the review -- without renumbering anything that already
exists (the gap-friendly feat-numbering scheme; numbers are permanent
once assigned). The CHANGELOG resolution follows feat-153's recorded
precedent verbatim: a union of both sides' `[Unreleased]` entries in
the standard section order, every entry byte-verbatim against its
respective parent, ours first and dev's after within `### Changed` --
here: our #180 any-markdown entry first, dev's #177 `FEAT`-tag entry
second. Status stays `review` rather than dropping back to
`progress`: Phases 100-130 (the actual implementation) are complete
and committed, and the new phases are review-stage work (unblocking
the PR + the review itself), not new feature scope.

#### 2026-10-02T17:40:00.000Z - Delete (not re-scope) the 3 feat-7 Task 0.29 stray-list-marker regression tests

User-approved after the 2026-10-02T14:30:00.000Z three-group failure
analysis. Rationale: the pinned trigger (a `+`-prefixed continuation line
inside a `## Recent Updates` entry) is dead by design under issue #180's
any-markdown relaxation (ACC-003) -- that input is now valid update-entry
content and no longer raises. Re-scoping rejected: it would require
hunting for a TSK location that preserves the same hint set and would
dilute the file's purpose of reproducing issue #27's real-world
triggers end-to-end; no unique coverage is lost, since
`tests/models/md/test_validation_error_baseline.py`'s
`test_list_field_leaves_a_stray_list_marker_line_unconsumed` pins the
identical actionable "text left over after processing all fields"
message (with the stray-list-marker hint) at engine level. Consequence:
the 24 non-schema test corrections + artifact regeneration land in Phase
100's own commit via a new in-between Task 100.165 (forced by ACC-008's
passing-gate-before-phase-commit), keeping Phase 110 purely additive as
planned; the supersession is recorded in
`tests/regression/test_issue_27.py`'s module docstring.

#### 2026-10-02T16:00:00.000Z - Full quality gate and separate commit per phase, not just at the end

Considered two existing project precedents for multi-phase features: the
lighter one (`feat-177-list-ref-feat`'s single "full quality gate" task at
the very last phase, with only the test suite re-run per earlier phase)
vs. the heavier one (`feat-30-sop`'s "Phase-end quality gate (ruff
format/check, vulture, full unittest) + commit" after every single
phase). Chose the heavier convention for this feature: it touches 6
domains' model files plus their test suites, and the test suite itself
runs in roughly a minute (parallelized via `pytest -n auto`), so four
full gate-runs cost a few extra minutes in exchange for catching any
per-phase lint/vulture regression immediately and keeping each phase
independently revertable via its own commit, instead of only discovering
an issue -- or needing to revert all 4 phases at once -- at the very end.
Phases 100/110/120 each gained a trailing quality-gate task
(`ruff format --check`/`ruff check`/`vulture`/full test suite) plus a
dedicated commit task; Phase 130 already ended with the equivalent
gate + commit shape and needed no change.

#### 2026-10-02T14:30:00.000Z - Kept the plan's raw-`_value` `text` property; the 24 non-schema test corrections move into Phase 110

Phase 100's full-suite run proved the plan's "existing positive tests
read `.content.text`, which both old and new types expose" expectation
incompatible with the plan's own Design Rule 2: `MarkdownParagraph.text`
re-parses `_value` and returns the stripped inline text (no trailing
newline), while the mandated `IntroductionBody`-style `text` returns
`_value` raw, carrying mdformat's canonical single trailing newline --
and qa's own shipped test for that precedent asserts the trailing
newline (`tests/qa/models/v2/test_body.py:230`). Chose the plan's
explicit Design Rule 2 / feat-114 precedent (raw `_value`, no new
stripping behavior) and accepted the 21 resulting assertion updates as
Phase 110 work, rather than deviating from the precedent to keep the old
assertions green unmodified. The same call subsumes the 3 feat-7
stray-list-marker regression tests: their fixture's `+`-prefixed line
inside a `## Recent Updates` entry is now valid content by design
(ACC-003), so re-scoping those tests (not restoring the old rejection)
is the only resolution consistent with the feature. Phase 100's
commit (Task 100.180) is therefore sequenced after Phase 110's
corrections land, not immediately after Phase 100, since the commit-time
pre-commit test hook would otherwise fail on the same 24 tests (the 5
schema-drift tests are handled by the commit-time schema hooks, which
run first).

(Superseded by the 17:40:00 entry: the corrections landed in Phase 100's
own commit via in-between Task 100.165.)

#### 2026-10-02T14:10:00.000Z - No custom non-blank validator needed

Investigated adding a pydantic validator to enforce non-blank content on
the new leaf type. Found `@field_validator("_value")` is structurally
impossible (`_value` is a private attribute, not a `model_fields` entry --
pydantic rejects this at class-definition time, confirmed by a dead,
commented-out attempt already present at the bottom of
`models/md/markdown_str.py`), and `@model_validator(mode="after")` fires
before `from_text` populates `_value` for a leaf class, so it can never
see the real content either. Since `content` stays a mandatory field, the
engine's existing `process_field` assertion (`assert extent > 0` for a
mandatory field) already rejects blank content, because the base
`MarkdownStr.get_extent` returns `0` for empty text -- the exact same
mechanism that made `MarkdownParagraph` reject blank content before this
change. Decided no new validator code is needed at all.

#### 2026-10-02T13:50:00.000Z - Use a per-domain MarkdownStr leaf class, mirroring feat-114's IntroductionBody idiom

Considered keeping `MarkdownParagraph` but overriding its `get_extent`,
vs. declaring the field directly as bare `MarkdownStr`, vs. a dedicated
per-domain leaf subclass. Rejected overriding `MarkdownParagraph` (its
whole contract is "exactly one paragraph token"; overriding it would
fight its own design). Rejected a bare `MarkdownStr` field because
`MarkdownStr` declares zero pydantic fields itself (`_value` is a private
attribute, invisible to `model_dump()`), which would serialize to `{}`
over the MCP transport. Chose a dedicated per-domain leaf class
(`UpdateEntryContent` in `vcr`/`dec`/`sop`/`sysrs`/`tsk`, plus
`DecisionEntryContent` in `feat`) with a `text` computed property,
exactly mirroring the already-shipped
`feat-114-qa-introduction-any-markdown`'s `IntroductionBody` precedent,
keeping each domain owning its own concrete leaf class per the project's
domain-first convention.

#### 2026-10-02T13:20:00.000Z - Track via a GitHub issue first, add this feat folder afterward

Initially decided to track this cross-cutting, 6-domain change via a
GitHub issue (#180) rather than a dedicated `.specmgr/feat/` folder,
since the design was still being worked out interactively. Once the
design was settled (model change, no new validator needed, scope
confirmed across all 6 domains including `feat`'s `DecisionEntry`),
decided to also scaffold this feat folder to track the multi-phase
implementation plan and progress, per the project's standard convention
for multi-file, multi-domain work units.

### Related PRs / Commits

- [Issue #180](https://github.com/dfch/biz.dfch.SpecMgr/issues/180): tracking issue for this feature.
