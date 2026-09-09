---
classification: null
created: '2026-09-05 00:20:55.989+02:00'
id: 2687d267-b1f7-4bf6-96f1-2bbf70e19b84
status: draft
type: tsk
updated: '2026-09-06 09:37:34.609+02:00'
version: 1.0.0
---

# Fix Remaining feat-* README.md Documents to Validate Against the Current FEAT Schema

<!-- Tracks the 33 `.specmgr/feat/<ref>/README.md` documents that still fail to parse
against the current `FeatDocument` schema (frontmatter + body), as reported by
`specmgr_list_feat`/`specmgr_get_feat`. `feat-0-termxplorer-mcp` was already fixed
as a worked example -- see the detailed method in "Recent Updates" below before
starting any of these. Number the tasks so they are easier to track. -->

- [ ] Task 1: Fix `feat-10-add-artifact-type-tasklist/README.md`. Known error: a `### Requirements` bullet has a leading `[x]` checkbox marker and wraps across multiple lines, both invalid for `RequirementItem`.

- [ ] Task 2: Fix `feat-12-qa-artifact/README.md`. Known error: a `### Requirements` bullet's description text wraps across multiple lines (embedded newline breaks the single-line `REQ-NNN: ` regex).

- [ ] Task 3: Fix `feat-13-list-paging/README.md`. Known error: a `### Requirements` bullet's description text wraps across multiple lines.

- [ ] Task 4: Fix `feat-14-qa-v2-adjacent-qa/README.md`. Known error: a `### Requirements` bullet's description text wraps across multiple lines.

- [ ] Task 5: Fix `feat-15-add-artifact-type-risk/README.md`. Known error: a `### Requirements` bullet has a leading `[x]` checkbox marker and wraps across multiple lines.

- [ ] Task 6: Fix `feat-16-problem-statement/README.md`. Known error: a `### Requirements` bullet's description text wraps across multiple lines.

- [ ] Task 7: Fix `feat-18-goal/README.md`. Known error: a `### Requirements` bullet's description text wraps across multiple lines.

- [ ] Task 8: Fix `feat-21-decision/README.md`. Known error: an `### Acceptance Criteria` item has a parenthetical `(REQ-001)` right after the `ACC-NNN` number instead of directly before the colon, and wraps across multiple lines.

- [ ] Task 9: Fix `feat-22-consolidate-mutation-tools/README.md`. Known error: a `### Requirements` bullet's description text wraps across multiple lines.

- [ ] Task 10: Fix `feat-27-validation/README.md`. Frontmatter already fixed; the raw-HTML `<domain>` defect (a nested-backtick code-span delimiter mismatch around "before: `\"raw HTML is not permitted...`" -- the outer single-backtick delimiter collided with an inner nested double-backtick sequence, fixed by widening the outer delimiter to a triple backtick) is also already fixed. Known error (body, now surfaced): an `### Updates` entry heading around body line 124 (`#### 2026-09-02 00:15:00.000Z — Orchestrator final verification and close-out`) fails the `#### {timestamp} ( - | : ) {title}` regex -- an em dash `—` is used instead of the required `-`/`:` separator; inspect and reformat.

- [ ] Task 11: Fix `feat-28-get-update/README.md`. Frontmatter already fixed; the raw-HTML `<d>` defect is also already fixed (two causes: a soft-wrapped narrative line starting with a bare `+`, which CommonMark interpreted as starting a new bulleted list mid-paragraph -- fixed by escaping it to `\+`; and a genuinely bare, unwrapped `get_<d>` mention -- fixed by wrapping it in backticks). Known error (body, now surfaced): an `### Updates` entry heading around body line 207 (`#### 2026-09-02 — Merged upstream dev (63149b0)...`) fails the `#### {timestamp} ( - | : ) {title}` regex -- a bare date with no time-of-day, using an em dash `—` instead of the required `-`/`:` separator; inspect and reformat to the full `YYYY-MM-DD HH:MM:SS.fff` + `Z`/offset timestamp.

- [ ] Task 12: Fix `feat-30-sop/README.md`. Known error: a `### Requirements` bullet's description text wraps across multiple lines.

- [ ] Task 13: Fix `feat-31-feature/README.md`. Frontmatter `version` already normalized to `1.0.0` (this body error is unaffected). Known error: a bare, unescaped `</content>` token in prose is parsed as raw inline HTML and rejected; wrap it in a code span or an HTML comment.

