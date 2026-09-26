---
status: accepted
date: '2026-09-25'
decision-makers: OpenCode agent + user decision
id: 9080b37c-82b3-4f63-81f1-79641d0bf14c
version: 1.0.0
---

# Extend the non-raising structured-result workaround to get_<d>'s parse-failure case

## Context and Problem Statement

feat-150-mcp-lifecycle-commands (GitHub issue #150) Phase 1 adds a `repair` MCP prompt whose with-id discovery branch says "call `get_<d>(id)` and read its wrapped parse error". That claim is factually wrong for the 11 flat-file domains: `general.tools._doc_paths.find_doc_path_by_id` -- the shared id-to-path scan every `get_<d>` routes through -- silently skips a file that fails to parse (so one broken file never blocks lookup of a different, valid id). So `get_req(id)` on a document that exists but is broken raises only a generic "no requirement found with id ... the id must be the bare document UUID" -- no parse cause, no path, no line. Only `feat` (whose hand-rolled `feat.tools._paths.find_feat_path_by_id` already wraps the parse failure) surfaces the cause. Today's manual smoke test reproduced both the operational dead-end and the underlying delivery defect: on this OpenCode host, `get_req`'s exception text was truncated to a bare "Error executing tool get_req" while `list_req()`'s failed-row `error` field -- part of a normal, successful (`isError: false`) result -- passed through intact.

This is the third case in the ADR 519d1206-4d2a-4500-9046-6db635209996 workaround chain (client-side `isError: true` result truncation, confirmed on OpenCode 1.18.27): case 1 redesigned the generic `validate` tool to a non-raising `{valid, errors}` result; case 2 (ADR b399f1ce-ed42-4929-b01c-7a57d18e8014) extended that same rationale narrowly to `set_status`'s invalid-status case only, via a purpose-built `InvalidStatusResult`. This ADR decides whether and how to extend the chain to case 3 -- `get_<d>` on a document that exists but fails to parse -- and records the concrete design feat-150's Phase 1a implements from.

## Decision Drivers

- Deliver the actionable parse error (cause, path, line) for a with-id `get_<d>` lookup host-independently, the same way 519d1206/b399f1ce did for `validate` and `set_status` -- a broken document is exactly the one case Phase 1's `repair` prompt with-id branch depends on, and a truncated generic not-found message is an operational dead-end.
- Cost ~zero tokens on the common (successful) path: the MCP SDK serializes results with `model_dump(..., exclude_none=True)`, so a new union member that only materializes on the failure path adds nothing to a healthy `get_<d>`'s wire form.
- Reuse the already-twice-established union-result precedent (519d1206's `ValidateResult`, b399f1ce's `InvalidStatusResult`) rather than inventing a new failure-delivery mechanism.
- Keep the change narrow and get-only: `update`/`delete`/`set_status`/`set_classification`/`validate`/`list_references` must keep raising exactly as today, and `find_doc_path_by_id`'s documented skip-on-parse-failure behavior must not change.

## Considered Options

- Option 1: Do nothing -- keep every `get_<d>` raise-based, relying on the existing exception message.
- Option 2: Enrich the exception by adding a name-prefix fallback inside the shared `find_doc_path_by_id` scan so the not-found message carries the parse cause.
- Option 3: Wrap every successful `get_<d>` result in a uniform `{document, error, path}` envelope so the failure channel is always present.
- Option 4 (chosen): Narrowly extend 519d1206's non-raising, structured-result approach to the `get_<d>` parse-failure case only, via a purpose-built `ParseFailureResult` returned instead of raising the domain's not-found error.

## Decision Outcome

Option 4: a new, purpose-built, non-raising `ParseFailureResult` (in `general/models/parse_failure_result.py`, mirroring `InvalidStatusResult`'s shape) with fields `error: str` (the parse-failure message), `path: str` (absolute on-disk file path), and `id: str` (the requested id, echoed). Every `get_<d>` tool (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`; ADR excluded) returns it in place of raising the domain's `XNotFoundError` when the requested id resolves to an on-disk file whose content fails to parse -- for both `raw=False` and `raw=True` (a broken document never returns raw text; the invariant that no specmgr MCP tool can return the raw content of a document that fails to parse is load-bearing for `repair`). Every other outcome is unchanged: a healthy document returns exactly today's shape (the parsed `<D>Document`, or the body `str` when `raw=True` -- the success wire form stays byte-identical because the SDK's `exclude_none` means the new union member only materializes on the failure path), a truly absent id still raises the domain's `XNotFoundError`, and an invalid id shape / path injection is still a `ValueError` from `validate_id` before any file access.

The concrete mechanism (implemented in feat-150 Phase 1a):

1. Flat domains (11): on `XNotFoundError` from `load_by_id`, run a new shared helper `general.tools._doc_paths.find_parse_failure(base_dir, id_, read_fn) -> tuple[Path, str] | None`. It scans `iter_doc_paths(base_dir)` for the single file whose stem encodes `id_` as a hyphen-bounded token (the flat-file naming is `<type>-<id>-<slug>.md`), attempts the domain's own cache-backed `read_fn(path)` on it, and returns `(path, str(exc))` if that read raises a parse error (`AssertionError`/`pydantic.ValidationError`/`yaml.YAMLError`), else `None` (no name match, a vanished file, or a name-matching file that parses cleanly -- a frontmatter-id mismatch). It does not touch `find_doc_path_by_id`'s skip behavior.

2. `feat`: no scan -- the folder name IS the id. A bespoke `feat.tools._paths.find_feat_parse_failure(base_dir, id_)` checks the single `<base>/<id_>/README.md` path and converts an existing-but-unparseable file into the same `(path, str(exc))` shape, extracting the inner parse message so it matches `list_feat`'s failed-row error text.

3. Error-text consistency (a testable invariant): `ParseFailureResult.error` MUST equal the `error` field of the `list_<d>` failed row for the same broken file. Both are `str()` of the domain's own parse exception captured through the same cache-backed `read_<d>` reader, so the two are byte-identical by construction -- the `get_<d>` path deliberately does not reuse `load_by_id`'s (or `find_*_path_by_id`'s) own wrapped message ("...could not be read as a valid ... document..."), which prepends tool-specific framing that `list_<d>` does not carry.

4. If the mechanism yields `(path, error)`, the `get_<d>` tool applies the same `assert_within(base_dir, path)` defense-in-depth guard the primary path uses, then returns the result; otherwise it re-raises the original `XNotFoundError` unchanged.

### Consequences

- Good: the actionable parse error (cause, path, line) now reaches the calling agent host-independently for a with-id `get_<d>` lookup, closing the operational dead-end Phase 1's `repair` narration depends on -- the exact case 519d1206's wire-level proof showed would otherwise be truncated.
- Good: `feat` and the 11 flat-file domains are unified -- every `get_<d>` now surfaces a parse failure the same way, where before only `feat` did.
- Good: zero change to the successful `get_<d>` wire shape -- the SDK's `exclude_none` means the new union member only materializes on the failure path.
- Bad: this is the third documented asymmetric tool contract in this repo (519d1206's `validate`, b399f1ce's `set_status`, now `get_<d>`) -- a future contributor must know the chain rather than assume a single universal error-reporting convention across the whole tool surface.
- Bad: the `get_<d>` return union widens from two shapes (`<D>Document | str`) to three (`<D>Document | str | ParseFailureResult`).
- Bad (tracked, not blocking): as with 519d1206/b399f1ce, a live MCP-client round-trip cannot be automated; verification is unit-level only. The workaround remains harmless and correct if/when a client fixes its `isError: true` handling.

### Confirmation

Confirmed during feat-150-mcp-lifecycle-commands Phase 1a at the unit level: a `ParseFailureResult` (not a raised not-found error) is returned for a broken document for all 12 whole-body domains, its `error` text equals the same file's `list_<d>` failed-row `error`, `raw=True` on a broken document still returns a `ParseFailureResult` (never a raw `str`), a healthy document returns exactly the pre-change shape, and a truly absent id still raises the domain's not-found error -- via direct Python calls, mirroring the confirmation 519d1206/b399f1ce record. No live MCP-client/OpenCode-session round-trip is attempted or recorded as an outstanding commitment, for the same automation-limitation reasons both prior ADRs document.

## Pros and Cons of the Options

### Option 1: Do nothing -- keep get\_<d> raise-based

#### Pros

- No new work, no new result-type union, no asymmetric tool contract to document or maintain beyond the two 519d1206/b399f1ce already introduced.
- Matches every other `get_<d>` failure mode's raise-based convention.

#### Cons

- Known to fail on at least one real, current, widely-used MCP client (OpenCode 1.18.27) for exactly the same reason 519d1206 fixed for `validate` and b399f1ce fixed for `set_status`: the parse cause feat-27-validation invested in is discarded before it reaches the agent, and the agent is left a bare, generic not-found message with no cause, path, or line.
- Leaves Phase 1's `repair` prompt with-id branch an operational dead-end: it narrates reading "the wrapped parse error" from `get_<d>(id)`, which the 11 flat domains never produce.

### Option 2: Enrich the exception via a name-prefix fallback in find_doc_path_by_id

#### Pros

- A single, shared change could surface the parse cause in the existing `XNotFoundError` message for every id-resolving tool, not just `get_<d>`.

#### Cons

- Changes the failure-message behavior of every id-resolving tool (`update`/`delete`/`set_status`/`set_classification`/`list_references` too), which are all required to keep raising exactly as today -- a broader change surface than Phase 1a's get-only scope.
- Still rides the lossy `isError: true` channel: an enriched exception is exactly what 519d1206's wire-level proof showed the client truncates to a bare "Error executing tool ...". Enriching the message does not sidestep the truncation; only a successful (`isError: false`) structured result does.

### Option 3: Uniform envelope wrapping every successful result

#### Pros

- A single, uniform `{document, error, path}` shape across all `get_<d>` outcomes -- one non-raising path to reason about.

#### Cons

- Changes the successful `get_<d>` wire shape for every consumer (the parsed document would nest under `document`), a disproportionate change to a working, widely-relied-upon contract for the sake of one failure case.
- Contradicts 519d1206's own explicit caution against treating its non-raising workaround as an unconditional best practice to apply everywhere reflexively.

### Option 4: Narrow ParseFailureResult on the get_<d> failure path only (chosen)

#### Pros

- Directly fixes Phase 1's `repair` with-id dead-end for every whole-body domain, using a rationale and pattern already proven out by 519d1206/b399f1ce.
- Fully within this repo's own control; immediately effective without waiting on a third-party client fix.
- Zero change to the successful `get_<d>` wire shape -- the SDK's `exclude_none` means the new union member only materializes on the failure path.
- Keeps every other id-resolving tool's contract (`update`/`delete`/`set_*`/`validate`/`list_references`) and `find_doc_path_by_id`'s skip behavior unchanged, matching Phase 1a's explicit get-only, narrow scope.
- Unifies `feat` and the 11 flat-file domains under one failure-delivery shape.

#### Cons

- Introduces a third documented asymmetric tool contract (519d1206's `validate`, b399f1ce's `set_status`, now `get_<d>`) -- a future contributor must know the chain.
- Widens the `get_<d>` return union from two shapes to three.
- Same tracked-but-unresolved limitation as 519d1206/b399f1ce: no live MCP-client round-trip can be automated; verification stays unit-level.

## More Information

- ADR 519d1206-4d2a-4500-9046-6db635209996 ("Design validate as a non-raising, structured-result tool to work around client-side MCP error-content truncation"): the prior decision this ADR extends; its Context/Consequences/Confirmation carry the full original investigation.
- ADR b399f1ce-ed42-4929-b01c-7a57d18e8014 ("Extend the non-raising structured-result workaround to set_status's invalid-status case"): the immediate precedent for a narrow, purpose-built, union-annotated structured result; the `InvalidStatusResult` model this ADR's `ParseFailureResult` mirrors.
- Feature plan and progress: `.specmgr/feat/feat-150-mcp-lifecycle-commands/README.md` (Phase 1a, REQ-013; the `repair` prompt whose with-id branch this ADR unblocks).
- GitHub issue #150: https://github.com/dfch/biz.dfch.SpecMgr/issues/150.
