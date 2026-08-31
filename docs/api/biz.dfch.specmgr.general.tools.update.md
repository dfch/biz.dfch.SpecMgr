# `biz.dfch.specmgr.general.tools.update`

``@mcp.tool()`` wrapper: update (feat-22-consolidate-mutation-tools, Phase 2).

The generic, cross-domain whole-body *and* line-range replace tool for the
ten whole-body document types (``req``/``uc``/``tsk``/``qa``/``prb``/
``gol``/``rsk``/``dec``/``sop``/``feat``). It dispatches on the explicit
``type`` parameter to a private per-domain adapter (``_update_<d>``), each
a **verbatim port** of
the corresponding per-domain ``update_<d>`` tool's function body (same
domain lock, same ``load_by_id``, same frontmatter carry-over with only
``updated`` bumped, same verbatim persistence via the domain's own
``write_<d>_file``, same domain ``XNotFoundError``) plus the REQ-002 range
branch: with ``begin``/``end`` given, the on-disk body is re-read via
:func:`._splice.body_text`, spliced via :func:`._splice.splice_body`, and
the *spliced result* is validated as a whole document and persisted
verbatim instead of the raw fragment. ``sop`` is the first domain built
dispatch-only from day one (ADR 36905d5b): its ``_update_sop`` adapter was
written directly in this shape rather than ported from a retired
per-domain tool.

The parameter is intentionally named ``type`` (it matches the frontmatter
field vocabulary the client already knows); no enabled ruff rule objects to
the builtin shadow. The 10-way union return type is annotation-only -- the
MCP input schema is built from the parameters, and the SDK serializes
whichever concrete document is returned.

``feat`` is the one domain whose adapter (``_update_feat``) diverges from
the other nine's identical shape in how it resolves ``id``: via
``feat.tools._paths``'s bespoke folder-per-document shortcut, not a
flat-file directory scan (see
``.specmgr/feat/feat-31-feature/README.md`` Design Notes, "Addressing").
It bumps ``updated`` to the same microsecond timestamp as every other
domain -- an earlier, deliberate divergence (a plain ``YYYY-MM-DD`` date)
was reversed for cross-domain consistency; see that feature's Decisions
Made.

ADR is deliberately *not* a ``type`` here: its section-level MADR mutation
contract (``update_frontmatter``/``update_section``/``option_*``) has no
whole-body replace by design.

## Functions

### `_update_dec(id_: 'str', content: 'str', begin: 'int | None', end: 'int | None') -> 'DecDocument'`

Replace the body of the decision identified by ``id_`` (whole-body or line-range mode).

Verbatim port of the previous per-domain decision update tool's
function body (same ``dec_lock``, ``load_by_id``, frontmatter carry-over
with only ``updated`` bumped, ``write_dec_file``, ``DecNotFoundError``;
that per-domain tool was retired in feat-22 Phase 8, when the DEC
domain -- merged from dev while still on the old per-domain mechanism
-- was converted to the generic tools), plus the REQ-002 range branch
(see :func:`_update_req`).


### `_update_feat(id_: 'str', content: 'str', begin: 'int | None', end: 'int | None') -> 'FeatDocument'`

Replace the body of the feature identified by ``id_`` (whole-body or line-range mode).

Mirrors :func:`_update_dec`'s shape (same ``feat_lock``, ``load_by_id``,
``write_feat_file``, ``FeatNotFoundError``) with one feat-only
divergence (see the module docstring): ``id_`` resolves via
``feat.tools._paths``'s bespoke folder-per-document shortcut (through
``load_by_id``/``feat_base_dir``), not a flat-file directory scan.
``updated`` is bumped to the same microsecond timestamp as every other
domain.


### `_update_gol(id_: 'str', content: 'str', begin: 'int | None', end: 'int | None') -> 'GolDocument'`

Replace the body of the goal identified by ``id_`` (whole-body or line-range mode).

