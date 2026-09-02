# `biz.dfch.specmgr.sysrs.tools.create_sysrs`

``@mcp.tool()`` wrapper: create_sysrs (Task 3.2).

Unlike ``adr.tools.create_adr`` (which accepts a full ``frontmatter``/``body``
pair and renders the body back out via ``render_adr``), ``create_sysrs``
accepts **body markdown only** and never renders anything: the caller's own
already-validated ``content`` text is persisted byte-for-byte, and only the
small frontmatter YAML block is code-generated and prepended -- mirrors
``vcr.tools.create_vcr``/``dec.tools.create_dec`` file-for-file.

Thin file-I/O adapter; there is no in-memory cache of a parsed
:class:`~biz.dfch.specmgr.sysrs.models.v1.SysrsDocument` -- the ``.md`` file
itself is always the source of truth, matching every other tool in this
codebase.

## Functions

### `create_sysrs(content: 'str') -> 'SysrsDocument'`

Create and write a new System Requirements Specification document.

``content`` is body markdown only (the ``Sysrs`` H1 and its sections) --
it must not carry a YAML frontmatter block. The entire frontmatter is
built by this tool: a fresh id (``uuid.uuid4()``), ``type="sysrs"``,
``status="draft"`` (always, never caller-supplied on create),
``created``/``updated`` both set to the current timestamp, and
``version`` set to the current ``models.md`` schema version.

``content`` is validated by constructing a
:class:`~biz.dfch.specmgr.sysrs.models.v1.Sysrs` from it
(``Sysrs.from_text(format_text(content))``); a structural failure
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
SysrsDocument
    The newly created document, with its assigned id in
    ``frontmatter.id``.

Raises
------
AssertionError
    A structural failure in ``content``. The message is prefixed with domain/tool/channel
    context (e.g. ``"sysrs create_sysrs (body): ..."``) by the shared tool-boundary
    wrapper (:func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`), layered on top
    of the engine's own field-path/line/snippet enrichment (feat-27-validation Phases 1/2).
    Nothing is written.
pydantic.ValidationError
    A field/cross-field validation failure in ``content`` -- similarly prefixed. Nothing is
    written.

