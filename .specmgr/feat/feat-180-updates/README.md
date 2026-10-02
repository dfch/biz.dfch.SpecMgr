---
classification: null
created: '2026-10-02T13:15:57.269+02:00'
id: feat-180-updates
status: planning
type: feat
updated: '2026-10-02T14:56:28.119+02:00'
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

- [ ] ACC-001: An `UpdateEntry`/`DecisionEntry` containing only a plain paragraph still parses and round-trips identically to today, in all 6 domains (no regression).
- [ ] ACC-002: An `UpdateEntry`/`DecisionEntry` containing multiple blank-line-separated paragraphs parses and round-trips successfully, in all 6 domains.
- [ ] ACC-003: An `UpdateEntry`/`DecisionEntry` containing a bullet/numbered list parses and round-trips successfully, in all 6 domains.
- [ ] ACC-004: An `UpdateEntry`/`DecisionEntry` containing a fenced code block parses and round-trips successfully, in all 6 domains.
- [ ] ACC-005: An `UpdateEntry`/`DecisionEntry` with blank/whitespace-only content under its heading still fails to parse with an `AssertionError` (non-blank requirement preserved), in all 6 domains.
- [ ] ACC-006: `model_dump()` on a parsed document surfaces the new leaf field's real text content for a non-paragraph body, not an empty object.
- [ ] ACC-007: The full test suite passes after every phase below, not just at the end.
- [ ] ACC-008: Each of the 4 phases ends with a passing full quality gate (`ruff format --check`, `ruff check`, `vulture`, full test suite) before that phase's own commit -- not just a single check against the final state.
- [ ] ACC-009: Every affected domain's packaged `schema.json` (both copies) and `docs/api/` are regenerated and committed in sync with the model change (no drift).
- [ ] ACC-010: `CHANGELOG.md` carries an entry describing the relaxation under `[Unreleased]`.

### Scope

#### Included

- New `UpdateEntryContent` (and `feat`'s `DecisionEntryContent`) leaf classes, and the `content` field retype, in `vcr`/`feat`/`dec`/`sop`/`sysrs`/`tsk`'s `models/v1/body.py`.
- Test additions in each domain's `tests/<domain>/models/v1/test_body.py`, plus a check (and update only if needed) of each domain's `tests/<domain>/models/v1/test_parser.py` for paragraph-specific fixtures/assertions. `tsk`'s `test_create_tsk.py` requires no change (its only `## Recent Updates` fixture is a single paragraph, verified) and is explicitly excluded.
- Regenerated `docs/*_schema.json` and each domain's packaged `<domain>/data/<domain>_schema.json`, plus `docs/GENERATED.md`/`docs/api/`.
- A `CHANGELOG.md` entry under `[Unreleased]`.
- A separate commit after each of the 4 phases' own passing quality gate, rather than one final commit for the whole feature.

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

- [ ] Task 100.100: In `vcr/models/v1/body.py`, add `UpdateEntryContent(MarkdownStr)` with a `text` computed property; retype `UpdateEntry.content`. Do NOT drop the `MarkdownParagraph` import -- it stays in use by `CrossReference.value`/`.notes`, `Coverage.value`, and `AcceptanceCriterion.description` in this same file.
- [ ] Task 100.110: In `feat/models/v1/body.py`, add `UpdateEntryContent(MarkdownStr)`; retype `UpdateEntry.content`.
- [ ] Task 100.120: In `feat/models/v1/body.py`, add `DecisionEntryContent(MarkdownStr)`; retype `DecisionEntry.content`; drop the now-unused `MarkdownParagraph` import if nothing else in the module uses it.
- [ ] Task 100.130: In `dec/models/v1/body.py`, add `UpdateEntryContent(MarkdownStr)`; retype `UpdateEntry.content`. Do NOT drop the `MarkdownParagraph` import -- it stays in use by `DecisionOutcome.statement` in this same file.
- [ ] Task 100.140: In `sop/models/v1/body.py`, add `UpdateEntryContent(MarkdownStr)`; retype `UpdateEntry.content`; drop the now-unused `MarkdownParagraph` import if nothing else in the module uses it.
- [ ] Task 100.150: In `sysrs/models/v1/body.py`, add `UpdateEntryContent(MarkdownStr)`; retype `UpdateEntry.content`; drop the now-unused `MarkdownParagraph` import if nothing else in the module uses it.
- [ ] Task 100.160: In `tsk/models/v1/body.py`, add `UpdateEntryContent(MarkdownStr)`; retype `UpdateEntry.content`; drop the now-unused `MarkdownParagraph` import if nothing else in the module uses it.
- [ ] Task 100.170: Phase-end quality gate: `uv run --frozen ruff format --check && uv run --frozen ruff check`; `uv run --frozen vulture src/ whitelist.py --min-confidence 60`; run the full test suite. All must pass before moving to Phase 110.
- [ ] Task 100.180: Commit Phase 100's changes (the 6 domains' `body.py` model retypes) before starting Phase 110.

