# `biz.dfch.specmgr.general.tools.set_classification`

``@mcp.tool()`` wrapper: set_classification (feat-56-classification, Phase 2).

The generic, cross-domain classification-change tool for the twelve
whole-body document types
(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/``sysrs``).
Unlike the 13-way ``set_status`` (``general/tools/set_status.py``), ``adr``
is deliberately excluded here: ADR's separate ``AdrFrontmatter`` model
(``models/adr/``) is out of scope for the ``classification`` field entirely
(``.specmgr/feat/feat-56-classification-attribute-in-frontmatter/README.md``
Scope section) -- there is no ADR adapter, no ``superseded_by``-style
parameter, and no 12th entry in the dispatch table.

It dispatches on the explicit ``type`` parameter to a private per-domain
adapter (``_set_classification_<d>``), each shaped exactly like
``set_status.py``'s corresponding ``_set_status_<d>`` adapter (same domain
lock, same ``load_by_id``, same ``_path_safety.assert_within`` guard, same
raw-body re-read via the established ``frontmatter.loads(...).content``
mechanism and verbatim re-persistence) but replacing ``classification``
instead of ``status`` in the reconstructed frontmatter. ``sop`` is built
dispatch-only from day one (ADR 36905d5b-8057-4294-8665-c7eed5534db0), so
its ``_set_classification_sop`` adapter was written directly in this shape
rather than ported from any retired per-domain tool -- true of every
adapter in this module, since ``set_classification`` itself is new
(there was never a per-domain ``set_classification_<d>`` tool to port).

The ``feat`` adapter (``_set_classification_feat``) diverges from the other
ten whole-body domains' identical shape in the same way
``_update_feat``/``_set_status_feat`` do: it resolves ``id`` via
``feat.tools._paths``'s bespoke folder-per-document shortcut, not a
flat-file directory scan (see ``.specmgr/feat/feat-31-feature/README.md``
Design Notes). It bumps ``updated`` to the same shared date+time timestamp
(via ``general.tools._timestamps.now_timestamp()``) as every other domain.

The parameter is intentionally named ``type`` (it matches the frontmatter
field vocabulary the client already knows); no enabled ruff rule objects
to the builtin shadow. The 12-way union return type is annotation-only --
the MCP input schema is built from the parameters, and the SDK serializes
whichever concrete document is returned.

Blank/whitespace-only ``classification`` values clear the field back to
``None``/absent automatically: the domain's ``XFrontmatter`` inherits the
shared ``MarkdownFrontmatter``'s own blank-to-``None`` validator
(feat-56-classification Phase 1), so the raw string is passed through to
the ``XFrontmatter(**fm_data)`` reconstruction unmodified -- no
special-casing for blank input lives in this module.

No ``create_<d>`` tool accepts a ``classification`` argument (explicitly
rejected in favor of this single generic tool, per the feature's Scope
section) -- ``set_classification`` is the sole classification-change entry
point for every domain.

Safety (mirroring ``set_status``'s/``update``'s/``delete``'s own REQ-009/
REQ-003): the public :func:`set_classification` validates ``id`` via
``_path_safety.validate_id`` before dispatch (a ``ValueError`` before any
filesystem access), and every adapter confines the resolved path to the
domain's own base directory with ``_path_safety.assert_within`` after
``load_by_id``, inside the domain lock.

Since feat-27-validation added ``wrap_tool_errors``/``FRONTMATTER_CHANNEL``
(``models/md/_errors.py``) and already applies it to every ``set_status.py``
adapter around its ``XFrontmatter(**fm_data)`` reconstruction call, every
adapter here wraps its own reconstruction the same way (``domain="<d>"``,
``tool="set_classification"``, ``channel=FRONTMATTER_CHANNEL``) -- per the
feature's own Design Notes, skipping this would regress this tool's errors
to a pre-feat-27 bare/unhelpful shape while every sibling tool has the
enriched (field path + line reference + fix hint) shape.

