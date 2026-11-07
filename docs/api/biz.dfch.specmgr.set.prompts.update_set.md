# `biz.dfch.specmgr.set.prompts.update_set`

``@mcp.prompt()``: update_set (feat-173-req-iso29148-level-set Phase 180).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing set (SET) document by id, using the
existing ``set/tools/`` surface (``get_set``, generic ``validate`` tool) plus
the generic ``update``/``edit``/``set_status`` tools in ``general/tools/``
(called with ``type="set"``; ``get_set``'s ``raw=True`` parameter serves the
line-range flow's line numbers, with ``numbered=True`` additionally printing
each line's 1-based body-line number, ready to feed into ``update``'s
``offset``). There is no ``specmgr://set/{id}`` resource to point at --
id-based reads always go through the ``get_set`` tool only (DEC
ddfb1109-422d-4507-8dbc-dc5e4bec9614).

There is no ``update_frontmatter``/
``option_*`` equivalent here: SET is dispatch-only from day one (DEC
36905d5b-8057-4294-8665-c7eed5534db0) -- a whole-body or line-range replace
(the generic ``update`` tool with ``type="set"``), a surgical exact-match
replacement (the generic ``edit`` tool with ``type="set"``), plus a single,
dedicated status-change path (the generic ``set_status`` tool with
``type="set"``) -- mirroring ``dec.prompts.update_dec``/
``req.prompts.update_req``/``vcr.prompts.update_vcr``.

Like ``dec.prompts.update_dec``/``req.prompts.update_req``/
``vcr.prompts.update_vcr`` (and unlike ``gol.prompts.update_gol``, which
takes only the document ``id``), this prompt also accepts an optional
``instructions`` argument pre-filled with the requested change; when
absent, the substituted fallback tells the LLM to ask the user before
making any change rather than guessing.

This prompt only ever *narrates* the revision flow (reading current state
via ``get_set``, showing what the document currently holds, eliciting
revisions via the ``question`` tool, then calling the generic ``update``
tool with ``type="set"``, the generic ``edit`` tool with ``type="set"``,
with the generic ``set_status`` tool with ``type="set"`` mentioned as a
separate, optional follow-up) -- it never calls
``get_set``/``question``/``update``/``edit``/``set_status`` itself, exactly
like every other prompt in this codebase.

The actual instructional text lives in its own packaged data file,
``set/data/set_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for the set markdown it narrates to the LLM without those colliding with
this module's own substitution.

## Functions

### `update_set(id: 'str', instructions: 'str | None' = None) -> 'str'`

Return instructional text for revising the set document identified by ``id``.

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
    ``get_set``, ``question``, ``update``, ``edit``, or
    ``set_status`` itself -- it only narrates that sequence for the
    LLM to carry out.

