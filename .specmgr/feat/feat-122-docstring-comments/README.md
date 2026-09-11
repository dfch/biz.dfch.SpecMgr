---
classification: null
created: '2026-09-11 06:58:07.735+02:00'
id: feat-122-docstring-comments
status: planning
type: feat
updated: '2026-09-11 22:00:55.518+02:00'
version: 1.0.0
---

# Feature: Stop Restating Hardcoded Domain/Type Counts in Prose Docstrings and Comments

## Plan

### Overview

While verifying feat-120-remove-confluence, stale prose was found in `src/biz/dfch/specmgr/general/tools/__init__.py` claiming "the eleven whole-body document types" when the current count is twelve (missing `sysrs`, added by feat-32-sysrs). A repo-wide search showed this is a systemic pattern: many docstrings, comments, and MCP tool description strings restate "how many domains does this tool/concept apply to" as a cardinal number word (`ten`/`eleven`/`twelve`/`thirteen`), duplicating information already fully and authoritatively expressed by the code itself (a `Literal[...]` type hint, a `frozenset`/tuple of domain names, or an explicit `req/uc/tsk/.../sysrs` list right next to the number). Every time a domain is added (most recently `sysrs`; `AGENTS.md` already reserves a future spot for `ac`), every one of these manually-written count words has to be found and bumped by hand, with no test or lint rule catching a miss -- and the drift has already produced inconsistent counts describing the identical set of domains across different files, in some cases producing counts that are now flatly incorrect (not just redundant) because a list/count was never updated after `sysrs` was added. This feature removes the bare cardinal-number pattern from `src/`, `AGENTS.md`, and (at full priority) `tests/` prose, corrects the handful of spots where the underlying count/list itself is stale rather than merely redundant, and adds a convention to `.specmgr/conventions.md` so the pattern is not reintroduced.

### Requirements

- REQ-001: No `src/` docstring, comment, or MCP tool description string states a bare cardinal number (`ten`/`eleven`/`twelve`/`thirteen`, in word or digit form) as a domain/type count.

- REQ-002: Where a docstring/comment already lists the actual domains explicitly (e.g. `req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs`), the list is kept as-is but the redundant cardinal-number adjective in front of it is dropped -- unless the existing list/count is itself stale (e.g. missing a domain added after the list was last written), in which case the list/count is corrected to the current, accurate domain set, not merely destyled (see REQ-008 for the confirmed cases).

- REQ-003: Where a comment describes a domain set by contrast to another (e.g. "every domain except `feat`", "every domain except `adr`"), it is phrased relationally instead of restating a count that then has to be kept in sync separately.

- REQ-004: `specmgr docs` and `specmgr mcp-docs` produce zero further `git status` diff after the wording edits, since some of the edited strings feed generated documentation (`docs/api/`, `docs/GENERATED.md`, `docs/MCP.md`).

- REQ-005: `.specmgr/conventions.md` documents the new "don't restate a domain/type count as a cardinal number" rule in the `### Docstring Style` subsection (under `## Additional Best Practices`).

- REQ-006: The same count-word cleanup identified in `src/` is also applied to the identified `tests/` docstrings/comments (non-assertion text only), tracked at the same priority as the `src/` cleanup.

- REQ-007: No `Literal[...]` type hint, `frozenset`/tuple constant, or dispatch table that defines which domains a tool supports is changed by this feature -- the change is prose-only.

- REQ-008: The following spots are confirmed to carry a **stale** (factually incorrect, not just redundant) count or explicit domain list -- missing `sysrs`, or otherwise miscounting the current 12 whole-body domains -- and must have their content corrected, not just cosmetically destyled: `general/tools/__init__.py`'s `update`/`set_classification`/`delete` paragraphs (say "eleven" and list 11 domains, actually twelve); the same paragraphs' embedded "ten flat domains" sub-phrase (line 44, inside the `delete` paragraph, describing the flat-file domains excluding `feat`; actual count is eleven, not ten); its `set_status` paragraph (says "twelve" and lists 12 domains, actually thirteen including `adr`); `general/tools/set_classification.py:46` ("ten whole-body domains'", should be eleven); `general/tools/set_status.py:699` ("eleven whole-body domains", should be twelve); `general/tools/update.py:47` ("the other ten's identical shape", should be eleven) and `update.py:786` ("ten UUID domains", should be eleven); `general/tools/delete.py:42` and `:411` ("ten UUID domains" x2, should be eleven); `general/tools/_path_safety.py`'s `assert_uuid` docstring (says "ten `_UUID_TYPES` domains", the constant has twelve entries); `general/tools/_splice.py` (says "eleven `get_<d>` tools", all twelve whole-body `get_<d>` tools implement `raw=True`); `adr/tools/create_adr.py` and `adr/tools/validate_adr.py` (both say "eleven whole-body domains", should be twelve); `tests/general/tools/test_update.py` (says "ten UUID domains" at lines 604/1338, should be eleven; also "ten whole-body document types" at line 20, should be twelve; also "eleven whole-body domains, feat included" at line 1360, self-contradictory as written, should be twelve). The spots beyond the original six were found by a third, independent review pass -- see REQ-012.

- REQ-009: `AGENTS.md`'s confirmed 14 occurrences of the same cardinal-number pattern (13 word-form, plus 1 digit-form introduced by the `dev` merge described in REQ-011) are in scope and reworded identically to the `src/`/`tests/` cleanup.

- REQ-010: `CHANGELOG.md`, `docs/adr/*.md`, `docs/gol/*.md`, `docs/req/*.md`, and `docs/sysrs/*.md` are explicitly out of scope: these are historical/point-in-time records (a changelog entry or an ADR/GOL/REQ/SysRS artifact describes the state of the world when it was written), not living documentation, so a count that was accurate at authoring time is not "drift" in the sense this feature addresses.

