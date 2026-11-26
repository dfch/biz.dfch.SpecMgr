# History: MCP write tools return the full document on every call, filling up context quickly

#### 2026-09-02 23:57:00.000+02:00 - (Phase 5) Docs verified current, AGENTS.md updated, ACC-005 confirmed satisfied -- feature done

Completed Phase 5 (Tasks 5.1-5.3), the final phase. **Task 5.1**: ran `uv run --frozen specmgr docs` and `uv run --frozen specmgr mcp-docs` from a
  clean tree (after Phase 4's last commit `36cca8e`); `git status --short`/`git diff --stat` showed
  zero changes afterward -- confirming `docs/api/`, `docs/GENERATED.md`, and `docs/MCP.md` were
  already fully current, since the repo's pre-commit hooks already ran both generators on every
  prior commit in this feature. No drift found; nothing to stage.
**Task 5.2**: searched `AGENTS.md` and `README.md` for existing prose describing what
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
**Task 5.3**: final quality gate, all green -- `ruff format --check` (1541 files already
  formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (no
  findings), `python -m unittest discover -v -s tests -t . -p "test_*.py"` (3071 tests, all passing
  -- same count as the end of Phase 4, since Phase 5 touched no test files).
**ACC-005 re-investigation**: Phase 4 left ACC-005 unchecked, noting it "did not find/verify
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
Pydantic frontmatter models declare no `body` field). **`create_<d>` (all 11 domains)**: each domain's own `tests/<d>/tools/test_create_<d>.py`
  already had a `test_builds_frontmatter_and_returns_document` test asserting
  `assertIsInstance(result, XxxFrontmatter)`; added the two new assertions immediately after it
  in all 11 files (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`, `dec`, `sop`, `feat`, `vcr`),
  importing each domain's `XxxDocument` class alongside the already-imported `XxxFrontmatter`.
**`update`**: `tests/general/tools/test_update.py`'s `_CASES` list (covering 10 of the 11
  whole-body domains -- `feat` is tested separately via `tests/feat/tools/test_integration.py`,
  since its fixture/addressing strategy differs from the other ten's flat-file `_seed`/`_doc_path`
  helpers) is genuinely data-driven; extended the shared `_Case` dataclass with
  `frontmatter_type`/`document_type` fields, populated them for all 10 cases, and added the three
  assertions once in `TestUpdateWholeBody.test_replaces_body_preserving_id_type_status_created_version`
  (the one test that actually captures `update`'s own return value) -- covering all 10 domains
  through the existing `for case in _CASES:` loop, not 10 near-duplicate test methods. Added the
  same three assertions to `tests/feat/tools/test_integration.py`'s own `update(...)` call (step
  4 of its lifecycle walkthrough) for `feat`'s coverage.
**`set_status`**: same data-driven pattern in `tests/general/tools/test_set_status.py`'s
  `TestSetStatusWholeBodyDomains` class (its `_CASES` also excludes `feat`, mirroring `update`'s
  own test file) -- extended `_Case` the same way and added the three assertions once in
  `test_changes_status_bumps_updated_leaves_body_untouched`. Added the same three assertions to
  `tests/feat/tools/test_integration.py`'s `set_status(...)` call (step 5) for `feat`'s coverage.
  The ADR-specific `TestSetStatusAdr` class was deliberately left alone for the frontmatter-only
  assertions (out of scope) but gained the Task 4.2 regression assertion instead (see below).
**`set_classification`**: same data-driven pattern in
  `tests/general/tools/test_set_classification.py`'s `TestSetClassificationWholeBodyDomains`
  class -- this file's `_CASES` already included `feat` (unlike `update`'s/`set_status`'s own),
  so all 11 domains are covered through the single data-driven assertion block added to
  `test_sets_classification_bumps_updated_leaves_body_untouched`.
**Task 4.2 (delete/ADR regression)**: added `self.assertIsInstance(result, str)` to
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

Completed Phase 3 (Tasks 3.1-3.3). Applied the Phase 1 contract mechanically to all 11 per-domain `create_<d>` tools: `req/tools/create_req.py`, `uc/tools/create_uc.py`, `tsk/tools/create_tsk.py`, `qa/tools/create_qa.py`, `prb/tools/create_prb.py`, `gol/tools/create_gol.py`, `rsk/tools/create_rsk.py`, `dec/tools/create_dec.py`, `sop/tools/create_sop.py`, `feat/tools/create_feat.py`, `vcr/tools/create_vcr.py`: each tool's `-> XxxDocument` return annotation changed to `-> XxxFrontmatter`; the `new_doc = XxxDocument(frontmatter=new_frontmatter, body=body)` line removed; `return new_doc` changed to `return new_frontmatter`. The preceding `body = Xxx.from_text(format_text(content))` binding stays exactly as-is in every file (unlike Phase 2's `update.py`), since `body.text` (or, for `create_feat`, `feature_title(body.text)`) is still needed to derive the filename slug -- no `F841` finding resulted. The now-fully-unused `XxxDocument` import removed from each file's models import line (confirmed via grep that no other reference to `XxxDocument` remained -- module docstrings still mention the class name in a `:class:` cross-reference/prose sense, which is fine since it is documentation about the general "no in-memory cache" pattern, not a code reference); `XxxFrontmatter` imports and the body-model imports (`Requirement`, `UseCase`, `Task`, `Qa`, `Prb`, `Goal`, `Risk`, `Decision`, `Feature`, `Sop`, `Vcr`) kept. `create_feat.py`'s extra logic (optional caller-chosen `id`, `FileExistsError` pre-write check, `feat_create_lock()`) is otherwise untouched -- only the same four mechanical changes applied. Each tool's `description=` text gained one short clarifying clause ("Returns the newly created document's frontmatter only (no body); use the corresponding `get_<d>` tool to fetch the full document afterward."), matching Phase 2's phrasing style for `update`/`set_status`/`set_classification`; each docstring's Returns section rewritten to name the `XxxFrontmatter` type, note the id now lives directly on `.id` (not nested under `.frontmatter.id`), and point at the corresponding `get_<d>` tool.
Fixed every existing test that broke because `create_<d>`'s return value is now the frontmatter object directly, not a `XxxDocument` wrapper. Beyond each domain's own `test_create_<d>.py` (all 11), the full-suite run surfaced widespread breakage in every domain's `test_get_<d>.py`/`test_list_<d>.py` (which seed fixtures via `create_<d>` and then read `.frontmatter.id`/`.frontmatter.X` off that seed value), six cross-domain `test_integration.py` files (`dec`, `gol`, `prb`, `sop`, `feat`, `vcr` -- their `create_<d>` call's own return value was asserted with `.frontmatter.*`/`.body.*`, plus already-fixed-in-Phase-2 `update`/`set_status` result assertions that referenced `created.frontmatter.*`), two `feat`-specific files (`test_set_feat_id.py`, whose `set_feat_id` return value is unchanged but whose `create_feat`-seeded `created.frontmatter.*` reads needed fixing; `test_list_feat.py`), two `feat/prompts/` walkthrough tests (`test_create_feat.py`, `test_update_feat.py`), and five generic-tool files whose fixtures seed via every domain's `create_<d>` (`tests/general/tools/test_update.py`, `test_set_status.py`, `test_set_classification.py`, `test_delete.py`, `test_error_context.py`) plus `tests/regression/test_issue_27.py`. In every case the fix was the same: `.frontmatter.X` on the tool's own `create_<d>` return value became `.X`; the handful of `.body.X` assertions on that same return value (which have nothing left to read, since the return value carries no body at all) were rewritten to call the domain's own `get_<d>(id)` tool first and assert against the freshly fetched full document's `.body.X` instead -- preserving each test's original intent without expanding coverage, exactly the pattern Phase 2 used. `assertIsInstance(created, XxxDocument)` checks on a `create_<d>` return value became `assertIsInstance(created, XxxFrontmatter)`, with the corresponding import swapped (or, where the module also uses `XxxDocument` elsewhere -- e.g. `dec`'s/`gol`'s/`sop`'s/`vcr`'s/`feat`'s integration tests, which still call `parse_<d>`/`get_<d>_example` and assert on those results -- both `XxxDocument` and `XxxFrontmatter` are imported side by side). Every `get_<d>`/`parse_<d>`/`list_<d>` test's own assertions on *those* tools' still-unchanged return values, and every ADR-specific test, are untouched.
Quality gate, all green: `ruff format --check` (1541 files already formatted, after one reformat of `tests/general/tools/test_update.py` for two lines that now fit under the 120-char limit once `created.frontmatter.` shrank to `created.`), `ruff check` (all checks passed, no new findings -- `body` stayed genuinely used in every `create_<d>` file, so no `F841`), `vulture src/ whitelist.py --min-confidence 60` (no findings), `python -m unittest discover -v -s tests -t . -p "test_*.py"` (3070 tests, all passing).


#### 2026-09-02 22:45:00.000+02:00 - Phase 2 done: generic tools (update/set_status/set_classification) return frontmatter-only

Completed Phase 2 (Tasks 2.1-2.5). Applied the Phase 1 contract mechanically to all three generic dispatch tools in `general/tools/`: `update.py`: all 11 `_update_<d>` adapters' return annotation changed `-> XxxDocument` to `-> XxxFrontmatter`; the `new_doc = XxxDocument(frontmatter=new_frontmatter, body=body)` line removed from both the whole-body and range branches of each adapter; `return new_doc` changed to `return new_frontmatter`. The now-pointless `body = Xxx.from_text(...)` bindings (both branches, all 11 domains) became `F841` unused-variable findings once the document-wrapping was removed, since `body` was only ever used to build the removed `XxxDocument(...)` -- fixed by dropping the assignment and keeping the bare validating call (`Xxx.from_text(format_text(...))`) for its side effect (raising on invalid content), matching the Design Notes' point that this validation step performs no cross-field logic today but must still run. The module-level union alias renamed `_UpdateDocument` -> `_UpdateFrontmatter` with every member changed to its `XxxFrontmatter` counterpart; the `_ADAPTERS` dict value type and the public `update()` return annotation updated accordingly; the now-fully-unused `XxxDocument` imports (11 domains) removed, `XxxFrontmatter` imports and the body-model imports (`Requirement`, `UseCase`, `Task`, `Qa`, `Prb`, `Goal`, `Risk`, `Decision`, `Feature`, `Sop`, `Vcr`) kept. `update()`'s `description=` text and docstring Returns section updated to state the frontmatter-only response shape and point callers at the corresponding `get_<d>` tool.
`set_status.py`: the same mechanical change applied to its 11 non-adr adapters (`_set_status_req` .. `_set_status_vcr`); `_set_status_adr` and the `Adr` union member are explicitly untouched (out of scope, per the feature's Scope section and the plan's explicit exception). The union alias renamed `_SetStatusDocument` -> `_SetStatusFrontmatter`, keeping `Adr` in the union; `_ADAPTERS` dict value type and the public `set_status()` return annotation updated; the 11 now-unused `XxxDocument` imports removed. `set_status()`'s `description=` text and docstring Returns section updated, explicitly noting the `adr` branch still returns the full `Adr` document (unchanged).
`set_classification.py`: the same mechanical change applied to all 11 adapters (no `adr` branch exists in this tool at all). Union alias renamed `_SetClassificationDocument` -> `_SetClassificationFrontmatter`; `_ADAPTERS` dict value type and the public `set_classification()` return annotation updated; the 11 now-unused `XxxDocument` imports removed; `description=`/docstring Returns updated.
Also fixed every existing test that broke because `result` (the tool's return value) is now the frontmatter object directly, not a `XxxDocument` wrapper: `tests/general/tools/test_update.py`, `test_set_status.py` (its non-adr `TestSetStatusWholeBodyDomains` test only -- the ADR-specific tests are unchanged, since `_set_status_adr` still returns the full `Adr`), and `test_set_classification.py` all had their `result.frontmatter.X`/`result.body.X` assertions on the tool's own direct return value rewritten to `result.X` (dropping the now-nonexistent `.frontmatter` indirection; `.body` assertions on the *tool's own return value* no longer apply since the body is gone). Beyond the three generic-tool test files the plan named, the full-suite run surfaced six cross-domain integration tests and one prompt test that also call `update`/`set_status` directly and asserted on their return value's `.frontmatter.*`/`.body.*` -- `tests/vcr/tools/test_integration.py`, `tests/prb/tools/test_integration.py`, `tests/dec/tools/test_integration.py`, `tests/gol/tools/test_integration.py`, `tests/sop/tools/test_integration.py`, `tests/feat/tools/test_integration.py`, and `tests/feat/prompts/test_update_feat.py`. Their `.frontmatter.*` assertions on the tool's own return value became `.X` the same way; their `.body.*` assertions (which no longer have anything to read, since the return value no longer carries a body at all) were rewritten to call the domain's own `get_<d>(id)` tool first and assert against the freshly fetched full document's `.body.*` instead -- preserving each test's original intent (confirming the body was actually persisted/updated) without expanding coverage. Every `create_<d>`/`get_<d>`/`parse_<d>` test's own `.frontmatter.*`/`.body.*` assertions (on `create_<d>`'s own still-unchanged return value, Phase 3's job) and every ADR-specific test are untouched.
Quality gate, all green: `ruff format --check` (1541 files already formatted), `ruff check` (all checks passed, after fixing 11 new `F841` findings from the removed `XxxDocument` wrapping making `body` locals genuinely unused), `vulture src/ whitelist.py --min-confidence 60` (no findings), `python -m unittest discover -v -s tests -t . -p "test_*.py"` (3070 tests, all passing).


#### 2026-09-02 22:12:00.000+02:00 - Phase 1 done: formalized frontmatter-only return contract

Completed Phase 1 (Design the shared minimal-response shape): documented the concrete, unambiguous contract Phases 2/3 must follow (see Design Notes) -- the return type annotation for every in-scope tool/adapter changes from the domain's `XxxDocument` to its `XxxFrontmatter`; internally each adapter still builds/validates the body exactly as today, but the now-pointless `XxxDocument(...)` wrapping construction (confirmed by reading every in-scope domain's `document.py` to have zero `model_validator`/`field_validator` cross-field logic) is removed and `return new_frontmatter` used instead; no new Pydantic model classes are needed; only the success-path return statement/type annotation changes, not internal helper signatures; error/validation-failure paths already raise exceptions rather than returning a value, so REQ-005/ACC-005 need zero code changes. Also verified via `grep -rn` across all 44 `*/prompts/*.py` files that no prompt documents or depends on the old full-document response shape -- confirming the existing claim, no prompt changes needed.


#### 2026-09-02 21:55:52.000+02:00 - Added Depends On (feat-27-validation)

Added a `Dependencies` / `Depends On` entry referencing `feat-27-validation`, since this feature's error paths (REQ-005/ACC-005) rely on the actionable, field-path/line-referenced error messages that feature introduced staying intact and unchanged. Also opened GitHub issue #70 to track a validation error-surfacing gap found while drafting this feature (a bare `create_<d>` token outside backticks fails with an unhelpful generic error instead of the actionable detail feat-27-validation promises) -- tracked separately, out of scope for this feature.


#### 2026-09-02 00:00:00.000Z - Created

Feature drafted from GitHub issue #69, covering the generic `update`/`set_status`/`set_classification` tools and all 11 per-domain `create_<d>` tools switching to a frontmatter-only success response. ADR-specific tools and `delete` are out of scope.
