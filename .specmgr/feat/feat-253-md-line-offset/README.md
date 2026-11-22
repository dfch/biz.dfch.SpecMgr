---
classification: null
created: '2026-11-22T15:33:48.257+01:00'
id: feat-253-md-line-offset
status: planning
type: feat
updated: '2026-11-22T15:33:48.257+01:00'
version: 1.0.0
---

# Feature: models/md Scalar-Field Line-Offset Deficit in Actionable Error Messages (Issue #253)

## Plan

### Overview

The actionable error messages of the shared `models/md` engine (feat-27-validation) carry a 1-based line reference into the mdformat-normalized body. For a multi-field `MarkdownSection*` with several scalar (`process_field`) fields, that line reference is too low: it is short by one line for each separator blank line between the fields that were consumed before the offending block. The field path and the cause/fix hint are correct. Only the line number is wrong.

The root cause is in the scalar-field loop of `MarkdownStr.from_text` (`src/biz/dfch/specmgr/models/md/markdown_str.py`). The loop advances `remaining_offset` by the reported `extent` of the field it just consumed. Then `format_text(...)` re-normalizes the remainder, and that step removes the leading separator line, which is not part of `extent`. As a result, `remaining_offset` never includes the removed separator lines. The `_offset` that each later field receives is short, and so are the "text left over" and "expected ..., found no match" line references and every later child's `_line`. The `process_list_field` path already avoids this problem: it measures a before/after line-count delta. This feature applies the same approach to the scalar path.

The defect is pre-existing and shared by every domain built on `models/md`. It does not change whether a document is accepted or rejected. It only makes triage harder, because the reported line points at the wrong place.

### Requirements

- REQ-001: The scalar-field branch of `MarkdownStr.from_text` MUST advance `remaining_offset` by the actually-consumed line count of `remaining_text` (the before/after line-count delta across the re-normalization), not by the field's reported `extent`, matching the `process_list_field` branch.
- REQ-002: The "text left over after processing all fields" message of a multi-field section MUST report the 1-based line of the unconsumed block in the mdformat-normalized body.
- REQ-003: The "expected ..., found no match" message for a field that follows one or more consumed scalar fields MUST report the 1-based line, in the mdformat-normalized body, where that field's remaining text starts.
- REQ-004: The `_line` attribute of every child instance parsed after one or more consumed scalar fields MUST equal its 1-based line in the mdformat-normalized body, so that domain-level messages built from `self._line` (e.g. `rsk/models/v1/tara.py`, `rsk/models/v1/assessment.py`) report the correct line.
- REQ-005: The fix MUST NOT change acceptance or rejection of any document, any exception type, any document-relative field path, or any cause/fix hint. Only line numbers that were too low may change.
- REQ-006: The change MUST be confined to the shared `models/md` engine. No domain model, parser, or tool changes its behavior except through the corrected line number.

### Acceptance Criteria

