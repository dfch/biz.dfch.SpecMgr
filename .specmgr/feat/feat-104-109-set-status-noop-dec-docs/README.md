---
classification: null
created: '2026-09-14 12:11:30.116+02:00'
id: feat-104-109-set-status-noop-dec-docs
status: done
type: feat
updated: '2026-09-14 21:14:01.842Z'
version: 1.0.0
---

# Feature: set_status No-Op On Unchanged Status (#109) + Document DEC Updates Timestamp Forms (#104)

## Plan

### Overview

Bundles two small, independently-scoped GitHub issues found during a backlog triage. They are functionally unrelated -- one is a generic cross-domain tool behavior change, the other is a documentation-only fix scoped to a single domain -- but each is small enough on its own that pairing them in one feature folder is more efficient than opening two separate ones (precedent: `feat-67-70-71`, `feat-73-74-76`, `feat-81-83-validation`, `feat-38-39-41-43-44`). GitHub issue #109 asks that `set_status` become a no-op (no write, no `updated` bump) when the caller passes a `status` identical to the document's current status. GitHub issue #104 asks that DEC's `## Updates` section documents, via its template/example, that its heading accepts both a bare `yyyy-MM-dd` date and a full `yyyy-MM-dd HH:mm:ss.fff(Z|±HH:mm)` timestamp -- today only the date-only form is shown anywhere a human or agent would look first.

> **Superseded timestamp-format decisions (feat-146-date-time, 2026-09-24):** ADR `8c889262-152b-4b8e-ae2c-75371f7a9edf` supersedes this feature's finding that DEC's `## Updates` heading
> "already accepts both forms" (date-only and full timestamp): the date-only form is now rejected everywhere, and all entry headings and frontmatter `created`/`updated` use the uniform
> full date+time contract (`T` written, `T`-or-space accepted). The full-timestamp examples this feature added to `dec_example.md`/`dec_template.md` remain valid.

### Requirements

- REQ-001: `set_status(id, type, status, superseded_by=None)` must return without writing to disk or bumping `updated` when `status` (or, for `type="adr"` with `superseded_by` given, the composed `f"superseded by {superseded_by}"` value) is identical to the document's current on-disk status, for every dispatched domain (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`, `dec`, `sop`, `feat`, `vcr`, `sysrs`, `adr`).

