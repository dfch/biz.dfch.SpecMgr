---
date: '2026-09-03'
decision-makers: OpenCode agent + user decision
id: 519d1206-4d2a-4500-9046-6db635209996
status: accepted
version: 1.0.0
---

# Design validate as a non-raising, structured-result tool to work around client-side MCP error-content truncation

## Context and Problem Statement

feat-81-83-validation (GitHub issues #81/#83) investigated why a validation failure surfaces to an agent as an opaque, uncaught exception rather than a structured, inspectable result. feat-27-validation already made every validation exception's message actionable (field path, line number, cause/fix hint). feat-67-70-71 confirmed the MCP transport forwards that full message to the client unabridged, with no truncation, at the wire level. Yet, when feat-81-83-validation's own Phase 1 investigation reproduced issue #83's two literal repro cases through the actual `validate_req`/`validate_dec`/`validate_feat` MCP tools inside an OpenCode 1.18.27 session, the calling agent received only a bare, contentless `"Error executing tool <name>"` string for each -- the full, actionable message never reached the model, despite being present, in full, in the server's wire-level `CallToolResult` (confirmed via a standalone MCP JSON-RPC client that bypassed OpenCode's own tool-calling layer entirely). A shallow clone of OpenCode's `dev`-branch source shows its own code path for a failed MCP tool call (`packages/opencode/src/mcp/catalog.ts`, `packages/opencode/src/tool/code-mode.ts`) explicitly joins and preserves every text content block from an `isError: true` result -- so, as read, this loss is not expected from that code, and the exact root cause remains unpinned-down and outside this repo's control (an unfiled draft report is kept at `.specmgr/feat/feat-81-83-validation/opencode-issue-mcp-tool-error-truncated.md`). By contrast, every successful (`isError: false`) tool result observed in the same session -- regardless of size -- passed through completely and losslessly (e.g. `list_feat`'s full multi-entry JSON, large `get_<d>`/`parse_<d>` bodies). This means: if OpenCode's (or an equivalent MCP client's) tool-error handling worked the way its own source suggests it should, this repo would not need to change `validate`'s contract at all -- a raise-on-failure tool whose exception message is already fully actionable (feat-27-validation) would be sufficient, matching every other tool's convention in this codebase. The redesign of `validate` to a non-raising, structured `{valid, errors}` result is therefore fundamentally a workaround for a confirmed, external client defect, not a change motivated by this repo's own design preferences in isolation. This decision is recorded as an ADR, not left only in the feature's own Design Notes, because its implication reaches beyond this one feature: any present or future tool in this repo that signals failure by raising is exposed to the same externally-imposed risk on any MCP client exhibiting this behavior.

## Decision Drivers

- Preserve feat-27-validation's actionable failure detail all the way to the calling agent, regardless of which MCP client is in use.
- Avoid depending on a specific client's (OpenCode's) internal error-handling correctness, since that is outside this repo's control and was empirically shown to be unreliable in a real, current, widely-used client (OpenCode 1.18.27).
- Keep the fix entirely within this repo's own server-side tool contracts, since filing or fixing the client-side bug is outside this repo's control (tracked only as a courtesy, unfiled draft issue).
- Do not overstate the fix as a generally "better design" independent of the underlying client defect -- it is a targeted workaround, and should be documented as such so a future maintainer does not mistake it for an unconditional best practice.

## Considered Options

- Option 1: Do nothing -- keep every `validate_<d>` tool raise-based, relying on feat-27-validation's already-actionable exception messages.
- Option 2: File and wait for an upstream fix in OpenCode (or whichever MCP client is affected), keeping `validate_<d>` raise-based in the meantime.
- Option 3 (chosen): Redesign the new generic `validate` tool (feat-81-83-validation REQ-003/004) to a non-raising, structured `{valid, errors}` result, and record this rationale for future tool-design decisions in this repo.

## Decision Outcome

