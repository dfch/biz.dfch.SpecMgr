# `biz.dfch.specmgr.adr.prompts.create_adr`

``@mcp.prompt()``: create_adr (.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md §11).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new MADR 4.0.0-based ADR using the existing
``adr/tools/`` surface (``create_adr``, ``option_create``,
``validate_adr``) plus the generic ``set_status`` tool in
``general/tools/`` (always called with ``type="adr"`` for an ADR).

Naming note: this prompt is named ``create_adr``, the same name as the
``@mcp.tool()`` in ``adr/tools/create_adr.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration.

The actual instructional text lives in its own packaged data file,
``adr/data/adr_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``/``$decision_makers``/...), not ``str.format``, precisely so
the instructions file itself is free to use plain, unescaped ``{...}``
braces for the MADR markdown headings it narrates to the LLM (e.g.
``# {title}``) without those colliding with this module's own
substitution.

## Functions

### `create_adr(topic: 'str', decision_makers: 'str | None' = None, consulted: 'str | None' = None, informed: 'str | None' = None) -> 'str'`

Return instructional text for drafting a new ADR about ``topic``.

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