- REQ-011: Merging `dev` into this branch after the plan was first drafted (bringing in `feat-107-doc-cache`, GitHub issue #107, a per-domain read-cache feature touching all 80 files across every domain) introduced new occurrences of the identical cardinal-number pattern into files that either did not exist yet or were not in scope at drafting time -- including, ironically, inside `feat-107-doc-cache`'s own newly-added `AGENTS.md` paragraph. Every file identified by the post-merge re-audit (see Design Notes) is folded into Phase 1/Phase 2 scope rather than left as a silent gap, and this plan's line-number cross-references are corrected where the merge shifted them.

- REQ-012: A third, independent gap review -- run directly against the current repository state rather than trusting this plan's own prior line numbers/counts -- found that even after two prior review passes, scope was still incomplete: (a) `general/tools/_timestamps.py:34-35` carries a previously-undetected stale digit-form occurrence ("the 11 `create_<d>` tools... and the 11 `set_status` adapter sites") that belongs in scope but was absent from every prior file list; (b) REQ-008's own "confirmed stale" list was itself still incomplete, missing at least eight additional stale spots inside files already in scope, even though this plan's own Design Notes had already namechecked the `delete.py`/`update.py` "ten UUID domains" drift as illustrative motivation without ever turning it into an actionable, corrected item (see Design Notes for the full account). All of REQ-012's findings are folded into REQ-008, Scope, and the Task List rather than left as a fourth silent gap.

- REQ-013: Every occurrence touched during Phase 1/Phase 2 implementation must be cross-checked against the domain's actual current `Literal[...]`/constant/tool count at edit time (per ACC-007), not only the occurrences pre-identified in REQ-008 -- since REQ-008's enumerated list has now proven incomplete across three successive review passes (pre-implementation, post-`dev`-merge, and REQ-012's independent re-verification), treating it as exhaustive is not a safe assumption.

- REQ-014: Before applying any fix, each occurrence's phrasing must be classified as either a *self-excluded relational* count (e.g. "the other eleven domains", meaning the current domain's 11 siblings out of 12 total -- already correct as-is in `_cache.py`/`_sentinel.py`/`list_feat.py`/`_doc_paths.py`) or a *total-inclusive* count (e.g. "the eleven whole-body domains" describing all of them from an outside perspective such as ADR's own docs, or "ten UUID domains" meaning the UUID-domain total minus `feat`) -- the same words ("eleven"/"ten") mean different numbers in these two phrasings, so a mechanical global find/replace (e.g. blindly bumping every "eleven" to "twelve") would silently break the already-correct self-excluded occurrences while fixing the total-inclusive ones, or vice versa. REQ-001's actual fix (removing the cardinal number entirely in favor of an explicit list or relational phrase) sidesteps this risk if applied literally, but the distinction must still be understood before rewording, since a shortened relational rewrite (e.g. "the other whole-body domains") must still preserve which domains are meant.

- REQ-015: As a final due-diligence check (Task 3.2), a broadened grep covering the cardinal numbers six/seven/eight/nine (word and digit form, in addition to the ten-thirteen range already audited) is run across `src/`, `tests/`, and `AGENTS.md` to confirm no older docstring -- written when the domain count was smaller, before `dec`/`sop`/`vcr`/`sysrs` were added -- still carries an even-more-stale, undetected reference; this range was not covered by any of the three prior review passes.

### Acceptance Criteria

- [ ] ACC-001: No `src/` docstring/comment/description string states a bare cardinal number (`ten`/`eleven`/`twelve`/`thirteen`, or their digit forms) as a domain/type count; explicit domain lists and relational phrasing ("except `feat`"/"except `adr`") are used instead.

- [ ] ACC-002: `specmgr docs`/`specmgr mcp-docs` (and, per Task 3.2, `specmgr adr-toc`) produce zero further `git status` diff after the edits.

- [ ] ACC-003: Full quality gate green: `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, `pytest -n auto`.

- [ ] ACC-004: `.specmgr/conventions.md` documents the new rule.

- [ ] ACC-005: The same cleanup is applied to the identified `tests/` files (Phase 2), tracked at full priority rather than deferred.

- [ ] ACC-006: `AGENTS.md` has zero remaining bare cardinal-number domain/type counts (word or digit form).

- [ ] ACC-007: Every stale count/list identified across all review passes (REQ-008's full list, as most recently expanded by REQ-012) is verified corrected (not just destyled) by a follow-up `grep`/read after editing, cross-checked against the domain's actual `Literal[...]`/constant it was describing; per REQ-013, this cross-check applies to every occurrence touched during implementation, not only the ones pre-identified before Phase 1 started.

- [ ] ACC-008: Every file identified by REQ-011's post-merge re-audit (`general/tools/_doc_paths.py`, `feat/tools/_cache.py`, `req/tools/_cache.py`, `tests/general/tools/test_doc_cache_structural.py`, `tests/general/tools/test_doc_cache_delete_scan_race.py`, and the new `AGENTS.md` paragraph) is confirmed reworded by a follow-up `grep` after editing.

- [ ] ACC-009: `general/tools/_timestamps.py`'s stale digit-form domain-count phrases are corrected and confirmed reworded by a follow-up `grep` after editing (REQ-012).

- [ ] ACC-010: The final broadened six/seven/eight/nine grep (REQ-015, Task 3.2) across `src/`, `tests/`, and `AGENTS.md` finds zero further domain/type-count occurrences.

### Scope

#### Included

- Rewording docstrings/comments/MCP tool description strings in the 22 confirmed `src/` files: the issue's original 16 (`general/tools/__init__.py`, `general/tools/set_classification.py`, `general/tools/set_status.py`, `general/tools/update.py`, `general/tools/delete.py`, `general/tools/validate.py`, `general/tools/_path_safety.py`, `server.py`, `general/resources/config.py`, `general/resources/__init__.py`, `feat/models/v1/summary.py`, `feat/tools/list_feat.py`, `models/config_info.py`, `models/md/_frontmatter_parse.py`, `adr/tools/validate_adr.py`, `adr/tools/create_adr.py`), plus 2 more found via a repo-wide `grep -rn -iE "\b(ten|eleven|twelve|thirteen)\b" --include="*.py" src/` audit that the issue's own list missed: `general/tools/_splice.py` and `rsk/tools/_sentinel.py`; plus 3 more found via a post-plan re-audit after merging `dev`'s `feat-107-doc-cache` (GitHub issue #107) into this branch, which introduced new occurrences the original audit could not have found (REQ-011): `general/tools/_doc_paths.py` (a pre-existing file substantially rewritten by that merge), and two brand-new files it added, `feat/tools/_cache.py` and `req/tools/_cache.py`; plus 1 more found via a third, independent re-audit performed directly against the current repository state (REQ-012): `general/tools/_timestamps.py` (a pre-existing file none of the prior two audits examined, carrying a stale digit-form "the 11 `create_<d>` tools" phrase). Considerably more of these occurrences require an actual factual correction, not merely destyling, than originally identified -- REQ-008 (as expanded by REQ-012) is the current, complete list; the 3 merge-introduced files from REQ-011 and most of the REQ-011/REQ-012 file-level additions already carry correct counts and only need destyling.

- Rewording `AGENTS.md`'s 14 confirmed occurrences of the same pattern (REQ-009): 13 word-form found in the original audit, plus 1 digit-form found inside the `feat-107-doc-cache` paragraph the `dev` merge itself added (REQ-011).

- Rewording the same count-word pattern in the 16 confirmed `tests/` files: the original 10 (`tests/sysrs/models/v1/test_parser.py`, `tests/general/resources/test_config.py`, `tests/general/models/test_summary.py`, `tests/general/tools/test_set_classification.py`, `tests/general/tools/test_validate.py`, `tests/general/tools/test__path_safety.py`, `tests/general/tools/test_set_status.py`, `tests/general/tools/test_delete.py`, `tests/general/tools/test_update.py`, `tests/feat/tools/test_list_feat.py`), plus 4 more found via a follow-up audit covering digit-form counts and files the original grep missed: `tests/commands/test_schema.py`, `tests/general/tools/test_error_context.py`, `tests/models/md/test_frontmatter_errors.py`, and `tests/adr/tools/test_create_adr.py` (this last one only matches in digit form -- "the 11 whole-body domains" -- which is why the original word-only grep missed it); plus 2 more brand-new test files added by the `dev` merge's `feat-107-doc-cache` (REQ-011): `tests/general/tools/test_doc_cache_structural.py` and `tests/general/tools/test_doc_cache_delete_scan_race.py`. The third-pass re-audit (REQ-012) found no additional `tests/` files beyond these 16 once QA-category-count and ADR's-own-tool-count false positives are excluded.

- Adding a new rule to `.specmgr/conventions.md`'s `### Docstring Style` subsection (under `## Additional Best Practices`).

- Regenerating `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md` where the edited strings feed generated docs, confirmed via a clean `git status` diff.

- A full quality-gate run (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`) after each phase's edits, as a safety net.

#### Explicitly Out Of Scope

- Any change to the actual `Literal[...]` type hints, `frozenset`/tuple constants, or dispatch tables that define which domains a tool supports -- this feature is prose-only.

- feat-120-remove-confluence itself; this issue's trigger was discovered during that feature's verification but is unrelated to Confluence in subject matter.

- Adding an automated lint/CI rule that catches a reintroduced cardinal-number count word; only a documented convention in `.specmgr/conventions.md` is in scope.

- `CHANGELOG.md`, `docs/adr/*.md`, `docs/gol/*.md`, `docs/req/*.md`, `docs/sysrs/*.md` (REQ-010): historical/point-in-time records, not living documentation, so left untouched.

- `src/biz/dfch/specmgr/qa/data/qa_*_instructions.md`'s "ten fixed category headings" wording: this "ten" describes QA's own fixed ISO-25010-derived category count, not a domain/type count, and is not subject to the same domain-addition drift this feature targets.

- `.specmgr/conventions.md`'s `### Docstring Style` subsection's own example, which is written in Google-style (`Args:`/`Returns:`) even though every file audited across all three review passes actually uses NumPy-style (`Parameters`/`Returns` with underlines): a real, pre-existing style-guide/practice mismatch noticed while touching that subsection (Task 3.1), but unrelated to the cardinal-number pattern this feature targets, so left as-is.

### Design Notes

The rule exists because manually-maintained count words have already drifted: `delete.py`/`update.py` describe "the ten UUID domains" while `set_classification.py` describes "the eleven UUID domains" for the identical set, and `tests/general/tools/test_update.py` alone mixes "ten whole-body document types", "twelve domains", and "eleven whole-body domains" in different docstrings. Dropping the redundant cardinal number -- keeping only explicit domain lists or relational phrasing -- removes the drift vector entirely, since there is no longer a count to fall out of sync whenever a domain (e.g. `sysrs`, and later `ac`) is added.

A fresh `grep -rn -iE "\b(ten|eleven|twelve|thirteen)\b" --include="*.py" src/` confirmed 82 total word-form occurrences (80 matching lines, two of which carry two matches each) across these 18 files (not the issue's original 16) -- each a small, one-word/one-phrase edit inside an existing docstring paragraph, comparable in scale to (and smaller than) precedent single-phase/single-task batches already completed in this repo (feat-38-39-41-43-44's Phase 3: 44 call sites across ~13 files in one task; Phase 5: one line added to 39 files in one task), which is why this feature keeps three phases rather than subdividing further by file count.

A follow-up verification pass (done before Phase 1 implementation started) additionally found: (1) digit-form counts (e.g. "12-way union return type", "13-way `set_status`") inside `set_classification.py`, `set_status.py`, and `update.py` that the original word-only grep never matched, even though REQ-001 always covered digit form; (2) that several of the paragraphs this feature intended to merely destyle are not just stylistically redundant but factually wrong -- `general/tools/__init__.py`'s `update`/`set_classification`/`delete` paragraphs explicitly enumerate 11 domains (no `sysrs`) while the tools' own `Literal[...]` (originally at `update.py:700`, `set_classification.py:494`, `delete.py:363` -- see the note below on why these line numbers have since shifted) show 12; its `set_status` paragraph says "twelve" while `set_status.py`'s `Literal` shows 13 (12 whole-body + `adr`); `_path_safety.py:117`'s `assert_uuid` docstring says "ten" against a 12-element `_UUID_TYPES` frozenset (line 66); `_splice.py:23,48` says "eleven `get_<d>` tools" against 12 confirmed `get_<d>` tools implementing `raw: bool = False`; and `adr/tools/create_adr.py:24`/`adr/tools/validate_adr.py:29` both say "eleven whole-body domains" against the current 12. REQ-008/ACC-007 track fixing these as actual content corrections, verified against the code they describe, not simply dropping the adjective (REQ-002's caveat). The same follow-up pass found 3 additional `tests/` files with word-form matches the issue's original audit missed (`tests/commands/test_schema.py`, `tests/general/tools/test_error_context.py`, `tests/models/md/test_frontmatter_errors.py`) and 1 more matching only in digit form (`tests/adr/tools/test_create_adr.py`, "the 11 whole-body domains"), plus confirmed `AGENTS.md` itself (the single most authoritative, actively-maintained reference this repo has) carries 13 occurrences of the identical pattern and was folded into scope (REQ-009) rather than left as a silent gap.

**Post-merge re-audit (REQ-011), done after merging `dev` into this branch, before any Phase 1 implementation started.** Merging `dev` pulled in `feat-107-doc-cache` (GitHub issue #107), an 80-file change adding a per-domain read cache to all 12 whole-body domains. A fresh repo-wide re-grep (word- and digit-form, `src/`, `tests/`, `AGENTS.md`) found this merge introduced new occurrences of the exact pattern this feature targets, none of which the original audit could have found since the content didn't exist yet:

- `general/tools/_doc_paths.py` (pre-existing file, substantially rewritten by the merge) gained a new digit-form occurrence ("...the generic `delete` tool triggers the exact same race for every one of the other 11 domains."); count is correct (11 = 12 whole-body minus `feat`), needs destyling only.
- `feat/tools/_cache.py` and `req/tools/_cache.py` (brand-new files the merge added) each carry a domain-count phrase ("the other eleven whole-body domains" x2 in `feat/tools/_cache.py`; "the other 11 generic whole-body domains" in `req/tools/_cache.py`) -- correct counts, destyling only. None of the other 10 domains' own `_cache.py` copies carry this note.
- `feat/tools/list_feat.py` (already in scope, Task 1.12) gained a *second*, digit-form occurrence ("...the same rule every one of the other 11 whole-body domains'...") alongside its pre-existing word-form one -- both must be reworded, not just the original.
- `tests/general/tools/test_doc_cache_structural.py` and `tests/general/tools/test_doc_cache_delete_scan_race.py` (both brand-new files) carry 6 and 4 occurrences respectively (word- and digit-form), all with correct counts.
- `AGENTS.md`'s own newly-merged `feat-107-doc-cache` paragraph contains a digit-form occurrence ("for the 12 generic whole-body domains (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`, `dec`, `sop`, `feat`, `vcr`, `sysrs`)") that the original word-only-derived "13 confirmed occurrences" (REQ-009) did not and could not count -- bringing AGENTS.md's total to 14.

Separately (found during the same pass, but pre-existing and independent of the merge): `tests/general/tools/test_delete.py` (lines 40, 754, 763) and `tests/general/tools/test_update.py` (lines 1293, 1303) each also carry an un-flagged digit-form "12-value `type` enum" phrase not called out in either file's original task text (2.8/2.9) -- a reminder that each Phase 2 task requires a full word-and-digit re-grep of its own file at implementation time, not just the specific lines this plan happens to enumerate.

The merge also added net-new lines to four files this plan cites by exact line number: `set_classification.py` (+24 net lines), `set_status.py` (+24), `update.py` (+36), and `delete.py` (+34) -- all from newly-added cache-warming/invalidation calls, not from any change to the cardinal-number prose itself. Every line-number citation for these four files in this plan has been corrected accordingly (Design Notes above, Tasks 1.2-1.4). `_path_safety.py`, `_splice.py`, `create_adr.py`, `validate_adr.py`, `general/tools/__init__.py`, `validate.py`, `server.py`, and `rsk/tools/_sentinel.py` were not touched by the merge, so their existing citations remain accurate.

**Third-pass independent re-verification (REQ-012/REQ-013/REQ-014), performed via a fresh audit against the current repository state rather than against this plan's own prior citations.** Even after two review passes, one whole file and several stale spots inside already-in-scope files were still missing:

- `general/tools/_timestamps.py:34-35` ("the 11 `create_<d>` tools... and the 11 `set_status` adapter sites -- Task 3.3") was never in any prior file list; it is stale (12 `create_<d>` tools exist now, one per whole-body domain including `sysrs`) and is added to scope (Task 1.20).
- REQ-008's own "confirmed stale" list proved incomplete a second time: `general/tools/set_classification.py:46` ("ten whole-body domains'"), `general/tools/set_status.py:699` ("eleven whole-body domains"), `general/tools/update.py:47,786` ("the other ten's identical shape"/"ten UUID domains"), `general/tools/delete.py:42,411` ("ten UUID domains" x2), and `general/tools/__init__.py:44`'s own "ten flat domains" sub-phrase (inside the `delete` paragraph Task 1.1 already touches) are all stale and were not previously flagged for correction -- even though this Design Notes section's own opening paragraph already namechecked the `delete.py`/`update.py` "ten UUID domains" drift as illustrative motivation, that observation was never turned into an actionable REQ-008 item or task-level instruction until now. `tests/general/tools/test_update.py` also has two more stale spots beyond the two already tracked: line 20 ("ten whole-body document types", should be twelve) and line 1360 ("eleven whole-body domains, feat included", self-contradictory as written, should be twelve).
- The word "eleven" (and "ten") is used for two structurally different counts throughout this codebase: a *self-excluded relational* count ("the other eleven domains" = 12 total minus the domain describing itself -- correct as-is in `_cache.py`/`_sentinel.py`/`list_feat.py`/`_doc_paths.py`) and a *total-inclusive* count (e.g. ADR's own docs saying "the eleven whole-body domains" to mean all of them, since ADR itself is not one of the twelve -- wrong, should say twelve). A mechanical, blind numeric substitution across the codebase would fix one phrasing while breaking the other; REQ-014 records this as an explicit implementation-time judgment call, not a global search-and-replace.
- As a lower-cost due-diligence step, REQ-015/Task 3.2 adds a final grep across the six-to-nine cardinal-number range (word and digit form), since none of the three review passes so far specifically checked for an even-older stale reference predating `dec`/`sop`/`vcr`/`sysrs`'s additions.

Separately, and outside this feature's own scope: `.specmgr/conventions.md`'s `### Docstring Style` subsection's own example is written in Google-style (`Args:`/`Returns:`), while every file audited across all three review passes actually uses NumPy-style (`Parameters`/`Returns` with underlines) throughout. This pre-existing style-guide/practice mismatch is unrelated to the cardinal-number pattern this feature targets and is left unresolved here (noted for awareness only, see Explicitly Out Of Scope).

### Related Decisions

- ADR 36905d5b-8057-4294-8665-c7eed5534db0: establishes that a new document domain adds one dispatch entry to each generic tool (`update`/`set_status`/etc.) rather than a new per-domain tool; this feature applies the same anti-duplication spirit to prose, replacing hand-maintained domain counts with the domain list or dispatch table that already exists in code.

### Task List

#### Phase 1: Reword src/ and AGENTS.md docstrings, comments, and MCP tool description strings

- [ ] Task 1.1: Reword the four paragraphs (`update`, `set_status`, `set_classification`, `delete`) in `general/tools/__init__.py` -- per REQ-008, also correct the `update`/`set_classification`/`delete` paragraphs' domain lists to include `sysrs` (eleven -> twelve) and the `set_status` paragraph's count and list to include both `sysrs` and `adr` correctly (twelve -> thirteen), not just remove the adjective; also correct the same paragraphs' embedded "ten flat domains" sub-phrase (line 44, inside the `delete` paragraph) to "eleven" -- a sub-detail distinct from the top-level domain-list/count fix, found via REQ-012's third-pass review.

- [ ] Task 1.2: Reword `general/tools/set_classification.py`, including the digit-form "12-way"/"13-way" phrases (lines 25, 55, 174 as of the post-`dev`-merge line numbers; originally 25, 55, 162 before the merge shifted them, see Design Notes). Also correct line 46's "ten whole-body domains'" to "eleven" (found via REQ-012's third-pass review, not merely a destyle).

- [ ] Task 1.3: Reword `general/tools/set_status.py`, including the digit-form "13-way" phrases (lines 54, 211 as of the post-`dev`-merge line numbers; originally 54, 199 before the merge shifted them, see Design Notes). Also correct line 699's "eleven whole-body domains" to "twelve" (found via REQ-012's third-pass review, not merely a destyle).

- [ ] Task 1.4: Reword `general/tools/update.py`, including the digit-form "12-way" phrases (lines 42, 155 as of the post-`dev`-merge line numbers; originally 42, 143 before the merge shifted them, see Design Notes). Also correct line 47's "the other ten's identical shape" and line 786's "ten UUID domains" to "eleven" (found via REQ-012's third-pass review, not merely a destyle).

- [ ] Task 1.5: Reword `general/tools/delete.py` -- per REQ-008 (as expanded by REQ-012), also correct lines 42 and 411's "ten UUID domains" to "eleven", not merely destyle.

- [ ] Task 1.6: Reword `general/tools/validate.py`.

- [ ] Task 1.7: Reword `general/tools/_path_safety.py` -- per REQ-008, also correct `assert_uuid`'s docstring from "ten" to "twelve" `_UUID_TYPES` domains (the frozenset itself already has twelve entries; only the prose is stale).

- [ ] Task 1.8: Reword `server.py`.

- [ ] Task 1.9: Reword `general/resources/config.py`.

- [ ] Task 1.10: Reword `general/resources/__init__.py`.

- [ ] Task 1.11: Reword `feat/models/v1/summary.py`.

- [ ] Task 1.12: Reword `feat/tools/list_feat.py` -- the `dev` merge (REQ-011) added a second, digit-form occurrence ("...the other 11 whole-body domains'...") alongside the original word-form one; both must be reworded.

- [ ] Task 1.13: Reword `models/config_info.py`.

- [ ] Task 1.14: Reword `models/md/_frontmatter_parse.py`.

- [ ] Task 1.15: Reword `adr/tools/validate_adr.py` -- per REQ-008, also correct "eleven whole-body domains" to "twelve".

- [ ] Task 1.16: Reword `adr/tools/create_adr.py` -- per REQ-008, also correct "eleven whole-body domains" to "twelve".

- [ ] Task 1.17: Reword `general/tools/_splice.py` (per REQ-008, also correct "eleven `get_<d>` tools" to "twelve") and `rsk/tools/_sentinel.py` -- 2 files the issue's own audit missed, found via a fresh repo-wide grep.

- [ ] Task 1.18: Reword `AGENTS.md`'s 14 confirmed occurrences (REQ-009: 13 word-form plus 1 digit-form added by the `dev` merge's own `feat-107-doc-cache` paragraph); cross-check each against the current, actual domain count/list it describes rather than assuming the existing number is merely redundant (same caution as REQ-008).

- [ ] Task 1.19: Reword the 3 `src/` files found by the post-`dev`-merge re-audit (REQ-011): `general/tools/_doc_paths.py`, `feat/tools/_cache.py`, and `req/tools/_cache.py`. All three already carry the correct domain count -- destyling only, no factual correction needed.

- [ ] Task 1.20: Reword `general/tools/_timestamps.py`'s stale digit-form phrase at lines 34-35 ("the 11 `create_<d>` tools... and the 11 `set_status` adapter sites") -- a file missing from every prior file list, found only by REQ-012's third-pass re-audit; correct the counts to reflect the current 12 `create_<d>` tools / 12 `set_status` adapter sites, not merely destyle.

- [ ] Task 1.21: Regenerate `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md` via `specmgr docs`/`specmgr mcp-docs`; confirm a clean `git status` diff.

- [ ] Task 1.22: Run the full quality gate (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, `pytest -n auto`).

#### Phase 2: Reword tests/ docstrings and comments

- [ ] Task 2.1: Reword `tests/sysrs/models/v1/test_parser.py`.

- [ ] Task 2.2: Reword `tests/general/resources/test_config.py`.

- [ ] Task 2.3: Reword `tests/general/models/test_summary.py`.

- [ ] Task 2.4: Reword `tests/general/tools/test_set_classification.py`.

- [ ] Task 2.5: Reword `tests/general/tools/test_validate.py`, including the digit-form "12-way" phrase (line 21).

- [ ] Task 2.6: Reword `tests/general/tools/test__path_safety.py`.

- [ ] Task 2.7: Reword `tests/general/tools/test_set_status.py`.

- [ ] Task 2.8: Reword `tests/general/tools/test_delete.py`.

- [ ] Task 2.9: Reword `tests/general/tools/test_update.py`, reconciling the different counts ("ten", "twelve", "eleven") mixed across its docstrings -- per REQ-008, "ten UUID domains" (lines 604, 1338) is factually stale and must become "eleven" (twelve whole-body domains minus `feat`), not just be destyled. Two further spots were missing from this task's original line-number citations, found via REQ-012's third-pass review: line 20's "ten whole-body document types" is stale and must become "twelve" (not eleven -- a different fix direction than the UUID-domain spots, since this phrase is a total-inclusive count, not a self-excluded one), and line 1360's "eleven whole-body domains, feat included" is self-contradictory as written and must become "twelve".

- [ ] Task 2.10: Reword `tests/feat/tools/test_list_feat.py`.

- [ ] Task 2.11: Reword `tests/commands/test_schema.py` -- found via the follow-up audit, missed by the issue's original list.

- [ ] Task 2.12: Reword `tests/general/tools/test_error_context.py` -- found via the follow-up audit, missed by the issue's original list.

- [ ] Task 2.13: Reword `tests/models/md/test_frontmatter_errors.py` -- found via the follow-up audit, missed by the issue's original list.

- [ ] Task 2.14: Reword `tests/adr/tools/test_create_adr.py` -- matches only in digit form ("the 11 whole-body domains"), which is why the original word-only grep missed this file; reword to "twelve".

- [ ] Task 2.15: Reword `tests/general/tools/test_doc_cache_structural.py` and `tests/general/tools/test_doc_cache_delete_scan_race.py` -- 2 brand-new test files found by the post-`dev`-merge re-audit (REQ-011); both already carry correct domain counts, destyling only. While in these files, also verify Tasks 2.8 (`test_delete.py`, digit-form "12-value `type` enum" at lines 40, 754, 763) and 2.9 (`test_update.py`, same phrase at lines 1293, 1303) each catch that additional un-flagged digit-form occurrence, not just the lines their own task text enumerates.

- [ ] Task 2.16: Run the full quality gate again after the Phase 2 edits.

#### Phase 3: Codify the convention

- [ ] Task 3.1: Add a rule to `.specmgr/conventions.md`'s `### Docstring Style` subsection (nested under `## Additional Best Practices`, not the unrelated top-level `## Documentation Requirements` section) stating that a generic tool's supported-domain count must not be restated as a cardinal number in prose (word or digit form); use explicit domain lists or relational phrasing instead.

- [ ] Task 3.2: Run a final full quality-gate pass and confirm `specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc` produce zero diff. Also run a final broadened grep across `src/`, `tests/`, and `AGENTS.md` for the cardinal numbers six/seven/eight/nine (word and digit form), confirming no older, undetected stale domain-count reference remains from before `dec`/`sop`/`vcr`/`sysrs` were added (REQ-015).

## Progress

### Current Status

**As of 2026-09-11**: Feature drafted from GitHub issue #122; no code changes have been made yet. A follow-up verification pass (documented in Design Notes) expanded and corrected the original issue-derived scope before implementation started: added `AGENTS.md` (13 occurrences, REQ-009) and 4 more `tests/` files (3 missed by the original word-only grep, 1 matching only in digit form) to scope, and identified 6 specific spots (REQ-008) where the existing count/domain list is not merely redundant but factually stale (missing `sysrs`), requiring an actual correction rather than a cosmetic destyle.

After that review, `dev` was merged into this branch (bringing in `feat-107-doc-cache`, GitHub issue #107, an 80-file per-domain read-cache change), and a second, post-merge re-audit (REQ-011) found the merge had introduced further occurrences of the same pattern, plus shifted several previously-cited line numbers. Scope grew again: `src/` from 18 to 21 files (+`general/tools/_doc_paths.py`, `feat/tools/_cache.py`, `req/tools/_cache.py`), `tests/` from 14 to 16 files (+`test_doc_cache_structural.py`, `test_doc_cache_delete_scan_race.py`), and `AGENTS.md` from 13 to 14 occurrences (a digit-form count inside the merge's own new paragraph). Phase 1 was 21 tasks (was 20, before that 19), Phase 2 was 16 tasks (was 15, before that 11) covering 16 files (was 14, before that 10), and Task 1.2/1.3/1.4's line-number citations were corrected for the four files (`set_classification.py`, `set_status.py`, `update.py`, `delete.py`) whose content the merge shifted. Phase 3's Task 3.1 still points at the correct `.specmgr/conventions.md` subsection. Phase 2 remains tracked at full priority, not as an optional lower-priority addendum, since the full test suite must run in any case.

A third gap review, requested by the user and performed as an independent re-verification against the current repository state (not against this plan's own prior citations), found the plan was still incomplete in two ways even after the two reviews above: one entire file (`general/tools/_timestamps.py`) had never been added to scope, and REQ-008's "confirmed stale" list -- despite already having been revised twice -- was still missing at least eight stale spots inside files already in scope (`set_classification.py`, `set_status.py`, `update.py` x2, `delete.py` x2, `general/tools/__init__.py`'s own embedded "ten flat domains" sub-phrase, and two further spots in `tests/general/tools/test_update.py`). It also surfaced a subtler risk the plan had not previously documented: the words "eleven"/"ten" carry two different meanings depending on phrasing (self-excluded relational vs. total-inclusive), so a careless mechanical fix could introduce new drift of the exact kind this feature exists to remove. Added REQ-012/REQ-013/REQ-014/REQ-015, ACC-009/ACC-010, expanded REQ-008 and the Scope section, expanded Tasks 1.1-1.5 and 2.9 with the newly found spots, inserted Task 1.20 (renumbering the former 1.20/1.21 doc-regen/quality-gate tasks to 1.21/1.22), and appended a final broadened low-number grep to Task 3.2. No code changes have been made in any of the three review passes; all are planning-only.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-11 03:00:00.000Z - Third gap review (independent repository re-verification) found REQ-008 was still incomplete, a missing file, and a phrase-ambiguity risk

A third gap review, run independently against the current repository state via a fresh audit (word-form and context-filtered digit-form greps across `src/`, `tests/`, and `AGENTS.md`, plus direct reads of every file/line this plan already cited), found the plan was still incomplete even after two prior review passes: (1) `general/tools/_timestamps.py:34-35` carries a stale digit-form "the 11 `create_<d>` tools... and the 11 `set_status` adapter sites" phrase and was missing from every prior file list -- added to Scope and as Task 1.20 (renumbering the former Task 1.20/1.21 doc-regen/quality-gate tasks to 1.21/1.22); (2) REQ-008's own "confirmed stale" list, despite two prior revisions, still missed at least eight stale spots inside files already in scope: `general/tools/set_classification.py:46`, `general/tools/set_status.py:699`, `general/tools/update.py:47,786`, `general/tools/delete.py:42,411`, `general/tools/__init__.py:44`'s own embedded "ten flat domains" sub-phrase, and `tests/general/tools/test_update.py:20,1360` -- all folded into REQ-008 and the relevant Tasks (1.1-1.5, 2.9), even though this plan's own Design Notes had already namechecked the `delete.py`/`update.py` "ten UUID domains" drift as illustrative motivation without ever turning it into an actionable item; (3) a previously-undocumented implementation risk was identified and recorded as REQ-014: "eleven"/"ten" are used for two structurally different counts throughout the codebase (a self-excluded relational count, correct as-is in several already-in-scope files, versus a total-inclusive count, wrong in ADR's own docs and the UUID-domain spots), so a mechanical global find/replace would silently break one phrasing while fixing the other; (4) as a cheap due-diligence addition, REQ-015 adds a final six-to-nine cardinal-number grep to Task 3.2, since none of the three review passes had specifically checked for an even-older stale reference predating `dec`/`sop`/`vcr`/`sysrs`. Also noted, as an explicit Out-of-Scope callout rather than a silent observation: `.specmgr/conventions.md`'s own `### Docstring Style` example is Google-style while the codebase actually uses NumPy-style throughout -- unrelated to this feature, left as-is. Added REQ-012/REQ-013/REQ-014/REQ-015, ACC-009/ACC-010, broadened ACC-007's cross-check requirement to cover every occurrence touched (not only the pre-identified list), and updated Scope/Design Notes/Current Status accordingly. No code changes were made in this pass; it is a planning-only refinement, done before any Phase 1 implementation started.

#### 2026-09-11 02:00:00.000Z - Scope re-audited after merging dev (feat-107-doc-cache)

A second gap review, requested after `dev` was merged into this branch, checked whether the merge had opened up new occurrences of the pattern or invalidated anything already in the plan. It had, on both counts. The merge brought in `feat-107-doc-cache` (GitHub issue #107, an 80-file change adding a per-domain read cache to all 12 whole-body domains), which: (1) added 3 new `src/` files carrying the same cardinal-number pattern -- a substantially-rewritten pre-existing file (`general/tools/_doc_paths.py`) and two brand-new files (`feat/tools/_cache.py`, `req/tools/_cache.py`) -- none of which the original audit could have found since the content didn't exist yet; all three already state the correct count and need destyling only, not a factual fix; (2) added a second, digit-form occurrence to `feat/tools/list_feat.py` (Task 1.12), a file already in scope, alongside its pre-existing word-form one; (3) added 2 new, brand-new `tests/` files (`test_doc_cache_structural.py`, `test_doc_cache_delete_scan_race.py`) carrying 6 and 4 occurrences respectively; (4) added a digit-form occurrence to `AGENTS.md` inside the very paragraph the merge itself contributed to that file, describing the merge's own feature -- bumping AGENTS.md's REQ-009 count from 13 to 14; and (5) added net-new lines to `set_classification.py`, `set_status.py`, `update.py`, and `delete.py` (24-36 lines each, all cache-warming/invalidation calls), shifting every line number Tasks 1.2/1.3/1.4 and the Design Notes previously cited for those four files' digit-form phrases and `Literal[...]` cross-checks -- corrected in place rather than left to go stale. Also found, independent of the merge: `tests/general/tools/test_delete.py` and `tests/general/tools/test_update.py` (both already in scope) each carry an additional, previously-un-flagged digit-form "12-value `type` enum" phrase not called out in their task text -- noted as a reminder in Task 2.15 that each Phase 2 task needs its own full re-grep at implementation time. Added REQ-011/ACC-008, updated REQ-009/Scope/Task 1.2/1.3/1.4/1.12/1.18, inserted Task 1.19 (new src files, renumbering the former 1.19/1.20 doc-regen/quality-gate tasks to 1.20/1.21) and Task 2.15 (new test files, renumbering the former 2.15 quality-gate task to 2.16), and reconciled a minor pre-existing ACC-002/Task 3.2 inconsistency (ACC-002 now also mentions the `specmgr adr-toc` check Task 3.2 already ran). No code changes were made in this pass; it is a planning-only refinement, done before any Phase 1 implementation started.

#### 2026-09-11 01:00:00.000Z - Scope refined following a pre-implementation gap review

A gap/inconsistency review of the freshly-drafted plan, run before any implementation started, found and corrected four categories of issues: (1) the `tests/` file audit was incomplete -- 3 files with word-form matches (`tests/commands/test_schema.py`, `tests/general/tools/test_error_context.py`, `tests/models/md/test_frontmatter_errors.py`) and 1 with a digit-form-only match (`tests/adr/tools/test_create_adr.py`, "the 11 whole-body domains") were missing from Phase 2's list, even though REQ-001 already covered digit form; (2) `AGENTS.md` -- the repo's single most authoritative, actively-maintained reference, and the same doc the feature's own Overview cites -- carried 13 occurrences of the identical pattern but was absent from scope entirely; added as REQ-009/ACC-006/Task 1.18; (3) REQ-002's "just drop the adjective, keep the list as-is" premise was verified false for 6 confirmed spots (`general/tools/__init__.py`'s four dispatch-tool paragraphs, `_path_safety.py`'s `assert_uuid` docstring, `_splice.py`'s `get_<d>` count, `create_adr.py`/`validate_adr.py`'s "eleven whole-body domains") where the existing list/count is missing `sysrs` and is therefore factually wrong, not just redundant -- added REQ-008/ACC-007 and updated the affected tasks (1.1, 1.2, 1.3, 1.4, 1.7, 1.15, 1.16, 1.17, 2.9) to require an actual correction, cross-checked against the `Literal[...]`/constant/tool-count each describes; (4) Task 3.1 named "`.specmgr/conventions.md`'s Documentation Requirements/Docstring Style section" as if it were one section, when `### Docstring Style` is actually nested under the unrelated `## Additional Best Practices`, not under `## Documentation Requirements` -- reworded to point unambiguously at `### Docstring Style`. Also added REQ-010/an Explicitly-Out-Of-Scope bullet explicitly excluding `CHANGELOG.md`/`docs/adr/`/`docs/gol/`/`docs/req/`/`docs/sysrs/` (historical/point-in-time records) and QA's own unrelated "ten fixed category headings" wording, so these exclusions are now a stated decision rather than a silent gap. No code changes were made in this pass; it is a planning-only refinement.

#### 2026-09-11 00:00:00.000Z - Created

Feature drafted from GitHub issue #122 ("Stop restating hardcoded domain/type counts in prose docstrings and comments"), discovered during feat-120-remove-confluence verification. Scope mirrors the issue's three phases, with Phase 2 (tests/ cleanup) tracked at full priority rather than as an optional lower-priority addendum, per user direction. Phase 1 scope expanded from the issue's 16 files to 18 after a follow-up grep found 2 more matching files (`general/tools/_splice.py`, `rsk/tools/_sentinel.py`) the issue's own audit missed. Kept the 3-phase structure rather than splitting further by file count, since the measured scope (80 occurrences across 18 files, mechanical one-word/one-phrase edits) is smaller than precedent single-phase/single-task batches already completed successfully in this repo (feat-38-39-41-43-44's Phase 3: 44 sites across ~13 files; Phase 5: 39 files), and no code changes made this a candidate for a heavier phase-implementer context load.
