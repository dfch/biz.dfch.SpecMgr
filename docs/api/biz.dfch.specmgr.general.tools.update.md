# `biz.dfch.specmgr.general.tools.update`

``@mcp.tool()`` wrapper: update (feat-22-consolidate-mutation-tools, Phase 2).

The generic, cross-domain whole-body *and* line-range replace tool for the
eleven whole-body document types (``req``/``uc``/``tsk``/``qa``/``prb``/
``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``). It dispatches on the
explicit ``type`` parameter to a private per-domain adapter (``_update_<d>``),
each a **verbatim port** of
the corresponding per-domain ``update_<d>`` tool's function body (same
domain lock, same ``load_by_id``, same frontmatter carry-over with only
``updated`` bumped, same verbatim persistence via the domain's own
``write_<d>_file``, same domain ``XNotFoundError``) plus the REQ-002 range
branch: with ``offset`` given (``limit`` optional), the on-disk body is
re-read via :func:`._splice.body_text`, spliced via
:func:`._splice.splice_body` at the read-style ``offset``/``limit``
coordinates, and the *spliced result* is validated as a whole document and
persisted verbatim instead of the raw fragment. ``sop`` is the first domain
built dispatch-only from day one (ADR 36905d5b): its ``_update_sop`` adapter was
written directly in this shape rather than ported from a retired
per-domain tool.

The parameter is intentionally named ``type`` (it matches the frontmatter
field vocabulary the client already knows); no enabled ruff rule objects to
the builtin shadow. The 11-way union return type is annotation-only -- the
MCP input schema is built from the parameters, and the SDK serializes
whichever concrete document is returned.

``feat`` is the one domain whose adapter (``_update_feat``) diverges from
the other ten's identical shape in how it resolves ``id``: via
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

### `_update_dec(id_: 'str', content: 'str', offset: 'int | None', limit: 'int | None') -> 'DecDocument'`

Replace the body of the decision identified by ``id_`` (whole-body or line-range mode).

Verbatim port of the previous per-domain decision update tool's
function body (same ``dec_lock``, ``load_by_id``, frontmatter carry-over
with only ``updated`` bumped, ``write_dec_file``, ``DecNotFoundError``;
that per-domain tool was retired in feat-22 Phase 8, when the DEC
domain -- merged from dev while still on the old per-domain mechanism
-- was converted to the generic tools), plus the REQ-002 range branch
(see :func:`_update_req`).


### `_update_feat(id_: 'str', content: 'str', offset: 'int | None', limit: 'int | None') -> 'FeatDocument'`

Replace the body of the feature identified by ``id_`` (whole-body or line-range mode).

Mirrors :func:`_update_dec`'s shape (same ``feat_lock``, ``load_by_id``,
``write_feat_file``, ``FeatNotFoundError``) with one feat-only
divergence (see the module docstring): ``id_`` resolves via
``feat.tools._paths``'s bespoke folder-per-document shortcut (through
``load_by_id``/``feat_base_dir``), not a flat-file directory scan.
``updated`` is bumped to the same microsecond timestamp as every other
domain.


### `_update_gol(id_: 'str', content: 'str', offset: 'int | None', limit: 'int | None') -> 'GolDocument'`

Replace the body of the goal identified by ``id_`` (whole-body or line-range mode).

Verbatim port of the previous per-domain goal update tool's function
body (same ``gol_lock``, ``load_by_id``, frontmatter carry-over with
only ``updated`` bumped, ``write_gol_file``, ``GolNotFoundError``; that
per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
branch (see :func:`_update_req`).


### `_update_prb(id_: 'str', content: 'str', offset: 'int | None', limit: 'int | None') -> 'PrbDocument'`

Replace the body of the problem statement identified by ``id_`` (whole-body or line-range mode).

Verbatim port of the previous per-domain problem statement update
tool's function body (same ``prb_lock``, ``load_by_id``, frontmatter
carry-over with only ``updated`` bumped, ``write_prb_file``,
``PrbNotFoundError``; that per-domain tool was retired in feat-22
Phase 3), plus the REQ-002 range branch (see :func:`_update_req`).


