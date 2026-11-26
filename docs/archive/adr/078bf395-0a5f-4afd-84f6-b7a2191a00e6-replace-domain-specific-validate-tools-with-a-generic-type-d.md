---
status: accepted
date: '2026-09-04'
decision-makers: OpenCode agent + user decision
id: 078bf395-0a5f-4afd-84f6-b7a2191a00e6
version: 1.0.0
---

# Replace domain-specific validate tools with a generic type-dispatched validate tool

## Context and Problem Statement

The specmgr MCP server exposes thirteen `validate_<d>` tools: twelve whole-body-domain tools (`validate_req`, `validate_uc`, `validate_tsk`, `validate_qa`, `validate_prb`, `validate_gol`, `validate_rsk`, `validate_dec`, `validate_sop`, `validate_feat`, `validate_vcr`, `validate_sysrs`) that are structurally identical byte-for-byte except for the domain name and the Pydantic model/parse-function names they call, plus `validate_adr` (id-based, re-reads from disk, no `full` parameter), which is structurally different. GitHub issue #81 asks for an inventory of these tools and a decision on how to consolidate them. Separately, GitHub issue #83 reports that a validation failure surfaces only as an opaque, uncaught exception rather than a structured, inspectable result -- investigation (`.specmgr/feat/feat-81-83-validation/README.md` Design Notes) traced this to a confirmed external MCP-client rendering gap that discards `isError: true` tool-result content (recorded separately as ADR 519d1206-4d2a-4500-9046-6db635209996), for which converting a dry-run check tool from raise-on-failure to an always-returned, structured `{valid, errors}` result is a robust, client-independent workaround. Both problems point at the same twelve tools, so this decision addresses them together: reduce the tool surface, per ADR 36905d5b-8057-4294-8665-c7eed5534db0's existing generic-dispatch convention (`update`/`set_status`/`set_classification`/`delete`), and change the result contract from raise-only to a non-raising structured result -- a first for that convention, since every prior generic tool it covers is mutation-adjacent and still raises on failure.

## Decision Drivers

- Minimal tool surface: twelve near-duplicate `validate_<d>` tools collapse into one, matching the `update`/`set_status`/`set_classification`/`delete` precedent (ADR 36905d5b-8057-4294-8665-c7eed5534db0).
- The calling client already knows the domain (the same vocabulary as the frontmatter `type` field), so an explicit `type` parameter costs the client nothing and keeps dispatch unambiguous, single-domain, and directory-scan-free -- the same driver ADR 36905d5b already established.
- `validate` is disk-free and id-free (content-based dry run) for all twelve domains -- no lock, no filesystem access, no id resolution needed, unlike `update`/`set_status`/`set_classification`/`delete`'s id-based adapters.
- REQ-004 (feat-81-83-validation): the generic tool must never raise for a content-validation failure -- it always returns a structured `{valid: bool, errors: list[{message: str}]}` result, reusing feat-27-validation's already-enriched exception messages verbatim, while a `full`/content-shape mismatch (an already-actionable caller error, not a content-validation failure) still raises `ValueError`. This is a workaround for the confirmed external client defect recorded in ADR 519d1206-4d2a-4500-9046-6db635209996, and is the reason this consolidation changes the tool's error-handling contract, not just its dispatch mechanism, unlike every prior tool ADR 36905d5b-8057-4294-8665-c7eed5534db0 covers.
- `validate_adr`'s signature (`id`-based, disk-touching, no `full` parameter, `AdrParseError` instead of `AssertionError` as its structural channel, an additional `AdrNotFoundError` failure mode) does not fit the same per-domain-adapter shape as the twelve content-based tools; forcing it in would require either bolting a content-based dry-run path onto ADR's own parser or giving the generic tool a divergent per-type parameter shape -- both rejected as unnecessary complexity for one domain.

## Considered Options

1. A generic `validate(type, content, full)` tool with one private per-domain adapter inside `general/tools/validate.py` (`adr` excluded, `validate_adr` kept as its own standalone tool, unchanged), returning a non-raising `{valid, errors}` result for content-validation failures while still raising `ValueError` for a `full`/content-shape mismatch or an unsupported `type`. Chosen.
2. Keep the twelve per-domain `validate_<d>` tools, and add the non-raising `{valid, errors}` behavior to each independently.
3. Keep the raise-only per-domain tools' error contract unchanged, and only add a generic dispatch wrapper around them (addressing issue #81's tool-surface complaint but not issue #83's opaque-failure complaint).
4. Force `validate_adr` into the same generic tool via a divergent, per-type parameter shape (e.g. an optional `id` alongside `content`/`full`), so all thirteen `validate_<d>` tools collapse into one.

## Decision Outcome

