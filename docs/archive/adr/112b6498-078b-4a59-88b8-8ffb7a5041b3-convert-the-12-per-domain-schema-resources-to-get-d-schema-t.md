---
status: accepted
date: '2026-10-17'
decision-makers: dfch
id: 112b6498-078b-4a59-88b8-8ffb7a5041b3
version: 1.0.0
---

# Convert the 12 per-domain schema resources to get_<d>_schema tools

## Context and Problem Statement

Every whole-body domain (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs) exposes its generated JSON Schema (2020-12 dialect) as an MCP resource at `specmgr://<d>/schema` (`<d>/resources/<d>_schema.py`), read from the packaged data copy `<d>/data/<d>_schema.json` (kept in sync with `docs/<d>_schema.json` by the pre-commit `specmgr-schema-<d>-package` hooks and the CI schema-drift steps).

feat-128's round-trip investigation (8 controlled fresh-agent runs, `root-cause-analysis.md`) ranked the root causes of agents skipping the schema, with discoverability first: the schema is a resource, not a tool; nothing in the agent's always-in-context tool surface (94 published tool descriptions on 0.34.0) names it; and 0/4 no-prompt runs made any resource-layer call at all. Perceived cost was second: the 2-hop resource route (discover via `list_resources`, then read) costs 2 round-trips and 12-53 KB per fetch.

