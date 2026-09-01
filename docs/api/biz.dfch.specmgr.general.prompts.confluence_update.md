# `biz.dfch.specmgr.general.prompts.confluence_update`

``@mcp.prompt()``: confluence_update (feat-50-confluence Phase 8, REQ-012/ACC-011).

Returns instructional text -- not itself a tool call -- that tells an LLM
to call the ``confluence_update`` ``@mcp.tool()`` (``general/tools/
confluence_update.py``) with the same two parameters given here, so a user
can trigger a Confluence page upload with a single, simple instruction
instead of needing to know the underlying tool's exact name/parameters.

Naming note: this prompt is named ``confluence_update``, the same name as
the ``@mcp.tool()`` in ``general/tools/confluence_update.py``. This is not
a collision -- the MCP protocol keeps prompts and tools in separate
registries (``prompts/list`` vs. ``tools/list``) -- but is called out here
explicitly so the two are not mistaken for the same registration, same
precedent as ``dec.prompts.create_dec``/``gol.prompts.create_gol``/
``req.prompts.create_req``.

Unlike the multi-step, ``TodoWrite``/``question``-tool-driven interview
prompts elsewhere in this codebase (e.g. ``dec.prompts.create_dec``), this
is a thin, single-tool-call prompt: it never reads the Markdown file,
never renders anything, and never calls ``confluence_update`` itself --
exactly like every other prompt in this codebase, it only narrates the one
tool call for the LLM to carry out and asks it to report back the
`version`/`failed_images` values the tool itself returns.

The actual instructional text lives in its own packaged data file,
``general/data/general_confluence_update_instructions.md``, read fresh on
every call via ``general.tools._packaged_data.read_packaged_text``.
Placeholders use ``string.Template`` (``$page_url_or_id``/
``$markdown_file_path``), not ``str.format``, so the packaged file is free
to use plain, unescaped ``{...}`` braces of its own.

## Functions

### `confluence_update(page_url_or_id: 'str', markdown_file_path: 'str') -> 'str'`

Return instructional text for uploading ``markdown_file_path`` to ``page_url_or_id``.

Parameters
----------
page_url_or_id:
    The same value the ``confluence_update`` tool accepts: a bare
    numeric page id, a browsable Confluence page URL, or a REST
    content URL.
markdown_file_path:
    The same value the ``confluence_update`` tool accepts: the local
    filesystem path to the Markdown file to render and push as the
    page's new body.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call. This function never calls
    the ``confluence_update`` tool itself -- it only narrates that one
    call for the LLM to carry out.