Verbatim port of the previous per-domain goal update tool's function
body (same ``gol_lock``, ``load_by_id``, frontmatter carry-over with
only ``updated`` bumped, ``write_gol_file``, ``GolNotFoundError``; that
per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
branch (see :func:`_update_req`).


### `_update_prb(id_: 'str', content: 'str', begin: 'int | None', end: 'int | None') -> 'PrbDocument'`

Replace the body of the problem statement identified by ``id_`` (whole-body or line-range mode).

Verbatim port of the previous per-domain problem statement update
tool's function body (same ``prb_lock``, ``load_by_id``, frontmatter
carry-over with only ``updated`` bumped, ``write_prb_file``,
``PrbNotFoundError``; that per-domain tool was retired in feat-22
Phase 3), plus the REQ-002 range branch (see :func:`_update_req`).


### `_update_qa(id_: 'str', content: 'str', begin: 'int | None', end: 'int | None') -> 'QaDocument'`

Replace the body of the QA document identified by ``id_`` (whole-body or line-range mode).

Verbatim port of the previous per-domain QA document update tool's
function body (same ``qa_lock``, ``load_by_id``, frontmatter carry-over
with only ``updated`` bumped, ``write_qa_file``, ``QaNotFoundError``;
that per-domain tool was retired in feat-22 Phase 3), plus the REQ-002
range branch (see :func:`_update_req`).


### `_update_req(id_: 'str', content: 'str', begin: 'int | None', end: 'int | None') -> 'ReqDocument'`

Replace the body of the requirement identified by ``id_`` (whole-body or line-range mode).

Verbatim port of the previous per-domain requirement update tool's
function body (same ``req_lock``, ``load_by_id``, frontmatter carry-over
with only ``updated`` bumped, ``write_req_file``, ``ReqNotFoundError``;
that per-domain tool was retired in feat-22 Phase 3), plus the REQ-002
range branch: with ``begin``/``end`` given (both-or-neither is
enforced by the public :func:`update` before dispatch), the on-disk
body is re-read via :func:`body_text`, spliced via
:func:`splice_body`, and the *spliced result* is validated and
persisted verbatim instead of the raw fragment.


### `_update_rsk(id_: 'str', content: 'str', begin: 'int | None', end: 'int | None') -> 'RskDocument'`

Replace the body of the risk identified by ``id_`` (whole-body or line-range mode).

