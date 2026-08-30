# `biz.dfch.specmgr.feat.tools.parse_feat`

``@mcp.tool()`` wrapper: parse_feat (Task 2.3).

Reads a feature markdown file from disk and parses it into a structured
:class:`FeatDocument`, mirroring ``dec.tools.parse_dec``'s own pattern --
read path -> parse via free function returning typed document model. Errors
(propagated uncaught from the parser's ``AssertionError``/
``pydantic.ValidationError`` or raised by ``Path.read_text()``) surface as
MCP tool errors to the caller.

Unlike ``load_by_id``/``find_feat_path_by_id`` (Task 2.1/2.2), this tool
takes an arbitrary filesystem path, not an ``id`` -- it never checks that
``frontmatter.id`` matches the containing folder's own name (that invariant
is a *tool-layer addressing* concern, REQ-003, not something a bare
"parse this file" operation should enforce).

## Functions

### `parse_feat(path: 'str') -> 'FeatDocument'`

Parse the feature file at ``path`` into a :class:`FeatDocument`.

Reads the file from disk, then parses and validates its content. "Parse"
here also means "validate": letting :class:`Feature` /
:class:`FeatFrontmatter` / :class:`FeatDocument`'s own Pydantic
validators run during parsing is the only validation pass there is --
there is no separate validation step. Any structural problem
(unrecognized/misplaced heading, list the schema doesn't expect) or
field/cross-field validation failure is not caught or wrapped here: it
propagates naturally as ``AssertionError``/``pydantic.ValidationError``,
so the MCP layer reports it as a tool error with the underlying
message, giving the caller something concrete to self-correct from.
Similarly, file-access errors migrate as
``FileNotFoundError``/``PermissionError``/``OSError``.

Parameters
----------
path:
    The filesystem path to the ``.md`` file to parse (absolute or
    relative to the current working directory) -- typically
    ``<feature base dir>/<id>/README.md``.

Returns
-------
FeatDocument
    The parsed, validated document.

