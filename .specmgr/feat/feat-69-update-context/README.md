---
classification: null
created: '2026-09-02 21:49:41.712+02:00'
id: feat-69-update-context
status: planning
type: feat
updated: '2026-09-02 23:20:00.000+02:00'
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

### Acceptance Criteria

- [ ] ACC-001: After a successful `update` call, the response contains the document's frontmatter only -- no body content.
- [ ] ACC-002: After a successful `set_status` call, the response contains the document's frontmatter only (reflecting the new status/updated) -- no body content.
- [ ] ACC-003: After a successful `set_classification` call, the response contains the document's frontmatter only (reflecting the new classification/updated) -- no body content.
- [ ] ACC-004: After a successful `create_<d>` call, the response contains the newly generated frontmatter only -- no body content.
- [ ] ACC-005: A validation/parse error from any of the above still returns the existing detailed error message, unchanged.
- [ ] ACC-006: `delete` and all ADR-specific tools are verified unchanged by this feature (regression check, not new behavior).
- [ ] ACC-007: Tests updated/added across all eleven whole-body domains plus the three generic tools to assert frontmatter-only responses.

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

### Task List

#### Phase 1: Design the shared minimal-response shape

- [x] Task 1.1: Decide/document the frontmatter-only return type contract shared by update/set_status/set_classification/`create_<d>` (Design Notes).
- [x] Task 1.2: Confirm via test run that no prompt currently documents the old full-document response shape (already verified: none do).

#### Phase 2: Generic tools (general/tools/)

- [x] Task 2.1: Change `update` to return frontmatter-only across all 11 whole-body domains.
- [x] Task 2.2: Change `set_status` to return frontmatter-only across all 11 whole-body domains (adr branch unchanged).
- [x] Task 2.3: Change `set_classification` to return frontmatter-only across all 11 whole-body domains.
- [x] Task 2.4: Update each tool's MCP `description=` text and docstring Returns section.
- [x] Task 2.5: Run the full test suite (`uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`) plus `ruff format --check`/`ruff check`/`vulture` before moving to Phase 3.

#### Phase 3: Per-domain `create_<d>` tools

- [x] Task 3.1: Change all 11 `create_<d>` tools to return frontmatter-only.
- [x] Task 3.2: Update each tool's MCP `description=` text and docstring Returns section.
- [x] Task 3.3: Run the full test suite plus `ruff format --check`/`ruff check`/`vulture` before moving to Phase 4.

#### Phase 4: Tests

- [ ] Task 4.1: Update/add unit tests asserting frontmatter-only responses for update/set_status/set_classification/`create_<d>` across all 11 domains.
- [ ] Task 4.2: Add a regression test confirming `delete` and ADR tools are unaffected.
- [ ] Task 4.3: Run the full test suite plus `ruff format --check`/`ruff check`/`vulture` before moving to Phase 5.

#### Phase 5: Docs

- [ ] Task 5.1: Regenerate `docs/api/` + `docs/GENERATED.md` via `specmgr docs`.
- [ ] Task 5.2: Update AGENTS.md bullets/README mentions of write-tool return shapes if any exist.
- [ ] Task 5.3: Run the full test suite (final validation) plus `ruff format --check`/`ruff check`/`vulture` before considering the feature done.

## Progress

### Current Status

**As of 2026-09-02**: Feature drafted from GitHub issue #69. Root cause confirmed by reading source: `update`, `set_status`, `set_classification`, and every per-domain `create_<d>` tool return the fully re-parsed document (frontmatter + body) on every successful write; `delete` already returns a minimal path string, and ADR-specific tools are out of scope for this feature. Approach agreed: all in-scope tools switch to a frontmatter-only response (small, bounded size) instead of frontmatter+body (unbounded, growing with document size); error paths are untouched. No prompts currently document the old response shape, so no prompt changes are needed. **Phase 1 (design) is complete**: the frontmatter-only contract is formalized in Design Notes (return type change, removal of the now-pointless `XxxDocument(...)` wrapping construction, no new models needed, error paths untouched by design) and verified against every domain's `document.py`; Task 1.2's prompt-shape check is confirmed clean. **Phase 2 (generic tools) is complete**: `update`, `set_status` (its 11 non-adr adapters; the `adr` branch is unchanged), and `set_classification` all now return the domain's `XxxFrontmatter` object directly instead of the full `XxxDocument`. Full test suite green (3070 tests), ruff/vulture clean. **Phase 3 (per-domain `create_<d>` tools) is complete**: all 11 `create_<d>` tools now return the domain's `XxxFrontmatter` object directly instead of the full `XxxDocument`. Full test suite green (3070 tests), ruff/vulture clean. Phase 4 (tests) has not started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 23:20:00.000+02:00 - Phase 3 done: all 11 `create_<d>` tools return frontmatter-only

