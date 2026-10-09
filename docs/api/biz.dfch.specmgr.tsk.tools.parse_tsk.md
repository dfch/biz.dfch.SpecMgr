# `biz.dfch.specmgr.tsk.tools.parse_tsk`

``@mcp.tool()`` wrapper: parse_tsk (Task 3.2).

Reads a task list markdown file from disk and parses it into a structured
:class:`TskDocument`, mirroring ``req.tools.parse_req``'s own pattern -- read
path -> parse via free-function returning typed document model. A
content-validation failure of an existing file (the parser's
``AssertionError``/``pydantic.ValidationError``/``yaml.YAMLError``) is
caught and returned as the non-raising ``ValidateResult``
(feat-204-create-error, ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e -- case
5 of the ADR 519d1206-4d2a-4500-9046-6db635209996 non-raising,
structured-result workaround chain); only the file-access errors raised
by ``Path.read_text()`` for a truly-absent or unreadable path still
surface as MCP tool errors to the caller.

Inserted late in the Phase 3 task list (Task 3.2, renumbering every
subsequent task by one) after REQ-004 was found to list ``parse_tsk`` among
the nine required MCP tools while Phase 2 only ever built the model-layer
free function of the same name -- see the feature README's Decisions Made.

## Functions

### `parse_tsk(path: 'str') -> 'TskDocument | ValidateResult'`

Parse the task list file at ``path`` into a :class:`TskDocument`.

Reads the file from disk, then parses and validates its content. "Parse"
here also means "validate": letting :class:`Task` /
:class:`TskFrontmatter` / :class:`TskDocument`'s own Pydantic validators
run during parsing is the only validation pass there is, exactly like
``req.tools.parse_req``'s own docstring describes for requirements --
there is no separate validation step. Any structural problem
(unrecognized/misplaced heading, list the schema doesn't expect) or
field/cross-field validation failure raises
``AssertionError``/``pydantic.ValidationError`` (a malformed frontmatter
block raises ``yaml.YAMLError``) internally, but this tool catches all
three (feat-204-create-error, ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e --
case 5 of the ADR 519d1206-4d2a-4500-9046-6db635209996 non-raising,
structured-result workaround chain) and returns the enriched message
(domain/tool context prepended by the shared tool-boundary wrapper,
:func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`, on top of
the engine's own field-path/line/snippet enrichment, feat-27-validation
Phases 1/2), capped at 300 chars exactly as the generic ``validate`` tool
caps it (feat-110), as the non-raising ``ValidateResult(valid=False, ...)``
(see Returns below) -- the caller still gets something concrete to
self-correct from, in-band. File-access errors for a truly-absent or
unreadable path are never caught: they still migrate as
``FileNotFoundError``/``PermissionError``/``OSError`` (see Raises below).

Parameters
----------
path:
    The filesystem path to the ``.md`` file to parse (absolute or
    relative to the current working directory).

Returns
-------
TskDocument | ValidateResult
    The parsed, validated document. On an existing file that fails to
    parse, a non-raising
    :class:`~biz.dfch.specmgr.general.models.ValidateResult`
    (``valid=False``) with exactly one ``errors`` entry whose
    ``message`` is the enriched exception text capped at 300 chars
    exactly as the generic ``validate`` tool caps it (feat-110, via
    :func:`~biz.dfch.specmgr.models.md._markdown.snippet`), instead of
    ``AssertionError``/``pydantic.ValidationError``/``yaml.YAMLError``
    (feat-204-create-error, ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e --
    case 5 of the ADR 519d1206-4d2a-4500-9046-6db635209996 non-raising,
    structured-result workaround chain).

Raises
------
FileNotFoundError / PermissionError / OSError
    A file-access failure reading ``path`` -- the only remaining raise on
    this surface: ``Path.read_text()`` runs outside the tool's own catch,
    so a truly-absent or unreadable path still surfaces the ``OSError``-
    family error to the caller unchanged (the documented file-access
    contract, feat-204-create-error REQ-002).

