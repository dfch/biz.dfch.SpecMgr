---
classification: null
created: '2026-09-03 12:38:25.338+02:00'
id: feat-81-83-validation
status: planning
type: feat
updated: '2026-09-03 12:38:25.338+02:00'
version: 1.0.0
---

# Feature: Consolidate Validation Tools and Fix Opaque Validation/List Failures (#81, #83)

## Plan

### Overview

GitHub issues #81 and #83 both concern how this repo's MCP tools report validation failures. Issue #81 asks for an inventory of the (currently eleven) per-domain `validate_<d>` tools and a decision on how to consolidate them, plus whether `list_<d>` should return a document path (already true for `feat` via `FeatSummary.path`), so an agent can read/edit/validate a document with minimum token cost. Issue #83 reports two related problems: (a) a validation failure surfaces only as an opaque, uncaught exception rather than a structured, inspectable result, and (b) `list_<d>` silently reports `total: 0` when every document in a directory fails to parse, indistinguishable from an empty or misconfigured directory. Prior work already closed part of the "opaque" complaint: `feat-27-validation` made every validation exception's message actionable (field path, line, cause/fix hint), and `feat-67-70-71` confirmed the MCP transport forwards that full message to the client unabridged, with no truncation. What remains open is the delivery mechanism itself -- a dry-run check tool (`validate_<d>`) still only ever succeeds or raises, so a caller cannot get back a structured, inspectable `{valid, errors}` result -- plus `list_<d>`'s silent-zero problem, which no prior feature touched. This feature investigates whether issue #83's own two literal repro cases still reproduce against current HEAD (following the same investigate-first method `feat-67-70-71` used for issues #70/#71), then: (1) replaces the eleven per-domain `validate_<d>` tools with one generic, type-dispatched `validate` tool (mirroring the existing `update`/`set_status`/`set_classification`/`delete` precedent, ADR 36905d5b-8057-4294-8665-c7eed5534db0) that always returns a structured `{valid, errors}` result instead of raising for a content-validation failure; (2) fixes `list_<d>` to report parse failures explicitly, via an `error_count` header field and inline failed-document entries in `results`; and (3) decides, and where warranted implements, `list_<d>` summary path-field parity with `FeatSummary.path` across the other eleven whole-body domains.

### Requirements

- REQ-001: Before any implementation, reproduce issue #83's two literal repro bodies (a `req` document with naive-isoformat `created`/`updated` timestamps; a `dec` document with an em dash instead of a hyphen in an `## Updates` sub-heading) against current HEAD through `validate_req`/`validate_dec`, and record in Design Notes whether the reported opaque-failure symptom still reproduces or was already resolved by `feat-27-validation`/`feat-67-70-71`.

- REQ-002: Produce an inventory (in Design Notes) of every current `validate_<d>` tool's signature, domain list, and behavior, as issue #81 explicitly requests, before designing its replacement.

- REQ-003: Replace the eleven per-domain `validate_<d>` tools with one generic, type-dispatched `validate(type, content, full)` tool in `general/tools/`, mirroring the `update`/`set_status`/`set_classification`/`delete` precedent (ADR 36905d5b-8057-4294-8665-c7eed5534db0); the per-domain tools are removed, not kept as wrappers, matching that precedent.

- REQ-004: The generic `validate` tool never raises for a content-validation failure; it always returns a structured result (`{valid: bool, errors: [{field, message}]}`), reusing `feat-27-validation`'s already-enriched, actionable message text verbatim as each error's `message` -- only a shape-mismatch on `full`/`type` (an already-actionable `ValueError` today) may still raise.

- REQ-005: `parse_<d>`/`get_<d>` keep their existing raise-based contract unchanged -- this feature's structured-result change is scoped to `validate` only.

- REQ-006: `list_<d>` (all twelve whole-body domains) reports parse failures explicitly: an `error_count` field alongside `total`/`truncated`, with each failed document appearing inline within `results` -- its `ref` populated, `title` replaced by a fixed marker, and a new `error` field carrying the actual exception message -- rather than being silently omitted.

- REQ-007: Decide, and where warranted implement, whether `list_<d>` summaries for the other eleven whole-body domains gain a `path` field matching `FeatSummary.path`'s existing precedent; record the decision and its rationale in Design Notes regardless of outcome.

