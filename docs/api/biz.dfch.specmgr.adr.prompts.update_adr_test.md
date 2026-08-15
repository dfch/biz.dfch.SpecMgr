# `biz.dfch.specmgr.adr.prompts.update_adr_test`

``@mcp.prompt()``: update_adr_test (.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md §11).

Experimental, strictly step-gated variant of ``update_adr`` (see
``adr/prompts/update_adr.py``), kept as a *separate* prompt -- not a
replacement -- so the two can be registered side by side and compared:
the same underlying read-first/map-to-tool/validate-last flow, but
rewritten as a series of hard numbered gates ("do not proceed to gate
N+1 until gate N's exit condition is met", "never fabricate a value to
pass a gate") instead of the softer step-by-step narration used by
``update_adr``. This lets a caller switch between ``update_adr`` and
``update_adr_test`` for the same revision and observe whether the
stricter phrasing measurably improves compliance (e.g. always reading
current state first, never guessing at an unspecified change) -- see
the conversation in .specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md §11 for the rationale.

## Functions

### `update_adr_test(id: 'str', instructions: 'str | None' = None) -> 'str'`

Return step-gated instructional text for revising the ADR identified by ``id``.

See ``update_adr`` (``adr/prompts/update_adr.py``) for the non-gated
baseline this variant is meant to be compared against; the parameters
and returned-value contract are identical.

Parameters
----------
id:
    The existing document's specmgr-assigned identifier.
instructions:
    Free-text description of the requested change. When absent, the
    returned instructions tell the LLM to ask the user first rather
    than guessing.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call.

