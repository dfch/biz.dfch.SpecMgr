---
classification: null
created: '2026-09-23 22:33:23.868+02:00'
id: feat-146-date-time
status: planning
type: feat
updated: '2026-09-23 23:22:17.685+02:00'
version: 1.0.0
---

# Feature: Uniform Full ISO 8601 Date+Time Timestamps (T-Canonical Frontmatter, Both Separators Accepted)

## Plan

### Overview

GitHub issue #146 exposed that `feat`'s `### Updates`/`### Decisions Made` entry headings require a full
ISO 8601 date+time timestamp while `tsk`/`dec`/`vcr`/`sysrs` accept a bare `yyyy-MM-dd` date -- a
cross-domain inconsistency deliberately introduced by feat-38-39-41-43-44 (REQ-004). This feature
establishes one uniform, full date+time timestamp format for every timestamp location in every
whole-body artifact type (ADR excluded): the `## Recent Updates`/`## Updates`/`### Updates`/
`### Decisions Made` entry headings of the six domains that have them, and the frontmatter
`created`/`updated` fields of all twelve whole-body domains. The accepted format is `yyyy-MM-dd` +
(`T` or space) + `HH:mm:ss` + `.` + exactly 3-digit milliseconds + (`Z` or `±HH:MM`); date-only is
rejected everywhere. The MCP write side (frontmatter only, which the MCP always owns) emits the
`T`-separated canonical form; examples, templates, and migrated documents keep the space-separated
form in entry-heading section titles for readability.

### Requirements

- REQ-001: Entry headings in `tsk.RecentUpdates`, `dec.Updates`, `vcr.Updates`, `sysrs.Updates` accept only the full date+time form (`yyyy-MM-dd[T ]HH:mm:ss.fff` + `Z`/`±HH:MM`); date-only is rejected with an actionable error.
- REQ-002: Entry headings in `feat.Updates`, `feat.DecisionsMade`, and `sop.Updates` additionally accept the `T` separator (space and `T` both valid).
- REQ-003: Frontmatter `created`/`updated` accept both `T` and space separators in all twelve whole-body domains (shared `MarkdownFrontmatter._DATE_TIME_PATTERN`); date-only, 6-digit fractions, and timezone-less values remain rejected.
- REQ-004: The MCP write side emits `T`-separated frontmatter values: `general/tools/_timestamps.py::format_timestamp` (and `now_timestamp`) switch to the `T` form; all create/update/set_status sites inherit the change with no per-site edits.
- REQ-005: `models/md/_ordering.py::validate_newest_first` drops its now-dead mixed date-only/date+time day-granularity branch (plain aware `datetime.fromisoformat` comparison); `format_date` is removed (zero callers after REQ-001).
- REQ-006: `_stringify_metadata` (shared parse path + per-domain copies) normalizes PyYAML-coerced `datetime` objects to the `T`-canonical form with 3-digit milliseconds instead of bare `str()` (which drops milliseconds and yields a rejected shape).
- REQ-007: Packaged data migrated to the conventions: the 24 template/example frontmatters use the `T` form; the 8 date-only entry headings (dec/vcr/sysrs/tsk templates + examples) become space-form midnight UTC (`yyyy-MM-dd 00:00:00.000Z`); the 8 tsk/dec/vcr/sysrs create/update instruction files describe full form only with space-form examples.
- REQ-008: The repo's own documents parse after the change: the 3 date-only entry headings in `docs/tsk` (x2) and `docs/sysrs` (x1) are migrated to space-form midnight UTC; no frontmatter mass-migration in `docs/` (space remains valid and converges on write).
- REQ-009: A new ADR documents the uniform format, the `T` write convention, the space-in-section-titles convention, and the supersession of feat-38-39-41-43-44 D4/D5/D7/D11/REQ-004/ACC-004/ACC-005 and feat-32-sysrs' locked lenient shape; brief supersession notes are added to the affected previous feature READMEs.
- REQ-010: All twelve `*_schema.json` files are regenerated (`specmgr schema`), `docs/api`/`docs/GENERATED.md`/`docs/adr/README.md` are regenerated, `CHANGELOG.md` gains an `[Unreleased]` BREAKING entry, and GitHub issue #146 is commented with the fix + ADR reference.

### Acceptance Criteria