#### Phase 110: New test coverage

- [ ] Task 110.100: In `tests/vcr/models/v1/test_body.py`, add multi-paragraph/list/code-block positive tests for `UpdateEntry.content` (existing negative tests use bare `assertRaises`, not message-specific assertions, so they need no fix -- confirm they still pass unmodified).
- [ ] Task 110.110: In `tests/feat/models/v1/test_body.py`, do the same for both `UpdateEntry` and `DecisionEntry`.
- [ ] Task 110.120: In `tests/dec/models/v1/test_body.py`, do the same.
- [ ] Task 110.130: In `tests/sop/models/v1/test_body.py`, do the same; also check `tests/sop/models/v1/test_parser.py` for any paragraph-specific fixtures/assertions and update only if needed.
- [ ] Task 110.140: In `tests/sysrs/models/v1/test_body.py`, do the same; also check `tests/sysrs/models/v1/test_parser.py` for any paragraph-specific fixtures/assertions and update only if needed.
- [ ] Task 110.150: In `tests/tsk/models/v1/test_body.py`, do the same; also check `tests/tsk/models/v1/test_parser.py` for any paragraph-specific fixtures/assertions and update only if needed. `tests/tsk/tools/test_create_tsk.py` needs no edit (its only `## Recent Updates` fixture is a single paragraph) -- confirm it still passes unmodified rather than editing it.
- [ ] Task 110.155: For parity with Tasks 110.130/110.140/110.150's `test_parser.py` check, also check `tests/vcr/models/v1/test_parser.py`, `tests/feat/models/v1/test_parser.py`, and `tests/dec/models/v1/test_parser.py` for any paragraph-specific fixtures/assertions and update only if needed.
- [ ] Task 110.160: Add/confirm `model_dump()` assertions covering the non-paragraph content case (ACC-006).
- [ ] Task 110.170: Phase-end quality gate: `uv run --frozen ruff format --check && uv run --frozen ruff check`; `uv run --frozen vulture src/ whitelist.py --min-confidence 60`; run the full test suite. All must pass before moving to Phase 120.
- [ ] Task 110.180: Commit Phase 110's changes (the new/updated tests) before starting Phase 120.

#### Phase 120: Regenerate build artifacts

- [ ] Task 120.100: Run `specmgr schema` for each of the 6 domains -- two separate invocations per domain (`--output-dir docs/` and `--output-dir src/biz/dfch/specmgr/<domain>/data`), 12 invocations total, unless relying on the corresponding `specmgr-schema`/`specmgr-schema-<domain>-package` pre-commit hooks to regenerate both automatically on commit.
- [ ] Task 120.110: Run `specmgr docs` to regenerate `docs/GENERATED.md`/`docs/api/` for the changed docstrings.
- [ ] Task 120.120: Phase-end quality gate: `uv run --frozen ruff format --check && uv run --frozen ruff check`; `uv run --frozen vulture src/ whitelist.py --min-confidence 60`; run the full test suite. All must pass before moving to Phase 130.
- [ ] Task 120.130: Commit Phase 120's changes (the regenerated schema/docs artifacts) before starting Phase 130.