- REQ-002: The no-op path must still return the same type of value the changed-status path returns today (the domain's own `XFrontmatter` for the whole-body domains, the full `Adr` for `type="adr"`) so callers see no difference in return shape.

- REQ-003: The no-op path must not raise for an otherwise-valid call (it is a success, not an error), and the existing out-of-vocabulary `InvalidStatusResult` pre-check must still run exactly as it does today, before any adapter/no-op check is reached.

- REQ-004: `dec/data/dec_example.md` and/or `dec/data/dec_template.md` must show, in at least one `## Updates` entry, the full `yyyy-MM-dd HH:mm:ss.fff(Z|±HH:mm)` timestamp form alongside the existing bare-date form, so a human or agent copying the example sees both accepted shapes without needing to read `dec/models/v1/body.py` or `docs/dec_schema.json`.

- REQ-005: The documentation change must not alter DEC's parsing/validation behavior in any way (`_UPDATE_ENTRY_HEADING_PATTERN`/`@alias` untouched) -- this is example/template content only.

### Acceptance Criteria

- [x] ACC-001: A parametrized regression test (extending `tests/general/tools/test_set_status.py`'s existing `_CASES` table) calls `set_status` with each whole-body domain's own current status and asserts the file's bytes/mtime are unchanged, the returned frontmatter's `updated` field is unchanged, and the returned object equals the pre-call frontmatter.

- [x] ACC-002: A dedicated ADR test calls `set_status(type="adr", status=<current status>)`, and separately calls it with `superseded_by=<X>` where the document's current status is already `"superseded by X"`, and asserts no write occurs (file bytes unchanged) in both cases.

- [x] ACC-003: The existing "status changed, `updated` bumped" tests (`test_changes_status_bumps_updated_leaves_body_untouched`, `test_changes_plain_status_with_superseded_by_none`, `test_superseded_by_composes_status_string_in_file`) still pass unmodified, proving the no-op path is additive, not a regression to the changed-status path.

- [x] ACC-004: `parse_dec(dec_example())` (and/or `dec_template()`) still succeeds after the documentation edit, and the edited entry's heading uses the full-timestamp form verbatim, demonstrating REQ-004.

- [x] ACC-005: The existing `tests/dec/resources/test_dec_example.py`/`test_dec_template.py` tests pass unmodified (they assert entry *count* and structural facts, not exact heading text, so no test changes are expected -- if one does turn out to need updating, that is itself flagged as a Progress update).

### Scope

#### Included

- Code change: one early-return no-op check added to each of the 13 `_set_status_<d>` adapters in `general/tools/set_status.py` (12 whole-body domains + `adr`), computed against the domain's own already-loaded `existing`/`adr` value, inside the existing domain lock, before any write.

- Test change: new no-op regression tests added to `tests/general/tools/test_set_status.py`, reusing its existing `_Case`/`_CASES` table and `TempDocsDirTestCase` fixture.

- Doc-only change: `dec/data/dec_example.md` and/or `dec/data/dec_template.md` updated to show the full-timestamp `## Updates` heading form.

- Docstring/description updates on `set_status` (module docstring + `@mcp.tool()` description) reflecting the new no-op behavior.

#### Explicitly Out Of Scope

- GitHub issue #108 ("set_status tool calls shall honour a state machine") -- a materially larger design question about which status *transitions* are valid at all. #109 covers only the identity/no-change case and does not gate any other transition.

- Any change to `dec/models/v1/body.py`'s `_UPDATE_ENTRY_HEADING_PATTERN`/`UpdateEntry` parsing logic -- the accepted timestamp forms are already correct; only their visibility in template/example content changes.

- Extending the same full-timestamp-form documentation gap to `tsk`/`vcr`/`sysrs` (which share the same optional-time-of-day `## Updates`/`## Recent Updates` heading convention per their own REQ-004-derived docstrings) -- noted as a possible future follow-up but not requested by issue #104, which is DEC-only.

- Any change to how `set_status`'s existing out-of-vocabulary `InvalidStatusResult` pre-check works.

### Design Notes

Read-only investigation performed 2026-09-14 (no code changed yet, per explicit user instruction):

- **#109 mechanics**: each `_set_status_<d>` adapter already does `path, existing = load_<d>_by_id(base_dir, id_)` then `assert_within(...)` before touching `now_timestamp()`/the write. The no-op check slots in right after `assert_within`: `if existing.frontmatter.status == status: return existing.frontmatter`. For `_set_status_adr`, the comparison target must mirror `models.adr.v1.mutations.set_status`'s own composition rule: `target = status if superseded_by is None else f"superseded by {superseded_by}"`, then `if adr.frontmatter.status == target: return adr`.

- Because nothing is written on the no-op path, no cache invalidation/re-warm call is needed -- the existing cache entry (if any) already reflects the unchanged on-disk content.

- The pre-dispatch `_check_status_allowed` out-of-vocabulary check is unaffected and still runs before any adapter is called, exactly as today (REQ-003).

- **#104 mechanics**: `dec/models/v1/body.py`'s `_UPDATE_ENTRY_HEADING_PATTERN` already accepts both forms (confirmed via a live `validate` tool call against both a date-only and a full-timestamp `### ...` heading, both returning `{"valid": true}`), and the `UpdateEntry` docstring already documents both -- which is why the generated `docs/dec_schema.json` already shows this correctly. The only real gap is in `dec/data/dec_example.md`/`dec_template.md`, which currently show only the date-only form on both of `dec_example.md`'s two entries and the template's single entry.

- The safest edit keeps `dec_example.md`'s entry *count* at 2 (to avoid touching `test_packaged_example_parses_and_exercises_every_section`'s `len(updates.updates) == 2` assertion) by converting one existing entry's heading to the full-timestamp form rather than adding a third entry.

### Task List

#### Phase 1: set_status no-op (#109)

- [x] Task 1.1: Add the no-op early-return to each of the 13 `_set_status_<d>` adapters in `general/tools/set_status.py`.

- [x] Task 1.2: Update `set_status`'s module docstring and `@mcp.tool()` description to document the no-op behavior.

- [x] Task 1.3: Add/extend regression tests in `tests/general/tools/test_set_status.py` (ACC-001, ACC-002) and confirm ACC-003's existing tests still pass.

#### Phase 2: DEC Updates timestamp documentation (#104)

- [x] Task 2.1: Edit `dec/data/dec_example.md` to show the full-timestamp `## Updates` heading form on one existing entry.

- [x] Task 2.2: RESOLVED by the user: also update `dec/data/dec_template.md`'s single `## Updates` entry to the full-timestamp form (not example-only -- both files now show it).

- [x] Task 2.3: Confirm `tests/dec/resources/test_dec_example.py`/`test_dec_template.py` still pass unmodified (ACC-005); run the full test suite.

## Progress

### Current Status

**As of 2026-09-14**: Both phases complete -- Phase 1 (`set_status` no-op, #109) and Phase 2 (DEC Updates timestamp documentation, #104). Feature done.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-14 21:14:01.842Z - Phase 2 complete: DEC Updates timestamp documentation (#104)

Converted one existing `## Updates` entry's heading in each of `dec/data/dec_example.md`
(`### 2026-07-28 : Accepted` -> `### 2026-07-28 09:15:42.317Z : Accepted`) and
`dec/data/dec_template.md` (`### 2026-08-27 - Created` -> `### 2026-08-27 09:14:27.512Z - Created`)
to the full-timestamp `yyyy-MM-dd HH:mm:ss.fff(Z|±HH:mm)` form, demonstrating REQ-004 without
touching `dec/models/v1/body.py`'s `_UPDATE_ENTRY_HEADING_PATTERN`/`@alias` (REQ-005). Task 2.2
("decide whether `dec_template.md` also needs a full-timestamp example") was RESOLVED by the user
before implementation: update BOTH `dec_example.md` and `dec_template.md`, not `dec_example.md`
alone. Entry counts were kept unchanged in both files (2 in the example, 1 in the template) per
the plan's Design Notes, so `test_packaged_example_parses_and_exercises_every_section`'s
`len(updates.updates) == 2` assertion and every other structural assertion in
`tests/dec/resources/test_dec_example.py`/`test_dec_template.py` needed no changes at all
(ACC-005 held exactly as predicted). Verified `parse_dec(dec_example())`/`parse_dec(dec_template())`
still succeed and the edited headings' computed `.timestamp` round-trips verbatim (ACC-004). One
adjustment beyond the plan's literal wording: the first millisecond value chosen for the example
entry (`09:15:00.000Z`) tripped the pre-existing `tests/regression/test_issue_67.py` "no round
placeholder timestamp" regression test (feat-67-70-71 ACC-001, `_ROUND_MILLISECONDS_PATTERN`
`\.000[Z+-]`) -- replaced with a non-round value (`09:15:42.317Z`); the template's chosen value
(`09:14:27.512Z`) was already non-round and needed no change. Quality gate green: `ruff format
--check`, `ruff check`, `vulture`, `pytest tests/dec/` (228 passed), full `pytest` suite (3307
passed), `specmgr docs` (no diff beyond the two edited data files -- `docs/dec_schema.json` is
schema-derived, not example-derived, and was confirmed unchanged), `specmgr adr-toc` (no changes).

#### 2026-09-14 17:37:32.000Z - Phase 1 complete: set_status no-op (#109)

Added the no-op early-return (`if existing.frontmatter.status == status: return existing.frontmatter`) to each of the 12 whole-body `_set_status_<d>` adapters in `general/tools/set_status.py`, and the ADR-specific composed-target equivalent (`target_status = status if superseded_by is None else f"superseded by {superseded_by}"`) to `_set_status_adr` -- all 13 adapters covered, each check placed right after `assert_within` and before any write, inside the existing domain lock. Updated the module docstring, the `@mcp.tool()` `description=`, and the `set_status` function's own docstring body (behavior prose + Returns section) to document the no-op behavior. Extended `tests/general/tools/test_set_status.py` with `test_same_status_is_a_noop_leaves_file_and_updated_untouched` (iterates `_CASES`, ACC-001) and two dedicated ADR tests, `test_same_plain_status_is_a_noop_leaves_file_untouched` and `test_same_superseded_by_composition_is_a_noop_leaves_file_untouched` (ACC-002); confirmed the 3 existing "status changed" tests (`test_changes_status_bumps_updated_leaves_body_untouched`, `test_changes_plain_status_with_superseded_by_none`, `test_superseded_by_composes_status_string_in_file`) still pass unmodified (ACC-003). Quality gate green: `ruff format --check`, `ruff check`, `vulture`, `pytest tests/general/tools/test_set_status.py` (19 passed), full `pytest` suite (3307 passed), `specmgr docs` (regenerated `docs/api/biz.dfch.specmgr.general.tools.set_status.md` to reflect the docstring changes, nothing else), `specmgr adr-toc` (no changes). No design decisions needed beyond what the plan already specified -- the mechanics matched the Design Notes exactly.

#### 2026-09-14 09:14:27.512Z - Created

Feature folder created to bundle GitHub issues #109 (`set_status` no-op on unchanged status) and #104 (document DEC `## Updates` heading's full-timestamp form), following the existing multi-issue-bundle precedent (`feat-67-70-71`, `feat-81-83-validation`). Scope, requirements, and acceptance criteria drafted from a read-only investigation of `general/tools/set_status.py`, `tests/general/tools/test_set_status.py`, and `dec/models/v1/body.py`/`dec/data/dec_example.md`/`dec_template.md`. Implementation deliberately deferred per explicit user instruction.

### Related PRs / Commits

- [Issue #109](https://github.com/dfch/biz.dfch.SpecMgr/issues/109): set_status shall return without updating anything when target status equals source status.

- [Issue #104](https://github.com/dfch/biz.dfch.SpecMgr/issues/104): DEC Updates heading accepts yyyy-MM-dd as well as a full timestamp (undocumented).