- [ ] ACC-001: A synthetic multi-field `MarkdownSection` model in `tests/models/md` with two consumed scalar fields followed by an unconsumed trailing block raises the "text left over" `AssertionError` with the exact normalized-body line of the trailing block (REQ-001, REQ-002); the test fails on the pre-fix code.
- [ ] ACC-002: A synthetic model whose mandatory third field finds no match after two consumed scalar fields raises "expected ..., found no match" with the exact normalized-body line where the remainder starts (REQ-003); the test fails on the pre-fix code.
- [ ] ACC-003: A test asserts that the `_line` of a child parsed after two consumed scalar fields equals its normalized-body line (REQ-004), and an `rsk` test pins the corrected line in one `self._line`-based message (tara or assessment) whose field follows a consumed scalar field, or records that no current rsk shape reaches that case.
- [ ] ACC-004: The issue's repro, a `dec` document whose `## Decision Outcome` is a lead paragraph plus a second paragraph plus a block quote, fails through `parse_dec`/`validate(type="dec")` with a line reference that points at the block quote's normalized-body line (line 5 in the issue's section-relative example), not the pre-fix value (line 3).
- [ ] ACC-005: Every pinned message that changes in `tests/models/md/test_validation_error_baseline.py` or any other test changes only in its line number, upward, and each changed pin is listed in the phase's update entry (REQ-005).
- [ ] ACC-006: `git diff --stat` against `dev` touches only `src/biz/dfch/specmgr/models/md/`, tests, and this plan (REQ-006).
- [ ] ACC-007: The full quality gate passes: `ruff format --check`, `ruff check`, `vulture`, and `pytest -n auto`.

### Scope

#### Included

- Fix the `remaining_offset` advance in the scalar-field branch of `MarkdownStr.from_text`.
- Regression tests for the "text left over" and "found no match" line references and for child `_line` values.
- The issue's `dec` `## Decision Outcome` repro as a domain-level regression test.
- Updates to pinned messages whose line numbers were wrong before the fix (baseline tests and downstream `_line` consumers such as `rsk`).

#### Explicitly Out Of Scope

- Any change to message wording, field paths, cause/fix hints, or exception types.
- Any change to the acceptance or rejection rules of any domain (e.g. feat-247's relaxed `## Decision Outcome`).
- Line-number accuracy of the `process_list_field` path, which is already correct.
- Line references relative to the raw on-disk file (including frontmatter); the reference stays relative to the mdformat-normalized body.

### Dependencies

#### Depends On

- FEAT feat-27-validation: introduced the actionable messages and their 1-based line references that this feature corrects.

#### Blocks

- FEAT feat-247-dec-outcome-blocks: its rejected-kinds errors for `## Decision Outcome` show the same under-reported line. feat-247 does not cause the defect and does not need this fix to ship, but its messages are only correct after it.

### Design Notes

Current scalar branch (`markdown_str.py`, end of the field loop):

```python
remaining_offset += extent
remaining_lines = remaining_text.splitlines()[extent:]
remaining_text = format_text("\n".join(remaining_lines)) if remaining_lines else ""
```

Proposed change, identical in principle to the list branch directly above it:

```python
remaining_lines = remaining_text.splitlines()[extent:]
new_remaining_text = format_text("\n".join(remaining_lines)) if remaining_lines else ""
consumed = len(remaining_text.splitlines()) - len(new_remaining_text.splitlines())
remaining_offset += consumed
remaining_text = new_remaining_text
```

`consumed` is `extent` plus the separator lines that the re-normalization removed. Optionally, factor the shared "slice, re-normalize, measure delta" step into one small helper that both branches call, so they cannot drift apart again.

Line-number model: `_offset` is 0-based and relative to the start of the text handed to the outermost `from_text` call; messages report `_offset + 1`. The tests must state which text that is (the normalized body or the section text) and compute the expected line from it, not from the raw file.

Impact on `_line`: `process_field` passes `remaining_offset` as the child's `_offset`, so the same deficit reaches every child's `_line`. Domain validators that format `self._line` (currently `rsk/models/v1/tara.py` and `rsk/models/v1/assessment.py`) inherit the fix with no change to their own code.

### Task List

#### Phase 100: Pin the Defect

- [ ] Task 100.100: Add failing synthetic engine tests in `tests/models/md` for the "text left over" line (ACC-001), the "found no match" line (ACC-002), and child `_line` (ACC-003, engine part).
- [ ] Task 100.110: Add the failing `dec` `## Decision Outcome` repro test (ACC-004).
- [ ] Task 100.120: Find the `rsk` `self._line` message case that follows a consumed scalar field and pin its correct line, or record in this plan that no current rsk shape reaches that case (ACC-003, rsk part).

#### Phase 110: Fix the Offset

- [ ] Task 110.100: Change the scalar-field branch of `MarkdownStr.from_text` to advance `remaining_offset` by the before/after line-count delta (REQ-001); optionally extract a shared helper for both branches.
- [ ] Task 110.110: Update the code comment and docstring in `from_text` that describe offset tracking, so both branches are documented as delta-based.
- [ ] Task 110.120: Make the Phase 100 tests pass; update every other pinned message whose line number changes, and list each one in the update entry (ACC-005).

#### Phase 120: Verify and Close Out

- [ ] Task 120.100: Run the full quality gate (ACC-007) and check the diff scope (ACC-006).
- [ ] Task 120.110: Update `CHANGELOG.md` `[Unreleased]` with a Fixed entry referencing issue #253.
- [ ] Task 120.120: Update this plan's Progress section and set the status to review.

## Progress

### Current Status

**As of 2026-11-22**: Planned from GitHub issue #253. No implementation has started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-22T14:33:13.895Z - Created

Created the feature plan from GitHub issue #253. The scope is the fix of the scalar-field offset in the shared `models/md` engine plus all consumers of the corrected offset (engine messages and child `_line`, e.g. `rsk`). The regression oracle is synthetic engine tests plus the issue's `dec` `## Decision Outcome` repro.

### More Information

- GitHub issue #253: models/md: scalar-field 'text left over' errors under-report the body line (offset deficit per consumed field).