### `_update_qa(id_: 'str', content: 'str', offset: 'int | None', limit: 'int | None') -> 'QaDocument'`

Replace the body of the QA document identified by ``id_`` (whole-body or line-range mode).

Verbatim port of the previous per-domain QA document update tool's
function body (same ``qa_lock``, ``load_by_id``, frontmatter carry-over
with only ``updated`` bumped, ``write_qa_file``, ``QaNotFoundError``;
that per-domain tool was retired in feat-22 Phase 3), plus the REQ-002
range branch (see :func:`_update_req`).


### `_update_req(id_: 'str', content: 'str', offset: 'int | None', limit: 'int | None') -> 'ReqDocument'`

Replace the body of the requirement identified by ``id_`` (whole-body or line-range mode).

Verbatim port of the previous per-domain requirement update tool's
function body (same ``req_lock``, ``load_by_id``, frontmatter carry-over
with only ``updated`` bumped, ``write_req_file``, ``ReqNotFoundError``;
that per-domain tool was retired in feat-22 Phase 3), plus the REQ-002
range branch: with ``offset`` given (``limit`` optional; ``limit``
without ``offset`` is rejected by the public :func:`update` guard
before dispatch), the on-disk body is re-read via :func:`body_text`,
spliced via :func:`splice_body` at the read-style ``offset``/``limit``
coordinates, and the *spliced result* is validated and persisted
verbatim instead of the raw fragment.


### `_update_rsk(id_: 'str', content: 'str', offset: 'int | None', limit: 'int | None') -> 'RskDocument'`

Replace the body of the risk identified by ``id_`` (whole-body or line-range mode).

Verbatim port of the previous per-domain risk update tool's function
body (same ``rsk_lock``, ``load_by_id``, frontmatter carry-over with
only ``updated`` bumped, ``write_rsk_file``, ``RskNotFoundError``; that
per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
branch (see :func:`_update_req`).


### `_update_sop(id_: 'str', content: 'str', offset: 'int | None', limit: 'int | None') -> 'SopDocument'`

Replace the body of the SOP identified by ``id_`` (whole-body or line-range mode).

Verbatim-shape port of :func:`_update_dec` (same ``sop_lock``,
``load_by_id``, frontmatter carry-over with only ``updated`` bumped,
``write_sop_file``, ``SopNotFoundError``; ``sop`` is the first domain
built dispatch-only from day one per ADR 36905d5b, so there was never a
per-domain ``update_sop`` tool to port -- this adapter was written
directly in this shape), plus the REQ-002 range branch
(see :func:`_update_req`).


### `_update_tsk(id_: 'str', content: 'str', offset: 'int | None', limit: 'int | None') -> 'TskDocument'`

Replace the body of the task list identified by ``id_`` (whole-body or line-range mode).

Verbatim port of the previous per-domain task list update tool's
function body (same ``tsk_lock``, ``load_by_id``, frontmatter carry-over
with only ``updated`` bumped, ``write_tsk_file``, ``TskNotFoundError``;
that per-domain tool was retired in feat-22 Phase 3), plus the REQ-002
range branch (see :func:`_update_req`).


### `_update_uc(id_: 'str', content: 'str', offset: 'int | None', limit: 'int | None') -> 'UcDocument'`

Replace the body of the use case identified by ``id_`` (whole-body or line-range mode).

Verbatim port of the previous per-domain use-case update tool's function
body (same ``uc_lock``, ``load_by_id``, frontmatter carry-over with only
``updated`` bumped, ``write_uc_file``, ``UcNotFoundError``; that
per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
branch (see :func:`_update_req`).


### `_update_vcr(id_: 'str', content: 'str', offset: 'int | None', limit: 'int | None') -> 'VcrDocument'`

Replace the body of the verification case record identified by ``id_`` (whole-body or line-range mode).

Mirrors :func:`_update_dec`'s shape (same ``vcr_lock``, ``load_by_id``,
frontmatter carry-over with only ``updated`` bumped, ``write_vcr_file``,
``VcrNotFoundError``), plus the REQ-002 range branch (see
:func:`_update_req`).


### `update(id: 'str', type: "Literal['req', 'uc', 'tsk', 'qa', 'prb', 'gol', 'rsk', 'dec', 'sop', 'feat', 'vcr']", content: 'str', offset: 'int | None' = None, limit: 'int | None' = None) -> '_UpdateDocument'`

Replace the body of an existing document, in whole-body or line-range mode.

Cross-domain generic for the eleven whole-body document types
(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``);
dispatches on ``type`` to the domain's own ported adapter (same lock,
same id resolution, same frontmatter carry-over, same verbatim
persistence, same domain not-found error).

