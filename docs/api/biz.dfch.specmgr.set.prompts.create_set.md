# `biz.dfch.specmgr.set.prompts.create_set`

``@mcp.prompt()``: create_set (feat-173-req-iso29148-level-set Phase 180).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new set (SET) document using the
existing ``set/tools/``/``set/resources/`` surface (``list_set``,
``specmgr://set/template``/``specmgr://set/example``,
``get_set_schema``, ``create_set``, generic ``validate`` tool).

This prompt has no frontmatter-related
parameters to pre-fill: ``create_set`` builds the entire set frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown. The body narrates set's own
shape: a single ``# {title}`` H1, the mandatory opaque free-markdown
``## Description`` (any blocks allowed), and the mandatory ``## Items``
 flat bullet list (any mix of the 11 reference tags, at least one item) --
 there are no other sections.

Naming note: this prompt is named ``create_set``, the same name as the
``@mcp.tool()`` in ``set/tools/create_set.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration (same precedent as
``dec.prompts.create_dec``/``gol.prompts.create_gol``/
``vcr.prompts.create_vcr``).

This prompt only ever *narrates* the interview flow (checking for a
near-duplicate via ``list_set``, building a ``TodoWrite`` list, eliciting
the title, the ``## Description`` content, and the ``## Items`` list via
the ``question`` tool, then calling ``create_set``) -- it never calls
``TodoWrite``/``question``/``list_set``/``create_set`` itself, exactly
like every other prompt in this codebase (see
``tsk.prompts.implement_task``'s own docstring for the same contract).

The actual instructional text lives in its own packaged data file,
``set/data/set_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the set
markdown headings it narrates to the LLM (e.g. ``# {title}``) without
those colliding with this module's own substitution.

## Functions

### `create_set(topic: 'str') -> 'str'`

Return instructional text for drafting a new set document about ``topic``.

Parameters
----------
topic:
    Free-text description of the set document to be
    drafted -- becomes the seed for the document's title and body.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call. This function never calls
    ``TodoWrite``, ``question``, ``list_set``, or ``create_set``
    (the tool) itself -- it only narrates that sequence for the LLM
    to carry out.

