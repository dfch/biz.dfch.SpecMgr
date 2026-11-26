---
status: accepted
date: '2026-11-05'
decision-makers: OpenCode agent + user decision (plan locked during feat-108-fsm planning)
id: a79608e4-88cd-498f-8ca1-445df4d04f92
version: 1.0.0
---

# Per-domain status state machines for set_status: domain-owned tables, central aggregation, and the non-raising, current-state-relative transition result

## Context and Problem Statement

GitHub issue #108 (https://github.com/dfch/biz.dfch.SpecMgr/issues/108) reports that the generic `set_status` tool writes any in-vocabulary status regardless of the document's current status: it validates the requested `status` only against the dispatched domain's flat closed vocabulary (the pre-dispatch/pre-load `InvalidStatusResult` check, ADR b399f1ce-ed42-4929-b01c-7a57d18e8014 -- case 2 of the ADR 519d1206-4d2a-4500-9046-6db635209996 non-raising, structured-result workaround chain) and then persists it. Every domain's `status` field carries implicit lifecycle semantics the tool ignores: `req` moves `draft` -> `proposed` -> `accepted` -> `implemented` (with `superseded`/`deprecated` terminal), `rsk` moves `open` -> `mitigating` -> `closed`, and so on -- yet `accepted -> draft` is possible on any whole-body domain today, as is any other in-vocabulary jump. The fix must decide (a) where each domain's transition machine lives, (b) where the enforcement runs and how, (c) what a disallowed transition returns, and (d) how the ADR artifact type is treated.

This is case 6 of the ADR 519d1206-4d2a-4500-9046-6db635209996 workaround chain (client-side `isError: true` result truncation, confirmed on OpenCode 1.18.27): case 1 redesigned the generic `validate` tool to a non-raising `{valid, errors}` result; case 2 (ADR b399f1ce-ed42-4929-b01c-7a57d18e8014) extended that rationale narrowly to `set_status`'s invalid-status case, via `InvalidStatusResult`; case 3 (ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c) extended it to `get_<d>`'s parse-failure case, via `ParseFailureResult`; case 4 (ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f) extended it to the four generic mutation tools' failure cases, via `ParseFailureResult`/`ValidateResult`; case 5 (ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e) extended it to the `create_<d>`/`parse_<d>` content-validation cases. A disallowed `set_status` transition's actionable detail -- the target statuses allowed from the document's current state -- is exactly the payload the chain's rationale shows the raise-based channel destroys, so this case follows the same pattern: a non-raising structured result, not a raised exception.

One chain-bookkeeping record this ADR must settle: case 5 (f14f125e) explicitly recorded -- in its Decision Outcome, a Consequences bullet, and Option 4's own Cons -- that the generic `delete` tool "remains unchanged" and "becomes a later candidate (case 6) if ever addressed". This ADR takes the case-6 slot for the `set_status` disallowed-transition surface; `delete`'s raise-based contract remains unchanged by this ADR and stays the chain's later candidate if ever addressed. No accepted ADR is edited or superseded: 519d1206, b399f1ce, 9080b37c, b8c9bfea, and f14f125e remain byte-identical, refined by reference only, per the chain's established precedent.

This ADR records the concrete design FEAT feat-108-fsm implements from: domain-owned per-domain state-machine tables plus one central aggregation, a single pure cross-cutting check wired through the existing `set_status` dispatch post-load/pre-write, the non-raising, current-state-relative `InvalidStatusTransitionResult` as `set_status`'s second error surface (distinct from the unchanged case-2 `InvalidStatusResult`), and the ADR artifact-type exclusion.

## Decision Drivers