- REQ-008: Regression tests reproduce issue #83's two literal repro bodies end-to-end through the new generic `validate` tool, and a directory with a mix of valid and unparseable documents end-to-end through `list_<d>` for at least two domains.

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 -- Design Notes records a confirmed-real-or-already-fixed verdict for both of issue #83's literal repro bodies, reproduced against current HEAD.

- [ ] ACC-002: Verifies REQ-002 -- Design Notes contains a table/list of all eleven current `validate_<d>` tools with signature and behavior.

- [ ] ACC-003: Verifies REQ-003/REQ-004 -- the generic `validate(type, content, full)` tool exists, dispatches to all applicable domains, returns `{valid, errors}` without raising for a content-validation failure, and the eleven per-domain `validate_<d>` tools no longer exist.

- [ ] ACC-004: Verifies REQ-005 -- existing `parse_<d>`/`get_<d>` tests continue to pass unchanged (raise-based contract untouched).

- [ ] ACC-005: Verifies REQ-006 -- a `list_<d>` test with a directory containing both valid and unparseable documents asserts `error_count` is correct and each failed document appears in `results` with `ref`/marker/`error` populated.

- [ ] ACC-006: Verifies REQ-007 -- Design Notes records the path-field decision, and if "yes", every affected domain's summary type gains the field with a passing test.

- [ ] ACC-007: Verifies REQ-008 -- the regression tests described exist and pass.

### Scope

#### Included

- Investigation/reproduction of issue #83's two literal repro cases against current HEAD.

- Inventory of all eleven current `validate_<d>` tools (issue #81's explicit ask).

- A new generic, type-dispatched `validate` tool in `general/tools/` returning a structured, non-raising `{valid, errors}` result.

- Removal of the eleven per-domain `validate_<d>` tools once the generic tool is live and tested.

- `list_<d>` fix: `error_count` header field plus inline failed-document entries in `results`, across all twelve whole-body domains.

- Decision, and implementation if warranted, of `list_<d>` summary `path`-field parity with `FeatSummary.path`.

- Regression tests, docstring `Raises`/return-shape updates, `docs/api`/`docs/GENERATED.md`/`docs/MCP.md` regeneration, and an `AGENTS.md` update.

#### Explicitly Out Of Scope

- Consolidating `parse_<d>`/`get_<d>` into a generic dispatch tool -- per the recorded decision, only `validate` is consolidated; reads stay per-domain.

- Changing `parse_<d>`/`get_<d>`'s raise-based error contract -- already actionable per `feat-27-validation`, untouched here.

- New exception types or a typed structural-error channel -- the generic `validate` tool's `{valid, errors}` result is built from the existing enriched exception messages, not a new channel.

- Re-litigating message content quality for `create_<d>`/`update`/`set_status` -- already addressed by `feat-27-validation`/`feat-67-70-71`; this feature only changes `validate`'s and `list_<d>`'s result shape.

- Wiring `validate`/`list_<d>` into CI/pre-commit over the repo's own `.specmgr`/`docs` documents -- tracked separately (ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73).

### Dependencies

#### Depends On

- `feat-27-validation` (done) -- supplies the actionable exception messages this feature's `validate` result reuses verbatim.

- `feat-67-70-71` (done) -- confirmed the MCP transport does not truncate/discard those messages, ruling out a transport-layer explanation for issue #83's reported symptom.

### Design Notes

Open design questions to resolve in Phase 1, recorded here for continuity:

- Whether the generic `validate` tool's `type` parameter includes all twelve domains (the eleven whole-body domains plus `adr`, mirroring `set_status`'s precedent of being the one fully-universal generic tool) or only the eleven whole-body domains (mirroring `update`/`delete`/`set_classification`, which exclude `adr`). Tentatively assumed: all twelve, since `validate_adr` already exists today and issue #81 does not suggest dropping ADR validation.

- The exact shape of `{valid, errors}` -- whether `errors` is a flat list of `{field, message}` or nested to mirror pydantic's own `.errors()` shape; whether `full=True`/`full=False` (frontmatter+body vs. body-only) is preserved as a parameter on the generic tool unchanged from today's per-domain tools.