**Whole-body mode** (no ``offset``/``limit``): ``content`` is body
markdown only, with no YAML frontmatter block -- the same shape the
per-domain ``update_<d>`` tools accept. Validated the same way: the
domain body model's ``from_text(format_text(content))``, letting
``AssertionError`` (structural failure) or ``pydantic.ValidationError``
(field/cross-field failure) propagate uncaught, with nothing written in
either case.

**Range mode** (``offset`` given): ``content`` is a replacement
*fragment* addressed by read-style ``offset``/``limit`` coordinates,
where ``N`` is the number of lines of the current frontmatter-stripped
body (the text ``get_<d>(id, raw=True)`` returns) and ``N+1`` is the
virtual end-of-body position (one past the last line). ``offset`` is
the 1-based first body line to replace; ``limit`` is the number of
lines to replace -- the replaced range is ``offset..offset+limit-1``:
an omitted ``limit`` replaces through the last body line, ``limit=0``
is a pure insert of ``content``'s lines before line ``offset`` (with
``offset=N+1`` that is the append case), and ``offset=N+1`` appends
after the last line. The on-disk body is re-read under the domain
lock, spliced (drop the range's lines, insert the fragment's lines at
position ``offset - 1``), and the *spliced result* -- not the fragment
-- is validated as a whole body exactly like whole-body mode and then
persisted verbatim, so unchanged regions of the on-disk body stay
byte-identical. An empty ``content`` deletes the range (legal iff the
result still validates). The YAML frontmatter is never addressable:
coordinates are body-relative by construction.

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
    ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``, ``feat``,
    ``vcr``.
content:
    Whole-body mode: the replacement body markdown, with no
    frontmatter block. Range mode: the replacement fragment for the
    lines ``offset..offset+limit-1`` (may be empty to delete the
    range).
offset:
    Optional 1-based first body line to replace; allowed ``1..N+1``,
    where ``N+1`` (one past the last body line) is the virtual
    end-of-body position. A given ``offset`` enters range mode; on its
    own it replaces through the last body line.
limit:
    Optional number of lines to replace starting at ``offset``
    (``0`` = pure insert); must be given together with ``offset``
    (``limit`` without ``offset`` is a ``ValueError``).

Returns
-------
ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument |
GolDocument | RskDocument | DecDocument | FeatDocument | SopDocument |
VcrDocument
    The updated document of the dispatched domain type.

Raises
------
ValueError
    Misused range coordinates: ``limit`` given without ``offset``
    (raised before any file access), or ``offset < 1``,
    ``offset > N + 1``, ``limit < 0``, or ``offset + limit - 1 > N``
    (raised after the on-disk body is read; the message names the
    offending value(s) and the allowed range). Nothing is written in
    any of these cases.
AssertionError
    The (spliced) body is structurally invalid (e.g. a range that
    deletes the H1). Nothing is written.
pydantic.ValidationError
    A field/cross-field validation failure in the (spliced) body (e.g.
    a range producing an out-of-vocabulary value). Nothing is written.
ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError /
PrbNotFoundError / GolNotFoundError / RskNotFoundError / DecNotFoundError /
FeatNotFoundError / SopNotFoundError / VcrNotFoundError
    No document of the dispatched ``type`` has this id -- the
    domain's own not-found error, unchanged from the per-domain tools.

