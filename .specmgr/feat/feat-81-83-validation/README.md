---
classification: null
created: '2026-09-03 10:38:25.338Z'
id: feat-81-83-validation
status: in-progress
type: feat
updated: '2026-09-04 18:00:00.000Z'
version: 1.1.0
---

# Feature: Consolidate Validation Tools and Fix Opaque Validation/List Failures (#81, #83)

## Plan

### Overview

GitHub issues #81 and #83 both concern how this repo's MCP tools report validation failures. Issue #81 asks for an inventory of the per-domain `validate_<d>` tools and a decision on how to consolidate them, plus whether `list_<d>` should return a document path (already true for `feat` via `FeatSummary.path`), so an agent can read/edit/validate a document with minimum token cost. There are actually thirteen `validate_<d>` tools today (not eleven, as an earlier draft of this plan assumed): twelve whole-body-domain tools sharing an identical `(content: str, full: bool = False) -> bool` signature, plus `validate_adr` (`id`-based, re-reads from disk, no `full` parameter) which differs structurally from the other twelve. Issue #83 reports two related problems: (a) a validation failure surfaces only as an opaque, uncaught exception rather than a structured, inspectable result, and (b) `list_<d>` silently reports `total: 0` when every document in a directory fails to parse, indistinguishable from an empty or misconfigured directory. Prior work already closed part of the "opaque" complaint: `feat-27-validation` made every validation exception's message actionable (field path, line, cause/fix hint), and `feat-67-70-71` confirmed the MCP transport forwards that full message to the client unabridged, with no truncation. What remains open is the delivery mechanism itself -- a dry-run check tool (`validate_<d>`) still only ever succeeds or raises, so a caller cannot get back a structured, inspectable `{valid, errors}` result -- plus `list_<d>`'s silent-zero problem, which no prior feature touched. This feature investigates whether issue #83's own two literal repro cases still reproduce against current HEAD (following the same investigate-first method `feat-67-70-71` used for issues #70/#71), then: (1) replaces twelve of the thirteen per-domain `validate_<d>` tools (all except `validate_adr`, which is kept unchanged) with one generic, type-dispatched `validate` tool (mirroring the existing `update`/`set_status`/`set_classification`/`delete` precedent, ADR 36905d5b-8057-4294-8665-c7eed5534db0) that always returns a structured `{valid, errors}` result instead of raising for a content-validation failure; (2) fixes `list_<d>` to report parse failures explicitly, via an `error_count` header field and inline failed-document entries in `results`; and (3) adds `list_<d>` summary `path`-field parity with `FeatSummary.path` across the other eleven whole-body domains, retrofitting `FeatSummary.path` itself to use a resolved (absolute) path in the same pass.

### Requirements

- REQ-001: Before any implementation, reproduce issue #83's two literal repro bodies (a `req` document with naive-isoformat `created`/`updated` timestamps; a `dec` document with an em dash instead of a hyphen in an `## Updates` sub-heading) against current HEAD through `validate_req`/`validate_dec`, and record in Design Notes whether the reported opaque-failure symptom still reproduces or was already resolved by `feat-27-validation`/`feat-67-70-71`.

- REQ-002: Produce an inventory (in Design Notes) of every current `validate_<d>` tool's signature, domain list, and behavior -- all thirteen, including `validate_adr` -- as issue #81 explicitly requests, before designing its replacement.

- REQ-003: Replace twelve of the thirteen per-domain `validate_<d>` tools (all except `validate_adr`, which keeps its distinct `id`-based, disk-touching signature and is excluded from consolidation) with one generic, type-dispatched `validate(type, content, full)` tool in `general/tools/`, mirroring the `update`/`set_status`/`set_classification`/`delete` precedent (ADR 36905d5b-8057-4294-8665-c7eed5534db0); the twelve consolidated per-domain tools are removed, not kept as wrappers, matching that precedent. A dedicated new ADR records this consolidation decision, extending ADR 36905d5b-8057-4294-8665-c7eed5534db0's dispatch-only convention -- established for mutation-adjacent tools (`update`/`set_status`/`set_classification`/`delete`) -- to `validate`, a read-only/dry-run tool category it did not originally cover, mirroring `feat-36-delete`'s own precedent of writing a dedicated ADR even where a general convention already existed (Task 2.2).

