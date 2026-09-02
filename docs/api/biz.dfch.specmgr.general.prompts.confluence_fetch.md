# `biz.dfch.specmgr.general.prompts.confluence_fetch`

``@mcp.prompt()``: confluence_fetch (feat-50-confluence Phase 8, REQ-013/ACC-012).

Returns instructional text -- not itself a tool call -- that tells an LLM
to call the ``confluence_fetch`` ``@mcp.tool()`` (``general/tools/
confluence_fetch.py``) with the same parameters given here, so a user can
trigger a Confluence page/attachment download with a single, simple
instruction instead of needing to know the underlying tool's exact name/
parameters.

Naming note: this prompt is named ``confluence_fetch``, the same name as
the ``@mcp.tool()`` in ``general/tools/confluence_fetch.py``. This is not
a collision -- the MCP protocol keeps prompts and tools in separate
registries (``prompts/list`` vs. ``tools/list``) -- but is called out here
explicitly for the same reason as ``general.prompts.confluence_update``'s
own docstring note (precedent: ``dec.prompts.create_dec``/
``gol.prompts.create_gol``/``req.prompts.create_req``).

Same thin, single-tool-call, non-calling contract as
``general.prompts.confluence_update``: this prompt never fetches anything
itself, it only narrates the one tool call for the LLM to carry out.

The actual instructional text lives in its own packaged data file,
``general/data/general_confluence_fetch_instructions.md``, read fresh on
every call via ``general.tools._packaged_data.read_packaged_text``.
Placeholders use ``string.Template`` (``$url``/``$destination_path``), not
``str.format``. ``destination_path`` is optional on the underlying tool
(only needed for a binary/non-text fetch, per
``ConfluenceDestinationPathRequiredError``); when it is not given here, a
literal explanatory placeholder string is substituted instead of a blank,
mirroring ``general.prompts.compact_history``'s own
``cutoff_hint or "(not given -- ...)"`` pattern.

## Functions

### `confluence_fetch(url: 'str', destination_path: 'str | None' = None) -> 'str'`

Return instructional text for fetching ``url`` via the ``confluence_fetch`` tool.

Parameters
----------
url:
    The same value the ``confluence_fetch`` tool accepts: a URL that
    case-insensitively matches the configured base URL.
destination_path:
    The same value the ``confluence_fetch`` tool accepts: the
    filesystem path to write non-text/binary response content to.
    Only required when the fetched content turns out to be binary
    (e.g. an image); omit it for a normal page/text fetch.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call. This function never calls
    the ``confluence_fetch`` tool itself -- it only narrates that one
    call for the LLM to carry out.

