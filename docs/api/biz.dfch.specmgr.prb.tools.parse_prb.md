# `biz.dfch.specmgr.prb.tools.parse_prb`

``@mcp.tool()`` wrapper: parse_prb (Task 3.2).

Reads a problem statement markdown file from disk and parses it into a
structured :class:`PrbDocument`, mirroring ``tsk.tools.parse_tsk``'s own
pattern -- read path -> parse via free-function returning typed document
model. Errors (propagated uncaught from the parser's
``AssertionError``/``pydantic.ValidationError`` or raised by
``Path.read_text()``) surface as MCP tool errors to the caller.

## Functions

### `parse_prb(path: 'str') -> 'PrbDocument'`

Parse the problem statement file at ``path`` into a :class:`PrbDocument`.

Reads the file from disk, then parses and validates its content. "Parse"
here also means "validate": letting :class:`Prb` / :class:`PrbFrontmatter`
/ :class:`PrbDocument`'s own Pydantic validators run during parsing is the
only validation pass there is, exactly like ``tsk.tools.parse_tsk``'s own
docstring describes for task lists -- there is no separate validation
step. Any structural problem (unrecognized/misplaced heading, a section
the schema doesn't expect) or field/cross-field validation failure is not
caught or wrapped here: it propagates naturally as
``AssertionError``/``pydantic.ValidationError``, so the MCP layer reports
it as a tool error with the underlying message, giving the caller
something concrete to self-correct from. Similarly, file-access errors
migrate as ``FileNotFoundError``/``PermissionError``/``OSError``.

Parameters
----------
path:
    The filesystem path to the ``.md`` file to parse (absolute or
    relative to the current working directory).

Returns
-------
PrbDocument
    The parsed, validated document.

