---
classification: null
created: '2026-11-03T20:33:04.587+01:00'
id: feat-255-i18n-typo
status: done
type: feat
updated: '2026-11-09T20:49:57.894Z'
version: 1.0.0
---

# Feature: I18n Review Cleanup: Tag-List Typo, heading_table Import Edge, Stale Counts (Issue #255)

## Plan

### Overview

This feature is a consolidated cleanup of the carry-over findings from the two
feat-reviewer passes over feat-173-req-iso29148-level-set (PR #254, merged
2026-11-03). Issue #255 enumerates four fixable defects: (1) the 12-tag
reference vocabulary in `specmgr://i18n` §5.1 (`general/data/general_i18n.md:122`)
carries a stale `SOP` where `TXT` belongs (code authority:
`general/tools/_references.py:122`); (2) `general/models/heading_table.py:72`
is the repo's last model→tools import edge (it imports `DEFAULT_LANGUAGE`
from `general/tools/_path_safety.py`, owed by feat-197-i18n); (3) AGENTS.md's
`_envregistry.py` paragraph (lines 1252-1253) claims "twelve `@mcp.tool()`
modules" where the actual count is 14; (4) the repo's own SYSRS document
`## System Scope` (line 19) is stale at "fourteen document-type domains
(adr … txt)" -- there are now 15 with `set`. Issue item 5 (the pre-`set`
i18n scope record in a QA interview document) was evaluated and deliberately
left as-is. Total footprint is ~15 changed lines across 7 files plus the
regeneration convergence.

### Requirements