Completed Phase 3 (Tasks 3.1-3.3). Applied the Phase 1 contract mechanically to all 11 per-domain `create_<d>` tools:

- `req/tools/create_req.py`, `uc/tools/create_uc.py`, `tsk/tools/create_tsk.py`, `qa/tools/create_qa.py`, `prb/tools/create_prb.py`, `gol/tools/create_gol.py`, `rsk/tools/create_rsk.py`, `dec/tools/create_dec.py`, `sop/tools/create_sop.py`, `feat/tools/create_feat.py`, `vcr/tools/create_vcr.py`: each tool's `-> XxxDocument` return annotation changed to `-> XxxFrontmatter`; the `new_doc = XxxDocument(frontmatter=new_frontmatter, body=body)` line removed; `return new_doc` changed to `return new_frontmatter`. The preceding `body = Xxx.from_text(format_text(content))` binding stays exactly as-is in every file (unlike Phase 2's `update.py`), since `body.text` (or, for `create_feat`, `feature_title(body.text)`) is still needed to derive the filename slug -- no `F841` finding resulted. The now-fully-unused `XxxDocument` import removed from each file's models import line (confirmed via grep that no other reference to `XxxDocument` remained -- module docstrings still mention the class name in a `:class:` cross-reference/prose sense, which is fine since it is documentation about the general "no in-memory cache" pattern, not a code reference); `XxxFrontmatter` imports and the body-model imports (`Requirement`, `UseCase`, `Task`, `Qa`, `Prb`, `Goal`, `Risk`, `Decision`, `Feature`, `Sop`, `Vcr`) kept. `create_feat.py`'s extra logic (optional caller-chosen `id`, `FileExistsError` pre-write check, `feat_create_lock()`) is otherwise untouched -- only the same four mechanical changes applied. Each tool's `description=` text gained one short clarifying clause ("Returns the newly created document's frontmatter only (no body); use the corresponding `get_<d>` tool to fetch the full document afterward."), matching Phase 2's phrasing style for `update`/`set_status`/`set_classification`; each docstring's Returns section rewritten to name the `XxxFrontmatter` type, note the id now lives directly on `.id` (not nested under `.frontmatter.id`), and point at the corresponding `get_<d>` tool.

Fixed every existing test that broke because `create_<d>`'s return value is now the frontmatter object directly, not a `XxxDocument` wrapper. Beyond each domain's own `test_create_<d>.py` (all 11), the full-suite run surfaced widespread breakage in every domain's `test_get_<d>.py`/`test_list_<d>.py` (which seed fixtures via `create_<d>` and then read `.frontmatter.id`/`.frontmatter.X` off that seed value), six cross-domain `test_integration.py` files (`dec`, `gol`, `prb`, `sop`, `feat`, `vcr` -- their `create_<d>` call's own return value was asserted with `.frontmatter.*`/`.body.*`, plus already-fixed-in-Phase-2 `update`/`set_status` result assertions that referenced `created.frontmatter.*`), two `feat`-specific files (`test_set_feat_id.py`, whose `set_feat_id` return value is unchanged but whose `create_feat`-seeded `created.frontmatter.*` reads needed fixing; `test_list_feat.py`), two `feat/prompts/` walkthrough tests (`test_create_feat.py`, `test_update_feat.py`), and five generic-tool files whose fixtures seed via every domain's `create_<d>` (`tests/general/tools/test_update.py`, `test_set_status.py`, `test_set_classification.py`, `test_delete.py`, `test_error_context.py`) plus `tests/regression/test_issue_27.py`. In every case the fix was the same: `.frontmatter.X` on the tool's own `create_<d>` return value became `.X`; the handful of `.body.X` assertions on that same return value (which have nothing left to read, since the return value carries no body at all) were rewritten to call the domain's own `get_<d>(id)` tool first and assert against the freshly fetched full document's `.body.X` instead -- preserving each test's original intent without expanding coverage, exactly the pattern Phase 2 used. `assertIsInstance(created, XxxDocument)` checks on a `create_<d>` return value became `assertIsInstance(created, XxxFrontmatter)`, with the corresponding import swapped (or, where the module also uses `XxxDocument` elsewhere -- e.g. `dec`'s/`gol`'s/`sop`'s/`vcr`'s/`feat`'s integration tests, which still call `parse_<d>`/`get_<d>_example` and assert on those results -- both `XxxDocument` and `XxxFrontmatter` are imported side by side). Every `get_<d>`/`parse_<d>`/`list_<d>` test's own assertions on *those* tools' still-unchanged return values, and every ADR-specific test, are untouched.

