# `biz.dfch.specmgr.general.tools.set_status`

``@mcp.tool()`` wrapper: set_status (feat-22-consolidate-mutation-tools, Phase 4).

The generic, cross-domain status-change tool for all thirteen document types
(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/``sysrs``/``adr``).
It dispatches on the explicit ``type`` parameter to a private per-domain
adapter (``_set_status_<d>``), each a **verbatim port** of the
corresponding per-domain status tool's function body (same domain lock,
same ``load_by_id``, same raw-body re-read and verbatim re-persistence,
same frontmatter reconstruction through the domain's own
``XFrontmatter`` constructor -- so the domain's closed status vocabulary
validates -- and the same domain ``XNotFoundError``; those per-domain
tools were retired in feat-22 Phase 4). The ADR adapter ports the
previous per-domain ADR status tool's function body (same ``adr_lock``,
``load_by_id``, and ``write_adr`` render round-trip,
``AdrNotFoundError``) including its delegation to
``models.adr.v1.mutations.set_status``, which composes ``status`` as
``"superseded by {superseded_by}"`` when ``superseded_by`` is given.
``sop`` is the first domain built dispatch-only from day one (ADR
36905d5b): its ``_set_status_sop`` adapter was written directly in this
shape rather than ported from a retired per-domain tool.

The ``feat`` adapter (``_set_status_feat``) diverges from the other ten
whole-body domains' identical shape in the same way ``_update_feat``
(in ``update.py``) does: it resolves ``id`` via
``feat.tools._paths``'s bespoke folder-per-document shortcut, not a
flat-file directory scan (see
``.specmgr/feat/feat-31-feature/README.md`` Design Notes). It bumps
``updated`` to the same shared date+time timestamp (via
``general.tools._timestamps.now_timestamp()``) as every other domain --
an earlier, deliberate divergence (a plain ``YYYY-MM-DD`` date) was
reversed for cross-domain consistency; see that feature's Decisions Made.

The parameter is intentionally named ``type`` (it matches the frontmatter
field vocabulary the client already knows); no enabled ruff rule objects
to the builtin shadow. The 13-way union return type is annotation-only --
the MCP input schema is built from the parameters, and the SDK
serializes whichever concrete document is returned.

``superseded_by`` is accepted only for ``type="adr"``: the
"superseded by X" status pattern is ADR-specific (no other domain's
``XFrontmatter.status`` accepts it). The public :func:`set_status`
rejects it for any other ``type`` with a ``ValueError`` before any file
access.

Neither any ``create_<d>`` tool nor the generic :func:`update` tool
accepts a ``status`` argument at all -- this tool is the sole
status-change entry point for every domain.

``models.adr.v1.mutations`` is imported qualified (as ``mutations``)
because the pure, in-memory operation it delegates to shares this
wrapper's own name.

Safety (REQ-009, feat-38-39-41-43-44 Phase 4): the public
:func:`set_status` validates ``id`` via ``_path_safety.validate_id``
before dispatch (a ``ValueError`` before any filesystem access --
mirroring the generic ``delete`` tool's own REQ-003; ``_path_safety``'s
UUID-shaped domains now include ``adr``), and every adapter confines the
resolved path to the domain's own base directory with
``_path_safety.assert_within`` after ``load_by_id``, inside the domain
lock.

## Functions

### `_set_status_adr(id_: 'str', status: 'str', superseded_by: 'str | None') -> 'Adr'`

Replace the status of the ADR identified by ``id_``.

Port of the previous per-domain ADR status tool's function body
(same ``adr_lock``, ``load_by_id``, delegation to
``models.adr.v1.mutations.set_status`` -- which composes ``status`` as
``"superseded by {superseded_by}"`` when ``superseded_by`` is given --
and the ``write_adr`` render round-trip, ``AdrNotFoundError``; that
per-domain tool was retired in feat-22 Phase 4).


### `_set_status_dec(id_: 'str', status: 'str', superseded_by: 'str | None') -> 'DecFrontmatter'`

Replace the status of the decision identified by ``id_``.

Verbatim port of the previous per-domain decision status tool's
function body (same ``dec_lock``, ``load_by_id``, ``write_dec_file``,
``DecNotFoundError``; that per-domain tool was retired in feat-22
Phase 8, when the DEC domain -- merged from dev while still on the
old per-domain mechanism -- was converted to the generic tools) --
see :func:`_set_status_req` for the full semantics.


### `_set_status_feat(id_: 'str', status: 'str', superseded_by: 'str | None') -> 'FeatFrontmatter'`

Replace the status of the feature identified by ``id_``.

Mirrors :func:`_set_status_dec`'s shape (same ``feat_lock``,
``load_by_id``, ``write_feat_file``, ``FeatNotFoundError``) -- see
:func:`_set_status_req` for the full semantics -- with the same
feat-only divergence ``_update_feat`` (in ``update.py``) documents:
``id_`` resolves via ``feat.tools._paths``'s bespoke folder-per-document
shortcut, not a flat-file directory scan. ``updated`` is bumped to the
same shared date+time timestamp as every other domain.


