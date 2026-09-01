# `biz.dfch.specmgr.vcr.tools.parse_vcr`

``@mcp.tool()`` wrapper: parse_vcr (Task 2.1).

Reads a verification case record markdown file from disk and parses it into
a structured :class:`VcrDocument`, mirroring ``dec.tools.parse_dec``'s own
pattern -- read path -> parse via free-function returning typed document
model. Errors (propagated uncaught from the parser's ``AssertionError``/
``pydantic.ValidationError`` or raised by ``Path.read_text()``) surface as
MCP tool errors to the caller.

## Functions

### `parse_vcr(path: 'str') -> 'VcrDocument'`

Parse the verification case record file at ``path`` into a :class:`VcrDocument`.

Reads the file from disk, then parses and validates its content. "Parse"
here also means "validate": letting :class:`Vcr` /
:class:`VcrFrontmatter` / :class:`VcrDocument`'s own Pydantic validators
run during parsing is the only validation pass there is -- there is
no separate validation step. Any structural problem (unrecognized/misplaced
heading, list the schema doesn't expect) or field/cross-field validation
failure propagates as
``AssertionError``/``pydantic.ValidationError``, so the MCP layer reports
it as a tool error with the underlying message, giving the caller something
concrete to self-correct from. Similarly, file-access errors migrate as
``FileNotFoundError``/``PermissionError``/``OSError``.

Parameters
----------
path:
    The filesystem path to the ``.md`` file to parse (absolute or
    relative to the current working directory).

Returns
-------
VcrDocument
    The parsed, validated document.

Raises
------
AssertionError
    A structural problem in the parsed body (unrecognized/misplaced heading, a list the
    schema doesn't expect, ...). The message is prefixed with domain/tool context (e.g.
    ``"vcr parse_vcr: ..."``) by the shared tool-boundary wrapper
    (:func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`), layered on top of the
    engine's own field-path/line/snippet enrichment (feat-27-validation Phases 1/2).
pydantic.ValidationError
    A field/cross-field validation failure -- similarly prefixed.
yaml.YAMLError
    Malformed frontmatter YAML -- similarly prefixed, on top of the frontmatter-block
    naming and document-relative line remap :mod:`~biz.dfch.specmgr.models.md.
    _frontmatter_parse` already applies.
FileNotFoundError / PermissionError / OSError
    A file-access failure reading ``path`` -- untouched by this wrapper (already
    actionable; out of this feature's scope).