#### Phase 130: CHANGELOG and final verification

- [ ] Task 130.100: Add a `CHANGELOG.md` entry under `[Unreleased]` -> `### Changed` (backward-compatible field-type relaxation, not a new feature) describing the relaxation across the 6 domains.
- [ ] Task 130.110: `uv run --frozen ruff format --check && uv run --frozen ruff check`.
- [ ] Task 130.120: `uv run --frozen vulture src/ whitelist.py --min-confidence 60`.
- [ ] Task 130.130: Run the full test suite one final time.
- [ ] Task 130.140: Review `git status`/`git diff` for completeness, then commit.

## Progress

### Current Status

**As of 2026-10-02**: Planning complete; GitHub issue #180 opened
capturing the design (per-domain `UpdateEntryContent`/`DecisionEntryContent`
leaf classes mirroring `feat-114`'s `IntroductionBody` idiom; no new
validator code needed since the engine's existing mandatory-field
zero-extent check already enforces non-blank content). Implementation not
yet started -- Phase 100 (Model change) is next.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-02T16:30:00.000Z - Clarified why the manual phase-end gate isn't redundant with pre-commit hooks

Added a Design Notes paragraph explaining that each phase's manual
quality-gate task (ruff format/check, ruff check, vulture, full test
suite) is not duplicate busywork even though this repo's installed
pre-commit hooks already re-enforce the identical checks -- plus
schema/docs drift -- automatically on every `git commit` touching
`src/**/*.py`/`tests/**/*.py`: the manual run is purely for fast local
feedback, catching a failure before attempting the commit rather than
discovering it mid-commit and having to fix-then-retry.

#### 2026-10-02T15:00:00.000Z - Plan refined after codebase-verification review

Reviewed the plan against the actual codebase (per-domain `body.py` files,
the `feat-114` `IntroductionBody` precedent, `models/md/markdown_str.py`
internals, existing tests, schema files, and `CHANGELOG.md`) and corrected
several issues: (1) Phase 110's premise that existing tests need
`MarkdownParagraph`-specific error-message fixes was false -- no such
assertions exist in any of the 6 domains; reworded all Phase 110 tasks to
be purely additive and added an explanatory paragraph to Design Notes;
(2) Tasks 100.100 (`vcr`) and 100.130 (`dec`) incorrectly implied
`MarkdownParagraph` might be dropped -- it stays in use elsewhere in both
files (`CrossReference`/`Coverage`/`AcceptanceCriterion` in `vcr`,
`DecisionOutcome.statement` in `dec`), now stated explicitly; (3) resolved
an inconsistency where only `tsk`'s `test_create_tsk.py` was singled out
for an edit it doesn't need, and only `sop`/`tsk` called out `test_parser.py`
checks -- added Task 110.155 for `vcr`/`feat`/`dec` parity and clarified
`test_create_tsk.py` needs no change; (4) Task 120.100 now spells out the
two separate `specmgr schema` invocations per domain; (5) Task 130.100 now
specifies the `### Changed` CHANGELOG subsection; (6) Design Notes now
notes that this extends the `feat-114` `IntroductionBody` idiom into new
(mandatory-field) territory rather than being a pure mirror, and that
`.text` is also required for existing call-site compatibility, not just
`model_dump()`.

#### 2026-10-02T14:15:00.000Z - Created

Feature folder created from GitHub issue #180, following a plan-mode
design discussion that: (1) confirmed scope as all 6 domains (`vcr`,
`feat`, `dec`, `sop`, `sysrs`, `tsk`) including `feat`'s `DecisionEntry`;
(2) confirmed a new per-domain `UpdateEntryContent`/`DecisionEntryContent`
leaf class (mirroring `feat-114`'s `IntroductionBody(MarkdownStr)` idiom)
replaces `MarkdownParagraph` as the field type; (3) confirmed `content`
stays mandatory and non-blank is enforced for free by the engine's
existing mandatory-field zero-extent check, with no new validator code
required; (4) confirmed example/template markdown files are left
unchanged, since the relaxation is a strict superset and existing
single-paragraph examples remain valid.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

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