## Functions

### `_set_classification_dec(id_: 'str', classification: 'str') -> 'DecFrontmatter'`

Replace the classification of the decision identified by ``id_``.

See :func:`_set_classification_req` for the full semantics (same
``dec_lock``, ``load_by_id``, ``write_dec_file``, ``DecNotFoundError``).


### `_set_classification_feat(id_: 'str', classification: 'str') -> 'FeatFrontmatter'`

Replace the classification of the feature identified by ``id_``.

Mirrors :func:`_set_classification_dec`'s shape (same ``feat_lock``,
``load_by_id``, ``write_feat_file``, ``FeatNotFoundError``) -- see
:func:`_set_classification_req` for the full semantics -- with the same
feat-only divergence ``_update_feat``/``_set_status_feat`` document:
``id_`` resolves via ``feat.tools._paths``'s bespoke folder-per-document
shortcut, not a flat-file directory scan. ``updated`` is bumped to the
same shared date+time timestamp as every other domain.


### `_set_classification_gol(id_: 'str', classification: 'str') -> 'GolFrontmatter'`

Replace the classification of the goal identified by ``id_``.

See :func:`_set_classification_req` for the full semantics (same
``gol_lock``, ``load_by_id``, ``write_gol_file``, ``GolNotFoundError``).


### `_set_classification_prb(id_: 'str', classification: 'str') -> 'PrbFrontmatter'`

Replace the classification of the problem statement identified by ``id_``.

See :func:`_set_classification_req` for the full semantics (same
``prb_lock``, ``load_by_id``, ``write_prb_file``, ``PrbNotFoundError``).


### `_set_classification_qa(id_: 'str', classification: 'str') -> 'QaFrontmatter'`

Replace the classification of the QA document identified by ``id_``.

See :func:`_set_classification_req` for the full semantics (same
``qa_lock``, ``load_by_id``, ``write_qa_file``, ``QaNotFoundError``).


### `_set_classification_req(id_: 'str', classification: 'str') -> 'ReqFrontmatter'`

Replace the classification of the requirement identified by ``id_``.

Shaped exactly like :func:`~.set_status._set_status_req` (same
``req_lock``, ``load_by_id``, raw-body re-read via the established
``frontmatter.loads(...).content`` mechanism and verbatim
re-persistence, frontmatter reconstructed through :class:`ReqFrontmatter`'s
own constructor, ``write_req_file``, ``ReqNotFoundError``), replacing
``classification`` instead of ``status``.


### `_set_classification_rsk(id_: 'str', classification: 'str') -> 'RskFrontmatter'`

Replace the classification of the risk identified by ``id_``.

See :func:`_set_classification_req` for the full semantics (same
``rsk_lock``, ``load_by_id``, ``write_rsk_file``, ``RskNotFoundError``).


### `_set_classification_sop(id_: 'str', classification: 'str') -> 'SopFrontmatter'`

Replace the classification of the SOP identified by ``id_``.

Verbatim-shape port of :func:`_set_classification_dec` (same
``sop_lock``, ``load_by_id``, ``write_sop_file``, ``SopNotFoundError``;
``sop`` is the first domain built dispatch-only from day one per ADR
36905d5b, so this adapter was written directly in this shape) -- see
:func:`_set_classification_req` for the full semantics.


### `_set_classification_sysrs(id_: 'str', classification: 'str') -> 'SysrsFrontmatter'`

Replace the classification of the System Requirements Specification identified by ``id_``.

Mirrors :func:`_set_classification_sop`'s shape (same ``sysrs_lock``,
``load_by_id``, ``write_sysrs_file``, ``SysrsNotFoundError``; ``sysrs``
is dispatch-only from day one per ADR 36905d5b, so this adapter was
written directly in this shape) -- see :func:`_set_classification_req`
for the full semantics.


### `_set_classification_tsk(id_: 'str', classification: 'str') -> 'TskFrontmatter'`

