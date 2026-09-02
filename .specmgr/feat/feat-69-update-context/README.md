---
classification: null
created: '2026-09-02 21:49:41.712+02:00'
id: feat-69-update-context
status: done
type: feat
updated: '2026-09-03 00:10:00.000+02:00'
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

- [x] ACC-001: After a successful `update` call, the response contains the document's frontmatter only -- no body content.
- [x] ACC-002: After a successful `set_status` call, the response contains the document's frontmatter only (reflecting the new status/updated) -- no body content.
- [x] ACC-003: After a successful `set_classification` call, the response contains the document's frontmatter only (reflecting the new classification/updated) -- no body content.
- [x] ACC-004: After a successful `create_<d>` call, the response contains the newly generated frontmatter only -- no body content.
- [x] ACC-005: A validation/parse error from any of the above still returns the existing detailed error message, unchanged.
- [x] ACC-006: `delete` and all ADR-specific tools are verified unchanged by this feature (regression check, not new behavior).
- [x] ACC-007: Tests updated/added across all eleven whole-body domains plus the three generic tools to assert frontmatter-only responses.

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

- [x] Task 4.1: Update/add unit tests asserting frontmatter-only responses for update/set_status/set_classification/`create_<d>` across all 11 domains.
- [x] Task 4.2: Add a regression test confirming `delete` and ADR tools are unaffected.
- [x] Task 4.3: Run the full test suite plus `ruff format --check`/`ruff check`/`vulture` before moving to Phase 5.

#### Phase 5: Docs

- [x] Task 5.1: Regenerate `docs/api/` + `docs/GENERATED.md` via `specmgr docs`.
- [x] Task 5.2: Update AGENTS.md bullets/README mentions of write-tool return shapes if any exist.
- [x] Task 5.3: Run the full test suite (final validation) plus `ruff format --check`/`ruff check`/`vulture` before considering the feature done.

## Progress

### Current Status

**As of 2026-09-02**: Feature drafted from GitHub issue #69. Root cause confirmed by reading source: `update`, `set_status`, `set_classification`, and every per-domain `create_<d>` tool return the fully re-parsed document (frontmatter + body) on every successful write; `delete` already returns a minimal path string, and ADR-specific tools are out of scope for this feature. Approach agreed: all in-scope tools switch to a frontmatter-only response (small, bounded size) instead of frontmatter+body (unbounded, growing with document size); error paths are untouched. No prompts currently document the old response shape, so no prompt changes are needed. **Phase 1 (design) is complete**: the frontmatter-only contract is formalized in Design Notes (return type change, removal of the now-pointless `XxxDocument(...)` wrapping construction, no new models needed, error paths untouched by design) and verified against every domain's `document.py`; Task 1.2's prompt-shape check is confirmed clean. **Phase 2 (generic tools) is complete**: `update`, `set_status` (its 11 non-adr adapters; the `adr` branch is unchanged), and `set_classification` all now return the domain's `XxxFrontmatter` object directly instead of the full `XxxDocument`. Full test suite green (3070 tests), ruff/vulture clean. **Phase 3 (per-domain `create_<d>` tools) is complete**: all 11 `create_<d>` tools now return the domain's `XxxFrontmatter` object directly instead of the full `XxxDocument`. Full test suite green (3070 tests), ruff/vulture clean. **Phase 4 (tests) is complete**: every in-scope test file now carries explicit, positive assertions (`assertIsInstance(result, XxxFrontmatter)` + `assertNotIsInstance(result, XxxDocument)` + `assertFalse(hasattr(result, "body"))`) proving the frontmatter-only contract, plus explicit regression assertions that `delete`/ADR tools are unaffected. Full test suite green (3071 tests), ruff/vulture clean. **Phase 5 (docs) is complete, and the feature is done**: `specmgr docs`/`specmgr mcp-docs` confirmed zero drift (Phases 2-4's pre-commit hooks already kept `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md` current on every prior commit); `AGENTS.md`'s `general/` bullet gained one new sentence stating that `update`/`set_status` (its eleven non-`adr` adapters)/`set_classification`/every `create_<d>` tool now return frontmatter-only on success, citing `feat-69-update-context`, with the `adr` branch and ADR-specific tools explicitly excluded; `README.md` needed no change (verified by search, no existing text described the old return shape). Final quality gate all green: `ruff format --check`, `ruff check`, `vulture`, and the full suite (3071 tests). ACC-005 re-investigated and now checked: existing tests already assert that a validation/structural failure raises (`AssertionError`/`pydantic.ValidationError`) *and* leaves the on-disk file byte-identical/writes nothing at all, across `update` (`test_update.py`'s `test_structural_failure_raises_and_leaves_file_byte_identical`/`test_field_validation_failure_raises_and_leaves_file_byte_identical`/`test_status_not_settable_through_update`), `set_status` (`test_set_status.py`'s equivalent `before`/`assertEqual(path.read_text(...), before)` pattern), `set_classification` (`test_set_classification.py`, same pattern), and all 11 `create_<d>` domains (each `test_create_<d>.py` has a `test_*_raises_and_writes_nothing` pair) -- these predate this feature (feat-27-validation and earlier) and were never touched by Phases 2-4 since they only touch success-path code, so they demonstrate REQ-005/ACC-005 held throughout. All seven acceptance criteria are now satisfied; the feature is complete.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 (Phase 5) - Docs verified current, AGENTS.md updated, ACC-005 confirmed satisfied -- feature done

