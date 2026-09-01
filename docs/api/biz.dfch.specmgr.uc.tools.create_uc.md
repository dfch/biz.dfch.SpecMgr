# `biz.dfch.specmgr.uc.tools.create_uc`

``@mcp.tool()`` wrapper: create_uc (Task 3.1.5).

Mirrors ``req.tools.create_req``: accepts **body markdown only** and never
renders anything -- the caller's own already-validated ``content`` text is
persisted byte-for-byte, and only the small frontmatter YAML block is
code-generated and prepended. There is therefore no ``write_uc``/``render_uc``
in ``uc.tools._io`` for this tool to call -- the frontmatter+content
composition is factored into ``uc.tools._write.write_uc_file`` instead,
shared with the generic ``update`` tool in ``general.tools``.

Thin file-I/O adapter; there is no in-memory cache of a parsed
:class:`~biz.dfch.specmgr.uc.models.v2.UcDocument` -- the ``.md`` file
itself is always the source of truth, matching every other tool in this
codebase.

## Functions

### `create_uc(content: 'str') -> 'UcDocument'`

Create and write a new use-case document.

``content`` is body markdown only (the ``UseCase`` H1 and its sections)
-- it must not carry a YAML frontmatter block. The entire frontmatter is
built by this tool: a fresh id (``uuid.uuid4()``), ``type="uc"``,
``status="draft"`` (always, never caller-supplied on create),
``created``/``updated`` both set to the current timestamp, and
``version`` set to the current ``models.md`` schema version.

``content`` is validated by constructing a
:class:`~biz.dfch.specmgr.uc.models.v2.UseCase` from it
(``UseCase.from_text(format_text(content))``); a structural failure
raises ``AssertionError`` and a field/cross-field failure raises
``pydantic.ValidationError``, both re-raised with domain/tool context
prepended (see Raises below) -- nothing is written in
either case.

No body rendering is ever needed: the caller's own already-validated
``content`` is persisted byte-for-byte, exactly as submitted; only the
small, code-constructed frontmatter YAML block is (re)generated.

Parameters
----------
content:
    The new document's body markdown, with no frontmatter block.

Returns
-------
UcDocument
    The newly created document, with its assigned id in
    ``frontmatter.id``.

Raises
------
AssertionError
    A structural failure in ``content``. The message is prefixed with domain/tool/channel
    context (e.g. ``"uc create_uc (body): ..."``) by the shared tool-boundary
    wrapper (:func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`), layered on top
    of the engine's own field-path/line/snippet enrichment (feat-27-validation Phases 1/2).
    Nothing is written.
pydantic.ValidationError
    A field/cross-field validation failure in ``content`` -- similarly prefixed. Nothing is
    written.

