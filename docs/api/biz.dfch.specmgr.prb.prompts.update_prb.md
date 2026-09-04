# `biz.dfch.specmgr.prb.prompts.update_prb`

``@mcp.prompt()``: update_prb (Task 3.15).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Problem Statement (PRB) document by id, using
the existing ``prb/tools/`` surface (``get_prb``, generic ``validate`` tool) plus
the generic ``update``/``set_status`` tools in ``general/tools/`` (called
with ``type="prb"``; ``get_prb``'s ``raw=True`` parameter serves the
line-range flow's line numbers). There is no ``specmgr://prb/{id}``
resource to point at -- id-based reads always go through the ``get_prb``
tool only.

Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: PRB's lifecycle surface is deliberately small
-- a whole-body or line-range replace (the generic ``update`` tool with
``type="prb"``) plus a single, dedicated status-change path (the generic
``set_status`` tool with ``type="prb"``) -- mirroring
``tsk.prompts.update_task``/``qa.prompts.update_qa``.

This prompt only ever *narrates* an 9-step revision flow (reading current
state via `get_prb`, showing which of the 7 questions are already answered,
eliciting revisions via the `question` tool, re-synthesizing `Summary` and
`Gap`, optionally revising `Impact`/`Future State`/`References`/
`More Information`, then calling the generic `update` tool with
`type="prb"`, with the generic `set_status` tool with `type="prb"`
mentioned as a separate, optional follow-up) -- it never calls
``get_prb``/``question``/``update``/``set_status`` itself, exactly like
every other prompt in this codebase.

The actual instructional text lives in its own packaged data file,
``prb/data/prb_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for the PRB markdown it narrates to the LLM without those colliding with
this module's own substitution.

## Functions

### `update_prb(id: 'str', instructions: 'str | None' = None) -> 'str'`

Return instructional text for revising the problem statement identified by ``id``.

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
    ``get_prb``, ``question``, ``update``, or ``set_status`` itself
    -- it only narrates that sequence for the LLM to carry out.

