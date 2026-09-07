---
status: accepted
date: '2026-09-07'
decision-makers: OpenCode agent + user decision
id: b399f1ce-ed42-4929-b01c-7a57d18e8014
version: 1.0.0
---

# Extend the non-raising structured-result workaround to set_status's invalid-status case

## Context and Problem Statement

GitHub issue #103 reports that the generic `set_status` tool's error for an invalid `status` value is uninformative. feat-103-set-status-error's investigation found the underlying `pydantic.ValidationError` message is already complete and actionable (feat-27-validation already enriches it with the domain's full sorted allowed-values list) -- the real defect is the same OpenCode 1.18.27 client-side truncation of `isError: true` MCP tool results already diagnosed by ADR 519d1206-4d2a-4500-9046-6db635209996, which redesigned only the generic `validate` tool to a non-raising `{valid, errors}` contract and explicitly left every other tool, including `set_status`, raise-based. `set_status`'s single most common, most easily triggered failure mode -- an out-of-vocabulary `status` value for a given `type` -- reproduces exactly the same "opaque failure" symptom 519d1206 fixed for `validate`: the actionable message never reaches the calling agent through an affected client. This ADR decides whether and how to extend 519d1206's rationale to this one additional case, and records the concrete design (vocabulary lookup + result shape + check placement) feat-103's Phase 2 implements from.

## Decision Drivers

- Preserve feat-27-validation's actionable allowed-values detail all the way to the calling agent for set_status's single most common failure mode, regardless of which MCP client is in use (same driver as 519d1206).
- Keep the fix narrowly scoped to the invalid-status case only: every other set_status failure mode (unknown id, path-injection/invalid id shape, superseded_by misuse on a non-adr type) is comparatively rare in practice and stays raise-based, per feat-103 REQ-002 -- an agent that already has a valid id/type (e.g. from list_<d>/get_<d>) is far more likely to guess an out-of-vocabulary status than to mis-shape an id.
- Do not duplicate any domain's existing closed status vocabulary (`_ALLOWED_STATUSES`/`_FIXED_STATUSES`) -- reuse each domain's single source of truth directly.
- Do not overstate this as a general redesign of set_status's contract, mirroring 519d1206's own caution against treating a targeted workaround as an unconditional best practice.
- Prefer failing fast (no domain lock, no file I/O) for a purely input-shaped failure, consistent with the existing `validate_id`/`superseded_by` guards already in `set_status()`.

## Considered Options

- Option 1: Do nothing -- leave set_status's invalid-status case raise-based, relying on feat-27-validation's already-actionable exception message.
- Option 2: File and wait for an upstream OpenCode fix to the client-side isError truncation, keeping set_status raise-based in the meantime.
- Option 3: Redesign set_status's entire contract to non-raising for every failure mode (unknown id, path-injection, superseded_by misuse, invalid status alike).
- Option 4 (chosen): Narrowly extend 519d1206's non-raising, structured-result approach to set_status's invalid-status case only, leaving every other set_status failure mode raise-based.

## Decision Outcome

Option 4: `set_status()` pre-checks `status` against the dispatched domain's own closed vocabulary before taking any domain lock or touching the filesystem, and returns a new, purpose-built, non-raising `InvalidStatusResult` instead of letting `pydantic.ValidationError` propagate when `status` is out of vocabulary. Every other set_status failure mode (unknown id, path-injection/invalid id shape, superseded_by misuse on a non-adr type) continues to raise exactly as before -- this is a narrow, additive extension of 519d1206's rationale to one additional case, not a general redesign of set_status's contract (Option 3, rejected as disproportionate to REQ-002's narrow scope).

The concrete design, to be implemented in feat-103 Phase 2:

