# `biz.dfch.specmgr.sop.tools.create_sop`

``@mcp.tool()`` wrapper: create_sop (Task 2.2).

Unlike ``adr.tools.create_adr`` (which accepts a full ``frontmatter``/``body``
pair and renders the body back out via ``render_adr``), ``create_sop`` accepts
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

### `create_sop(content: 'str') -> 'SopFrontmatter | ValidateResult'`

Create and write a new SOP document.

``content`` is body markdown only (the ``Sop`` H1 and its sections)
-- it must not carry a YAML frontmatter block. The entire frontmatter is
built by this tool: a fresh id (``uuid.uuid4()``), ``type="sop"``,
``status="draft"`` (always, never caller-supplied on create),
``created``/``updated`` both set to the current timestamp, and
``version`` set to the current ``models.md`` schema version.

``content`` is validated by constructing a
:class:`~biz.dfch.specmgr.sop.models.v1.Sop` from it
(``Sop.from_text(format_text(content))``). A structural failure
raises ``AssertionError`` and a field/cross-field failure raises
``pydantic.ValidationError`` -- but this tool catches both
(feat-204-create-error, ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e --
case 5 of the ADR 519d1206-4d2a-4500-9046-6db635209996 non-raising,
structured-result workaround chain) and returns the enriched message
(domain/tool/channel context prepended by the shared tool-boundary
wrapper, :func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`,
on top of the engine's own field-path/line/snippet enrichment,
feat-27-validation Phases 1/2) as the non-raising
``ValidateResult(valid=False, ...)`` (see Returns below) instead --
nothing is written in that case.

No body rendering is ever needed: the caller's own already-validated
``content`` is persisted byte-for-byte, exactly as submitted; only the
small, code-constructed frontmatter YAML block is (re)generated.

Parameters
----------
content:
    The new document's body markdown, with no frontmatter block.

Returns
-------
SopFrontmatter | ValidateResult
    The newly created document's frontmatter only (no body), with its
    assigned id in ``.id``. Use the corresponding ``get_sop`` tool to
    fetch the full document afterward. On a content-validation failure
    of ``content``, a non-raising
    :class:`~biz.dfch.specmgr.general.models.ValidateResult`
    (``valid=False``) with exactly one ``errors`` entry whose
    ``message`` is the enriched exception text capped at 300 chars
    exactly as the generic ``validate`` tool caps it (feat-110, via
    :func:`~biz.dfch.specmgr.models.md._markdown.snippet`), instead of
    ``AssertionError``/``pydantic.ValidationError`` -- nothing is written
    in that case (feat-204-create-error, ADR
    f14f125e-eaad-4f4f-a6fd-3c931bed726e -- case 5 of the ADR
    519d1206-4d2a-4500-9046-6db635209996 non-raising, structured-result
    workaround chain).

