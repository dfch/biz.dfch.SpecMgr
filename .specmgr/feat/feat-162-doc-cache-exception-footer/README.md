---
classification: null
created: '2026-10-01T05:55:44.404+02:00'
id: feat-162-doc-cache-exception-footer
status: planning
type: feat
updated: '2026-10-01T07:10:00.000+02:00'
version: 1.0.0
---

# Feature: Str-Faithful DocCache Exception Reconstruction

## Plan

### Overview

GitHub issue #162: `general/tools/_doc_cache.py::_fresh_exception` re-raises a *reconstructed* exception on every warm cache hit against a previously-failed parse (feat-107-doc-cache, REQ-011). Its `pydantic.ValidationError` reconstruction unconditionally wraps every per-field error detail in a `pydantic_core.PydanticCustomError` before calling `ValidationError.from_exception_data(...)`. That blanket wrap is correct for frontmatter-field errors (already enriched into a custom `"frontmatter_value_error"` kind by `models.md._frontmatter_parse.enrich_frontmatter_validation_error`, which never carried a footer to begin with), but wrong for a genuine **body**-field `ValidationError` (e.g. a domain's own `Body.from_text(...)` model validators): those are recognized, pydantic-core-builtin error kinds, and `str()`-ing one normally appends a trailing `For further information visit https://errors.pydantic.dev/<ver>/v/<type>` line -- a line the custom-error wrap silently drops on every warm re-raise. The module's own docstring premise ("every parse error is already enriched into a custom error type") is therefore false for the body-field case.

Impact: `ParseFailureResult.error` (from `get_<d>`; always a warm read) and `list_<d>`'s failed-row `error` (footer present on the process's first read of that content, footer-less on warm re-reads) differ by exactly the trailing line depending on read order. feat-150-mcp-lifecycle-commands Task 1a.8 (2026-09-26, Option B) qualified the documented "byte-identical" invariant everywhere it was claimed, rather than fixing the reconstruction immediately, and filed this feature's GitHub issue (#162) to carry the deferred fix (Option A). `AssertionError` and `yaml.error.MarkedYAMLError` reconstruction are already exact (positional/keyword round-trip) and are out of scope -- only the `ValidationError` branch is broken.

