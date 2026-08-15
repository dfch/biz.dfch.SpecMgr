# `biz.dfch.specmgr.adr.prompts.create_adr_test`

``@mcp.prompt()``: create_adr_test (.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md §11).

Experimental, strictly step-gated variant of ``create_adr`` (see
``adr/prompts/create_adr.py``), kept as a *separate* prompt -- not a
replacement -- so the two can be registered side by side and compared: the
same underlying MADR structure and ``adr/tools/`` sequence, but rewritten
as a series of hard numbered gates ("do not proceed to gate N+1 until gate
N's exit condition is met", "never fabricate a value to pass a gate")
instead of the softer step-by-step narration used by ``create_adr``. This
lets a caller switch between ``create_adr`` and ``create_adr_test`` for
the same topic and observe whether the stricter phrasing measurably
improves compliance (e.g. fewer fabricated mandatory-field values, fewer
skipped duplicate checks) -- see the conversation in
.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md §11 for the rationale.

Naming note: like ``create_adr`` itself, this prompt's name does not
collide with any ``@mcp.tool()`` -- ``adr/tools/`` has no ``create_adr_test``
tool; the underlying tool sequence driven by this prompt is unchanged
(``create_adr``, ``option_create``, ``set_status``, ``validate_adr``).

## Functions

### `create_adr_test(topic: 'str', decision_makers: 'str | None' = None, consulted: 'str | None' = None, informed: 'str | None' = None) -> 'str'`

Return step-gated instructional text for drafting a new ADR about ``topic``.

See ``create_adr`` (``adr/prompts/create_adr.py``) for the non-gated
baseline this variant is meant to be compared against; the parameters
and returned-value contract are identical.

Parameters
----------
topic:
    Free-text description of the decision to be made -- becomes the
    seed for ``title``/``context_and_problem_statement``.
decision_makers:
    Pre-known ``decision-makers`` frontmatter value, if any; otherwise
    the returned instructions tell the LLM to ask the user.
consulted:
    Pre-known ``consulted`` frontmatter value, if any.
informed:
    Pre-known ``informed`` frontmatter value, if any.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call.

