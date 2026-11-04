---
classification: null
created: '2026-11-04T14:21:56.524+01:00'
id: feat-108-fsm
status: progress
type: feat
updated: '2026-11-04T20:18:35.752+01:00'
version: 1.0.0
---

# Feature: set_status honours a per-domain status state machine

## Plan

### Overview

The generic `set_status` tool currently validates a requested status only against each domain's flat closed vocabulary (the pre-load `InvalidStatusResult` check from feat-103) and then writes it regardless of the document's current status. This adds per-domain status state machines: a `set_status` call is honoured only when the transition from the document's current status to the requested target is allowed by that domain's defined machine, rejecting disallowed transitions (issue #108's example: `draft -> proposed -> accepted`, but never `accepted -> draft`). The mechanism is cross-cutting (lives in `general/tools/`, wired through the existing dispatch), domain-owned (each domain defines its table next to its existing `_ALLOWED_STATUSES`), and linked to the shared `general/tools/_domains` registry. A disallowed transition returns a non-raising `InvalidStatusTransitionResult` whose `allowed_values` are the targets valid from the current state. Rollout is phased: the reusable cross-cutting function, then a REQ pilot, then the remaining 13 whole-body domains. ADR is out of scope.

### Requirements

- REQ-001: Each of the 14 whole-body domains defines a `_STATUS_TRANSITIONS` state machine (a mapping from a current status to the allowed target statuses) next to its existing `_ALLOWED_STATUSES` in its own `models/<v>/frontmatter.py`.
- REQ-002: The generic `set_status` enforces the dispatched domain's machine: after loading the existing document and before any write, it rejects a transition whose target is not in that domain's `_STATUS_TRANSITIONS[current_status]`.
- REQ-003: A central `_STATUS_TRANSITIONS_BY_TYPE` aggregation in `general/tools/` is built from the per-domain constants, keyed to the shared `general/tools/_domains` registry (`ALL_DOMAINS`/`WHOLE_BODY_DOMAINS`) with an import-time drift assert, and is opt-in per domain (a domain without a table passes through until its table lands) so rollout can be phased.
- REQ-004: A disallowed transition is rejected before any write (nothing is persisted) with a non-raising `InvalidStatusTransitionResult` (a sibling to `InvalidStatusResult` in `general/models/`) carrying the current status, the requested target, and the allowed target statuses from the current state (not the domain's full vocabulary), so the detail survives MCP clients that truncate `isError` text (the ADR 519d1206 chain).
- REQ-005: The pre-existing pre-load out-of-vocabulary path is unchanged and remains distinct from the new transition check: it still returns `InvalidStatusResult` (the full flat vocabulary) before the doc is loaded, and the no-op on an unchanged status (issue #109), the existing-but-broken `ParseFailureResult`, the path-safety `ValueError`s, and the ADR-only `superseded_by` guard all keep their current order and semantics.
- REQ-006: ADR is excluded from the state machine and keeps its current flat-vocabulary behavior, consistent with its treatment in i18n (feat-197) and feat-170.
- REQ-007: Per-domain tables are authorable as a mapping of status to a list of allowed next statuses (flexible enough to represent cycles, e.g. `review` to `done` and back), normalized to set semantics for membership checks in code.
- REQ-008: The `set_status` tool description, `server.py` docstring, regenerated `docs/MCP.md`, and `AGENTS.md` are updated to document the enforcement, and a new ADR is authored recording the design (domain-owned tables plus central aggregation, the current-state-relative structured result, the two distinct error surfaces, and the ADR exclusion).
- REQ-009: Tests cover, per domain, the full transition matrix (golden), an allowed transition succeeding, a disallowed transition returning `InvalidStatusTransitionResult` with the current-state-relative `allowed_values`, a multi-step cycle, a terminal current state (empty `allowed_values`), the no-op, and the aggregation drift/coverage assert.

### Acceptance Criteria

- [ ] ACC-001: For each of the 14 whole-body domains, `_STATUS_TRANSITIONS` exists in its frontmatter module and is pinned by a per-domain golden matrix test.
- [ ] ACC-002: After its phase lands, `set_status` for a whole-body domain rejects a disallowed transition (e.g. req `accepted` -> `draft`) before any write by returning `InvalidStatusTransitionResult` whose `allowed_values` are the allowed targets from the current state (including an empty list for a terminal current state), and allows the reverse where the table permits.
- [ ] ACC-003: A multi-step cycle (e.g. feat `review` -> `done` -> `progress` -> `done`) succeeds while each step is in the domain's table.
- [ ] ACC-004: The no-op (requested status equals current) still returns success with no write and no `updated` bump.
- [ ] ACC-005: The pre-load out-of-vocabulary `InvalidStatusResult` path is unchanged and still runs before dispatch, distinct from the new transition check.
- [ ] ACC-006: ADR `set_status` behavior is byte-identical to today (no transition enforcement).
- [ ] ACC-007: The `_STATUS_TRANSITIONS_BY_TYPE` drift assert passes; after the final rollout phase it asserts full coverage of the 14 non-ADR whole-body domains.
- [ ] ACC-008: `docs/MCP.md`, `server.py`, and `AGENTS.md` are updated and consistent with a new ADR.
- [ ] ACC-009: The full quality gate is green: ruff format/check, pylint (advisory), vulture, pytest, and `specmgr docs` drift.

### Scope

#### Included

- The state-machine tables for the 14 whole-body domains (req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs, txt, set).
- The cross-cutting transition check wired through the existing `set_status` dispatch (post-load, pre-write).
- The central aggregation, its registry link, and its drift/coverage assert.
- The non-raising `InvalidStatusTransitionResult` channel.
- Per-domain and cross-domain tests, docs updates, and a new ADR.

#### Explicitly Out Of Scope

- ADR (excluded; keeps flat-vocabulary behavior).
- Any change to `create_*` (status is still set by the domain's own default on create; this feature only governs `set_status`).
- The `update`, `edit`, `set_classification`, and `delete` tools.
- Adding new status values to any domain's existing vocabulary (the machine constrains transitions over the current vocabularies only).
- Migrating existing on-disk documents into a "valid" state (the machine governs future `set_status` calls only).
- A general-purpose FSM engine or shared library; this is a declarative per-domain table plus one cross-cutting check.
- i18n (status is a closed vocabulary, never translated; the check applies to the variant's own current status exactly as the no-op does, and is language-invariant).

### Dependencies

#### Depends On

- FEAT feat-103-set-status-error (the existing `InvalidStatusResult` non-raising precedent the new result mirrors).
- FEAT feat-125-domain-lists (the `general/tools/_domains` single source of truth the aggregation links to).

#### Blocks

- The reserved `ac` domain's onboarding must define a `_STATUS_TRANSITIONS` table when it lands, to satisfy the final full-coverage assert.

### Design Notes

The check runs inside each `_set_status_<d>` adapter, immediately after the existing no-op comparison (`existing.frontmatter.status == status`) and before the `raw_body` re-read and `write_<d>_file` — so it needs the current status, rejects before any write, and does not disturb the no-op, out-of-vocabulary, `ParseFailureResult`, or path-safety order. A shared pure helper (e.g. `general/tools/_status_fsm.py`) takes `(type, current, target)` and returns an `InvalidStatusTransitionResult` or `None`; adapters call it and return early on a miss. The ADR adapter is untouched.

Two distinct error surfaces: (A) the pre-existing pre-load out-of-vocabulary check, which keeps returning `InvalidStatusResult` with the full flat vocabulary (it runs before the doc is loaded, so no current state is known); and (B) the new post-load transition check, which returns `InvalidStatusTransitionResult` with the allowed targets from the current state.

Representation: each domain's table is a `dict[str, frozenset[str]]` (current status -> allowed targets), authorable as `status: [targets]` per REQ-007; an empty target set marks a terminal state. The central `_STATUS_TRANSITIONS_BY_TYPE: dict[str, dict[str, frozenset[str]] | None]` is built from the per-domain constants; `None` means "no table yet" (passthrough) during phased rollout, so the aggregation's import-time assert starts as a subset check and tightens to full coverage of the 14 non-ADR whole-body domains after the final phase. ADR has no entry (excluded).

The `InvalidStatusTransitionResult` model (sibling to `InvalidStatusResult`, both exported from `general/models/__init__.py`):

```text
InvalidStatusTransitionResult
  valid:          False
  type:           "req"
  from_status:    "accepted"        # current, loaded from disk
  to_status:      "draft"           # requested
  allowed_values: [...]             # targets allowed from from_status, sorted (not the full vocab)
  message:        "Invalid status transition 'accepted' -> 'draft' for type 'req'. "
                  "Allowed from 'accepted': implemented, rejected, superseded, deprecated"
```

Terminal edge case: when `from_status` has an empty allowed set, `allowed_values` is `[]` and the message reads `"... Status 'superseded' is terminal (no outgoing transitions)."`

Proposed per-domain tables (defaults, cycling-friendly, each adjustable in review; ADR excluded):

```text
req  (also gol):
  draft:      [proposed, rejected]
  proposed:   [accepted, rejected, draft]
  accepted:   [implemented, superseded, deprecated, rejected]
  rejected:   [proposed, draft]
  implemented:[superseded, deprecated]
  superseded: []
  deprecated: []

uc:
  draft:      [proposed]
  proposed:   [accepted, draft]
  accepted:   [superseded, deprecated]
  deprecated: []
  superseded: []

dec:
  draft:      [proposed, rejected]
  proposed:   [accepted, rejected, draft]
  accepted:   [superseded, deprecated, rejected]
  rejected:   [proposed, draft]
  superseded: []
  deprecated: []

tsk  (also qa):
  draft:     [active, cancelled]
  active:    [done, cancelled, draft]
  done:      [active, cancelled]
  cancelled: [draft, active]

prb:
  draft:     [active, cancelled]
  active:    [resolved, cancelled, draft]
  resolved:  [active, cancelled]
  cancelled: [draft, active]

rsk:
  open:       [mitigating, accepted, occurred, dropped]
  mitigating: [accepted, occurred, closed, dropped, open]
  accepted:   [mitigating, occurred, closed, dropped]
  occurred:   [closed, mitigating, dropped]
  closed:     [open, occurred]
  dropped:    [open]

sop  (also sysrs):
  draft:    [review, approved]
  review:   [approved, draft]
  approved: [active, retired, review]
  active:   [retired, review]
  retired:  [active, review]

feat:
  planning: [progress]
  progress: [review, planning]
  review:   [done, progress]
  done:     [progress, review]

vcr:
  draft:    [progress]
  progress: [complete, draft]
  complete: [approved, progress]
  approved: [progress]

txt:
  draft:    [progress]
  progress: [done, draft]
  done:     [progress]

set:
  draft:    [progress, review]
  progress: [review, done, draft]
  review:   [done, progress]
  done:     [progress, review]
```

### Related Decisions

- ADR b399f1ce-ed42-4929-b01c-7a57d18e8014 (feat-103): the `set_status` non-raising `InvalidStatusResult` precedent the new result mirrors.
- ADR 519d1206-4d2a-4500-9046-6db635209996: the non-raising structured-result workaround chain the `InvalidStatusTransitionResult` extends.
- ADR c4efbde6-fd19-4aa8-8668-95316ed62dcc (feat-125): the `general/tools/_domains` single source of truth the aggregation links to.
- ADR 38efdb66 (feat-197): status is a closed vocabulary, never translated (the machine is language-invariant).
- New ADR to be authored in this feature recording the design.

### Task List

#### Phase 100: Cross-cutting mechanism

- [x] Task 100.100: Add the `InvalidStatusTransitionResult` model to `general/models/` (sibling to `InvalidStatusResult`) and export it from `general/models/__init__.py`.
- [x] Task 100.110: Build the central `_STATUS_TRANSITIONS_BY_TYPE` aggregation in `general/tools/` (keyed to the `_domains` registry, opt-in per domain with `None` = passthrough) plus the shared pure check helper `(type, current, target) -> InvalidStatusTransitionResult | None`, with the import-time drift assert.
- [x] Task 100.120: Wire the helper into each `_set_status_<d>` adapter post-load/pre-write (after the no-op comparison, before the raw-body re-read/write), preserving the no-op, out-of-vocabulary, `ParseFailureResult`, and path-safety order (table-less domains pass through until Phases 110/120 land their respective tables); leave the ADR adapter untouched.

#### Phase 110: Pilot — REQ

- [x] Task 110.100: Define `req`'s `_STATUS_TRANSITIONS` in `req/models/v1/frontmatter.py` next to `_ALLOWED_STATUSES`.
- [x] Task 110.110: End-to-end REQ tests (an allowed transition; a disallowed one e.g. `accepted` -> `draft` returning `InvalidStatusTransitionResult` with current-state-relative `allowed_values`; a multi-step cycle; a terminal current state with empty `allowed_values`; the no-op; and out-of-vocabulary still returning `InvalidStatusResult`).

#### Phase 120: Roll out the remaining 13 whole-body domains

- [ ] Task 120.100: Define the remaining 13 domains' `_STATUS_TRANSITIONS` (uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs, txt, set) per the Design Notes tables.
- [ ] Task 120.110: Per-domain golden transition-matrix tests (including each domain's cycle and terminal cases).
- [ ] Task 120.120: Tighten the aggregation coverage assert to full (all 14 non-ADR whole-body domains present).

#### Phase 130: Docs and registry sync

- [ ] Task 130.100: Update the `set_status` tool description and the `server.py` docstring.
- [ ] Task 130.110: Regenerate `docs/MCP.md` and update `AGENTS.md`.
- [ ] Task 130.120: Author the ADR recording the design (domain-owned tables plus central aggregation, the current-state-relative structured result, the two distinct error surfaces, and the ADR exclusion).

#### Phase 140: Quality gates

- [ ] Task 140.100: ruff format/check plus pylint (advisory) plus vulture.
- [ ] Task 140.110: Full pytest suite, `specmgr docs` drift, and `specmgr lint`.

## Progress

### Current Status

Phase 110 (Pilot — REQ) is complete. `req`'s own `_STATUS_TRANSITIONS` state machine (Task 110.100) is defined in `req/models/v1/frontmatter.py` next to `_ALLOWED_STATUSES` (authorable list-of-lists form normalized to a `dict[str, frozenset[str]]`, with import-time vocabulary-coverage and in-vocabulary-target asserts) and wired into the central `_STATUS_TRANSITIONS_BY_TYPE` aggregation in `general/tools/_status_fsm.py` (the `req` entry carries the domain's own constant by identity; the other 13 whole-body entries stay `None` = passthrough; no `adr` entry). The `set_status` tool now enforces the machine for `req` post-load/pre-write (Task 110.110): the end-to-end coverage lives in the new `tests/general/tools/test_set_status_fsm_req.py` (allowed/disallowed/terminal/no-op/out-of-vocabulary pins plus the full 7x7 transition matrix, all asserting on-disk file state) and the golden table pin in `tests/req/models/v1/test_frontmatter.py`. Phase 100's mechanism (model, aggregation, helper, adapter wiring) and the ADR adapter are unchanged in behavior for every domain other than `req`. Next: Phase 120 (Roll out the remaining 13 whole-body domains).

### Blockers

- None.

### Updates

<!-- Newest first. -->

#### 2026-11-04T19:18:35.000Z - Implemented Phase 110: the REQ pilot (table + end-to-end tests)

Implemented Phase 110 (Tasks 110.100/110.110). Task 110.100: `req`'s own `_STATUS_TRANSITIONS` in `req/models/v1/frontmatter.py` next to `_ALLOWED_STATUSES` -- the locked Design Notes table (draft -> [proposed, rejected], proposed -> [accepted, rejected, draft], accepted -> [implemented, superseded, deprecated, rejected], rejected -> [proposed, draft], implemented -> [superseded, deprecated], superseded/deprecated terminal) authored as a private list-of-lists `_STATUS_TRANSITIONS_RAW` and normalized to the public-to-module `dict[str, frozenset[str]]` the aggregation requires, with import-time asserts pinning full vocabulary coverage (`set(table) == _ALLOWED_STATUSES`) and in-vocabulary targets. Task 110.110: `general/tools/_status_fsm.py`'s `_STATUS_TRANSITIONS_BY_TYPE` `req` entry now carries the domain's own constant by identity (the other 13 whole-body entries stay `None` = passthrough; the Phase-100 subset-form drift assert is unchanged and now active for `req`; no `adr` entry); the module's Phase-100 "every entry None / byte-identical" wording is updated in `_status_fsm.py` and in `set_status.py`'s module docstring (the `@mcp.tool` description and `server.py` stay untouched for Phase 130; `_set_status_adr` is byte-identical, ACC-006). Tests: new `tests/general/tools/test_set_status_fsm_req.py` (the per-domain e2e home; temp `SPECMGR_DOCS_DIR` + real `create_req` seed + public `set_status`, every case asserting the on-disk file) -- allowed `draft` -> `proposed` (status on disk, `updated` bumped, body byte-identical); disallowed `accepted` -> `draft` (`InvalidStatusTransitionResult`, `allowed_values == ["deprecated", "implemented", "rejected", "superseded"]` pinned, exact normal-form message, file byte-identical); the multi-step cycle `draft` -> `proposed` -> `draft` -> `proposed` -> `accepted`; terminal `superseded` (empty `allowed_values`, exact terminal-form message, file untouched); the no-op on a terminal state (success, no write, no `updated` bump -- pinning no-op-before-transition-check order); out-of-vocabulary `"bogus"` on a `draft` and an `accepted` req (still the distinct pre-load `InvalidStatusResult` with the full flat vocabulary, file untouched); and the full 7x7 matrix walk (49 (current, target) pairs through the public tool, each classified no-op/allowed/rejected exactly as the landed table says, with the exact per-pair message form). The golden table pin (exact normalized equality + terminals + coverage + in-vocabulary targets + the 7x7 matrix) lives in `tests/req/models/v1/test_frontmatter.py`. The Phase-100 seam state changed accordingly: `test_set_status.py`'s req `_CASES.valid_status` re-targeted `"accepted"` -> `"proposed"` (a fresh req's `draft` -> `accepted` is now a rejected transition, so the positive/no-op/spy rows drive the allowed edge; the seam test methods and their wiring/no-op/order pins are otherwise unchanged), and `test__status_fsm.py`'s "every entry None" pin became the Phase-110 pair (`req` entry is the landed domain table by identity and equals the locked shape; every other entry still `None`) plus a no-patching landed-table enforcement test. Direct Phase-110 fallout repaired in two out-of-gate i18n modules whose ACC-006 rows picked a disallowed-from-`draft` target for `req` (alphabetical pick `accepted`): `test_i18n_all_domains.py` gained the shared `_set_status_target(spec)` helper (req -> `proposed`, every other domain unchanged) and `test_i18n_closed_vocabulary.py` uses it. Gate: `ruff format --check` (2411 files already formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (no output), `pytest -n auto tests/req tests/general/tools/test_set_status_fsm_req.py tests/general/tools/test__status_fsm.py tests/general/tools/test_set_status.py tests/general/models` (375 passed), plus the repaired i18n modules and the adjacent wiring/guard/error-context modules (428/428 and 37/37 passed in the combined runs); `specmgr docs` regenerated `docs/api/..._status_fsm.md`, `docs/api/...set_status.md` (the wording updates) and `docs/GENERATED.md` (test-file count 519 -> 520), all staged.

#### 2026-11-04T15:52:00.000Z - Implemented Phase 100: the cross-cutting status state-machine mechanism

Implemented Phase 100 (Tasks 100.100/100.110/100.120). Task 100.100: `InvalidStatusTransitionResult` (`general/models/invalid_status_transition_result.py`, a sibling of `InvalidStatusResult`, exported from `general/models/__init__.py`) with the locked `valid`/`type`/`from_status`/`to_status`/`allowed_values`/`message` shape and the two locked message forms (normal with the sorted `allowed_values` joined in field order, terminal with an empty list). Task 100.110: `general/tools/_status_fsm.py` — the `_STATUS_TRANSITIONS_BY_TYPE` aggregation (one entry per `WHOLE_BODY_DOMAINS` member, every value `None` in Phase 100, no `adr` entry), the Phase 100 subset-form import-time drift assert (keys ⊆ `WHOLE_BODY_DOMAINS`, `ADR` absent, every non-`None` table's current-status keys and target values checked against the domain's own `_ALLOWED_STATUSES` — vacuous today, active from Phase 110), the pure core `decide_transition(table, type_, current, target)`, and the public `check_status_transition(type_, current, target)` (module stays mcp-free like the other `_private.py` helpers). Task 100.120: the helper is wired into all 14 whole-body `_set_status_<d>` adapters in `set_status.py` immediately after the no-op comparison and before the raw-body re-read; each adapter's return annotation and the `_SetStatusFrontmatter` union alias (and the public `set_status` docstring Returns) carry the new member; the module docstring documents the two-error-surface design. The `@mcp.tool` description and `server.py` are untouched (Phase 130); `_set_status_adr` is byte-identical (ACC-006). Tests: `tests/general/models/test_invalid_status_transition_result.py` (model shape + both message forms), `tests/general/tools/test__status_fsm.py` (aggregation invariants, the pure core's passthrough/allowed/disallowed/terminal/not-a-key paths, the helper's lookup), and a new `TestSetStatusTransitionSeam` in `tests/general/tools/test_set_status.py` (spy-pinned wiring + passthrough for req/feat, the no-op-first and out-of-vocabulary-first order pins). Gate: `ruff format --check` (2408 files clean), `ruff check` (clean), `vulture --min-confidence 60` (clean; `whitelist.py` gained the two unique model field names `from_status`/`to_status`), targeted pytest (`tests/general/models` + `test__status_fsm.py` + `test_set_status.py` + `test__domains.py`: 216 passed), wider sweep `tests/general` + `tests/set` (1476 passed). `specmgr docs` regenerated (two new API pages, updated indexes).

#### 2026-11-04T14:08:46.000Z - Applied plan-refinement findings (G1, D1, I1)

Applied the three findings from a plan-refinement pass. G1: the two `### Dependencies` entries now carry `FEAT` reference tags, so the machine-readable reference surface coincides with the prose surface. D1: the drafting-era Updates/Decisions entry timestamps are aligned to the frontmatter `created` stamp (the entries cannot predate file creation). I1: Task 100.120 now states the REQ-003 passthrough seam explicitly (table-less domains pass through until Phases 110/120 land their respective tables).

#### 2026-11-04T13:21:56.524Z - Drafted feature plan from issue #108

Created the `feat-108-fsm` plan. Scope is the 14 whole-body domains with ADR excluded. Rollout is phased: a Phase 100 cross-cutting mechanism (the `InvalidStatusTransitionResult` model, the central aggregation linked to the `_domains` registry, and the post-load/pre-write check wired into the adapters), a Phase 110 REQ pilot, and a Phase 120 rollout of the remaining 13 domains. A disallowed transition returns a non-raising result whose `allowed_values` are the targets valid from the current state (distinct from the pre-existing pre-load out-of-vocabulary `InvalidStatusResult`, which keeps the full flat vocabulary). Per-domain tables are domain-owned next to each `_ALLOWED_STATUSES` and expressed as a cycling-friendly `status: [targets]` mapping.

### Decisions Made

#### 2026-11-04T19:18:35.000Z - Phase 110 implementation choices

Locked the Phase 110 implementation details: (a) the `req` table ships as the two-constant shape the orchestrator's locked design anticipated -- a private `_STATUS_TRANSITIONS_RAW` (list literals, the REQ-007 authorable form, exactly the locked table) plus the normalized public-to-module `_STATUS_TRANSITIONS: dict[str, frozenset[str]]` (a dict comprehension, so the source stays list-authored) -- with two import-time asserts in `req/models/v1/frontmatter.py` itself (`set(_STATUS_TRANSITIONS) == _ALLOWED_STATUSES`, every target in-vocabulary) mirroring the aggregation's per-entry check at the domain's own boundary; the aggregation imports the normalized constant (identity, no copy). (b) The e2e module is `tests/general/tools/test_set_status_fsm_req.py` (the orchestrator-named home for the per-domain e2e rows; Phase 120 will add sibling `test_set_status_fsm_<d>.py` modules). (c) Phase-100 test state pins that the locked table invalidates were updated in place rather than left red: `test_set_status.py`'s req `_CASES.valid_status` moved `"accepted"` -> `"proposed"` (a fresh req is `draft`, and `draft` -> `accepted` is now a rejected transition; the seam methods' own wiring/no-op/order pins needed no code change and kept their names), and `test__status_fsm.py`'s "every entry is the None passthrough" test became the Phase-110 pair (req entry is the landed table by identity + locked-shape equality; every other entry still None) with the passthrough loop skipping `req`. (d) Two out-of-gate i18n test modules (feat-197's `test_i18n_all_domains.py` ACC-006 row and `test_i18n_closed_vocabulary.py`'s canonical-status row) picked req's target as the alphabetical first in-vocabulary status other than the create status (`accepted` -- now a disallowed transition from `draft`); they share a new `_set_status_target(spec)` helper in `test_i18n_all_domains.py` (req -> the allowed `proposed`; every other domain byte-identical to the old derivation) instead of special-casing the target inline in both files.

#### 2026-11-04T15:52:00.000Z - Phase 100 implementation choices

Locked the Phase 100 implementation details: (a) `InvalidStatusTransitionResult.allowed_values` is **sorted** (the plan's field spec), and the message joins that sorted field in field order — the plan's Design Notes example lists the values in table order, but the sorted field spec wins, keeping the structured result self-consistent under client-side truncation (the ADR 519d1206 rationale). (b) A `current` status that is not a key of the domain's table is treated as a **terminal state** (empty `allowed_values`, terminal message form) — the decision stays total and deterministic, although this is structurally unreachable once a domain's table pins full vocabulary coverage. (c) The helper module is `general/tools/_status_fsm.py` — the plan's suggested "e.g." name, used as-is. (d) The decision is factored into the pure core `decide_transition(table, type_, current, target)` (the plan's `decide`, renamed for descriptiveness) so the public `check_status_transition` only indexes the aggregation; tests exercise the core with temporary tables without mutating module state (plus one `mock.patch.dict` test for the lookup itself). Bookkeeping: the frontmatter `status` moved `planning` -> `progress` with implementation started.

#### 2026-11-04T13:21:56.524Z - Locked scope, channel, and mechanics during planning

Excluded ADR (consistent with i18n/feat-170). Chose domain-owned tables plus a central aggregation linked to `general/tools/_domains`. Chose a cycling-friendly `status: [targets]` representation so a document can move `review` -> `done` and back. Fixed the failure channel upfront as a non-raising `InvalidStatusTransitionResult` (the current-state-relative `allowed_values` payload makes the structured result the truncation-surviving form, per the ADR 519d1206 chain) and dropped the earlier `ValueError` spike. Kept the pre-load out-of-vocabulary `InvalidStatusResult` distinct and unchanged. Chose phased rollout starting with REQ.

### Related PRs / Commits

- None yet.

### More Information

- GitHub issue: https://github.com/dfch/biz.dfch.SpecMgr/issues/108
- Related prior features: feat-103-set-status-error (the `InvalidStatusResult` precedent), feat-104-109-set-status-noop-dec-docs (the no-op behavior to preserve).