Likely fix shape (to be confirmed by Phase 100's spike): per field-error detail, attempt reconstruction via a plain, recognized-kind `type=`/`ctx=` pass-through first (letting pydantic-core regenerate its own templated message *and* footer for a genuine builtin kind), and fall back to the current `PydanticCustomError` wrap only when that fails (the already-custom frontmatter case). The exact mechanism needs a short, isolated spike against pydantic-core's real `InitErrorDetails`/`from_exception_data` behavior before being applied inside the shared cache module every domain's read path depends on.

**Coordination note (see Phase 900, last):** feat-170-update-edit-parse-failure (GitHub issue #170, PR #175, implemented in its own git worktree, not yet merged to `dev` as of this writing) independently propagated the exact same "Option B, 2026-09-26, follow-up issue #162" qualified language into 4 more tool files (`general/tools/{update,edit,set_status,set_classification}.py`), a new ADR (`b8c9bfea-6dcf-4158-bfc5-4ec17abb842f`), and 4 more `_strip_pydantic_footer` test-helper copies, none of which this feature's own doc-restoration sweep (Phase 140) can reach, since they live on a different branch/worktree. Phase 900 exists solely so that cleanup is not forgotten once both features have landed.

### Requirements

- REQ-001: `DocCache._fresh_exception`'s `pydantic.ValidationError` branch must reconstruct a fresh exception whose `str()` output is byte-identical to the original exception's `str()` output, for every real parse failure this codebase's own `parse_<domain>` functions can raise -- both a frontmatter-field failure (enriched, custom-typed) and a body-field failure (a recognized pydantic-core builtin kind, which must retain its generated message and, when applicable, its trailing documentation-link footer line).

- REQ-002: The `AssertionError` and `yaml.error.MarkedYAMLError` reconstruction branches are unchanged -- they already round-trip `str()` exactly and are not touched by this feature.

- REQ-003: `ParseFailureResult.error` (from `get_<d>`) and `list_<d>`'s failed-row `error` for the same broken file must be byte-identical in both read orders (list-first and get-first) for all 12 whole-body domains -- replacing feat-150's relaxed, content-based (`_strip_pydantic_footer`) consistency tests with plain `==` identity. "Both orders" means each domain's own cache sees a genuine cold read followed by a genuine warm read, in each direction; a unique per-test temp file (the existing test pattern already uses one) combined with controlling which of `get_<d>`/`list_<d>` is called first is sufficient to produce both orderings within a single test process -- no subprocess/fresh-process isolation is required, since each domain's `DocCache` is keyed by resolved absolute path and a fresh temp file's cache entry never collides with another test's, in the same process.

- REQ-004: `list_<d>()`'s own row `error` text must be stable across repeated calls within one process (no longer footer-on-first-read, footer-less-on-warm-rereads).

- REQ-005: Fresh-exception semantics are preserved -- the reconstruction, not a re-raise of the stored exception instance, remains the mechanism (no shared-traceback mutation across threads/calls).

- REQ-006: Every site that documented the Option B qualification (ADR 9080b37c's Decision Outcome item 3 + Confirmation, the `ParseFailureResult` module+class docstrings, `find_parse_failure`'s docstring, `find_feat_parse_failure`'s docstring, the `repair` prompt/instructions/skill/agent wording, the 12 `get_<d>` tool descriptions/docstrings, `AGENTS.md`, `CHANGELOG.md`, `server.py`'s module docstring, and the regenerated `docs/MCP.md` + `docs/api` pages) is re-tightened back to the unqualified, full byte-identical invariant -- amending ADR 9080b37c in place (same decision, precision fix, not a reversal), not creating a new ADR.

### Acceptance Criteria

- [ ] ACC-001: (REQ-001/REQ-002) A unit test proves cold `str()` == warm `str()` for `pydantic.ValidationError` (both a frontmatter-field and a body-field fixture), `AssertionError`, and `yaml.YAMLError`, in `tests/general/tools/test__doc_cache.py`.

- [ ] ACC-002: (REQ-003) `get_<d>.error == list_<d>`'s failed-row `.error` in **both** orders (list-first and get-first, each order exercised via call ordering against a fresh per-test temp file within the same test process -- see REQ-003) for all 12 whole-body domains, with the 12 `_strip_pydantic_footer`-based relaxed assertions and helper copies removed.

- [ ] ACC-003: (REQ-004) `list_<d>()`'s row `error` text is asserted stable across repeated calls within one process (new or tightened test).

- [ ] ACC-004: (REQ-005) A test proves two reconstructions of the same cached `ValidationError` failure are `is`-distinct exception objects (unchanged behavior, regression guard).

- [ ] ACC-005: (REQ-006) Every site on the doc-restoration list is re-tightened; `specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc` regenerate with no further manual edits needed.

- [ ] ACC-006: Full quality gate green (ruff format/check, vulture, `pytest -n auto`, all three doc generators idempotent).

### Scope

#### Included

- `general/tools/_doc_cache.py`'s `_fresh_exception` function and its module/function docstrings.

- The 12 `tests/<d>/tools/test_get_<d>.py` consistency tests (tightening + helper removal).

- `tests/general/prompts/test_repair.py`'s pinned narration wording: it asserts the exact qualified substring `general/data/general_repair_instructions.md` carries today (`"treat the two texts as the same defect, not byte-equal"`), which Phase 140's re-tightening of that instructions file removes -- feat-150's own original doc-restoration sweep touched this same test file for the same reason (its 2026-09-27 Updates entry, item 12), and this feature's Phase 140 must too.

- New/updated tests in `tests/general/tools/test__doc_cache.py`.

- The full doc-restoration sweep enumerated in REQ-006 (amending ADR 9080b37c in place), plus a new `CHANGELOG.md` `### Fixed` entry under `[Unreleased]` documenting the behavior change itself -- distinct from, and in addition to, re-tightening the *existing*, now-stale `[Unreleased]` entries feat-150 already wrote.

#### Explicitly Out Of Scope

- Any change to `AssertionError`/`yaml.error.MarkedYAMLError` reconstruction (already exact).

- Any change to `DocCache`'s hashing, locking, copy-on-hit, or reconcile/move/invalidate mechanics (feat-107's own, unrelated to this bug).

- Any change to `models/md/_errors.py`'s `wrap_tool_errors` or `models/md/_frontmatter_parse.py`'s `enrich_frontmatter_validation_error`. Both unconditionally wrap every per-field detail in a `PydanticCustomError` the same way `_fresh_exception`'s buggy branch does, but *correctly*: both are rewriting the message itself (prefixing domain/tool/line context) regardless of outcome, so dropping the trailing pydantic documentation-link footer there is an intentional, already-tested side effect of enrichment (see `tests/models/md/test_errors.py`'s `assertNotIn("https://errors.pydantic.dev", ...)`), not an instance of this bug. The Phase 140 doc sweep must not "fix" these just because their docstrings use similar "already enriched" language.

