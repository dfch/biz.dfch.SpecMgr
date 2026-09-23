# `biz.dfch.specmgr.general.tools.list_references`

``@mcp.tool()`` wrapper: list_references (feat-144-ref-artifact, Phase 2).

The generic, cross-domain cross-reference listing tool (ADR 36905d5b's
dispatch-only convention: one ``general/tools/`` module, not a per-domain
``list_references_<d>``). It takes a *source* document's ``type``/``id`` --
every whole-body domain (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/
``rsk``/``dec``/``sop``/``feat``/``vcr``/``sysrs``) plus ``adr`` -- reads
the source as raw, frontmatter-stripped body text
(``general.tools._splice.body_text``: the doc-cache does **not** apply to
the source, since extraction needs the literal markdown), extracts every
``<TYPE> <uuid>`` cross-reference from it
(``general.tools._references.find_references``), deduplicates repeated
occurrences of the same reference (first-occurrence order preserved), and
resolves each unique reference to the referenced document in its own target
domain (``general.tools._references.resolve_reference``: the target
domains' own cache-backed ``load_by_id``; ``adr`` never, ADR bfd76370).
The result is one
:class:`~biz.dfch.specmgr.general.models.reference.ReferenceRow` per unique
reference, wrapped in ``PagedResult[ReferenceRow]`` via the exact ``list_*``
paging mechanism (``normalize_paging`` + ``paginate``, ADR ec9f5262):
``total`` = the number of unique references, ``error_count`` = the number
of references that could not be resolved, ``truncated`` when more
references exist beyond the page.

The naive per-reference resolution strategy (every unique reference is
resolved on each call) is the accepted v1 limitation -- the per-domain
batched optimization is tracked in GitHub issue #145.

Error semantics: an invalid source ``type``/``id`` (unknown type,
path-injection attempt, wrong-format id) is a ``ValueError`` raised by
``_path_safety.validate_id`` **before** any filesystem access (ACC-005); a
source document that does not exist on disk raises the source domain's own
``XNotFoundError`` (identical to ``get_<d>``, ACC-006); a *reference* that
cannot be resolved never raises -- it is a row with null ``title``/``path``
and the target domain's not-found message in ``error`` (ACC-003).

The parameter is intentionally named ``type`` (it matches the frontmatter
field vocabulary the client already knows); no enabled ruff rule objects
to the builtin shadow.

## Functions

### `_load_source_path(type_: 'str', id_: 'str') -> 'tuple[Path, Path]'`

Resolve the source document's on-disk path (feat-144 Task 2.3).

Returns ``(base_dir, path)`` for the source domain: ``base_dir`` the
source domain's own base directory (for the caller's
``_path_safety.assert_within`` defense-in-depth check), ``path`` the
resolved source file. The source domain's own ``XNotFoundError``
propagates unchanged (a source that does not exist on disk is this
tool's only not-found *raise* -- ACC-006, identical to ``get_<d>``).


### `list_references(type: 'Literal[*ALL_DOMAINS,]', id: 'str', max_results: 'int | None' = None, offset: 'int | None' = None) -> 'PagedResult[ReferenceRow]'`

List the cross-references of one source document, resolved and paged.

The source is identified by ``type`` (every whole-body domain
``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/
``feat``/``vcr``/``sysrs``, plus ``adr``) and its own ``id``, and is
validated via ``_path_safety.validate_id`` before any filesystem
access (ACC-005). The source is then read as raw, frontmatter-stripped
body text (``_splice.body_text`` -- the doc-cache does not apply to it,
since extraction needs the literal markdown), and every ``<TYPE>
<uuid>`` cross-reference in that text is extracted
(``_references.find_references``: the reference tag is case-insensitive
and separated from the uuid by one or more space/tab/dash characters;
a match may sit anywhere in a line; the reference's own inline title is
not captured). Repeated occurrences of the same ``(type, id)``
reference are deduplicated to one row, first-occurrence order preserved
(REQ-005).

Each unique reference is resolved to the referenced document in its own
target domain (``_references.resolve_reference``: the nine flat target
domains read through their own cache-backed ``load_by_id``; ``adr``
never does -- ADR bfd76370). The row's ``title`` is the referenced
document's own ``# {title}`` H1 and its ``path`` the referenced
document's resolved absolute file path; a reference whose target does
not exist on disk is a row with ``title``/``path`` ``None`` and the
target domain's own not-found message in ``error`` -- target resolution
never raises (ACC-003).

The full, deduplicated row list is wrapped in
``PagedResult[ReferenceRow]`` via the exact ``list_*`` paging
mechanism (``_paging.normalize_paging`` + ``paginate``, ADR ec9f5262):
``total`` = the number of unique references, ``error_count`` = the
number of references that could not be resolved, ``truncated`` when
more references exist beyond the page (ACC-009).

Parameters
----------
type:
    The source document's type / domain: one of ``adr``, ``req``,
    ``uc``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``,
    ``sop``, ``feat``, ``vcr``, ``sysrs``.
id:
    The source document's specmgr-assigned identifier (the
    ``feat-NNN-slug`` folder name for ``feat``).
max_results:
    Maximum number of reference rows to return in this page. Defaults
    to ``general.tools._paging.DEFAULT_MAX_RESULTS`` when not given
    (``None``); otherwise clamped into range (see
    :func:`~biz.dfch.specmgr.general.tools._paging.normalize_paging`).
offset:
    Zero-based index of the first reference row to include in this
    page. Defaults to ``0`` when not given (``None``); negative values
    are floored to ``0``.

Returns
-------
PagedResult[ReferenceRow]
    One row per unique cross-reference in the source document's body,
    in first-occurrence order, windowed to the requested page.
    ``results`` is empty if the source body contains no references at
    all, or if ``offset`` is past the end of the full list.

Raises
------
ValueError
    ``id`` is a path-injection attempt or not in the dispatched
    domain's own format (raised before any filesystem access; nothing
    is read) -- ACC-005.
ReqNotFoundError / UcNotFoundError / TskNotFoundError /
QaNotFoundError / PrbNotFoundError / GolNotFoundError /
RskNotFoundError / DecNotFoundError / SopNotFoundError /
FeatNotFoundError / VcrNotFoundError / SysrsNotFoundError /
AdrNotFoundError
    No document of the dispatched source ``type`` has this ``id`` --
    the source domain's own not-found error, propagated unchanged from
    the source domain's own ``load_by_id`` (identical to ``get_<d>``)
    -- ACC-006.