- [ ] ACC-001: A date-only entry heading fails to parse in `tsk`/`dec`/`vcr`/`sysrs` with an actionable `AssertionError` (field path + line + expected format), and a full timestamp with either `T` or space parses in all six entry-heading domains.
- [ ] ACC-002: Frontmatter `created`/`updated` values with either separator parse in all twelve domains (quoted, and unquoted via the REQ-006 normalization); date-only values remain rejected.
- [ ] ACC-003: Every `create_<d>`/`update`/`set_status` write emits `T`-separated `created`/`updated` values, verified by write + byte-exact read-back round-trip.
- [ ] ACC-004: Newest-first ordering compares full timestamps as aware datetimes (no day-granularity rule; same-day `T` vs space pairs order by the time component), equal timestamps allowed, out-of-order pairs rejected in all six domains.
- [ ] ACC-005: Every packaged template/example/instruction file parses through its own domain's tool and shows the conventions (frontmatter `T`, entry-heading examples space).
- [ ] ACC-006: Every document under `docs/` parses through its own domain's tools; the 3 migrated headings carry space-form midnight UTC values.
- [ ] ACC-007: The `specmgr schema`/`specmgr docs`/`specmgr adr-toc` drift checks are green; the ADR appears in `docs/adr/README.md` and is `accepted`; the CHANGELOG entry and the issue #146 comment exist.
- [ ] ACC-008: The full quality gate (ruff format/check, vulture, `pytest -n auto --cov`, pylint baseline unchanged) is green after every phase.

### Scope

#### Included

- The six `body.py` entry-heading regex pairs (`feat` x2 sections, `sop`, `tsk`, `dec`, `vcr`, `sysrs`).
- `models/md/_ordering.py` (mixed-granularity branch removal), `models/md/frontmatter.py` (D5 pattern), `general/tools/_timestamps.py` (write form, `format_date` removal).
- `_stringify_metadata` normalization across the shared parse path and per-domain copies.
- All 24 packaged template/example frontmatters, the 8 packaged date-only entry headings, the 8 tsk/dec/vcr/sysrs instruction files, and `tests/feat/models/v1/data/feat_reference.md`.
- The 3 `docs/` entry-heading migrations and the repo-wide docs parse gate.
- Test updates: the ~44 files pinning space-form frontmatter, the 4 files with date-only entry fixtures, `tests/models/md/test__ordering.py`, `tests/general/tools/test__timestamps.py`, `tests/models/md/test_frontmatter.py`, and `tests/regression/test_issue_67.py`'s now-moot date-only exclusion.
- The new ADR, the brief previous-feature supersession notes, CHANGELOG, AGENTS.md touch-up, and doc regeneration.

#### Explicitly Out Of Scope

- The ADR domain (own frontmatter, free-form `date`, no `created`/`updated`, no `now_timestamp` usage).
- UC v1 (legacy, `date`-typed frontmatter, referenced by no tool; UC v2 is covered via the shared base).
- Frontmatter mass-migration of existing `docs/` files (space remains accepted; values converge on write).
- The ~28 pre-existing `.specmgr/feat/*/README.md` parse failures (tracked separately by `docs/tsk/tsk-2687d267`).
- Any new MCP tools, resources, or prompts.

### Design Notes

The accepted timestamp regex fragment is shared verbatim across the six entry-heading sites and the D5 frontmatter pattern: `\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})`.

Write/read split: frontmatter is system-owned (the MCP is its only writer) and therefore always written `T`-separated; entry headings are hand/agent-authored body content where both separators are accepted and examples/templates use space for readability. This matches ADR 23a14195's ISO 8601 combined form (`T`) while keeping the human-facing convention unchanged.

PyYAML hazard (verified): unquoted values in either separator coerce to `datetime` and bare `str()` drops milliseconds (and renders `+00:00`), which is why D5 rejects the coerced shape today; REQ-006's normalization makes unquoted values parse and converge to the `T` canonical form. The write path is already safe: `frontmatter.dumps` auto single-quotes timestamp-like strings (verified byte-exact round-trip).

Schema evolution is in-place on `models/v1` (no v2) per the prb/feat-132 breaking-evolution precedent; the ADR records the explicit supersession of the lenient decisions.

No external dependencies; this feature is self-contained.

### Related Decisions

