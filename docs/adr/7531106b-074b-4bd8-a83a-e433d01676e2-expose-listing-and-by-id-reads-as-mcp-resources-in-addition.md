---
status: accepted
decision-makers: dfch
id: 7531106b-074b-4bd8-a83a-e433d01676e2
version: 1.0.0
---

# Expose listing and by-id reads as MCP resources in addition to tools

## Context and Problem Statement

Clients need to retrieve ADR listings and individual ADRs. Two MCP mechanisms are available: @mcp.tool() (for explicit LLM invocation) and @mcp.resource() (for context attachment without a round-trip). Tools are callable by the LLM; resources are addressable URIs that a client can attach as context. The question is: should these reads be exposed only as tools, only as resources, or both?

## Decision Drivers

Different client use cases: LLM-driven explicit reads (tools), client-side context attachment without tool invocation (resources); consistency with sibling-project conventions (e.g., specmgr://version resource for version info).

## Considered Options

Tools only (list_adrs, get_adr as @mcp.tool()) vs. resources only (specmgr://adr/list, specmgr://adr/{id} as @mcp.resource()) vs. both.

## Decision Outcome

Expose both. Implement `list_adrs()` and `get_adr(id)` as MCP tools for explicit LLM-driven calls. Additionally, implement read-only MCP resources: `specmgr://adr/list` (returns the same listing) and `specmgr://adr/{id}` (template resource, RFC 6570 URI template, returns the same document). Both tools and resources use the same underlying id-resolution logic (fresh directory scan, no cache) and read the same current on-disk state. The tools are invoked when the LLM explicitly requests a read; the resources are used by clients that want to attach an ADR as context (e.g., in a message prompt) without tool overhead.

### Consequences

Flexibility: clients can use either mechanism depending on their flow (explicit LLM tool call vs. context-attachment pattern). Code reuse: both tools and resources call the same underlying I/O functions. Trade-off: a small amount of duplication in the interface layer (two ways to do the same read), but this is necessary to support both use cases.

## More Information

Tools are defined in adr/tools/get_adr.py and adr/tools/_list.py (actually option_list.py for options within an ADR, and adr/tools/ for the get_adr tool). Resources are defined in adr/resources/adr_list.py (@mcp.resource(uri='specmgr://adr/list')) and adr/resources/adr_get.py (@mcp.resource(uri='specmgr://adr/{id}')).