Option 3: the new generic `validate` tool never raises for a content-validation failure; it always returns a structured `{valid: bool, errors: list[{message: str}]}` result, explicitly as a defensive workaround for the observed OpenCode 1.18.27 client-side truncation of `isError: true` MCP tool results -- not as an independently preferred design in isolation. This does not retroactively change any other existing raise-based tool's contract in this repo (`create_<d>`, `update`, `set_status`, `set_classification`, `delete`, `parse_<d>`/`get_<d>` all keep raising); it is scoped to `validate` and to guiding future tool-design decisions that face the same need. Filing or fixing the underlying OpenCode-side defect remains explicitly out of scope for this repo -- the draft report at `.specmgr/feat/feat-81-83-validation/opencode-issue-mcp-tool-error-truncated.md` is kept only as a courtesy artifact, not a dependency of this decision.

### Consequences

- Good: `validate`'s failure detail reliably reaches the calling agent regardless of which MCP client is used, without depending on any external fix or its timeline.
- Good: establishes a documented rationale that future generic dispatch tools facing the same need can point to directly, instead of independently rediscovering the same investigation.
- Bad: introduces an asymmetry in this repo's tool-contract conventions -- most tools still raise on failure, so contributors must know this one exception's rationale rather than assume a single universal error-reporting convention across the whole tool surface.
- Bad: depends on an external, unfiled bug report for full context; if OpenCode (or another affected client) fixes its handling, this repo will carry a workaround that is no longer strictly necessary, though it remains harmless and still correct.

### Confirmation

Confirmed during feat-81-83-validation's Phase 1 investigation: a standalone MCP JSON-RPC client, bypassing OpenCode's own tool-calling layer, proved the specmgr server always sends the full, actionable message on the wire; every observed successful (`isError: false`) tool result in the same OpenCode 1.18.27 session passed through intact regardless of size, while every observed `isError: true` result was truncated to a bare `"Error executing tool <name>"`. Future confirmation, once the generic `validate` tool is implemented (feat-81-83-validation Phase 2): its `{valid, errors}` result must be observed intact end-to-end through a live OpenCode session for at least the two Phase 1 regression fixtures (the `req` naive-isoformat-timestamp repro and the `dec` em-dash-heading repro).

## Pros and Cons of the Options

### Option 1: Do nothing -- keep validate\_<d> raise-based

#### Pros

- No new work, no asymmetric tool contract to document or maintain.
- Matches every other tool's raise-based convention in this repo.

#### Cons

- Known to fail silently on at least one real, current, widely-used MCP client (OpenCode 1.18.27): the actionable message feat-27-validation invested in is discarded before it ever reaches the agent.
- Defeats the purpose of feat-27-validation's enrichment work whenever exercised through that client's `isError` path -- the agent is left with exactly the opaque-failure symptom issue #83 reports.

### Option 2: File and wait for an upstream OpenCode fix

#### Pros

- Fixes the root cause rather than working around it; benefits every existing and future raise-based tool automatically, once adopted, with no special-casing needed in this repo.

#### Cons

- Entirely outside this repo's control and timeline; no guarantee of if, when, or how a third-party project accepts and releases a fix.
- Leaves this repo's own agents broken for validation failures in the meantime, for an indeterminate period.
- Does not address other MCP clients that may exhibit the same or a similar defect independently of OpenCode.

### Option 3: Redesign validate to a non-raising, structured result (chosen)

#### Pros

- Fully within this repo's own control; immediately effective without waiting on a third party.
- Empirically validated: successful (`isError: false`) tool results were observed, in the same investigation, to pass through completely regardless of size, so this design sidesteps the exact channel shown to be lossy.
- Documents the rationale once, for reuse by any future tool facing the same need, rather than leaving it implicit or requiring rediscovery.

#### Cons

- Introduces an asymmetry in this repo's tool-contract conventions: most tools still raise on failure, and a future contributor must know this exception's specific rationale.
- Explicitly a workaround, not an independently "better" design -- if not documented as such, it risks being copied as a general best practice beyond the situations that actually warrant it.

## More Information

- Feature plan and progress: `.specmgr/feat/feat-81-83-validation/README.md` (Design Notes section carries the full investigation detail this ADR summarizes).
- Drafted, unfiled upstream bug report: `.specmgr/feat/feat-81-83-validation/opencode-issue-mcp-tool-error-truncated.md`.
- Related work: `feat-27-validation` (done) -- supplies the actionable exception messages this decision's `{valid, errors}` result reuses verbatim; `feat-67-70-71` (done) -- confirmed the MCP transport itself does not truncate/discard those messages, which this ADR's investigation corroborated at the wire level while narrowing the actual loss to the client's `isError: true` handling.
