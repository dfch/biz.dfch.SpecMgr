# `biz.dfch.specmgr.rsk.tools.parse_rsk`

``@mcp.tool()`` wrapper: parse_rsk (Task 3.2).

Reads a risk markdown file from disk and parses it into a structured
:class:`RskDocument`, mirroring ``tsk.tools.parse_tsk``'s own pattern -- read
path -> parse via free-function returning typed document model. Errors
(propagated uncaught from the parser's ``AssertionError``/
``pydantic.ValidationError`` or raised by ``Path.read_text()``) surface as
MCP tool errors to the caller.

## Functions

### `parse_rsk(path: 'str') -> 'RskDocument'`

Parse the risk file at ``path`` into a :class:`RskDocument`.

Reads the file from disk, then parses and validates its content. "Parse"
here also means "validate": letting :class:`Risk` /
:class:`RskFrontmatter` / :class:`RskDocument`'s own Pydantic validators
run during parsing is the only validation pass there is, exactly like
``tsk.tools.parse_tsk``'s own docstring describes for task lists --
there is no separate validation step. Any structural problem
(unrecognized/misplaced heading, an assessment H3 outside its regex
``@alias``, wrong section order) or field/cross-field validation
failure is not caught or wrapped here: it propagates naturally as
``AssertionError``/``pydantic.ValidationError``, so the MCP layer
reports it as a tool error with the underlying message, giving the
caller something concrete to self-correct from. Similarly, file-access
errors migrate as ``FileNotFoundError``/``PermissionError``/``OSError``.

Parameters
----------
path:
    The filesystem path to the ``.md`` file to parse (absolute or
    relative to the current working directory).

Returns
-------
RskDocument
    The parsed, validated document.

