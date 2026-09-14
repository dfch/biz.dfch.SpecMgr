---
classification: null
created: '2026-09-14 12:11:30.116+02:00'
id: feat-104-109-set-status-noop-dec-docs
status: planning
type: feat
updated: '2026-09-14 12:11:30.116+02:00'
version: 1.0.0
---

# Feature: set_status No-Op On Unchanged Status (#109) + Document DEC Updates Timestamp Forms (#104)

## Plan

### Overview

Bundles two small, independently-scoped GitHub issues found during a backlog triage. They are functionally unrelated -- one is a generic cross-domain tool behavior change, the other is a documentation-only fix scoped to a single domain -- but each is small enough on its own that pairing them in one feature folder is more efficient than opening two separate ones (precedent: `feat-67-70-71`, `feat-73-74-76`, `feat-81-83-validation`, `feat-38-39-41-43-44`). GitHub issue #109 asks that `set_status` become a no-op (no write, no `updated` bump) when the caller passes a `status` identical to the document's current status. GitHub issue #104 asks that DEC's `## Updates` section documents, via its template/example, that its heading accepts both a bare `yyyy-MM-dd` date and a full `yyyy-MM-dd HH:mm:ss.fff(Z|±HH:mm)` timestamp -- today only the date-only form is shown anywhere a human or agent would look first.

### Requirements

- REQ-001: `set_status(id, type, status, superseded_by=None)` must return without writing to disk or bumping `updated` when `status` (or, for `type="adr"` with `superseded_by` given, the composed `f"superseded by {superseded_by}"` value) is identical to the document's current on-disk status, for every dispatched domain (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`, `dec`, `sop`, `feat`, `vcr`, `sysrs`, `adr`).

- REQ-002: The no-op path must still return the same type of value the changed-status path returns today (the domain's own `XFrontmatter` for the whole-body domains, the full `Adr` for `type="adr"`) so callers see no difference in return shape.

- REQ-003: The no-op path must not raise for an otherwise-valid call (it is a success, not an error), and the existing out-of-vocabulary `InvalidStatusResult` pre-check must still run exactly as it does today, before any adapter/no-op check is reached.

- REQ-004: `dec/data/dec_example.md` and/or `dec/data/dec_template.md` must show, in at least one `## Updates` entry, the full `yyyy-MM-dd HH:mm:ss.fff(Z|±HH:mm)` timestamp form alongside the existing bare-date form, so a human or agent copying the example sees both accepted shapes without needing to read `dec/models/v1/body.py` or `docs/dec_schema.json`.

- REQ-005: The documentation change must not alter DEC's parsing/validation behavior in any way (`_UPDATE_ENTRY_HEADING_PATTERN`/`@alias` untouched) -- this is example/template content only.

### Acceptance Criteria

- [ ] ACC-001: A parametrized regression test (extending `tests/general/tools/test_set_status.py`'s existing `_CASES` table) calls `set_status` with each whole-body domain's own current status and asserts the file's bytes/mtime are unchanged, the returned frontmatter's `updated` field is unchanged, and the returned object equals the pre-call frontmatter.

- [ ] ACC-002: A dedicated ADR test calls `set_status(type="adr", status=<current status>)`, and separately calls it with `superseded_by=<X>` where the document's current status is already `"superseded by X"`, and asserts no write occurs (file bytes unchanged) in both cases.

- [ ] ACC-003: The existing "status changed, `updated` bumped" tests (`test_changes_status_bumps_updated_leaves_body_untouched`, `test_changes_plain_status_with_superseded_by_none`, `test_superseded_by_composes_status_string_in_file`) still pass unmodified, proving the no-op path is additive, not a regression to the changed-status path.

- [ ] ACC-004: `parse_dec(dec_example())` (and/or `dec_template()`) still succeeds after the documentation edit, and the edited entry's heading uses the full-timestamp form verbatim, demonstrating REQ-004.

- [ ] ACC-005: The existing `tests/dec/resources/test_dec_example.py`/`test_dec_template.py` tests pass unmodified (they assert entry *count* and structural facts, not exact heading text, so no test changes are expected -- if one does turn out to need updating, that is itself flagged as a Progress update).

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

- [ ] Task 1.1: Add the no-op early-return to each of the 13 `_set_status_<d>` adapters in `general/tools/set_status.py`.

- [ ] Task 1.2: Update `set_status`'s module docstring and `@mcp.tool()` description to document the no-op behavior.

- [ ] Task 1.3: Add/extend regression tests in `tests/general/tools/test_set_status.py` (ACC-001, ACC-002) and confirm ACC-003's existing tests still pass.

#### Phase 2: DEC Updates timestamp documentation (#104)

- [ ] Task 2.1: Edit `dec/data/dec_example.md` to show the full-timestamp `## Updates` heading form on one existing entry.

- [ ] Task 2.2: Decide (don't assume) whether `dec/data/dec_template.md` also needs a full-timestamp example, or whether `dec_example.md` alone satisfies REQ-004.

- [ ] Task 2.3: Confirm `tests/dec/resources/test_dec_example.py`/`test_dec_template.py` still pass unmodified (ACC-005); run the full test suite.

## Progress

### Current Status

**As of 2026-09-14**: Feature folder created, planning only. No implementation has started -- both phases are pending. This entry was written before any code change, per the user's explicit "do not implement" instruction.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-14 09:14:27.512Z - Created

Feature folder created to bundle GitHub issues #109 (`set_status` no-op on unchanged status) and #104 (document DEC `## Updates` heading's full-timestamp form), following the existing multi-issue-bundle precedent (`feat-67-70-71`, `feat-81-83-validation`). Scope, requirements, and acceptance criteria drafted from a read-only investigation of `general/tools/set_status.py`, `tests/general/tools/test_set_status.py`, and `dec/models/v1/body.py`/`dec/data/dec_example.md`/`dec_template.md`. Implementation deliberately deferred per explicit user instruction.

### Related PRs / Commits

- [Issue #109](https://github.com/dfch/biz.dfch.SpecMgr/issues/109): set_status shall return without updating anything when target status equals source status.

- [Issue #104](https://github.com/dfch/biz.dfch.SpecMgr/issues/104): DEC Updates heading accepts yyyy-MM-dd as well as a full timestamp (undocumented).
