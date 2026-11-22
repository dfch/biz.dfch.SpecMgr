---
classification: null
created: '2026-11-22T15:33:48.257+01:00'
id: feat-253-md-line-offset
status: review
type: feat
updated: '2026-11-22T17:01:32.328+01:00'
version: 1.0.0
---

# Feature: models/md Scalar-Field Line-Offset Deficit in Actionable Error Messages (Issue #253)

## Plan

### Overview

The actionable error messages of the shared `models/md` engine (feat-27-validation) carry a 1-based line reference into the mdformat-normalized body. That line reference, and the `_line` of every parsed child, is often too low. The field path and the cause/fix hint are correct. Only the line number is wrong.

Two mechanisms cause the deficit. Both have the same shape: a parent cuts off the part it has consumed, re-normalizes the rest with `format_text(...)` (which removes the leading blank separator line), and then advances the offset by a count that does not include the removed line.

1. Scalar-field hand-off. The scalar-field loop of `MarkdownStr.from_text` (`src/biz/dfch/specmgr/models/md/markdown_str.py`) advances `remaining_offset` by the reported `extent` of the field it just consumed. The extent of a paragraph or of a block-quote-like leaf field (e.g. feat-247's `OutcomeBlocks`) stops before the trailing blank line, so one line is lost after each such field. The extent of a section-typed field runs up to the next heading and includes its trailing blank line, so no line is lost after a section. This is the mechanism that issue #253 reports.
2. Own-block hand-off. `MarkdownSection.from_text` (`markdown_section.py`), `MarkdownParagraph.from_text` (`markdown_paragraph.py`), and `MarkdownListItem.from_text` (`markdown_list_item.py`) pass `_offset + own_lines` to their children, where `own_lines` is the token-map end of their own heading, paragraph, or item paragraph. When a blank line follows that block, the re-normalization removes it and the children start one line too low. This affects every section with nested fields, at every nesting level, and every `MarkdownListItemWithNotes` note.

The deficits add up along the nesting path. Measured on `dev` 9c9d7349: in `## X` / blank / `A.` / blank / `### Y` / blank / `B.`, the engine reports `A.` on line 2 (true 3), `### Y` on line 3 (true 5), and `B.` on line 4 (true 7). The `process_list_field` path already avoids the problem, because it measures a before/after line-count delta. This feature applies the same approach to every hand-off.

The defect is pre-existing and shared by every domain built on `models/md`. It does not change whether a document is accepted or rejected. It only makes triage harder, because the reported line points at the wrong place.

### Requirements

- REQ-001: The scalar-field branch of `MarkdownStr.from_text` MUST advance `remaining_offset` by the actually-consumed line count of `remaining_text` (the before/after line-count delta across the re-normalization), not by the field's reported `extent`, matching the `process_list_field` branch.
- REQ-002: The "text left over after processing all fields" message of a multi-field section MUST report the 1-based line of the unconsumed block in the mdformat-normalized body.
- REQ-003: The "expected ..., found no match" message MUST report the 1-based line, in the mdformat-normalized body, where that field's remaining text starts. When the remaining text is empty (e.g. a mandatory field is missing at the end of its parent), the message MUST report the line directly after the last consumed line, which can be one past the last line of the body.
- REQ-004: The `_line` attribute of every parsed child, at every nesting level, MUST equal its 1-based line in the mdformat-normalized body. Every domain-level message built from `self._line` therefore reports the correct line, with no change to its own code. The current consumers are `rsk/models/v1/tara.py`, `rsk/models/v1/assessment.py`, `rsk/models/v1/risk_matrix.py`, `vcr/models/v1/body.py`, `feat/models/v1/body.py`, `tsk/models/v1/task_item.py`, and `general/models/dtais.py`, `ears.py`, `iso29148.py`, `rasci.py`.
- REQ-005: The fix MUST NOT change acceptance or rejection of any document, any exception type, any document-relative field path, or any cause/fix hint. Only line numbers that were too low may change.
- REQ-006: The behavioral change MUST be confined to the shared `models/md` engine. No domain model, parser, or tool changes its behavior except through the corrected line number. Regenerated documentation and schema files, `CHANGELOG.md`, and this plan change only as a consequence.
- REQ-007: `MarkdownSection.from_text`, `MarkdownParagraph.from_text`, and `MarkdownListItem.from_text` MUST advance the offset they hand to their children by the actually-consumed line count of their own text (the before/after line-count delta across the re-normalization), not by the token-map end of their own block.

### Acceptance Criteria

- [x] ACC-001: A synthetic multi-field `MarkdownSection` model in `tests/models/md` with two consumed scalar fields followed by an unconsumed trailing block raises the "text left over" `AssertionError` with the exact normalized-body line of the trailing block (REQ-001, REQ-002). The model is parsed from a section text with its heading, so the heading hand-off is covered too. The test fails on the pre-fix code.
- [x] ACC-002: A synthetic model whose mandatory third field finds no match after two consumed scalar fields raises "expected ..., found no match" with the exact normalized-body line where the remainder starts (REQ-003). The test fails on the pre-fix code.
- [x] ACC-003: A test asserts that the `_line` of a child parsed after two consumed scalar fields equals its normalized-body line (REQ-004). An `rsk` test pins the corrected line in one `self._line`-based message (tara or assessment) of a real rsk body. Because every child inside a section is affected by the heading hand-off, this case always exists.
- [x] ACC-004: The issue's repro is a `dec` body built from the packaged `dec/data/dec_example.md`, where `## Decision Outcome` holds the lead paragraph, a second paragraph, and a block quote. It fails through `parse_dec` with a "text left over" line reference equal to the block quote's line in the normalized body that `parse_dec_body` builds. The test computes the expected line from that normalized body (the first line that starts with `> `) and does not take it from the issue. Measured on `dev` 9c9d7349: true line 38, pre-fix 35, scalar-only fix 36. The test fails on the pre-fix code and on a scalar-only fix. The repro needs feat-247's relaxed `## Decision Outcome` rule, which is on `dev` but not in release v0.38.0, so the test runs against the worktree code and not against a release-based `specmgr` MCP server.
- [x] ACC-005: Every pinned message that changes in `tests/models/md/test_validation_error_baseline.py`, `tests/models/md/test_error_messages.py`, or any other test changes only in its line number, upward, and each changed pin is listed in the phase's update entry (REQ-005). A test docstring that states a line number is corrected together with its pin. Known cases: `test_error_messages.py` `test_missing_leaf_paragraph_line_reference_points_at_the_entry_heading` (`### My Update` is line 5, not 4; the missing `content` is reported at line 6 per REQ-003) and `test_a_second_entry_reports_a_deeper_line_reference` (`### Second Update` is line 9; expected line 10, not 8).
- [x] ACC-006: `git diff --stat` against `dev` touches only `src/biz/dfch/specmgr/models/md/`, tests, regenerated files (`docs/api/`, `docs/GENERATED.md`, `docs/*_schema.json`, `src/biz/dfch/specmgr/*/data/*_schema.json`), `CHANGELOG.md`, and this plan (REQ-006). No domain model, parser, or tool source file changes.
- [x] ACC-007: The full quality gate passes: `ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`, and the `specmgr docs` / `specmgr schema` drift checks.
- [x] ACC-008: Synthetic tests pin the own-block hand-off (REQ-007): a section with a paragraph and a nested H3 section (the `## X` / `### Y` shape in the Overview: `A.` line 3, `### Y` line 5, `B.` line 7), and a `MarkdownListItemWithNotes` whose note follows a blank line (note on its true line). The tests fail on the pre-fix code. `MarkdownParagraph` with nested fields gets the same test if a synthetic model can reach that path; otherwise the update entry records why not.
- [x] ACC-009: An oracle test parses every packaged `*_example.md` of the `models/md`-based domains and, for every parsed child at every nesting level, asserts that line `child._line` of the normalized body is the first line of that child's text. It needs no hand-computed line numbers and fails on the pre-fix code.

### Scope

#### Included

- Delta-based offset advance in the scalar-field branch of `MarkdownStr.from_text` (REQ-001).
- Delta-based offset hand-off in `MarkdownSection.from_text`, `MarkdownParagraph.from_text`, and `MarkdownListItem.from_text` (REQ-007).
- One shared helper for the "slice, re-normalize, return (new text, consumed lines)" step, used by every site above and by the `process_list_field` branch.
- Regression tests for the "text left over" and "found no match" line references, the empty-remainder rule, child `_line` values, and the example-file oracle.
- The issue's `dec` `## Decision Outcome` repro as a domain-level regression test.
- Updates to pinned messages and test docstrings whose line numbers were wrong before the fix, in `tests/models/md` and in downstream `_line` consumers (REQ-004 list).
- Regeneration of the documentation and schema files that carry the changed docstrings.

#### Explicitly Out Of Scope

- Any change to message wording, field paths, cause/fix hints, or exception types.
- Any change to the acceptance or rejection rules of any domain (e.g. feat-247's relaxed `## Decision Outcome`).
- Line references relative to the raw on-disk file (including frontmatter); the reference stays relative to the mdformat-normalized body.

### Dependencies

#### Depends On

- FEAT feat-27-validation: introduced the actionable messages and their 1-based line references that this feature corrects.
- FEAT feat-247-dec-outcome-blocks: its relaxed `## Decision Outcome` rule is what makes the issue's repro shape (lead paragraph, second paragraph, block quote) reach the "text left over" error that ACC-004 pins. It is merged on `dev` but not in release v0.38.0. feat-247 does not cause the defect. Its rejected-kinds messages show the corrected line only after this fix.

### Design Notes

Current scalar branch (`markdown_str.py`, end of the field loop):

```python
remaining_offset += extent
remaining_lines = remaining_text.splitlines()[extent:]
remaining_text = format_text("\n".join(remaining_lines)) if remaining_lines else ""
```

Current own-block hand-off (`markdown_section.py`; `markdown_paragraph.py` and `markdown_list_item.py` use the same pattern with `own_lines`):

```python
heading_lines = heading_map[1]
body_lines = text.splitlines()[heading_lines:]
body_text = format_text("\n".join(body_lines)) if body_lines else ""
instance = super().from_text(body_text, _path=own_path, _offset=_offset + heading_lines)
```

Proposed change: one shared helper in `models/md` that slices off the first `n` lines, re-normalizes the rest, and returns the new text together with the consumed line count (`len(text.splitlines()) - len(new_text.splitlines())`). Every site above calls it and advances its offset by the returned count. The `process_list_field` branch already computes the same delta inline and uses the helper's count as well, so no site can drift again. The consumed count is the block's own lines plus the separator lines that the re-normalization removed. For an empty rest it is all lines of the text, which gives the REQ-003 empty-remainder rule.

Line-number model: `_offset` is 0-based and relative to the start of the text handed to the outermost `from_text` call; messages report `_offset + 1`. This is feat-27's documented limitation. Real callers pass the whole normalized body (e.g. `parse_dec_body` passes `format_text(content)` to `Decision.from_text`), so the tests compute every expected line from that normalized body, never from the raw file or from a section-relative text.

Impact on `_line`: `process_field` and the own-block hand-offs pass the corrected offset as the child's `_offset`, so every child's `_line` is correct. The domain validators in the REQ-004 list inherit the fix with no change to their own code.

Verification environment: run every check with the worktree code (`uv run --frozen ...`). The `specmgr` MCP server in the development session is based on the latest release tag (v0.38.0), not on `dev`. It lacks unreleased material such as feat-247's `## Decision Outcome` rule and the ADR removal (feat-46), so its `validate`/`parse_dec` results differ from the worktree for the ACC-004 repro.

### Task List

#### Phase 100: Pin the Defect

- [x] Task 100.100: Add failing synthetic engine tests in `tests/models/md` for the "text left over" line (ACC-001), the "found no match" line (ACC-002), and child `_line` (ACC-003, engine part).
- [x] Task 100.105: Add failing synthetic tests for the own-block hand-off of sections, list items with notes, and (if reachable) paragraphs (ACC-008), and for the REQ-003 empty-remainder rule.
- [x] Task 100.110: Add the failing `dec` `## Decision Outcome` repro test with the expected line computed from the normalized body (ACC-004).
- [x] Task 100.115: Add the failing example-file oracle test over every packaged `*_example.md` of the `models/md`-based domains (ACC-009).
- [x] Task 100.120: Pin the corrected line of one `rsk` `self._line`-based message (tara or assessment) of a real rsk body (ACC-003, rsk part).

#### Phase 110: Fix the Offset

- [x] Task 110.100: Add the shared "slice, re-normalize, return (new text, consumed lines)" helper and use it in the scalar-field and list branches of `MarkdownStr.from_text` (REQ-001).
- [x] Task 110.105: Use the helper for the own-block hand-off in `MarkdownSection.from_text`, `MarkdownParagraph.from_text`, and `MarkdownListItem.from_text` (REQ-007).
- [x] Task 110.110: Update the code comments and docstrings that describe offset tracking, so every hand-off is documented as delta-based.
- [x] Task 110.120: Make the Phase 100 tests pass; update every other pinned message and test docstring whose line number changes (incl. the two `test_error_messages.py` cases in ACC-005 and the downstream consumers in the REQ-004 list, e.g. `tests/tsk/models/v1/test_task_item.py`, `tests/feat/models/v1/test_body.py`), and list each one in the update entry (ACC-005).
- [x] Task 110.130: Regenerate `docs/api/`, `docs/GENERATED.md`, and the JSON schemas (`specmgr docs`, `specmgr schema`) for the changed docstrings, e.g. `markdown_str`, `markdown_block_quote`, the domain body pages, `docs/qa_schema.json`, and `qa/data/qa_schema.json`.

#### Phase 120: Verify and Close Out

- [x] Task 120.100: Run the full quality gate (ACC-007) and check the diff scope (ACC-006).
- [x] Task 120.110: Update `CHANGELOG.md` `[Unreleased]` with a Fixed entry referencing issue #253.
- [x] Task 120.120: Update this plan's Progress section and set the status to review.

## Progress

### Current Status

**As of 2026-11-22**: The implementation is complete and in review. Phases 100, 110, and 120 are done. Every hand-off in `models/md` advances the line offset by the delta that the shared helper `consume_leading_lines` returns. ACC-001 to ACC-009 are met, the full quality gate and the drift checks pass (except the 2 known, unrelated `tests/evals/test_cli_gates.py` rootless-Docker failures, which PR #272 fixes), and `CHANGELOG.md` has a Fixed entry. Next: review and merge.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-22T16:01:32.324Z - Phase 120 verified and closed out

Implemented Tasks 120.100 to 120.120. All checks ran with the worktree code (`uv run --frozen ...`).

- Gate (Task 120.100, ACC-007):
  - `uv run --frozen ruff format --check`: pass (2387 files already formatted).
  - `uv run --frozen ruff check`: pass.
  - `uv run --frozen vulture src/ whitelist.py --min-confidence 60`: pass.
  - `uv run --frozen pytest -n auto -q`: 6127 passed, 18 skipped, 11124 subtests passed, 2 failed. The 2 failures are `tests/evals/test_cli_gates.py::TestCliOverFixtures::test_good_workspace_cli_matches_preexported_fixture` and `test_weak_workspace_cli_is_valid_but_thin`. They come from rootless Docker on this machine, are unrelated to this feature, and are fixed by the separate PR #272.
  - Drift: `specmgr docs`, `specmgr mcp-docs`, `specmgr schema`, and the 14 `specmgr schema --type <t> --output-dir src/biz/dfch/specmgr/<t>/data` runs, followed by `git status --short`: no change.
- Pre-fix check: in a temporary detached worktree at HEAD with `src/biz/dfch/specmgr/models/md/` restored from `dev`, the 12 new tests give 11 failed and 1 passed. The test that passes is `test_every_example_has_parsed_children`, the non-empty guard of the oracle. The worktree was removed.
- Diff scope (ACC-006): `git diff --stat dev...HEAD` lists 58 files. They are the plan, `docs/GENERATED.md`, 43 `docs/api/*.md` pages, 6 files under `src/biz/dfch/specmgr/models/md/`, and 8 test files. No other `src/` file changed and no JSON schema changed. `CHANGELOG.md` is the only other changed file (this phase).
- ACC walk-through:
  - ACC-001: `tests/models/md/test_line_offset.py` `test_text_left_over_reports_the_line_of_the_unconsumed_block` (true line 7, pre-fix 4; fails pre-fix).
  - ACC-002: `test_found_no_match_reports_the_line_where_the_remainder_starts` (true line 7, pre-fix 4; fails pre-fix). The REQ-003 empty-remainder rule: `test_found_no_match_with_an_empty_remainder_reports_the_line_after_the_last_line`.
  - ACC-003: `test_child_line_after_two_scalar_fields_is_its_normalized_body_line` (engine part) and `tests/rsk/models/v1/test_tara_line_reference.py` `test_invalid_quadrant_bullet_reports_its_normalized_body_line` (rsk tara, true line 24, pre-fix 20). Both fail pre-fix.
  - ACC-004: `tests/dec/models/v1/test_outcome_line_reference.py` `test_text_left_over_reports_the_block_quote_line` (expected line computed from the normalized body, 38; pre-fix 35; scalar-only fix 36, per the Phase 100 entry). Fails pre-fix.
  - ACC-005: the 5 changed pins listed in the Phase 110 entry, each changed only in its line number, upward. Diff: `tests/models/md/test_error_messages.py`, `tests/test_schema_metadata_invariance.py`, `tests/general/tools/test_validate.py`.
  - ACC-006: the diff-scope check above.
  - ACC-007: the gate above.
  - ACC-008: `test_nested_section_children_are_on_their_normalized_body_lines` (`(3, 5, 7)`), `test_section_child_after_the_heading_is_on_its_normalized_body_line`, `test_list_item_note_after_a_blank_line_is_on_its_normalized_body_line`, and `test_paragraph_child_after_the_paragraph_is_on_its_normalized_body_line`. All fail pre-fix.
  - ACC-009: `tests/models/md/test_example_line_oracle.py` `test_every_parsed_child_line_is_the_first_line_of_its_text` over the 14 packaged examples. Fails pre-fix.
- CHANGELOG (Task 120.110): a `### Fixed` entry under `[Unreleased]` for issue #253.
- Plan (Task 120.120): ACC-001 to ACC-009 and the Phase 120 tasks ticked, Current Status rewritten, frontmatter `status` set to `review` and `updated` bumped.

#### 2026-11-22T15:36:39.449Z - Phase 110 fixed the offset

Implemented Tasks 110.100 to 110.130. Behavioral changes are only in `src/biz/dfch/specmgr/models/md/`.

- Helper (Task 110.100): `consume_leading_lines(text, count) -> tuple[str, int]` in `src/biz/dfch/specmgr/models/md/_markdown.py`, next to `format_text`. It slices off the first `count` lines, re-normalizes the rest with `format_text` (`""` for an empty rest), and returns the rest with the consumed count `len(text.splitlines()) - len(rest.splitlines())`. For an empty rest the count is all lines of `text`, which gives the REQ-003 empty-remainder rule.
- Call sites:
  - `markdown_str.py`: the scalar-field branch of `MarkdownStr.from_text` (REQ-001) and the per-item loop of `process_list_field`. The list branch of `from_text` keeps its before/after delta across `process_list_field`, because that method returns the reduced text and not a count (its public signature is used by tests). That delta is the telescoping sum of the per-item helper counts, so it is the same value. A comment records this.
  - `markdown_section.py`, `markdown_paragraph.py`, `markdown_list_item.py`: the own-block hand-off (REQ-007) passes `_offset + consumed` instead of `_offset + heading_lines` / `_offset + own_lines`.
  - `markdown_block_quote.py`: no change in behavior. The composite quote consumes no line (dedenting keeps every line), so its children start at its own `_offset`. A comment records that the delta is `0`.
- Docs (Task 110.110): the docstrings of `MarkdownStr.from_text`, `process_list_field` (`_offset`), `MarkdownSection.from_text`, `MarkdownParagraph.from_text`, and `MarkdownListItem.from_text` now describe the delta-based hand-off and name `consume_leading_lines`. Inline comments at every call site name feat-253.
- Phase 100 tests (Task 110.120): removed the 11 strict `xfail` markers, the `_PRE_FIX` constant, the module docstring note about it, and the 4 `import pytest` lines that only served them, in `tests/models/md/test_line_offset.py`, `tests/models/md/test_example_line_oracle.py`, `tests/dec/models/v1/test_outcome_line_reference.py`, and `tests/rsk/models/v1/test_tara_line_reference.py`. All 12 tests pass.
- Changed pins (ACC-005). Each one changes only in its line number, upward. Field path, message text, hint, and exception type are unchanged:
  - `tests/models/md/test_error_messages.py` `test_missing_leaf_paragraph_line_reference_points_at_the_entry_heading`: line 4 to line 6 (`### My Update` is line 5 of the 5-line body; the missing `content` is reported one past the end, REQ-003). Docstring corrected.
  - `tests/models/md/test_error_messages.py` `test_a_second_entry_reports_a_deeper_line_reference`: line 8 to line 10 (`### Second Update` is line 9). Docstring extended with the lines.
  - `tests/test_schema_metadata_invariance.py` `TestTskCheckboxInvariance.test_bad_marker_character_still_rejected_with_same_message`: `Task > TaskItem (line 2)` to `(line 3)` (`- [z] Bad checkbox` is line 3, after `# Task List` and a blank line).
  - `tests/test_schema_metadata_invariance.py` `TestTskCheckboxInvariance.test_missing_marker_still_rejected_with_same_message`: `Task > TaskItem (line 2)` to `(line 3)`, same reason.
  - `tests/general/tools/test_validate.py` `TestValidateMessageTruncation.test_short_message_is_returned_unchanged`: line 3 to line 4 (the `req` body has 3 lines and `Characteristics` is missing at its end, REQ-003).
- Downstream consumers named in the task: `tests/tsk/models/v1/test_task_item.py` (`TaskItem (line 3)`, through `process_list_field`, which was already delta-based) and `tests/feat/models/v1/test_body.py` (`FeatTaskItem (line 1)`, a standalone item) were already correct and are unchanged. No pin in `tests/models/md/test_validation_error_baseline.py` changed.
- Regenerated (Task 110.130): `docs/GENERATED.md` (also the test-file count, 502 to 506, from the 4 Phase 100 test files) and 43 `docs/api/*.md` pages: the 6 changed `models/md` modules, every `markdown_section*`, `markdown_code_block`, `markdown_comment`, `common_sections`, and every domain or `general` model page that inherits the changed `from_text` / `process_list_field` docstrings. No JSON schema changed: `specmgr schema` and the 14 `specmgr schema --type <t> --output-dir src/biz/dfch/specmgr/<t>/data` runs produce no diff, because the schemas do not carry these method docstrings. `specmgr mcp-docs` and `specmgr harness-bundle` produce no diff. A second run of all regenerations produces no further diff.
- Gate: `ruff format --check`, `ruff check`, and `vulture` pass. `pytest -n auto -q`: everything passes, 0 xfailed, except the 2 known `tests/evals/test_cli_gates.py` `TestCliOverFixtures` failures (rootless Docker on this machine, unrelated).

#### 2026-11-22T15:08:43.858Z - Phase 100 pinned the defect

Added the Phase 100 tests (Tasks 100.100 to 100.120). No `src/` file changed. Every test that fails on the pre-fix engine has the marker `@pytest.mark.xfail(strict=True, reason="feat-253: fixed in Phase 110")`, so the suite stays green and each test is shown to fail. Every expected line comes from the mdformat-normalized text given to the outermost `from_text` call. No expected line is hard-coded.

- `tests/models/md/test_line_offset.py` (ACC-001, ACC-002, ACC-003 engine part, REQ-003, ACC-008), 8 tests, all `xfail`:
  - `test_text_left_over_reports_the_line_of_the_unconsumed_block`: pre-fix line 4, true line 7.
  - `test_found_no_match_reports_the_line_where_the_remainder_starts`: pre-fix line 4, true line 7.
  - `test_found_no_match_with_an_empty_remainder_reports_the_line_after_the_last_line`: pre-fix line 4, true line 6 (5-line text plus one).
  - `test_child_line_after_two_scalar_fields_is_its_normalized_body_line`: pre-fix `(2, 3, 4)`, true `(3, 5, 7)`.
  - `test_section_child_after_the_heading_is_on_its_normalized_body_line`: pre-fix line 2, true line 3.
  - `test_nested_section_children_are_on_their_normalized_body_lines` (the Overview's `## X` / `### Y` shape): pre-fix `(2, 3, 4)`, true `(3, 5, 7)`.
  - `test_list_item_note_after_a_blank_line_is_on_its_normalized_body_line`: pre-fix line 2, true line 3.
  - `test_paragraph_child_after_the_paragraph_is_on_its_normalized_body_line`: pre-fix line 2, true line 3.
- Reachability: a synthetic model can reach `MarkdownParagraph` with nested fields. `_LeadWithQuote(MarkdownParagraph)` has a `quote: MarkdownBlockQuote` field and is parsed directly, so ACC-008's paragraph case is pinned and does not need a reason note.
- `tests/models/md/test_example_line_oracle.py` (ACC-009), 2 tests: `test_every_parsed_child_line_is_the_first_line_of_its_text` is `xfail`. Before the fix, it finds that the `_line` of all 597 parsed children of the 14 packaged `{domain}_example.md` files is wrong. `test_every_example_has_parsed_children` passes before the fix. It is not marked, because it only makes sure that the oracle is not empty. The domains come from `WHOLE_BODY_DOMAINS`, and each document is parsed through `whole_body_domain(...).parse_text`. The comparison ignores surrounding whitespace, because nested children are rendered dedented. It also ignores the number of an ordered-list marker, because mdformat renumbers an item that is rendered alone (`01.` in the `uc` body becomes `1.`).
- `tests/dec/models/v1/test_outcome_line_reference.py` (ACC-004), 1 test, `xfail`: `parse_dec` reports line 35 before the fix. The true line is 38, the first `> ` line of `format_text` of the frontmatter-stripped content.
- `tests/rsk/models/v1/test_tara_line_reference.py` (ACC-003 rsk part), 1 test, `xfail`. The test uses the packaged `rsk_tara.md` and removes the backticks from the strategy word of one quadrant bullet. `QuadrantItem.strategy`'s `self._line` message reports line 20 before the fix. The true line is 24. The test uses tara and not assessment, because the `@alias` regex of the `Probability`/`Impact` heading rejects a bad heading at parse time. So the `self._line` messages in `assessment.py` cannot be reached through the engine.
- Fix check (scratch only, reverted, `git status` clean for `src/`): with a simulated delta-based fix at all four hand-off sites, all 12 new tests pass. With only the scalar fix, the `dec` test still fails and reports line 36, as ACC-004 states.

#### 2026-11-22T14:54:01.220Z - Plan refined

Applied the refinement review. The main change widens the scope: the deficit has a second mechanism, the own-block hand-off in `MarkdownSection`, `MarkdownParagraph`, and `MarkdownListItem` (new REQ-007, ACC-008, Tasks 100.105 and 110.105). Without that fix, ACC-004 cannot pass. Measured on `dev` 9c9d7349 with the worktree code: the dec repro reports line 35 for a block quote on line 38, and a scalar-only fix would report 36. Other changes:

- ACC-004 is restated against `parse_dec_body`'s normalized body, with the expected line computed in the test.
- REQ-003 defines the empty-remainder line.
- REQ-004 lists every `self._line` consumer.
- ACC-005 names the two `test_error_messages.py` pins whose docstrings state wrong lines.
- ACC-006 and REQ-006 allow `CHANGELOG.md` and the regenerated docs and schemas (new Task 110.130).
- ACC-007 includes the drift checks.
- ACC-009 adds an example-file oracle test (Task 100.115).
- The ACC-003 escape hatch is dropped.
- The shared helper is mandatory.
- feat-247 moves from Blocks to Depends On: it is done and is a precondition of the ACC-004 repro shape, not something this feature blocks.
- Design Notes record that the session's `specmgr` MCP server runs release v0.38.0, so verification uses the worktree code.

#### 2026-11-22T14:33:13.895Z - Created

Created the feature plan from GitHub issue #253. The scope is the fix of the scalar-field offset in the shared `models/md` engine plus all consumers of the corrected offset (engine messages and child `_line`, e.g. `rsk`). The regression oracle is synthetic engine tests plus the issue's `dec` `## Decision Outcome` repro.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-22T15:36:39.449Z - Put the hand-off helper in `_markdown.py` and keep `process_list_field`'s signature

`consume_leading_lines` lives in the private `models/md/_markdown.py`, next to `format_text`, because every caller already imports from there and the helper is a pure text operation. `process_list_field` keeps its public `(remaining_text, items)` return value, because domain tests call it directly. The list branch of `MarkdownStr.from_text` therefore keeps its own before/after delta, which equals the sum of the per-item helper counts. The helper does not assert that the consumed count is at least `count`, because a new assertion could change acceptance (REQ-005).

#### 2026-11-22T15:08:43.858Z - Pin pre-fix failures with strict pytest xfail markers

The pre-commit hook runs the full test suite, so a red test cannot be committed. Each Phase 100 test that fails before the fix therefore has the marker `@pytest.mark.xfail(strict=True, reason="feat-253: fixed in Phase 110")`. The tests stay `unittest.TestCase` methods. The marker is the one pytest-specific part. The repo already uses a pytest marker in `tests/general/tools/test_similarity_real_backend.py`, and CI and pre-commit run the suite through pytest. `strict=True` turns an unexpected pass into a failure. `--runxfail` shows the real failure and the reported line. Phase 110 removes every marker when the fix lands.

### More Information

- GitHub issue #253: models/md: scalar-field 'text left over' errors under-report the body line (offset deficit per consumed field).