Verbatim port of the previous per-domain risk update tool's function
body (same ``rsk_lock``, ``load_by_id``, frontmatter carry-over with
only ``updated`` bumped, ``write_rsk_file``, ``RskNotFoundError``; that
per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
branch (see :func:`_update_req`).


### `_update_sop(id_: 'str', content: 'str', begin: 'int | None', end: 'int | None') -> 'SopDocument'`

Replace the body of the SOP identified by ``id_`` (whole-body or line-range mode).

Verbatim-shape port of :func:`_update_dec` (same ``sop_lock``,
``load_by_id``, frontmatter carry-over with only ``updated`` bumped,
``write_sop_file``, ``SopNotFoundError``; ``sop`` is the first domain
built dispatch-only from day one per ADR 36905d5b, so there was never a
per-domain ``update_sop`` tool to port -- this adapter was written
directly in this shape), plus the REQ-002 range branch
(see :func:`_update_req`).


### `_update_tsk(id_: 'str', content: 'str', begin: 'int | None', end: 'int | None') -> 'TskDocument'`

Replace the body of the task list identified by ``id_`` (whole-body or line-range mode).

Verbatim port of the previous per-domain task list update tool's
function body (same ``tsk_lock``, ``load_by_id``, frontmatter carry-over
with only ``updated`` bumped, ``write_tsk_file``, ``TskNotFoundError``;
that per-domain tool was retired in feat-22 Phase 3), plus the REQ-002
range branch (see :func:`_update_req`).


### `_update_uc(id_: 'str', content: 'str', begin: 'int | None', end: 'int | None') -> 'UcDocument'`

Replace the body of the use case identified by ``id_`` (whole-body or line-range mode).

Verbatim port of the previous per-domain use-case update tool's function
body (same ``uc_lock``, ``load_by_id``, frontmatter carry-over with only
``updated`` bumped, ``write_uc_file``, ``UcNotFoundError``; that
per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
branch (see :func:`_update_req`).


### `update(id: 'str', type: "Literal['req', 'uc', 'tsk', 'qa', 'prb', 'gol', 'rsk', 'dec', 'sop', 'feat']", content: 'str', begin: 'int | None' = None, end: 'int | None' = None) -> '_UpdateDocument'`

Replace the body of an existing document, in whole-body or line-range mode.

Cross-domain generic for the ten whole-body document types
(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``);
    dispatches on ``type`` to the domain's own ported adapter (same lock,
    same id resolution, same frontmatter carry-over, same verbatim
    persistence, same domain not-found error).

    **Whole-body mode** (no ``begin``/``end``): ``content`` is body
    markdown only, with no YAML frontmatter block -- the same shape the
    per-domain ``update_<d>`` tools accept. Validated the same way: the
    domain body model's ``from_text(format_text(content))``, letting
    ``AssertionError`` (structural failure) or ``pydantic.ValidationError``
    (field/cross-field failure) propagate uncaught, with nothing written in
    either case.

    **Range mode** (both ``begin`` and ``end`` given): ``content`` is a
    replacement *fragment* for the current on-disk body's 1-based,
    inclusive line range ``begin..end``, where ``N`` is the number of lines
    of the current frontmatter-stripped body (the text ``get_<d>(id,
    raw=True)`` returns) and ``N+1`` is a virtual position past the last
    line (``begin = end = N+1`` appends at end of body; ``end = N+1``
    extends the range through the last line). The on-disk body is re-read
    under the domain lock, spliced (drop lines ``begin..min(end, N)``,
    insert the fragment's lines at position ``begin - 1``), and the
    *spliced result* -- not the fragment -- is validated as a whole body
    exactly like whole-body mode and then persisted verbatim, so unchanged
    regions of the on-disk body stay byte-identical. An empty ``content``
    deletes the range (legal iff the result still validates). The YAML
    frontmatter is never addressable: coordinates are body-relative by
    construction.

    In both modes the existing file's frontmatter is carried over with
    every field preserved except ``updated`` (bumped to the current
    microsecond timestamp); ``status`` in particular is never settable
    through this tool -- the generic ``set_status`` tool in
    ``general.tools`` is the only status-change path.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    type:
    The document type / domain: one of ``req``, ``uc``, ``tsk``,
    ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``, ``feat``.
    content:
        Whole-body mode: the replacement body markdown, with no
        frontmatter block. Range mode: the replacement fragment for lines
        ``begin..end`` (may be empty to delete the range).
    begin:
        Optional 1-based first line of the range to replace. Must be given
        together with ``end`` (exactly one of the two is a ``ValueError``).
    end:
        Optional 1-based last line of the range to replace (inclusive);
        ``N+1`` (one past the last body line) extends the range through
        end of body. Must be given together with ``begin``.

    Returns
    -------
ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument |
GolDocument | RskDocument | DecDocument | FeatDocument | SopDocument
        The updated document of the dispatched domain type.

    Raises
    ------
    ValueError
        Misused range coordinates: exactly one of ``begin``/``end`` given
        (raised before any file access), or ``begin < 1``, ``begin > end``,
        or ``end > N + 1`` (raised after the on-disk body is read; the
        message names the offending value(s) and the allowed range).
        Nothing is written in any of these cases.
    AssertionError
        The (spliced) body is structurally invalid (e.g. a range that
        deletes the H1). Nothing is written.
    pydantic.ValidationError
        A field/cross-field validation failure in the (spliced) body (e.g.
        a range producing an out-of-vocabulary value). Nothing is written.
    ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError /
PrbNotFoundError / GolNotFoundError / RskNotFoundError / DecNotFoundError /
FeatNotFoundError / SopNotFoundError
        No document of the dispatched ``type`` has this id -- the
        domain's own not-found error, unchanged from the per-domain tools.

