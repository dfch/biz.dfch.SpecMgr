---
classification: null
created: '2026-11-22T15:43:46.858+01:00'
id: feat-248-249-stale-docs
status: review
type: feat
updated: '2026-11-22T16:47:46.728+01:00'
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
- [x] ACC-005: The full quality gate passes: `ruff format --check`, `ruff check`, `vulture`, the full `pytest -n auto` suite, and the doc/schema/mcp-docs drift checks (process criterion; REQ-007 covers the CHANGELOG housekeeping).
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

## Progress

### Current Status

**As of 2026-11-22**: Phase 100 (issue #248) committed as `22a84b33`, Phase 110 (issue #249) committed as `232512e1`. Phase 120 (close-out) implemented, uncommitted: `CHANGELOG.md` `[Unreleased]` entries, `AGENTS.md` `prb/` bullet corrected, all acceptance criteria ticked. Next: status `review` and the PR against `dev` (orchestrator).

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

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

### More Information

GitHub issues: #248 (stale PRB recovery directive), #249 (`specmgr docs` misses `req/models` and `gol/models`).
