---
classification: null
created: '2026-11-04T14:21:56.524+01:00'
id: feat-108-fsm
status: review
type: feat
updated: '2026-11-05T19:29:25.000+01:00'
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

- [x] ACC-001: For each of the 14 whole-body domains, `_STATUS_TRANSITIONS` exists in its frontmatter module and is pinned by a per-domain golden matrix test.
- [x] ACC-002: After its phase lands, `set_status` for a whole-body domain rejects a disallowed transition (e.g. req `accepted` -> `draft`) before any write by returning `InvalidStatusTransitionResult` whose `allowed_values` are the allowed targets from the current state (including an empty list for a terminal current state), and allows the reverse where the table permits.
- [x] ACC-003: A multi-step cycle (e.g. feat `review` -> `done` -> `progress` -> `done`) succeeds while each step is in the domain's table.
- [x] ACC-004: The no-op (requested status equals current) still returns success with no write and no `updated` bump.
- [x] ACC-005: The pre-load out-of-vocabulary `InvalidStatusResult` path is unchanged and still runs before dispatch, distinct from the new transition check.
- [x] ACC-006: ADR `set_status` behavior is byte-identical to today (no transition enforcement).
- [x] ACC-007: The `_STATUS_TRANSITIONS_BY_TYPE` drift assert passes; after the final rollout phase it asserts full coverage of the 14 non-ADR whole-body domains.
- [x] ACC-008: `docs/MCP.md`, `server.py`, and `AGENTS.md` are updated and consistent with a new ADR.
- [x] ACC-009: The full quality gate is green: ruff format/check, pylint (advisory), vulture, pytest, and `specmgr docs` drift.

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

- [x] Task 120.100: Define the remaining 13 domains' `_STATUS_TRANSITIONS` (uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs, txt, set) per the Design Notes tables.
- [x] Task 120.110: Per-domain golden transition-matrix tests (including each domain's cycle and terminal cases).
- [x] Task 120.120: Tighten the aggregation coverage assert to full (all 14 non-ADR whole-body domains present).

#### Phase 130: Docs and registry sync

- [x] Task 130.100: Update the `set_status` tool description and the `server.py` docstring.
- [x] Task 130.110: Regenerate `docs/MCP.md` and update `AGENTS.md`.
- [x] Task 130.120: Author the ADR recording the design (domain-owned tables plus central aggregation, the current-state-relative structured result, the two distinct error surfaces, and the ADR exclusion).

#### Phase 140: Quality gates

- [x] Task 140.100: ruff format/check plus pylint (advisory) plus vulture.
- [x] Task 140.110: Full pytest suite, `specmgr docs` drift, and `specmgr lint`.

## Progress

### Current Status

Implementation complete — all five phases (100–140) landed and committed, the full Phase-140 quality gate green (ruff format/check, vulture, full pytest 6131 passed/18 skipped/11203 subtests, `specmgr docs`/`adr-toc`/`mcp-docs` zero drift, `specmgr lint --all` 171 linted/0 failed, pylint advisory 9.03/10 with no feature-code findings), and all nine acceptance criteria (ACC-001…ACC-009) met — the feature is in review. Per-command gate evidence: the 2026-11-05T13:06:43Z Updates entry; per-ACC evidence: the 2026-11-05T15:12:48Z Updates entry. The post-implementation review (feat-reviewer) ran and is complete — all ACCs confirmed met, the single wording finding fixed (`4a360327`), PR #256 CI green; the feature awaits merge (not merged — by design).

### Blockers

- None.

### Updates

<!-- Newest first. -->

#### 2026-11-05T18:29:25.000Z - Post-implementation review run — one finding (D1) fixed, CI re-green

Ran the feat-reviewer post-implementation review (read-only, over `git diff 3d2c3f8..HEAD` at the review commit). It confirmed all nine acceptance criteria met (ACC-003 with the recorded Phase-120 cycle-walk deviation), no behavioral defects, and no blocking gaps, and verified the 14 `_STATUS_TRANSITIONS` tables + the 14 per-domain golden pins byte-exact against the plan's Design Notes, the pre-load-vs-post-load channel order spy-pinned, the ADR adapter diff-free, and `docs/MCP.md`/`server.py`/`AGENTS.md`/ADR a79608e4-88cd-498f-8ca1-445df4d04f92 mutually consistent.

Non-blocking improvement items from the review: I1 = the one actual finding — stale Phase-110 rollout wording in `tests/general/tools/test_set_status.py`'s `TestSetStatusTransitionSeam` class docstring (it still said the `feat` entry "is still the `None` passthrough seam until Phase 120") plus the two `..._passes_through_for_req/feat` test method names, wording-only (the pins drive table-ALLOWED transitions: req `draft` -> `proposed`, feat `planning` -> `progress`); I2 (the e2e matrix seeds a fresh document per pair — runtime acceptable, cosmetic) and I3 (`docs/api/` lacks `req.models.v1.frontmatter`/`gol.models.v1.frontmatter` pages — verified pre-existing at the plan's base commit, not feature drift; a candidate follow-up issue) both left as recorded, not actioned.

