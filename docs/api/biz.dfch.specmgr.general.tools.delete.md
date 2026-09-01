# `biz.dfch.specmgr.general.tools.delete`

``@mcp.tool()`` wrapper: delete (feat-36-delete, Phase 2).

The generic, cross-domain hard-delete tool for the eleven whole-body
document types (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/
``dec``/``sop``/``feat``/``vcr``). It dispatches on the explicit ``type``
parameter to a private per-domain adapter (``_delete_<d>``), each of which
resolves the document by ``id`` through the domain's own ``load_by_id``
(guaranteeing a valid, parseable document of that domain with that exact
``id`` before anything is removed -- the parsed document is discarded, only
the path is needed), takes the domain's own per-id lock around the whole
resolve-then-delete sequence (the very lock the generic ``update`` and
``set_status`` tools take for the same id, so a concurrent same-id mutation
cannot interleave with the delete), and hard-deletes the document from
disk: the single ``*.md`` file for the ten flat domains
(``Path.unlink``), or the entire ``<base>/<id>/`` folder for ``feat``
(``shutil.rmtree`` -- deleting ``README.md``, any ``history.md``, and any
session transcripts in that folder; ``feat`` is folder-per-document, ADR
8cf940c5). On success the adapter returns the deleted path as a ``str``
(the file path for the flat domains, the folder path for ``feat``).

Safety (REQ-003): the public :func:`delete` validates ``id`` via
:func:`_path_safety.validate_id` (no ``/``, no ``\``, no ``..``, plus the
domain's own format -- canonical lowercase-hex UUID for the ten UUID
domains, ``feat-NNN-slug`` for ``feat``) **before** any filesystem access,
so a path-injection attempt or a wrong-format id is a ``ValueError`` raised
before dispatch. Each adapter additionally confines the resolved path to
the domain's own base directory with :func:`_path_safety.assert_within`
inside the lock -- defense-in-depth against any future gap in the id
validation (it needs the resolved path, available only there).

Error contract (REQ-005): a missing document raises the domain's own
``XNotFoundError`` (propagated unchanged from ``load_by_id`` -- the
adapter does not catch it); an I/O failure during the actual
``unlink``/``rmtree`` (``OSError``/``PermissionError``/race) is caught and
re-raised as :class:`DeleteError` carrying the resolved path and the
underlying ``OSError`` as ``__cause__``.

ADR is deliberately *not* a ``type`` here: it never had a ``delete_adr``
stub, and hard-deleting an ADR could break other ADRs' "superseded by X"
cross-references (see ``.specmgr/feat/feat-36-delete/README.md``'s
Decisions Made).

The parameter is intentionally named ``type`` (it matches the frontmatter
field vocabulary the client already knows); no enabled ruff rule objects
to the builtin shadow.

## Classes

### `DeleteError`

A delete failed at the filesystem layer (I/O error, permission, or race).

Carries the resolved path and the underlying ``OSError`` as
``__cause__`` so the MCP host can surface a meaningful message to the
caller (REQ-005).

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `_delete_dec(id_: 'str') -> 'str'`

Hard-delete the decision ``id_`` from disk (REQ-001/004/005/006).

Same resolve/lock/safety semantics as :func:`_delete_req`.


### `_delete_feat(id_: 'str') -> 'str'`

Hard-delete the feature ``id_`` from disk (REQ-001/004/005/006).

``feat`` is folder-per-document (ADR 8cf940c5), so the deletion target
is the entire containing ``<base>/<id_>/`` folder (removed via
``shutil.rmtree`` -- deleting ``README.md``, any ``history.md``, and
any session transcripts in that folder), not the ``README.md`` file,
and the folder path is what is returned -- see :func:`_delete_req` for
the shared resolve/lock/safety semantics.


### `_delete_gol(id_: 'str') -> 'str'`

Hard-delete the goal ``id_`` from disk (REQ-001/004/005/006).

Same resolve/lock/safety semantics as :func:`_delete_req`.


### `_delete_prb(id_: 'str') -> 'str'`

Hard-delete the problem statement ``id_`` from disk (REQ-001/004/005/006).

Same resolve/lock/safety semantics as :func:`_delete_req`.


### `_delete_qa(id_: 'str') -> 'str'`

