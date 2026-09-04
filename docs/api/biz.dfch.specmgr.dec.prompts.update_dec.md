# `biz.dfch.specmgr.dec.prompts.update_dec`

``@mcp.prompt()``: update_dec (Task 4.1).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Decision (DEC) document by id, using the
existing ``dec/tools/`` surface (``get_dec``, generic ``validate`` tool) plus the
generic ``update``/``set_status`` tools in ``general/tools/`` (called with
``type="dec"``; ``get_dec``'s ``raw=True`` parameter serves the line-range
flow's line numbers). There is no ``specmgr://dec/{id}`` resource to point
at -- id-based reads always go through the ``get_dec`` tool only (ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614).

Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: DEC's lifecycle surface is deliberately
small -- a whole-body or line-range replace (the generic ``update`` tool
with ``type="dec"``) plus a single, dedicated status-change path (the
generic ``set_status`` tool with ``type="dec"``) -- mirroring
``req.prompts.update_req``/``rsk.prompts.update_risk``.

Like ``req.prompts.update_req``/``rsk.prompts.update_risk`` (and unlike
``gol.prompts.update_gol``, which takes only the document ``id``), this
prompt also accepts an optional ``instructions`` argument pre-filled with
the requested change; when absent, the substituted fallback tells the LLM
to ask the user before making any change rather than guessing.

This prompt only ever *narrates* the revision flow (reading current state
via `get_dec`, showing which sections are present vs. empty, eliciting
revisions via the `question` tool, then calling the generic `update` tool
with `type="dec"`, with the generic `set_status` tool with `type="dec"`
mentioned as a separate, optional follow-up) -- it never calls
``get_dec``/``question``/``update``/``set_status`` itself, exactly like
every other prompt in this codebase.

The actual instructional text lives in its own packaged data file,
``dec/data/dec_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for the DEC markdown it narrates to the LLM without those colliding with
this module's own substitution.

## Functions

### `update_dec(id: 'str', instructions: 'str | None' = None) -> 'str'`

Return instructional text for revising the decision identified by ``id``.

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
    the MCP SDK), not itself a tool call. This function never calls
    ``get_dec``, ``question``, ``update``, or ``set_status`` itself
    -- it only narrates that sequence for the LLM to carry out.