- REQ-004: The generic `validate` tool never raises for a content-validation failure; it always returns a structured result (`{valid: bool, errors: list[{message: str}]}` -- no `field` key), reusing `feat-27-validation`'s already-enriched, actionable message text verbatim as each error's `message` -- only a shape-mismatch on `full`/`type` (an already-actionable `ValueError` today, including passing `type="adr"` or any other unsupported/unknown domain, mirroring `update`/`set_classification`/`delete`'s existing rejection of `adr`) may still raise. In practice, `errors` currently holds zero or one entries: each domain's validation logic performs exactly one guarded parse call, so at most one exception can ever be caught per invocation today -- the list shape is deliberate forward-compatibility (matching pydantic's own per-error `.errors()` structure, which existing tooling does not yet expose to callers, per the "`{valid, errors}` shape" design note below), not an indication multiple concurrent errors are common.

- REQ-005: `parse_<d>`/`get_<d>` keep their existing raise-based contract unchanged -- this feature's structured-result change is scoped to `validate` only.

- REQ-006: `list_<d>` (all twelve whole-body domains) reports parse failures explicitly through one new, shared `general/tools/_listing.py` helper (`build_summaries()`, callback-based, mirroring `general/tools/_doc_paths.py::find_doc_path_by_id`'s existing generalization pattern) reused by every domain's `list_<d>.py`, replacing the eleven-times-copy-pasted try/except/append loop rather than a "shared listing helper" that -- per an earlier draft's incorrect assumption -- already existed. `PagedResult` gains `error_count: int = 0` (default `0`, so `list_adr` -- out of scope -- is unaffected), counting failed documents across the *entire* base directory, independent of `offset`/`max_results` paging, mirroring `total`'s own already-documented across-all-pages semantics. Failed documents appear inline within `results` and now contribute to `total` alongside successes -- a deliberate semantics change from today's "parseable documents only" `total`, since that is precisely what fixes issue #83's "indistinguishable from an empty directory" complaint. Each failed entry has `id=None`, `title`/`status` both replaced by the fixed marker `"<failed to parse>"`, `ref` populated as `path.stem` (identical to every domain's existing successful-entry `ref` derivation), `path` populated the same way as a successful entry (REQ-007), and a new `error: str | None` field (added to the shared `DocSummary` base, `None` for successful entries) carrying the actual exception message -- rather than being silently omitted. `rsk` is a documented implementation exception within this same requirement, not a scope carve-out: `RskSummary` carries additional derived fields beyond the `DocSummary` base (see Design Notes), so its failed entries are built from a parsed sentinel document rather than hand-set literals, but the externally observable contract (marker `title`/`status`, `ref`, `path`, `error`, contribution to `total`/`error_count`) is identical to every other domain. The failure catch set covers all three of `validate_<d>`'s own documented parse-failure channels -- `AssertionError`, `pydantic.ValidationError`, and `yaml.YAMLError` (malformed frontmatter) -- not just the first two, so a document with malformed YAML frontmatter is reported as a failed entry rather than crashing `list_<d>` outright. Directory-listing/permission errors that could prevent even filename enumeration are out of scope.

- REQ-007: Add a `path: str` field (an absolute, `.resolve()`d filesystem path) to `list_<d>` summaries for the other eleven whole-body domains, matching and extending `FeatSummary.path`'s existing precedent; in the same pass, retrofit `FeatSummary.path` itself to use a resolved (absolute) path rather than its current unresolved `str(path)`, and revise `DocSummary.ref`'s docstring to drop its "must not read this off disk" policy language now that `path` makes direct reads a sanctioned, first-class option for every whole-body domain. Implemented by adding `path: str` and `error: str | None = None` directly to the shared `DocSummary` base model (`general/models/summary.py`) rather than redeclaring them in each of the eleven other domains' summary subclasses; `FeatSummary`'s existing separate `path` field is removed in favor of the inherited one once retrofitted to the resolved form, rather than duplicated.

- REQ-008: Regression tests reproduce issue #83's two literal repro bodies end-to-end through the new generic `validate` tool, and a directory with a mix of valid and unparseable documents end-to-end through `list_<d>` for at least two domains.

- REQ-009 (Phase 6, added following an independent post-closeout quality review): Fix the 11 stale domain `__init__.py` module docstrings (`dec`/`feat`/`gol`/`prb`/`qa`/`req`/`rsk`/`sop`/`tsk`/`uc`/`vcr`) that still enumerate the retired `validate_<d>` tool in their own "tools (...)" listing (e.g. `req/__init__.py`'s docstring still lists `validate_req` as one of its tools) -- a real, verifiable inaccuracy Task 2.3/5.2 did not catch because both only audited `AGENTS.md`/`server.py`/prompts, not every domain package's own module docstring. In the same pass, also correct `sysrs/__init__.py`'s own unrelated, pre-existing staleness (claims "7 tools" and that "`sysrs.prompts` is still an empty placeholder sub-package", both no longer true as of feat-32-sysrs's later phases), since it is touched during the same audit. Regenerate `docs/api/`/`docs/GENERATED.md` afterward, since they mirror these docstrings verbatim and currently ship the same stale claims.

- REQ-010 (Phase 6): Fix `general/tools/validate.py`'s `yaml.YAMLError` message-enrichment gap. Every `_validate_<d>` adapter's unconditional, unwrapped `has_frontmatter = bool(frontmatter.loads(content).metadata)` probe -- run before the `full=True`/`full=False` branch is even decided -- raises PyYAML's raw, un-enriched error (opaque `"<unicode string>"` location, block-relative line number) for malformed frontmatter YAML, instead of `parse_<d>`'s enriched form (`"the frontmatter block"` naming, document-relative line number, via `models/md/_frontmatter_parse.py::enrich_frontmatter_yaml_error`) -- because the probe runs entirely outside any `wrap_tool_errors` context. This directly contradicts REQ-004's own claim ("reusing feat-27-validation's already-enriched message... verbatim") for this one channel, and was inherited unchanged from the original per-domain `validate_<d>` tools (a "verbatim port"), not introduced by this feature -- but it was never caught because `tests/general/tools/test_validate.py` (849 lines, 15 test methods) contains zero `yaml`/`YAMLError`/malformed-YAML-syntax test coverage, unlike the parallel `list_<d>` fix (Task 3.3), which got a dedicated test for exactly this channel. Fix: add a private helper `_detect_frontmatter(content: str, *, domain: str) -> bool` inside `general/tools/validate.py` (kept local to this file, not promoted to a shared `models/md` module, since nothing else in the codebase currently needs this exact composition) that composes `enrich_frontmatter_yaml_error` (block-naming + document-relative line remap) with `wrap_tool_errors`'s own domain/tool labeling, used by all twelve adapters in place of their raw probe, so a malformed-YAML `validate(type=<d>, content=..., full=True)` call's error message becomes textually identical to `parse_<d>`'s own message for the same input (modulo the `wrap_tool_errors` label prefix). Must not change the existing `full`/content-shape-mismatch `ValueError` behavior -- `TestValidateFullShapeMismatchRaises` must keep passing unmodified.

- REQ-011 (Phase 6): Amend ADR 519d1206-4d2a-4500-9046-6db635209996's `### Confirmation` section, which currently commits to a specific future step ("its `{valid, errors}` result must be observed intact end-to-end through a live OpenCode session for at least the two Phase 1 regression fixtures") that this feature's own closeout (Phase 5) never actually performed or recorded -- only unit-level Python calls (`TestValidateIssue83Regressions`) were run. Revise that section to state precisely what was verified (unit-level `{valid, errors}` shape reproduction of both Phase 1 regression fixtures via direct Python calls, not a live MCP client round-trip) rather than leaving an unfulfilled, silently-open commitment in an `accepted`-status ADR.

### Acceptance Criteria

- [x] ACC-001: Verifies REQ-001 -- Design Notes records a confirmed-real-or-already-fixed verdict for both of issue #83's literal repro bodies, reproduced against current HEAD. Verdict: both reproduce as client-observed symptoms, root-caused to a client-side tool-error-rendering gap outside this repo's code, not a server-side regression -- see Design Notes.

- [x] ACC-002: Verifies REQ-002 -- Design Notes contains a table/list of all thirteen current `validate_<d>` tools with signature and behavior. Verdict: inventory complete, see Design Notes.

- [x] ACC-003: Verifies REQ-003 -- the generic `validate(type, content, full)` tool exists, dispatches to all twelve applicable domains, the twelve consolidated per-domain `validate_<d>` tools (all except `validate_adr`, which still exists unchanged) no longer exist, their dedicated `test_validate_<d>.py` files are removed/migrated (Task 2.5), and a new ADR documenting the consolidation decision exists (Task 2.2). Verdict: done -- `general/tools/validate.py` implements the tool, the twelve per-domain tools and their dedicated tests are removed, ADR 078bf395-0a5f-4afd-84f6-b7a2191a00e6 records the decision, and `docs/adr/README.md` is regenerated.

- [x] ACC-004: Verifies REQ-004 -- `validate` never raises for a content-validation failure, returns `{valid, errors}` with `errors: list[{message}]` reusing `feat-27-validation`'s enriched messages verbatim; a test confirms `validate(type="adr", ...)` and any other unsupported `type` still raise `ValueError`; a further test, for a representative sample of domains (`req`, `dec`, `vcr`), confirms that a `full`/content-shape mismatch still raises `ValueError` through the generic tool rather than being swallowed into `{valid: false}`. Verdict: done -- `tests/general/tools/test_validate.py` (`TestValidateAllDomains`, `TestValidateUnsupportedType`, `TestValidateFullShapeMismatchRaises`, `TestValidateIssue83Regressions`) covers all of this; the exception handler catches exactly `(AssertionError, ValidationError, yaml.YAMLError)`.

- [x] ACC-005: Verifies REQ-005 -- existing `parse_<d>`/`get_<d>` tests continue to pass unchanged (raise-based contract untouched). Verdict: done -- the full test suite (3308 tests) passes unchanged for `parse_<d>`/`get_<d>`; only `validate_<d>`-referencing tests were migrated.

- [x] ACC-006: Verifies REQ-006 -- a `list_<d>` test with a directory containing both valid and unparseable documents asserts `error_count` is correct (across the whole directory, not just the current page) and `total` includes failed entries, with each failed document appearing in `results` with `ref`/marker/`error`/`path` populated -- for at least two domains, including `rsk`'s sentinel-document construction (see Design Notes); a dedicated test additionally asserts the RSK sentinel markdown parses successfully on its own, independent of `list_rsk`'s own test, so a future RSK schema change is caught at the sentinel level. Verdict: done -- `tests/req/tools/test_list_req.py`/`tests/rsk/tools/test_list_rsk.py` cover the full contract (including a malformed-YAML-frontmatter fixture each), `tests/rsk/tools/test__sentinel.py` covers the sentinel document independently, and `tests/general/tools/test__listing.py` covers `build_summaries()` directly.

- [x] ACC-007: Verifies REQ-007 -- all eleven other whole-body domains' summary types gain `path` via the shared `DocSummary` base with a passing test each; `FeatSummary` is retrofitted to the inherited, resolved `path` (its own redundant field declaration removed) with its existing tests updated accordingly; `DocSummary.ref`'s docstring no longer states callers must not read the file off disk directly. Verdict: done -- confirmed all eleven other domains' `list_<d>.py`/`test_list_<d>.py` already had `path=str(path.resolve())` and `Path(summary.path).is_absolute()` assertions from Phase 3; `FeatSummary`'s own redundant `path` field declaration removed (now purely inherited from `DocSummary`), `list_feat.py`'s `_to_summary`/`_to_failed_summary` retrofitted to `path.resolve()`, and `tests/feat/tools/test_list_feat.py`/`tests/general/models/test_summary.py` updated/extended accordingly; `DocSummary.ref`'s docstring revised.

- [x] ACC-008: Verifies REQ-008 -- the regression tests described exist and pass. Verdict: done -- `tests/general/tools/test_validate.py::TestValidateIssue83Regressions` reproduces both of issue #83's literal repro bodies end-to-end through the generic `validate` tool (`{valid: False, errors: [...]}`, never a raised exception); `tests/req/tools/test_list_req.py`/`tests/rsk/tools/test_list_rsk.py` each reproduce a mixed valid/unparseable directory end-to-end through `list_<d>` (including a malformed-YAML-frontmatter fixture), satisfying the "at least two domains" requirement. Full suite (3342 tests) passes.

- [ ] ACC-009: Verifies REQ-009 -- `grep -rn "validate_<d>"` (for each of the twelve retired names) across all twelve domains' `__init__.py` files returns nothing implying a still-existing per-domain tool; `sysrs/__init__.py`'s docstring accurately reflects its current tool/prompt/resource counts; `docs/api/`/`docs/GENERATED.md` regenerated with zero remaining stale mentions.

- [ ] ACC-010: Verifies REQ-010 -- a new test in `tests/general/tools/test_validate.py` submits identical malformed-YAML-frontmatter content to `validate(type=<d>, content=..., full=True)` and to `parse_<d>` for at least two domains (e.g. `req`, `dec`), asserting `{valid: False}` and that the two paths' error messages match (up to the `wrap_tool_errors` label prefix); all pre-existing `test_validate.py` tests continue to pass unmodified.

- [ ] ACC-011: Verifies REQ-011 -- ADR 519d1206's Confirmation section no longer describes an unperformed live-session check as an open commitment.

### Scope

#### Included

- Investigation/reproduction of issue #83's two literal repro cases against current HEAD.

- Inventory of all thirteen current `validate_<d>` tools (issue #81's explicit ask).

- A new generic, type-dispatched `validate` tool in `general/tools/` returning a structured, non-raising `{valid, errors}` result.

- Removal of twelve per-domain `validate_<d>` tools (all except `validate_adr`) once the generic tool is live and tested.

- `list_<d>` fix: `error_count` header field plus inline failed-document entries in `results`, across all twelve whole-body domains.

- `list_<d>` summary `path`-field parity with `FeatSummary.path` across the other eleven whole-body domains, plus retrofitting `FeatSummary.path` to a resolved (absolute) path and revising `DocSummary.ref`'s docstring accordingly.

- Regression tests, docstring `Raises`/return-shape updates, `docs/api`/`docs/GENERATED.md`/`docs/MCP.md` regeneration, `CHANGELOG.md` `[Unreleased]` entries (with **BREAKING** markers where applicable, per phase), a new ADR recording the `validate`-consolidation decision, and an `AGENTS.md` update.

- Phase 6 (added following an independent post-closeout quality review, before this feature's true closeout): fixing 11 domain `__init__.py` docstrings' stale `validate_<d>` mentions plus `sysrs/__init__.py`'s own unrelated drift (REQ-009); fixing `validate`'s `yaml.YAMLError` message-enrichment gap for malformed frontmatter YAML via a private `_detect_frontmatter` helper (REQ-010); amending ADR 519d1206's Confirmation section to match what was actually verified (REQ-011).

#### Explicitly Out Of Scope

- Consolidating `parse_<d>`/`get_<d>` into a generic dispatch tool -- per the recorded decision, only `validate` is consolidated; reads stay per-domain.

- Changing `parse_<d>`/`get_<d>`'s raise-based error contract -- already actionable per `feat-27-validation`, untouched here.

- Changing `validate_adr`'s `id`-based, disk-touching contract -- it is structurally different from the other twelve `validate_<d>` tools (no `full` parameter, always re-reads from disk) and stays a standalone tool, excluded from the generic `validate` tool.

- Handling directory-listing/permission errors in `list_<d>`'s failure reporting -- REQ-006/Task 3.1 only cover per-document content/parse failures, not enumeration failures.

- Filing or fixing the drafted OpenCode client-side bug report (`opencode-issue-mcp-tool-error-truncated.md`) -- it is outside this repo's control; the draft is saved as a courtesy artifact only.

- New exception types or a typed structural-error channel -- the generic `validate` tool's `{valid, errors}` result is built from the existing enriched exception messages, not a new channel.

- Re-litigating message content quality for `create_<d>`/`update`/`set_status` -- already addressed by `feat-27-validation`/`feat-67-70-71`; this feature only changes `validate`'s and `list_<d>`'s result shape.

- Wiring `validate`/`list_<d>` into CI/pre-commit over the repo's own `.specmgr`/`docs` documents -- tracked separately (ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73).

### Dependencies

#### Depends On

- `feat-27-validation` (done) -- supplies the actionable exception messages this feature's `validate` result reuses verbatim.

- `feat-67-70-71` (done) -- confirmed the MCP transport does not truncate/discard those messages, ruling out a transport-layer explanation for issue #83's reported symptom.

### Design Notes

**Phase 1 investigation finding (2026-09-03): the opaque-failure symptom reproduces, but its root cause is a client-side rendering gap, not a specmgr server-side regression.**

Both of issue #83's literal repro bodies were reproduced against current HEAD:

- The `req` naive-isoformat-timestamp repro (`created`/`updated` as `'2026-08-05T08:15:42'` instead of the required `'yyyy-MM-dd HH:mm:ss.fff' + Z/offset` variant), submitted to `validate_req(content, full=True)`.
- The `dec` em-dash-heading repro (an `## Updates` sub-heading using `### 2026-08-27 — Created` -- an em dash `—` -- instead of a hyphen `-`), submitted to `validate_dec(content, full=True)`.

In this agent session, calling either tool (or `validate_feat`, tested the same way while refining this very document) through the normal MCP tool-call interface surfaced only a bare, contentless `"Error executing tool <name>"` message -- exactly the opaque-failure symptom issue #83 describes, and exactly what this feature's REQ-003/004 remedy targets.

However, calling the *same* `validate_req` tool with the *same* input directly over raw MCP JSON-RPC (a standalone Python script using the `mcp` SDK's `stdio_client`/`ClientSession` to spawn `python -m biz.dfch.specmgr mcp` and inspect the wire-level `CallToolResult`, bypassing this session's own tool-calling harness entirely) shows the **full, actionable, `feat-27-validation`-enriched message present in `content[].text`**, e.g.:

```
Error executing tool validate_req: 2 validation errors for ReqFrontmatter
created
  req validate_req: req frontmatter block, field 'created' (document line 2): Value error, created/updated '2026-08-05T08:15:42' must be the date+time variant 'yyyy-MM-dd HH:mm:ss.fff' followed by 'Z' or a signed '+HH:mm'/'-HH:mm' offset [...]
updated
  req validate_req: req frontmatter block, field 'updated' (document line 6): Value error, created/updated '2026-08-06T03:27:27' must be the date+time variant 'yyyy-MM-dd HH:mm:ss.fff' followed by 'Z' or a signed '+HH:mm'/'-HH:mm' offset [...]
```

**Verdict**: `feat-67-70-71`'s conclusion -- "the MCP transport forwards that full message to the client unabridged, with no truncation" -- is confirmed correct at the wire level; this is not a regression. The `"Error executing tool <name>: "` prefix is the MCP/FastMCP framework's own standard formatting for a tool-raised exception, and the full enriched message follows it intact in the actual server response. The opacity this feature's own investigation (and issue #83's original report) observed happens one layer further out: in the *calling agent's own tool-invocation rendering*, which -- in this session, and evidently in whatever client issue #83's reporter used -- appears to discard `content[].text` beyond a short generic fragment whenever a `CallToolResult` has `is_error=true`. This is outside specmgr's own code and cannot be fixed by any change to this repository's server-side error-enrichment machinery.

This finding does not change any of this feature's REQ-003/004 design -- it reinforces why it is the right fix. A tool result's `is_error=true` path is, empirically, at the mercy of a client's own (possibly lossy) error-rendering behavior, uncontrollable from the server side. A tool result's ordinary *successful* return value, by contrast, has been observed in this same session to pass through completely and losslessly regardless of size or content (e.g. this session's own `list_feat` calls, and the large text bodies read via `get_<d>`/`parse_<d>` tools). Converting `validate` from raise-on-failure to always-returns-`{valid, errors}` therefore sidesteps the lossy client-side path entirely, independent of which MCP client is in use -- a strictly more robust fix than relying on every possible client to render `is_error=true` content faithfully.

A drafted (not filed) upstream bug report against the OpenCode client used in this investigation (version 1.18.27) is saved alongside this plan at `.specmgr/feat/feat-81-83-validation/opencode-issue-mcp-tool-error-truncated.md`, documenting the repro, the wire-level evidence above, and pointers into OpenCode's own `dev`-branch source (`packages/opencode/src/mcp/catalog.ts`, `packages/opencode/src/tool/code-mode.ts`) that -- as read -- should already preserve the full message, making the exact root cause still unpinned-down on OpenCode's side. This is tracked as a courtesy artifact only; filing it is explicitly out of scope for this feature (see Scope) and does not gate any of this feature's own tasks.

This reasoning -- that `validate`'s redesign is a workaround for an external defect, not an independently preferred design, and that the rationale generalizes beyond this one feature -- is formally recorded as ADR 519d1206-4d2a-4500-9046-6db635209996 rather than left only here, per this repo's own convention that a decision affecting more than one feature belongs in a full ADR (see `AGENTS.md`).

**Tool-count correction**: an earlier draft of this plan said "eleven" `validate_<d>` tools; that figure was stale (it predates `sysrs` and one other domain being added). There are thirteen `validate_<d>` tools total: twelve whole-body-domain tools sharing an identical `(content: str, full: bool = False) -> bool` signature, plus `validate_adr` (`id`-based, re-reads from disk, no `full` parameter). This correction is reflected throughout the rest of the plan.

**Task 1.4 inventory: all thirteen current `validate_<d>` tools** (source: each domain's `tools/validate_<d>.py`, confirmed against `server.py`'s registration list). The twelve whole-body-domain tools are structurally identical byte-for-byte except for the domain name and the Pydantic model/parse-function names they call -- each detects "has frontmatter" via `bool(frontmatter.loads(content).metadata)`, then either calls `<Model>.from_text(format_text(content))` (body-only path) or `parse_<d>(content)` (full-document path), wrapped in `wrap_tool_errors(domain=..., tool=..., channel=...)` for message enrichment (feat-27-validation). `validate_adr` alone diverges structurally, per Scope's explicit carve-out.

| Tool | Domain | Signature | `full=False` (default) behavior | `full=True` behavior | Exceptions let propagate |
| --- | --- | --- | --- | --- | --- |
| `validate_req` | req | `(content: str, full: bool = False) -> bool` | Validates body-only content via `Requirement.from_text(format_text(content))`; raises `ValueError` if a frontmatter block is found. | Validates a complete document via `parse_req(content)`; raises `ValueError` if no frontmatter block is found. | `ValueError` (full/shape mismatch), `AssertionError` (structural), `pydantic.ValidationError` (field/cross-field), `yaml.YAMLError` (`full=True` only, malformed frontmatter) |
| `validate_uc` | uc | `(content: str, full: bool = False) -> bool` | Validates body-only content via `UseCase.from_text(format_text(content))` (v2 model); raises `ValueError` if a frontmatter block is found. | Validates a complete document via `parse_uc(content)`; raises `ValueError` if no frontmatter block is found. | Same set as `validate_req` |
| `validate_tsk` | tsk | `(content: str, full: bool = False) -> bool` | Validates body-only content via `Task.from_text(format_text(content))`; raises `ValueError` if a frontmatter block is found. | Validates a complete document via `parse_tsk(content)`; raises `ValueError` if no frontmatter block is found. | Same set as `validate_req` |
| `validate_qa` | qa | `(content: str, full: bool = False) -> bool` | Validates body-only content via `Qa.from_text(format_text(content))` (v2 model); raises `ValueError` if a frontmatter block is found. | Validates a complete document via `parse_qa(content)`; raises `ValueError` if no frontmatter block is found. | Same set as `validate_req` |
| `validate_prb` | prb | `(content: str, full: bool = False) -> bool` | Validates body-only content via `Prb.from_text(format_text(content))`; raises `ValueError` if a frontmatter block is found. | Validates a complete document via `parse_prb(content)`; raises `ValueError` if no frontmatter block is found. | Same set as `validate_req` |
| `validate_gol` | gol | `(content: str, full: bool = False) -> bool` | Validates body-only content via `Goal.from_text(format_text(content))`; raises `ValueError` if a frontmatter block is found. | Validates a complete document via `parse_gol(content)`; raises `ValueError` if no frontmatter block is found. | Same set as `validate_req` |
| `validate_rsk` | rsk | `(content: str, full: bool = False) -> bool` | Validates body-only content via `Risk.from_text(format_text(content))`; raises `ValueError` if a frontmatter block is found. | Validates a complete document via `parse_rsk(content)`; raises `ValueError` if no frontmatter block is found. | Same set as `validate_req` |
| `validate_dec` | dec | `(content: str, full: bool = False) -> bool` | Validates body-only content via `Decision.from_text(format_text(content))`; raises `ValueError` if a frontmatter block is found. | Validates a complete document via `parse_dec(content)`; raises `ValueError` if no frontmatter block is found. | Same set as `validate_req` |
| `validate_sop` | sop | `(content: str, full: bool = False) -> bool` | Validates body-only content via `Sop.from_text(format_text(content))`; raises `ValueError` if a frontmatter block is found. | Validates a complete document via `parse_sop(content)`; raises `ValueError` if no frontmatter block is found. | Same set as `validate_req` |
| `validate_feat` | feat | `(content: str, full: bool = False) -> bool` | Validates body-only content via `Feature.from_text(format_text(content))`; raises `ValueError` if a frontmatter block is found. | Validates a complete document via `parse_feat(content)`; raises `ValueError` if no frontmatter block is found. **Divergence note**: `full=True` deliberately does *not* check the "frontmatter `id` equals containing folder's name" invariant -- that is enforced at the addressing/tool layer (`feat.tools._paths`), not here, since this disk-free tool has no path/folder-name to check against. | Same set as `validate_req` |
| `validate_vcr` | vcr | `(content: str, full: bool = False) -> bool` | Validates body-only content via `Vcr.from_text(format_text(content))`; raises `ValueError` if a frontmatter block is found. | Validates a complete document via `parse_vcr(content)`; raises `ValueError` if no frontmatter block is found. | Same set as `validate_req` |
| `validate_sysrs` | sysrs | `(content: str, full: bool = False) -> bool` | Validates body-only content via `Sysrs.from_text(format_text(content))`; raises `ValueError` if a frontmatter block is found. | Validates a complete document via `parse_sysrs(content)`; raises `ValueError` if no frontmatter block is found. | Same set as `validate_req` |
| `validate_adr` | adr | `(id: str) -> bool` **(no `content`, no `full`)** | N/A -- no `full` parameter; always re-reads and re-parses the on-disk ADR identified by `id` via `load_by_id(adr_base_dir(), id)` on every call (no in-memory cache, no disk-free/id-free content path at all). | Same as the only column above -- there is no body-only/full-document distinction for this tool. | `AdrParseError` (ADR's own structural-error channel -- a plain `ValueError` subclass, used instead of `AssertionError`), `pydantic.ValidationError`, `yaml.YAMLError`, `AdrNotFoundError` (untouched by the wrapper, already actionable) |

All thirteen tools return `True` on success and never return `False` -- "validate" *is* successfully constructing the Pydantic model during parsing; there is no separate validation pass. Every tool wraps its guarded parse call in `wrap_tool_errors(domain=..., tool=..., channel=...)` (`validate_adr` additionally passes `also_catch=(AdrParseError,)`) so the message carries domain/tool/channel context on top of `feat-27-validation`'s field-path/line/cause-hint enrichment.

**`validate_adr`'s structural divergence from the other twelve**, consolidated: (1) it is `id`-based and disk-touching (re-reads the file from disk every call) rather than `content`-based and disk-free/id-free; (2) it has no `full` parameter at all -- it always validates what is structurally a complete on-disk document; (3) its own structural-failure channel is `AdrParseError` (a `ValueError` subclass) rather than `AssertionError`; (4) it can additionally raise `AdrNotFoundError` for an unknown `id`, a failure mode none of the other twelve content-based tools have (they have no `id` to look up). This is exactly why REQ-003/ACC-003 excludes `validate_adr` from the generic `validate` tool consolidation.

Design questions resolved during plan refinement (2026-09-03), prior to Phase 1 kickoff, superseding the "open question"/"tentative" framing that predated a research pass over the existing generic-tool precedents:

- **Generic `validate`'s domain list**: excludes `adr`, matching `update`/`set_classification`/`delete`'s 12-way precedent (each of those three excludes `adr` for its own documented, domain-specific reason) rather than `set_status`'s 13-way exception. `validate_adr` is structurally the odd one out among the thirteen `validate_<d>` tools -- `id`-based and disk-touching, with no `full` parameter -- whereas all twelve whole-body domains share an identical `(content, full)` signature. `validate_adr` is therefore kept as its own standalone tool, unchanged, and excluded from consolidation.

- **`{valid, errors}` shape**: `errors` is `list[{message: str}]` -- no `field` key. No existing precedent for a non-raising structured result exists anywhere in the codebase (this is greenfield). `feat-27-validation`'s enrichment pipeline fuses field path, line number, and cause/fix hint into a single opaque message string before the error ever reaches a tool boundary; pydantic's structured `loc`/`msg` data (via `.errors()`) is used internally only to rebuild another exception, never exposed to a caller. A separate `field` key would require new, fragile extraction, and would be `None`/absent for `AssertionError`/YAML-sourced errors regardless, since no structured field data exists for those channels at all. Reusing the already-enriched message string verbatim as each error's sole content avoids both problems. `full=True`/`full=False` is preserved as a parameter on the generic tool, unchanged from today's per-domain tools.

- **Failed `list_<d>` entry marker / `ref` semantics**: `title` is replaced with the fixed marker `"<failed to parse>"`; `ref` is `path.stem` (the filename stem), identical to every domain's existing successful-entry `ref` derivation -- confirmed universal across every `list_<d>`/`list_adr` implementation: `ref` is always filename-derived, never frontmatter-`id`-first. A content-parse failure never prevents deriving `ref`, since reading a filename doesn't require successfully parsing the file's content. Directory-listing/permission errors that could prevent even filename enumeration are explicitly out of scope for this feature.

- **`list_<d>` `path`-field parity (REQ-007)**: `path` is added to all eleven other whole-body domains' summary types, as an absolute, `.resolve()`d path -- not left as an undecided "decide, and where warranted implement" question. `FeatSummary.path` is retrofitted in the same pass to also use a resolved path (a deliberate behavior change from its current unresolved `str(path)`), and `DocSummary.ref`'s docstring is revised to drop its "callers must not read this off disk themselves" policy language, since `path` now makes direct reads a sanctioned, first-class option for every whole-body domain rather than a `feat`-only divergence. This decision was made knowingly against the stricter, more conservative alternative (leaving `ref`'s policy intact and declining to add `path` to the other eleven domains, on the grounds that their architecture -- locking, id-based dispatch, validation-on-write -- assumes tool-only mutation, unlike `feat`'s sanctioned direct-editing convention); implementers should keep the tool-only mutation contract intact elsewhere (`path` is for reads/context, not a new direct-write path) even though direct reads are now explicitly sanctioned.

**Follow-up refinements (2026-09-04), resolved before Phase 2 implementation begins:**

- **Why `errors` omits a `field` key uniformly, not just for some error sources**: Pydantic-sourced validation errors do carry structured `loc` data internally (via `.errors()`); `AssertionError`/YAML-sourced errors carry none. Rather than populate `field` for some errors and leave it `None`/absent for others depending on which validation layer raised, `{message}` alone is used for every error, keeping the shape predictable regardless of source.

- **Shared `list_<d>` helper**: `general/tools/_doc_paths.py::find_doc_path_by_id` already establishes the callback-based generalization pattern this feature follows for `list_<d>`: a new `general/tools/_listing.py::build_summaries(paths, read, to_summary, to_failed_summary, error_types=(AssertionError, ValidationError, yaml.YAMLError)) -> tuple[list[SummaryT], int]` replaces the eleven-times-copy-pasted try/except/append loop (confirmed byte-for-byte identical across `req`/`dec`/`gol`/`prb`/`qa`/`sop`/`sysrs`/`tsk`/`uc`/`vcr`; `rsk`/`feat` differ only in summary construction, handled by their own `to_summary`/`to_failed_summary` callbacks) -- an earlier draft of Task 3.1 incorrectly assumed a shared helper already existed; it did not. `yaml.YAMLError` is included in the default catch set, not just `AssertionError`/`ValidationError` as an earlier draft of this design proposed: `parse_<d>` genuinely raises it, unwrapped, for malformed frontmatter YAML -- confirmed via source (`models/md/_frontmatter_parse.py`) -- exactly one of `validate_<d>`'s own three documented failure channels. Omitting it would leave a document with malformed YAML frontmatter crashing `list_<d>` outright instead of appearing as a failed entry, which is precisely issue #83(b)'s complaint. Related, out-of-scope gap noted for a future feature: `general/tools/_doc_paths.py::find_doc_path_by_id` (backing `get_<d>`/`update`/`set_status`/`delete`'s id lookup) has this same `yaml.YAMLError`-uncaught gap today; this feature does not touch it.

- **Phase 3/Phase 4 sequencing**: `path` is introduced on the shared `DocSummary` base in Phase 3 (Task 3.1), not Phase 4. Since `build_summaries()`'s callbacks must construct a fully-valid model instance for every row -- success or failure -- the moment they run, Task 3.1 necessarily populates `path=path.resolve()` on every domain's *successful*-entry construction too, as an unavoidable side effect of `path` becoming mandatory (no default) on the shared base -- the RSK sentinel's own Phase 3 `model_copy` already sets `path` as one of its "four fields" the sentinel itself can't supply, confirming `path` must already exist and be wired by that point. Task 4.1 therefore introduces no new field-population code; it verifies/spot-checks what Task 3.1 already wired for the other eleven domains, and Phase 4's real remaining scope is `FeatSummary`'s retrofit (Task 4.2), the `ref` docstring revision (Task 4.3), and dedicated `path`-field tests (Task 4.4).

- **`RskSummary`'s extra fields -- sentinel-document design**: `RskSummary` is the only domain summary type carrying fields beyond the shared `DocSummary` base (`initial_level`, `residual_level`, `strategy`, `scope`, `residual_probability`, `residual_impact`, `residual_product`) -- every other domain's summary type is a plain, fieldless `DocSummary` subclass. These seven fields are derived, via `RskSummary.from_document()`, from a fully-parsed `RskDocument`'s computed properties (e.g. `Assessment.level`, `Probability.value`) -- values that do not exist independently of a complete, successfully-validated object graph; Pydantic model construction is atomic, so a parse failure yields zero of the seven fields, never a partial set. Two alternatives were rejected: weakening `RskSummary`'s fields to `Optional` (defeats the field constraints' purpose for real rows too, not just failed ones); and fabricating schema-valid-but-plausible placeholder data via direct `RskSummary(...)` construction (indistinguishable from real, low-severity data in an aggregate risk view unless every consumer checks `error` first -- worse than a silent zero, since it is a believable lie rather than an obvious absence). Adopted instead: a fixed, valid, deliberately worst-case-severity RSK markdown document (`rsk/tools/_sentinel.py::_SENTINEL_RSK_TEXT`), parsed exactly once via the real `parse_rsk` pipeline (no bypass) into `_SENTINEL_RSK_DOCUMENT: RskDocument`. A failed row is built by running this sentinel through the same `RskSummary.from_document()` every real row uses, then `model_copy(update={"id": None, "status": "<failed to parse>", "path": ..., "error": ...})` for only the four fields no document could ever supply. Every domain-specific value -- `title="<failed to parse>"` (the sentinel's real H1), `strategy="accept"`, `scope="unknown"`, `initial_level`/`residual_level` (genuinely computed as `"very high"` from `Probability 5`/`Impact 5`, i.e. `level_from_product(25)`), `residual_probability`/`residual_impact`/`residual_product` (`5`/`5`/`25`) -- comes from real parsing and derivation, not hand-typed literals, so it can never drift out of sync with `level_from_product`'s own thresholds; a future schema-breaking change to the RSK model surfaces as a loud sentinel-parse failure, not silent staleness. `accept`/`dropped` (the sentinel frontmatter's real, valid `status`, overridden to the marker afterward, since `RskFrontmatter.status` is closed-vocabulary-enforced the same way `Strategy._validate_value` enforces the TARA words) are chosen as the most passive/neutral values of their respective closed vocabularies, so a fabricated row cannot accidentally trigger any strategy/status-keyed downstream automation. `RskSummary`'s own field constraints are completely unmodified -- no schema change of any kind. A dedicated unit test parses `_SENTINEL_RSK_TEXT` via `parse_rsk` directly and asserts success, independent of any `list_rsk` test, so a future RSK schema change (a new mandatory section, a changed `_TARA_PATTERN`, a renamed heading) is caught at the sentinel's own narrow, fast test rather than surfacing indirectly through `list_rsk`.

**Phase 6 motivation: independent quality review findings (2026-09-04), after the feature's own Phase 5 closeout.** A review conducted separately from this feature's own self-audits re-verified the shipped artifacts against their own claims (running the real quality gate, reading the actual implementation rather than trusting the Updates log, and probing the generic `validate` tool live) and found three concrete, reproducible gaps, none of which invalidate the feature's overall design but which do contradict specific claims recorded as `[x]`/"done"/"no edits needed" above:

1. **Stale docstrings** (REQ-009): 11 of 12 domain `__init__.py` module docstrings still literally list the retired `validate_<d>` tool as existing (confirmed via `grep`), even though Task 2.3/5.2 both claimed a full audit with "no edits needed" -- those audits only covered `AGENTS.md`/`server.py`/prompts, not each domain package's own top-level docstring. `docs/api/*.md` mirrors this stale text verbatim (it regenerates from the docstrings, so "zero drift" after `specmgr docs` only proves the generator matched its stale source, not that the source was accurate).

2. **Unenriched `yaml.YAMLError` messages in `validate`** (REQ-010): live-reproduced by calling `validate(type="req", content=<malformed-YAML-frontmatter doc>, full=True)` directly -- it correctly returns `{valid: False, ...}` (REQ-004's core "never raises" contract holds), but the single error message is PyYAML's raw, un-enriched text (`in "<unicode string>", line 2, column 1`), not `parse_req`'s enriched equivalent (`in "the frontmatter block", line 2`) for the byte-identical input. Root cause: each `_validate_<d>` adapter's `has_frontmatter` probe (`bool(frontmatter.loads(content).metadata)`) runs unconditionally, before `full` is even branched on and entirely outside any `wrap_tool_errors` context, so a malformed-YAML exception raised there never reaches either enrichment layer. This is inherited byte-for-byte from the original per-domain `validate_<d>` tools (a "verbatim port," not a regression this feature introduced), but it directly contradicts REQ-004's own text ("reusing feat-27-validation's already-enriched message... verbatim") for this one of its three named channels, and `tests/general/tools/test_validate.py`'s 15 test methods across 849 lines contain zero `yaml`/`YAMLError` coverage to have ever caught it -- an asymmetry against the parallel `list_<d>` fix in this same feature, which got a dedicated `yaml.YAMLError` test (Task 3.3) specifically because Task 3.1's own design notes flagged that channel by name.

3. **ADR 519d1206's unfulfilled Confirmation commitment** (REQ-011): that ADR's `### Confirmation` section commits to a specific future step -- observing `validate`'s result "intact end-to-end through a live OpenCode session" for both Phase 1 regression fixtures, once Phase 2 shipped -- that no entry in this feature's own Updates log records as ever having been performed.

None of these three gaps required reopening this feature's core design (the generic `validate` tool, the `list_<d>` failure-reporting fix, the RSK sentinel, both ADRs' reasoning all hold up); they are documentation-accuracy and test-completeness fixes plus one narrow, well-scoped code fix, tracked as Phase 6 rather than folding silently back into Phase 2/3/5's already-closed task numbers, so the discrepancy between what was claimed done and what was actually done stays visible in this document's own history rather than being quietly overwritten.

### Related Decisions

- ADR 36905d5b-8057-4294-8665-c7eed5534db0: established the one-generic-dispatch-tool-per-mutation convention (`update`/`set_status`/`delete`) this feature extends to `validate`.

- ADR 519d1206-4d2a-4500-9046-6db635209996: records that `validate`'s non-raising, structured `{valid, errors}` design (REQ-003/004) is fundamentally a workaround for a confirmed, external OpenCode 1.18.27 client-side defect (truncating `isError: true` MCP tool results down to a bare `"Error executing tool <name>"`), not an independently preferred design -- written up separately from this feature's own Design Notes because the rationale generalizes to any future tool in this repo facing the same need.

- ADR 078bf395-0a5f-4afd-84f6-b7a2191a00e6: documents the decision to extend ADR 36905d5b-8057-4294-8665-c7eed5534db0's dispatch-only convention to `validate`, a read-only/dry-run tool category distinct from the mutation-adjacent tools (`update`/`set_status`/`set_classification`/`delete`) that convention originally covered -- mirroring `feat-36-delete`'s own precedent of writing a dedicated ADR even where a general convention already existed.

### Task List

#### Phase 1: Investigation and Inventory

- [x] Task 1.1: Reproduce issue #83's `req` naive-isoformat-timestamp repro against current HEAD via `validate_req`. Done -- see Design Notes.

- [x] Task 1.2: Reproduce issue #83's `dec` em-dash-heading repro against current HEAD via `validate_dec`. Done -- see Design Notes.

- [x] Task 1.3: Record a confirmed-real-or-already-fixed verdict for both, in Design Notes. Done -- verdict recorded, with a root-cause diagnosis that narrows this feature's fix rationale (also spot-checked via `validate_feat`; see Design Notes).

- [x] Task 1.4: Inventory all thirteen current `validate_<d>` tools (signature, domain, behavior) in Design Notes, per issue #81. Done -- see Design Notes.

- [x] Task 1.5: Resolve the open design questions in Design Notes (generic `validate`'s domain list; `{valid, errors}` shape; failed-entry marker/`ref` semantics; `list_<d>` `path`-field parity) -- resolved 2026-09-03 during plan refinement, ahead of Phase 1 kickoff; see Design Notes and the Decisions Made log below.

#### Phase 2: Generic `validate` Tool

- [x] Task 2.1: Implement the generic `validate(type, content, full)` tool in `general/tools/`, dispatching to each of the twelve applicable domains' existing validation logic (`adr` excluded), returning `{valid: bool, errors: list[{message: str}]}` without raising for a content-validation failure. The exception handler must catch exactly `(AssertionError, ValidationError, yaml.YAMLError)`, never a bare `ValueError`, so the `full`/content-shape-mismatch `ValueError` (REQ-004's carve-out) still propagates instead of being absorbed into `{valid: false}`. Done -- `src/biz/dfch/specmgr/general/tools/validate.py` (twelve private `_validate_<d>` adapters, a dispatch table, and the public `validate` `@mcp.tool()`), plus `src/biz/dfch/specmgr/general/models/validate_result.py` (`ValidateResult`/`ValidationErrorEntry`).

- [x] Task 2.2: Create a new ADR documenting the decision to consolidate the twelve per-domain `validate_<d>` tools into the generic `validate(type, content, full)` tool -- extending ADR 36905d5b-8057-4294-8665-c7eed5534db0's dispatch-only convention to a read-only/dry-run tool category, distinct from `update`/`set_status`/`set_classification`/`delete`'s mutation category -- via `create_adr`, then `specmgr adr-toc`; update the placeholder bullet under Related Decisions above with the assigned id. Done -- ADR 078bf395-0a5f-4afd-84f6-b7a2191a00e6 (`docs/adr/078bf395-0a5f-4afd-84f6-b7a2191a00e6-replace-domain-specific-validate-tools-with-a-generic-type-d.md`), `docs/adr/README.md` regenerated, Related Decisions bullet updated.

- [x] Task 2.3: Migrate `create_<d>`/`update_<d>` prompts and `AGENTS.md`'s `validate_<d>` mentions to the generic `validate` tool, for the twelve consolidated domains; `validate_adr` references are left untouched. Done -- all 24 `create_<d>`/`update_<d>` prompt `.py` docstrings/descriptions and their packaged `*_instructions.md` data files updated to reference the generic `validate` tool; `AGENTS.md`'s per-domain bullets, the `general/` bullet, and the "Still genuinely missing" section updated; `server.py`'s own module docstring updated (its per-domain tool lists and the `general/tools/` paragraph).

- [x] Task 2.4: Remove the twelve consolidated per-domain `validate_<d>` tool files (all except `validate_adr`, which remains). Done -- `git rm`'d all twelve `<d>/tools/validate_<d>.py` files and their `__init__.py` imports/`__all__`/docstring registrations.

- [x] Task 2.5: Remove the 12 dedicated `test_validate_<d>.py` files (~1600 lines total; coverage superseded by Task 2.6's generic-tool tests), and update the 6 `test_integration.py` files (dec/feat/sop/sysrs/vcr, plus one more) and the 3 regression tests (`test_issue_27.py`, `test_issue_70.py`, `test_issue_71.py`) plus `tests/general/tools/test_error_context.py` that currently import a `validate_<d>` function directly, repointing each to the generic `validate` tool. Done -- 12 `test_validate_<d>.py` files removed; the 5 affected `test_integration.py` files (dec/feat/sop/sysrs/vcr -- `prb`/`gol`'s own `test_integration.py` never referenced `validate_<d>`, confirmed by search), the 3 regression tests, `tests/general/tools/test_error_context.py`, and `tests/sop/prompts/test_create_sop.py`/`tests/sysrs/prompts/test_create_sysrs.py` (found by a broader search, per this task's own instruction) all repointed to the generic `validate` tool.

- [x] Task 2.6: Unit tests for the generic tool across all twelve applicable domains, plus the two regression fixtures from Phase 1, plus a test that `validate(type="adr", ...)` and any other unsupported `type` still raise `ValueError`, plus a test -- for a representative sample of domains (`req`, `dec`, `vcr`) -- that a `full`/content-shape mismatch (`full=True` with body-only content, and `full=False` with a complete document) still raises `ValueError` through the generic tool rather than being swallowed into `{valid: false}`. Done -- `tests/general/tools/test_validate.py` (15 test methods across 4 test classes, parameterized over all twelve domains' ported fixture bodies).

- [x] Task 2.7: Add a `CHANGELOG.md` `[Unreleased]` entry (**BREAKING**) documenting the twelve `validate_<d>` tool removals and the new generic `validate` tool's non-raising `{valid, errors}` contract. Done -- `CHANGELOG.md` `[Unreleased]` gained an "Added" entry for the new `validate` tool and a "Removed" **BREAKING** entry for the twelve retired `validate_<d>` tools.

#### Phase 3: `list_<d>` Failure Reporting

- [x] Task 3.1: Implement `general/tools/_listing.py::build_summaries()` (per Design Notes), with a default `error_types=(AssertionError, ValidationError, yaml.YAMLError)` -- covering all three of `validate_<d>`'s own documented parse-failure channels, not just the first two, so malformed frontmatter YAML is reported as a failed entry rather than crashing `list_<d>`; add `error_count: int = 0` to `PagedResult` and `path`/`error` to the shared `DocSummary` base; wire all twelve whole-body domains' `list_<d>.py` through the new helper, replacing each domain's own copy-pasted loop -- this necessarily also populates `path=path.resolve()` on every *successful*-entry construction across all twelve domains, since `path` is now mandatory on the shared base (see Design Notes' Phase 3/Phase 4 sequencing note; Task 4.1 only verifies/spot-checks this afterward, it does not introduce new population code); update `AGENTS.md`'s `list_<d>` bullets to mention `error_count`. Done -- `general/tools/_listing.py` (`build_summaries()`, `default_failed_summary()`, `FAILED_TO_PARSE_MARKER`, `DEFAULT_ERROR_TYPES`) added; `PagedResult.error_count: int = 0` and `DocSummary.path: str`/`error: str | None = None` added; `general/tools/_paging.py::paginate()` gained an `error_count: int = 0` parameter threaded straight into the returned `PagedResult`; all twelve `list_<d>.py` files (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`) now route through `build_summaries()`. **Clarification on the "across all twelve domains" wording above**: per this task's own delegated implementation instructions, `feat` is the one deliberate exception -- `list_feat.py`'s `to_summary`/`to_failed_summary` callbacks keep `FeatSummary.path` as the existing *unresolved* `str(path)` in this phase (via `default_failed_summary(..., resolve=False)` for its failed rows), since `FeatSummary` already had its own separate `path` field before this feature and its resolved-path retrofit is explicitly Phase 4, Task 4.2's job, not this one's -- so "all twelve domains" above should be read as "the other eleven domains get a brand-new resolved `path` field; `feat`'s pre-existing `path` field is merely routed through the new helper, unchanged in value." `AGENTS.md`'s twelve `list_<d>` bullets each now mention `error_count`.

- [x] Task 3.2: Implement RSK's sentinel-document construction (`rsk/tools/_sentinel.py`) per Design Notes; wire into `list_rsk`'s `to_failed_summary` callback; add a dedicated unit test that parses `_SENTINEL_RSK_TEXT` via `parse_rsk` and asserts it succeeds, independent of `list_rsk`'s own tests. Done -- `rsk/tools/_sentinel.py` (`_SENTINEL_RSK_TEXT`, `_SENTINEL_RSK_DOCUMENT`, `build_failed_rsk_summary()`) added and wired into `list_rsk.py`; `tests/rsk/tools/test__sentinel.py` added (9 tests, parsing `_SENTINEL_RSK_TEXT` directly, independent of `list_rsk`'s own tests). One deviation from the plan's original design, recorded in Decisions Made below: the sentinel's H1 is a plain descriptive title, not literally `"<failed to parse>"` -- `title` is overridden via `model_copy` (a fifth field, alongside `id`/`status`/`path`/`error`) using the shared `FAILED_TO_PARSE_MARKER` constant, since writing that literal marker text as a markdown H1 is rejected by `models/md`'s own raw-HTML guard and every markdown escape-hatch that survives the guard leaves its own syntax embedded in `.text`'s raw-source-derived output.

- [x] Task 3.3: Regression tests with a mixed valid/unparseable directory for at least two domains, including `rsk`; include at least one malformed-YAML-frontmatter fixture (not just structural/field-validation failures) to exercise the `yaml.YAMLError` path. Done -- `req` and `rsk` (the two mandated domains) each gained a `test_returns_summaries_and_reports_malformed_file_as_a_failed_entry` test (structural-failure fixture, asserting `total`/`error_count`, marker `title`/`status`, `ref`, resolved `path`, `error`) and a dedicated `test_malformed_yaml_frontmatter_is_reported_as_a_failed_entry` test exercising the `yaml.YAMLError` path; every other whole-body domain's own pre-existing `test_list_<d>.py` was also updated (not just left red) since `build_summaries()`'s semantics change broke their old skip-based assertions -- `uc`/`tsk`/`qa`/`prb`/`gol`/`dec`/`sop`/`vcr`/`sysrs`/`feat` all got their `..._skips_malformed_..."` test renamed to `..._reports_malformed_..._as_a_failed_entry` and their `total`/`error_count` assertions updated to match. New `tests/general/tools/test__listing.py` (18 tests) covers `build_summaries()`/`default_failed_summary()` directly (all three `error_types` channels, a non-matching exception propagating, mixed success/failure ordering, custom `error_types`). `tests/general/tools/test_paging.py`/`tests/general/models/test_paged_result.py`/`tests/general/models/test_summary.py` updated for `error_count`/`path`/`error`; `AdrSummary`'s own tests split off into their own, narrower four-field expectation, since `adr` is out of scope for this feature and `AdrSummary` deliberately does not gain `path`/`error`.

- [x] Task 3.4: Add a `CHANGELOG.md` `[Unreleased]` entry (**BREAKING**) documenting `list_<d>`'s `total`/`error_count` semantics change (`total` now includes failed entries alongside successes). Done -- `CHANGELOG.md` `[Unreleased]` gained a "Changed" **BREAKING** entry.

#### Phase 4: `list_<d>` Path Field Parity

- [x] Task 4.1: Confirm/spot-check the `path` field population Task 3.1 already wired into the other eleven whole-body domains' `list_<d>` implementations (see Design Notes' Phase 3/Phase 4 sequencing note -- Task 3.1 necessarily populated `path=path.resolve()` on every successful-entry construction across all twelve domains as an unavoidable consequence of `path` becoming mandatory on the shared base; this task introduces no new field-population code); update `AGENTS.md`'s `list_<d>`/`FeatSummary` bullets to mention the shared `path` field. Done -- confirmed, by reading each of the eleven `list_<d>.py` files, that `path=str(path.resolve())` (successful entries) and a plain `default_failed_summary(...)` call defaulting to resolved (failed entries) are genuinely present for req/uc/tsk/qa/prb/gol/rsk/dec/sop/vcr/sysrs, and that each domain's own `test_list_<d>.py` already asserts `Path(summary.path).is_absolute()`/`Path(failed.path) == broken_path.resolve()` -- no gaps found, no new field-population code introduced. Updated all twelve `list_<d>` bullets in `AGENTS.md` (including `rsk`/`feat`'s own) to mention the (now-shared) resolved `path` field, and rewrote `FeatSummary`'s stale "one extra field" bullet paragraph (see Task 4.2).

- [x] Task 4.2: Retrofit `FeatSummary.path`/`list_feat.py` to also use `path.resolve()` instead of the current unresolved `str(path)`; update any existing `feat` tests that assert on the old unresolved-path format; remove `FeatSummary`'s now-redundant local `path` field declaration, since it is now inherited from `DocSummary`. Done -- `feat/tools/list_feat.py`'s `_to_summary` now builds `path=str(path.resolve())`, and `_to_failed_summary` no longer passes `resolve=False` (that parameter was removed entirely, see Decisions Made); `feat/models/v1/summary.py`'s `FeatSummary` no longer redeclares `path: str` (now purely inherited from `DocSummary`), and its module/class docstrings rewritten accordingly; `tests/feat/tools/test_list_feat.py` gained `Path(summary.path).is_absolute()`/exact resolved-equality assertions (no test asserted the old literal unresolved form, so nothing broke, but the module docstring's stale Phase 3/4 framing was corrected); `tests/general/models/test_summary.py` gained a new `TestFeatSummarySharesDocSummaryBase` class asserting `FeatSummary` now matches every other whole-body domain's exact field set and no longer redeclares `path` in its own `__annotations__`.

- [x] Task 4.3: Revise `DocSummary.ref`'s docstring to drop the "callers must not read this off disk themselves" policy language, since `path` now makes direct reads a sanctioned, first-class option for every whole-body domain. Done -- see the revised docstring quoted in this phase's own Updates entry below.

- [x] Task 4.4: Tests for the new `path` field (all eleven domains) and for `FeatSummary`'s changed, now-resolved `path` behavior. Done -- the eleven other domains' tests already had full `path` coverage from Phase 3 (Task 4.1 confirmed, no gaps to fill); `feat`'s own coverage extended in `tests/feat/tools/test_list_feat.py` (absolute-path assertion for every summary, exact resolved-path equality for the failed entry) and `tests/general/models/test_summary.py` (`TestFeatSummarySharesDocSummaryBase`); `tests/general/tools/test__listing.py`'s now-removed `resolve=False` test replaced with a single `test_path_is_always_resolved` test reflecting the simplified, always-resolving `default_failed_summary` (Decisions Made).

- [x] Task 4.5: Add a `CHANGELOG.md` `[Unreleased]` entry documenting the `path`/`error` fields on all twelve whole-body domains' `list_<d>` summaries and `FeatSummary.path`'s resolved-path retrofit. Done -- amended Phase 3's own "Changed" `list_<d>` bullet to drop its now-stale "`feat`/`FeatSummary` keeps its existing unresolved form for now" parenthetical, and added a new dedicated "Changed" bullet documenting `FeatSummary.path`'s field-removal/resolved-path retrofit.

#### Phase 5: Verification and Closeout

- [x] Task 5.1: Full quality gate (`ruff format --check`, `ruff check`, `vulture`, full `unittest` suite). Done -- all four commands clean (1652 files already formatted, all ruff checks passed, no vulture output, 3342 tests passed via `pytest -n auto --cov=src`); see Updates below.

- [x] Task 5.2: Regenerate `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md`; confirm no `AGENTS.md` edit was missed beyond what Tasks 2.3/3.1/4.1 already covered; confirm the three `CHANGELOG.md [Unreleased]` entries from Tasks 2.7/3.4/4.5 are all present (or consciously squashed into fewer entries if committed together). Done -- `specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc` all re-ran with zero drift (Phases 2-4 already left everything current); `AGENTS.md` audited in full, no stale content found (all twelve `validate_<d>` mentions correctly phrased as "former"/removed, the generic `validate` tool mentioned for all twelve domains, `error_count`/resolved `path` mentioned in all twelve `list_<d>` bullets, "Still genuinely missing" section already correctly names the generic `validate` tool); `CHANGELOG.md [Unreleased]` audited, confirmed all three pieces of information present (consciously squashed into one "Added" + one "Removed" + two "Changed" entries rather than kept as three separate per-phase entries): (a) the `validate` tool addition + twelve `validate_<d>` removals, (b) `list_<d>`'s `total`/`error_count` semantics change, (c) `path`/`error` fields on all twelve domains' summaries + `FeatSummary.path`'s resolved-path retrofit. No edits needed to either file.

- [x] Task 5.3: Comment on GitHub issues #81 and #83 with the outcome; mark this feature done. Done -- see Updates below for the comment URLs.

#### Phase 6: Post-Review Remediation

- [ ] Task 6.1: Audit all twelve domain `__init__.py` docstrings (`dec`/`feat`/`gol`/`prb`/`qa`/`req`/`rsk`/`sop`/`tsk`/`uc`/`vcr`/`sysrs`) for `validate_<d>`-staleness and any other drift; fix each in place (REQ-009). Regenerate `specmgr docs` (`docs/api/`/`docs/GENERATED.md`) and confirm no remaining stale mentions.

- [ ] Task 6.2: Implement the private `_detect_frontmatter(content: str, *, domain: str) -> bool` helper inside `general/tools/validate.py` (kept local to this file per REQ-010's own scoping decision), composing `models/md/_frontmatter_parse.py::enrich_frontmatter_yaml_error` with `wrap_tool_errors`'s domain/tool labeling; replace all twelve adapters' raw `bool(frontmatter.loads(content).metadata)` probes with it. Confirm `TestValidateFullShapeMismatchRaises` and every other pre-existing `test_validate.py` test still passes unmodified.

- [ ] Task 6.3: Add the missing `yaml.YAMLError` regression test(s) to `tests/general/tools/test_validate.py` for at least two domains (e.g. `req`, `dec`), asserting message parity between `validate(type=<d>, ..., full=True)` and `parse_<d>` for identical malformed-YAML-frontmatter input (REQ-010/ACC-010).

- [ ] Task 6.4: Revise ADR 519d1206-4d2a-4500-9046-6db635209996's `### Confirmation` section per REQ-011.

- [ ] Task 6.5: Full quality gate re-run (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, full `pytest -n auto --cov=src`); `specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc` drift checks; add a `CHANGELOG.md [Unreleased]` entry only if warranted (likely not needed -- Phase 6's changes are docstring/test/ADR-only, no MCP tool contract change; record the "no entry needed" conclusion explicitly rather than silently skipping it).

- [ ] Task 6.6: Update Progress/Current Status and the Decisions Made log; mark ACC-009/ACC-010/ACC-011 `[x]`; restore `status: done` in frontmatter once all of Phase 6 is complete.

## Progress

### Current Status

**As of 2026-09-04**: Phases 1-5 complete (REQ-001 through REQ-008, ACC-001 through ACC-008, all `[x]`); **Phase 6 (Post-Review Remediation) added and not yet started** (REQ-009 through REQ-011, ACC-009 through ACC-011, all `[ ]`), following an independent quality review conducted after this feature's own Phase 5 closeout -- see Design Notes' "Phase 6 motivation" note for the three findings driving it. `status` reverted from `done` to `in-progress` accordingly; it goes back to `done` once Phase 6's own Task 6.6 closes it out.

Phases 1-5 summary (unchanged from the original closeout): **all 5 phases, all 8 REQs/ACCs (ACC-001 through ACC-008) done.** Feature drafted from GitHub issues #81 and #83, then refined three times ahead of Phase 1 -- see the earlier Updates entries below for that refinement history. Phase 1 confirmed both of issue #83's repro cases reproduce as client-observed symptoms, root-caused to a client-side tool-error-rendering gap, not a specmgr server-side regression, and inventoried all thirteen `validate_<d>` tools. Phase 2 implemented the generic `validate(type, content, full)` tool in `general/tools/`, recorded the consolidation decision as ADR 078bf395-0a5f-4afd-84f6-b7a2191a00e6, removed the twelve per-domain `validate_<d>` tools and their dedicated tests, and migrated every dependent prompt/test. Phase 3 implemented the shared `general/tools/_listing.py::build_summaries()` helper (REQ-006), added `PagedResult.error_count`/`DocSummary.path`+`error`, wired all twelve `list_<d>.py` files through it so a malformed document now appears inline in `results` as a failed entry (marker `title`/`status`, `ref`, `path`, `error`) and contributes to `total`/`error_count` instead of being silently skipped, built RSK's sentinel-document construction (`rsk/tools/_sentinel.py`) for its own richer `RskSummary`, added regression tests (including a malformed-YAML-frontmatter fixture) for `req`/`rsk` plus updated every other domain's own pre-existing list test for the new semantics, and updated `AGENTS.md`'s twelve `list_<d>` bullets to mention `error_count`. `feat`'s `FeatSummary.path` deliberately kept its existing unresolved form in Phase 3 (Phase 4, Task 4.2's job). Phase 4 closed out REQ-007/ACC-007: confirmed (Task 4.1) the other eleven domains' `path`-field population and test coverage already fully landed in Phase 3, with no gaps; retrofitted `FeatSummary.path`/`list_feat.py` to the same resolved (absolute) form the other eleven domains use, and removed `FeatSummary`'s now-redundant separate `path` field declaration (Task 4.2); revised `DocSummary.ref`'s docstring to drop its "must not read this off disk" policy language (Task 4.3); added/extended tests confirming the new behavior, including simplifying `default_failed_summary` by removing its now-unused `resolve` parameter (Task 4.4, see Decisions Made); and added a `CHANGELOG.md` `[Unreleased]` entry (Task 4.5). Phase 5 (this closeout) re-ran the full quality gate (`ruff format --check`: 1652 files already formatted; `ruff check`: all checks passed; `vulture src/ whitelist.py --min-confidence 60`: no output; `pytest -n auto --cov=src`: 3342 passed) with zero regressions, confirmed `specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc` all already reflect the current state with zero drift, audited `AGENTS.md`/`CHANGELOG.md` in full and found no stale content requiring correction, marked ACC-008 done (REQ-008's regression tests were already implemented in Phases 2/3 and verified passing here), and posted outcome comments to GitHub issues #81 and #83 (see Updates below for the comment URLs). No code changes were needed in Phase 5 -- it is a pure verification/closeout pass.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

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

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-04 18:00:00.000Z - Phase 6 scoping decisions, made during the independent post-closeout quality review

Three implementation-approach decisions were made while turning the review's findings into Phase 6's REQ-009/010/011:

1. **REQ-010's `yaml.YAMLError` enrichment gap is fixed, not just documented.** Considered leaving the behavior as-is (it matches the original per-domain `validate_<d>` tools byte-for-byte) and only correcting REQ-004/the module docstring's overstated "verbatim" enrichment claim plus adding the missing test. Rejected in favor of an actual fix, since `validate`'s entire purpose is consistent, actionable failure reporting, and leaving one of its three named channels quietly worse than the other two undermines that purpose more than the small code change to fix it costs.

2. **The `_detect_frontmatter` helper stays private inside `general/tools/validate.py`, not promoted to a shared `models/md` module.** Considered adding it to `models/md/_frontmatter_parse.py`/`_errors.py` for future reusability. Rejected for now: nothing else in the codebase currently needs this exact composition (`enrich_frontmatter_yaml_error` + `wrap_tool_errors` labeling for a presence-only probe, as opposed to a full parse), and adding it to a shared module speculatively would be scope creep beyond what REQ-010 actually requires.

3. **REQ-011 amends ADR 519d1206's Confirmation section rather than attempting the live-session re-check it originally committed to.** A live MCP-client round-trip isn't something an agent session can reliably automate or independently verify (the same limitation Phase 1's own investigation ran into, requiring a bespoke standalone JSON-RPC script outside the normal tool-calling harness). Rather than attempt and possibly mis-record another ad hoc repro, the ADR's own Confirmation section is corrected to state what was actually verified (unit-level `{valid, errors}` shape reproduction), consistent with this repo's general preference for accurate records over unfulfilled commitments.

4. **`sysrs/__init__.py`'s own unrelated docstring staleness is fixed in the same Phase 6 pass as REQ-009**, rather than filed as a separate cleanup item, since it is discovered and touched during the same twelve-domain `__init__.py` audit and costs nothing extra to fix immediately.

#### 2026-09-04 16:00:00.000Z - Removed `default_failed_summary`'s `resolve` parameter entirely rather than leaving it as dead flexibility

Decided, during Phase 4 implementation, to remove `general/tools/_listing.py::default_failed_summary`'s
`resolve: bool = True` parameter outright rather than simply leaving it in place (still defaulting to
`True`) now that every one of the twelve domains' `to_failed_summary` callbacks resolves. `feat` was the
only caller that ever passed `resolve=False` (Phase 3's own deliberate, temporary carve-out for
`FeatSummary`'s not-yet-retrofitted unresolved `path`); once Task 4.2 retrofitted `feat` to also resolve,
no caller anywhere in the codebase had a remaining use for `resolve=False`, and the parameter's own
Phase-3-era docstring ("`feat` passes `False` in Phase 3 to keep its existing... behavior (Phase 4, Task
4.2 flips this)") would otherwise have become permanently stale, describing a boundary that no longer
exists in the code. Removing it (rather than keeping it as unused, always-`True` optionality) matches this
phase's own prompt's explicit preference ("if no caller needs `resolve=False` anymore, simplifying...is
cleaner and should be preferred over leaving dead flexibility around"). Every caller
(`default_failed_summary(cls, path, error)`/`default_failed_summary(cls, path, error, ref=...)`) and every
place describing the Phase 3/Phase 4 boundary in the past tense (`_listing.py`'s own docstrings,
`list_feat.py`'s module docstring, `AGENTS.md`'s `feat` bullet, this plan's own Design Notes reference to
Task 3.1's sequencing note) were updated so no "Phase 3 exception" language remains describing a boundary
that, after this phase, no longer exists.

#### 2026-09-04 15:00:00.000Z - RSK sentinel's `title` is overridden via `model_copy`, not read off the sentinel's own H1

Decided, during Phase 3 implementation, that the RSK sentinel document's H1 must be a plain
descriptive title (`"RSK Sentinel Document (Internal)"`), not literally the fixed marker text
`"<failed to parse>"` as an earlier draft of the design proposed -- discovered to be technically
infeasible once actually implemented: `models/md`'s own raw-HTML guard
(`models/md/_markdown.py::_assert_no_raw_html`) rejects a bare `<...>` token as an `html_inline`
tag unless it starts with `<!--`, so `# <failed to parse>` fails to parse outright with an
`AssertionError` ("raw HTML is not permitted..."). Every markdown escape-hatch that survives the
guard was tried and rejected in turn: a code span (`` `<failed to parse>` ``) and a backslash
escape (`\<failed to parse>`) both parse successfully, but `MarkdownSection.text`'s composite-case
branch returns the heading's inline token's raw *source* content verbatim (confirmed by direct
inspection of `markdown-it-py`'s token stream), not a markdown-unescaped/rendered string -- so
either escape-hatch leaves its own syntax (backticks, or a literal backslash) embedded in `.text`,
never yielding the bare `"<failed to parse>"` string the design called for. Resolved by keeping
every risk-specific field (`initial_level`/`residual_level`/`strategy`/`scope`/
`residual_probability`/`residual_impact`/`residual_product`) genuinely derived from real parsing
as originally designed, but adding `title` as a fifth `model_copy`-overridden field (alongside
`id`/`status`/`path`/`error`) -- using the exact same `general.tools._listing.FAILED_TO_PARSE_MARKER`
constant every other domain's failed entries use for their own `title`/`status`, so the RSK
sentinel's marker can never drift out of sync with the other eleven domains' even though it is no
longer read off the sentinel document's own H1. `RskSummary`'s field constraints, and every other
part of the original sentinel-document design (a fixed, valid, deliberately worst-case-severity
document parsed once via the real, unmodified `parse_rsk` pipeline), are completely unchanged.

#### 2026-09-04 14:00:00.000Z - `validate`'s unsupported-`type` check is an explicit `ValueError`, not an implicit `KeyError`

Decided, during Phase 2 implementation, that `validate()`'s unsupported-`type` guard (including
`type="adr"`) must be an explicit `if type not in _ADAPTERS: raise ValueError(...)` check rather
than mirroring `delete`'s/`set_classification`'s own actual runtime behavior for the same
misuse -- an implicit `KeyError` from the dispatch-dict lookup itself, confirmed via
`tests/general/tools/test_set_classification.py::test_adr_type_is_not_supported`'s own explicit
`self.assertRaises(KeyError)`. This was called out explicitly, twice, in this phase's own
implementation instructions ("make sure passing `type=\"adr\"` literally raises `ValueError` at
runtime, not just at static-type-check time"), and is required by ACC-004's own wording ("a test
confirms `validate(type=\"adr\", ...)` and any other unsupported `type` still raise
`ValueError`"). `validate` has no `id` parameter and therefore no `_path_safety.validate_id` call
to piggyback the check onto (unlike `delete`/`set_classification`/`update`, which validate `id`
format before dispatch and happen to also raise `ValueError` for other reasons on the way there,
making their own `KeyError`-for-unsupported-`type` behavior easy to overlook) -- so `validate`'s
own explicit check is a deliberate, freestanding guard, not a byproduct of some other validation
path. Note that `update`'s/`set_classification`'s own docstrings already (inaccurately) document
a `ValueError` for an unsupported `type`, so `validate`'s explicit, correct-per-its-own-docstring
behavior is arguably a corrected precedent for future generic tools, not a one-off inconsistency.

#### 2026-09-04 12:00:00.000Z - Independent plan review: write a dedicated ADR for the validate consolidation, fix `list_<d>`'s YAMLError gap, add CHANGELOG/test-migration tasks, clarify path-field sequencing

Decided, following an independent review of this plan before Phase 2 begins, to write a new dedicated ADR for the `validate_<d>` -> generic `validate` consolidation (Task 2.2) rather than relying solely on citing ADR 36905d5b-8057-4294-8665-c7eed5534db0's general convention, since `feat-36-delete` set the precedent of writing its own dedicated ADR for an equivalent per-tool consolidation even though the general convention already existed, and `validate` is arguably a distinct category (read-only/dry-run, not a mutation tool) worth its own explicit record. Decided to add `yaml.YAMLError` to `build_summaries()`'s default failure-catch set (Task 3.1) rather than leaving it at `(AssertionError, ValidationError)` as originally designed, since `parse_<d>` genuinely raises it unwrapped for malformed frontmatter and leaving it uncaught would have shipped an incomplete fix for issue #83(b) (a malformed-YAML document would still crash `list_<d>` outright). Decided to add explicit `CHANGELOG.md [Unreleased]` tasks per phase (2.7/3.4/4.5) rather than leaving CHANGELOG maintenance implicit, matching this repo's own established precedent on the two most directly comparable prior features. Decided to add an explicit test-migration task (2.5) for the dependent test files rather than assuming Task 2.4's "remove the tool files" implicitly covers it, since 22 other test files import a `validate_<d>` function directly and would otherwise break with an unhandled `ImportError` the moment Task 2.4 runs. Decided to keep the `errors: list[{message}]` shape (not switch to a scalar `error: str | None`) despite it holding at most one entry in every case the current implementation can produce, on forward-compatibility grounds, but to say so explicitly in REQ-004/Design Notes rather than leaving the discrepancy undocumented. Decided to clarify, rather than restructure, the Phase 3/Phase 4 boundary for the `path` field: Task 3.1 already has to introduce and populate it for all twelve domains as an unavoidable consequence of it becoming a mandatory field on the shared `DocSummary` base, so Task 4.1 is reworded to a verification/spot-check step instead of pretending to add the field from scratch a second time.

#### 2026-09-04 09:00:00.000Z - Shared `list_<d>` helper, `list_<d>` total/error_count semantics, and RSK's sentinel-document design

Decided to generalize `list_<d>`'s failure-reporting loop into one shared `general/tools/_listing.py` helper (mirroring `general/tools/_doc_paths.py::find_doc_path_by_id`'s existing callback-based precedent) instead of the originally-planned per-domain edits, since the twelve domains' loops are (with the exception of `rsk`/`feat`'s summary-construction step) byte-for-byte identical. Decided `total`'s meaning changes to include failed entries once they are folded into `results` (rather than adding a second "successes only" count field), and `error_count` counts across the whole directory independent of paging, mirroring `total`'s own existing semantics -- both computed for free by materializing the full list, including failures, before `paginate()` slices it. Decided against weakening `RskSummary`'s schema (`Optional` fields) or fabricating schema-valid-but-plausible placeholder risk data to represent a failed RSK document, since the latter is indistinguishable from real, low-severity data in an aggregate risk-matrix view and considered worse than a silent zero (a believable lie, not an obvious absence). Decided instead on a fixed, deliberately worst-case-severity sentinel RSK markdown document, parsed once through the unmodified real `parse_rsk` pipeline, with only the four fields no document could ever supply (`id`, the `status` marker, `path`, `error`) set after parsing via `model_copy` -- keeping `RskSummary`'s schema completely untouched while still surfacing every failed risk document as an unmistakable (title marker plus worst-case severity), non-fabricated-looking row. A dedicated test parses the sentinel text on its own, so a future RSK schema change is caught immediately rather than surfacing indirectly through `list_rsk`.

#### 2026-09-03 17:00:00.000Z - Wrote a full ADR for the client-side-defect workaround rationale

Decided this feature's own Design Notes were not a sufficient home for the reasoning behind `validate`'s non-raising design, since that reasoning -- it exists to work around a confirmed external OpenCode defect, not as an independently preferred design -- generalizes beyond this one feature to any future tool in this repo that signals failure by raising. Wrote ADR 519d1206-4d2a-4500-9046-6db635209996 to record it as a full architectural decision, per this repo's own convention that decisions affecting more than one feature belong in a full ADR rather than a feature-local log.

#### 2026-09-03 16:00:00.000Z - No change to REQ-003/004's design after root-causing the opaque-failure symptom to a client-side gap

Decided not to broaden this feature's scope to "fix" the client-side tool-error-rendering gap that root-causes the opaque-failure symptom observed in Tasks 1.1-1.3, since it lives outside specmgr's own code (in the calling agent's tool-invocation harness) and specmgr has no way to control or detect which MCP client is in use. Decided instead that this finding is evidence *for* REQ-003/004 as already designed, not a reason to change it: since a tool's ordinary successful return value has been observed to pass through completely regardless of size/content, while an `is_error=true` result is empirically at the mercy of a client's own (possibly lossy) rendering, converting `validate` from raise-on-failure to always-returns-`{valid, errors}` sidesteps the lossy path entirely, independent of which client calls it.

#### 2026-09-03 15:00:00.000Z - Design questions resolved during plan refinement

Resolved, ahead of Phase 1, the four open design questions the plan had deferred: (1) the generic `validate` tool's domain list excludes `adr` (12-way, matching `update`/`set_classification`/`delete`'s precedent), since `validate_adr` is structurally different (`id`-based, disk-touching, no `full` parameter) from the twelve identical-signature whole-body `validate_<d>` tools -- `validate_adr` stays standalone and unchanged; (2) the `{valid, errors}` result shape is `errors: list[{message: str}]` with no `field` key, since no existing machinery separates field/line data back out of `feat-27-validation`'s already-fused enriched message strings, and a `field` key would be `None` for `AssertionError`/YAML-sourced errors regardless; (3) a failed `list_<d>` entry uses the fixed marker `title="<failed to parse>"` with `ref=path.stem` (identical to every domain's existing successful-entry derivation), with directory/permission enumeration errors left explicitly out of scope; (4) REQ-007's previously-conditional `path`-field decision is resolved to "yes, implement" for all eleven other whole-body domains, as an absolute/resolved path rather than `FeatSummary`'s current unresolved form -- `FeatSummary.path` itself is retrofitted to match, and `DocSummary.ref`'s "must not read this off disk" docstring policy is revised accordingly, since direct reads become a sanctioned, first-class option for every domain rather than a `feat`-only divergence. Also corrected a stale "eleven" `validate_<d>` tool count to the actual thirteen throughout the plan.

#### 2026-09-03 14:27:36.412Z - Scope and design decisions recorded at creation

Combined issues #81 and #83 into one feature (they cross-reference each other and both concern validation-result reporting). Decided the generic `validate` tool consolidates only `validate_<d>` (not `parse_<d>`/`get_<d>`), matching the existing precedent that only write-adjacent tools are consolidated into generic dispatch tools; the per-domain tools are removed outright once migrated, not kept as backward-compatible wrappers, matching the `update`/`set_status`/`delete` precedent. Decided `list_<d>`'s failure reporting adds an `error_count` header field and folds failed documents directly into `results` (marker `title` + `error` field) rather than a separate parallel array, so a caller sees failures without a second lookup. Decided to investigate first (Phase 1) whether issue #83's own two literal repro cases still reproduce against current HEAD, following the same method `feat-67-70-71` used for issues #70/#71, rather than assuming a code fix is still needed.
