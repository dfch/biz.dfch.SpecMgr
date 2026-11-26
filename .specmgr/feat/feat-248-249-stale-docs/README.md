---
classification: null
created: '2026-11-22T15:43:46.858+01:00'
id: feat-248-249-stale-docs
status: progress
type: feat
updated: '2026-11-26T13:19:28.000+01:00'
version: 1.0.0
---

# Feature: Stale PRB Recovery Directive and Missing req/gol Model API Docs

## Plan

### Overview

Two small, independent documentation-surface defects surfaced during feat-173-req-iso29148-level-set and tracked as GitHub issues #248 and #249, bundled into one feature because each is a one-phase fix.

Issue #248: the "Old-shape recovery" block in `prb/data/prb_update_instructions.md` tells the agent to re-read an unparseable PRB via `get_prb(id, raw=True)` and to repair it via the generic `update` tool. Both claims are false against current behavior: `get_prb` resolves the id through a full parse first and returns the non-raising `ParseFailureResult` before the `raw` branch is reached (feat-150, DEC 9080b37c-82b3-4f63-81f1-79641d0bf14c), and `update`/`edit` re-parse the existing document and return the same result without writing (feat-170, DEC b8c9bfea-6dcf-4158-bfc5-4ec17abb842f). An agent following the directive cannot recover exactly the documents it exists for. The `req` directive shipped in FEAT feat-173-req-iso29148-level-set (commit `dbd754ee`, merged via PR #254 as `83be6624`) already carries the correct host-file-tool mechanism and is the model text.

Issue #249: `src/biz/dfch/specmgr/req/models/` and `src/biz/dfch/specmgr/gol/models/` have no `__init__.py`, so they are namespace packages. The `specmgr docs` generator's `pkgutil.walk_packages` walk does not descend into them, so no `docs/api/` page for any `req.models.v1.*` or `gol.models.v1.*` module has ever been emitted -- and the `specmgr docs` drift check cannot detect what the walk never emits.

### Requirements

- REQ-001: The "Old-shape recovery" block in `prb/data/prb_update_instructions.md` uses the host-file-tool repair mechanism: a `get_prb(id)` parse failure naming the missing lead sentence is not fatal; no specmgr read returns the body of an unparseable document, so the raw file is read with the host's own file-read tool at the `path` the parse-failure result carries; the derive/confirm flow runs on that text; the repaired file is written back with the host's own file-write tool (the generic `update`/`edit` tools cannot repair one); a confirming `get_prb(id)` call must parse before the requested change proceeds. The repair write follows the `repair` prompt's rule: the frontmatter block (including `id`/`created`/`status`/`version`) stays byte-for-byte unchanged and `updated` is left untouched, because a repair is not an edit; the originally requested change that follows goes through `update`, which bumps `updated` itself.
- REQ-002: The rewritten PRB recovery block is present tense only (no change-history phrasing) and keeps the existing derive/confirm/insert-under-H1 content of steps 2-3 intact.
- REQ-003: `tests/prb/prompts/test_update_prb.py::test_mentions_old_shape_recovery_via_raw_reread` no longer pins the false `get_prb(id, raw=True)` mechanism; it asserts the corrected wording, mirroring `tests/req/prompts/test_update_req.py::test_mentions_legacy_level_recovery_directive`. Its negative assertions (no `get_prb(id, raw=True)`, no `update(id, type="prb", content)` as the repair write) run only on the recovery-block slice -- the text between `**Old-shape recovery.**` and `## 2. If no change was specified` -- because the rest of the prompt legitimately keeps `update(id, type="prb", content)` (pinned by `test_mentions_both_generic_mutation_tools`) and `get_prb(id, raw=True, numbered=True)` (pinned by `test_mentions_range_update_flow`). The rewrite keeps every phrase pinned by `test_mentions_deriving_or_eliciting_lead_sentence_blanks` (`derive-then-confirm`, `` `What` -> both `[Current state]` and ``, `` `Who` -> `[stakeholder]` ``, `` `Why` -> ``, `[underlying cause]`) and by `test_mentions_inserting_sentence_under_h1_then_proceeding` (`Insert the confirmed sentence as its own paragraph directly under the`, `H1 title`, `proceeding to step 2 below with the originally requested change`), so both tests pass unchanged.
- REQ-004: `src/biz/dfch/specmgr/req/models/__init__.py` and `src/biz/dfch/specmgr/gol/models/__init__.py` exist, in the docstring-only shape of `prb/models/__init__.py`/`tsk/models/__init__.py` (license header plus package docstring; no import from `.v1`, no `__all__`), so no new import edge or import-cycle risk is introduced and `whitelist.py` needs no change. The `req/models` docstring describes the versioned-sub-package layout, so `tsk/models/__init__.py`'s existing "Mirrors ``req/models``'s layout" cross-reference becomes true; the `gol/models` docstring follows the same wording.
- REQ-005: `specmgr docs` emits `docs/api/` pages for every `req.models.v1.*` and `gol.models.v1.*` module, and the regenerated pages land in the same commit as the `__init__.py` files.
- REQ-006: A regression test fails if any directory on the path between `src/biz/dfch/specmgr/` (inclusive) and a git-tracked `.py` file under it -- every ancestor directory, not only the file's own parent -- lacks an `__init__.py` (the implicit namespace roots `src/biz/` and `src/biz/dfch/` are outside its scope). The every-ancestor rule is required: `req/models/` and `gol/models/` contain no `.py` file of their own (only the `v1/` subpackage, which has an `__init__.py`), so a parent-directory-only check reports zero missing directories even before the fix.
- REQ-007: Both fixes carry `CHANGELOG.md` `[Unreleased]` entries (housekeeping).

