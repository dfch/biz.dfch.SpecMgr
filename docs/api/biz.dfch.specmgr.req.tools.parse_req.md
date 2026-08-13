# `biz.dfch.specmgr.req.tools.parse_req`

``@mcp.tool()`` wrapper: parse_req.

Reads a requirement markdown file from disk and parses it into a structured
:class:`ReqDocument`, mirroring ``uc.tools.parse_uc``'s own pattern -- read
path → parse via free-function returning typed document model.  Errors
(propagated uncaught from the parser's ``AssertionError``/
``pydantic.ValidationError`` or raised by ``Path.read_text()``) surface as
MCP tool errors to the caller.

## Functions

### `parse_req(path: 'str') -> 'ReqDocument'`

Parse the requirement file at ``path`` into a :class:`ReqDocument`.

Reads the file from disk, then parses and validates its content. "Parse"
here also means "validate": letting :class:`Requirement` /
:class:`ReqFrontmatter` / :class:`ReqDocument`'s own Pydantic validators
run during parsing is the only validation pass there is, exactly like
``adr.tools.validate_adr``'s own docstring describes for ADRs -- there is
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
ReqDocument
    The parsed, validated document.

