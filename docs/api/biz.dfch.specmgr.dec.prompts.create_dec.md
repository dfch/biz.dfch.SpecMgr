# `biz.dfch.specmgr.dec.prompts.create_dec`

``@mcp.prompt()``: create_dec (Task 4.1).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Decision (DEC) document using the existing
``dec/tools/``/``dec/resources/`` surface (``list_dec``,
``specmgr://dec/template``/``specmgr://dec/example``,
``specmgr://dec/schema``, ``create_dec``, ``validate_dec``).

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_dec`` builds the entire DEC frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown. The body keeps the ADR's
general structure (context, drivers, considered options, outcome, related
artifacts, pros/cons, more information, updates) but is narrated through
DEC's own section names, with ``## Pros and Cons`` -- not ADR's
``## Pros and Cons of the Options`` -- as the options container.

Naming note: this prompt is named ``create_dec``, the same name as the
``@mcp.tool()`` in ``dec/tools/create_dec.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration (same precedent as
``gol.prompts.create_gol``/``req.prompts.create_req``).

This prompt only ever *narrates* the interview flow (checking for a
duplicate via ``list_dec``, building a ``TodoWrite`` list, eliciting the
mandatory context and outcome plus each optional section via the
``question`` tool, then calling ``create_dec``) -- it never calls
``TodoWrite``/``question``/``list_dec``/``create_dec`` itself, exactly like
every other prompt in this codebase (see ``tsk.prompts.implement_task``'s
own docstring for the same contract).

The actual instructional text lives in its own packaged data file,
``dec/data/dec_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the DEC
markdown headings it narrates to the LLM (e.g. ``# {title}``) without
those colliding with this module's own substitution.

## Functions

### `create_dec(topic: 'str') -> 'str'`

Return instructional text for drafting a new decision about ``topic``.

Parameters
----------
topic:
    Free-text description of the decision to be drafted -- becomes
    the seed for the document's title and context.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call. This function never calls
    ``TodoWrite``, ``question``, ``list_dec``, or ``create_dec``
    itself -- it only narrates that sequence for the LLM to carry out.

