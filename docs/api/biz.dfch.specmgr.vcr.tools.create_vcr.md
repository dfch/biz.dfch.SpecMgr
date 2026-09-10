# `biz.dfch.specmgr.vcr.tools.create_vcr`

``@mcp.tool()`` wrapper: create_vcr (Task 2.1).

Unlike ``adr.tools.create_adr`` (which accepts a full ``frontmatter``/``body``
pair and renders the body back out via ``render_adr``), ``create_vcr`` accepts
**body markdown only** and never renders anything: the caller's own
already-validated ``content`` text is persisted byte-for-byte, and only the
small frontmatter YAML block is code-generated and prepended -- mirrors
``dec.tools.create_dec`` file-for-file.

Thin file-I/O adapter. The ``.md`` file itself is always the source of
truth (ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3); the in-memory cache
warmed after the write below (feat-107-doc-cache Phase 4, REQ-003) is only
ever a content-hash-validated memoization of that file's own current
state, never an independent fact, matching every other tool in this
codebase.

## Functions

### `create_vcr(content: 'str') -> 'VcrFrontmatter'`

Create and write a new verification case record document.

``content`` is body markdown only (the ``Vcr`` H1 and its sections) --
it must not carry a YAML frontmatter block. The entire frontmatter is
built by this tool: a fresh id (``uuid.uuid4()``), ``type="vcr"``,
``status="draft"`` (always, never caller-supplied on create),
``created``/``updated`` both set to the current timestamp, and
``version`` set to the current ``models.md`` schema version.

``content`` is validated by constructing a
:class:`~biz.dfch.specmgr.vcr.models.v1.Vcr` from it
(``Vcr.from_text(format_text(content))``); a structural failure
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
VcrFrontmatter
    The newly created document's frontmatter only (no body), with its
    assigned id in ``.id``. Use the corresponding ``get_vcr`` tool to
    fetch the full document afterward.

Raises
------
AssertionError
    A structural failure in ``content``. The message is prefixed with domain/tool/channel
    context (e.g. ``"vcr create_vcr (body): ..."``) by the shared tool-boundary
    wrapper (:func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`), layered on top
    of the engine's own field-path/line/snippet enrichment (feat-27-validation Phases 1/2).
    Nothing is written.
pydantic.ValidationError
    A field/cross-field validation failure in ``content`` -- similarly prefixed. Nothing is
    written.

