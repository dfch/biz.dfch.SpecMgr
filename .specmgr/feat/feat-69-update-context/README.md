---
classification: null
created: '2026-09-02 21:49:41.712+02:00'
id: feat-69-update-context
status: done
type: feat
updated: '2026-10-07T06:21:40.948Z'
version: 1.0.0
---

# Feature: MCP write tools return the full document on every call, filling up context quickly

## Plan

### Overview

Every mutating MCP tool call currently returns the fully re-parsed document (frontmatter + body) on success, not a lightweight acknowledgement. Confirmed by reading the source: the generic `update`, `set_status`, and `set_classification` tools (`general/tools/`), and every per-domain `create_<d>` tool (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`), all return the whole document object. Because documents such as QA transcripts, FEAT READMEs, and ADRs are explicitly append-only by convention, the returned payload grows monotonically with the document's size across a session, driving up the token cost of every subsequent write call -- this was observed directly during a `feat-63-refine` design session. This feature makes successful writes return the document's frontmatter only (small, bounded size, regardless of how large the body grows) instead of frontmatter+body, matching the behavior of OpenCode's own built-in `edit` tool, which does not echo the whole file back on a successful edit. Error/validation-failure responses are unaffected -- they keep returning full, actionable detail. Callers who need the full document after a write can still get it via the existing, explicit `get_<d>` tool.

### Requirements

- REQ-001: The generic `update` tool must return the document's frontmatter only (no body) on a successful write, across all eleven whole-body domains.
- REQ-002: The generic `set_status` tool must return the document's frontmatter only (no body) on a successful write, across all eleven whole-body domains (the `adr` dispatch branch is unchanged, see Scope).
- REQ-003: The generic `set_classification` tool must return the document's frontmatter only (no body) on a successful write, across all eleven whole-body domains.
- REQ-004: Every per-domain `create_<d>` tool must return the newly generated frontmatter only (no body) on success, since the frontmatter (id, status, created, updated, version) is server-generated data the caller cannot otherwise learn, while the body is exactly what the caller just submitted.
- REQ-005: Error/validation-failure responses from any of the above are unchanged by this feature -- they keep returning full actionable detail (per feat-27-validation).
- REQ-006: The generic `delete` tool already returns a minimal payload (the deleted path) and needs no change.
- REQ-007: Callers who need the full resulting document after a successful write must use the existing `get_<d>` tool explicitly.
- REQ-008: The `sysrs` domain, added to `dev` after this feature's branch point, must receive the same frontmatter-only treatment as the other 11 whole-body domains for `update`/`set_status`/`set_classification`/`create_sysrs`.

### Acceptance Criteria

- [x] ACC-001: After a successful `update` call, the response contains the document's frontmatter only -- no body content.
- [x] ACC-002: After a successful `set_status` call, the response contains the document's frontmatter only (reflecting the new status/updated) -- no body content.
- [x] ACC-003: After a successful `set_classification` call, the response contains the document's frontmatter only (reflecting the new classification/updated) -- no body content.
- [x] ACC-004: After a successful `create_<d>` call, the response contains the newly generated frontmatter only -- no body content.
- [x] ACC-005: A validation/parse error from any of the above still returns the existing detailed error message, unchanged.
- [x] ACC-006: `delete` and all ADR-specific tools are verified unchanged by this feature (regression check, not new behavior).
- [x] ACC-007: Tests updated/added across all eleven whole-body domains plus the three generic tools to assert frontmatter-only responses.
- [x] ACC-008: The `sysrs` domain (merged in from `dev` after this feature's branch point) also returns frontmatter-only from `update`/`set_status`/`set_classification`/`create_sysrs`, with tests updated/added mirroring ACC-001-004/007's pattern.

### Scope

#### Included

- The generic `update` tool (`general/tools/update.py`) across all eleven whole-body domains (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr).
- The generic `set_status` tool (`general/tools/set_status.py`) across all twelve domains, excluding the `adr` dispatch branch (left unchanged per scope decision).
- The generic `set_classification` tool (`general/tools/set_classification.py`) across all eleven whole-body domains.
- Every per-domain `create_<d>` tool (11 domains): create_req, create_uc, create_tsk, create_qa, create_prb, create_gol, create_rsk, create_dec, create_sop, create_feat, create_vcr.
- Updating each tool's return type annotation and MCP tool description to reflect the new frontmatter-only response shape.
- Updating/adding unit tests asserting the new response shape per domain.

#### Explicitly Out Of Scope

- All ADR-specific tools (create_adr, update_frontmatter, update_section, option_create, option_read, option_update, option_delete, set_status's adr branch) -- deferred until ADR's own mechanism is reworked.
- The generic `delete` tool -- already returns a minimal payload (the deleted path), no change needed.
- Any diff/patch-of-changes feature in the response (considered and dropped in favor of the simpler frontmatter-only approach).
- Changes to `get_<d>` tools' behavior -- they remain the explicit, unchanged way to fetch a full document.
- Any change to server-side validation logic or error message content (feat-27-validation's error paths are untouched).
- The `sysrs` domain's `delete` adapter -- `delete` was never in scope for this feature (REQ-006), and merging `sysrs` in from `dev` does not change that; `_delete_sysrs` needs no change.

### Dependencies

#### Depends On

- feat-27-validation: this feature's error paths (REQ-005/ACC-005) rely on the actionable, field-path/line-referenced error messages that feature introduced staying intact and unchanged.

### Design Notes

The shared contract: every in-scope tool's success return type stays the same document model, but the body is always empty/omitted -- frontmatter is bounded in size regardless of document length, unlike the body, which grows unboundedly for append-only documents. Verified: no existing prompt (`*/prompts/*.py`) documents or depends on the old full-document response shape, so no prompt changes are required for this feature.

**2026-09-02 (Phase 1) -- formalized contract for Phases 2/3:**

1. **Return type.** Each in-scope tool/adapter's return type annotation changes from the domain's `XxxDocument` (or an N-way union of `XxxDocument`s for the three generic dispatch tools) to the domain's own `XxxFrontmatter` (or the equivalent N-way union of `XxxFrontmatter`s). The tool returns the frontmatter object directly -- not a `XxxDocument` wrapper with an emptied-out body. This applies to `general/tools/update.py`, `general/tools/set_status.py`, `general/tools/set_classification.py` (all three: the public dispatch function's return annotation, the module-level N-way union type alias such as `update.py`'s `_UpdateDocument`, the `_ADAPTERS` dispatch table's `Callable[..., _UpdateDocument]` value type, and every private `_update_<d>`/`_set_status_<d>`/`_set_classification_<d>` adapter's own `-> XxxDocument` annotation), and to all 11 `create_<d>` tools' `-> XxxDocument` annotation.
2. **No cross-field validation is lost.** Read every in-scope domain's `document.py` (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`, `dec`, `sop`, `feat`, `vcr`): none defines a `model_validator`/`field_validator` of any kind -- each `XxxDocument` is a plain two-field `pydantic.BaseModel` container (`frontmatter: XxxFrontmatter`, `body: XxxBody`) with zero cross-field logic. All real validation already happened earlier in each adapter, when `body` was built via `Xxx.from_text(format_text(...))` and `new_frontmatter` was built via `XxxFrontmatter(**fm_data)` -- constructing `XxxDocument(frontmatter=new_frontmatter, body=body)` today serves *no* validation purpose, only shapes the return value. Consequence: Phases 2/3 implementers should **remove** the now-pointless `new_doc = XxxDocument(frontmatter=new_frontmatter, body=body)` line in each adapter (it would otherwise become an unused-variable lint/vulture finding) and change `return new_doc` to `return new_frontmatter` (in `set_status`'s no-splice branches, which reuse `existing.body` and never rebuild `body`, the same applies: drop the `XxxDocument(...)` construction, return `new_frontmatter` directly). Do not delete the frontmatter-construction lines themselves -- only the trailing document-wrapping + return.
3. **`create_<d>` tools follow the identical pattern.** Each builds `body` from the submitted `content` (validation), builds `new_frontmatter` (server-generated id/status/created/updated/version), persists via `write_<d>_file(...)`, and today wraps both into `new_doc = XxxDocument(frontmatter=new_frontmatter, body=body)` purely to return it. Per point 2, that wrapping adds no validation; drop it and `return new_frontmatter` instead.
4. **No new Pydantic model classes.** The existing per-domain `XxxFrontmatter` classes (already imported into every one of these tool modules today, since they are used to build `new_frontmatter`) are reused as-is for the response type. Nothing new to define in any `models/vN/` package.
5. **Scope of the change per adapter.** This is a narrow, mechanical, low-risk change: for `update`/`set_status`/`set_classification`, only (a) the removed `XxxDocument(...)` construction line, (b) the changed `return` statement, and (c) the function's own `->` return-type annotation change. The public `@mcp.tool()`-decorated function's return type annotation, its module-level union alias, the `_ADAPTERS` dict's value type, and the Returns section of its docstring all change accordingly; no other internal helper signature (`load_by_id`, `write_<d>_file`, `body_text`/`splice_body`, lock context managers, etc.) changes at all. Same for `create_<d>`: only the trailing wrap-and-return plus the function's own return annotation and docstring Returns section change.
6. **Error paths need zero code changes.** Confirmed by reading `update.py`/`set_status.py`/`create_req.py`: every validation/parse failure path (`AssertionError`, `pydantic.ValidationError`, the domain's own `XxxNotFoundError`, `ValueError` from `_path_safety`) is a *raised exception*, propagated uncaught out of the tool function -- there is no "error return value" branch anywhere in scope. REQ-005/ACC-005 ("error paths unchanged") are therefore satisfied automatically by this design and require no implementation work in Phases 2/3; only success-path `return` statements and return-type annotations change.

**2026-09-02 (Phase 6) -- extending the contract to the merged-in `sysrs` domain:** `origin/dev` gained a 12th whole-body domain (`sysrs`, PR #68) after this feature's branch point, developed in parallel against the OLD (pre-feat-69) full-document-return shape. Merging `origin/dev` into this branch therefore requires applying the exact same Phase 1 contract (points 1-5 above) to `sysrs`'s `_update_sysrs`/`_set_status_sysrs`/`_set_classification_sysrs` adapters and its `create_sysrs` tool, so the codebase does not end up in an inconsistent state (11 domains frontmatter-only, 1 still full-document). `sysrs`'s `delete` adapter needs no change -- `delete` was out of scope for this feature from the start (REQ-006) and remains so.

### Task List

#### Phase 100: Design the shared minimal-response shape

- [x] Task 100.100: Decide/document the frontmatter-only return type contract shared by update/set_status/set_classification/`create_<d>` (Design Notes).
- [x] Task 100.110: Confirm via test run that no prompt currently documents the old full-document response shape (already verified: none do).

#### Phase 110: Generic tools (general/tools/)

- [x] Task 110.100: Change `update` to return frontmatter-only across all 11 whole-body domains.
- [x] Task 110.110: Change `set_status` to return frontmatter-only across all 11 whole-body domains (adr branch unchanged).
- [x] Task 110.120: Change `set_classification` to return frontmatter-only across all 11 whole-body domains.
- [x] Task 110.130: Update each tool's MCP `description=` text and docstring Returns section.
- [x] Task 110.140: Run the full test suite (`uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`) plus `ruff format --check`/`ruff check`/`vulture` before moving to Phase 3.

#### Phase 120: Per-domain `create_<d>` tools

- [x] Task 120.100: Change all 11 `create_<d>` tools to return frontmatter-only.
- [x] Task 120.110: Update each tool's MCP `description=` text and docstring Returns section.
- [x] Task 120.120: Run the full test suite plus `ruff format --check`/`ruff check`/`vulture` before moving to Phase 4.

#### Phase 130: Tests

- [x] Task 130.100: Update/add unit tests asserting frontmatter-only responses for update/set_status/set_classification/`create_<d>` across all 11 domains.
- [x] Task 130.110: Add a regression test confirming `delete` and ADR tools are unaffected.
- [x] Task 130.120: Run the full test suite plus `ruff format --check`/`ruff check`/`vulture` before moving to Phase 5.

#### Phase 140: Docs

- [x] Task 140.100: Regenerate `docs/api/` + `docs/GENERATED.md` via `specmgr docs`.
- [x] Task 140.110: Update AGENTS.md bullets/README mentions of write-tool return shapes if any exist.
- [x] Task 140.120: Run the full test suite (final validation) plus `ruff format --check`/`ruff check`/`vulture` before considering the feature done.

#### Phase 150: Merge upstream dev (sysrs domain) and extend the frontmatter-only contract to sysrs

- [x] Task 150.100: Merge `origin/dev` (PR #68's `sysrs` domain) into this feature branch, resolving conflicts.
- [x] Task 150.110: Apply the same frontmatter-only contract (Phases 1-4's pattern) to the new `sysrs` domain's `update`/`set_status`/`set_classification` adapters and its `create_sysrs` tool.
- [x] Task 150.120: Fix/extend `sysrs`-related tests to match (mirroring Phases 2-4's approach), across `tests/general/tools/test_{update,set_status,set_classification}.py`'s new `sysrs` cases and `tests/sysrs/` itself.
- [x] Task 150.130: Reconcile `AGENTS.md` domain-count wording between this feature's sentence and `dev`'s bump to 12 whole-body domains.
- [x] Task 150.140: Regenerate docs, run the full quality gate.

## Progress

### Current Status

**As of 2026-09-02**: Feature drafted from GitHub issue #69. Root cause confirmed by reading source: `update`, `set_status`, `set_classification`, and every per-domain `create_<d>` tool return the fully re-parsed document (frontmatter + body) on every successful write; `delete` already returns a minimal path string, and ADR-specific tools are out of scope for this feature. Approach agreed: all in-scope tools switch to a frontmatter-only response (small, bounded size) instead of frontmatter+body (unbounded, growing with document size); error paths are untouched. No prompts currently document the old response shape, so no prompt changes are needed. **Phase 1 (design) is complete**: the frontmatter-only contract is formalized in Design Notes (return type change, removal of the now-pointless `XxxDocument(...)` wrapping construction, no new models needed, error paths untouched by design) and verified against every domain's `document.py`; Task 1.2's prompt-shape check is confirmed clean. **Phase 2 (generic tools) is complete**: `update`, `set_status` (its 11 non-adr adapters; the `adr` branch is unchanged), and `set_classification` all now return the domain's `XxxFrontmatter` object directly instead of the full `XxxDocument`. Full test suite green (3070 tests), ruff/vulture clean. **Phase 3 (per-domain `create_<d>` tools) is complete**: all 11 `create_<d>` tools now return the domain's `XxxFrontmatter` object directly instead of the full `XxxDocument`. Full test suite green (3070 tests), ruff/vulture clean. **Phase 4 (tests) is complete**: every in-scope test file now carries explicit, positive assertions (`assertIsInstance(result, XxxFrontmatter)` + `assertNotIsInstance(result, XxxDocument)` + `assertFalse(hasattr(result, "body"))`) proving the frontmatter-only contract, plus explicit regression assertions that `delete`/ADR tools are unaffected. Full test suite green (3071 tests), ruff/vulture clean. **Phase 5 (docs) is complete, and the feature is done**: `specmgr docs`/`specmgr mcp-docs` confirmed zero drift (Phases 2-4's pre-commit hooks already kept `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md` current on every prior commit); `AGENTS.md`'s `general/` bullet gained one new sentence stating that `update`/`set_status` (its eleven non-`adr` adapters)/`set_classification`/every `create_<d>` tool now return frontmatter-only on success, citing `feat-69-update-context`, with the `adr` branch and ADR-specific tools explicitly excluded; `README.md` needed no change (verified by search, no existing text described the old return shape). Final quality gate all green: `ruff format --check`, `ruff check`, `vulture`, and the full suite (3071 tests). ACC-005 re-investigated and now checked: existing tests already assert that a validation/structural failure raises (`AssertionError`/`pydantic.ValidationError`) *and* leaves the on-disk file byte-identical/writes nothing at all, across `update` (`test_update.py`'s `test_structural_failure_raises_and_leaves_file_byte_identical`/`test_field_validation_failure_raises_and_leaves_file_byte_identical`/`test_status_not_settable_through_update`), `set_status` (`test_set_status.py`'s equivalent `before`/`assertEqual(path.read_text(...), before)` pattern), `set_classification` (`test_set_classification.py`, same pattern), and all 11 `create_<d>` domains (each `test_create_<d>.py` has a `test_*_raises_and_writes_nothing` pair) -- these predate this feature (feat-27-validation and earlier) and were never touched by Phases 2-4 since they only touch success-path code, so they demonstrate REQ-005/ACC-005 held throughout. All seven acceptance criteria are now satisfied; the feature is complete. **Phase 6 (merge upstream `dev`/sysrs contract extension) is complete**: `origin/dev` (PR #68) added a 12th whole-body domain, `sysrs`, developed against the old full-document-return shape; `origin/dev` was merged in (`git merge --no-commit --no-ff`), resolving 9 real conflicts across `update.py`/`set_status.py`/`set_classification.py` (3 regions each: import block, N-way union type, docstring/Returns text) and `test_update.py`/`test_set_status.py` (1 import-ordering conflict each) plus `test_set_classification.py` (an import-ordering conflict and the `_CASES` list rebuild), keeping HEAD's frontmatter-only shape while folding in dev's `sysrs` additions and correct domain-count bumps (eleven->twelve/twelve->thirteen); the 4 generated-doc conflicts (`docs/MCP.md`, 3 `docs/api/*.md` files) were resolved with `git checkout --theirs` and then fully regenerated via `specmgr docs`/`specmgr mcp-docs`. The same Phase 1 contract was then applied to `sysrs`'s `_update_sysrs`/`_set_status_sysrs`/`_set_classification_sysrs` adapters and `create_sysrs` (drop `SysrsDocument(...)` wrapping, return `SysrsFrontmatter` directly, fix return annotations, update docstrings/`description=` text). Tests fixed: `test_update.py`/`test_set_status.py` (added missing `frontmatter_type=SysrsFrontmatter, document_type=SysrsDocument` to the merged-in `sysrs` `_Case`), `tests/sysrs/tools/test_create_sysrs.py` (`assertIsInstance(result, SysrsFrontmatter)` + negative checks + `get_sysrs`-based body fetch), `tests/sysrs/tools/test_integration.py` (every `.frontmatter.X`/`.body.X` read on a tool's own `create_sysrs`/`update`/`set_status`/`set_classification` return value fixed the same way Phase 2/3 fixed the other six domains' `test_integration.py` files), and two more sysrs test files surfaced only by the full suite run (`test_get_sysrs.py`, `test_list_sysrs.py` -- both called `created.frontmatter.id` on `create_sysrs`'s own return value). `AGENTS.md`'s stale "eleven non-`adr` adapters" wording (from this feature's own Phase 5 sentence) fixed to "twelve" now that `sysrs` is one of them; every other domain-count number in that same paragraph was already correct from `dev`'s own merge. Full quality gate green: `ruff format --check` (1627 files), `ruff check` (all checks passed), `vulture` (no findings), full suite (3293 tests, up from 3071 pre-merge -- the ~220 new tests are `sysrs`'s own suite from `dev`), `specmgr docs`/`specmgr mcp-docs` regenerated with zero remaining drift.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 23:59:00.000+02:00 - (Phase 6) Merged origin/dev (sysrs domain), extended frontmatter-only contract to sysrs

Completed Phase 6 (Tasks 6.1-6.5), reopened after this feature was believed done because
`origin/dev` gained commit `c30e03e` (PR #68, "feat(sysrs): add System Requirements Specification
(SYSRS) domain") after this feature's branch point -- a 12th whole-body domain developed in
parallel against the OLD (pre-feat-69) full-document-return shape, conflicting with this feature's
open PR #75 in exactly the three generic-tool files this feature already changed. **Task 6.1 (merge)**: `git fetch origin && git merge --no-commit --no-ff origin/dev`. Confirmed
  the exact conflict set matched the pre-flighted answer key: 3 real `.py` source conflicts
  (`update.py`, `set_status.py`, `set_classification.py`, 3-4 regions each: an import block, the
  N-way `_UpdateFrontmatter`/`_SetStatusFrontmatter`/`_SetClassificationFrontmatter` union
  definition, and docstring/Returns-section text -- `set_status.py` additionally had a 4th region,
  the function signature's own return annotation + opening docstring sentence), 3 test-file
  conflicts (`test_update.py`/`test_set_status.py`: one import-ordering region each;
  `test_set_classification.py`: an import-ordering region plus the `_CASES` list, where HEAD's
  8-positional-arg `_Case` shape had to absorb dev's new `sysrs` entry, still using dev's OLD
  6-positional-arg shape), and 4 generated-doc conflicts (`docs/MCP.md` plus 3
  `docs/api/biz.dfch.specmgr.general.tools.{update,set_status,set_classification}.md`).
  Resolved every `.py` conflict by keeping HEAD's frontmatter-only shape (unions, docstrings,
  Returns prose) while folding in dev's structural additions (`sysrs` imports, the new
  `SysrsFrontmatter` union member, dev's correct domain-count bumps -- "eleven" -> "twelve"
  whole-body domains, "twelve" -> "thirteen" total incl. `adr`); import-ordering conflicts resolved
  alphabetically; `test_set_classification.py`'s `_CASES` list rebuilt as one 8-positional-arg list
  with a new `sysrs` entry (`SysrsFrontmatter`/`SysrsDocument`/`sysrs_base_dir`/
  `SysrsNotFoundError`/`create_sysrs`/`_SYSRS_MINIMAL_BODY`) inserted in dev's relative position
  (before `feat`). The 4 generated-doc conflicts were resolved with `git checkout --theirs` (an
  arbitrary pick, since Task 6.5 fully regenerates them afterward anyway) and then genuinely
  regenerated via `specmgr docs`/`specmgr mcp-docs`.
**Task 6.2 (sysrs contract)**: applied the identical Phase 1/2/3 mechanical change to the 4 spots
  the merge brought in still on the old shape: `_update_sysrs`/`_set_status_sysrs`/
  `_set_classification_sysrs` (drop `new_doc = SysrsDocument(...)`, `return new_frontmatter`,
  `-> SysrsFrontmatter`; `_update_sysrs`'s whole-body/range branches had the same now-unused
  `body` binding Phase 2 found in the other 11 domains, fixed the same way -- dropped the
  assignment, kept the bare validating `Sysrs.from_text(...)` call) and
  `sysrs/tools/create_sysrs.py`'s `create_sysrs` (same pattern, `body` still used for
  `slugify(body.text)` as in every other `create_<d>` tool; `description=`/docstring Returns
  updated with the same "frontmatter only (no body); use `get_sysrs`" clause every other
  `create_<d>` tool got in Phase 3).
**Task 6.3 (sysrs tests)**: `tests/general/tools/test_update.py`/`test_set_status.py` were
  missing `frontmatter_type=SysrsFrontmatter, document_type=SysrsDocument` on their merged-in
  `sysrs` `_Case` (the mandatory fields this feature's Phase 4 added) -- added both, which
  automatically extends the existing shared-loop frontmatter-only assertions to `sysrs` with no new
  test methods; `test_set_classification.py`'s `_CASES` rebuild in Task 6.1 already covered this.
  `tests/sysrs/tools/test_create_sysrs.py`'s `test_builds_frontmatter_and_returns_document` fixed
  exactly like every other domain's own Phase 3/4 fix: `assertIsInstance(result, SysrsFrontmatter)`,
  dropped the `.frontmatter.`/`.body.` indirection, added `assertNotIsInstance(result,
  SysrsDocument)` + `assertFalse(hasattr(result, "body"))`, and switched the body-text check to
  `get_sysrs(result.id).body.text`. `tests/sysrs/tools/test_integration.py`'s ~20
  `.frontmatter.X`/`.body.X` reads on `create_sysrs`/`update`/`set_status`/`set_classification`'s
  own return values fixed the same way Phase 2/3 fixed the other six domains' `test_integration.py`
  files (`.frontmatter.X` -> `.X`; `.body.X` rewritten to fetch via `get_sysrs(id)` first).
  `tests/sysrs/prompts/test_create_sysrs.py`/`test_update_sysrs.py` needed no change (narration-only
  text checks, never touch a tool's return value). The full suite run then surfaced two more sysrs
  test files the task's own instructions said not to touch pre-emptively unless they actually
  failed: `tests/sysrs/tools/test_get_sysrs.py` and `test_list_sysrs.py`, both calling
  `created.frontmatter.id` on `create_sysrs`'s own (now frontmatter-only) return value -- fixed the
  same `.frontmatter.id` -> `.id` way, leaving every other untouched file in `tests/sysrs/` (models,
  resources, `test__io.py`/`test__lock.py`/`test__paths.py`/`test__write.py`/
  `test_get_sysrs_example.py`/`test_get_sysrs_template.py`/`test_parse_sysrs.py`/
  `test_validate_sysrs.py`) green without modification, confirming none of them call the tools this
  feature changes.
**Task 6.4 (AGENTS.md)**: found the stale "its eleven non-`adr` adapters" wording in the
  `general/` bullet's own Phase-5-added sentence (a leftover from before `sysrs` existed); fixed to
  "twelve". Every other domain-count number in that same paragraph (`dev`'s own "twelve whole-body
  domains", "all thirteen", "twelve `get_<d>` tools", "all thirteen, incl. `get_adr`") was already
  correct from the clean (non-conflicting) merge and left untouched.
**Task 6.5 (docs + gate)**: `specmgr docs` (458 module files + `GENERATED.md`) and
  `specmgr mcp-docs` (`docs/MCP.md`) regenerated, replacing the placeholder `--theirs` content from
  Task 6.1 with genuinely current output. Full quality gate green: `ruff format --check` (1627
  files already formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py
  --min-confidence 60` (no findings), `python -m unittest discover -v -s tests -t . -p "test_*.py"`
  (3293 tests, up from 3071 pre-merge -- the ~220 new tests are `sysrs`'s own suite merged in from
  `dev` -- all passing).
The merge is left uncommitted, fully staged (`git add -A`), for the orchestrator to review and
finish (per this phase's own instructions: do not run `git commit`).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 23:59:00.000+02:00 - (Phase 6) Resolved the 4 generated-doc merge conflicts with `--theirs` rather than hand-merging

`docs/MCP.md` and 3 `docs/api/biz.dfch.specmgr.general.tools.*.md` files conflicted during the
`origin/dev` merge purely because both branches' source changes touched the same generated
sections. Rather than hand-merge these derived files (which would require re-deriving exactly what
`specmgr docs`/`specmgr mcp-docs` would produce anyway), resolved them arbitrarily with
`git checkout --theirs` and immediately regenerated all of them for real via `specmgr docs`/
`specmgr mcp-docs` once the source conflicts were fixed -- the `--theirs` pick was never meant to
be the final content, only a way to unblock the merge; the task's own instructions explicitly
sanctioned this ("resolve them any way that lets the merge proceed ... regenerate ... which will
overwrite whatever you picked with the correct, current content anyway").

#### 2026-09-02 23:57:00.000+02:00 - (Phase 5) Ticked ACC-005 based on pre-existing tests, without adding new ones

Phase 4 left ACC-005 unchecked because it didn't go looking for "nothing was written" coverage
specifically. Rather than writing new tests myself (Phase 4 already closed test-writing for this
feature, and the plan's own instructions for Phase 5 say to investigate, not expand scope), I
searched for and found pre-existing tests -- in `test_update.py`, `test_set_status.py`,
`test_set_classification.py`, and all 11 `test_create_<d>.py` files -- that already assert both
halves of ACC-005 (the actionable exception is still raised, and the file is left untouched/never
created). Since this coverage predates this feature and was never touched by Phases 2-4 (which only
changed success-path returns), I judged it sufficient evidence that REQ-005/ACC-005 held throughout
without needing to author anything new, and ticked the checkbox on that basis.

#### 2026-09-02 23:55:00.000+02:00 - Placed `feat`'s `update`/`set_status` frontmatter-only assertions in `test_integration.py`, not the generic test files (Phase 4)

`tests/general/tools/test_update.py`'s and `tests/general/tools/test_set_status.py`'s own
`_CASES` lists both, pre-existing before this feature, exclude `feat` (its folder-per-document
fixture/addressing strategy differs from the other ten domains' flat-file `_seed`/`_doc_path`
helpers) -- `feat`'s coverage of the generic `update`/`set_status` tools already lived solely in
`tests/feat/tools/test_integration.py`'s lifecycle walkthrough. Rather than bolt a parallel,
one-off `feat` case onto either generic test file's data-driven `_CASES` (a structural change
beyond this test-only phase's scope) or invent a new test file, added the three frontmatter-only
assertions directly to `test_integration.py`'s existing `update(...)`/`set_status(...)` call
sites -- consistent with the plan's own instruction to extend an existing, naturally-fitting test
rather than duplicate structure. `set_classification`'s own `_CASES` already included `feat`
before this phase, so no equivalent judgment call was needed there.

#### 2026-09-02 23:20:00.000+02:00 - Left each `create_<d>` module docstring's `:class:` cross-reference to `XxxDocument` alone (Phase 3)

Each `create_<d>.py` module docstring's opening paragraph says something like "there is no in-memory cache of a parsed `:class:`~biz.dfch.specmgr.req.models.v1.ReqDocument`` -- the `.md` file itself is always the source of truth". Task 3.1 removed the `XxxDocument` *import* (now genuinely unused in the tool's code) but this prose reference to the class name is still an accurate, general statement about the codebase's I/O pattern (no caching), not a claim that this specific tool constructs a `XxxDocument` -- and Sphinx `:class:` roles resolve by fully-qualified path, not local import, so the docstring still renders correctly without the import. Left unchanged rather than rewritten, since the plan's task list only calls for changing the function's own Returns section and the `description=` text, not the module docstring's introductory paragraph.

#### 2026-09-02 22:45:00.000+02:00 - Dropped the unused `body` binding rather than keeping a dead variable (Phase 2)

Removing the `new_doc = XxxDocument(frontmatter=new_frontmatter, body=body)` line per the Phase 1 contract left the preceding `body = Xxx.from_text(format_text(...))` binding in `update.py` genuinely unused (an `F841` finding across all 11 domains, both the whole-body and range branches) -- `body`'s only prior use was building the now-removed `XxxDocument`. Fixed by dropping the assignment and keeping the bare `Xxx.from_text(format_text(...))` call for its validation side effect (it still raises `AssertionError`/`pydantic.ValidationError` on invalid content, which is the only thing that call was ever needed for per the Design Notes' point 2). This is a direct, mechanical consequence of the Phase 1 contract, not a new design decision -- documented here because it wasn't spelled out explicitly in the plan's per-adapter change list.

#### 2026-09-02 22:40:00.000+02:00 - Fixed broader breakage beyond the three named test files (Phase 2)

The plan named `tests/general/tools/test_update.py`/`test_set_status.py`/`test_set_classification.py` as the tests to fix for Task 2.5. Running the full suite surfaced six cross-domain integration tests (`vcr`/`prb`/`dec`/`gol`/`sop`/`feat`) and one prompt test (`feat`'s `update_feat`) that also call the generic `update`/`set_status` tools directly and asserted `.frontmatter.*`/`.body.*` on the return value -- these broke for the same root reason (return value is now frontmatter-only) and were in scope for "the full test suite MUST be green" even though not individually named. Fixed the same way: `.frontmatter.X` -> `.X` on the tool's own return value, and `.body.X` assertions (which have nothing left to read since the return value carries no body) rewritten to fetch the current document via the domain's own `get_<d>(id)` tool first, then assert against that. This preserves each test's original intent (the body was actually persisted) without adding new coverage, consistent with the phase's "only fix what breaks" instruction.

#### 2026-09-02 22:10:00.000+02:00 - Formalized frontmatter-only return contract (Phase 1)

Made explicit, beyond what was already decided, that Phases 2/3 should not just change return type annotations but should also remove the now-pointless `new_doc = XxxDocument(frontmatter=new_frontmatter, body=body)` construction line in every adapter/tool, returning `new_frontmatter` directly instead -- confirmed by reading every in-scope domain's `document.py` that no `XxxDocument` class defines a `model_validator`/`field_validator`, so that construction step performs no cross-field validation today and would become dead code (an unused-variable lint/vulture finding) once the return statement no longer needs it.

#### 2026-09-02 00:00:00.000Z - Dropped ADR from scope

ADR-specific mutating tools (create_adr, update_frontmatter, update_section, option_create/option_read/option_update/option_delete, set_status's adr branch) are excluded from this feature, since ADR's own mechanism is expected to be reworked/phased out separately -- no benefit to updating it now.

#### 2026-09-02 00:00:00.000Z - Frontmatter-only over diff/patch

Chose a uniform "return frontmatter only, omit body" response shape over a bespoke per-tool payload (e.g. success flag + id/path + updated, or a diff/patch of changed lines): frontmatter is bounded in size and this is far simpler and more consistent to implement across all in-scope tools than custom payload shapes or diff generation.

### Related PRs / Commits

- [Issue #69](https://github.com/dfch/biz.dfch.SpecMgr/issues/69): tracking issue for this feature.