### Acceptance Criteria

- [x] ACC-001: `prb/data/prb_update_instructions.md` no longer contains `get_prb(id, raw=True)` in its recovery block, and does not instruct `update(id, type="prb", content)` as the repair write; it names the host file-read/file-write tools, the parse-failure `path`, and the confirming `get_prb(id)` call; a grep of the added agent-facing lines for the change-history words `previously`, `now`, `instead of`, `formerly`, `used to be` returns no match (REQ-001, REQ-002).
- [x] ACC-002: The updated `test_update_prb.py` recovery test passes and fails against the old wording; its negative assertions are scoped to the recovery-block slice; `test_mentions_deriving_or_eliciting_lead_sentence_blanks` and `test_mentions_inserting_sentence_under_h1_then_proceeding` pass unchanged (REQ-003).
- [x] ACC-003: `uv run --frozen specmgr docs` produces, for each of `req` and `gol`, the `docs/api/` pages `biz.dfch.specmgr.<d>.models`, `biz.dfch.specmgr.<d>.models.v1`, and `biz.dfch.specmgr.<d>.models.v1.{_util,body,document,frontmatter,parser,summary}` (the exact set is confirmed against the `v1/` module listing at implementation time), committed; a second run shows no diff (REQ-004, REQ-005).
- [x] ACC-004: The namespace-package guard test passes on the branch and fails if either new `__init__.py` is removed -- demonstrated once by temporarily deleting `req/models/__init__.py` and observing the red run, recorded in the Progress update (REQ-006).
- [x] ACC-005: The full quality gate passes: `ruff format --check`, `ruff check`, `vulture`, the full `pytest -n auto` suite, and the doc/schema/mcp-docs drift checks (process criterion; REQ-007 covers the CHANGELOG housekeeping). (maintainer-accepted exception: the full suite runs 6117 passed / 2 failed locally -- the 2 failures are the Docker/Structurizr export tests in tests/evals/test_cli_gates.py, which fail identically on the base commit 9c9d7349; GitHub CI is green)
- [x] ACC-006: Import smoke check: `import biz.dfch.specmgr.req.models` and `import biz.dfch.specmgr.gol.models` succeed, and `importlib.util.find_spec(...)` reports each as a regular package (`origin` is its `__init__.py`, not a namespace portion) (REQ-004).

### Scope

#### Included