- The literal marker text for a failed `list_<d>` entry's `title` (e.g. `"<failed to parse>"`) and whether `ref` for such an entry is the filename stem (consistent with every other domain's `ref` semantics for id-less documents) even though the failure may prevent even the filename-based `ref` derivation in some edge cases (e.g. a directory-listing/permission error, as opposed to a parse error).

### Related Decisions

- ADR 36905d5b-8057-4294-8665-c7eed5534db0: established the one-generic-dispatch-tool-per-mutation convention (`update`/`set_status`/`delete`) this feature extends to `validate`.

### Task List

#### Phase 1: Investigation and Inventory

- [ ] Task 1.1: Reproduce issue #83's `req` naive-isoformat-timestamp repro against current HEAD via `validate_req`.

- [ ] Task 1.2: Reproduce issue #83's `dec` em-dash-heading repro against current HEAD via `validate_dec`.

- [ ] Task 1.3: Record a confirmed-real-or-already-fixed verdict for both, in Design Notes.

- [ ] Task 1.4: Inventory all eleven current `validate_<d>` tools (signature, domain, behavior) in Design Notes, per issue #81.

- [ ] Task 1.5: Resolve the open design questions in Design Notes (generic `validate`'s domain list; `{valid, errors}` shape; failed-entry marker/`ref` semantics).

#### Phase 2: Generic `validate` Tool

- [ ] Task 2.1: Implement the generic `validate(type, content, full)` tool in `general/tools/`, dispatching to each domain's existing validation logic, returning `{valid, errors}` without raising for a content-validation failure.

- [ ] Task 2.2: Migrate every caller/reference (prompts, docs, `AGENTS.md`) from the per-domain `validate_<d>` tools to the generic tool.

- [ ] Task 2.3: Remove the eleven per-domain `validate_<d>` tool files.

- [ ] Task 2.4: Unit tests for the generic tool across all applicable domains, plus the two regression fixtures from Phase 1.

#### Phase 3: `list_<d>` Failure Reporting

- [ ] Task 3.1: Add `error_count` and inline failed-document entries (`ref`/marker `title`/`error`) to `list_<d>`'s shared listing helper, across all twelve whole-body domains.

- [ ] Task 3.2: Regression tests with a mixed valid/unparseable directory for at least two domains.

#### Phase 4: `list_<d>` Path Field Parity

- [ ] Task 4.1: Implement the Phase 1 path-field decision (add `path` to the other eleven domains' summary types, or record why not).

- [ ] Task 4.2: Tests for the implemented (or explicitly declined) behavior.

#### Phase 5: Verification and Closeout

- [ ] Task 5.1: Full quality gate (`ruff format --check`, `ruff check`, `vulture`, full `unittest` suite).

- [ ] Task 5.2: Regenerate `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md`; update `AGENTS.md`.

- [ ] Task 5.3: Comment on GitHub issues #81 and #83 with the outcome; mark this feature done.

## Progress

### Current Status

**As of 2026-09-03**: Feature drafted from GitHub issues #81 and #83; no implementation started. Ready for Phase 1's investigation.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-03 14:27:36.412Z - Created

Created from GitHub issues #81 (consolidate validation tools) and #83 (opaque validation errors; `list_<domain>` silently reporting zero on parse failures). Combines both issues into one feature since #83 is referenced by #81 and both concern how validation failures/results are reported by this repo's MCP tools.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-03 14:27:36.412Z - Scope and design decisions recorded at creation

Combined issues #81 and #83 into one feature (they cross-reference each other and both concern validation-result reporting). Decided the generic `validate` tool consolidates only `validate_<d>` (not `parse_<d>`/`get_<d>`), matching the existing precedent that only write-adjacent tools are consolidated into generic dispatch tools; the per-domain tools are removed outright once migrated, not kept as backward-compatible wrappers, matching the `update`/`set_status`/`delete` precedent. Decided `list_<d>`'s failure reporting adds an `error_count` header field and folds failed documents directly into `results` (marker `title` + `error` field) rather than a separate parallel array, so a caller sees failures without a second lookup. Decided to investigate first (Phase 1) whether issue #83's own two literal repro cases still reproduce against current HEAD, following the same method `feat-67-70-71` used for issues #70/#71, rather than assuming a code fix is still needed.
