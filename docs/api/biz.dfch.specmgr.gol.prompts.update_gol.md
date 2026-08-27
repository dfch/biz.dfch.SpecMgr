# `biz.dfch.specmgr.gol.prompts.update_gol`

``@mcp.prompt()``: update_gol (Task 3.15).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Goal (GOL) document by id, using the existing
``gol/tools/`` surface (``get_gol``, ``validate_gol``) plus the generic
``update``/``set_status`` tools in ``general/tools/`` (called with
``type="gol"``; ``get_gol``'s ``raw=True`` parameter serves the line-range
flow's line numbers). There is no ``specmgr://gol/{id}`` resource to point at
-- id-based reads always go through the ``get_gol`` tool only.

Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: GOL's lifecycle surface is deliberately small
-- a whole-body or line-range replace (the generic ``update`` tool with
``type="gol"``) plus a single, dedicated status-change path (the generic
``set_status`` tool with ``type="gol"``) -- mirroring
``req.prompts.update_req``/``prb.prompts.update_prb``.

Unlike ``req.prompts.update_req``/``prb.prompts.update_prb`` (which also
accept an optional ``instructions`` argument pre-filled with the requested
change), this prompt takes only the document ``id``: which sections to
add or revise is not pre-given but discovered during the narrated
interview itself (step 2 of the instructions file shows the user which
sections are present vs. empty and asks via the ``question`` tool which
ones to change).

This prompt only ever *narrates* the revision flow (reading current state
via `get_gol`, showing which sections are present vs. empty, eliciting
revisions via the `question` tool, then calling the generic `update` tool
with `type="gol"`, with the generic `set_status` tool with `type="gol"`
mentioned as a separate, optional follow-up) -- it never calls
``get_gol``/``question``/``update``/``set_status`` itself, exactly like
every other prompt in this codebase.

The actual instructional text lives in its own packaged data file,
``gol/data/gol_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``), not ``str.format``, precisely so the instructions file itself
is free to use plain, unescaped ``{...}`` braces for the GOL markdown it
narrates to the LLM without those colliding with this module's own
substitution.

## Functions

### `update_gol(id: 'str') -> 'str'`

Return instructional text for revising the goal identified by ``id``.

Parameters
----------
id:
    The existing document's specmgr-assigned identifier.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call. This function never calls
    ``get_gol``, ``question``, ``update``, or ``set_status`` itself
    -- it only narrates that sequence for the LLM to carry out.