- [ ] Task 14: Fix `feat-32-sysrs/README.md`. Known error: a `### Requirements` bullet has a parenthetical `(research, done)` right after the `REQ-NNN` number instead of after the colon, and wraps across multiple lines.

- [ ] Task 15: Fix `feat-33-vcr/README.md`. Frontmatter `version` already normalized to `1.0.0` (this body error is unaffected). Known error: a `### Requirements` bullet has a parenthetical `(decided)` right after the `REQ-NNN` number, and wraps across multiple lines.

- [ ] Task 16: Fix `feat-4-use-cases/README.md`. Frontmatter `version` already normalized to `1.0.0` (this body error is unaffected). Known error: `### Scope` uses free-form `**Included in this feature:**` prose instead of the mandatory `#### Included`/`#### Explicitly Out Of Scope` H4 sub-headings -- this is an old document predating several current schema fields (also check Requirements/Acceptance Criteria/Task List presence).

- [ ] Task 17: Fix `feat-40-docs-prune/README.md`. Known error: a `### Requirements` bullet's description text wraps across multiple lines.

- [ ] Task 18: Fix `feat-48-feat-id/README.md`. Frontmatter already fixed (`created`/`updated` now valid). Known error (body, now surfaced): an `### Updates` entry heading around body line 138 (e.g. `#### 2026-09-02 18:00:00.000Z — Phase 6: Release (Task 6.2, PR opened)`) fails the `#### {timestamp} ( - | : ) {title}` regex -- likely an em dash `—` used instead of the required `-`/`:` separator; inspect and reformat.

- [ ] Task 19: Fix `feat-5-md-model-parser/README.md`. Frontmatter `version` already normalized to `1.0.0` (this body error is unaffected). Known error: `### Requirements` content is free-form reconciliation prose, not a list of `REQ-NNN: ...` bullets -- this is an old document predating the current schema; needs the fullest rework of this batch.

- [ ] Task 20: Fix `feat-50-confluence/README.md`. Frontmatter already fixed (`created`/`updated` now valid). Known error (body, now surfaced): a `### Task List` `#### Phase N` section around body line 162 has a checklist item that does not match the `- [ ]`/`- [x] Task N.M: ...` pattern; inspect and reformat.

- [ ] Task 21: Fix `feat-51-mcp-cwd/README.md`. Frontmatter already fixed (`created`/`updated` now valid). Known error (body, now surfaced): an `### Updates` entry heading around body line 71 (e.g. `#### 2026-09-02 — Phase 3 complete: final verification pass, feature done`) fails the `#### {timestamp} ( - | : ) {title}` regex -- missing the time-of-day component; reformat to the full `YYYY-MM-DD HH:MM:SS.fff` + `Z`/offset timestamp.

- [ ] Task 22: Fix `feat-56-classification-attribute-in-frontmatter/README.md`. Frontmatter already fixed; the raw-HTML `<d>` defect is also already fixed (root cause: a broken nested code span around "`- A change to \`status\` -> set_status(...)`" -- an outer single-backtick delimiter collided with an inner nested single-backtick pair, plus several stray backslash-escaped backticks and missing spaces around adjacent code spans; fixed by widening the outer delimiter to a double backtick and correcting the escaping/spacing throughout that sentence, with every word preserved unchanged). Known error (body, now surfaced): an `### Updates` entry heading around body line 178 (`#### 2026-09-02 22:15:00.000Z — Phase 5 (Verification) complete -- feature done`) fails the `#### {timestamp} ( - | : ) {title}` regex -- an em dash `—` is used instead of the required `-`/`:` separator; inspect and reformat.

- [ ] Task 23: Fix `feat-57-uc-commands/README.md`. Frontmatter already fixed (`created`/`updated` now valid). Known error (body, now surfaced): an `### Updates` entry heading around body line 115 (e.g. `#### 2026-09-02 00:00:00.000Z — Phase 4: Tests & verification (feature complete)`) fails the `#### {timestamp} ( - | : ) {title}` regex -- likely an em dash `—` used instead of the required `-`/`:` separator; inspect and reformat.

- [ ] Task 24: Fix `feat-6-requirement-artifact/README.md`. Frontmatter `version` already normalized to `1.0.0` (this body error is unaffected). Known error: a `### Requirements` bullet has a leading `[x]` checkbox marker, invalid for `RequirementItem`.

- [ ] Task 25: Fix `feat-69-update-context/README.md`. Known error: a bare `<d>` token in prose is parsed as raw inline HTML and rejected; wrap it in a code span or an HTML comment.