Replace the classification of the task list identified by ``id_``.

See :func:`_set_classification_req` for the full semantics (same
``tsk_lock``, ``load_by_id``, ``write_tsk_file``, ``TskNotFoundError``).


### `_set_classification_uc(id_: 'str', classification: 'str') -> 'UcFrontmatter'`

Replace the classification of the use case identified by ``id_``.

See :func:`_set_classification_req` for the full semantics (same
``uc_lock``, ``load_by_id``, ``write_uc_file``, ``UcNotFoundError``).


### `_set_classification_vcr(id_: 'str', classification: 'str') -> 'VcrFrontmatter'`

Replace the classification of the verification case record identified by ``id_``.

Mirrors :func:`_set_classification_dec`'s shape (same ``vcr_lock``,
``load_by_id``, ``write_vcr_file``, ``VcrNotFoundError``) -- see
:func:`_set_classification_req` for the full semantics.


### `set_classification(id: 'str', type: "Literal['req', 'uc', 'tsk', 'qa', 'prb', 'gol', 'rsk', 'dec', 'sop', 'feat', 'vcr', 'sysrs']", classification: 'str') -> '_SetClassificationFrontmatter'`

Replace the ``classification`` frontmatter field of an existing document.

Cross-domain generic for the twelve whole-body document types
(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``);
dispatches on ``type`` to the domain's own adapter (same lock, same id
resolution, same body handling, same domain not-found error). ``adr``
is deliberately excluded (its separate ``AdrFrontmatter`` model is out
of scope for this feature).

The existing file's frontmatter is carried over with every field
preserved except ``classification`` (replaced) and ``updated`` (bumped
to the current date+time timestamp, via
``general.tools._timestamps.now_timestamp()``); the body is never
touched -- its raw, on-disk markdown (not a render of the parsed
model) is re-read and re-persisted verbatim.

``classification`` is fully free-text: the domain's shared
``MarkdownFrontmatter`` base normalizes a blank/whitespace-only value to
``None`` (feat-56-classification Phase 1) when the frontmatter is
reconstructed through the domain's own ``XFrontmatter`` constructor, so
passing ``""`` or whitespace here clears the field back to
``None``/absent in the rendered YAML.

Safety (mirroring ``set_status``'s/``update``'s/``delete``'s own
REQ-009/REQ-003): ``id`` is validated via ``_path_safety.validate_id``
(no ``/``, no ``\``, no ``..``, plus the dispatched domain's own
format -- canonical lowercase-hex UUID for the eleven UUID domains,
``feat-NNN-slug`` for ``feat``) **before** any filesystem access, so a
path-injection attempt, a wrong-format id, or an unsupported ``type``
is a ``ValueError`` raised before dispatch. Each adapter additionally
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
    ``vcr``, ``sysrs``.
classification:
    The new classification value. Fully free-text; a blank or
    whitespace-only value clears the field back to ``None``/absent.

Returns
-------
ReqFrontmatter | UcFrontmatter | TskFrontmatter | QaFrontmatter | PrbFrontmatter |
GolFrontmatter | RskFrontmatter | DecFrontmatter | FeatFrontmatter | SopFrontmatter |
VcrFrontmatter | SysrsFrontmatter
    The updated document's frontmatter only (no body) of the dispatched domain type;
    use the corresponding ``get_<d>`` tool to fetch the full document afterward.

Raises
------
ValueError
    ``id`` is a path-injection attempt or not in the dispatched
    domain's own format, or ``type`` is not one of the twelve
    supported domains (raised before any filesystem access; nothing
    is written).
ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError /
PrbNotFoundError / GolNotFoundError / RskNotFoundError / DecNotFoundError /
FeatNotFoundError / SopNotFoundError / VcrNotFoundError / SysrsNotFoundError
    No document of the dispatched ``type`` has this id -- the
    domain's own not-found error, unchanged from the sibling generic
    tools.