- The machine must be domain-owned: each domain's lifecycle semantics (which transitions over its own closed vocabulary are legal) live next to the domain's own `_ALLOWED_STATUSES` in its `models/<v>/frontmatter.py` -- the module that already owns the vocabulary, in the domain-first layout (ADR ece4554b-725c-4f76-bc04-5d2b760363d2) -- while the enforcement stays one cross-cutting check in `general/tools/` wired through the existing generic-tool dispatch (ADR 36905d5b-8057-4294-8665-c7eed5534db0): no per-domain `set_status`-side logic.
- The central aggregation must be keyed to the shared `general/tools/_domains` registry (ADR c4efbde6-fd19-4aa8-8668-95316ed62dcc) with an import-time drift assert, so a new domain's onboarding (the reserved `ac` domain) fails loudly rather than silently skipping the machine.
- The rejection must be a non-raising structured result whose current-state-relative detail (the targets allowed from the document's current status -- never the full flat vocabulary) survives MCP clients that truncate `isError` text (the ADR 519d1206 rationale; the feature's earlier planning spike of raising `ValueError` is rejected for exactly this reason).
- The pre-write guarantee: a disallowed transition persists nothing, bumps `updated` not, and warms no cache -- the same observable contract as the unchanged-status no-op (GitHub issue #109).
- The existing channel order must stay undisturbed (feat-108-fsm REQ-005): the path-safety `ValueError`s (before any filesystem access), the ADR-only `superseded_by` guard, the language guard, the pre-dispatch/pre-load out-of-vocabulary `InvalidStatusResult` (case 2 -- still first), the unchanged-status no-op, the existing-but-broken `ParseFailureResult` (case 4), and the domain not-found raises all keep their current order and semantics.
- Phased-rollout feasibility: a 14-domain behavior change must land incrementally (the reusable cross-cutting mechanism, then a `req` pilot, then the remaining whole-body domains) -- the aggregation needs an opt-in per-domain seam (`None` entry = passthrough until the domain's table lands), tightening to full coverage only after the final rollout phase.
- Cycles must be representable (a document may move `review` -> `done` and back): the table is a current-status -> target-set mapping, not a linear stage list.
- The ADR artifact type is excluded, consistent with its permanent single-language treatment (feat-197-i18n, ADR 38efdb66-8025-45c5-bbe8-45b25fc7a772) and its flat-vocabulary, no-generic-mutation-surface treatment (feat-170, ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f).
- No migration of existing on-disk documents: the machine governs future `set_status` calls only.

## Considered Options

- Option 1: Per-domain `set_status`-side checks -- each `_set_status_<d>` adapter carries its own transition table and lookup logic.
- Option 2 (chosen): One cross-cutting, declarative design -- domain-owned `_STATUS_TRANSITIONS` tables (the `status: [targets]` authorable form, normalized to `dict[str, frozenset[str]]`, cycling-friendly, an empty target set marking a terminal state) next to each domain's own `_ALLOWED_STATUSES`; a central `_STATUS_TRANSITIONS_BY_TYPE` aggregation in `general/tools/_status_fsm.py` keyed to the `general/tools/_domains` registry (import-time drift assert, `None`-entry passthrough seam for phased rollout); and a single pure check wired into every whole-body adapter post-load/pre-write through the existing dispatch.
- Option 3: Raise `ValueError` on a disallowed transition, carrying the current-state-relative detail in the exception message (the feature's earlier planning spike).
- Option 4: A shared FSM engine/library that the domains instantiate.

## Decision Outcome

Option 2: each of the 14 whole-body domains owns a `_STATUS_TRANSITIONS` state machine -- a mapping from current status to the allowed target statuses, authored as `status: [targets]` (REQ-007) and normalized to `dict[str, frozenset[str]]` (an empty target set marks a terminal state; cycles are representable) -- next to its own `_ALLOWED_STATUSES` in its `models/<v>/frontmatter.py`, with import-time asserts at the domain's own boundary pinning full vocabulary coverage (the table's keys equal the domain's closed vocabulary) and in-vocabulary targets. `general/tools/_status_fsm.py` aggregates the 14 domains' own landed tables by identity into `_STATUS_TRANSITIONS_BY_TYPE`, keyed to the shared `general/tools/_domains` registry: the import-time drift assert (in its full-coverage form after the final rollout phase) checks that the aggregation's keys equal `WHOLE_BODY_DOMAINS`, that no entry is `None`, that ADR has no entry, and that every table names only statuses from its domain's own closed vocabulary. The single pure check -- `decide_transition(table, type_, current, target)` (the total, deterministic core; a `None` table passes through) plus the public `check_status_transition(type_, current, target)` (which only indexes the aggregation) -- is called by every whole-body `_set_status_<d>` adapter inside the domain lock, immediately after the unchanged-status no-op comparison and before the raw-body re-read and `write_<d>_file`, so a rejection is pre-write: nothing is persisted, `updated` is not bumped, and no cache is warmed. The rollout landed in phases and is complete (Phase 100 the mechanism, Phase 110 the `req` pilot, Phase 120 the remaining 13 whole-body domains): every whole-body domain's own table is enforced.

The concrete design, as implemented in FEAT feat-108-fsm:

1. The two distinct error surfaces. (A) The pre-existing pre-dispatch/pre-load out-of-vocabulary check is unchanged and still runs first: an out-of-vocabulary `status` returns the non-raising `InvalidStatusResult` (the domain's full flat vocabulary, sorted -- no current state is known before the document is loaded) -- case 2 of the 519d1206 chain (ADR b399f1ce-ed42-4929-b01c-7a57d18e8014). (B) The new post-load transition check returns the non-raising `InvalidStatusTransitionResult` -- a sibling of, not a reuse or subclass of, `InvalidStatusResult` (`general/models/invalid_status_transition_result.py`) -- with fields `valid` (always `False`; there is no successful variant), `type` (echoed back), `from_status` (the document's current on-disk status, loaded by the adapter), `to_status` (the requested target), `allowed_values` (the targets the domain's machine allows from `from_status`, sorted -- never the domain's full flat vocabulary; an empty list marks a terminal current state), and `message` -- normal form: `"Invalid status transition '{from_status}' -> '{to_status}' for type '{type}'. Allowed from '{from_status}': {allowed_values}"` (the sorted values comma-and-space-joined in field order); terminal form (`allowed_values` empty): `"... Status '{from_status}' is terminal (no outgoing transitions)."`. This is case 6 of the 519d1206 chain: the current-state-relative detail is the payload a raised exception would lose to client-side `isError` truncation.

2. The per-domain tables. The locked tables for the 14 whole-body domains (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`/`txt`/`set` -- cycling-friendly defaults, with `superseded`/`deprecated` terminals in `req`/`gol`/`uc`/`dec` only) are recorded in the feature plan's Design Notes (`.specmgr/feat/feat-108-fsm/README.md`), which this ADR cites by reference rather than restating. Each table is pinned by a per-domain golden test (exact normalized equality, the terminal/no-terminal pin, key coverage, in-vocabulary targets, the full N-by-N pair matrix), and the enforcement is pinned end-to-end per domain through the public `set_status` (the full N-by-N matrix walk with on-disk assertions, the named multi-step cycle walk with a back edge, a disallowed transition returning the case-6 result with the file byte-identical, the no-op succeeding before the check, and the out-of-vocabulary case returning `InvalidStatusResult` first).

3. The ADR exclusion (REQ-006). `type="adr"` has no aggregation entry, and `_set_status_adr` never calls the check: the ADR artifact type keeps its flat-vocabulary behavior byte-identical (including its own `"superseded by X"` composition and its no-op semantics), consistent with its permanent single-language treatment (feat-197-i18n, ADR 38efdb66-8025-45c5-bbe8-45b25fc7a772) and its exclusion from the case-4 generic-mutation surface (feat-170, ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f). The pure core's `None`-table passthrough is the total-decision seam that covers it (and unregistered types in general) without special-casing the check itself.

4. The unchanged channel order (REQ-005/ACC-004/ACC-005). Path-safety `ValueError`s (before any filesystem access), the ADR-only `superseded_by` guard, the language guard, the pre-dispatch/pre-load out-of-vocabulary `InvalidStatusResult` (case 2, first), the domain lock and load (the existing-but-broken `ParseFailureResult`, case 4), the unchanged-status no-op (issue #109), and then -- only for a loaded, status-changing whole-body call -- the post-load transition check. A disallowed transition returns the case-6 result before the write, the `updated` bump, and the cache warming ever run; a truly-absent id still raises the domain's not-found error.

5. No migration. Existing on-disk documents are not touched: the machine governs future `set_status` calls only, so a document sitting in a status with no outgoing table edge is stuck only for `set_status` (every read surface, and `create_<d>`/`update`/`edit`/`set_classification`/`delete`, are unaffected). `status` is a closed-vocabulary frontmatter value, never translated (feat-197-i18n, ADR 38efdb66-8025-45c5-bbe8-45b25fc7a772), so the machine is language-invariant: a non-default-language variant is checked against its own current status exactly as the EN document is.

6. Chain bookkeeping (case 6). ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e's record that the generic `delete` tool "becomes a later candidate (case 6) if ever addressed" is overtaken: this ADR takes the case-6 slot for the `set_status` disallowed-transition surface; `delete`'s raise-based contract remains unchanged by this ADR and stays the chain's later candidate. No accepted ADR is edited or superseded -- 519d1206, b399f1ce, 9080b37c-82b3-4f63-81f1-79641d0bf14c, b8c9bfea, and f14f125e remain byte-identical, refined by reference only, per the chain's established precedent.

### Consequences

- Good: the 14-domain lifecycle defect (issue #108's `accepted -> draft`) is closed with one cross-cutting check and no per-adapter logic: the lifecycle semantics live next to the vocabulary that already constrains them (domain-first, ADR ece4554b-725c-4f76-bc04-5d2b760363d2), and the aggregation's import-time assert makes a new domain's onboarding (the reserved `ac` domain) fail loudly if it skips the machine.
- Good: the rejection's current-state-relative detail (the allowed targets from the document's current status, or the terminal message form) survives MCP clients that truncate `isError` text -- case 6 of the 519d1206 chain, the same rationale the chain has already proven five times.
- Good: the pre-write guarantee and the unchanged channel order -- nothing is persisted on a rejection, `updated` is not bumped, and the no-op, out-of-vocabulary, `ParseFailureResult`, and path-safety contracts keep their current order and semantics (ACC-004/ACC-005/ACC-006).
- Good: cycles are first-class (a document may move `review` -> `done` and back, per the locked tables), and the `None`-entry passthrough seam let the 14-domain behavior change land incrementally (mechanism, `req` pilot, remaining domains), with the aggregation's assert tightening to full coverage only after the final phase (ACC-007).
- Bad: this is the sixth documented asymmetric tool contract in this repo (519d1206's `validate`, b399f1ce's `set_status` invalid-status, 9080b37c's `get_<d>`, b8c9bfea's four generic mutation tools, f14f125e's `create_<d>`/`parse_<d>`, now `set_status`'s disallowed-transition case) -- a future contributor must know the chain.
- Bad: the `set_status()` return union widens for every whole-body domain (each adapter now carries `InvalidStatusTransitionResult` alongside `ParseFailureResult`) -- a caller must check for the new failure shape on every non-exception return.
- Bad: a document sitting in a status with no outgoing table edge is stuck for `set_status` until the table changes (reads and every other tool are unaffected) -- accepted, since the machine governs transitions, not the on-disk state (no migration).
- Bad (tracked, not blocking): as with the chain's other members, a live MCP-client/OpenCode-session round-trip is not something an agent session can reliably automate; verification is limited to unit-level assertions of the structured result's shape and content (the golden matrices, the e2e walks, the message-form pins, the file-untouched assertions).

### Confirmation

Confirmed by FEAT feat-108-fsm's Phases 100/110/120 on the feat-108-fsm branch (full test suite green at Phase 120: 6131 passed, 18 skipped): (a) each of the 14 whole-body domains' `_STATUS_TRANSITIONS` table is pinned by its own per-domain golden matrix test (exact normalized equality, the terminal/no-terminal pin, key coverage equal to the domain's own `_ALLOWED_STATUSES`, in-vocabulary targets, the full N-by-N pair matrix); (b) the enforcement is pinned end-to-end per domain through the public `set_status` -- a disallowed transition (e.g. `req`'s `accepted` -> `draft`) returns `InvalidStatusTransitionResult` with the current-state-relative sorted `allowed_values` and the exact normal-form message while the on-disk file stays byte-identical, a terminal current state returns the empty `allowed_values` plus the terminal-form message, the named multi-step cycle walk succeeds while every step is in the domain's table, the no-op still succeeds with no write before the check runs, and the out-of-vocabulary case still returns `InvalidStatusResult` first; (c) the aggregation's full-coverage import-time assert pins keys equal to `WHOLE_BODY_DOMAINS`, no `None` entry, and ADR's absence (ACC-007); (d) `_set_status_adr` is byte-identical to pre-feature behavior (ACC-006). The per-domain tables are the feature plan's user-approved defaults. As with the chain's other members, no live MCP-client/OpenCode-session round-trip is attempted or recorded as an outstanding commitment, for the same automation-limitation reasons they document.

## Pros and Cons of the Options

### Option 1: Per-domain set_status-side checks

#### Pros

- No new cross-cutting module: each adapter is self-contained, and a domain can evolve its machine without touching shared code.

#### Cons

- 14 copies of the same lookup/message logic across 14 adapters in `general/tools/set_status.py` -- drift-prone (a message-form, ordering, or result-shape change touches every copy), and no single place to key the machine to the `general/tools/_domains` registry or to assert full coverage.
- Puts lifecycle semantics in the tool wrapper (or scattered per-domain tool modules) rather than next to the vocabulary that already constrains them -- the domain-first layout (ADR ece4554b-725c-4f76-bc04-5d2b760363d2) says the schema-level facts belong in the domain's own models.

### Option 2: Domain-owned tables, central aggregation, one pure check (chosen)

#### Pros

- One source of truth per concern: the lifecycle semantics live in each domain's own frontmatter module (next to `_ALLOWED_STATUSES`), the enforcement is one pure check in `general/tools/_status_fsm.py`, and the aggregation is keyed to the shared `_domains` registry with an import-time drift assert (a new domain -- the reserved `ac` -- cannot onboard without its table).
- Cycles and terminal states are first-class (a `status: [targets]` mapping with set semantics), and the `None`-entry passthrough seam made the 14-domain behavior change land incrementally (mechanism, `req` pilot, remaining domains) with the assert tightening to full coverage only after the final phase.
- The non-raising, current-state-relative `InvalidStatusTransitionResult` delivers the allowed-targets detail host-independently (case 6 of the 519d1206 chain); the pre-write guarantee holds (nothing persisted, `updated` not bumped); and the existing channel order (no-op, out-of-vocabulary, `ParseFailureResult`, path-safety) is undisturbed.
- The ADR exclusion falls out structurally (no aggregation entry, the pure core's `None` passthrough) rather than by special-casing inside the check.

#### Cons

- The `set_status()` return union widens for every whole-body domain, and this is the sixth documented asymmetric tool contract a future contributor must know.
- Rollout touches two modules per domain (the frontmatter table plus the aggregation import) -- the drift assert catches a miss, but the onboarding cost is real.
- No migration: a document stuck in a status with no outgoing edge is stuck for `set_status` until the table changes (accepted -- the machine governs transitions, not on-disk state).

### Option 3: Raise ValueError on a disallowed transition

#### Pros

- No new result model and no union widening; matches the raise-based convention of `set_status`'s every other failure mode (unknown id, path-injection, `superseded_by` misuse).

#### Cons

- The current-state-relative allowed-targets detail is exactly the payload the 519d1206 chain's rationale shows client-side `isError` truncation destroys (the chain has reproduced the dead-end on OpenCode 1.18.27) -- a raised message cannot carry it host-independently.
- Contradicts the repo's own precedent for this same tool's second failure surface: case 2 (ADR b399f1ce-ed42-4929-b01c-7a57d18e8014) already chose the non-raising structured result for `set_status`'s invalid-status case for the same reason.
- This was the feature's earlier planning spike; it is recorded here as rejected, not deferred.

### Option 4: A shared FSM engine/library

#### Pros

- A general-purpose implementation (states, transitions, guards, rendering) could serve future state machines in the repo, and would centralize the cycle/terminal semantics in one tested component.

#### Cons

- Explicitly out of scope for issue #108 (the feature plan's Explicitly Out Of Scope names "a general-purpose FSM engine or shared library" -- the need is a declarative per-domain table plus one cross-cutting check).
- A new dependency/library surface for a single consumer, with no second use case to justify it -- disproportionate machinery for a membership check.

## More Information

- GitHub issue #108: https://github.com/dfch/biz.dfch.SpecMgr/issues/108.
- Feature plan and progress: `.specmgr/feat/feat-108-fsm/README.md` (the locked per-domain tables in its Design Notes; the two-error-surface design; the phased rollout, Phases 100/110/120; and the ACC-003 feat cycle-walk deviation recorded in its Decisions Made).
- ADR 519d1206-4d2a-4500-9046-6db635209996 ("Design validate as a non-raising, structured-result tool to work around client-side MCP error-content truncation"): case 1 of the chain this ADR extends; its client-side `isError`-truncation rationale is the driver for the case-6 non-raising result.
- ADR b399f1ce-ed42-4929-b01c-7a57d18e8014 ("Extend the non-raising structured-result workaround to set_status's invalid-status case"): case 2; the unchanged first error surface this ADR's second surface is distinct from, and the precedent for a `set_status`-specific non-raising result model.
- ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c ("Extend the non-raising structured-result workaround to get_<d>'s parse-failure case"): case 3; the `ParseFailureResult` channel this ADR leaves unchanged (a broken document is reported at load, before the transition check ever runs).
- ADR c4efbde6-fd19-4aa8-8668-95316ed62dcc ("Single source of truth for the document-type domain-name set"): the `general/tools/_domains` registry the aggregation is keyed to.
- ADR 38efdb66-8025-45c5-bbe8-45b25fc7a772 ("Multi-language artifact variants: directory layout, heading-mapping table, and language vocabulary"): status is a closed vocabulary, never translated (the machine is language-invariant); the ADR's permanent single-language treatment this ADR's exclusion mirrors.
- ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e ("Extend the non-raising structured-result workaround to the create_<d>/parse_<d> content-validation cases"): case 5; its "delete as the later candidate (case 6)" prediction is overtaken by this ADR (the case-6 slot goes to the `set_status` transition surface; `delete` remains the later candidate); f14f125e is not edited.
- ADR 898bfcd0-85f9-462f-93a8-747bda4166c8 ("Author and edit ADRs only through MCP structured tools, never raw markdown"): the authoring mandate this ADR itself follows -- created and status-changed only through the specmgr MCP `create_adr`/`set_status` structured tools, never hand-written or hand-edited.