- [ ] Task 26: Fix `feat-7-various-improvements/README.md`. Known error: a bare `<name>` token in prose is parsed as raw inline HTML and rejected; wrap it in a code span or an HTML comment.

- [ ] Task 27: Fix `feat-73-74-76/README.md`. Known error: leftover, unrecognized trailing content in `## Plan` after all its known fields are matched (structure/heading mismatch somewhere in that section) -- inspect closely, likely an extra or misplaced `### Design Notes` sub-heading.

- [ ] Task 28: Fix `feat-8-coverage-badge/README.md`. Frontmatter already fixed (`status` now `done`). Known error (body, now surfaced): `### Scope` around body line 33 uses free-form `**Included:**` prose instead of the mandatory `#### Included`/`#### Explicitly Out Of Scope` H4 sub-headings.

- [ ] Task 29: Fix `feat-80-feat-id/README.md`. Known error: an `### Updates` entry heading uses a bare date with an extra colon inside the title, or otherwise fails the `#### {timestamp} ( - | : ) {title}` heading regex -- inspect and reformat to the full `YYYY-MM-DD HH:MM:SS.fff` + `Z`/offset timestamp form.

- [ ] Task 30: Fix `feat-81-83-validation/README.md`. Frontmatter `version` already normalized to `1.0.0` (this body error is unaffected). Known error: a `### Requirements` bullet has a long parenthetical `(Phase 6, added following an independent post-closeout quality review)` right after the `REQ-NNN` number, and wraps across multiple lines.

- [ ] Task 31: Fix `feat-9-doc-in-specmgr/README.md`. Frontmatter already fixed (`status` now `progress`). Known error (body, now surfaced): `### Scope` around body line 32 uses free-form `**Included:**` prose instead of the mandatory `#### Included`/`#### Explicitly Out Of Scope` H4 sub-headings.

- [ ] Task 32: Fix `feat-92-resources/README.md`. Known error: a `#### Phase N` task item has a checkbox marker embedded after other text (malformed `- [x] Task 4.1: ...` continuation) and wraps across multiple lines.

- [ ] Task 33: Fix `feat-94-frontmatter-schema/README.md`. Known error: leftover, unrecognized trailing content in `### Updates` after all recognized entries are matched -- an entry heading likely doesn't match the required `#### {timestamp} ( - | : ) {title}` pattern.

## Recent Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-09-06 07:36:11.000Z - Raw-HTML defects fixed for Tasks 10, 11, 22; known-error text refreshed again

Fixed the raw-HTML/list-marker body defects for the 3 documents whose "Known error" text (as of the previous entry below) described a raw-inline-HTML rejection: Task 10 (`feat-27-validation`), Task 11 (`feat-28-get-update`), Task 22 (`feat-56-classification-attribute-in-frontmatter`). Each fix was a small, surgical text replacement diagnosed by tokenizing the exact mdformat-normalized body against this repo's own `markdown_it` instance (`biz.dfch.specmgr.models.md._markdown.md`) to locate precisely which code-span delimiter was mismatched, then verifying the corrected snippet in isolation produced zero `html_inline`/`html_block` tokens before touching the real file. `feat-27-validation`: a "before:" quoted example message used a single-backtick outer code-span delimiter around content that itself contained a nested double-backtick-delimited sequence, so the outer span closed early at the first inner single-backtick run, leaving `<domain>` unprotected -- fixed by widening the outer delimiter to a triple backtick (no words changed). `feat-28-get-update`: two independent causes in the same paragraph -- (1) a soft-wrapped continuation line started with a bare `+`, which CommonMark interpreted as interrupting the paragraph to start a new bulleted list (the same defect class this repo's own feat-27 was built to diagnose, coincidentally present in feat-28's own prose), fixed by escaping it to `\+`; (2) a separate, genuinely bare `get_<d>` mention with no surrounding backticks at all, fixed by wrapping it in a code span. `feat-56-classification-attribute-in-frontmatter`: a sentence describing an appended instructions bullet had a broken nested code span (single-backtick outer delimiter colliding with an inner single-backtick pair around "status"), two stray backslash-escaped backticks that don't actually prevent delimiter matching in CommonMark (escapes are not processed inside code-span delimiter search), and several missing spaces where adjacent code spans had been accidentally glued to neighboring words -- fixed by widening the outer delimiter to a double backtick, removing the two stray escapes, and adding the missing spaces; every word in the sentence is unchanged. Content-preservation was verified for all three by stripping backticks/backslashes and comparing whitespace-collapsed old vs. new text -- identical in every case (see the subagent's own report, which additionally caught that the `feat-56` comparison needed the stricter "remove all whitespace" comparison rather than "collapse to one space", since two of the fixes correctly *inserted* previously-missing spaces between words that had been typo'd together, e.g. `status`)bullet:` -> `status`) bullet:` -- no word itself changed). Frontmatter `updated` was bumped to a shared batch timestamp (`2026-09-06 07:25:54.000Z`) on all three; every other frontmatter field, and the rest of each document's body, was left untouched. Re-ran `specmgr_list_feat` afterward and independently confirmed via direct `git diff`: all three raw-HTML errors are gone, each now surfacing a *different*, unrelated, already-known-class defect instead (an `### Updates` entry heading using an em dash `—` instead of the required `-`/`:` separator -- the same class of defect already tracked for Tasks 18, 21, 23) -- their "Known error" text above has been updated accordingly. None of these 3 documents are fully `valid` yet (`specmgr_list_feat`'s `error_count` is still 33/40, unchanged) -- the newly-surfaced `### Updates` heading defects still need their own fix pass. No `git commit` was run.

