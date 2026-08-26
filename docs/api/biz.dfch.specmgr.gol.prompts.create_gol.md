# `biz.dfch.specmgr.gol.prompts.create_gol`

``@mcp.prompt()``: create_gol (Task 3.14).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Goal (GOL) document using the existing
``gol/tools/``/``gol/resources/`` surface (``list_gol``,
``specmgr://gol/template``/``specmgr://gol/example``, ``specmgr://gol/schema``,
``create_gol``, ``validate_gol``).

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_gol`` builds the entire GOL frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown.

Naming note: this prompt is named ``create_gol``, the same name as the
``@mcp.tool()`` in ``gol/tools/create_gol.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration (same precedent as
``req.prompts.create_req``/``prb.prompts.create_prb``).

This prompt only ever *narrates* the interview flow (checking for a
duplicate via `list_gol`, building a ``TodoWrite`` list, eliciting the goal
statement and source plus each optional section via the ``question`` tool,
then calling `create_gol`) -- it never calls ``TodoWrite``/``question``/
``list_gol``/``create_gol`` itself, exactly like every other prompt in this
codebase (see ``tsk.prompts.implement_task``'s own docstring for the same
contract).

The actual instructional text lives in its own packaged data file,
``gol/data/gol_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the GOL
markdown headings it narrates to the LLM (e.g. ``# {title}``) without
those colliding with this module's own substitution.

## Functions

### `create_gol(topic: 'str') -> 'str'`

Return instructional text for drafting a new goal about ``topic``.

Parameters
----------
topic:
    Free-text description of the goal to be drafted -- becomes
    the seed for the document's title and goal statement.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call. This function never calls
    ``TodoWrite``, ``question``, ``list_gol``, or ``create_gol``
    itself -- it only narrates that sequence for the LLM to carry out.

