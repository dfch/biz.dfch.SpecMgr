# `biz.dfch.specmgr.adr.tools.validate_adr`

``@mcp.tool()`` wrapper: validate_adr (plan §7, §8, §9a, §10 item 4).

Thin file-I/O/id-lookup adapter -- re-reads and re-parses the current
on-disk state on every call; there is no in-memory cache of a parsed
:class:`Adr` (plan §7, §9a): the ``.md`` file itself is always the source
of truth.

## Functions

### `validate_adr(id: 'str') -> 'bool'`

Validate the ADR identified by ``id``.

"Validate" is simply letting :class:`Adr`/:class:`AdrBody`/
:class:`AdrFrontmatter`'s own Pydantic validators run during parsing
(plan §7): there is no separate validation pass here. Successfully
constructing the :class:`Adr` *is* the validation, so this function
only ever returns ``True`` -- it never returns ``False``. Any parse or
validation failure instead propagates as
``AdrParseError``/``pydantic.ValidationError`` (not caught or wrapped
here), so the MCP layer reports it naturally as a tool error, giving
the LLM the underlying message to self-correct from.

Parameters
----------
id:
    The document's specmgr-assigned identifier.

Returns
-------
bool
    Always ``True`` on success.