### 2026-09-06 07:15:22.000Z - Frontmatter-only pass completed for 15 documents; known-error text refreshed

Completed a frontmatter-only pass (separate from the body fixes tracked above) on 15 of the 33 documents, done via direct read/overwrite (not `specmgr_update`, for the same reason noted below): 7 documents (Tasks 10, 11, 18, 20, 21, 22, 23) had their `created`/`updated` reformatted from bare-ISO/`T`-separated/fractional-second-mismatched values to the required `yyyy-MM-dd HH:mm:ss.fff` + `Z`/offset shape; 2 documents (Tasks 28, 31) had their invalid `status` corrected (`completed` -> `done`, `in-progress` -> `progress`); 6 documents (Tasks 13, 15, 16, 19, 24, 30) had an elevated `version` (e.g. `1.13.0`, `1.7.0`, `1.16.4`, `1.6.15`, `1.2.0`) reset to `1.0.0` to match the convention every already-clean `feat` document uses (this was not required to fix parsing -- `models.md` only enforces the major version component -- but was done for consistency per explicit user confirmation). Every touched document also had `updated` bumped to a shared batch timestamp (`2026-09-06 07:09:18.000Z`); `id`/`created` (for the non-Group-A docs)/`type`/`classification` were left untouched, and no body content was touched in any of the 15. Re-ran `specmgr_list_feat` afterward: for the 9 documents whose frontmatter actually was the blocking error (the 7 timestamp docs + 2 status docs), the reported error changed to a body-level defect, confirming the frontmatter itself now parses cleanly -- their "Known error" text above has been updated accordingly to describe the newly-surfaced body defect instead of the now-fixed frontmatter one. For the 6 version-only documents, the reported error is unchanged (as expected, since an elevated-but-major-1 `version` was never the actual blocker) -- their task lines above got a short parenthetical note instead, so it's clear the frontmatter part of that task is already done even though the error text itself didn't change. None of these 15 documents are fully `valid` yet (`specmgr_list_feat`'s `error_count` is still 33/40) -- the body-level defects tracked by these tasks still need their own fix pass.

### 2026-09-04 22:17:05.000Z - Other defects, and the step-by-step fix method

Other defects seen in this batch: raw inline HTML tokens (a bare `<name>`, `<d>`, `</content>` in prose) rejected by the CommonMark parser, fixed by wrapping them in a code span (e.g. `` `<name>` ``) or an HTML comment; `### Updates`/`### Decisions Made` entry headings not matching the `#### {timestamp} ( - | : ) {title}` pattern (wrong separator, missing time-of-day, or a bare date without the full timestamp), fixed by reformatting while keeping entries newest-first; and, in the two oldest documents (`feat-4-use-cases`, `feat-5-md-model-parser`), entirely missing mandatory sections that need whatever equivalent free-form content already exists reshaped into the mandatory heading structure without inventing new facts. The fix method, step by step, for every task above: read the target file; run `specmgr_validate` with `type="feat"`, `full=true`, and the file's current full content (frontmatter + body) to see the first reported error (it reports one error at a time, so this is iterative); fix only structure/formatting per the rules in the other entries below, preserving every piece of substantive content (all requirements, task items, narrative text, decisions/updates, code/file references) and never deleting real information or shortening technical descriptions; re-run `specmgr_validate` and repeat until it returns valid with no errors; then bump frontmatter `updated` to the current UTC timestamp in the required format, keep `id`/`created`/`version` unchanged, and keep `status` unchanged unless it was one of the invalid values noted in the other entries below; write the corrected file back to its exact original path (overwrite in place), without creating a new folder/id and without touching any other feature folder; finally verify with `specmgr_get_feat(id=<ref>)` (must succeed) and `specmgr_list_feat` (that ref's entry must show `"error": null`), and do not run `git commit` -- leave each fix as an uncommitted working-tree edit for review.