- ADR 8c889262-152b-4b8e-ae2c-75371f7a9edf ("Use full ISO 8601 date+time timestamps in all entry headings and frontmatter (accept T or space, write T)"): created by this feature, Phase 0.
- ADR 23a14195-339c-48af-99d2-97c9964041ae ("Use ISO 8601 for all dates and times"): aligned, not superseded -- the `T` combined form becomes canonical for machine-written values.
- feat-38-39-41-43-44 (D4/D5/D7/D11, REQ-004/REQ-006): superseded in part -- see the ADR.
- feat-32-sysrs (locked lenient `## Updates` shape): superseded in part -- see the ADR.

### Task List

#### Phase 0: ADR + feature folder

- [x] Task 0.1: Create the ADR via `create_adr` (status `draft`), capturing context/drivers/options/decision/consequences per this plan.
- [x] Task 0.2: Create this feature folder via `create_feat` (id `feat-146-date-time`) with the plan above, citing the ADR id.
- [x] Task 0.3: Run `specmgr adr-toc`; full quality gate.

#### Phase 1: Frontmatter/write core + frontmatter sweep

- [ ] Task 1.1: `general/tools/_timestamps.py`: `format_timestamp` space→`T`; remove `format_date` (+ `__all__`); docstring updates.
- [ ] Task 1.2: `models/md/frontmatter.py`: `_DATE_TIME_PATTERN` → `[T ]`; comment block + field docstrings.
- [ ] Task 1.3: `_stringify_metadata`: `datetime` → `T`-canonical with milliseconds (shared path + per-domain copies).
- [ ] Task 1.4: Sweep: 24 packaged frontmatters → `T`; `feat_reference.md` → `T`; ~44 test files (writer-output assertions + fixtures → `T`, keep explicit space-acceptance tests); `test__timestamps.py` (12 tests); `test_frontmatter.py` matrix.
- [ ] Task 1.5: `specmgr schema` (all twelve) + `specmgr docs`; full quality gate.

#### Phase 2: Entry headings (six domains)

- [ ] Task 2.1: Widen `feat` (body.py:435/442) + `sop` (body.py:372/377) to `[T ]`.
- [ ] Task 2.2: Tighten `tsk` (body.py:69/74), `dec` (body.py:424/429), `vcr` (body.py:320/326), `sysrs` (body.py:996/1002): mandatory time + `[T ]`.
- [ ] Task 2.3: `models/md/_ordering.py`: delete `_DATE_ONLY_LENGTH` + mixed-granularity branch; docstrings.
- [ ] Task 2.4: Body docstrings: drop leniency wording ("REQ-004", "locked post-sibling shape", feat body.py:449-454 "deliberately not the same format as frontmatter"); cite the ADR.
- [ ] Task 2.5: Packaged data: 8 date-only headings → space midnight UTC (`dec_example:136`, `sysrs_example:535/541`, `sysrs_template:236`, `tsk_example:25/29`, `tsk_template:22`, `vcr_template:54`); rewrite 8 tsk/dec/vcr/sysrs instruction files (full form only, space examples); check feat/sop/other instruction wording.
- [ ] Task 2.6: Tests: flip date-only accept→reject (4 files); `test__ordering.py` drop date-only/mixed cases; add `T`-accept per domain; review `test_issue_67.py` exclusion + comment.
- [ ] Task 2.7: `specmgr schema` + full quality gate.

#### Phase 3: Repo documents migration

- [ ] Task 3.1: Migrate 3 `docs/` entry headings → space midnight UTC (`docs/tsk` x2, `docs/sysrs` x1).
- [ ] Task 3.2: Parse gate: every `docs/` document through its own domain tools; full quality gate.

#### Phase 4: Previous-feature notes + closeout

- [ ] Task 4.1: Brief supersession notes (one blockquote each, citing the ADR id) in: feat-38-39-41-43-44, feat-32-sysrs, feat-67-70-71, feat-104-109-set-status-noop-dec-docs, feat-94-frontmatter-schema; verify-by-grep candidates (feat-31-feature, feat-33-vcr, feat-10-add-artifact-type-tasklist, feat-21-decision, feat-5-md-model-parser, feat-93-feat-template) get notes only if they carry format decisions.
- [ ] Task 4.2: `CHANGELOG.md` `[Unreleased]` BREAKING entry; AGENTS.md touch-up (now_timestamp shared format → `T` write, both accepted).
- [ ] Task 4.3: Final doc regeneration (`specmgr docs`, `specmgr mcp-docs`, `specmgr adr-toc`); ADR `set_status` → `accepted`; GitHub comment on issue #146.
- [ ] Task 4.4: Full quality gate.

## Progress

### Current Status