### `_set_status_gol(id_: 'str', status: 'str', superseded_by: 'str | None') -> 'GolFrontmatter'`

Replace the status of the goal identified by ``id_``.

Verbatim port of the previous per-domain goal status tool's function
body (same ``gol_lock``, ``load_by_id``, ``write_gol_file``,
``GolNotFoundError``; that per-domain tool was retired in feat-22
Phase 4) -- see :func:`_set_status_req` for the full semantics.


### `_set_status_prb(id_: 'str', status: 'str', superseded_by: 'str | None') -> 'PrbFrontmatter'`

Replace the status of the problem statement identified by ``id_``.

Verbatim port of the previous per-domain problem statement status
tool's function body (same ``prb_lock``, ``load_by_id``,
``write_prb_file``, ``PrbNotFoundError``; that per-domain tool was
retired in feat-22 Phase 4) -- see :func:`_set_status_req` for the
full semantics.


### `_set_status_qa(id_: 'str', status: 'str', superseded_by: 'str | None') -> 'QaFrontmatter'`

Replace the status of the QA document identified by ``id_``.

Verbatim port of the previous per-domain QA document status tool's
function body (same ``qa_lock``, ``load_by_id``, ``write_qa_file``,
``QaNotFoundError``; that per-domain tool was retired in feat-22
Phase 4) -- see :func:`_set_status_req` for the full semantics.


### `_set_status_req(id_: 'str', status: 'str', superseded_by: 'str | None') -> 'ReqFrontmatter'`

Replace the status of the requirement identified by ``id_``.

Verbatim port of the previous per-domain requirement status tool's
function body (same ``req_lock``, ``load_by_id``, raw-body re-read via
the established ``frontmatter.loads(...).content`` mechanism and
verbatim re-persistence, frontmatter reconstructed through
:class:`ReqFrontmatter`'s own constructor so the closed status
vocabulary validates, ``write_req_file``, ``ReqNotFoundError``; that
per-domain tool was retired in feat-22 Phase 4). ``superseded_by`` is
never used here -- the public :func:`set_status` guard rejects it for
every non-``adr`` type before dispatch.


### `_set_status_rsk(id_: 'str', status: 'str', superseded_by: 'str | None') -> 'RskFrontmatter'`

Replace the status of the risk identified by ``id_``.

Verbatim port of the previous per-domain risk status tool's function
body (same ``rsk_lock``, ``load_by_id``, ``write_rsk_file``,
``RskNotFoundError``; that per-domain tool was retired in feat-22
Phase 4) -- see :func:`_set_status_req` for the full semantics.


### `_set_status_sop(id_: 'str', status: 'str', superseded_by: 'str | None') -> 'SopFrontmatter'`

Replace the status of the SOP identified by ``id_``.

Verbatim-shape port of :func:`_set_status_dec` (same ``sop_lock``,
``load_by_id``, ``write_sop_file``, ``SopNotFoundError``; ``sop`` is the
first domain built dispatch-only from day one per ADR 36905d5b, so there
was never a per-domain ``set_status_sop`` tool to port -- this adapter
was written directly in this shape) -- see :func:`_set_status_req` for
the full semantics.


### `_set_status_sysrs(id_: 'str', status: 'str', superseded_by: 'str | None') -> 'SysrsFrontmatter'`

Replace the status of the System Requirements Specification identified by ``id_``.

Verbatim-shape port of :func:`_set_status_sop` (same ``sysrs_lock``,
``load_by_id``, ``write_sysrs_file``, ``SysrsNotFoundError``; ``sysrs``
is dispatch-only from day one per ADR 36905d5b, so this adapter was
written directly in this shape) -- see :func:`_set_status_req` for
the full semantics.


### `_set_status_tsk(id_: 'str', status: 'str', superseded_by: 'str | None') -> 'TskFrontmatter'`

Replace the status of the task list identified by ``id_``.

Verbatim port of the previous per-domain task list status tool's
function body (same ``tsk_lock``, ``load_by_id``, ``write_tsk_file``,
``TskNotFoundError``; that per-domain tool was retired in feat-22
Phase 4) -- see :func:`_set_status_req` for the full semantics.


### `_set_status_uc(id_: 'str', status: 'str', superseded_by: 'str | None') -> 'UcFrontmatter'`

Replace the status of the use case identified by ``id_``.

Verbatim port of the previous per-domain use-case status tool's
function body (same ``uc_lock``, ``load_by_id``, ``write_uc_file``,
``UcNotFoundError``; that per-domain tool was retired in feat-22
Phase 4) -- see :func:`_set_status_req` for the full semantics.


### `_set_status_vcr(id_: 'str', status: 'str', superseded_by: 'str | None') -> 'VcrFrontmatter'`

