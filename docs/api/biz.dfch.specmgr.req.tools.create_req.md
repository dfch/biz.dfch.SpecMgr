# `biz.dfch.specmgr.req.tools.create_req`

``@mcp.tool()`` wrapper: create_req (Task 3.12).

Unlike ``adr.tools.create_adr`` (which accepts a full ``frontmatter``/``body``
pair and renders the body back out via ``render_adr``), ``create_req`` accepts
**body markdown only** and never renders anything: the caller's own
already-validated ``content`` text is persisted byte-for-byte, and only the
small frontmatter YAML block is code-generated and prepended (Task 3.9's
design). There is therefore no ``write_req``/``render_req`` in
``req.tools._io`` for this tool to call -- the frontmatter+content
composition is factored into ``req.tools._write.write_req_file`` instead,
shared with ``update_req`` (Task 3.13).

Thin file-I/O adapter; there is no in-memory cache of a parsed
:class:`~biz.dfch.specmgr.req.models.v1.ReqDocument` -- the ``.md`` file
itself is always the source of truth, matching every other tool in this
codebase.

## Functions

### `create_req(content: 'str') -> 'ReqDocument'`

Create and write a new requirement document.

``content`` is body markdown only (the ``Requirement`` H1 and its
sections) -- it must not carry a YAML frontmatter block. The entire
frontmatter is built by this tool: a fresh id (``uuid.uuid4()``),
``type="req"``, ``status="draft"`` (always, never caller-supplied on
create), ``created``/``updated`` both set to the current timestamp, and
``version`` set to the current ``models.md`` schema version.

``content`` is validated by constructing a
:class:`~biz.dfch.specmgr.req.models.v1.Requirement` from it
(``Requirement.from_text(format_text(content))``); a structural failure
raises ``AssertionError`` and a field/cross-field failure raises
``pydantic.ValidationError``, both uncaught -- nothing is written in
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
ReqDocument
    The newly created document, with its assigned id in
    ``frontmatter.id``.

