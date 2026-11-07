---
classification: null
created: '2026-11-03T20:33:04.587+01:00'
id: feat-255-i18n-typo
status: planning
type: feat
updated: '2026-11-03T20:33:04.587+01:00'
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

- [ ] ACC-001: Verifies REQ-001 -- `general_i18n.md` §5.1 lists the 12 tags ending `…VCR, SYSRS, TXT, FEAT`; the test pin asserts `TXT` (no `SOP`); the i18n resource test suite passes.

- [ ] ACC-002: Verifies REQ-002 -- the AST sweep over all model modules returns zero tools-layer imports; an isolated import probe confirms `mcp` is not in `sys.modules` after importing `general.models.heading_table` (the I1/I2 method); the full test suite is green.

- [ ] ACC-003: Verifies REQ-003 -- AGENTS.md names 14 modules, matching `general/tools/__init__.py`'s own imports.

- [ ] ACC-004: Verifies REQ-004 -- the SYSRS document names 15 domains (`adr … set`); the document still parses (the `specmgr lint` gate / `get_sysrs` green); no other line of the document changed.

- [ ] ACC-005: Verifies REQ-005 -- `specmgr docs` second run converges (no diff); `ruff format --check`, `ruff check`, `vulture`, and `pytest -n auto` are all green.

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

- [ ] Task 100.100: Item 1 -- replace `SOP` by `TXT` in `general/data/general_i18n.md` §5.1's tag list (line 122) and update the coordinated pin in `tests/general/resources/test_i18n.py` (line 274) to assert `TXT`

- [ ] Task 100.110: Item 2 -- relocate the canonical `DEFAULT_LANGUAGE` into `general/models/heading_table.py` (dropping the line-72 tools import), alias it in `general/tools/_path_safety.py` (keeping it in `__all__`), and correct the docstring references

- [ ] Task 100.120: Item 3 -- change AGENTS.md's "twelve `@mcp.tool()` modules" to 14 (lines 1252-1253)

- [ ] Task 100.130: Item 4 -- change the SYSRS document's System Scope from "fourteen document-type domains (adr … txt)" to "fifteen document-type domains (adr … set)" via the generic `update`/`edit` tool (`type="sysrs"`)

#### Phase 110: Verification and convergence

- [ ] Task 110.100: Run the AST sweep over all model modules (zero tools-layer imports) plus the isolated `mcp not in sys.modules` probe for `general.models.heading_table`

- [ ] Task 110.110: Regenerate with `specmgr docs`; confirm the second run converges with no diff

- [ ] Task 110.120: Run the full quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`) and walk the acceptance criteria ACC-001…ACC-005

## Progress

### Current Status

**As of 2026-11-03**: Feature drafted from issue #255 (opened 2026-11-03, the carry-over from the feat-173 review passes; PR #254 merged the same day). All four findings verified in-tree at file:line granularity. No implementation started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-03T19:31:24.000Z - Created

Feature drafted from [issue #255](https://github.com/dfch/biz.dfch.SpecMgr/issues/255). The four fixable findings (the i18n §5.1 tag-list typo, the last model→tools import edge, the AGENTS.md tool-module count, the SYSRS domain count) were verified in-tree at file:line before drafting; issue item 5 (the QA interview record) is deliberately left as-is per the issue's own evaluation. The plan is a single consolidated pass in the shape the issue suggests: Phase 100 (items 1-4), Phase 110 (verification + regeneration convergence).

### Related PRs / Commits

- [Issue #255](https://github.com/dfch/biz.dfch.SpecMgr/issues/255): the tracking issue for this feature.

- [PR #254](https://github.com/dfch/biz.dfch.SpecMgr/pull/254): the merged feat-173 PR whose two feat-reviewer passes surfaced all four findings (fix commits `3edeee2`, `847c447`; merge commit `83be662`).
