---
status: accepted
date: '2026-08-15'
decision-makers: OpenCode agent + user decision
id: ddfb1109-422d-4507-8dbc-dc5e4bec9614
version: 1.0.0
---

# Expose id-based REQ document reads as a tool (get_req), not a resource

## Context and Problem Statement

feat-6-requirement-artifact Task 3.17 deliberately exposed id-based single-document reads for the REQ domain only as an MCP resource (`specmgr://req/{id}`, `req/resources/req_get.py`), explicitly superseding an earlier-considered `get_req` tool -- the stated rationale was "id-based single-document read is a resource only, everything else in this surface is a tool". This mirrored the *shape* of the ADR domain's `specmgr://adr/{id}` resource, except ADR also ships a `get_adr` tool alongside it, so the two domains were never actually symmetric.

In practice, LLM/agent clients calling this MCP server fail to reliably invoke `specmgr://req/{id}` to retrieve a requirement by id -- resources are a much less-used affordance for on-demand, parameterized lookups than tools are, in current agent tool-use patterns. This defeats the purpose of exposing the lookup at all: the calling model either skips the read entirely, or falls back to less reliable paths (e.g. reading `specmgr://req/list` and guessing, or trying to read the underlying `.md` file directly off disk). This was raised as feat-7-various-improvements Task 0.9, which also asks whether the same reasoning should retroactively apply to the already-shipped `get_adr` tool / `specmgr://adr/{id}` resource pair.

## Decision Drivers

- Reliability: in observed practice, LLM agents invoke tools far more reliably than resources for on-demand, parameterized (id-based) data retrieval.
- Consistency across document domains (`adr`, `req`, and future `uc`/`ac`) for the same conceptual operation ("read one document by id").
- Avoid permanently maintaining two parallel code paths (tool and resource) for the same read when the resource path is rarely, if ever, actually exercised by callers.
- Minimize churn to the already-shipped, working ADR domain surface, which has no reported reliability problem to date.

## Considered Options

- Option 1: Add `get_req` tool, keep `specmgr://req/{id}` resource (tool and resource coexist, mirroring how ADR already works)
- Option 2: Add `get_req` tool, remove `specmgr://req/{id}` resource entirely (REQ becomes tool-only for id-based reads)
- Option 3: Do nothing -- keep REQ resource-only, reaffirming feat-6 Task 3.17's original decision

## Decision Outcome

Chosen option: "Option 2: Add `get_req` tool, remove `specmgr://req/{id}` resource entirely", because the resource has demonstrated the exact reliability problem this ADR describes, and keeping a rarely-invoked resource around after adding the tool would only add maintenance surface (two code paths, two test suites, two docstring entries) for a path that isn't actually helping callers.

This ADR explicitly does **not** extend the change to the ADR domain: `specmgr://adr/{id}` (`adr_get`) stays coexisting with the already-shipped `get_adr` tool, unchanged. This is a deliberate, accepted cross-domain divergence -- not an oversight -- recorded here so a future reader does not assume the two domains were meant to be symmetric. Any future document domain (`uc`/`get_uc`, `ac`/`get_ac`, ...) should follow the newer REQ precedent (tool-only for id-based reads) rather than the older ADR precedent, unless a specific reason to add a resource counterpart is identified at that time.

### Consequences

Good, because REQ's id-based read becomes reliably invocable by agents via a normal tool call, matching every other REQ lifecycle operation (`create_req`, `update_req`, `set_status_req`, `validate_req`), which are already tools.
Good, because it establishes a clear default for future document domains: id-based single-document read is a tool first; a resource counterpart is only added if a concrete need for non-tool-mediated context retrieval emerges.
Bad, because the ADR and REQ domains now visibly diverge in their tool/resource surface for the same conceptual operation (ADR keeps both `get_adr` tool and `adr_get` resource; REQ has only `get_req`) -- readers of both domains side by side must know this is intentional, not a bug, which is why it is written down here.
Neutral, because this reverses part of feat-6 Task 3.17's original design without reopening feat-6 itself -- feat-6's README is annotated with a pointer to this ADR rather than rewritten.

## More Information

Supersedes the `specmgr://req/{id}`-only decision recorded in feat-6-requirement-artifact/README.md Task 3.17. Tracked as feat-7-various-improvements Task 0.9 (sub-tasks 0.9.1-0.9.13).