Replace the status of the verification case record identified by ``id_``.

Mirrors :func:`_set_status_dec`'s shape (same ``vcr_lock``,
``load_by_id``, ``write_vcr_file``, ``VcrNotFoundError``) -- see
:func:`_set_status_req` for the full semantics. ``vcr`` is not
``adr``, so ``superseded_by`` must never be given.


### `set_status(id: 'str', type: "Literal['req', 'uc', 'tsk', 'qa', 'prb', 'gol', 'rsk', 'dec', 'sop', 'feat', 'vcr', 'sysrs', 'adr']", status: 'str', superseded_by: 'str | None' = None) -> '_SetStatusFrontmatter'`

Replace the status of an existing document, across all thirteen domains.

    Cross-domain generic for every document type
    (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/``sysrs``/``adr``);
    dispatches on ``type`` to the domain's own ported adapter (same lock,
    same id resolution, same body handling, same domain not-found error).

    For the eleven whole-body domains the existing file's frontmatter is
    carried over with every field preserved except ``status`` (replaced)
    and ``updated`` (bumped to the current date+time timestamp, via
    ``general.tools._timestamps.now_timestamp()``); the
    body is never touched -- its raw, on-disk markdown (not a render of
    the parsed model) is re-read and re-persisted verbatim. For
    ``type="adr"`` the change delegates to
    ``models.adr.v1.mutations.set_status`` (which composes ``status`` as
    ``"superseded by {superseded_by}"`` when ``superseded_by`` is given)
    and re-renders the full file via the ``write_adr`` round-trip.

    The new ``status`` must be in the domain's own closed vocabulary: the
    frontmatter is reconstructed through the domain's own
    ``XFrontmatter`` constructor, so the domain's own validator enforces
    its set. Where that set lives is documented per domain -- see each
    ``XFrontmatter.status`` field (the twelve whole-body domains'
    ``models/<v>/frontmatter.py`` and ``models/adr/v1/frontmatter.py``)
    rather than any list in this docstring.

    Safety (REQ-009, feat-38-39-41-43-44 Phase 4, mirroring ``delete``'s
    own REQ-003): ``id`` is validated via ``_path_safety.validate_id`` (no
    ``/``, no ``\``, no ``..``, plus the dispatched domain's own format --
    canonical lowercase-hex UUID for the twelve UUID domains including
    ``adr``, ``feat-NNN-slug`` for ``feat``) **before** any filesystem
    access, so a path-injection attempt or a wrong-format id is a
    ``ValueError`` raised before dispatch. Each adapter additionally
    confines the resolved path to the domain's own base directory with
    ``_path_safety.assert_within`` inside the lock -- defense-in-depth
    against any future gap in the id validation.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    type:
        The document type / domain: one of ``req``, ``uc``, ``tsk``,
        ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``, ``feat``,
        ``vcr``, ``sysrs``, ``adr``.
    status:
        The new status. Must be one of the dispatched domain's own
        accepted values (see its ``XFrontmatter.status`` field). For
        ``adr``, ignored when ``superseded_by`` is given.
    superseded_by:
        ADR only. When given (with ``type="adr"``), ``status`` is
        composed as ``f"superseded by {superseded_by}"`` instead of being
        used verbatim. A ``ValueError`` for any other ``type``.

    Returns
    -------
ReqFrontmatter | UcFrontmatter | TskFrontmatter | QaFrontmatter | PrbFrontmatter |
GolFrontmatter | RskFrontmatter | DecFrontmatter | FeatFrontmatter | SopFrontmatter |
VcrFrontmatter | SysrsFrontmatter | Adr
    The updated document's frontmatter only (no body) of the dispatched domain type
    for the twelve whole-body domains; for ``type="adr"`` (unchanged, out of scope for
    this feature) the full ``Adr`` document, as before. Use the corresponding
    ``get_<d>`` tool to fetch the full document afterward for the twelve whole-body
    domains.

    Raises
    ------
    ValueError
        ``id`` is a path-injection attempt or not in the dispatched
        domain's own format (raised before any filesystem access; nothing
        is written), or ``superseded_by`` given with a ``type`` other
        than ``"adr"`` (raised before any file access). Nothing is
        written in either case.
    pydantic.ValidationError
        ``status`` is not in the dispatched domain's closed vocabulary
        (for ``adr``: not one of its six values and not a
        ``"superseded by ..."`` string). The message is prefixed with
        domain/tool/channel context (e.g. ``"tsk set_status
        (frontmatter): ..."``) by the shared tool-boundary wrapper
        (:func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`).
        Nothing is written.
    ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError /
    PrbNotFoundError / GolNotFoundError / RskNotFoundError / DecNotFoundError /
    FeatNotFoundError / SopNotFoundError / VcrNotFoundError / SysrsNotFoundError /
    AdrNotFoundError
        No document of the dispatched ``type`` has this id -- the
        domain's own not-found error, unchanged from the per-domain tools.

