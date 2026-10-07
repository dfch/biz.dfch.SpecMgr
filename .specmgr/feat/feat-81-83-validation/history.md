# History: Consolidate Validation Tools and Fix Opaque Validation/List Failures (#81, #83)

#### 2026-09-04 18:00:00.000Z - Phase 6 (Post-Review Remediation) planned: REQ-009/010/011, ACC-009/010/011, and the Phase 6 task list added following an independent quality review
An independent review of this already-closed-out feature (conducted after Phase 5) re-verified the shipped artifacts directly -- running the real quality gate, reading the actual implementation, and probing the generic `validate` tool live -- rather than relying on this document's own self-audit log. It confirmed the core design and full test suite (3342 tests, `ruff`/`vulture` clean) are sound, but found three concrete, reproducible gaps: (1) 11 of 12 domain `__init__.py` module docstrings still list the retired `validate_<d>` tool as existing, missed by Task 2.3/5.2's audits since those only covered `AGENTS.md`/`server.py`/prompts; (2) `validate`'s `yaml.YAMLError` messages are not enriched the way `parse_<d>`'s are, for malformed frontmatter YAML specifically, because each adapter's `has_frontmatter` probe runs outside any enrichment context -- reproduced live, and confirmed untested (zero `yaml`/`YAMLError` mentions in `test_validate.py`); (3) ADR 519d1206's own Confirmation section commits to a live-OpenCode-session re-check that was never recorded as performed. Added REQ-009/ACC-009 (docstring fix), REQ-010/ACC-010 (`_detect_frontmatter` helper + missing test coverage, kept as a private helper local to `general/tools/validate.py` per an explicit scoping decision -- see Decisions Made), and REQ-011/ACC-011 (ADR amendment) accordingly, plus a new Phase 6 task list (Tasks 6.1-6.6) and a Design Notes addendum recording the three findings in full. `status` reverted from `done` to `in-progress` in frontmatter; `version` bumped to `1.1.0`. This entry is planning-only -- no code, tests, or other files outside this plan document were touched; Phase 6's own tasks remain `[ ]` until implemented.