I1/D1 fixed in commit `4a360327` (`fix(feat-108-fsm): review D1 — stale Phase-110 rollout wording in the set_status seam tests`): the class docstring reworded to the Phase-120-complete reality (every aggregation entry carries the domain's own landed table, no `None` passthrough remains), both seam test methods renamed to `test_transition_check_is_wired_post_load_and_drives_an_allowed_transition_for_req/feat`, method docstrings aligned; no behavior/assertion change; targeted suite green (28 passed, 204 subtests); PR #256 CI re-run fully green (all 8 checks pass on `4a360327`).

#### 2026-11-05T15:12:48.000Z - Set status to review — implementation complete, ACC-001…ACC-009 met

Set the frontmatter `status` to `review` and ticked all nine acceptance criteria (per-ACC evidence below; the per-command quality-gate evidence is the Phase-140 entry beneath).

- ACC-001: every one of the 14 whole-body domains owns `_STATUS_TRANSITIONS` in its `models/<v>/frontmatter.py` next to `_ALLOWED_STATUSES` (the two-constant form — `_STATUS_TRANSITIONS_RAW` list literals plus the normalized `dict[str, frozenset[str]]` — with the two import-time asserts), and each is pinned by its own per-domain golden matrix test (`Test<D>StatusTransitions` in `tests/<d>/models/vN/test_frontmatter.py`: exact normalized equality vs the locked table, terminal/no-terminal pin, key coverage == `_ALLOWED_STATUSES`, in-vocabulary targets, full N×N pair matrix); the tables verified byte-exact to the plan's locked Design Notes.
- ACC-002: `set_status` rejects a disallowed transition pre-write — e.g. req `accepted` -> `draft` returns `InvalidStatusTransitionResult` with `allowed_values == ["deprecated", "implemented", "rejected", "superseded"]` (sorted, current-state-relative, not the full vocabulary) and the exact normal-form message while the on-disk file stays byte-identical (`updated` not bumped); a terminal current state (req/gol `superseded`/`deprecated`, uc/dec same) returns `allowed_values == []` plus the terminal-form message; the reverse/allowed edges persist (`tests/general/tools/test_set_status_fsm_req.py` + `tests/general/tools/test_set_status_fsm_domains.py` — the full per-domain N×N matrix walk through the public tool for all 13 remaining domains).
- ACC-003: the multi-step cycle succeeds while each step is in the domain's table — feat's e2e cycle `planning -> progress -> review -> done -> review -> done` (each step in the locked feat table; note the plan's example segment `progress -> done` is NOT allowed by the locked feat table, so the walk takes the minimal legal back-edge through `review` — the deviation is recorded in this plan's Phase-120 Decisions Made), plus the named cycle walk with a back edge for every other domain.
- ACC-004: the no-op (requested status == current) still returns success with no write and no `updated` bump — pinned on a terminal state (req `superseded` requesting `superseded`: file bytes + mtime unchanged, success shape returned) and on each domain's "final-feeling" state in `test_set_status_fsm_domains.py`; the no-op runs BEFORE the transition check (a terminal state is never rejected on its own status).
- ACC-005: the pre-dispatch/pre-load out-of-vocabulary `InvalidStatusResult` path is unchanged, still runs first, and is distinct from the transition check — spy-pinned (an out-of-vocabulary call never reaches `check_status_transition`), per-domain e2e-pinned (the returned object is `InvalidStatusResult` with the full flat sorted vocabulary, never `InvalidStatusTransitionResult`).
- ACC-006: ADR `set_status` behavior is byte-identical — `_set_status_adr` carries no diff in any phase, the aggregation has no `adr` entry (pinned), and every ADR test in the suite passes.
- ACC-007: the `_STATUS_TRANSITIONS_BY_TYPE` full-coverage import-time assert passes — keys equal `WHOLE_BODY_DOMAINS`, no `None` entry remains, `ADR` absent, per-entry vocabulary checks active; pinned by `tests/general/tools/test__status_fsm.py`.
- ACC-008: `docs/MCP.md` (regenerated via `specmgr mcp-docs` — exactly the two `set_status` description lines), `server.py`'s module docstring (the General-tools `set_status` entry + the sixth extension in the ADR 519d1206 chain paragraph, incl. the f14f125e case-6-slot bookkeeping record), and `AGENTS.md`'s `general/` bullet (the case-6 clause) are all updated and consistent with the new ADR a79608e4-88cd-498f-8ca1-445df4d04f92 (accepted, dated 2026-11-05, `specmgr lint`-clean, `specmgr adr-toc` regenerated).
- ACC-009: the full quality gate green — see the Phase-140 Updates entry above for the per-command evidence (ruff format 2413 files / ruff check / vulture clean / full pytest 6131 passed, 18 skipped, 11203 subtests / `specmgr docs` zero drift / `specmgr lint --all` linted=171 failed=0 excluded=1 / pylint advisory 9.03/10, zero findings naming feature-introduced code).

#### 2026-11-05T13:06:43.000Z - Ran Phase 140: Quality gates (the full gate green on the first run of every command — no fixes needed, nothing pre-existing to record)

Ran Phase 140 (Tasks 140.100/140.110) — the feature's final quality gate, a verification phase: the gates were executed and the concrete evidence below recorded; no feature code, per-domain table, doc wording, or test subject was changed because no gate was red. All commands ran from the worktree root with `uv run --frozen`, in the plan's specified order. (1) `ruff format --check` → `2413 files already formatted` (exit 0). (2) `ruff check` → `All checks passed!` (exit 0). (3) `pylint $(git ls-files '*.py')` → ADVISORY only (CI runs it with `|| true`): `Your code has been rated at 9.03/10 (previous run: 9.00/10, +0.03)` (exit 30) — 5600 finding lines: 267 cyclic-import, 233 duplicate-code, 136 line-too-long, 128 import-outside-toplevel, 69 too-many-locals, 52 too-few-public-methods, 18 too-many-statements, 17 too-many-lines, 12 too-many-instance-attributes, 10 too-many-branches, 8 too-many-arguments, 6 each of too-many-public-methods / too-many-positional-arguments / reimported / redefined-outer-name, 5 too-many-return-statements, 3 too-many-nested-blocks; **zero** name code this feature introduced: `general/tools/_status_fsm.py`, `general/models/invalid_status_transition_result.py`, and all 14 frontmatter `_STATUS_TRANSITIONS` modules are finding-free, and every other finding touching a feature-touched file is pre-existing or convention — the `set_status.py:23` line-too-long line predates the feature's diff (which starts at line 129; the line is the module docstring's 15-domain enumeration), the `server.py:581/649/676/983` line-too-long lines plus `server.py`'s too-many-lines / redefined-builtin 'set' / import-outside-toplevel / wrong-import-position / unused-import findings are all feat-173-era (git blame: commit 8ae323e3, feat-173 Phase 180) — the feature's Phase-130 docstring insertions added no new line of those; the feature's own test files carry only findings that mirror established repo conventions — C0116 missing-function-docstring (203 in feature tests vs 2506 in pre-existing tests), W0212 protected-access (feature tests access the private `_STATUS_TRANSITIONS_BY_TYPE` aggregation by design; 265 repo-wide), E1136 unsubscriptable-object (8 in the new `test_invalid_status_transition_result.py` — the same pydantic `.model_fields` false positive as the 7 pre-existing ones in `models/md/markdown_str.py`, `tests/general/models/test_parse_failure_result.py`, and `tests/qa/models/v2/test_parser.py`) — so no mechanical fix was applied and nothing is blocked. (4) `vulture src/ whitelist.py --min-confidence 60` → clean, no output (exit 0). (5) `pytest -n auto --cov=src --cov-report= -q` → `6131 passed, 18 skipped, 11203 subtests passed in 120.12s (0:02:00)` (exit 0). (6) `specmgr docs` → `✓ Wrote 587 module file(s) to …/docs/api` + `✓ Wrote …/docs/GENERATED.md`; `git status --short` empty afterwards (zero drift vs the committed generated tree) and a second run byte-identical (exit 0). (7) `specmgr lint --all` → `summary: linted=171 failed=0 skipped=0 excluded=1` (exit 0; the one excluded file is the generated `docs/adr/README.md` TOC, unconditionally excluded by design) — every corpus document parses, including this feature's new ADR `docs/adr/a79608e4-88cd-498f-8ca1-445df4d04f92-*.md` and this README. (8) Generator idempotency (final confirmation): `specmgr adr-toc` (`✓ Wrote docs/adr/README.md`) and `specmgr mcp-docs` (`✓ Wrote …/docs/MCP.md`) each left `git status --short` empty, and the sha256 of both generated files after a second pass of each generator is identical to after the first (byte-identical; no uncommitted drift anywhere). Working tree ends clean of generated artifacts; the only working-tree changes after the phase are this README's own Phase-140 bookkeeping (task ticks, Current Status, this entry, the frontmatter `updated` bump, `status` still `progress`).

