# `biz.dfch.specmgr.txt.prompts.create_txt`

``@mcp.prompt()``: create_txt (feat-229-txt Phase 120).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new free-form text (TXT) document using the
existing ``txt/tools/``/``txt/resources/`` surface (``list_txt``,
``specmgr://txt/template``/``specmgr://txt/example``,
``get_txt_schema``, ``create_txt``, generic ``validate`` tool).

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_txt`` builds the entire TXT frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown. The body narrates TXT's own
shape: a single ``# {title}`` H1, the mandatory free-form opaque body
(any markdown, including H2 to H6 headings, ending at the first
top-level ``## Updates`` H2), and the mandatory newest-first
``## Updates`` log -- there are no optional sections.

Naming note: this prompt is named ``create_txt``, the same name as the
``@mcp.tool()`` in ``txt/tools/create_txt.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration (same precedent as
``dec.prompts.create_dec``/``gol.prompts.create_gol``/
``vcr.prompts.create_vcr``).

This prompt only ever *narrates* the interview flow (checking for a
near-duplicate via ``list_txt``, building a ``TodoWrite`` list, eliciting
the title, body content, and ``## Updates`` entry via the ``question``
tool, then calling ``create_txt``) -- it never calls
``TodoWrite``/``question``/``list_txt``/``create_txt`` itself, exactly
like every other prompt in this codebase (see
``tsk.prompts.implement_task``'s own docstring for the same contract).

The actual instructional text lives in its own packaged data file,
``txt/data/txt_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the TXT
markdown headings it narrates to the LLM (e.g. ``# {title}``) without
those colliding with this module's own substitution.

## Functions

### `create_txt(topic: 'str') -> 'str'`

Return instructional text for drafting a new free-form text document about ``topic``.

Parameters
----------
topic:
    Free-text description of the free-form text document to be
    drafted -- becomes the seed for the document's title and body.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call. This function never calls
    ``TodoWrite``, ``question``, ``list_txt``, or ``create_txt``
    (the tool) itself -- it only narrates that sequence for the LLM
    to carry out.

