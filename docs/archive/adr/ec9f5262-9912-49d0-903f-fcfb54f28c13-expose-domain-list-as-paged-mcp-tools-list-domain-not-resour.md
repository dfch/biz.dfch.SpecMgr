---
status: accepted
date: '2026-08-19'
decision-makers: OpenCode agent + user decision
id: ec9f5262-9912-49d0-903f-fcfb54f28c13
version: 1.0.0
---

# Expose <domain>_list as paged MCP tools (list_<domain>), not resources

## Context and Problem Statement

The five `<domain>_list` MCP resources (`specmgr://adr/list`, `specmgr://req/list`, `specmgr://uc/list`, `specmgr://tsk/list`, `specmgr://qa/list`) each did a full, unbounded directory scan and returned a bare `list[<D>Summary]` on every call. As the number of documents in a base directory grows, this becomes increasingly expensive and eventually unwieldy for a calling agent to consume in one shot. Pagination (`max_results`/`offset`) was raised as feat-7-various-improvements Task 0.15/REQ-002, but MCP resources can only be parameterized via URI-template path segments, not arbitrary query parameters -- so `max_results`/`offset` cannot be added to a `@mcp.resource()` without contorting the URI shape. This mirrors the reasoning already recorded in ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 for `get_req`: resources are a poor fit whenever a read needs caller-supplied parameters.

## Decision Drivers

- Pagination parameters (`max_results`/`offset`) do not fit MCP resources, which are URI-template-only.
- Consistency with ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614's precedent: prefer tools over resources for parameterized, on-demand reads.
- Reuse an existing, proven paged-result shape rather than invent a new one, for consistency across this project's own MCP servers.
- Preserve the exact current scan/sort/skip-broken-file semantics -- no behavioral regression for callers relying on today's full listing.
- Keep the five domains' summary models on one shared, documented base field set where the dependency graph allows it.

## Considered Options

- Option 1: Keep `<domain>_list` as resources, encode `max_results`/`offset` into the URI template (e.g. `specmgr://req/list/{offset}/{max_results}`)
- Option 2: Convert all five `<domain>_list` resources into `@mcp.tool()` `list_<domain>` tools accepting `max_results`/`offset`, returning a shared `PagedResult[T]` wrapper
- Option 3: Keep resources unbounded as-is and defer pagination indefinitely

## Decision Outcome

Chosen option: "Option 2: Convert all five `<domain>_list` resources into `list_<domain>` tools returning `PagedResult[T]`", because it is the only option that gives callers real, bounded pagination without abusing the URI-template mechanism, and it follows the precedent already accepted in ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614. Each `list_<domain>` tool accepts `max_results`/`offset` (default page size 25, cap 100; out-of-range inputs are clamped, not errored), and returns a `PagedResult` shape -- `total`, `offset`, `max_results`, `truncated`, `results` -- taken verbatim from this project's own `asdste100` MCP server (`word_list`, `rules_examples`), rather than inventing a new contract. Each tool still fully materializes its domain's summary list first (identical scan/sort/skip-broken-file behavior as the retired resource) and then slices it in memory, so `total` reflects only parseable documents and no existing behavior regresses.

Four of the five domains' `*Summary` models (`ReqSummary`, `UcSummary`, `TskSummary`, `QaSummary`) now subclass a new shared `general/models/summary.py::DocSummary` base (`id`, `title`, `status`, `ref`). `AdrSummary` (`models/adr/v1/summary.py`) is a deliberate, permanent-for-now outlier: it stays field-identical to `DocSummary` but does not subclass it, because `models/adr` is a dependency-free base-library module (no `mcp` import, per `AGENTS.md`'s "models location" note), while `general/models` transitively requires the `mcp` extra through `general/__init__.py`'s unconditional import of `general.tools`/`general.resources`/`general.prompts`. Making `AdrSummary` subclass `DocSummary` would silently add a new `mcp` dependency to the base library. This is accepted as-is, with a known future redesign path: ADR is the only domain not yet using the generic markdown parser, and a future ADR-domain redesign is expected to revisit this asymmetry; a structural-equivalence test (`tests/general/models/test_summary.py`) keeps the two field sets in sync in the meantime.

This work was split out of feat-7-various-improvements Task 0.15 into its own feature folder, `feat-13-list-paging` (GitHub issue #13), and closes feat-7's REQ-002/ACC-002 (the pagination decision). It also advances, but does not fully close, feat-7's REQ-001/ACC-001 (the shared list-output contract): the contract is now shared and documented across all five domains, but ADR's summary shares it structurally rather than via inheritance, per the outlier above.

### Consequences

Good, because all five `list_<domain>` tools are now reliably invocable by agents with real pagination, matching the tool-first precedent already set for `get_req`.
Good, because the paged-result shape is proven and reused (from `asdste100`), not invented, keeping this project's own MCP servers consistent with each other.
Good, because scan/sort/skip-broken-file behavior is unchanged -- `total` still reflects only parseable documents, and each domain's own parse-failure exception tuple (e.g. ADR's `(AdrParseError, ValidationError)` vs. the other four's `(AssertionError, ValidationError)`) is preserved exactly.
Bad, because the five `<domain>_list` MCP resources are gone; any external client that was reading them as context-attachment resources (per the original rationale in ADR 7531106b-074b-4bd8-a83a-e433d01676e2) must switch to calling the `list_<domain>` tool instead.
Bad, because `AdrSummary` remains a visible, permanent-for-now asymmetry against the shared `DocSummary` base -- readers must know this is intentional (dependency-graph-driven), not an oversight, and that a future ADR-domain redesign may eventually resolve it.
Neutral, because this partially reverses the listing side of ADR 7531106b-074b-4bd8-a83a-e433d01676e2 (which added `specmgr://adr/list` as a resource) while leaving that ADR's by-id resource decision (`specmgr://adr/{id}`) untouched.

## More Information

Supersedes the listing-resource half of ADR 7531106b-074b-4bd8-a83a-e433d01676e2 ("Expose listing and by-id reads as MCP resources in addition to tools") for all five domains; that ADR's by-id resource decision is unaffected. Extends the tool-over-resource precedent of ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (`get_req`) to the listing case. Implemented in `.specmgr/feat/feat-13-list-paging/README.md` (split out of `feat-7-various-improvements` Task 0.15), which tracks the full per-domain task breakdown; see that feature folder's Decisions Made log for implementation-level detail not repeated here.
