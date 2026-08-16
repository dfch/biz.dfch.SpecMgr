# `biz.dfch.specmgr.uc.tools.parse_uc`

``@mcp.tool()`` wrapper: parse_uc.

Reads a use-case markdown file from disk and parses it into a structured
:class:`UcDocument`. Path-based (not id-based) by design -- ``get_uc``
(``uc.tools.get_uc``) is the id-based read path over the use-case base
directory (``uc.tools._paths``/``_io``); this tool instead parses any
markdown file the caller points it at directly.

## Functions

### `parse_uc(path: 'str') -> 'UcDocument'`

Parse the use-case file at ``path`` into a :class:`UcDocument`.

Reads the file from disk, then parses and validates its content. "Parse"
here also means "validate": letting :class:`UseCase`/
:class:`UcFrontmatter`/:class:`UcDocument`'s own Pydantic validators
run during parsing is the only validation pass there is, exactly like
`adr.tools.validate_adr`'s own docstring describes for ADRs -- there is
no separate validation step. Any structural problem (an unrecognized/
misplaced heading, a list the schema doesn't expect) or field/
cross-field validation failure is not caught or wrapped here: it
propagates naturally as ``AssertionError``/``pydantic.ValidationError``,
so the MCP layer reports it as a tool error with the underlying
message, giving the caller something concrete to self-correct from.
Similarly, file-access errors (missing file, permission denied) propagate
as ``FileNotFoundError``/``PermissionError``/``OSError``.

Parameters
----------
path:
    The filesystem path to the ``.md`` file to parse (absolute or
    relative to the current working directory).

Returns
-------
UcDocument
    The parsed, validated document.

