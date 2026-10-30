# `biz.dfch.specmgr.sysrs.tools.create_sysrs`

``@mcp.tool()`` wrapper: create_sysrs (Task 3.2).

Unlike ``adr.tools.create_adr`` (which accepts a full ``frontmatter``/``body``
pair and renders the body back out via ``render_adr``), ``create_sysrs``
accepts **body markdown only** and never renders anything: the caller's own
already-validated ``content`` text is persisted byte-for-byte, and only the
small frontmatter YAML block is code-generated and prepended -- mirrors
``vcr.tools.create_vcr``/``dec.tools.create_dec`` file-for-file.

Thin file-I/O adapter. The ``.md`` file itself is always the source of
truth (ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3); the in-memory cache
warmed after the write below (feat-107-doc-cache Phase 4, REQ-003) is only
ever a content-hash-validated memoization of that file's own current
state, never an independent fact, matching every other tool in this
codebase.

**Language variants (feat-197-i18n Phase 125, ADR 38efdb66 items 1/2/5/6).**
A 1:1 port of ``create_dec``'s ``language``/``id`` handling. ``create_sysrs``
gains two optional parameters, ``language`` (default ``"en"``) and ``id``.
With ``language`` omitted/``"en"`` the tool is byte-identical to before: it
assigns a fresh id and writes the flat ``docs/sysrs/sysrs-<id>-<slug>.md`` file
(and ``id`` must not be given). With a non-default ``language`` the tool
creates a *translation* of an existing System Requirements Specification: ``id`` -- the shared id of the
EN source document (REQ-003, the id is never language-qualified and is never
freshly assigned for a variant) -- is then **required**, the EN source must
already exist on disk (ADR item 2: the EN slug is the single filename
authority), and the variant is written to ``docs/sysrs/{language}/`` under the
EN source's exact basename with the shared id as its frontmatter ``id``
(fresh ``created``/``updated``, ``status="draft"`` -- this domain's create
status, as on every create). The body is validated through the variant's
heading-mapping table (:func:`~biz.dfch.specmgr.sysrs.models.v1.parse_sysrs_body`)
and then persisted byte-for-byte, like EN. An already-existing variant of the
same id and language is never overwritten (``FileExistsError``).

## Functions

### `_create_variant(id_: 'str', language: 'str', content: 'str') -> 'SysrsFrontmatter'`

Create the ``language`` variant of the existing EN ``sysrs`` document ``id_`` (ADR 38efdb66 item 2).

Resolves the EN source's path (the flat directory's id-scan), reuses its
exact basename inside ``docs/sysrs/{language}/``, and writes the
already-validated ``content`` byte-for-byte with a frontmatter carrying
the shared id (REQ-003). Runs under the variant's own per-language lock
so the existence guard and the write are atomic with respect to every
other mutation of this variant.

Parameters
----------
id_:
    The shared id of the EN source document.
language:
    The (shape-guarded, table-resolved, non-default) target language.
content:
    The already-validated variant body markdown.

Returns
-------
SysrsFrontmatter
    The variant's frontmatter (``id`` == ``id_``).

Raises
------
SysrsNotFoundError
    No EN source document with ``id_`` exists.
FileExistsError
    The variant file already exists.


### `create_sysrs(content: 'str', language: 'str' = 'en', id: 'str | None' = None) -> 'SysrsFrontmatter | ValidateResult'`

Create and write a new System Requirements Specification document.

``content`` is body markdown only (the ``Sysrs`` H1 and its sections) --
it must not carry a YAML frontmatter block. The entire frontmatter is
built by this tool: a fresh id (``uuid.uuid4()``), ``type="sysrs"``,
``status="draft"`` (always, never caller-supplied on create),
``created``/``updated`` both set to the current timestamp, and
``version`` set to the current ``models.md`` schema version.

``content`` is validated by constructing a
:class:`~biz.dfch.specmgr.sysrs.models.v1.Sysrs` from it
(``Sysrs.from_text(format_text(content))``). A structural failure
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

**Language variants (feat-197-i18n Phase 125).** With a non-default
``language`` this tool creates a translation of an existing EN
document rather than a new one -- see the module docstring: the
shared ``id`` of the EN source is a required argument (the variant's
frontmatter ``id`` is that same id, never a fresh one, REQ-003), the EN
source must exist, and the variant is written to
``docs/sysrs/{language}/`` under the EN source's exact basename
(ADR 38efdb66 item 2). ``content`` is validated through the variant's
heading-mapping table, and the existing-variant guard
(``FileExistsError``) runs under the variant's own per-language lock.

Parameters
----------
content:
    The new document's body markdown, with no frontmatter block (for a
    non-default ``language``: the translation, whose fixed-text
    headings may be translated per that language's table).
language:
    The language to create the document in: ``"en"`` (the default)
    creates a new, flat ``docs/sysrs/`` document with a freshly assigned
    id -- today's exact behavior; any other ISO 639-1-shaped lowercase
    two-letter code (e.g. ``"de"``) creates a translation variant of
    an existing EN document in ``docs/sysrs/{language}/``. Shape-guarded
    (and its heading-mapping table resolved) before any filesystem
    access.
id:
    The shared id of the existing EN source document. Required when
    ``language`` is not the default (the variant reuses it as its own
    frontmatter id); must be omitted for the default language (a new
    document's id is always server-assigned).

Returns
-------
SysrsFrontmatter | ValidateResult
    The newly created document's frontmatter only (no body), with its
    assigned id in ``.id``. Use the corresponding ``get_sysrs`` tool to
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

Raises
------
ValueError
    ``language`` is not an ISO 639-1-shaped lowercase two-letter code,
    a non-default ``language`` has no packaged heading-mapping table,
    ``id`` is missing for a non-default ``language``, ``id`` is given
    for the default language, or ``id`` is not a well-formed UUID --
    all raised before any filesystem access; nothing is written.
SysrsNotFoundError
    A non-default ``language`` was given but no EN source document
    with ``id`` exists (a variant requires its EN source, ADR 38efdb66
    item 2); nothing is written.
FileExistsError
    A variant of ``id`` in this non-default ``language`` already
    exists (a variant is never overwritten); nothing is written.