Completed Phase 5 (Tasks 5.1-5.3), the final phase.

- **Task 5.1**: ran `uv run --frozen specmgr docs` and `uv run --frozen specmgr mcp-docs` from a
  clean tree (after Phase 4's last commit `36cca8e`); `git status --short`/`git diff --stat` showed
  zero changes afterward -- confirming `docs/api/`, `docs/GENERATED.md`, and `docs/MCP.md` were
  already fully current, since the repo's pre-commit hooks already ran both generators on every
  prior commit in this feature. No drift found; nothing to stage.
- **Task 5.2**: searched `AGENTS.md` and `README.md` for existing prose describing what
  `update`/`set_status`/`set_classification`/`create_<d>` return on success. Confirmed: `README.md`
  has no such text at all (no change needed); `AGENTS.md`'s only "return"-related hits besides the
  `general/` bullet are the eleven `get_<d>(..., raw=True)` mentions (an unrelated, pre-existing
  parameter on the read-only tools) and the `delete`-returns-a-path mention -- none describe the
  in-scope tools' old full-document shape. Added one new sentence to `AGENTS.md`'s `general/` bullet
  (immediately after the `general/tools/` tool list, before `general/resources/`) stating that
  `update`, `set_status` (its eleven non-`adr` adapters), `set_classification`, and every
  per-domain `create_<d>` tool now return the domain's frontmatter object only (no body) on a
  successful write, with the `adr` dispatch branch of `set_status` and every ADR-specific tool
  (`create_adr`, `update_frontmatter`, `update_section`, the `option_*` tools) explicitly excluded
  and still returning the full document with `body` intact -- cited as `(feat-69-update-context)`,
  matching the file's existing citation convention. No per-domain bullet (`req/`, `uc/`, etc.) was
  touched, per the task's own instruction, since none of them describe any tool's return shape today.
- **Task 5.3**: final quality gate, all green -- `ruff format --check` (1541 files already
  formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (no
  findings), `python -m unittest discover -v -s tests -t . -p "test_*.py"` (3071 tests, all passing
  -- same count as the end of Phase 4, since Phase 5 touched no test files).
- **ACC-005 re-investigation**: Phase 4 left ACC-005 unchecked, noting it "did not find/verify
  dedicated error-path coverage." Searched `tests/general/tools/test_error_context.py` (confirms
  `create_<d>`/`update`/`set_status`/`validate_<d>` still raise `AssertionError`/
  `pydantic.ValidationError` with domain+tool-prefixed actionable messages, per feat-27-validation)
  plus every in-scope domain's own test files for a stronger "and nothing gets written" assertion.
  Found it already present, universally: `tests/general/tools/test_update.py`'s
  `test_structural_failure_raises_and_leaves_file_byte_identical`,
  `test_field_validation_failure_raises_and_leaves_file_byte_identical`, and
  `test_status_not_settable_through_update` all capture the on-disk file's content before calling
  `update` with invalid content, assert the expected exception is raised, then assert the file is
  byte-identical afterward, across every domain in `_CASES`; `tests/general/tools/test_set_status.py`
  and `tests/general/tools/test_set_classification.py` both have the equivalent
  `before = path.read_text(...)` / `assertEqual(path.read_text(...), before)` pattern around their
  own validation-failure tests; and all 11 `tests/<d>/tools/test_create_<d>.py` files have a
  `test_*_raises_and_writes_nothing`-named test pair (structural + field-validation) confirming
  `create_<d>` raises and creates no file at all on invalid content. All of this coverage predates
  this feature (feat-27-validation and earlier) and was never touched by Phases 2-4, since those
  phases only changed success-path `return` statements -- so it demonstrates REQ-005/ACC-005 held
  throughout this feature's work without requiring any new test. ACC-005 is now checked.

All seven acceptance criteria (ACC-001 through ACC-007) are satisfied. The feature is complete;
`Current Status` and the plan's frontmatter `status` are updated to reflect that.

#### 2026-09-02 23:55:00.000+02:00 - Phase 4 done: explicit frontmatter-only assertions added across all in-scope tests

Completed Phase 4 (Tasks 4.1-4.3). Phases 2/3 already fixed every test that broke from the
return-shape change (rewriting `.frontmatter.X`/`.body.X` reads, and swapping
`assertIsInstance(result, XxxDocument)` to `assertIsInstance(result, XxxFrontmatter)` where a
test happened to touch that). Phase 4's job was to go one step further: add explicit, *positive*
assertions -- for each of the 14 in-scope tools (`update`, `set_status`, `set_classification`,
and all 11 `create_<d>`), a block of three assertions next to the existing
`assertIsInstance(result, XxxFrontmatter)`:
`self.assertIsInstance(result, XxxFrontmatter)` (already present everywhere checked),
`self.assertNotIsInstance(result, XxxDocument)` (a genuinely new negative check -- confirmed it
did not exist anywhere before this phase), and `self.assertFalse(hasattr(result, "body"))`
(confirms the response is structurally bounded, not merely "the same type with an empty body" --
verified `hasattr` is `False` on `ReqFrontmatter` before relying on it everywhere else, since
Pydantic frontmatter models declare no `body` field).

- **`create_<d>` (all 11 domains)**: each domain's own `tests/<d>/tools/test_create_<d>.py`
  already had a `test_builds_frontmatter_and_returns_document` test asserting
  `assertIsInstance(result, XxxFrontmatter)`; added the two new assertions immediately after it
  in all 11 files (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`, `dec`, `sop`, `feat`, `vcr`),
  importing each domain's `XxxDocument` class alongside the already-imported `XxxFrontmatter`.
- **`update`**: `tests/general/tools/test_update.py`'s `_CASES` list (covering 10 of the 11
  whole-body domains -- `feat` is tested separately via `tests/feat/tools/test_integration.py`,
  since its fixture/addressing strategy differs from the other ten's flat-file `_seed`/`_doc_path`
  helpers) is genuinely data-driven; extended the shared `_Case` dataclass with
  `frontmatter_type`/`document_type` fields, populated them for all 10 cases, and added the three
  assertions once in `TestUpdateWholeBody.test_replaces_body_preserving_id_type_status_created_version`
  (the one test that actually captures `update`'s own return value) -- covering all 10 domains
  through the existing `for case in _CASES:` loop, not 10 near-duplicate test methods. Added the
  same three assertions to `tests/feat/tools/test_integration.py`'s own `update(...)` call (step
  4 of its lifecycle walkthrough) for `feat`'s coverage.
- **`set_status`**: same data-driven pattern in `tests/general/tools/test_set_status.py`'s
  `TestSetStatusWholeBodyDomains` class (its `_CASES` also excludes `feat`, mirroring `update`'s
  own test file) -- extended `_Case` the same way and added the three assertions once in
  `test_changes_status_bumps_updated_leaves_body_untouched`. Added the same three assertions to
  `tests/feat/tools/test_integration.py`'s `set_status(...)` call (step 5) for `feat`'s coverage.
  The ADR-specific `TestSetStatusAdr` class was deliberately left alone for the frontmatter-only
  assertions (out of scope) but gained the Task 4.2 regression assertion instead (see below).
- **`set_classification`**: same data-driven pattern in
  `tests/general/tools/test_set_classification.py`'s `TestSetClassificationWholeBodyDomains`
  class -- this file's `_CASES` already included `feat` (unlike `update`'s/`set_status`'s own),
  so all 11 domains are covered through the single data-driven assertion block added to
  `test_sets_classification_bumps_updated_leaves_body_untouched`.
- **Task 4.2 (delete/ADR regression)**: added `self.assertIsInstance(result, str)` to
  `tests/general/tools/test_delete.py`'s `test_delete_returns_deleted_path_and_removes_the_document`
  (delete's minimal-payload contract was already exercised via `assertEqual(result, str(target))`
  but never explicitly type-checked). Added `self.assertIsInstance(result, Adr)` plus a `.body`
  equality check to `tests/general/tools/test_set_status.py`'s
  `TestSetStatusAdr.test_changes_plain_status_with_superseded_by_none` (the ADR branch's success
  path). Added a new `test_response_is_full_document_with_body_intact` test method to
  `tests/adr/tools/test_create_adr.py` confirming `create_adr` still returns the full `Adr`
  document with `.body`/`.frontmatter` both intact (inspected `models/adr/v1/adr.py` first to
  confirm `Adr`'s exact `frontmatter`/`body` attribute names). Confirmed by inspection (no new
  tests needed) that `update_frontmatter`/`update_section`/`option_create`/`option_read`/
  `option_update`/`option_delete` -- all in `adr/tools/`, never touched by Phases 2/3 since they
  live outside `general/tools/` -- already assert full-document-with-body return shapes in their
  existing test files (`test_update_frontmatter.py`'s/`test_update_section.py`'s own
  `.frontmatter.*`/`.body.*` assertions on their `create_adr`/`update_frontmatter`/
  `update_section` return values; the four `option_*` tools return bare strings/lists by design,
  not documents, so there is no document-shape claim to regress-test for them at all).

Quality gate, all green: `ruff format --check` (1541 files already formatted), `ruff check` (all
checks passed -- one `F401` self-inflicted during drafting, an unused `FeatFrontmatter`/
`FeatDocument` import added to `test_update.py` before realizing `feat` is not in that file's
`_CASES`; removed), `vulture src/ whitelist.py --min-confidence 60` (no findings),
`python -m unittest discover -v -s tests -t . -p "test_*.py"` (3071 tests -- one more than
Phase 3's 3070, from the new `test_create_adr.py` regression method -- all passing).

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

#### 2026-09-02 (Phase 5) - Ticked ACC-005 based on pre-existing tests, without adding new ones

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