1. Vocabulary lookup (Task 1.2): a private, module-scope mapping in `general/tools/set_status.py`, e.g. `_ALLOWED_STATUSES_BY_TYPE: dict[str, frozenset[str]]`, built by importing each of the 12 whole-body domains' existing `_ALLOWED_STATUSES` constant plus ADR's `_FIXED_STATUSES`, directly from each domain's `models/v{N}/frontmatter.py` submodule (not the domain's package `__init__.py`, which does not re-export these private constants) -- e.g. `from ...req.models.v1.frontmatter import _ALLOWED_STATUSES as _REQ_ALLOWED_STATUSES`. This matches this same file's existing convention of importing other domains' private helpers directly (`_io`/`_lock`/`_paths`/`_write`); no new public accessor is introduced on any domain's frontmatter module. ADR's `_SUPERSEDED_PATTERN` regex is imported alongside `_FIXED_STATUSES` and checked specially: for `type="adr"`, `status` is valid if it is in `_FIXED_STATUSES` OR matches `_SUPERSEDED_PATTERN` (mirroring `AdrFrontmatter._validate_status`'s own check).

2. Result shape and message wording (Task 1.3): a new, greenfield Pydantic model `InvalidStatusResult`, in a new module `general/models/invalid_status_result.py` (mirroring `ValidateResult`'s precedent in `general/models/validate_result.py`), with fields `valid: bool` (always `False` on this model -- there is no successful variant of it), `type: str` (the requested domain type, echoed back), `status: str` (the rejected value, echoed back), `allowed_values: list[str]` (the domain's allowed values, sorted; for `type="adr"` the sorted 6-value fixed set plus one literal trailing descriptive entry `"superseded by <target-id>"`, documenting the pattern rather than trying to enumerate its infinite matches), and `message: str` -- the exact wording `"Invalid status '{status}' for type '{type}'. Allowed values: {allowed_values}"`, where `{allowed_values}` is `allowed_values` comma-and-space-joined (`", ".join(...)`) in the same order as the `allowed_values` field. `set_status()`'s return type annotation becomes `_SetStatusFrontmatter | InvalidStatusResult` -- a new top-level union added alongside the existing 13-way per-domain union, not folded into `_SetStatusFrontmatter` itself, so that name keeps meaning "the successful per-domain result" unambiguously.

3. Check placement and ordering: the pre-check runs inside the public `set_status()` function, after the existing `validate_id`/`superseded_by` guards but before dispatching to any `_set_status_<d>` adapter -- so an invalid `status` is rejected before any domain lock is taken or any file is read, the same fail-fast spirit as those two existing guards. This is a deliberate, minor behavior refinement: previously, if both `id` were unknown and `status` were out of vocabulary, the domain's own not-found error would win (status validation happened only after `load_by_id` succeeded, deep inside the adapter); after this change, the invalid-status pre-check runs first, since it depends only on the two input parameters (`type`, `status`), not on any successful id resolution. No existing test exercises both conditions simultaneously (`test_out_of_vocabulary_status_raises_validation_error_file_untouched` always seeds a valid, existing id; `test_unknown_id_raises_domain_not_found` always uses a valid status), so this refinement changes no currently-asserted behavior. One further refinement, confirmed with the user during Phase 2 implementation: when `type="adr"` and `superseded_by` is given, the pre-check does not validate `status` at all, regardless of its content -- `models.adr.v1.mutations.set_status` itself ignores the raw `status` argument in that case and composes `f"superseded by {superseded_by}"` instead, so validating the discarded `status` value would incorrectly reject an otherwise-valid call.

4. Every other set_status failure mode stays raise-based, unchanged: unknown id (`ReqNotFoundError`/.../`AdrNotFoundError`, raised from inside each adapter's `load_by_id`), path-injection or wrong-shaped `id` (`ValueError` from `_path_safety.validate_id`, already checked before this new pre-check), and `superseded_by` misuse on a non-adr `type` (`ValueError`, already checked before this new pre-check). These stay raise-based because REQ-002 scopes this feature narrowly, and because 519d1206 itself cautions against treating its non-raising workaround as a general best practice to apply everywhere reflexively -- these three failure modes are also comparatively rare in practice compared to guessing an out-of-vocabulary status string, since an agent typically already has a syntactically valid id/type pair (e.g. from a prior `list_<d>`/`get_<d>` call) but has no way to discover a domain's exact allowed-status set ahead of time short of reading its schema resource or triggering the failure once.

### Consequences

- Good: the allowed-values detail for set_status's single most commonly hit failure mode survives MCP clients that truncate `isError: true` results, matching 519d1206's own proven rationale.
- Good: no vocabulary duplication -- a single, small mapping table in `set_status.py` reuses each domain's existing `_ALLOWED_STATUSES`/`_FIXED_STATUSES` constant directly.
- Good: fails fast (no domain lock, no file I/O) for a purely input-shaped failure, consistent with the existing `validate_id`/`superseded_by` guards already in `set_status()`.
- Bad: widens the set of shapes a caller of `set_status()` must handle for a "non-exception" return -- previously any non-raising return was always one of the 13 successful per-domain types; callers must now also check `result.valid`/isinstance for this one additional failure mode, while every other set_status failure mode still raises.
- Bad: doubles this repo's documented asymmetric-tool-contract caveat (519d1206 already introduced one non-raising exception to the raise-based convention; this ADR introduces a second, narrower one) -- a future contributor must know both rationales rather than assume a single universal error-reporting convention across the whole tool surface.
- Bad (tracked, not blocking): as with 519d1206's own Confirmation section, a live MCP-client/OpenCode-session round-trip is not something an agent session can reliably automate; verification is limited to unit-level assertions of the structured result's shape and content, not an end-to-end client reproduction proving the truncation is actually avoided in practice.

### Confirmation

To be confirmed during feat-103-set-status-error's Phase 3: unit-level tests asserting `InvalidStatusResult` (not a raised `pydantic.ValidationError`) is returned for an out-of-vocabulary `status`, for all 13 domains (12 whole-body + adr), each asserting its own domain's `type`/rejected `status`/full sorted `allowed_values` list/exact `message` wording appear in the result, and that the on-disk file remains byte-identical (mirroring the existing `test_out_of_vocabulary_status_raises_validation_error_file_untouched` tests' file-untouched assertion, updated to the new non-raising shape). As with 519d1206's own Confirmation section, no live MCP-client/OpenCode-session round-trip is attempted or recorded as an outstanding commitment, for the same automation-limitation reasons documented there.

## Pros and Cons of the Options

### Option 1: Do nothing -- leave invalid-status raise-based

#### Pros

- No new work, no new result-type union, no asymmetric tool contract to document or maintain beyond the one 519d1206 already introduced.
- Matches every other set_status failure mode's raise-based convention.

#### Cons

- Known to fail silently on at least one real, current, widely-used MCP client (OpenCode 1.18.27) for exactly the same reason 519d1206 fixed for `validate`: the allowed-values detail feat-27-validation invested in is discarded before it ever reaches the agent.
- Leaves issue #103's reported symptom unaddressed for set_status's single most common failure mode, even though the fix is already proven out for an analogous case (`validate`).

### Option 2: Wait for an upstream OpenCode fix

#### Pros

- Fixes the root cause rather than working around it; benefits every remaining raise-based tool automatically, once adopted, with no special-casing needed in this repo.

#### Cons

- Entirely outside this repo's control and timeline, same as 519d1206's own Option 2 -- no guarantee of if, when, or how a third-party project accepts and releases a fix.
- Leaves this repo's agents exposed to the same opaque-failure symptom for set_status's invalid-status case in the meantime, for an indeterminate period.
- Does not address other MCP clients that may exhibit the same or a similar defect independently of OpenCode.

### Option 3: Redesign set_status's entire contract to non-raising

#### Pros

- Uniform contract across every set_status failure mode -- a caller only ever needs one non-raising-result-checking code path, not a mix of raise-based and structured-result failures.
- Would also protect the rarer failure modes (unknown id, path-injection, superseded_by misuse) from the same client-side truncation, should an agent ever hit one of those through an affected client.

#### Cons

- Disproportionate to REQ-002's narrow scope and to how issue #103 was actually triggered (an invalid status value, not a bad id or a superseded_by misuse).
- A much larger, riskier change surface: every one of the 13 adapters' id-resolution/lock/not-found paths would need redesigning, not just the single vocabulary check this ADR targets.
- Contradicts 519d1206's own explicit caution against treating its non-raising workaround as an unconditional best practice to apply everywhere reflexively, rather than a targeted fix for a demonstrated, specific pain point.

### Option 4: Narrowly extend the non-raising approach to the invalid-status case only (chosen)

#### Pros

- Directly fixes issue #103's reported symptom for set_status's single most common, most easily triggered failure mode, using a rationale and pattern already proven out by 519d1206 for `validate`.
- Fully within this repo's own control; immediately effective without waiting on a third party.
- No vocabulary duplication -- reuses each domain's existing `_ALLOWED_STATUSES`/`_FIXED_STATUSES` constant directly via a small, module-scope lookup table.
- Fails fast (no domain lock, no file I/O) for a purely input-shaped failure, consistent with the existing `validate_id`/`superseded_by` guards already in `set_status()`.
- Keeps every other set_status failure mode's contract unchanged, minimizing the change surface and matching REQ-002's explicit narrow-scope framing.

#### Cons

- Widens the set of shapes a caller of `set_status()` must handle for a non-raising return (13 successful per-domain types plus now one structured invalid-status result).
- Doubles this repo's documented asymmetric-tool-contract caveat (519d1206 already introduced one non-raising exception; this ADR introduces a second, narrower one) -- a future contributor must know both rationales.
- Same tracked-but-unresolved limitation as 519d1206: no live MCP-client/OpenCode-session round-trip can be automated to prove the truncation is actually avoided in practice; verification stays unit-level.

## More Information

- ADR 519d1206-4d2a-4500-9046-6db635209996 ("Design validate as a non-raising, structured-result tool to work around client-side MCP error-content truncation"): the prior decision this ADR narrowly extends; its Context/Consequences/Confirmation sections carry the full original investigation this ADR does not repeat.
- Feature plan and progress: `.specmgr/feat/feat-103-set-status-error/README.md` (Design Notes section sketches the same result shape/message wording this ADR finalizes).
- feat-27-validation (done): supplies the actionable, allowed-values-enriched exception message this decision's `InvalidStatusResult.message` field's wording is modeled on.
- feat-81-83-validation (done): original client-truncation investigation 519d1206 is based on.