**As of 2026-09-23**: Phase 0 complete: ADR 8c889262-152b-4b8e-ae2c-75371f7a9edf created (draft), this
feature folder created, `docs/adr/README.md` regenerated via `specmgr adr-toc`, and the phase-end
full quality gate green (ruff format/check, vulture, `pytest -n auto --cov` -- 3402 passed). All
format decisions are confirmed with the requester (uniform full date+time across all twelve
whole-body domains, ADR excluded, UC via v2; both `T` and space accepted; MCP writes frontmatter
in `T`; examples/templates keep space in section titles; full quality gate after each phase; brief
supersession notes for affected previous features; issue #146's error-message claim verified
non-reproducible server-side, so no prose rewording is in scope -- the raw `@alias` regex in the
error is the intentional machine-readable contract). Phases 1-4 (implementation) are deliberately
not started yet.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-23 20:40:25.711Z - Phase 0 complete: adr-toc regenerated, full quality gate green

Created the ADR (8c889262-152b-4b8e-ae2c-75371f7a9edf, `draft`), created this feature folder,
regenerated `docs/adr/README.md` via `specmgr adr-toc`, and ran the phase-end full quality gate
green (ruff format/check, vulture, `pytest -n auto --cov` -- 3402 passed). Implementation
(Phases 1-4) is deliberately not started yet.

#### 2026-09-23 20:31:28.001Z - Created

Feature created for GitHub issue #146 (`create_feat` fails on date-only `Updates`/`Decisions Made`
timestamps, inconsistent with `create_tsk`); plan finalized after the format decisions were
confirmed with the requester, and the ADR (8c889262-152b-4b8e-ae2c-75371f7a9edf) was created as
`draft` ahead of this folder.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-23 20:31:28.001Z - No error-message prose requirement: the raw regex in the error is the contract

GitHub issue #146's second suggested fix (surface a friendlier validation error) is not a
requirement of this feature: it was verified non-reproducible server-side (the MCP SDK 2.0.0
propagates the full enriched message -- field path, line, raw `@alias` regex, offending text --
and the reporter's bare error was client-side display truncation). Most consumers of these
messages are agents, for whom the raw regex is the machine-readable format contract; the requester
confirmed the current message shape is acceptable as-is. The ADR records this verification.

#### 2026-09-23 20:31:28.001Z - Full quality gate after each phase; brief previous-feature notes

Every phase ends with the full gate (ruff format/check, vulture, `pytest -n auto --cov`, pylint
baseline unchanged) and phases are self-contained so the suite is green at each phase end.
Affected previous feature READMEs get one brief blockquote note each stating their timestamp
decisions are superseded, without doc repair (pre-existing parse failures stay out of scope,
tracked by `docs/tsk/tsk-2687d267`).

#### 2026-09-23 20:31:28.001Z - Separator: accept `T` or space; frontmatter written `T`; section titles keep space

Both `T` and space are accepted in entry headings and frontmatter. Frontmatter is MCP-owned and
therefore always written `T`-separated (`now_timestamp` changes). Examples, templates, and
migrated documents keep the space-separated form in entry-heading section titles for readability.
This amends feat-38-39-41-43-44 D4 (space canonical write form) and D5/ACC-005 (T rejection) --
recorded in the ADR.

#### 2026-09-23 20:31:28.001Z - Scope: all twelve whole-body domains, ADR excluded, UC via v2

Every artifact type uses the uniform full date+time format except the (deprecated) ADR domain;
UC is covered through its v2 schema, which inherits the shared `MarkdownFrontmatter` (v1 is
legacy, referenced by no tool). `feat` was already strict and `sop` stays strict; `tsk`/`dec`/
`vcr`/`sysrs` tighten, and all six entry-heading domains widen to accept `T`.

### More Information

- GitHub issue: https://github.com/dfch/biz.dfch.SpecMgr/issues/146
- Decision: ADR 8c889262-152b-4b8e-ae2c-75371f7a9edf (created with this feature, Phase 0).
- Superseded prior decisions: feat-38-39-41-43-44 (REQ-004/REQ-006, D4/D5/D7/D11), feat-32-sysrs
  (locked lenient `## Updates` shape), feat-67-70-71 ("deliberately supported alternate
  granularity" declaration), feat-104-109-set-status-noop-dec-docs ("already accepts both forms"
  finding), feat-94-frontmatter-schema (space-form pattern pinned into the JSON schemas).