- REQ-001: The 12-tag reference vocabulary in `general/data/general_i18n.md` §5.1 must read `GOL`, `PRB`, `QA`, `UC`, `REQ`, `RSK`, `DEC`, `ADR`, `VCR`, `SYSRS`, `TXT`, `FEAT` (the stale `SOP` replaced by `TXT`, matching `general/tools/_references.py`'s `_UUID_REFERENCE_TYPES` plus `feat`), with the `tests/general/resources/test_i18n.py` content pin updated in coordination (asserting `TXT`, not `SOP`).

- REQ-002: No model module anywhere in the repo may import from the tools layer: `DEFAULT_LANGUAGE` must take a canonical model-side home (the `models/md/_cross_reference.FEAT_ID_PATTERN` precedent set by feat-173's second-review I1/I2), and `general/tools/_path_safety.py` must alias from there -- an AST sweep over all model modules (`src/biz/dfch/specmgr/models/`, `src/biz/dfch/specmgr/*/models/`, `src/biz/dfch/specmgr/general/models/`) must return zero `general.tools` imports.

- REQ-003: AGENTS.md's `_envregistry.py` paragraph must state the actual count of eagerly imported `@mcp.tool()` modules in `general/tools/__init__.py` (14) instead of the stale "twelve".

- REQ-004: The repo's own SYSRS document (`docs/sysrs/sysrs-8d752304-b076-4bad-89af-f8032158dd21-system-requirements-specification-biz-dfch-specmgr.md`) `## System Scope` must name fifteen document-type domains (`adr, req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs, txt, set`), updated via the normal sysrs doc-editing flow (one line; the `updated` bump is expected).

- REQ-005: After the code changes, the regenerated artifacts (`specmgr docs` → `docs/api/` + `docs/GENERATED.md`) must converge: a second run produces no diff.

### Acceptance Criteria

- [x] ACC-001: Verifies REQ-001 -- `general_i18n.md` §5.1 lists the 12 tags ending `…VCR, SYSRS, TXT, FEAT`; the test pin asserts `TXT` (no `SOP`); the i18n resource test suite passes.

- [x] ACC-002: Verifies REQ-002 -- the AST sweep over all model modules returns zero tools-layer imports; an isolated import probe confirms `mcp` is not in `sys.modules` after importing `general.models.heading_table` (the I1/I2 method); the full test suite is green.

- [x] ACC-003: Verifies REQ-003 -- AGENTS.md names 14 modules, matching `general/tools/__init__.py`'s own imports.

- [x] ACC-004: Verifies REQ-004 -- the SYSRS document names 15 domains (`adr … set`); the document still parses (the `specmgr lint` gate / `get_sysrs` green); no other line of the document changed.

- [x] ACC-005: Verifies REQ-005 -- `specmgr docs` second run converges (no diff); `ruff format --check`, `ruff check`, `vulture`, and `pytest -n auto` are all green.

### Scope

#### Included

- Item 1: the one-line data-file fix in `general_i18n.md` §5.1 plus the coordinated one-line test-pin update in `tests/general/resources/test_i18n.py`.

- Item 2: relocating the canonical `DEFAULT_LANGUAGE` model-side and aliasing it in `general/tools/_path_safety.py` (a direction-only refactor; no behavior change, no edits to the ~40 tools-layer consumers that import it from `_path_safety`).

- Item 3: the one-line count fix in AGENTS.md ("twelve" → "14").

- Item 4: the one-line domain-count fix in the SYSRS document ("fourteen … txt" → "fifteen … set") via the generic `update`/`edit` tool with `type="sysrs"`.

- The regeneration convergence (`specmgr docs`) and the full quality gate.

#### Explicitly Out Of Scope

- Issue item 5: the pre-`set` i18n scope record at `docs/qa/qa-317f6da0-a862-47b6-bcb2-c9993d77fd35-….md:98` -- evaluated, left as-is (a dated interview record; rewriting it would falsify the record).

- Changing the reference tag vocabulary itself (no new tags, no reordering; `SOP`/`TSK` stay non-tags -- "plausible future tag additions").

- Other stale "twelve"/"fourteen" mentions in dated records (feature READMEs, ADRs, session transcripts, history files).

- The stale generic-tool enumeration in the same SYSRS line 19 ("update, set_status, set_classification, delete, mdformat" -- incomplete, but not part of issue #255).

- Any new i18n functionality, new languages, or behavior change; feat-173 itself is complete and untouched.

### Dependencies

#### Depends On

- feat-197-i18n (done) -- owns the `DEFAULT_LANGUAGE` concept whose import direction item 2 settles.

- feat-173-req-iso29148-level-set (done, merged as PR #254) -- the review passes that surfaced all four findings; supplies the I1/I2 relocation precedent for item 2.

### Design Notes

Item 1 -- The code authority is `_UUID_REFERENCE_TYPES` (`("gol", …, "sysrs", "txt")`, 11 UUID tags) plus `("feat",)` in `general/tools/_references.py`; the `_REFERENCE_PATTERN` tag group is derived from it, so the documentation must match. The §5.2 `set` row of the same data file already lists the correct 12 tags (`…VCR, SYSRS, TXT, FEAT`) -- the §5.1 list is a plain stale typo. The test pin asserts each backticked tag individually (`test_common_group_names_the_cross_cutting_tokens`), so the fix is a coordinated two-line change (data + test); no other pin references the §5.1 list.

Item 2 -- Follows the I1/I2 precedent recorded in feat-173 (Updates + Decisions Made, 2026-11-03 16:33:41Z): canonical constant model-side, alias in the tools layer, the name staying in `_path_safety.__all__`, so every existing consumer (all `*/tools/*.py` modules and `general/resources/i18n.py`, which import it from `_path_safety`) stays untouched. The model-side home is `general/models/heading_table.py` itself -- its only model consumer (`resolve_heading_table` compares `language == DEFAULT_LANGUAGE`) -- and it imports nothing from the tools layer after the fix, so no new edge class and no import cycle (heading_table imports only stdlib plus the new local constant). Rationale (from feat-173): importing `general/tools/_path_safety` executes `general/tools/__init__.py`, which eagerly imports every `@mcp.tool()` module, so the `mcp` extra enters the model import graph one layer deeper than the direction allows. Verification: the AST sweep over all model modules plus the isolated `mcp not in sys.modules` probe (the I1/I2 method, with the package-init registration edges stubbed out).

Item 4 -- The SYSRS document is live spec content, not code: it is edited via the generic `update` (`type="sysrs"`, line range) or `edit` tool, never a raw file write; the frontmatter `updated` bump is expected and the body stays byte-identical except the one line; the pre-commit `specmgr lint` hook full-parses the staged document.

### Related Decisions

- feat-173-req-iso29148-level-set, Decisions Made 2026-11-03 16:33:41Z -- the I1/I2 relocation of the shared FEAT id-shape constant model-side (`models/md/_cross_reference.FEAT_ID_PATTERN`); the exact precedent item 2 follows.

- ADR 38efdb66-8025-45c5-bbe8-45b25fc7a772 (feat-197-i18n) -- the i18n design that introduced `DEFAULT_LANGUAGE` (items 1/6/7) and whose residual import direction this feature settles.

### Task List

#### Phase 100: Implementation (items 1-4)

- [x] Task 100.100: Item 1 -- replace `SOP` by `TXT` in `general/data/general_i18n.md` §5.1's tag list (line 122) and update the coordinated pin in `tests/general/resources/test_i18n.py` (line 274) to assert `TXT`

- [x] Task 100.110: Item 2 -- relocate the canonical `DEFAULT_LANGUAGE` into `general/models/heading_table.py` (dropping the line-72 tools import), alias it in `general/tools/_path_safety.py` (keeping it in `__all__`), and correct the docstring references

- [x] Task 100.120: Item 3 -- change AGENTS.md's "twelve `@mcp.tool()` modules" to 14 (lines 1252-1253)

- [x] Task 100.130: Item 4 -- change the SYSRS document's System Scope from "fourteen document-type domains (adr … txt)" to "fifteen document-type domains (adr … set)" via the generic `update`/`edit` tool (`type="sysrs"`)

#### Phase 110: Verification and convergence

- [x] Task 110.100: Run the AST sweep over all model modules (zero tools-layer imports) plus the isolated `mcp not in sys.modules` probe for `general.models.heading_table`

- [x] Task 110.110: Regenerate with `specmgr docs`; confirm the second run converges with no diff

- [x] Task 110.120: Run the full quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`) and walk the acceptance criteria ACC-001…ACC-005

## Progress

### Current Status

**As of 2026-11-08**: All phases are complete — Phase 100 (implementation, items 1-4 plus the CHANGELOG Fixed entry) and Phase 110 (verification + regeneration convergence) — with ACC-001…ACC-005 ticked and the full quality gate green (pytest 6297 passed / 18 skipped / 11218 subtests; `ruff format --check` / `ruff check` / `vulture` clean; `specmgr docs` converged with no diff). The post-implementation feat-reviewer pass returned verdict `ship` (no Errors/Gaps/Inconsistencies; ACC-001…ACC-005 all MET with independently re-verified evidence), and its two advisory Improvements (I1: no permanent AST regression guard pinning the model→tools import direction; I2: pre-existing — the §5.1 content pin asserts 11 of the 12 backticked tags) were deliberately not acted on, the plan fixing this feature's footprint (~15 changed lines across 7 files + regeneration) and scoping item 2's verification as a one-off sweep in the feat-173 precedent's shape. The feature is closed out to `done`; the branch is ready for push + PR to `dev` (head ref `feat-255-i18n-typo`).

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-08T21:02:57.163Z - Closeout: post-implementation review passed, status done

The post-implementation feat-reviewer pass returned verdict `ship`: no Errors, Gaps, or Inconsistencies, and ACC-001…ACC-005 all MET with independently re-verified evidence (i18n suite 25 passed / 124 subtests; AST sweep 199 model files / zero model→tools imports; isolated I1/I2 probe `mcp not in sys.modules`; full gate green). Its two advisory Improvements were named and deliberately not acted on — I1 (no permanent AST regression guard pinning the model→tools import direction; the sweep was one-off, as the feat-173 I1/I2 precedent itself was) and I2 (pre-existing: the §5.1 content pin asserts 11 of the 12 backticked tags, `` `FEAT` `` was never in the fragment tuple, before or after this change) — because the plan fixes this feature's footprint (~15 changed lines across 7 files + regeneration) and scopes item 2's verification as a one-off sweep in the feat-173 precedent's shape, and a new test file or a widened pin tuple would be scope creep the plan does not authorize (repo precedent for this treatment: feat-167's Phase 150 entry). Gate evidence summary: `ruff format --check` 2433 files already formatted, `ruff check` clean, `vulture src/ whitelist.py --min-confidence 60` clean, `pytest -n auto` 6297 passed / 18 skipped / 11218 subtests, `specmgr docs` second run converged with no diff. The status moves `review` → `done` in this closeout per the feat-108 closeout-commit pattern. Next: push the branch and open PR `feat-255-i18n-typo` → `dev` (the PR number is recorded under Related PRs / Commits once it is opened).

#### 2026-11-08T18:55:27.207Z - Status progress → review

Implementation (Phase 100, items 1-4 plus the CHANGELOG Fixed entry) and verification (Phase 110, regeneration convergence plus the full quality gate) are complete: all five acceptance criteria (ACC-001…ACC-005) are ticked with committed evidence, and the gate is green (`ruff format --check` / `ruff check` / `vulture` / `pytest -n auto` = 6297 passed, 18 skipped, 11218 subtests). The feature is submitted for the post-implementation review pass; any findings will be addressed in a fix phase, followed by the closeout commit (`status` → `done`).

#### 2026-11-08T18:33:25.552Z - Phase 110 complete (verification and convergence)

Task 110.100(a) AST sweep (REQ-002) over all three model locations (`src/biz/dfch/specmgr/models/`, `*/models/`, `general/models/`) parsed 199 model files with `ast` and found zero `Import`/`ImportFrom` nodes resolving into the tools layer (no `biz.dfch.specmgr.<anything>.tools` absolute name, no `..tools`/`...tools` relative import). Task 110.100(b) ran the isolated I1/I2 probe (the repo-wide package-init registration edge stubbed, per the feat-173 record) and reported `mcp in sys.modules: False` / `probe OK: mcp not in sys.modules` — confirming importing `general.models.heading_table` alone no longer pulls the `mcp` extra into the model import graph; the literal one-liner probe still reports `mcp` present on every tree because it measures `general/__init__`'s eager `from . import prompts, resources, tools` registration edge, not the model edge. Task 110.110 ran `specmgr docs` twice; both runs wrote 587 `docs/api/` module pages plus `docs/GENERATED.md` and left `git status` clean of any generated-file change, so the Phase 100 regeneration had already converged. Task 110.120 gate: `ruff format --check` = 2433 files already formatted, `ruff check` = All checks passed!, `vulture src/ whitelist.py --min-confidence 60` = clean, `pytest -n auto -q` = 6297 passed, 18 skipped, 11218 subtests passed (exit 0). ACC-001…ACC-005 walked and ticked: ACC-001 `general_i18n.md` §5.1 (line 122) ends `…SYSRS, TXT, FEAT` and the `test_i18n.py` pin asserts `TXT` with no `SOP` fragment (i18n suite 25 passed, 124 subtests); ACC-002 the 199-file AST sweep + isolated probe + green full suite; ACC-003 AGENTS.md names 14 modules matching `general/tools/__init__.py`'s 12 alphabetical + `check_translation_drift`/`list_languages`; ACC-004 the SYSRS `## System Scope` (line 19) names the fifteen domains `adr…set`, `specmgr lint` exit 0 (`linted=1 failed=0`), and the diff is exactly that one body line plus the `updated` bump; ACC-005 the docs double-run no-diff plus all four gate commands green.

#### 2026-11-08T17:26:33.110Z - Phase 100 complete (items 1-4)

All four items landed in one pass, gate green. Item 1: `general/data/general_i18n.md` §5.1's 12-tag reference list now ends `…VCR, SYSRS, TXT, FEAT` (the stale `SOP` — not a reference tag — replaced by `TXT`, matching the code authority `general/tools/_references.py`'s `_UUID_REFERENCE_TYPES` + `feat`; the §5.2 `set` row was already correct and no other `sop` mention touched), with the coordinated pin in `tests/general/resources/test_i18n.py`'s `test_common_group_names_the_cross_cutting_tokens` asserting `` `TXT` `` in place of the file's only `` `SOP` `` fragment. Item 2: `DEFAULT_LANGUAGE` now has its canonical model-side home in `general/models/heading_table.py` (first in its `__all__`, `#:` comment moved verbatim; the line-72 `..tools._path_safety` import — the repo's last model→tools edge — is gone), and `general/tools/_path_safety.py` aliases it from there with the name kept in `__all__`, so every existing tools-layer consumer is untouched; the one stale qualified docstring reference (`general/tools/_doc_paths.py`'s module docstring) was re-pointed to the new home; the isolated I1/I2 probe (the repo-wide package-init registration edge stubbed, per the feat-173 record) flips `mcp in sys.modules` True (PRE, with the recorded mid-cascade re-entry `ImportError` artifact) → False (POST), while the literal one-liner probe stays True on every tree because it measures `general/__init__`'s eager `from . import prompts, resources, tools` registration edge — the feat-173 "recorded contradiction" — not the model edge. Item 3: AGENTS.md's `_envregistry.py` paragraph now reads "14 `@mcp.tool()` modules" (verified against `general/tools/__init__.py`'s own 14 imports: the 12 alphabetical plus the deliberately last `check_translation_drift`/`list_languages`). Item 4: the SYSRS document's `## System Scope` now names fifteen document-type domains (`adr … txt, set`) — edited via the generic `edit` tool (`type="sysrs"`, byte-exact unique match), the document's diff is exactly that one body line plus the frontmatter `updated` bump, and `get_sysrs` still parses it. The new `CHANGELOG.md` `### Fixed` section (two bullets in the file's own em-dash prose style) landed between `### Changed` and `## [0.38.0]`, and `specmgr docs` regenerated exactly one `docs/api/` page (`_doc_paths.md`, mirroring the re-pointed docstring reference; module constants are not rendered as standalone entries) with `docs/GENERATED.md` byte-identical.

#### 2026-11-08T16:33:13.418Z - Status planning → progress

Implementation started on takeover from the exported session (`ses_e44fb2e76ffeVv6WZ60Eij0s6m`). The plan preconditions were re-verified in-tree: the four defects sit at the planned file:line locations, `general/tools/__init__.py` carries the 14-module count, and `CHANGELOG.md`'s `[Unreleased]` section carries no Fixed entry yet. Phase 100 is next.

#### 2026-11-03T19:31:24.000Z - Created

Feature drafted from [issue #255](https://github.com/dfch/biz.dfch.SpecMgr/issues/255). The four fixable findings (the i18n §5.1 tag-list typo, the last model→tools import edge, the AGENTS.md tool-module count, the SYSRS domain count) were verified in-tree at file:line before drafting; issue item 5 (the QA interview record) is deliberately left as-is per the issue's own evaluation. The plan is a single consolidated pass in the shape the issue suggests: Phase 100 (items 1-4), Phase 110 (verification + regeneration convergence).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-08T21:02:57.163Z - Review triage: advisory Improvements I1/I2 deliberately not acted on

The post-implementation feat-reviewer pass returned verdict `ship` (no Errors/Gaps/Inconsistencies; ACC-001…ACC-005 all MET), and its two advisory Improvements — I1 (no permanent AST regression guard pinning the model→tools import direction; the sweep was one-off, as the feat-173 I1/I2 precedent itself was) and I2 (pre-existing: the §5.1 content pin asserts 11 of the 12 backticked tags, `` `FEAT` `` was never in the fragment tuple, before or after this change) — were deliberately not acted on: the plan fixes this feature's footprint (~15 changed lines across 7 files + regeneration) and scopes item 2's verification as a one-off sweep in the feat-173 precedent's shape, so a new test file or a widened pin tuple would be scope creep the plan does not authorize (repo precedent for this treatment: feat-167's Phase 150 entry).

### Related PRs / Commits

- [Issue #255](https://github.com/dfch/biz.dfch.SpecMgr/issues/255): the tracking issue for this feature.

- [PR #254](https://github.com/dfch/biz.dfch.SpecMgr/pull/254): the merged feat-173 PR whose two feat-reviewer passes surfaced all four findings (fix commits `3edeee2`, `847c447`; merge commit `83be662`).

- [PR #259](https://github.com/dfch/biz.dfch.SpecMgr/pull/259): this feature's delivery PR (merged 2026-11-09T18:35:09Z as merge commit `3d74305`; auto-closed issue #255 by the merge).