#### 2026-09-04 17:00:00.000Z - Phase 5 (Verification and Closeout) complete: Tasks 5.1-5.3 done -- feature closed out
Closed out the whole feature. Task 5.1 re-ran the full quality gate with no
code changes needed: `ruff format --check` (1652 files already formatted),
`ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (no output), and the full `pytest -n auto --cov=src`
suite (3342 passed, unchanged from Phase 4's own count -- no test edits were
needed in this phase).
Task 5.2 re-ran `specmgr docs`, `specmgr mcp-docs`, and `specmgr adr-toc`;
`git status`/`git diff` showed zero drift after all three, confirming
Phases 2-4 already left `docs/api/`, `docs/GENERATED.md`, `docs/MCP.md`, and
`docs/adr/README.md` fully current. Audited `AGENTS.md` in full: confirmed
the generic `validate` tool is mentioned for all twelve domains, every
`validate_<d>` mention is correctly phrased as "former"/removed (none
describe a still-existing per-domain tool), all twelve `list_<d>` bullets
mention `error_count` and a resolved `path` field (`feat`'s own bullet
explicitly notes `path` is no longer `feat`-only), and the "Still genuinely
missing" section already correctly names the generic `validate` tool rather
than the retired thirteen per-domain names. No edits were needed. Audited
`CHANGELOG.md`'s `[Unreleased]` section in full: confirmed all three pieces
of information from Tasks 2.7/3.4/4.5 are present, consciously squashed
into one "Added" entry (the new `validate` tool), one "Removed" entry (the
twelve retired `validate_<d>` tools, itemized by name), and two "Changed"
entries (`list_<d>`'s `total`/`error_count` semantics change; `path`/`error`
fields on all twelve domains' summaries plus `FeatSummary.path`'s
resolved-path retrofit) rather than kept as three separate per-phase
entries -- explicitly permitted by this task's own wording. No edits were
needed.
Task 5.3 posted one outcome comment each to GitHub issues #81
(<https://github.com/dfch/biz.dfch.SpecMgr/issues/81#issuecomment-5545854938>)
and #83
(<https://github.com/dfch/biz.dfch.SpecMgr/issues/83#issuecomment-5545855566>),
summarizing the generic `validate(type, content, full)` tool replacing the
twelve per-domain `validate_<d>` tools, the new ADR
(078bf395-0a5f-4afd-84f6-b7a2191a00e6) recording that consolidation
decision, `list_<d>`'s `error_count`/inline-failed-entry fix, and the
`path`-field parity across all twelve whole-body domains; issue #83's
comment additionally covered the investigation finding that both repro
cases were confirmed to reproduce as client-observed symptoms but were
root-caused to a client-side MCP tool-error-rendering gap (not a specmgr
server-side regression), and that `validate`'s non-raising `{valid, errors}`
design is a client-independent workaround for that gap (ADR
519d1206-4d2a-4500-9046-6db635209996). Neither issue was closed, per this
task's own instruction -- that is left to a human.
Confirmed, on a final read-through, every ACC-001 through ACC-007 checkbox
was already `[x]` with a verdict note from Phases 1-4; found one genuine
gap -- ACC-008 (REQ-008's regression tests) was still `[ ]` even though the
regression tests it describes were already implemented and passing (Task
2.6's `TestValidateIssue83Regressions`, Task 3.3's mixed valid/unparseable
directory tests for `req`/`rsk`) -- and marked it `[x]` with a verdict note
identifying exactly which tests satisfy it. No new test code was written;
this was a documentation-only correction.
This closes the feature: all 5 phases and all 8 REQs/ACCs (ACC-001 through
ACC-008) are done, with a clean final quality gate and zero outstanding
documentation drift.

#### 2026-09-04 16:00:00.000Z - Phase 4 (`list_<d>` Path Field Parity) complete: Tasks 4.1-4.5 done
Closed out REQ-007/ACC-007. Task 4.1 (spot-check, no new field-population code):
confirmed by reading every one of the other eleven whole-body domains'
`list_<d>.py` files that Phase 3 already wired `path=str(path.resolve())` on
every successful-entry construction, and confirmed by reading every one of
their `test_list_<d>.py` files that each already asserts
`Path(summary.path).is_absolute()` (successful entries) and
`Path(failed.path) == broken_path.resolve()` (failed entries) -- no gaps
found across `req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`vcr`/`sysrs`.
Task 4.2 retrofitted `feat`: `feat/tools/list_feat.py`'s `_to_summary` now
builds `path=str(path.resolve())` (previously unresolved `str(path)`), and
its `_to_failed_summary` no longer passes `resolve=False` to
`default_failed_summary` (that parameter was removed entirely, see Decisions
Made below); `feat/models/v1/summary.py`'s `FeatSummary` no longer redeclares
its own `path: str` field -- it is now purely inherited from the shared
`DocSummary` base, like every other whole-body domain's summary -- and its
module/class docstrings were rewritten to describe this as history, not a
live divergence.
Task 4.3 revised `DocSummary.ref`'s docstring
(`general/models/summary.py`) to drop the "callers must not read this off
disk themselves, only pass it to the matching domain's `get_<domain>` tool"
policy sentence, replacing it with a note that `path` (the sibling field)
now exposes the real filesystem path directly for a caller that wants it,
per REQ-007.
Task 4.4 added/extended tests: `tests/feat/tools/test_list_feat.py` gained
an `is_absolute()` assertion for every summary in its malformed-folder test,
plus an exact `Path(failed.path) == (broken / README_FILENAME).resolve()`
equality assertion for the failed entry (mirroring every other domain's own
pattern), and its module docstring's stale Phase-3-vs-Phase-4 framing was
corrected; `tests/general/models/test_summary.py` gained a new
`TestFeatSummarySharesDocSummaryBase` class asserting `FeatSummary` now
declares the exact same field set as every other whole-body domain's
summary (`id`/`title`/`status`/`ref`/`path`/`error`) and no longer
redeclares `path` in its own class-level `__annotations__`;
`tests/general/tools/test__listing.py`'s `test_path_stays_unresolved_when_resolve_is_false`
test (exercising the now-removed `resolve` parameter) was replaced with a
single `test_path_is_always_resolved` test. The other eleven domains needed
no new tests -- Task 4.1 confirmed their Phase 3 coverage was already
complete.
Task 4.5 added a `CHANGELOG.md` `[Unreleased]` entry: amended Phase 3's own
"Changed" `list_<d>` bullet to drop its now-stale "`feat`/`FeatSummary`
already had its own `path` field; it keeps its existing unresolved form for
now, retrofitted separately" parenthetical (no longer true), and added a new
dedicated "Changed" bullet documenting `FeatSummary.path`'s field-removal/
resolved-path retrofit.
Updated `AGENTS.md` (Task 4.1's own scope): all twelve `list_<d>` bullets
(including `rsk`'s and `feat`'s own) now mention the shared, resolved `path`
field alongside their existing `error_count` mention; `feat`'s own bullet's
stale "`FeatSummary` adds one extra field beyond every other domain's
summary, `path: str`... a deliberate divergence" paragraph was rewritten to
state that `path` is no longer `feat`-only, while still noting `feat`'s own
direct-editing workflow treats it as a first-class, sanctioned entry point
by original design (not merely an incidental convenience gained later, as
for the other eleven domains).
Quality gate: `ruff format --check` (clean, 1652 files already formatted),
`ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (no output), the full `pytest -n auto --cov=src` suite
(3342 tests, up from 3339 immediately before this phase's test edits -- net
+3: +1 `test_path_is_always_resolved` replacing the removed
`test_path_stays_unresolved_when_resolve_is_false` in `test__listing.py`,
+1 `is_absolute()`/resolved-equality assertion pair in `test_list_feat.py`
(no new test method), +3 new test methods in the new
`TestFeatSummarySharesDocSummaryBase` class in `test_summary.py`), `specmgr docs` (regenerated exactly the four touched modules' API pages --
`feat.models.v1.summary`, `feat.tools.list_feat`,
`general.models.summary`, `general.tools._listing` -- plus
`docs/GENERATED.md`), `specmgr mcp-docs` (`docs/MCP.md` unchanged -- no
tool descriptions/signatures changed), and `specmgr adr-toc`
(`docs/adr/README.md` unchanged) all green.
Design decision made during this phase, not already covered by the plan's
own Design Notes (added to Decisions Made below): simplified
`general/tools/_listing.py::default_failed_summary` by removing its
`resolve: bool = True` parameter entirely, rather than leaving it as dead
flexibility once `feat` (its only caller ever passing `resolve=False`) was
retrofitted to always resolve -- every one of the twelve domains'
`to_failed_summary` callbacks now calls `default_failed_summary` with the
same, simplified two-or-three-positional-plus-`ref`-keyword signature.

#### 2026-09-04 15:00:00.000Z - Phase 3 (`list_<d>` Failure Reporting) complete: Tasks 3.1-3.4 done
Implemented REQ-006's `list_<d>` failure-reporting fix and the shared
listing infrastructure it depends on (Task 3.1): `general/tools/_listing.py`
(`build_summaries(paths, read, to_summary, to_failed_summary, error_types= (AssertionError, ValidationError, yaml.YAMLError))`, `default_failed_summary()`,
`FAILED_TO_PARSE_MARKER`), mirroring `general/tools/_doc_paths.py::find_doc_path_by_id`'s
callback-based generalization; `PagedResult.error_count: int = 0`;
`DocSummary.path: str`/`error: str | None = None` added to the shared base
(`general/models/summary.py`); `general/tools/_paging.py::paginate()` gained
an `error_count: int = 0` parameter threaded straight into the returned
`PagedResult`. All twelve `list_<d>.py` files (`req`/`uc`/`tsk`/`qa`/`prb`/
`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`) now route through
`build_summaries()`, replacing each domain's own copy-pasted try/except/append
loop; a file that fails to parse now appears inline in `results` as a failed
entry (`id=None`, `title`/`status` both `"<failed to parse>"`, `ref`/`path`
populated the same way as a successful entry, `error` carrying the caught
exception's message) rather than being silently skipped, and `total`/
`error_count` reflect the whole directory, independent of paging. Per this
phase's own delegated scope boundary, `feat`'s `FeatSummary.path` keeps its
existing *unresolved* `str(path)` form in this phase (via
`default_failed_summary(..., resolve=False)` for its failed rows) -- the
resolved-path retrofit is explicitly Phase 4, Task 4.2's job -- while the
other eleven domains' successful *and* failed entries both get a brand-new,
`.resolve()`d `path`. `AGENTS.md`'s twelve `list_<d>` bullets each now
mention `error_count`.
Implemented RSK's sentinel-document construction (Task 3.2):
`rsk/tools/_sentinel.py` (`_SENTINEL_RSK_TEXT`, `_SENTINEL_RSK_DOCUMENT`,
`build_failed_rsk_summary()`), a fixed, valid, deliberately
worst-case-severity (`Probability 5`/`Impact 5` in both assessments,
`level_from_product(25)` = `"very high"`) risk document, parsed exactly once
via the real, unmodified `parse_rsk` pipeline, then run through the same
`RskSummary.from_document()` every real row uses before `model_copy`
overriding the fields no document could ever supply. `tests/rsk/tools/test__sentinel.py`
(9 tests) parses `_SENTINEL_RSK_TEXT` directly, independent of `list_rsk`'s
own tests.
Added regression tests (Task 3.3): `req`/`rsk` (the two mandated domains)
each gained a full `test_returns_summaries_and_reports_malformed_file_as_a_failed_entry`
test (asserting `total`/`error_count`, marker `title`/`status`, `ref`,
resolved `path`, `error`) and a dedicated `test_malformed_yaml_frontmatter_is_reported_as_a_failed_entry`
test exercising the `yaml.YAMLError` path specifically (not just a
structural/field-validation failure); every other domain's own pre-existing
`test_list_<d>.py` (`uc`/`tsk`/`qa`/`prb`/`gol`/`dec`/`sop`/`vcr`/`sysrs`/`feat`)
was also updated for the new semantics, since `build_summaries()` broke
their old skip-based assertions outright (a document previously silently
skipped now counts toward `total`). New `tests/general/tools/test__listing.py`
(18 tests) covers `build_summaries()`/`default_failed_summary()` directly.
`tests/general/tools/test_paging.py`/`tests/general/models/test_paged_result.py`/
`tests/general/models/test_summary.py` updated for `error_count`/`path`/`error`;
`AdrSummary`'s own tests were split off into a narrower four-field
expectation, since `adr` is out of scope for this feature and `AdrSummary`
deliberately does not gain `path`/`error` (see Decisions Made below).
Added a `CHANGELOG.md` `[Unreleased]` entry (Task 3.4): a "Changed"
**BREAKING** entry documenting `list_<d>`'s `total`/`error_count` semantics
change.
Quality gate: `ruff format --check` (clean), `ruff check` (all checks
passed), `vulture src/ whitelist.py --min-confidence 60` (no output), the
full `pytest -n auto --cov=src` suite (3340 tests, up from 3308 -- net +32:
+18 `test__listing.py`, +9 `test__sentinel.py`, +5 new/renamed assertions
spread across the twelve `test_list_<d>.py` files and the three
`general/models`/`general/tools` test files), `specmgr docs` (regenerated
`docs/api/`/`docs/GENERATED.md`, two new API pages for `_listing.py`/
`_sentinel.py`), `specmgr mcp-docs` (`docs/MCP.md` unchanged -- no tool
descriptions/signatures changed), and `specmgr adr-toc` (`docs/adr/README.md`
unchanged) all green.
Design decision made during this phase, not already covered by the plan's
own Design Notes (added to Decisions Made below): the RSK sentinel's H1 is
a plain descriptive title, not literally `"<failed to parse>"` -- `title`
is overridden via `model_copy` (a fifth field, alongside `id`/`status`/
`path`/`error`) using the shared `FAILED_TO_PARSE_MARKER` constant, because
writing that literal marker text as a markdown H1 is rejected by
`models/md`'s own raw-HTML guard (a bare `<...>` token parses as
`html_inline`), and every escape-hatch that survives the guard (a code
span, a backslash escape) leaves its own markdown syntax embedded in
`MarkdownSection.text`'s raw-source-derived output instead of yielding the
bare marker string.

#### 2026-09-04 14:00:00.000Z - Phase 2 (Generic `validate` Tool) complete: Tasks 2.1-2.7 done
Implemented the generic, type-dispatched `validate(type, content, full)` tool in
`general/tools/validate.py` for the twelve whole-body domains (`adr` excluded,
`validate_adr` unchanged), covering REQ-003/REQ-004/ACC-003/ACC-004: twelve
private `_validate_<d>` adapters (verbatim ports of the retired per-domain
tool bodies, `wrap_tool_errors(domain=..., tool="validate", channel=...)`
enrichment preserved, but with `tool="validate"` -- the generic tool's own
name -- rather than the retired per-domain tool name, mirroring `update`'s/
`set_status`'s own generic-tool-name convention), a dispatch table, and the
public `validate()` function wrapping each adapter call in
`try`/`except (AssertionError, pydantic.ValidationError, yaml.YAMLError)` that
returns `ValidateResult(valid=False, errors=[ValidationErrorEntry(message=...)])`
on a catch instead of raising; an unsupported `type` (including `"adr"`) is an
explicit `if type not in _ADAPTERS: raise ValueError(...)` check, not a bare
dict-lookup `KeyError` -- this is a deliberate, explicitly-instructed deviation
from `delete`'s/`set_classification`'s own undocumented `KeyError`-for-`"adr"`
behavior (confirmed via their own tests), since ACC-004 explicitly requires a
`ValueError` here and there is no `_path_safety.validate_id` call to piggyback
on (`validate` is content-based, not id-based). Added
`general/models/validate_result.py` (`ValidateResult`/`ValidationErrorEntry`,
greenfield -- no existing non-raising-result precedent in this codebase) and
registered `validate` in `general/tools/__init__.py`.
Created ADR 078bf395-0a5f-4afd-84f6-b7a2191a00e6 (Task 2.2), extending ADR
36905d5b-8057-4294-8665-c7eed5534db0's dispatch-only convention to this
read-only/dry-run tool category; regenerated `docs/adr/README.md` via
`specmgr adr-toc`; updated the Related Decisions placeholder bullet above with
the real id.
Migrated every prompt/test dependent on the twelve retired `validate_<d>`
functions (Task 2.3/2.5): all 24 `create_<d>`/`update_<d>` prompt `.py`
docstrings/descriptions and their packaged `*_instructions.md` data files
(`validate_<d>(content, full=False)` -> `validate(type="<d>", content=content, full=False)`); `AGENTS.md`'s twelve per-domain bullets, the `general/` bullet
(added a `validate` paragraph mirroring `delete`'s own), and the "Still
genuinely missing" section; `server.py`'s own module docstring (per-domain
tool lists, the `general/tools/` paragraph, and the SOP prompts paragraph).
Removed the twelve `<d>/tools/validate_<d>.py` files and their `__init__.py`
imports/`__all__`/docstring mentions (Task 2.4), and their 12 dedicated
`test_validate_<d>.py` files (Task 2.5) -- their fixture bodies
(`_MINIMAL_BODY`/`_MALFORMED_BODY`/`_FULL_DOCUMENT`/bad-field bodies) were
ported into the new `tests/general/tools/test_validate.py` rather than
discarded. Repointed the 5 affected `test_integration.py` files (dec, feat,
sop, sysrs, vcr -- confirmed by search that `prb`'s and `gol`'s own
`test_integration.py` never referenced `validate_<d>`, so the plan's "6 files,
dec/feat/sop/sysrs/vcr plus one more" estimate was one too many), the 3
regression tests (`test_issue_27.py`, `test_issue_70.py`, `test_issue_71.py`),
`tests/general/tools/test_error_context.py`, and (found via the broader
search Task 2.5 itself called for) `tests/sop/prompts/test_create_sop.py`/
`tests/sysrs/prompts/test_create_sysrs.py`.
Added `tests/general/tools/test_validate.py` (Task 2.6): 15 test methods
across 4 classes -- `TestValidateAllDomains` (parameterized over all twelve
domains' ported fixture bodies: valid body-only, valid full document,
structural-failure-returns-`{valid:false}`, field-validation-failure-returns-
`{valid:false}` where a straightforward fixture existed, invalid-frontmatter-
field-when-`full=True`), `TestValidateUnsupportedType` (`type="adr"` and an
arbitrary bogus `type` both raise `ValueError`), `TestValidateFullShapeMismatchRaises`
(`req`/`dec`/`vcr` -- both mismatch directions each raise `ValueError`), and
`TestValidateIssue83Regressions` (the two Phase 1 repro fixtures, reproduced
through the generic tool, asserting `{valid: False, errors: [...]}` with the
enriched message present, never a raised exception). Added a `CHANGELOG.md`
`[Unreleased]` entry (Task 2.7): an "Added" entry for the new `validate` tool
and a "Removed" **BREAKING** entry for the twelve retired `validate_<d>`
tools, matching `delete`'s/`update`'s own precedent wording.
Quality gate: `ruff format --check` (clean), `ruff check` (all checks
passed), `vulture src/ whitelist.py --min-confidence 60` (no output), the
full `unittest discover` suite (3308 tests, up from 3293 -- net +15 new,
-1600ish lines of retired per-domain tests folded into one file), `specmgr docs` (regenerated `docs/api/`/`docs/GENERATED.md`, twelve stale
`validate_<d>` API pages pruned, two new pages added for `validate.py`/
`validate_result.py`), `specmgr adr-toc` (regenerated `docs/adr/README.md`),
and `specmgr mcp-docs` (regenerated `docs/MCP.md`) all green.
Design decision made during this phase, not already covered by the plan's
own Design Notes (added to Decisions Made below): the unsupported-`type`
check in `validate()` deliberately does NOT mirror `delete`'s/
`set_classification`'s own actual runtime behavior (an implicit `KeyError`
from the dispatch-dict lookup for `type="adr"`, confirmed via
`test_set_classification.py::test_adr_type_is_not_supported`) -- it uses an
explicit `if type not in _ADAPTERS: raise ValueError(...)` check instead,
per this phase's own prompt's explicit, repeated instruction that
`validate(type="adr", ...)` must raise `ValueError` "at runtime, not just at
static-type-check time." `update`'s/`set_classification`'s own docstrings
already (inaccurately) claim a `ValueError` for this case, so `validate`'s
explicit check is arguably a corrected precedent, not a deviation from the
documented (if not actual) contract.

#### 2026-09-04 13:00:00.000Z - Task 1.4 done: full inventory of all thirteen `validate_<d>` tools added; Phase 1 complete
Added the Task 1.4 inventory to Design Notes: a table covering all thirteen current `validate_<d>` tools' signatures, per-domain behavior for `full=False`/`full=True`, and the exceptions each lets propagate, plus a consolidated summary of `validate_adr`'s four points of structural divergence from the other twelve (id-based/disk-touching vs. content-based/disk-free, no `full` parameter, `AdrParseError` instead of `AssertionError` as its structural channel, and an additional `AdrNotFoundError` failure mode). This closes REQ-002/ACC-002 and, since Tasks 1.1-1.3 and 1.5 were already done, completes Phase 1 in full. No design decisions were made in this task (pure inventory/documentation); Phase 2 (the generic `validate` tool) has not started.

#### 2026-09-04 12:00:00.000Z - Plan refined a third time following an independent review: ADR task, YAMLError coverage, CHANGELOG tasks, test-migration task, full/type-mismatch test, path-field sequencing note
Refined the plan again, following an independent gap review conducted before Phase 2 implementation begins. Seven concrete gaps were raised and addressed: (1) added a Design Notes sequencing note clarifying that Task 3.1 (Phase 3), not Task 4.1 (Phase 4), is what actually introduces and populates the mandatory `path` field on the shared `DocSummary` base across all twelve domains -- Task 4.1 was reworded from "add the field" to "confirm/spot-check what Task 3.1 already wired," since `build_summaries()`'s callbacks must produce fully-valid model instances immediately in Phase 3, and the RSK sentinel's own Phase 3 `model_copy` already depended on `path` existing; (2) added Task 2.7/3.4/4.5, one `CHANGELOG.md [Unreleased]` entry per phase that ships a breaking change, matching `feat-36-delete`'s and `feat-38-39-41-43-44`'s own established per-phase CHANGELOG convention, which this plan had omitted entirely; (3) added Task 2.5, removing/migrating the 12 dedicated `test_validate_<d>.py` files (~1600 lines) plus the 6 `test_integration.py`, 3 regression, and 1 `test_error_context.py` files that import a `validate_<d>` function directly -- Task 2.4 ("remove the twelve tool files") did not previously account for the parallel test files that would otherwise `ImportError` immediately; (4) added a clarifying sentence to REQ-004 and a cross-reference in Design Notes explaining that `errors` currently holds zero or one entries in practice (each domain's validation performs exactly one guarded parse call), and that the list shape is deliberate forward-compatibility rather than an indication multiple concurrent errors are expected today; (5) added `yaml.YAMLError` to `build_summaries()`'s default `error_types` (Task 3.1, Design Notes) -- confirmed via source that `parse_<d>` genuinely raises it, unwrapped, for malformed frontmatter, and omitting it from the catch set would leave `list_<d>` crashing outright on such a document instead of reporting it as a failed entry, which is exactly issue #83(b)'s complaint; extended Task 3.3 to include a malformed-YAML fixture, and noted (out of scope) that `general/tools/_doc_paths.py::find_doc_path_by_id` shares this same gap today; (6) extended Task 2.6/ACC-004 with a new test, for a representative sample of domains (`req`/`dec`/`vcr`), confirming the `full`/content-shape-mismatch `ValueError` still propagates through the generic tool rather than being swallowed into `{valid: false}` -- and added an explicit exception-class-filtering note to Task 2.1; (7) added Task 2.2, writing a new dedicated ADR for the `validate`-consolidation decision (with a placeholder bullet under Related Decisions pending its assigned id), mirroring `feat-36-delete`'s own precedent of writing a dedicated ADR even where a general dispatch-only convention (36905d5b) already existed. Renumbered the rest of Phase 2 (2.2-2.4 -> 2.3-2.4, plus new 2.5-2.7) and fixed Task 5.2's now-stale "Tasks 2.2/3.1/4.1" cross-reference to "Tasks 2.3/3.1/4.1". No REQ/ACC renumbering was needed beyond extending ACC-003/ACC-004's existing wording in place.

#### 2026-09-04 09:00:00.000Z - Plan refined further: shared listing helper, `list_<d>` total/error_count semantics, RSK sentinel-document design, ACC restructured one-per-REQ
Refined the plan again, before Phase 2 implementation begins. Corrected Task 3.1's incorrect assumption that a shared `list_<d>` listing helper already existed (it did not -- confirmed the try/except/append loop is copy-pasted identically across ten domains); designed a new `general/tools/_listing.py::build_summaries()` helper to replace it, plus `error_count`/`path`/`error` additions to the shared `PagedResult`/`DocSummary` bases rather than duplicated per domain. Resolved `total`'s semantics once failed entries are folded into `results` (it now includes them, a deliberate change from today's "parseable only" meaning, which is exactly what fixes issue #83's silent-zero complaint) and `error_count`'s semantics (counts across the whole directory, mirroring `total`, not just the current page). Worked through, and resolved, why `RskSummary` -- the only domain summary type with fields beyond the shared `DocSummary` base -- cannot represent a failed row via `Optional` fields (rejected: weakens real rows' guarantees too) or fabricated plausible-looking placeholder data (rejected: indistinguishable from real low-severity risk data in an aggregate view); adopted a fixed, valid, deliberately worst-case-severity sentinel RSK document, parsed once through the real `parse_rsk` pipeline (no validation bypass), with only the four fields no document could ever supply (`id`/`status` marker/`path`/`error`) set after the fact -- see Design Notes for the full design and rationale, including a dedicated standalone test for the sentinel document itself. Also folded `validate_feat`'s ad hoc Phase 1 spot-check into Task 1.3, split Task 2.2/5.2's `AGENTS.md` responsibilities so the work isn't deferred to one vague catch-all task, and restructured Acceptance Criteria to exactly one ACC per REQ (previously ACC-003 covered both REQ-003 and REQ-004).

#### 2026-09-03 17:00:00.000Z - Recorded the client-side-defect workaround rationale as an ADR
Wrote ADR 519d1206-4d2a-4500-9046-6db635209996 ("Design `validate` as a non-raising, structured-result tool to work around client-side MCP error-content truncation"), formalizing the reasoning already captured in Design Notes: `validate`'s REQ-003/004 non-raising design exists because of a confirmed, external OpenCode 1.18.27 client-side defect, not as an independently preferred design -- a decision worth a full ADR since the rationale generalizes to any future tool in this repo facing the same need, not just this feature. Cross-referenced the ADR from Design Notes/Related Decisions and from the drafted, unfiled `opencode-issue-mcp-tool-error-truncated.md`.

#### 2026-09-03 16:00:00.000Z - Phase 1 Tasks 1.1-1.3 done: repro confirmed, root cause narrowed to a client-side rendering gap
Reproduced both of issue #83's literal repro bodies against current HEAD (`req` naive-isoformat timestamps via `validate_req`; `dec` em-dash `## Updates` sub-heading via `validate_dec`). In this agent session, both surfaced only as a bare, contentless `"Error executing tool <name>"` message through the normal MCP tool-call interface -- the opaque-failure symptom issue #83 describes. A follow-up raw MCP JSON-RPC inspection (bypassing this session's own tool-calling harness, via the `mcp` SDK's `stdio_client`) proved the specmgr server itself sends the full, `feat-27-validation`-enriched message in the wire-level `CallToolResult`; the truncation happens one layer further out, in the calling agent's own tool-result rendering. `feat-67-70-71`'s "transport forwards unabridged" conclusion is confirmed correct, not regressed. Full detail and rationale for how this reinforces (rather than changes) REQ-003/004's non-raising `validate` design are in Design Notes.

#### 2026-09-03 15:00:00.000Z - Plan refined: design questions resolved ahead of Phase 1
Refined the plan before starting implementation. Corrected a stale "eleven" `validate_<d>` tool count to the actual thirteen (twelve identical-signature whole-body tools plus the structurally-different `validate_adr`). Resolved all of Task 1.5's open design questions plus REQ-007's previously-conditional `path`-field decision -- see Design Notes and "Design questions resolved during plan refinement" below for the resolutions and rationale. Requirements, Acceptance Criteria, Scope, and the Task List were updated to reflect these resolutions.

#### 2026-09-03 14:27:36.412Z - Created
Created from GitHub issues #81 (consolidate validation tools) and #83 (opaque validation errors; `list_<domain>` silently reporting zero on parse failures). Combines both issues into one feature since #83 is referenced by #81 and both concern how validation failures/results are reported by this repo's MCP tools.