Quality gate, all green: `ruff format --check` (1541 files already formatted, after one reformat of `tests/general/tools/test_update.py` for two lines that now fit under the 120-char limit once `created.frontmatter.` shrank to `created.`), `ruff check` (all checks passed, no new findings -- `body` stayed genuinely used in every `create_<d>` file, so no `F841`), `vulture src/ whitelist.py --min-confidence 60` (no findings), `python -m unittest discover -v -s tests -t . -p "test_*.py"` (3070 tests, all passing).

#### 2026-09-02 22:45:00.000+02:00 - Phase 2 done: generic tools (update/set_status/set_classification) return frontmatter-only

Completed Phase 2 (Tasks 2.1-2.5). Applied the Phase 1 contract mechanically to all three generic dispatch tools in `general/tools/`:

- `update.py`: all 11 `_update_<d>` adapters' return annotation changed `-> XxxDocument` to `-> XxxFrontmatter`; the `new_doc = XxxDocument(frontmatter=new_frontmatter, body=body)` line removed from both the whole-body and range branches of each adapter; `return new_doc` changed to `return new_frontmatter`. The now-pointless `body = Xxx.from_text(...)` bindings (both branches, all 11 domains) became `F841` unused-variable findings once the document-wrapping was removed, since `body` was only ever used to build the removed `XxxDocument(...)` -- fixed by dropping the assignment and keeping the bare validating call (`Xxx.from_text(format_text(...))`) for its side effect (raising on invalid content), matching the Design Notes' point that this validation step performs no cross-field logic today but must still run. The module-level union alias renamed `_UpdateDocument` -> `_UpdateFrontmatter` with every member changed to its `XxxFrontmatter` counterpart; the `_ADAPTERS` dict value type and the public `update()` return annotation updated accordingly; the now-fully-unused `XxxDocument` imports (11 domains) removed, `XxxFrontmatter` imports and the body-model imports (`Requirement`, `UseCase`, `Task`, `Qa`, `Prb`, `Goal`, `Risk`, `Decision`, `Feature`, `Sop`, `Vcr`) kept. `update()`'s `description=` text and docstring Returns section updated to state the frontmatter-only response shape and point callers at the corresponding `get_<d>` tool.
- `set_status.py`: the same mechanical change applied to its 11 non-adr adapters (`_set_status_req` .. `_set_status_vcr`); `_set_status_adr` and the `Adr` union member are explicitly untouched (out of scope, per the feature's Scope section and the plan's explicit exception). The union alias renamed `_SetStatusDocument` -> `_SetStatusFrontmatter`, keeping `Adr` in the union; `_ADAPTERS` dict value type and the public `set_status()` return annotation updated; the 11 now-unused `XxxDocument` imports removed. `set_status()`'s `description=` text and docstring Returns section updated, explicitly noting the `adr` branch still returns the full `Adr` document (unchanged).
- `set_classification.py`: the same mechanical change applied to all 11 adapters (no `adr` branch exists in this tool at all). Union alias renamed `_SetClassificationDocument` -> `_SetClassificationFrontmatter`; `_ADAPTERS` dict value type and the public `set_classification()` return annotation updated; the 11 now-unused `XxxDocument` imports removed; `description=`/docstring Returns updated.