- Cleaning up feat-170's own, independently-introduced copy of the same qualified language right now -- that lives on a separate branch/worktree not yet merged to `dev`. Not skipped, only deferred: see Phase 900's own task.

- Opening a new ADR for this fix -- the existing ADR 9080b37c is amended in place instead (user decision).

### Dependencies

#### Depends On

- feat-107-doc-cache (owns `_fresh_exception` and the `DocCache` module this feature patches).

- feat-150-mcp-lifecycle-commands, Task 1a.8 (the Option B deferral decision that filed this feature's GitHub issue, #162, and the doc-restoration list this feature's Phase 140 re-tightens).

- ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c (amended in place by Phase 140, not superseded).

#### Blocks

- None known to block on this shipping. feat-170-update-edit-parse-failure (GitHub issue #170, PR #175) is NOT blocked by this feature (it already ships correctly under the qualified Option B invariant), but it independently carries the same debt in 4 more files and should adopt this fix's outcome once both have landed -- tracked by Phase 900, a coordination reminder, not a blocking dependency in either direction.

### Design Notes

**Why a spike phase.** `pydantic_core.ValidationError.from_exception_data` and its `InitErrorDetails` input are implemented in Rust (PyO3); their exact behavior for a plain, recognized-kind `type=` string (as opposed to a `PydanticCustomError`-wrapped one) needs to be verified empirically against this codebase's real pydantic version pin before committing to an implementation shape inside the shared cache module every domain's read path depends on. The spike's own pinned test cases (frontmatter-only and body-field) are kept as part of the permanent test suite afterward, not thrown away.

**Pre-spike findings (2026-10-01 plan review, confirmed by live experiment against this repo's pinned pydantic/pydantic-core version).** Three concrete implementation details established before Phase 100 starts, so the spike confirms/applies them rather than rediscovering them from scratch:

- `InitErrorDetails(..., ctx=None)` raises `TypeError: 'None' is not an instance of 'dict'` -- the reconstruction must include the `ctx` key only when the original `error.errors()` detail actually carries one (most builtin kinds do; some, e.g. `missing`, do not), never pass `ctx=detail.get("ctx")` unconditionally.
- `ValidationError.from_exception_data(...)` raises `KeyError: "Invalid error type: '<type>'"` (not some other exception) when `type=` is not one of pydantic-core's own recognized kinds -- this is the specific exception the fallback-to-custom-wrap path must catch.
- Every real `ValidationError` this codebase's own `parse_<domain>` functions raise is architecturally homogeneous, never mixed: `parse_frontmatter(...)` (always producing a 100% `PydanticCustomError`-wrapped error, via `enrich_frontmatter_validation_error`) and a domain body's `Body.from_text(...)` (always producing a 100% raw, recognized-builtin-kind error -- no domain body validator anywhere in this codebase uses `PydanticCustomError`) are two structurally separate validation passes, each raising its own complete exception. A single `ValidationError` combining both kinds of per-field detail does not appear reachable via any real call path in this codebase. Task 100.110's "mixed" case is therefore expected to resolve to "not producible"; the spike should confirm this quickly (and record the confirmation) rather than treat it as open-ended, and the implementation can use a single try/except around reconstructing the *whole* exception (attempt the builtin pass-through for every detail; fall back to the full custom-wrap for every detail only on failure) rather than genuinely mixed per-detail branching.

**Why amend ADR 9080b37c instead of opening a new one.** The ADR's Decision Outcome item 3 already documents the *qualified* claim (Option B, 2026-09-26) as an explicit, known interim state with its own "upgrade-ready: re-tighten per #162's doc-restoration list" language. This feature fully realizes that same decision -- the error-text consistency invariant -- rather than reversing or superseding it, so amending the existing ADR's text in place (the same pattern feat-150 itself used when it first qualified the claim) is the correct move, not a new ADR.

**feat-170 coordination (Phase 900).** feat-170-update-edit-parse-failure is implemented in its own git worktree and was not available to this feature's Phase 140 sweep (different branch, not yet merged to `dev`). It independently re-derived the identical "Option B / follow-up issue #162" wording in 4 more tool files, a new ADR (`b8c9bfea`), and 4 more `_strip_pydantic_footer` test helper copies. Once this feature has merged and feat-170's branch has rebased onto the new `dev`, that branch's own Option B language should be tightened the same way this feature's Phase 140 does for its original 12-domain/`get_<d>` surface -- a short, mechanical follow-up pass, not a design question, but easy to forget since it lives outside this feature's own repo checkout/worktree at the time this plan was written. Phase 900 exists purely to not lose track of it; the exact timing and ownership of that pass is a user call, deliberately not pre-decided here.

### Related Decisions

- ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c -- amended in place by Phase 140 (same decision, precision fix: the qualified error-text claim is re-tightened to the full byte-identical invariant this feature implements).

### Task List

#### Phase 100: Spike -- validate the reconstruction strategy

- [x] Task 100.100: Prototype a plain recognized-kind `type=`/`ctx=` pass-through reconstruction for a `ValidationError`'s per-field details -- applying the `ctx`-omission-when-absent and `KeyError`-on-unrecognized-type handling from this feature's Design Notes "Pre-spike findings" -- falling back to the current `PydanticCustomError` wrap only when the plain pass-through fails (the already-custom frontmatter case), against this codebase's actual pinned pydantic/pydantic-core version.

- [x] Task 100.110: Pin `str(reconstructed) == str(original)` for two fixtures: a frontmatter-only validation failure and a body-field validation failure (recognized builtin kind, footer-bearing). Confirm (per the Design Notes "Pre-spike findings") whether a mixed failure -- both kinds of field error in one `ValidationError` -- is producible under this codebase's two-stage frontmatter/body parsing; record the outcome explicitly either way rather than leaving it open-ended.

- [x] Task 100.120: Phase-end gate: full quality gate green (ruff format/check, vulture, pytest), then exactly one Conventional Commit for the phase.

#### Phase 110: Implement the fix

- [ ] Task 110.100: Apply the validated reconstruction strategy inside `general/tools/_doc_cache.py::_fresh_exception`'s `ValidationError` branch.

- [ ] Task 110.110: Update `_fresh_exception`'s own docstring and the module docstring's "every parse error is already enriched" premise to describe the corrected, two-path reconstruction.

- [ ] Task 110.120: Phase-end gate: full quality gate green, then exactly one Conventional Commit for the phase.

#### Phase 120: Cache-level tests

- [ ] Task 120.100: Add/extend `tests/general/tools/test__doc_cache.py` with cold-vs-warm `str()` equality tests for all three cacheable exception types (ACC-001), reusing Phase 100's pinned fixtures.

- [ ] Task 120.110: Add/confirm the `is`-distinct-exception-objects regression test survives unchanged (ACC-004).

- [ ] Task 120.120: Phase-end gate: full quality gate green, then exactly one Conventional Commit for the phase.

#### Phase 130: Tighten the 12 per-domain consistency tests

- [ ] Task 130.100: For each of the 12 `tests/<d>/tools/test_get_<d>.py` modules, replace the relaxed, `_strip_pydantic_footer`-based `error`-text comparison with plain `==` identity, in both read orders (list-first and get-first, exercised via call ordering against a fresh per-test temp file within the same test process -- see REQ-003), and delete the now-dead helper copy.

- [ ] Task 130.110: Add/confirm the `list_<d>()` row-stability-across-repeated-calls test (ACC-003) for at least one representative domain (or all 12, if cheap -- decide during implementation).

- [ ] Task 130.120: Phase-end gate: full quality gate green, then exactly one Conventional Commit for the phase.

#### Phase 140: Doc-restoration sweep

- [ ] Task 140.100: Amend ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c in place, via the ADR domain's own `update_section` tool (`docs/adr/*.md` is the live file the ADR MCP tools write directly -- it is not regenerated by `specmgr docs`/`adr-toc`), re-tightening the qualified claim back to the full byte-identical invariant in: Decision Outcome item 3, the Confirmation section, **and** Decision Outcome item 2's dangling cross-reference ("...carries the same parse defect as `list_feat`'s failed-row error text (see item 3 below for the consistency claim and its qualification)") -- item 2's parenthetical must drop "and its qualification" once item 3 no longer carries one, or the ADR becomes internally self-contradictory. Record this feature's id in the ADR's own history/changelog if the ADR format supports it.

- [ ] Task 140.110: Re-tighten `general/models/parse_failure_result.py`'s module + class docstrings.

- [ ] Task 140.120: Re-tighten `general/tools/_doc_paths.py`'s module docstring and `find_parse_failure`'s own docstring, and `feat/tools/_paths.py`'s `find_feat_parse_failure` docstring.

- [ ] Task 140.130: Re-tighten `general/data/general_repair_instructions.md`'s step 1 with-id line, `general/prompts/repair.py`'s module docstring + `@mcp.prompt` description, and `.opencode/agent/doc-repairer.md` (confirmed to repeat the qualified "not byte-equal text" claim at the time of this plan's review -- update it). `.opencode/skill/repair/SKILL.md` was also checked and does **not** currently carry the qualified wording (only the unqualified "same parse defect" phrase) -- re-check at implementation time in case it has changed since, but do not assume it needs an edit.

- [ ] Task 140.135: Update `tests/general/prompts/test_repair.py`'s pinned narration assertions (`assertIn("the same parse defect ...", ...)` / `assertIn("... treat the two texts as the same defect, not byte-equal", ...)`) to match the re-tightened wording Task 140.130 writes into `general_repair_instructions.md` -- this test pins that file's exact text and will fail once Task 140.130 lands if left unchanged.

- [ ] Task 140.140: Re-tighten all 12 `get_<d>` tool descriptions/docstrings (the Returns-section qualified phrase).

- [ ] Task 140.150: Re-tighten `AGENTS.md`, `CHANGELOG.md` (the existing, now-stale feat-150 `[Unreleased]` entries), and `server.py`'s module docstring. Additionally, add a **new** `CHANGELOG.md` `### Fixed` entry under `[Unreleased]` documenting this feature's own behavior change (`_fresh_exception`'s `ValidationError` reconstruction now preserves the trailing pydantic documentation-link footer for genuine body-field failures; `get_<d>`/`list_<d>` error text is now byte-identical regardless of read order) -- distinct from, and in addition to, the re-tightening of the old entries.

- [ ] Task 140.160: Regenerate `docs/MCP.md` (`specmgr mcp-docs`), `docs/api/` + `docs/GENERATED.md` (`specmgr docs`), and `docs/adr/README.md` (`specmgr adr-toc`); confirm no drift on a second run.

- [ ] Task 140.170: Phase-end gate: full quality gate green, then exactly one Conventional Commit for the phase.

#### Phase 150: Final Verification

- [ ] Task 150.100: Walk every Acceptance Criterion (ACC-001..ACC-006) with concrete evidence (command + output).

- [ ] Task 150.110: Full quality gate green: ruff format/check, vulture, `pytest -n auto --cov=src --cov-report=`, all three doc generators idempotent, `specmgr coverage-badge`; set this feature's frontmatter `status` to `done` and bump `updated`.

- [ ] Task 150.120: Exactly one Conventional Commit for the phase.

#### Phase 900: Coordinate feat-170 adoption (do not forget)

- [ ] Task 900.100: Once feat-170-update-edit-parse-failure's own branch/worktree has rebased onto a `dev` that includes this feature, sweep its own, independently-introduced copy of the same qualified language: delete the 4 `_strip_pydantic_footer` test-helper copies in `tests/general/tools/test_update.py`/`test_edit.py`/`test_set_status.py`/`test_set_classification.py` and tighten their assertions to plain `==`; reword the "Option B, 2026-09-26, follow-up issue #162" phrases in `general/tools/{update,edit,set_status,set_classification}.py`'s docstrings, ADR `b8c9bfea-6dcf-4158-bfc5-4ec17abb842f`'s Decision Outcome, and feat-170's own touched lines in `AGENTS.md`/`CHANGELOG.md`/`server.py`. Leave this task unchecked until that sweep has actually happened -- it lives on a different branch/worktree than this feature's own, and will not be caught by this feature's own quality gate.

## Progress

### Current Status

**As of 2026-10-01**: Phase 100 (spike) complete. The proposed reconstruction strategy -- a plain, recognized-kind `type=`/`ctx=` pass-through for a `ValidationError`'s per-field details, falling back to the current `PydanticCustomError` wrap only on `KeyError` -- is confirmed to work exactly against this codebase's pinned pydantic 2.13.4/pydantic-core 2.46.4, pinned by two new permanent tests in `tests/general/tools/test__doc_cache.py` built on real `parse_req` failures (not hand-built fixtures): a frontmatter-only failure (`status` out of vocabulary) round-trips `str()` exactly via the fallback wrap, and a body-field failure (`## Level`'s pattern validator) round-trips `str()` exactly via the plain pass-through, footer included. The single-vs-mixed-exception question is answered: **not producible** -- a document broken in both frontmatter and body still raises only the frontmatter failure (parse_frontmatter fails first, before `Body.from_text` ever runs), confirmed via a real `parse_req` call against a deliberately doubly-broken fixture. The spike's prototype reconstruction function is intentionally kept test-local (`_reconstruct_validation_error_spike`), not yet wired into production `_fresh_exception` -- Phase 110 (Task 110.100) applies it for real, with its own docstring updates. Root cause confirmed by reading `general/tools/_doc_cache.py::_fresh_exception` directly: the `ValidationError` branch unconditionally wraps every per-field detail in `PydanticCustomError` before calling `ValidationError.from_exception_data`, which is correct for already-custom frontmatter-field errors but silently drops the trailing pydantic documentation-link footer for genuine, recognized-builtin body-field errors. `AssertionError`/`yaml.error.MarkedYAMLError` reconstruction already round-trip `str()` exactly and are out of scope. Also confirmed (read-only inspection of the separate, not-yet-merged `feat-170-update-edit-parse-failure` branch/PR #175) that it independently propagated the identical qualified language into 4 more tool files, a new ADR, and 4 more test helper copies -- tracked here as Phase 900 so it is not forgotten, with its exact timing/ownership deliberately left as an open, later user decision.

### Blockers

- None currently. Implementation has not been authorized to start yet (explicit instruction: create the plan only, do not implement).

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-01T07:10:00.000Z - Phase 100 complete

Spiked and confirmed the proposed reconstruction strategy against this repo's pinned pydantic 2.13.4/pydantic-core 2.46.4. Prototyped (Task 100.100) a test-local `_reconstruct_validation_error_spike` function in `tests/general/tools/test__doc_cache.py`: attempts a plain `type=`/`ctx=` `InitErrorDetails` pass-through per field-error detail (omitting `ctx` entirely when the original detail has none -- `ctx=None` raises `TypeError`, confirmed live), falls back to the current production `PydanticCustomError`-wrap for the *whole* exception on `KeyError` (confirmed to be the exact exception `ValidationError.from_exception_data` raises for an unrecognized `type=` like `"frontmatter_value_error"`). Pinned (Task 100.110) via two new permanent tests built on real `parse_req` calls against deliberately malformed `req` fixtures (not hand-built pydantic_core objects): `test_frontmatter_only_failure_str_round_trips_via_the_custom_wrap_fallback` (a bad frontmatter `status` value; proves the fallback-wrap path is unchanged/still exact) and `test_body_field_failure_str_round_trips_via_the_plain_passthrough_including_its_footer` (a bad `## Level` value, a recognized builtin `"value_error"` kind; proves the plain pass-through preserves the trailing `https://errors.pydantic.dev/...` footer the current production code silently drops -- the bug itself). The mixed-failure question is answered and recorded: **not producible** -- `test_mixed_frontmatter_and_body_failure_is_not_producible_via_parse_req` breaks both frontmatter and body in one document and confirms `parse_req` still raises only the frontmatter failure (`parse_frontmatter` runs and fails first, before `Body.from_text` is ever reached), matching the Design Notes' pre-spike expectation. Scope discipline: the spike's prototype function is deliberately kept test-local, not wired into production `_fresh_exception` -- Phase 110 (Task 110.100/110.110) applies the validated strategy for real, with the matching docstring rewrite. Full quality gate green (ruff format/check, vulture, `pytest -n auto --cov=src --cov-report=`, 3849 passed). No design decisions needed beyond what the plan's pre-spike findings already established -- all three were confirmed exactly as predicted.

#### 2026-10-01T06:15:00.000Z - Plan review and refinement pass

Reviewed the plan against the actual `_doc_cache.py`/`_errors.py`/`_frontmatter_parse.py` source and ADR 9080b37c, and validated the proposed reconstruction strategy with live experiments against this repo's pinned pydantic/pydantic-core version. Confirmed the root-cause analysis and technical approach are sound, and folded the following corrections into the plan: added `tests/general/prompts/test_repair.py` to Scope (it pins exact wording Phase 140 removes); added a new `CHANGELOG.md` `### Fixed` entry task (previously only *re-tightening* of old stale text was planned); fixed ADR 9080b37c Decision Outcome item 2's dangling "and its qualification" cross-reference (Task 140.100); clarified Task 140.100's amendment mechanism (the ADR domain's `update_section` tool, not hand-editing `docs/adr/*.md`); replaced Task 140.130's "if they repeat" hedge with a concrete finding (`doc-repairer.md` does carry the qualified claim; `SKILL.md` currently does not); reworded REQ-003/ACC-002/Task 130.100 to drop the "fresh process per call" requirement in favor of same-process call-ordering against a per-test temp file (no subprocess isolation has precedent or is needed in this test suite); added pre-spike technical findings to the Design Notes (`ctx=None` raises `TypeError`, an unrecognized `type=` raises `KeyError`, and every real `ValidationError` in this codebase is architecturally homogeneous -- frontmatter-origin and body-origin errors never mix within one exception -- so Task 100.110's "mixed fixture" is expected to resolve to "not producible"); and added an explicit Scope exclusion clarifying that `wrap_tool_errors`/`enrich_frontmatter_validation_error`'s own, unrelated, intentional footer-dropping must not be "fixed" during the Phase 140 doc sweep. No implementation started; plan-only per explicit instruction.

#### 2026-10-01T03:55:44.404Z - Created

Created this feature from GitHub issue #162 triage (root cause read directly from `general/tools/_doc_cache.py`; coordination risk with the separate, not-yet-merged feat-170 branch identified via read-only inspection of its remote branch/open PR #175). Plan-only per explicit instruction -- implementation is a separate, later, authorized step, to be done in a dedicated worktree created by the user.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-01T03:58:00.000Z - Amend ADR 9080b37c in place rather than opening a new ADR

User decision: since this feature fully realizes (rather than reverses or supersedes) the error-text consistency invariant ADR 9080b37c already documents in its qualified, Option B form, the ADR's own text (Decision Outcome item 3 + Confirmation) is amended in place -- the same pattern feat-150 itself used when it first introduced the qualification -- instead of opening a new ADR.

#### 2026-10-01T03:57:00.000Z - feat-170 cleanup deferred to an explicit, unchecked Task List item

User decision: rather than deciding now how/when to clean up feat-170's own, independently introduced copy of the same qualified language (it lives on a separate, not-yet-merged branch/worktree), the decision is deferred -- but a dedicated, unchecked Phase 900 task is added at the very end of this feature's own Task List specifically so the follow-up is not forgotten once both features have landed.

### Related PRs / Commits

- [Issue #162](https://github.com/dfch/biz.dfch.SpecMgr/issues/162): the triggering bug report (filed by feat-150-mcp-lifecycle-commands's Task 1a.8, commit 10a4b62).

### More Information

See ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c for the full background on the non-raising `ParseFailureResult` workaround chain this feature's Phase 140 re-tightens, and feat-150-mcp-lifecycle-commands's own README (Task 1a.8, the "2026-09-26 17:01:41.000Z" Decisions Made entry) for the original Option A vs. Option B triage that deferred this fix and filed GitHub issue #162.