- Rewrite of the PRB "Old-shape recovery" block and its pinning test (issue #248).
- The two missing `models/__init__.py` files, the `specmgr docs` regeneration, and the namespace-package guard test (issue #249).
- `CHANGELOG.md` `[Unreleased]` entries for both fixes.

#### Explicitly Out Of Scope

- Changing `get_<d>(raw=True)` to return the body of an unparseable document (the `ParseFailureResult` channel is the intended contract).
- Any change to the `specmgr docs` generator's walk itself (the fix is regular packages, not namespace-package support in the walk).
- The stale, untracked `adr/` and `models/adr/` directories in local checkouts (only `__pycache__` content, not git-tracked).
- Recovery directives of any domain other than PRB.

### Dependencies

#### Depends On

- FEAT feat-150-mcp-lifecycle-commands (the `ParseFailureResult` channel of `get_<d>`, the host-file `repair` idiom).
- FEAT feat-170-update-edit-parse-failure (the `update`/`edit` non-raising parse-failure channel).
- FEAT feat-173-req-iso29148-level-set (commit `dbd754ee`, merged via PR #254, the model `req` recovery directive text).

### Design Notes

- PRB model text: the "Legacy `## Level` value recovery." block in `req/data/req_update_instructions.md` -- its steps 2-3 (host file-read at the parse-failure `path`; host file-write, because `update`/`edit` re-parse first) are transplanted; PRB's own derive/confirm/insert steps stay, re-pointed from "the raw body text from step 1" to the raw file text. The raw file includes the YAML frontmatter, so the insert instruction must say "directly under the H1" in file terms and leave the frontmatter byte-unchanged, `updated` included (see REQ-001).
- The `models/__init__.py` shape is docstring-only, following `prb/models/__init__.py`/`tsk/models/__init__.py` (not the re-exporting `dec`/`rsk`/`sop`/`vcr`/`txt`/`set`/`uc` variant). Existing `req.models.v1`/`gol.models.v1` importers keep working because a regular package is a strict superset of the namespace import path for a single portion, and with no import in the new files there is no new cycle edge.
- The guard test enumerates files from `git ls-files 'src/biz/dfch/specmgr/**/*.py'` (not a filesystem walk) so untracked `__pycache__`-only leftovers in a local checkout cannot make it flaky, then checks every ancestor directory of each file up to and including `src/biz/dfch/specmgr/` (REQ-006) -- not only each file's own parent.

### Related Decisions

- DEC 9080b37c-82b3-4f63-81f1-79641d0bf14c -- `get_<d>` non-raising `ParseFailureResult` channel.
- DEC b8c9bfea-6dcf-4158-bfc5-4ec17abb842f -- generic `update`/`edit` non-raising parse-failure channel.
- DEC ece4554b-725c-4f76-bc04-5d2b760363d2 -- domain-first layout (schemas under `<domain>/models/vN/`).
- DEC 9c687bb1-8ee7-41c8-84ec-07606356bc73 -- docs/lint/tests enforced via pre-commit.

DEC 9080b37c and DEC b8c9bfea parse cleanly with the worktree code (`specmgr lint` on both: `linted=2 failed=0`); the `ParseFailureResult` seen during refinement came from an older connected MCP server build, not from the documents.

### Task List

#### Phase 100: PRB recovery directive (issue #248)

- [x] Task 100.100: Rewrite the "Old-shape recovery" block in `src/biz/dfch/specmgr/prb/data/prb_update_instructions.md` to the host-file-tool mechanism (REQ-001, REQ-002).
- [x] Task 100.110: Update `tests/prb/prompts/test_update_prb.py::test_mentions_old_shape_recovery_via_raw_reread` to assert the corrected wording and reject the old mechanism on the recovery-block slice only; confirm `test_mentions_deriving_or_eliciting_lead_sentence_blanks` and `test_mentions_inserting_sentence_under_h1_then_proceeding` still pass unchanged (REQ-003).
- [x] Task 100.120: Confirm `docs/MCP.md`, `src/biz/dfch/specmgr/general/data/general_harness_bundle.json`, and `.opencode/` embed no copy of the PRB recovery block (expected: 0 matches for `Old-shape recovery` / `prb_update_instructions`, as verified at refinement) (REQ-001).
- [x] Task 100.130: Run the phase-end quality gate.

#### Phase 110: req/gol models regular packages (issue #249)

- [x] Task 110.100: Add the docstring-only `src/biz/dfch/specmgr/req/models/__init__.py` and `src/biz/dfch/specmgr/gol/models/__init__.py` (REQ-004).
- [x] Task 110.110: Add the namespace-package guard test (every-ancestor check over git-tracked `src/biz/dfch/specmgr/` `.py` files) and demonstrate it red with `req/models/__init__.py` temporarily removed (REQ-006, ACC-004).
- [x] Task 110.120: Regenerate `specmgr docs`, commit the new `docs/api/` pages and `docs/GENERATED.md` changes -- expected diff: the new `req`/`gol` model pages and module entries, plus the **Test files** count rising from 502 by the new guard test file (REQ-005, ACC-003).
- [x] Task 110.130: Run the phase-end quality gate, including vulture and the ACC-006 import smoke check; confirm `whitelist.py` and `AGENTS.md` need no change (AGENTS.md's "Its schema lives at `req/models/v1/`" stays true) (ACC-006, ACC-005).

#### Phase 120: Close-out

- [x] Task 120.100: Add `CHANGELOG.md` `[Unreleased]` entries for #248 and #249 (REQ-007).
- [x] Task 120.110: Tick acceptance criteria, update Progress, open the PR against `dev` referencing both issues. (Criteria ticked and Progress updated; the PR is opened by the orchestrator after status `review` is set.)

#### Phase 130: Fix phase (review cycle 1: G1/D1/D2/S1/S2/I1-I3)

- [x] Task 130.100: G1 -- the `prb_update_instructions.md` preamble names the "Old-shape recovery" block as the one exception to "every change goes through the specmgr MCP tools" (host file tools, frontmatter byte-unchanged); `req/data/req_update_instructions.md` is out of scope (follow-up issue #273).
- [x] Task 130.110: D1/D2 -- reword the `update_prb` MCP prompt `description` ("via a raw re-read") and the module docstring (`AssertionError`, "now") to the host file-read/file-write repair and the non-raising `ParseFailureResult` (DEC 9080b37c-82b3-4f63-81f1-79641d0bf14c); grep the repo for other PRB "raw re-read" recovery phrasing; regenerate `docs/MCP.md` and `docs/api/`.
- [x] Task 130.120: I1/I3 -- add a `validate(type="prb", content=<the full raw file text>, full=True)` dry-run loop step between the insert and the write-back in the recovery block, renumber the steps, and rewrap the long unwrapped recovery-block lines without splitting any test-pinned phrase.
- [x] Task 130.130: S1/I2 -- rename `test_mentions_old_shape_recovery_via_raw_reread` to `test_mentions_old_shape_recovery_via_host_file_repair`, assert the validate step, and add `assertLess` order checks (file-read < insert < validate < file-write < confirming `get_prb(id)`); show it red against the Phase 100 instructions file.
- [x] Task 130.140: S2 -- explicit `check=False` on the probe `subprocess.run` in `tests/test_no_namespace_packages.py` `setUp`.
- [x] Task 130.150: Run the phase-end quality gate.

#### Phase 140: Fix phase (review cycle 2: E1/G1/D1/S1/S2/I1/I2)

- [x] Task 140.100: E1 -- the `docs/api/biz.dfch.specmgr.req.models.v1.body.md` and `docs/api/biz.dfch.specmgr.gol.models.v1.body.md` pages carried the pre-feat-253 inherited `models/md` docstring text (`mdformat.text()`) once `dev` was merged; done in the merge commit `01d1722e` (merge of `origin/dev` at `48c5d3e5`, `CHANGELOG.md` conflict resolved by keeping both sides, `specmgr docs` regenerated, both pages hold 0 `mdformat.text()` matches, **Test files** count 509).
- [x] Task 140.110: G1 -- record the `dev` merge in this plan: add an Updates entry naming the merge commit `01d1722e`, the `CHANGELOG.md` resolution, the `specmgr docs` regeneration of the two req/gol body pages, and the **Test files** count 509 (502 at base + 6 from `dev` + 1 from this feature); add `01d1722e` to Related PRs / Commits. Leave Task 110.120 and the Phase 110 entry ("502 -> 503") as written -- they are historical.
- [x] Task 140.120: D1 -- in `src/biz/dfch/specmgr/prb/data/prb_update_instructions.md`, reword the "Old-shape recovery" trigger ("returns a parse failure because the body is missing the mandatory lead sentence") so it names what the parse-failure `error` actually contains: the `problem_statement` field (actual messages: `Prb > problem_statement: expected MarkdownParagraph, found no match ...` when the lead paragraph is absent, `problem_statement must match the template` when the first paragraph does not follow the template). Model text: the "whose error names the `## Level` value" trigger in `req/data/req_update_instructions.md`. Keep every test-pinned phrase intact; extend `tests/prb/prompts/test_update_prb.py::test_mentions_old_shape_recovery_via_host_file_repair` to assert `problem_statement` on the recovery-block slice. Present tense only.
- [x] Task 140.130: S2 -- in the same file's preamble, make the recovery-block exception cover both prohibitions explicitly: "Do not write raw markdown yourself beyond the body content you pass to `update`" and "every change to the document goes through the specmgr MCP tools" (today the exception clause hangs off the second only).
- [x] Task 140.140: S1 -- rewrap the overlong physical lines this branch added to match the surrounding wrap width (about 78 columns): the `update_prb` module docstring and MCP `description` in `src/biz/dfch/specmgr/prb/prompts/update_prb.py` (reported at lines 29 and 92), the #248 bullet in `CHANGELOG.md` `[Unreleased]` -> `### Fixed` (the line ending "`tests/prb/prompts/test_update_prb.py` pins the corrected"), and the edited `prb/` bullet in `AGENTS.md` (reported at line 265). Find them via `git diff 9c9d7349..HEAD` on those files; change wrapping only, not wording; do not split a test-pinned phrase.
- [x] Task 140.150: I1 -- in `tests/test_no_namespace_packages.py`, `skipTest` (instead of failing `assertTrue(files, ...)`, around line 86) when `git ls-files` returns no tracked file under `src/biz/dfch/specmgr/` (an unpacked sdist nested inside an unrelated git work tree).
- [x] Task 140.160: I2 -- in `src/biz/dfch/specmgr/tsk/models/__init__.py` (lines 19-21) and `src/biz/dfch/specmgr/prb/models/__init__.py` (lines 19-22), replace the stale "(in a later phase) the document wrapper and parser" with present-tense wording matching the new `req/models`/`gol/models` docstrings. Regenerate `specmgr docs` afterwards (the docstrings render into `docs/api/`).
- [x] Task 140.170: Run the phase-end quality gate: `ruff format --check`, `ruff check`, `vulture`, the full `pytest -n auto` suite, `specmgr docs`/`mcp-docs`/`harness-bundle` with no diff after the commit (`specmgr docs` run once, after Tasks 140.120-140.160), the `specmgr-docs-test-count` hook, and `specmgr lint` on this README; record the results in an Updates entry and update Current Status. Do not push or merge.

## Progress

### Current Status

**As of 2026-11-26**: Phases 100-130 committed (`22a84b33`, `232512e1`, `fd41f554`, `142db7c3`); `origin/dev` (`48c5d3e5`) merged into the branch as `01d1722e`. Phase 140 (review cycle 2, Tasks 140.100-140.170) is implemented and gate-green: Task 140.100 was done in the merge, Tasks 140.110-140.170 in this phase's working tree. The Phase 140 commit will be made by the orchestrator after verification, which then sets the status to `review` and pushes; its hash is deliberately not cited here. PR #271 is open against `dev` and not merged. The same preamble contradiction in `req/data/req_update_instructions.md` remains tracked as GitHub issue #273.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-26T12:18:49.000Z - Phase 140 implemented (review cycle 2)

Implemented Tasks 140.110-140.170 (Task 140.100 was already done in the merge, recorded in the entry below). D1: the "Old-shape recovery" trigger in `prb/data/prb_update_instructions.md` now reads "If `get_prb(id)` returns a parse failure whose error names the `problem_statement` field (the body is missing the mandatory lead sentence directly under the H1, or the first paragraph does not match the template), do not treat this as a fatal error:" (model: the `req` trigger's "whose error names the `## Level` value"), present tense; both test-pinned phrases stay contiguous on one line each, the verbatim derive-mapping clause and the composed-sentence code span are untouched, and `test_mentions_old_shape_recovery_via_host_file_repair` additionally asserts `problem_statement` on the recovery-block slice (verified: passes on the new text, fails on the old trigger via a patched scratch read). S2: the preamble's "with one exception" clause now covers both prohibitions explicitly ("Do not write raw markdown yourself beyond the body content you pass to `update`, and every change to the document goes through the specmgr MCP tools listed below -- with one exception: ..."). S1: rewrapped the seven branch-added physical lines over 78 columns to <= 78 with wrapping only (verified whitespace-normalized-identical wording, and the MCP `description`'s concatenated value byte-identical): `update_prb.py`'s module docstring (the "no `specmgr://prb/{id}` resource" passage) and its `description` literals (nine literal lines, all <= 78), the `CHANGELOG.md` #248 bullet (the confirming `get_prb(id)` call line and the "`tests/prb/prompts/test_update_prb.py` pins the corrected" line) and #249 bullet (the `.models.v1` long-token line), and the `AGENTS.md` `prb/` bullet (the "then proceed" line); the `origin/dev`-arrived overlong AGENTS.md line (the `check_generated_test_count.py` pre-commit sentence) was left untouched per the boundary note. I1: `test_every_ancestor_directory_has_init` in `tests/test_no_namespace_packages.py` now `skipTest`s (message naming the unpacked-sdist-in-an-unrelated-git-work-tree condition) when `git ls-files` finds no tracked file under `src/biz/dfch/specmgr/` (verified: skip on the empty case, still a failure when a directory lacks `__init__.py`, 2 passed on the repo). I2: `tsk/models/__init__.py` and `prb/models/__init__.py` now say "the frontmatter/body classes, the document wrapper, and the parser" (present tense, matching `req/models`/`gol/models`); `qa/models` untouched. G1: the merge record below. Gate: `ruff format --check` (2411 files already formatted), `ruff check` (All checks passed), `vulture src/ whitelist.py --min-confidence 60` (rc 0), full `pytest -n auto` -> **6158 passed, 18 skipped, 0 failed** (the 2 environmental Docker/Structurizr export tests in `tests/evals/test_cli_gates.py` passed this run, so the failure set did not grow), `python scripts/check_generated_test_count.py` (rc 0). `specmgr docs` (run once, after Tasks 140.120-140.160) changed exactly `docs/api/biz.dfch.specmgr.prb.prompts.update_prb.md`, `docs/api/biz.dfch.specmgr.tsk.models.md`, and `docs/api/biz.dfch.specmgr.prb.models.md` (8 insertions / 8 deletions); `docs/MCP.md` (`specmgr mcp-docs`) and `general_harness_bundle.json` (`specmgr harness-bundle`) are byte-identical (the description value is unchanged, `.opencode/` untouched), and `docs/GENERATED.md` stays at **Test files**: 509. A second run of all three generators shows no further diff (idempotence). `grep -rn "Old-shape recovery"` over `docs/MCP.md`, the harness bundle, and `.opencode/` returns 0 matches. `specmgr lint` on this README exits 0 (linted=1 failed=0).

#### 2026-11-26T12:18:46.000Z - dev merge recorded (G1)

`origin/dev` (`48c5d3e5`) was merged into the branch as `01d1722e`, resolving finding E1 (Task 140.100, done in the merge itself). The `CHANGELOG.md` merge conflict was resolved by keeping both sides. `specmgr docs` was regenerated in the merge commit, refreshing `docs/api/biz.dfch.specmgr.req.models.v1.body.md` and `docs/api/biz.dfch.specmgr.gol.models.v1.body.md`, which had carried the pre-feat-253 inherited `models/md` docstring text `mdformat.text()` (both now hold 0 matches). `docs/GENERATED.md` records **Test files**: 509 (502 at base + 6 from `dev` + 1 from this feature). `01d1722e` is listed under Related PRs / Commits. Task 110.120 and the Phase 110 entry ("502 -> 503") are historical and left as written.

#### 2026-11-26T08:09:25.000Z - Phase 140 planned (review cycle 2)

A second feat-reviewer pass over `9c9d7349..d0a185c1` found no defect on the branch itself and reported E1, G1, D1, S1, S2, I1, I2. `origin/dev` (`48c5d3e5`) was merged into the branch as `01d1722e`, which resolves E1 (see Task 140.100). Phase 140 holds one task per remaining finding plus the phase-end gate; Improvements I1/I2 are included, following the cycle-1 decision to fix Improvements too.

#### 2026-11-22T16:41:26.320Z - Plan hygiene

Renamed the Phase 130 heading to `#### Phase 130: Fix phase (review cycle 1: G1/D1/D2/S1/S2/I1-I3)` (the feat-263 fix-phase convention with feat-204-style finding IDs). Annotated the ticked ACC-005 line in place with the maintainer-accepted exception for the 2 environmental Docker/Structurizr export test failures. Recorded two decisions: skipping the suite-running pre-commit hooks for this feature's commits, and fixing review Improvements I1-I3 instead of treating them as advisory.

#### 2026-11-22T16:17:33.155Z - Phase 130 implemented

Applied the feat-reviewer findings. G1: the `prb/data/prb_update_instructions.md` preamble names the "Old-shape recovery" block as the one exception to "every change goes through the specmgr MCP tools" (host file tools, frontmatter byte-unchanged). I1/I3: the recovery block has a new step 4, a `validate(type="prb", content=<the full raw file text>, full=True)` dry-run loop until `valid: true` (the generic `repair` prompt's step 4 idiom), between the insert and the write-back; the write-back and confirm steps are renumbered 5 and 6; the long unwrapped lines of steps 3 and 6 are rewrapped with every test-pinned phrase on one line; the step 2 derive-mapping clause and the composed-sentence code span stay on one line each (the clause is pinned verbatim by `tests/prb/data/test_instructions_consistency.py`, shared with `prb_create_instructions.md`). D1: the `update_prb` MCP prompt `description` names the host file-read/file-write repair, not "a raw re-read"; `docs/MCP.md` regenerated. D2: the module docstring says `get_prb(id)` returns the non-raising `ParseFailureResult` (DEC 9080b37c-82b3-4f63-81f1-79641d0bf14c), present tense, and names the `validate` dry-run; `docs/api/biz.dfch.specmgr.prb.prompts.update_prb.md` regenerated. A repo grep (`src/`, `docs/`, `AGENTS.md`, `README.md`, `.opencode/`, the harness bundle, `CHANGELOG.md`) finds no other PRB "raw re-read" recovery phrasing; `.opencode/` is unchanged, so the harness bundle is unchanged. `AGENTS.md`'s `prb/` bullet and the `CHANGELOG.md` #248 bullet name the `validate` dry-run step, the preamble exception, and the MCP `description`. S1/I2: the recovery test is renamed `test_mentions_old_shape_recovery_via_host_file_repair` (REQ-003 and Task 100.110 cite its former name `test_mentions_old_shape_recovery_via_raw_reread` historically and are left as written); it asserts the validate call and the order file-read < insert < validate < file-write < confirming `get_prb(id)` on the block slice. Against the Phase 100 instructions file (`git show 22a84b33:...` swapped in) it fails (`1 failed, 16 passed`, `AssertionError` on the missing validate call); restored, `17 passed`. S2: explicit `check=False` on the `setUp` probe `subprocess.run` in `tests/test_no_namespace_packages.py`. Change-history grep over the added agent-facing lines: no match. `req/data/req_update_instructions.md` carries the same preamble-versus-recovery contradiction; it is out of scope here and needs a follow-up issue.

#### 2026-11-22T15:46:35.000Z - Phase 120 implemented

Added two `### Fixed` entries under `CHANGELOG.md` `[Unreleased]`, one for #248 and one for #249 (REQ-007). Corrected the stale `get_prb(id, raw=True)` recovery claim in `AGENTS.md`'s `prb/` bullet to the host-file-tool mechanism; a grep of `AGENTS.md` and `README.md` finds no other `get_prb(id, raw=True)` recovery claim. Acceptance criteria evidence, verified in this phase: ACC-001 -- the recovery block (`**Old-shape recovery.**` to `## 2. If no change was specified`) holds 0 matches for `get_prb(id, raw=True)` and for `update(id, type="prb", content)`, and it names `host's own file-read tool`, `host's own file-write tool`, the `path` of the parse-failure result, and a real `get_prb(id)` call; a grep of the lines that the branch adds to the file (`git diff 9c9d7349`) for `previously|now|instead of|formerly|used to be` (whole words) gives no match. ACC-002 -- the full suite includes `tests/prb/prompts/test_update_prb.py` green; the red run against the old wording is recorded in the Phase 100 entry. ACC-003 -- the 16 `docs/api/` pages `biz.dfch.specmgr.{req,gol}.models*` exist (committed in `232512e1`), and `specmgr docs` gives no diff. ACC-004 -- the red demonstration is recorded in the Phase 110 entry; the guard test is green. ACC-005 -- ruff format/check, vulture, and the `specmgr docs`/`mcp-docs`/`harness-bundle` drift checks pass; the full `pytest -n auto` run gives `2 failed, 6117 passed, 18 skipped`, and the only failures are the 2 known Docker/Structurizr export tests in `tests/evals/test_cli_gates.py` (export rc 1), which also fail on clean HEAD and are accepted as an environmental issue -- the suite is not fully green. ACC-006 -- both packages import, and `importlib.util.find_spec(...).origin` is `req/models/__init__.py` and `gol/models/__init__.py` (regular packages, `submodule_search_locations` set).

#### 2026-11-22T15:37:31.493Z - Phase 110 implemented

Added the docstring-only `src/biz/dfch/specmgr/req/models/__init__.py` and `src/biz/dfch/specmgr/gol/models/__init__.py` (license header plus package docstring, no import, no `__all__`); the `req/models` docstring names the versioned-sub-package layout that `tsk/models/__init__.py` cites, and the `gol/models` docstring mirrors it. Added `tests/test_no_namespace_packages.py`: it enumerates `git ls-files -z -- 'src/biz/dfch/specmgr/*.py'` (571 files) and checks every ancestor directory from each file's parent up to and including `src/biz/dfch/specmgr/` for a tracked `__init__.py` that is present on disk; a second test pins the every-ancestor rule on a synthetic `d/models/v1/` layout. Red demonstration: with `req/models/__init__.py` moved out of the tree, `uv run --frozen pytest -q tests/test_no_namespace_packages.py` gave `1 failed, 1 passed` with `AssertionError: Lists differ: [] != ['src/biz/dfch/specmgr/req/models']`; with the file restored, `2 passed`. `specmgr docs` emits 16 new `docs/api/` pages, which matches the `v1/` module listing (`_util`, `body`, `document`, `frontmatter`, `parser`, `summary`) for both domains: `biz.dfch.specmgr.<d>.models`, `biz.dfch.specmgr.<d>.models.v1`, and `biz.dfch.specmgr.<d>.models.v1.{_util,body,document,frontmatter,parser,summary}` for `req` and `gol`. The `docs/api/README.md` index gets the 16 entries, and `docs/GENERATED.md` gets the two new module lines and the **Test files** count 502 -> 503. A second `specmgr docs` run gives no diff. Import smoke check (ACC-006): both packages import, and `find_spec(...).origin` is each package's `__init__.py`. `whitelist.py` and `AGENTS.md` need no change. Gate: ruff format/check, vulture (rc 0), and the full `pytest -n auto` (`2 failed, 6117 passed, 18 skipped`; the 2 failures are the known Docker/Structurizr `tests/evals/test_cli_gates.py` export tests, which also fail on clean HEAD). `specmgr mcp-docs`/`harness-bundle` give no diff.

#### 2026-11-22T15:03:05.107Z - Phase 100 implemented

Rewrote the PRB "Old-shape recovery" block in `prb/data/prb_update_instructions.md` to the host-file-tool mechanism (host file-read at the parse-failure `path`; derive/confirm unchanged; insert under the H1 in the raw file text with the frontmatter, `updated` included, byte-unchanged; host file-write; confirming `get_prb(id)`; the follow-up change through `update`, which bumps `updated`). The `update_prb` module docstring carried the same false `get_prb(id, raw=True)` mechanism and is corrected too, which regenerates `docs/api/biz.dfch.specmgr.prb.prompts.update_prb.md`. `test_mentions_old_shape_recovery_via_raw_reread` asserts the corrected wording and runs its negative assertions on the recovery-block slice only; it fails against the old wording (`1 failed, 16 passed`, an `AssertionError` on the missing `If get_prb(id) returns a parse failure` phrase) and passes on the rewrite (`17 passed`), with `test_mentions_deriving_or_eliciting_lead_sentence_blanks` and `test_mentions_inserting_sentence_under_h1_then_proceeding` unchanged and green. `docs/MCP.md`, the harness bundle, and `.opencode/` hold 0 matches for `Old-shape recovery`/`prb_update_instructions`. Change-history grep over the added lines: no match. Gate: ruff format/check, vulture, full `pytest -n auto`, `specmgr docs`/`mcp-docs`/`harness-bundle` with only the expected `docs/api` page diff.

#### 2026-11-22T14:53:22.862Z - Refined

Applied the `feat-refiner` findings: REQ-006 and the guard test design now check every ancestor directory (a parent-only check passes even without the fix); commit citations corrected to `dbd754ee`/PR #254; REQ-003 scopes the negative assertions to the recovery block and names the other pinned tests; repair write rule (`updated` untouched) stated; docstring-only `models/__init__.py` shape chosen; REQ-007/ACC-006 added; Task 100.120 reworded as a confirming check; dependencies tagged `FEAT`; Created timestamp aligned with frontmatter. The two cited DECs lint clean with the worktree code.

#### 2026-11-22T14:43:46.858Z - Created

Feature plan created from GitHub issues #248 and #249. Both findings verified against `dev` at `9c9d7349`: the PRB block still says `get_prb(id, raw=True)` and `update(id, type="prb", content)`; `req/models/` and `gol/models/` still lack `__init__.py` and no `docs/api` page exists for either domain's models.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-26T08:09:25.000Z - Review cycle 2 Improvements I1/I2 fixed in Phase 140

The user decided (2026-11-26) that review cycle 2's Improvements are fixed in this feature, as in cycle 1, rather than treated as advisory: I1 (Task 140.150) and I2 (Task 140.160) stay in Phase 140. I2 is not deferred to follow-up issue #273.

#### 2026-11-22T16:41:26.320Z - Skip the suite-running pre-commit hooks for this feature's commits

The user decided (2026-11-22) that this feature's commits run with `SKIP=pytest,specmgr-coverage-badge`, because the pre-commit `pytest` and `specmgr-coverage-badge` hooks re-run the full suite, which fails locally only on the 2 environmental Docker/Structurizr export tests in `tests/evals/test_cli_gates.py` (also failing on a clean checkout of the base commit `9c9d7349`). Every other hook ran on every commit, the orchestrator ran the full suite itself at each phase, and GitHub CI on PR #271 is the authoritative gate.

#### 2026-11-22T16:41:26.320Z - Review Improvements I1-I3 fixed, not advisory

The feat-263 convention derives fix tasks from Errors/Gaps/Discrepancies only and treats Improvements as advisory. For review cycle 1 the user asked to fix all findings, so Phase 130 covers I1-I3 too.

#### 2026-11-22T16:17:33.155Z - `req` preamble contradiction deferred to a follow-up issue

The feat-reviewer's G1 finding (preamble "every change goes through the specmgr MCP tools" versus the recovery block's host-file read/write) applies equally to `req/data/req_update_instructions.md`'s preamble and its "Legacy `## Level` value recovery." block. Scope stays PRB-only (Explicitly Out Of Scope: recovery directives of any domain other than PRB); the `req` fix is tracked as GitHub issue #273.

#### 2026-11-22T15:46:35.000Z - Correct the `AGENTS.md` `prb/` bullet too

Scope extension of the Phase 120 close-out, same issue #248: `AGENTS.md`'s `prb/` bullet paraphrased the false recovery mechanism ("re-read via `get_prb(id, raw=True)`"). It now describes the host-file-tool mechanism of `prb/data/prb_update_instructions.md` (host file-read at the parse-failure `path`, derive/confirm, insert under the H1 with the frontmatter byte-unchanged, host file-write, confirming `get_prb(id)`, then proceed). The edit is minimal; `AGENTS.md` and `README.md` hold no other such claim.

#### 2026-11-22T15:03:05.107Z - Correct the `update_prb` module docstring too

The `prb/prompts/update_prb.py` module docstring paraphrased the same false recovery mechanism (`get_prb(id, raw=True)` "never parses, so it always succeeds") and is rendered into `docs/api/`, so it is corrected in Phase 100 alongside the instructions file to keep REQ-001's claim true across the generated docs. The same stale paraphrase in `AGENTS.md` (the `prb/` bullet) is left for the orchestrator to decide.

#### 2026-11-22T14:53:22.862Z - Docstring-only `models/__init__.py`

The new `req/models/__init__.py` and `gol/models/__init__.py` follow the docstring-only `prb`/`tsk` shape rather than the re-exporting `dec`/`txt` shape: the fix only needs regular packages for the docs walk, and adding no import avoids new cycle risk and vulture/`whitelist.py` churn.

#### 2026-11-22T14:43:46.858Z - Bundle #248 and #249, add a namespace-package guard

Both issues are small, independent doc-surface fixes from the same feat-173 retrospective, so they ship as one feature with one phase each. Beyond the issue's proposed fix, #249 gets a regression guard test so a future package directory cannot silently become a namespace package again.

### Related PRs / Commits

- `dbd754ee` -- feat-173 squashed commit, including the correct `req` recovery directive (model text) and the phases where the missing `docs/api` pages surfaced.
- `83be6624` -- PR #254 merge of feat-173 into `dev`.
- `22a84b33` -- Phase 100, PRB old-shape recovery uses host file tools (#248).
- `232512e1` -- Phase 110, `req`/`gol` models made regular packages (#249).
- `fd41f554` -- Phase 120, close-out.
- `142db7c3` -- Phase 130 review fixes.
- `01d1722e` -- merge of `origin/dev` (`48c5d3e5`) into the branch; `CHANGELOG.md` resolved, `specmgr docs` regenerated (Task 140.100).
- PR #271 -- this feature into `dev`.
- Issue #273 -- follow-up for the `req` update-prompt preamble.

### More Information

GitHub issues: #248 (stale PRB recovery directive), #249 (`specmgr docs` misses `req/models` and `gol/models`).
