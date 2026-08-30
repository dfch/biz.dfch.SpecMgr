# `biz.dfch.specmgr.feat.prompts.update_feat`

``@mcp.prompt()``: update_feat (Task 4.1).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Feature (FEAT) document by id, using the
existing ``feat/tools/`` surface (``get_feat``, ``validate_feat``) plus the
generic ``update``/``set_status`` tools in ``general/tools/`` (called with
``type="feat"``; ``get_feat``'s ``raw=True`` parameter serves the
line-range flow's line numbers). There is no ``specmgr://feat/{id}``
resource to point at -- id-based reads always go through the ``get_feat``
tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).

Unlike ADR's ``update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: FEAT's lifecycle surface is deliberately
small -- a whole-body or line-range replace (the generic ``update`` tool
with ``type="feat"``) plus a single, dedicated status-change path (the
generic ``set_status`` tool with ``type="feat"``) -- mirroring
``dec.prompts.update_dec``/``req.prompts.update_req``. There is no
``update_feat``/``set_status_feat`` tool of FEAT's own (REQ-006, ADR
36905d5b-8057-4294-8665-c7eed5534db0).

Like ``dec.prompts.update_dec``/``req.prompts.update_req`` (and unlike
``gol.prompts.update_gol``, which takes only the document ``id``), this
prompt also accepts an optional ``instructions`` argument pre-filled with
the requested change; when absent, the substituted fallback tells the LLM
to ask the user before making any change rather than guessing -- matching
the literal ``"(not given)"`` string that
``feat/data/feat_update_instructions.md`` itself checks for in its own
step 2 ("If 'Requested change' above says '(not given)', ask the user...").

This prompt only ever *narrates* the revision flow (reading current state
via ``get_feat``, showing which sections are present vs. empty, eliciting
revisions via the ``question`` tool, then calling the generic ``update``
tool with ``type="feat"``, with the generic ``set_status`` tool with
``type="feat"`` mentioned as a separate, optional follow-up) -- it never
calls ``get_feat``/``question``/``update``/``set_status`` itself, exactly
like every other prompt in this codebase.

The actual instructional text lives in its own packaged data file,
``feat/data/feat_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for the FEAT markdown it narrates to the LLM without those colliding with
this module's own substitution.

## Functions

### `update_feat(id: 'str', instructions: 'str | None' = None) -> 'str'`

Return instructional text for revising the feature identified by ``id``.

Parameters
----------
id:
    The existing document's ``feat-NNN-slug`` identifier (the
    containing folder's own name).
instructions:
    Free-text description of the requested change. When absent, the
    returned instructions tell the LLM to ask the user first rather
    than guessing.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call. This function never calls
    ``get_feat``, ``question``, ``update``, or ``set_status`` itself
    -- it only narrates that sequence for the LLM to carry out.