feat-189-reduce-agent-round-trips (GitHub issue #189, this feature) demoted the schema to constraint discovery in Phase 100 (the create/update instructions now fetch it only when structurally uncertain or when resolving a validation error, never as a mandatory pre-authoring step). Its Phase 120 (P2) metadata-only enrichment -- emitting the domains' closed sets as `json_schema_extra` `enum`/`pattern` metadata -- falsifies the zero-constraint rejection argument that originally kept a 1-hop `get_<d>_schema` tool off the table: the enriched schema carries machine-readable constraints an agent can act on, so the schema must be cheap and findable when the designated fallback is used.

Question: how should the generated schema be exposed on the MCP surface -- keep the 12 resources (with usage-oriented descriptions), convert them to 12 tools, or do nothing?

## Decision Drivers

- Discoverability on the always-in-context tool surface (the RCA's #1 root cause): the schema's own metadata must be visible without reaching the resource layer.
- Eliminate the 2-hop resource route (the RCA's #2 root cause): one tool call instead of discover-then-read.
- Consistency with ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (id-based reads as tools) and ADR ec9f5262-9912-49d0-903f-fcfb54f28c13 (listing as paged tools): the schema resource is the last per-domain authoring resource, and its conversion makes the per-domain authoring surface fully tool-based.
- Collapse plan items C6 (pointer clauses) and C7 (usage-oriented rewording) into one surface: the `get_<d>_schema` tool description carries both, instead of C7 living in a resource description agents never see.
- Zero content change: the same packaged file and the same provenance sentence; the fetch stays demoted (never a mandatory pre-authoring fetch), so the feature's T1-T3 measurable targets are unaffected.

## Considered Options

- Option 1: Convert to 12 `get_<d>_schema` tools and remove the 12 `specmgr://<domain>/schema` resources (chosen).
- Option 2: Keep the 12 resources, rewording their descriptions to be usage-oriented only (the plan's original C7; superseded by C17 -- it cannot fix tool-surface discoverability).
- Option 3: Do nothing (the baseline the round-trip evidence was measured against).

## Decision Outcome

Chosen option: "Option 1: Convert to 12 `get_<d>_schema` tools and remove the 12 `specmgr://<domain>/schema` resources", for the reasons in the Decision Drivers above: it is the only option that addresses the RCA's #1 root cause (discoverability) at all, and it is the direct continuation of the ddfb1109/ec9f5262 tool-over-resource precedent applied to the last per-domain authoring resource.

The decision: 12 new `@mcp.tool()` `get_<d>_schema` tools -- one per whole-body domain (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs) -- replace the 12 `specmgr://<domain>/schema` resources, whose resource modules are deleted. Each tool mirrors the sibling `get_<d>_template`/`get_<d>_example` tool shape file-for-file (no parameters; reads the packaged, build-guaranteed file via `general.tools._packaged_data.read_packaged_text("<d>", "schema", "json")`; a missing packaged file propagates `FileNotFoundError` uncaught, the codebase's let-it-raise convention).

Return shape (micro-decision D1, settled with the orchestrator): each `get_<d>_schema` tool returns the schema document as RAW JSON TEXT (str), byte-identical to the packaged `data/<d>_schema.json` and -- kept in sync by the pre-commit `specmgr-schema-<d>-package` hooks -- to `docs/<d>_schema.json`. This deliberately differs from the removed resource's parsed-dict return: it follows the raw-text convention of the sibling `get_<d>_template`/`get_<d>_example` tools, makes the content-identity test a literal byte comparison, and the wire content the agent sees is the same JSON document either way.

Usage-oriented descriptions (absorbing C7): each tool's description -- agent-facing and always in context -- carries (a) WHEN to fetch: constraint discovery, structural questions, unresolved validation errors, and never a mandatory pre-authoring fetch; (b) WHAT it is: the domain's generated JSON Schema (2020-12 dialect), the machine-readable / parsed-JSON view of the structure, not the markdown view, with the domain's `get_<d>_template` named as the authoring starting point; and (c) the provenance sentence kept verbatim in substance: generated by `specmgr schema`, kept current by a pre-commit hook/CI step, includes a `$comment` schema-layout version marker.

Recorded rationale lines:

- The plan's P2 enrichment (Phase 120, C13/C14) falsifies the zero-constraint rejection argument: the enriched schema carries `enum`/`pattern` metadata for the domains' closed sets, so the schema is worth being cheaply findable.
- The RCA's #1 root cause is discoverability in the always-in-context tool surface: after this conversion, 12 terse tool descriptions name the schema and its when/what, instead of a resource layer 0/4 no-prompt runs ever reached.
- The 2-hop resource route is eliminated: constraint discovery becomes one tool call.
- C6/C7 collapse into one surface: the `get_<d>_schema` tool description carries both the non-prescriptive pointer clause (C6) and the usage-oriented wording (C7); plan C7 (resource-description rewording only) is superseded.
- Tool-count delta, recorded as measured at this ADR's writing time against the current worktree surface: the published 0.34.0 probe count of 94 tools is stale; the worktree already carries 103 `@mcp.tool(` decorators (verified by line-anchored grep over `src/` at writing time) plus 49 `@mcp.resource(` registrations. The conversion adds 12 tools and removes 12 resources, so the expected figures are 103 -> 115 tools and 49 -> 37 resources, to be confirmed by the Phase 130 Task 130.100 live-surface probe.

Lineage: ADR 7531106b-074b-4bd8-a83a-e433d01676e2 ("Expose listing and by-id reads as MCP resources in addition to tools") is the mechanism's ancestor (listing/by-id reads as resources in addition to tools); the 12 per-domain schema resources were never within that ADR's decision scope (it covers the ADR domain's own `specmgr://adr/list`/`specmgr://adr/{id}` pair only), and this ADR's tool-only direction continues ADR ec9f5262-9912-49d0-903f-fcfb54f28c13's partial reversal of it (which retired the listing side of 7531106b while leaving its by-id resource side untouched).

### Consequences

Good, because constraint discovery becomes one hop and discoverable: the schema is named in 12 always-in-context tool descriptions with a when/what, addressing the RCA's #1 and #2 root causes together, and the per-domain authoring surface (template/example/schema) becomes fully tool-based, completing the ddfb1109/ec9f5262 precedent for the last per-domain authoring resource.

Good, because C6 and C7 collapse into one surface: the pointer clause and the usage-oriented wording both live in the tool description, so there is one place to keep them consistent instead of a description agents never see.

Good, because the content is unchanged and the change is test-pinned: each tool's output is byte-identical to `docs/<d>_schema.json` and to the packaged `data/<d>_schema.json` (the pre-commit `specmgr-schema-<d>-package` hooks keep the two in sync), verified by per-domain content-identity tests plus one central registration test pinning the 115-tool/37-resource totals.

Bad, because the 12 `specmgr://<domain>/schema` URIs are gone: any client that attached a schema as a context resource must switch to calling the `get_<d>_schema` tool -- the same kind of break ddfb1109/ec9f5262 already accepted for by-id and listing reads.

Bad, because the return shape changes from a parsed JSON dict to raw JSON text: a direct-Python caller of the removed resource function had to `json.loads` nothing before and now receives a string (the MCP wire content is the same JSON document either way, and no such caller exists inside this repo -- the removed resource's only consumers were agents).

Neutral, because the registration surfaces are updated in the same change: `server.py`'s module docstring, `AGENTS.md`'s per-domain bullets, `docs/MCP.md`, `docs/api/`, the 12 `<d>/tools/__init__.py` and 12 `<d>/resources/__init__.py` module docstrings, the 24 create/update instruction files' conditional schema sentence (now naming the tool), and the pre-commit/CI hook descriptions. Vulture and packaging are unaffected: `data/<d>_schema.json` was already shipped package data for every one of the 12 domains, and the new tool functions are re-exported via each `<d>/tools/__init__.py`'s `__all__`.

### Confirmation

The decision is made and implemented in the same phase (feat-189-reduce-agent-round-trips Phase 105, Tasks 105.100/105.110); `status: accepted` reflects that consensus-plus-implementation, consistent with the recent house ADRs that land as accepted.

## Pros and Cons of the Options

### Option 1: Convert to 12 get_<d>_schema tools and remove the 12 schema resources (chosen)

#### Pros

- Fixes the RCA's #1 root cause: the schema is named in the always-in-context tool surface (12 terse descriptions) instead of the resource layer 0/4 no-prompt runs reached.
- Eliminates the 2-hop route (RCA's #2 root cause): constraint discovery is one tool call.
- Makes the per-domain authoring surface fully tool-based, completing the ddfb1109/ec9f5262 precedent for the last per-domain authoring resource.
- Collapses C6/C7 into one surface (the tool description carries the pointer clause plus the usage-oriented wording).
- Content-identity tests pin each tool's output byte-identical to `docs/<d>_schema.json` and the packaged copy.

#### Cons

- Adds 12 always-in-context tool descriptions (103 -> 115 tools at this ADR's writing time) -- the acknowledged cost, mitigated by terse, one-sentence-group descriptions.
- The 12 `specmgr://<domain>/schema` URIs disappear; context-attachment clients must switch to the tool.
- The return shape changes from a parsed dict to raw JSON text (the wire content is the same JSON document either way).

### Option 2: Keep the 12 resources, rewording their descriptions usage-oriented only (the plan's original C7; superseded)

#### Pros

- Zero tool-surface growth (no 12 new always-in-context descriptions).
- Smallest diff: 12 description edits, no code removal.

#### Cons

- Cannot fix discoverability: a resource's own title/description is only seen if the agent reaches the resource layer at all (0/4 no-prompt runs did) -- the RCA's #1 root cause stays open.
- The 2-hop route (the RCA's #2 root cause) remains.
- The per-domain authoring surface stays resource-based, diverging from the ddfb1109/ec9f5262 tool-first precedent.

Superseded by Option 1 (plan C17).

### Option 3: Do nothing (the baseline)

#### Pros

- No change at all; the Phase 100 evidence already shows no-prompt agents succeed with zero schema fetches.

#### Cons

- Leaves the designated constraint-discovery fallback path 2-hop and undiscoverable -- exactly the shape the T2 prompt-condition evidence measured (one schema fetch per prompt run, on the 2-hop resource route).
- The Phase 120 (P2) enriched schema would land in a surface agents still cannot find, wasting the enrichment's discoverability payoff.

This is the baseline the round-trip evidence was measured against.

## More Information

Implemented in feat-189-reduce-agent-round-trips Phase 105 (`.specmgr/feat/feat-189-reduce-agent-round-trips/README.md`, Tasks 105.100/105.110; GitHub issue #189). The round-trip evidence it acts on lives in feat-128-schema-not-used (`root-cause-analysis.md`, `round-trip-reduction-plan.md`'s C17 row); the Phase 130 re-run (Task 130.100's live-surface probe) confirms the 115-tool/37-resource totals measured at this ADR's writing time.