Also fixed every existing test that broke because `result` (the tool's return value) is now the frontmatter object directly, not a `XxxDocument` wrapper: `tests/general/tools/test_update.py`, `test_set_status.py` (its non-adr `TestSetStatusWholeBodyDomains` test only -- the ADR-specific tests are unchanged, since `_set_status_adr` still returns the full `Adr`), and `test_set_classification.py` all had their `result.frontmatter.X`/`result.body.X` assertions on the tool's own direct return value rewritten to `result.X` (dropping the now-nonexistent `.frontmatter` indirection; `.body` assertions on the *tool's own return value* no longer apply since the body is gone). Beyond the three generic-tool test files the plan named, the full-suite run surfaced six cross-domain integration tests and one prompt test that also call `update`/`set_status` directly and asserted on their return value's `.frontmatter.*`/`.body.*` -- `tests/vcr/tools/test_integration.py`, `tests/prb/tools/test_integration.py`, `tests/dec/tools/test_integration.py`, `tests/gol/tools/test_integration.py`, `tests/sop/tools/test_integration.py`, `tests/feat/tools/test_integration.py`, and `tests/feat/prompts/test_update_feat.py`. Their `.frontmatter.*` assertions on the tool's own return value became `.X` the same way; their `.body.*` assertions (which no longer have anything to read, since the return value no longer carries a body at all) were rewritten to call the domain's own `get_<d>(id)` tool first and assert against the freshly fetched full document's `.body.*` instead -- preserving each test's original intent (confirming the body was actually persisted/updated) without expanding coverage. Every `create_<d>`/`get_<d>`/`parse_<d>` test's own `.frontmatter.*`/`.body.*` assertions (on `create_<d>`'s own still-unchanged return value, Phase 3's job) and every ADR-specific test are untouched.

Quality gate, all green: `ruff format --check` (1541 files already formatted), `ruff check` (all checks passed, after fixing 11 new `F841` findings from the removed `XxxDocument` wrapping making `body` locals genuinely unused), `vulture src/ whitelist.py --min-confidence 60` (no findings), `python -m unittest discover -v -s tests -t . -p "test_*.py"` (3070 tests, all passing).

#### 2026-09-02 22:12:00.000+02:00 - Phase 1 done: formalized frontmatter-only return contract

Completed Phase 1 (Design the shared minimal-response shape): documented the concrete, unambiguous contract Phases 2/3 must follow (see Design Notes) -- the return type annotation for every in-scope tool/adapter changes from the domain's `XxxDocument` to its `XxxFrontmatter`; internally each adapter still builds/validates the body exactly as today, but the now-pointless `XxxDocument(...)` wrapping construction (confirmed by reading every in-scope domain's `document.py` to have zero `model_validator`/`field_validator` cross-field logic) is removed and `return new_frontmatter` used instead; no new Pydantic model classes are needed; only the success-path return statement/type annotation changes, not internal helper signatures; error/validation-failure paths already raise exceptions rather than returning a value, so REQ-005/ACC-005 need zero code changes. Also verified via `grep -rn` across all 44 `*/prompts/*.py` files that no prompt documents or depends on the old full-document response shape -- confirming the existing claim, no prompt changes needed.

#### 2026-09-02 21:55:52.000+02:00 - Added Depends On (feat-27-validation)

Added a `Dependencies` / `Depends On` entry referencing `feat-27-validation`, since this feature's error paths (REQ-005/ACC-005) rely on the actionable, field-path/line-referenced error messages that feature introduced staying intact and unchanged. Also opened GitHub issue #70 to track a validation error-surfacing gap found while drafting this feature (a bare `create_<d>` token outside backticks fails with an unhelpful generic error instead of the actionable detail feat-27-validation promises) -- tracked separately, out of scope for this feature.

#### 2026-09-02 00:00:00.000Z - Created

Feature drafted from GitHub issue #69, covering the generic `update`/`set_status`/`set_classification` tools and all 11 per-domain `create_<d>` tools switching to a frontmatter-only success response. ADR-specific tools and `delete` are out of scope.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 23:20:00.000+02:00 - Left each create_<d> module docstring's `:class:` cross-reference to `XxxDocument` alone (Phase 3)

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
