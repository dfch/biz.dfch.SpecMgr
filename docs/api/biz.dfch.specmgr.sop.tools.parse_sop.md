# `biz.dfch.specmgr.sop.tools.parse_sop`

``@mcp.tool()`` wrapper: parse_sop (Task 2.2).

Reads a SOP markdown file from disk and parses it into a structured
:class:`SopDocument`, mirroring ``dec.tools.parse_dec``'s own pattern --
read path → parse via free-function returning typed document model. Errors
(propagated uncaught from the parser's ``AssertionError``/
``pydantic.ValidationError`` or raised by ``Path.read_text()``) surface as
MCP tool errors to the caller.

## Functions

### `parse_sop(path: 'str') -> 'SopDocument'`

Parse the SOP file at ``path`` into a :class:`SopDocument`.

Reads the file from disk, then parses and validates its content. "Parse"
here also means "validate": letting :class:`Sop` /
:class:`SopFrontmatter` / :class:`SopDocument`'s own Pydantic validators
run during parsing is the only validation pass there is -- there is
no separate validation step. Any structural problem (unrecognized/misplaced
heading, list the schema doesn't expect) or field/cross-field validation
failure is not caught or wrapped here: it propagates naturally as
``AssertionError``/``pydantic.ValidationError``, so the MCP layer reports
it as a tool error with the underlying message, giving the caller something
concrete to self-correct from.  Similarly, file-access errors migrate as
``FileNotFoundError``/``PermissionError``/``OSError``.

Parameters
----------
path:
    The filesystem path to the ``.md`` file to parse (absolute or
    relative to the current working directory).

Returns
-------
SopDocument
    The parsed, validated document.