Option 1: a generic, type-dispatched `validate(type, content, full)` tool in `general/tools/validate.py`, covering the twelve whole-body domains (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`) via one private per-domain adapter each (a verbatim port of the deleted tool's body, same `frontmatter.loads(content).metadata`-based frontmatter detection, same `wrap_tool_errors(domain=..., tool="validate", channel=...)` message enrichment). The public `validate` function wraps each adapter call in a `try`/`except (AssertionError, pydantic.ValidationError, yaml.YAMLError)` that returns `{"valid": False, "errors": [{"message": str(exception)}]}` on a catch instead of letting the exception propagate; a `full`/content-shape mismatch or an unsupported `type` still raises `ValueError` before or during dispatch, since that is a caller-usage error, not a content-validation failure, and is already actionable on its own. The twelve per-domain `validate_<d>` tools are removed outright, no deprecated wrappers -- matching `update`/`set_status`/`set_classification`/`delete`'s own precedent. `validate_adr` is excluded and stays a standalone tool, entirely unchanged: it remains `id`-based, disk-touching, always re-reads and re-parses the on-disk document, has no `full` parameter, and still raises rather than returning a structured result -- Option 4 was rejected as unnecessary complexity for one structurally divergent domain.

### Consequences

- Bad (breaking, 0.x): twelve MCP tools removed, one added. The MCP tool list is the only client contract; the change is recorded in `CHANGELOG.md` under `[Unreleased]`.
- `validate` is the first tool ADR 36905d5b-8057-4294-8665-c7eed5534db0's generic-dispatch convention covers that is read-only/dry-run rather than mutation-adjacent, and the first to change its error-handling contract (raise-only -> non-raising structured result) as part of the consolidation, not just its dispatch mechanism -- this ADR extends that convention to cover this new tool category, it does not amend or supersede ADR 36905d5b-8057-4294-8665-c7eed5534db0 itself.
- New forward convention: any future read-only/dry-run per-domain tool (validate-like) added for a new domain gets one adapter in the existing generic `validate` tool, never a new per-domain `validate_<d>` tool -- the same forward convention `delete`'s own ADR 1af6787b-eaab-4e8f-888f-531c1e76c19d already established for mutation tools.
- `validate_adr` remains a permanent, documented exception to the `validate` tool's domain list, the same way `adr` is already excluded from `update`/`set_classification`/`delete`'s domain lists for its own domain-specific reasons.
- The `{valid, errors}` non-raising shape's own rationale (a workaround for a confirmed external MCP-client defect, not an independently preferred design) is recorded separately in ADR 519d1206-4d2a-4500-9046-6db635209996; this ADR records only the dispatch-consolidation shape and the resulting error-handling contract, not that rationale.

## Pros and Cons of the Options

### Option 1: Generic `validate(type, content, full)` with per-domain adapters, non-raising result

Good: a single validate entry point (twelve near-duplicate tools collapse into one plus twelve small private adapters in one file, mirroring `update`/`set_status`/`set_classification`/`delete`); the explicit `type` keeps dispatch single-domain and unambiguous; disk-free/id-free, so no lock or filesystem access is needed; the non-raising `{valid, errors}` result sidesteps the confirmed external MCP-client rendering gap (ADR 519d1206-4d2a-4500-9046-6db635209996) regardless of which client calls it; `validate_adr` is left untouched, avoiding forcing an artificial common shape onto a structurally divergent tool.
Bad: the `validate` tool file grows as domains are added (one adapter per domain); callers must pass the explicit `type`; the tool's error contract now differs from every other generic tool in the codebase (non-raising vs. raise-only), which future maintainers must keep in mind when reusing this shape elsewhere.

### Option 2: Keep the twelve per-domain tools, add non-raising behavior to each independently

Good: no new generic dispatch surface; each domain's tool stays self-contained and independently discoverable.
Bad: the same non-raising `{valid, errors}` change must be implemented and tested twelve times instead of once; the tool surface stays at twelve near-duplicate tools, contradicting the minimal-surface driver and the `update`/`set_status`/`set_classification`/`delete` precedent of ADR 36905d5b-8057-4294-8665-c7eed5534db0. Rejected.

### Option 3: Generic dispatch wrapper only, keep the raise-only error contract

Good: addresses issue #81's tool-surface complaint with a smaller change (dispatch only, no error-handling rework).
Bad: does not address issue #83's opaque-failure complaint at all -- a caught exception would still propagate through the generic tool exactly as it does today, leaving the confirmed external MCP-client rendering gap (ADR 519d1206-4d2a-4500-9046-6db635209996) unmitigated. Rejected.

### Option 4: Force `validate_adr` into the generic tool via a divergent parameter shape

Good: all thirteen `validate_<d>` tools would collapse into a single tool, the smallest possible tool-surface count.
Bad: requires either bolting a content-based dry-run path onto ADR's own parser (out of scope, ADR's own parser is disk-based by design) or giving the generic tool a divergent per-type parameter shape (an optional `id` alongside `content`/`full`) that every one of the twelve other domains would never use -- unnecessary complexity for one structurally divergent domain. Rejected.

## More Information

- Feature plan and progress: `.specmgr/feat/feat-81-83-validation/README.md` (REQ-002 through REQ-005, ACC-002 through ACC-005, Design Notes' full tool inventory).
- Related ADRs: 36905d5b-8057-4294-8665-c7eed5534db0 (the generic type-dispatched tool convention this decision extends), 519d1206-4d2a-4500-9046-6db635209996 (the non-raising `{valid, errors}` shape's own external-client-defect-workaround rationale), 1af6787b-eaab-4e8f-888f-531c1e76c19d (`delete`'s own precedent of a dedicated ADR extending ADR 36905d5b-8057-4294-8665-c7eed5534db0 even where the general convention already existed).