#### 2026-11-05T10:26:32.000Z - Implemented Phase 130: Docs and registry sync (tool description, server.py docstring, docs/MCP.md, AGENTS.md, the ADR)

Implemented Phase 130 (Tasks 130.100/130.110/130.120; documentation + ADR only — no code behavior, adapter, dispatch, test, or per-domain table touched). Task 130.120 (executed first so the other deliverables could cite the new ADR): `docs/adr/a79608e4-88cd-498f-8ca1-445df4d04f92-per-domain-status-state-machines-for-set-status-domain-owned.md` ("Per-domain status state machines for set_status: domain-owned tables, central aggregation, and the non-raising, current-state-relative transition result"), authored through the structured `create_adr`/`set_status` MCP tools per the ADR 898bfcd0-85f9-462f-93a8-747bda4166c8 mandate (server-assigned id; `status: accepted`, `date: 2026-11-05`, `decision-makers: OpenCode agent + user decision (plan locked during feat-108-fsm planning)`). Content: the Context (issue #108 — `set_status` wrote any in-vocabulary status regardless of the current one, so `accepted -> draft` was possible; the case-6 slot of the ADR 519d1206 chain; the record that f14f125e's "delete as the later candidate (case 6) if ever addressed" prediction is overtaken — this ADR takes the case-6 slot for the `set_status` transition surface, `delete` remains the later candidate, and no accepted ADR is edited or superseded, refined by reference only); the Decision Drivers (the machine domain-owned next to each `_ALLOWED_STATUSES` while the enforcement stays one cross-cutting check in `general/tools/` wired through the existing dispatch; the non-raising current-state-relative result as the truncation-surviving form (the ADR 519d1206 rationale); the pre-write guarantee — nothing persisted, `updated` not bumped; the undisturbed channel order, REQ-005; the phased-rollout opt-in seam (`None` entry = passthrough); the cycling-friendly `status: [targets]` representation; the ADR exclusion per the feat-197/feat-170 precedent; no on-disk migration); four Considered Options with Pros/Cons (Option 1 per-domain duplicated `set_status`-side checks — rejected as drift-prone with no registry key; Option 2 the chosen declarative tables + central aggregation + single pure check; Option 3 raising `ValueError` — rejected: the current-state-relative allowed-targets detail is exactly what `isError` truncation destroys, and case 2 is this same tool's own non-raising precedent; Option 4 a shared FSM engine/library — rejected per the plan's Explicitly Out Of Scope); the Decision Outcome (the two distinct error surfaces with the exact normal/terminal message forms, the locked per-domain tables cited by reference to this plan's Design Notes rather than pasted, the enforcement point post-load/pre-write inside the domain lock immediately after the no-op comparison, the ADR exclusion, the unchanged channel order, the no-migration consequence, the full-coverage assert tightening after the final phase, and the chain-bookkeeping record); Consequences (Good/Bad incl. the sixth asymmetric-contract caveat, the widened return union, the stuck-document trade-off, and the tracked-but-not-blocking live-client-round-trip limitation) and Confirmation (implemented and tested on the feat-108-fsm branch — full suite green at Phase 120, 6131 passed/18 skipped; the per-domain tables are the plan's user-approved defaults); More Information (issue URL, this feature folder, and the related ADRs 519d1206/b399f1ce/9080b37c/c4efbde6/38efdb66-8025-45c5-bbe8-45b25fc7a772/f14f125e/898bfcd0 with their full titles). `specmgr adr-toc` regenerated `docs/adr/README.md` (the new ADR's row), and `specmgr lint` full-parses the new ADR cleanly. Task 130.100: (a) the `@mcp.tool(name="set_status")` `description=` in `src/biz/dfch/specmgr/general/tools/set_status.py` gained a closing per-domain state-machine paragraph — each whole-body domain's own `_STATUS_TRANSITIONS` table (next to its `_ALLOWED_STATUSES` in its frontmatter module) enforced post-load/pre-write immediately after the unchanged-status no-op comparison; a disallowed transition returns the non-raising `InvalidStatusTransitionResult` (`{valid: false, type, from_status, to_status, allowed_values, message}`) instead of writing — `allowed_values` are the targets allowed FROM THE CURRENT STATE, sorted, never the domain's full flat vocabulary, and an empty `allowed_values` marks a terminal current state whose message reads `... Status '{from_status}' is terminal (no outgoing transitions).`; nothing persisted (`updated` not bumped); the two distinct surfaces (the case-2 pre-dispatch/pre-load `InvalidStatusResult` still runs first, unchanged; the transition check is case 6 of the ADR 519d1206 chain); `type="adr"` excluded (keeps its flat-vocabulary behavior); citing issue #108 + ADR a79608e4; (b) the public `set_status` docstring's Returns section: the stale "During the phased rollout a domain whose table has not landed yet passes through unchanged" sentence replaced by the rollout-complete wording ("The rollout is complete as of Phase 120 (every whole-body domain's own table has landed and is enforced), and `type=\"adr\"` never produces this result (REQ-006: ADR keeps its flat-vocabulary behavior).") plus the new ADR id in the case-6 citation; (c) the module docstring's FSM paragraph head now cites the new ADR id. The `@mcp.tool` description is the piece that was missing (the module-level Returns prose had been updated in Phases 100–120). `_set_status_adr`, the adapters, and the dispatch are untouched. Task 130.110: (a) `docs/MCP.md` regenerated via `uv run --frozen specmgr mcp-docs` — exactly the two `set_status` description lines changed (the tool table row + the `### Tool: set_status` detail section), the new FSM paragraph included verbatim, a second run byte-identical; (b) `AGENTS.md` (repo root): the big `general/` bullet's chain paragraph gained the case-6 clause — inserted after the case-5 (f14f125e) clause and before the `_CAUGHT_EXCEPTIONS` definition clause (chain numbering 4 → 2-reminder → 5 → 6 preserved), naming `set_status`'s second post-load error surface (a sixth extension of the same chain, feat-108-fsm, GitHub issue #108, ADR a79608e4): each whole-body domain's own `_STATUS_TRANSITIONS` next to its `_ALLOWED_STATUSES`, the central `general/tools/_status_fsm.py` aggregation keyed to the `general/tools/_domains` registry (full-coverage import-time assert), the post-load/pre-write enforcement point immediately after the unchanged-status no-op comparison, the non-raising `InvalidStatusTransitionResult` (current-state-relative sorted `allowed_values`; `[]` plus the terminal message form; nothing written, `updated` not bumped), `adr` excluded, with the case-2 `InvalidStatusResult` still running pre-lock/pre-load first (unchanged); no per-domain bullet and no other section touched. `src/biz/dfch/specmgr/server.py`'s module docstring (Task 130.100b): the General-tools `set_status` entry gained the condensed state-machine + second-error-surface wording, and the 519d1206 chain paragraph — which ended at "A fifth extension (feat-204-create-error, ...)" — gained the sixth-extension sentence plus the one chain-bookkeeping record (f14f125e's "delete as the later candidate (case 6)" prediction overtaken; this ADR takes the case-6 slot for the `set_status` transition surface; `delete` remains the later candidate; no accepted ADR edited). Gate evidence: `ruff format --check` (2413 files already formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (clean, exit 0), full suite `pytest -n auto --cov=src --cov-report= -q` (6131 passed, 18 skipped, 11203 subtests passed, 119.62s — identical counts to Phase 120, no doc-driven regressions), `specmgr mcp-docs` (regenerated; second run byte-identical; `git status --short docs/MCP.md` = the one expected `M`), `specmgr adr-toc` (regenerated; second run byte-identical; `docs/adr/README.md` `M` + the new untracked ADR file), `specmgr docs` (regenerated; exactly `docs/api/biz.dfch.specmgr.general.tools.set_status.md` + `docs/api/biz.dfch.specmgr.server.md` changed, docstring-only diffs; second run made no further changes), `specmgr lint docs/adr/a79608e4-....md` (linted=1 failed=0 skipped=0 excluded=0).

#### 2026-11-05T04:35:53.000Z - Implemented Phase 120: the remaining 13 whole-body domains (tables + tightened assert + golden/e2e tests + fallout fixes)

Implemented Phase 120 (Tasks 120.100/120.110/120.120). Task 120.100: the locked Design Notes `_STATUS_TRANSITIONS` table for each of the 13 remaining whole-body domains (`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`/`txt`/`set`), each mirroring the `req` pilot byte-for-byte in shape: the module docstring note, the private list-of-lists `_STATUS_TRANSITIONS_RAW` (REQ-007 authoring form, the exact locked table), the normalized `_STATUS_TRANSITIONS: dict[str, frozenset[str]]` (dict comprehension), and the two import-time asserts (key coverage == the domain's own `_ALLOWED_STATUSES`, every target in-vocabulary); no `_ALLOWED_STATUSES` or validator touched. `general/tools/_status_fsm.py` now imports all 14 domains' `_STATUS_TRANSITIONS` and `_STATUS_TRANSITIONS_BY_TYPE` carries every whole-body domain's own landed constant by identity (annotation tightened to non-`None` values). Task 120.120: the aggregation's import-time drift assert is the full-coverage form (keys == `WHOLE_BODY_DOMAINS`, no entry `None`, `ADR` absent kept, per-entry vocabulary checks kept); the module docstring, the aggregation comment, and the `set_status.py` module docstring's stale "other domains still pass through" wording are updated (the `@mcp.tool` description and `server.py` stay untouched for Phase 130; `_set_status_adr` untouched, ACC-006). Task 120.110: a `Test<D>StatusTransitions` golden class in each of the 13 domains' own `tests/<d>/models/vN/test_frontmatter.py` (exact normalized equality vs the locked `_EXPECTED_TRANSITIONS`, the terminal pin for `uc`/`dec`/`gol` and the explicit no-terminal-state pin for the other ten domains, key coverage == `_ALLOWED_STATUSES`, in-vocabulary targets, full N×N pair matrix), the new sibling e2e module `tests/general/tools/test_set_status_fsm_domains.py` (all 13 domains in one module: per-domain spec dataclass pinned to the aggregation's own landed constants, the FULL N×N matrix walk through the public `set_status` with on-disk assertions — 25+16+16+16+49+36+36+25+16+16+25+9+16 pairs —, the named multi-step CYCLE walk with a back edge per domain, the out-of-vocabulary `InvalidStatusResult` pin (exact sorted `allowed_values` + message, file untouched), the no-op-before-check pin on each domain's most "final-feeling" state; `feat` handled with a per-seed unique `feat-0-<hex>` id since its folder-based create would otherwise collide on identical bodies), and `tests/general/tools/test__status_fsm.py` updated from the Phase-110 state pin (req landed + 13 `None`) to full coverage (every entry its domain's own landed constant by identity, no `None`, every whole-body domain enforced — an allowed transition passes, the diagonal is rejected). Fallout fixes (machine-legal walks, no assertion weakened, no subject changed): `tests/general/tools/test_set_status.py` `_CASES.valid_status` re-targeted `uc` "accepted" -> "proposed", `gol` "accepted" -> "proposed", `dec` "accepted" -> "proposed", `sop` "active" -> "approved"; `tests/general/tools/test_i18n_all_domains.py`'s `_set_status_target` replaced with the table-derived form `sorted(_STATUS_TRANSITIONS_BY_TYPE[spec.d][spec.status])[0]` (the now-unused `_allowed_statuses` helper removed); `tests/gol/tools/test_integration.py` and `tests/dec/tools/test_integration.py` gained the legal `proposed` step before their `accepted` step; `tests/sop/tools/test_integration.py` gained the legal `review` -> `approved` walk before its `active` step (the locked table does not allow `review` -> `active`, so one more step than the fallout list's literal wording — see Decisions Made); and `tests/dec/tools/test_i18n_write.py` — one fallout file beyond the verified list, the same dec `draft` -> `accepted` class in four asserting call sites plus one latent non-asserting call site — gained the legal `proposed` step at each. Gate evidence: `ruff format --check` (2412 files already formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (clean, exit 0), full suite `pytest -n auto --cov=src --cov-report= -q` (6131 passed, 18 skipped, 11203 subtests passed), `specmgr docs` regenerated (15 API pages + GENERATED.md; a second run is byte-identical).

#### 2026-11-04T19:18:35.000Z - Implemented Phase 110: the REQ pilot (table + end-to-end tests)

Implemented Phase 110 (Tasks 110.100/110.110). Task 110.100: `req`'s own `_STATUS_TRANSITIONS` in `req/models/v1/frontmatter.py` next to `_ALLOWED_STATUSES` -- the locked Design Notes table (draft -> [proposed, rejected], proposed -> [accepted, rejected, draft], accepted -> [implemented, superseded, deprecated, rejected], rejected -> [proposed, draft], implemented -> [superseded, deprecated], superseded/deprecated terminal) authored as a private list-of-lists `_STATUS_TRANSITIONS_RAW` and normalized to the public-to-module `dict[str, frozenset[str]]` the aggregation requires, with import-time asserts pinning full vocabulary coverage (`set(table) == _ALLOWED_STATUSES`) and in-vocabulary targets. Task 110.110: `general/tools/_status_fsm.py`'s `_STATUS_TRANSITIONS_BY_TYPE` `req` entry now carries the domain's own constant by identity (the other 13 whole-body entries stay `None` = passthrough; the Phase-100 subset-form drift assert is unchanged and now active for `req`; no `adr` entry); the module's Phase-100 "every entry None / byte-identical" wording is updated in `_status_fsm.py` and in `set_status.py`'s module docstring (the `@mcp.tool` description and `server.py` stay untouched for Phase 130; `_set_status_adr` is byte-identical, ACC-006). Tests: new `tests/general/tools/test_set_status_fsm_req.py` (the per-domain e2e home; temp `SPECMGR_DOCS_DIR` + real `create_req` seed + public `set_status`, every case asserting the on-disk file) -- allowed `draft` -> `proposed` (status on disk, `updated` bumped, body byte-identical); disallowed `accepted` -> `draft` (`InvalidStatusTransitionResult`, `allowed_values == ["deprecated", "implemented", "rejected", "superseded"]` pinned, exact normal-form message, file byte-identical); the multi-step cycle `draft` -> `proposed` -> `draft` -> `proposed` -> `accepted`; terminal `superseded` (empty `allowed_values`, exact terminal-form message, file untouched); the no-op on a terminal state (success, no write, no `updated` bump -- pinning no-op-before-transition-check order); out-of-vocabulary `"bogus"` on a `draft` and an `accepted` req (still the distinct pre-load `InvalidStatusResult` with the full flat vocabulary, file untouched); and the full 7x7 matrix walk (49 (current, target) pairs through the public tool, each classified no-op/allowed/rejected exactly as the landed table says, with the exact per-pair message form). The golden table pin (exact normalized equality + terminals + coverage + in-vocabulary targets + the 7x7 matrix) lives in `tests/req/models/v1/test_frontmatter.py`. The Phase-100 seam state changed accordingly: `test_set_status.py`'s req `_CASES.valid_status` re-targeted `"accepted"` -> `"proposed"` (a fresh req's `draft` -> `accepted` is now a rejected transition, so the positive/no-op/spy rows drive the allowed edge; the seam test methods and their wiring/no-op/order pins are otherwise unchanged), and `test__status_fsm.py`'s "every entry None" pin became the Phase-110 pair (`req` entry is the landed domain table by identity and equals the locked shape; every other entry still `None`) plus a no-patching landed-table enforcement test. Direct Phase-110 fallout repaired in two out-of-gate i18n modules whose ACC-006 rows picked a disallowed-from-`draft` target for `req` (alphabetical pick `accepted`): `test_i18n_all_domains.py` gained the shared `_set_status_target(spec)` helper (req -> `proposed`, every other domain unchanged) and `test_i18n_closed_vocabulary.py` uses it. Gate: `ruff format --check` (2411 files already formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (no output), `pytest -n auto tests/req tests/general/tools/test_set_status_fsm_req.py tests/general/tools/test__status_fsm.py tests/general/tools/test_set_status.py tests/general/models` (375 passed), plus the repaired i18n modules and the adjacent wiring/guard/error-context modules (428/428 and 37/37 passed in the combined runs); `specmgr docs` regenerated `docs/api/..._status_fsm.md`, `docs/api/...set_status.md` (the wording updates) and `docs/GENERATED.md` (test-file count 519 -> 520), all staged.

#### 2026-11-04T15:52:00.000Z - Implemented Phase 100: the cross-cutting status state-machine mechanism

Implemented Phase 100 (Tasks 100.100/100.110/100.120). Task 100.100: `InvalidStatusTransitionResult` (`general/models/invalid_status_transition_result.py`, a sibling of `InvalidStatusResult`, exported from `general/models/__init__.py`) with the locked `valid`/`type`/`from_status`/`to_status`/`allowed_values`/`message` shape and the two locked message forms (normal with the sorted `allowed_values` joined in field order, terminal with an empty list). Task 100.110: `general/tools/_status_fsm.py` — the `_STATUS_TRANSITIONS_BY_TYPE` aggregation (one entry per `WHOLE_BODY_DOMAINS` member, every value `None` in Phase 100, no `adr` entry), the Phase 100 subset-form import-time drift assert (keys ⊆ `WHOLE_BODY_DOMAINS`, `ADR` absent, every non-`None` table's current-status keys and target values checked against the domain's own `_ALLOWED_STATUSES` — vacuous today, active from Phase 110), the pure core `decide_transition(table, type_, current, target)`, and the public `check_status_transition(type_, current, target)` (module stays mcp-free like the other `_private.py` helpers). Task 100.120: the helper is wired into all 14 whole-body `_set_status_<d>` adapters in `set_status.py` immediately after the no-op comparison and before the raw-body re-read; each adapter's return annotation and the `_SetStatusFrontmatter` union alias (and the public `set_status` docstring Returns) carry the new member; the module docstring documents the two-error-surface design. The `@mcp.tool` description and `server.py` are untouched (Phase 130); `_set_status_adr` is byte-identical (ACC-006). Tests: `tests/general/models/test_invalid_status_transition_result.py` (model shape + both message forms), `tests/general/tools/test__status_fsm.py` (aggregation invariants, the pure core's passthrough/allowed/disallowed/terminal/not-a-key paths, the helper's lookup), and a new `TestSetStatusTransitionSeam` in `tests/general/tools/test_set_status.py` (spy-pinned wiring + passthrough for req/feat, the no-op-first and out-of-vocabulary-first order pins). Gate: `ruff format --check` (2408 files clean), `ruff check` (clean), `vulture --min-confidence 60` (clean; `whitelist.py` gained the two unique model field names `from_status`/`to_status`), targeted pytest (`tests/general/models` + `test__status_fsm.py` + `test_set_status.py` + `test__domains.py`: 216 passed), wider sweep `tests/general` + `tests/set` (1476 passed). `specmgr docs` regenerated (two new API pages, updated indexes).

#### 2026-11-04T14:08:46.000Z - Applied plan-refinement findings (G1, D1, I1)

Applied the three findings from a plan-refinement pass. G1: the two `### Dependencies` entries now carry `FEAT` reference tags, so the machine-readable reference surface coincides with the prose surface. D1: the drafting-era Updates/Decisions entry timestamps are aligned to the frontmatter `created` stamp (the entries cannot predate file creation). I1: Task 100.120 now states the REQ-003 passthrough seam explicitly (table-less domains pass through until Phases 110/120 land their respective tables).

#### 2026-11-04T13:21:56.524Z - Drafted feature plan from issue #108

Created the `feat-108-fsm` plan. Scope is the 14 whole-body domains with ADR excluded. Rollout is phased: a Phase 100 cross-cutting mechanism (the `InvalidStatusTransitionResult` model, the central aggregation linked to the `_domains` registry, and the post-load/pre-write check wired into the adapters), a Phase 110 REQ pilot, and a Phase 120 rollout of the remaining 13 domains. A disallowed transition returns a non-raising result whose `allowed_values` are the targets valid from the current state (distinct from the pre-existing pre-load out-of-vocabulary `InvalidStatusResult`, which keeps the full flat vocabulary). Per-domain tables are domain-owned next to each `_ALLOWED_STATUSES` and expressed as a cycling-friendly `status: [targets]` mapping.

### Decisions Made

#### 2026-11-05T10:26:32.000Z - Phase 130 implementation choices

Locked the Phase 130 documentation/ADR details: (a) the ADR id is server-assigned by `create_adr` (per the ADR 898bfcd0-85f9-462f-93a8-747bda4166c8 structured-tools mandate, the file was created and status-changed through the `create_adr`/`set_status` MCP tools, never hand-written): **a79608e4-88cd-498f-8ca1-445df4d04f92**, title "Per-domain status state machines for set_status: domain-owned tables, central aggregation, and the non-raising, current-state-relative transition result", file `docs/adr/a79608e4-88cd-498f-8ca1-445df4d04f92-per-domain-status-state-machines-for-set-status-domain-owned.md`, `status: accepted`, `date: 2026-11-05`, `decision-makers: OpenCode agent + user decision (plan locked during feat-108-fsm planning)` (the task-suggested variant of the recent "OpenCode agent + user decision" wording, since the plan was user-locked during feat-108-fsm planning). (b) The Considered Options take the task's four-option shape exactly: Option 1 per-domain duplicated `set_status`-side checks (rejected), Option 2 the chosen declarative domain-owned tables + central aggregation + single pure check, Option 3 raising `ValueError` (the earlier planning spike, rejected), Option 4 a shared FSM engine/library (rejected per the plan's Explicitly Out Of Scope) — with the Pros/Cons detail filled in from the locked design. (c) The ADR cites the locked per-domain tables by reference to this plan's Design Notes (per the task's "do NOT paste all 14 tables" instruction) and records the feat cycle-walk deviation only as a pointer to this plan's own Decisions Made entry (the ACC-003 example segment note). (d) In `AGENTS.md`, the case-6 clause was inserted into the chain paragraph AFTER the case-5 (f14f125e) clause and before the `_CAUGHT_EXCEPTIONS` definition clause — keeping the chain-extension numbering monotonic (4 → 2-reminder → 5 → 6) — rather than inline with the case-2 `set_status` sentence the task quoted as the anchor; the case-2 sentence itself is untouched, and the new clause re-states "the case-2 out-of-vocabulary `InvalidStatusResult` above still running pre-lock/pre-load first (unchanged)" to keep the two surfaces adjacent in prose. (e) The public `set_status` docstring's Returns section carried one stale sentence ("During the phased rollout a domain whose table has not landed yet passes through unchanged") that Phases 100–120 had left behind; it was replaced in place by the rollout-complete wording (the `@mcp.tool` `description=` — the task-identified missing piece — and `server.py` gained their new paragraphs; no other docstring prose was touched). (f) All three generators were run to idempotency (`specmgr mcp-docs`, `specmgr adr-toc`, `specmgr docs` — each second run byte-identical / no further changes), so `docs/MCP.md`, `docs/adr/README.md`, and the two `docs/api` pages reflect exactly this phase's docstring changes and nothing else.

#### 2026-11-05T04:35:53.000Z - Phase 120 implementation choices

Locked the Phase 120 implementation details: (a) the 13 tables ship byte-for-byte in the locked Design Notes shape as the two-constant form the `req` pilot established — a private `_STATUS_TRANSITIONS_RAW` (list literals) plus the normalized `_STATUS_TRANSITIONS: dict[str, frozenset[str]]` (dict comprehension) with the same two import-time asserts in each domain's own frontmatter module; the aggregation imports the normalized constants by identity, and its type annotation tightened to `dict[str, dict[str, frozenset[str]]]` (no `None` values) now that every entry is landed — the pure core `decide_transition` keeps its `None`-table passthrough (total decision, still exercised by tests and by unregistered types such as `adr`). (b) The e2e module is one file, `tests/general/tools/test_set_status_fsm_domains.py`, holding a frozen `_FsmDomainSpec` dataclass per domain (`create` callable, minimal body — reused verbatim from `test_set_status.py` where present, a new `_SET_MINIMAL_BODY` for `set` which has no `_CASES` entry there — create-start status, `_WALKS_FROM_START` reachability dict, the named cycle, one out-of-vocabulary value valid in another domain, the "final-feeling" no-op state) plus a `TestFsmDomainSpecs` integrity class that pins the spec data to the aggregation's own landed constants by identity and verifies every walk/cycle step is machine-legal; the matrix, cycle, out-of-vocabulary, and no-op behavioral classes then loop over the specs. `feat` is seeded through a `_create_feat_unique` wrapper (caller-chosen `feat-0-<hex>` id per seed) because `create_feat`'s default id derives from the body's H1 slug and identical bodies would collide. (c) **Deviation from the locked cycle walk, forced by the locked machine:** the task's locked feat cycle `planning -> progress -> review -> done -> progress -> done` ends in `progress` -> `done`, which the user-locked feat table does not allow (`progress`: [review, planning]) — the plan's own ACC-003 example segment (`review` -> `done` -> `progress` -> `done`) carries the same illegal step. Since the tables are locked ("do not adjust — user-approved defaults") and the tests must walk legal paths, the feat cycle takes the minimal legal back-edge to `done` through `review` instead: `planning -> progress -> review -> done -> review -> done` (one step changed, all walk positions and the ACC-003 "revisit done" property preserved; annotated in the spec itself). (d) **The sop integration fix needed two inserted steps, not one:** the fallout list's literal wording ("insert `review` ... before it") is impossible as written because the locked sop table does not allow `review` -> `active`; the legal lifecycle walk inserted is `draft` -> `review` -> `approved` -> `active` (the `review` step named by the list plus the `approved` step the machine requires), keeping the existing `active` step and every downstream assertion. (e) **One fallout file beyond the verified list:** `tests/dec/tools/test_i18n_write.py` — the same dec `draft` -> `accepted` class the list covers in the two i18n modules, in five call sites (four asserting, one latent non-asserting); each gained the legal `proposed` step with all assertions and subjects unchanged (reported to the orchestrator for verification). (f) The `_set_status_target` helper in `test_i18n_all_domains.py` now derives the ACC-006 write-row target from the landed machine — `sorted(_STATUS_TRANSITIONS_BY_TYPE[spec.d][spec.status])[0]`, the alphabetically-first LEGAL transition from the variant's create status (yielding `proposed` for req/uc/gol/dec, `active` for tsk/qa/prb, `accepted` for rsk, `approved` for sop/sysrs, `progress` for vcr/txt/set — byte-identical to the old derivation for every domain except the ones the machines now steer); the old full-vocabulary derivation and its `req`-only override (and the now-unused `_allowed_statuses` helper) are removed.

#### 2026-11-04T19:18:35.000Z - Phase 110 implementation choices

Locked the Phase 110 implementation details: (a) the `req` table ships as the two-constant shape the orchestrator's locked design anticipated -- a private `_STATUS_TRANSITIONS_RAW` (list literals, the REQ-007 authorable form, exactly the locked table) plus the normalized public-to-module `_STATUS_TRANSITIONS: dict[str, frozenset[str]]` (a dict comprehension, so the source stays list-authored) -- with two import-time asserts in `req/models/v1/frontmatter.py` itself (`set(_STATUS_TRANSITIONS) == _ALLOWED_STATUSES`, every target in-vocabulary) mirroring the aggregation's per-entry check at the domain's own boundary; the aggregation imports the normalized constant (identity, no copy). (b) The e2e module is `tests/general/tools/test_set_status_fsm_req.py` (the orchestrator-named home for the per-domain e2e rows; Phase 120 will add sibling `test_set_status_fsm_<d>.py` modules). (c) Phase-100 test state pins that the locked table invalidates were updated in place rather than left red: `test_set_status.py`'s req `_CASES.valid_status` moved `"accepted"` -> `"proposed"` (a fresh req is `draft`, and `draft` -> `accepted` is now a rejected transition; the seam methods' own wiring/no-op/order pins needed no code change and kept their names), and `test__status_fsm.py`'s "every entry is the None passthrough" test became the Phase-110 pair (req entry is the landed table by identity + locked-shape equality; every other entry still None) with the passthrough loop skipping `req`. (d) Two out-of-gate i18n test modules (feat-197's `test_i18n_all_domains.py` ACC-006 row and `test_i18n_closed_vocabulary.py`'s canonical-status row) picked req's target as the alphabetical first in-vocabulary status other than the create status (`accepted` -- now a disallowed transition from `draft`); they share a new `_set_status_target(spec)` helper in `test_i18n_all_domains.py` (req -> the allowed `proposed`; every other domain byte-identical to the old derivation) instead of special-casing the target inline in both files.

#### 2026-11-04T15:52:00.000Z - Phase 100 implementation choices

Locked the Phase 100 implementation details: (a) `InvalidStatusTransitionResult.allowed_values` is **sorted** (the plan's field spec), and the message joins that sorted field in field order — the plan's Design Notes example lists the values in table order, but the sorted field spec wins, keeping the structured result self-consistent under client-side truncation (the ADR 519d1206 rationale). (b) A `current` status that is not a key of the domain's table is treated as a **terminal state** (empty `allowed_values`, terminal message form) — the decision stays total and deterministic, although this is structurally unreachable once a domain's table pins full vocabulary coverage. (c) The helper module is `general/tools/_status_fsm.py` — the plan's suggested "e.g." name, used as-is. (d) The decision is factored into the pure core `decide_transition(table, type_, current, target)` (the plan's `decide`, renamed for descriptiveness) so the public `check_status_transition` only indexes the aggregation; tests exercise the core with temporary tables without mutating module state (plus one `mock.patch.dict` test for the lookup itself). Bookkeeping: the frontmatter `status` moved `planning` -> `progress` with implementation started.

#### 2026-11-04T13:21:56.524Z - Locked scope, channel, and mechanics during planning

Excluded ADR (consistent with i18n/feat-170). Chose domain-owned tables plus a central aggregation linked to `general/tools/_domains`. Chose a cycling-friendly `status: [targets]` representation so a document can move `review` -> `done` and back. Fixed the failure channel upfront as a non-raising `InvalidStatusTransitionResult` (the current-state-relative `allowed_values` payload makes the structured result the truncation-surviving form, per the ADR 519d1206 chain) and dropped the earlier `ValueError` spike. Kept the pre-load out-of-vocabulary `InvalidStatusResult` distinct and unchanged. Chose phased rollout starting with REQ.

### Related PRs / Commits

- PR: https://github.com/dfch/biz.dfch.SpecMgr/pull/256 (open, base `dev`, CI green — all 8 checks pass on `4a360327`)
- 0a745cb Phase 100 — cross-cutting status state-machine mechanism (issue #108)
- c5fa928 Phase 110 — REQ pilot: req status state machine + end-to-end enforcement tests (issue #108)
- 2d22059 Phase 120 — remaining 13 domain state machines, full-coverage assert, golden + e2e matrix tests (issue #108)
- 3e11707 Phase 130 — set_status tool/server/AGENTS.md docs sync + ADR a79608e4 (issue #108)
- 930851c Phase 140 — quality gate green, acceptance criteria walked (issue #108)
- a6e5082 set status to review — implementation complete, ACC-001…ACC-009 ticked (issue #108)
- 4a360327 review D1 — stale Phase-110 rollout wording in the set_status seam tests (issue #108)

### More Information

- GitHub issue: https://github.com/dfch/biz.dfch.SpecMgr/issues/108
- Related prior features: feat-103-set-status-error (the `InvalidStatusResult` precedent), feat-104-109-set-status-noop-dec-docs (the no-op behavior to preserve).