### 2026-09-04 22:17:04.000Z - The single most common defect: soft-wrapped REQ/ACC/Task bullets

The single most common defect in this batch: a `REQ-NNN:`/`ACC-NNN:`/`Task N.M:` bullet's own description text is soft-wrapped across multiple physical lines in the source file, and the parser's regex for these (e.g. `^REQ-\d{3}: (?P<description>.+)$`) has no `DOTALL`/`MULTILINE` flag, so an embedded newline inside the bullet's own text makes the whole match fail; the fix is to reflow the wrapped lines into a single logical line (join with single spaces), which preserves 100% of the original words and only removes the line breaks -- never shorten, paraphrase, or drop content to make a line "fit", long single lines are fine. A second common defect is a stray `- [x]`/`- [ ]` checkbox marker in front of a `REQ-NNN:`/`ACC-NNN:` item, or a parenthetical like `(decided)`/`(Phase 6, ...)` squeezed between the number and the colon, both of which are invalid; the fix is to move any such annotation to after the colon (inside the description text) or drop the checkbox entirely for Requirements, which are plain bullets and never checkboxes.

### 2026-09-04 22:17:03.000Z - The required FEAT document shape

The required FEAT shape (see resource `specmgr://feat/schema`, or `specmgr_get_feat_template`/`specmgr_get_feat_example` for worked samples): frontmatter `created`/`updated` must match `^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})$` (e.g. `2026-09-04 22:17:01.000Z`), not a bare ISO `T`-separated timestamp and not missing fractional seconds; frontmatter `status` must be exactly one of `planning`/`progress`/`review`/`done` (map old values like `completed` to `done` and `in-progress` to `progress`); the body is `# Feature: {title}` then `## Plan` holding mandatory `### Overview` free prose, mandatory `### Requirements` with at least one plain bullet `- REQ-NNN: {text}`, mandatory `### Acceptance Criteria` with at least one checkbox bullet `- [ ] ACC-NNN: {text}` or `- [x] ACC-NNN: {text}`, mandatory `### Scope` with exactly `#### Included` then `#### Explicitly Out Of Scope`, optional `### Dependencies` (`#### Depends On`/`#### Blocks`), optional `### Design Notes`, optional `### Related Decisions`, and mandatory `### Task List` with at least one `#### Phase N: {title}` each holding at least one flat checklist item `- [ ] Task N.M: {text}` or `- [x] Task N.M: {text}`; then `## Progress` holding mandatory `### Current Status` free prose, optional `### Blockers`, mandatory `### Updates` with at least one entry newest-first as `#### {timestamp} ( - | : ) {title}` followed by one lead prose paragraph, optional `### Decisions Made` in the same entry shape, optional `### Related PRs / Commits`, and optional `### More Information`; sections must appear in exactly this order, with no unknown or duplicate headings.

### 2026-09-04 22:17:02.000Z - Why the generic update/set_status tools cannot be used directly

The generic `specmgr_update`/`specmgr_set_status` tools first load-and-parse the existing document to preserve its frontmatter, which fails immediately for every document in this list, since that is the whole problem being fixed; so each fix must instead be done by reading the file directly (e.g. the `read` tool) and, once corrected, overwriting it directly (e.g. the `write` tool), not via `specmgr_update`.

### 2026-09-04 22:17:01.000Z - Created, with a detailed how-to method for every task above

Created this task list after fixing `feat-0-termxplorer-mcp/README.md` by hand as a worked example, which now parses cleanly; the remaining 33 `feat` documents in `.specmgr/feat/` still fail `specmgr_get_feat`/`specmgr_list_feat` parsing, and the entries above record the exact method used successfully on `feat-0-termxplorer-mcp`, to be repeated for each task above, one feature folder at a time.