Hard-delete the QA document ``id_`` from disk (REQ-001/004/005/006).

Same resolve/lock/safety semantics as :func:`_delete_req`.


### `_delete_req(id_: 'str') -> 'str'`

Hard-delete the requirement ``id_`` from disk (REQ-001/004/005/006).

Resolves the document via the domain's own ``load_req_by_id`` (the
parsed document is discarded -- only the path is needed; this also
guarantees a valid, parseable document before removal), takes
``req_lock`` around the whole resolve-then-delete sequence, confines
the resolved path to the requirement base directory, and removes the
single ``*.md`` file. The domain's own ``ReqNotFoundError`` propagates
unchanged; an ``unlink`` I/O failure re-raises as
:class:`DeleteError`.


### `_delete_rsk(id_: 'str') -> 'str'`

Hard-delete the risk ``id_`` from disk (REQ-001/004/005/006).

Same resolve/lock/safety semantics as :func:`_delete_req`.


### `_delete_sop(id_: 'str') -> 'str'`

Hard-delete the SOP ``id_`` from disk (REQ-001/004/005/006) -- see :func:`_delete_req` for the full semantics.


### `_delete_tsk(id_: 'str') -> 'str'`

Hard-delete the task list ``id_`` from disk (REQ-001/004/005/006).

Same resolve/lock/safety semantics as :func:`_delete_req`.


### `_delete_uc(id_: 'str') -> 'str'`

Hard-delete the use case ``id_`` from disk (REQ-001/004/005/006).

Same resolve/lock/safety semantics as :func:`_delete_req`.


### `_delete_vcr(id_: 'str') -> 'str'`

Hard-delete the verification case record ``id_`` from disk (REQ-001/004/005/006).

Same resolve/lock/safety semantics as :func:`_delete_req`.


### `delete(id: 'str', type: "Literal['req', 'uc', 'tsk', 'qa', 'prb', 'gol', 'rsk', 'dec', 'sop', 'feat', 'vcr']") -> 'str'`

Permanently delete an existing document from disk, across the eleven whole-body domains.

Cross-domain generic for every whole-body document type
(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/
``sop``/``feat``/``vcr``); dispatches on ``type`` to the domain's own
private adapter (same id resolution via the domain's ``load_by_id``,
same per-id domain lock around the whole resolve-then-delete sequence,
same domain not-found error). The ten flat domains remove their single
``*.md`` file; ``feat`` removes its entire ``<base>/<id>/`` folder
(``README.md``, any ``history.md``, any session transcripts --
folder-per-document, ADR 8cf940c5).

The ``id`` is validated before any filesystem access: a path-injection
attempt (``/``, ``\``, or ``..``) or a wrong-format id (not a canonical
lowercase-hex UUID for the ten UUID domains, or not a
``feat-NNN-slug`` for ``feat``) is a ``ValueError`` raised before
dispatch. The resolved path is additionally confined to the domain's
own base directory (defense-in-depth) inside the lock.

ADR is not a supported ``type``: it never had a ``delete_adr`` stub,
and hard-deleting an ADR could break other ADRs' "superseded by X"
cross-references.

Parameters
----------
id:
    The document's specmgr-assigned identifier (the ``feat-NNN-slug``
    folder name for ``feat``).
type:
    The document type / domain: one of ``req``, ``uc``, ``tsk``,
    ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``, ``feat``,
    ``vcr``.

Returns
-------
str
    The deleted path: the ``*.md`` file path for the ten flat
    domains, the folder path for ``feat``.

Raises
------
ValueError
    ``id`` is a path-injection attempt or not in the dispatched
    domain's own format (raised before any filesystem access; nothing
    is deleted).
ReqNotFoundError / UcNotFoundError / TskNotFoundError /
QaNotFoundError / PrbNotFoundError / GolNotFoundError /
RskNotFoundError / DecNotFoundError / SopNotFoundError /
FeatNotFoundError / VcrNotFoundError
    No document of the dispatched ``type`` has this id -- the
    domain's own not-found error, propagated unchanged from the
    domain's own ``load_by_id``.
DeleteError
    The filesystem ``unlink``/``rmtree`` itself failed (I/O error,
    permission, or race); wraps the underlying ``OSError`` as
    ``__cause__`` and names the resolved path.

