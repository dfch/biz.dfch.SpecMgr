# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=redefined-builtin  # id/type intentionally shadow the builtins: public tool API, issue #41

"""``@mcp.tool()`` wrapper: delete (feat-36-delete, Phase 2).

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
:func:`_path_safety.validate_id` (no ``/``, no ``\\``, no ``..``, plus the
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
"""

from __future__ import annotations

import shutil
from collections.abc import Callable
from typing import Literal

from ...dec.tools._io import load_by_id as load_dec_by_id
from ...dec.tools._lock import dec_lock
from ...dec.tools._paths import dec_base_dir
from ...feat.tools._io import load_by_id as load_feat_by_id
from ...feat.tools._lock import feat_lock
from ...feat.tools._paths import feat_base_dir
from ...gol.tools._io import load_by_id as load_gol_by_id
from ...gol.tools._lock import gol_lock
from ...gol.tools._paths import gol_base_dir
from ...prb.tools._io import load_by_id as load_prb_by_id
from ...prb.tools._lock import prb_lock
from ...prb.tools._paths import prb_base_dir
from ...qa.tools._io import load_by_id as load_qa_by_id
from ...qa.tools._lock import qa_lock
from ...qa.tools._paths import qa_base_dir
from ...req.tools._io import load_by_id as load_req_by_id
from ...req.tools._lock import req_lock
from ...req.tools._paths import req_base_dir
from ...rsk.tools._io import load_by_id as load_rsk_by_id
from ...rsk.tools._lock import rsk_lock
from ...rsk.tools._paths import rsk_base_dir
from ...server import mcp
from ...sop.tools._io import load_by_id as load_sop_by_id
from ...sop.tools._lock import sop_lock
from ...sop.tools._paths import sop_base_dir
from ...tsk.tools._io import load_by_id as load_tsk_by_id
from ...tsk.tools._lock import tsk_lock
from ...tsk.tools._paths import tsk_base_dir
from ...uc.tools._io import load_by_id as load_uc_by_id
from ...uc.tools._lock import uc_lock
from ...uc.tools._paths import uc_base_dir
from ...vcr.tools._io import load_by_id as load_vcr_by_id
from ...vcr.tools._lock import vcr_lock
from ...vcr.tools._paths import vcr_base_dir
from ._path_safety import assert_within, validate_id

__all__ = ["delete"]

#: The eleven whole-body domains the generic delete tool covers (ADR excluded).
_DELETE_TYPES = ("req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "feat", "vcr")


class DeleteError(OSError):
    """A delete failed at the filesystem layer (I/O error, permission, or race).

    Carries the resolved path and the underlying ``OSError`` as
    ``__cause__`` so the MCP host can surface a meaningful message to the
    caller (REQ-005).
    """


def _delete_req(id_: str) -> str:
    """Hard-delete the requirement ``id_`` from disk (REQ-001/004/005/006).

    Resolves the document via the domain's own ``load_req_by_id`` (the
    parsed document is discarded -- only the path is needed; this also
    guarantees a valid, parseable document before removal), takes
    ``req_lock`` around the whole resolve-then-delete sequence, confines
    the resolved path to the requirement base directory, and removes the
    single ``*.md`` file. The domain's own ``ReqNotFoundError`` propagates
    unchanged; an ``unlink`` I/O failure re-raises as
    :class:`DeleteError`.
    """
    base_dir = req_base_dir()
    with req_lock(id_):  # REQ-004
        path, _existing = load_req_by_id(base_dir, id_)  # resolves + ReqNotFoundError
        assert_within(base_dir, path)  # REQ-003 defense-in-depth
        try:
            path.unlink()  # REQ-006
        except OSError as ex:
            raise DeleteError(f"failed to delete {path}: {ex}") from ex  # REQ-005
    return str(path)  # REQ-001


def _delete_uc(id_: str) -> str:
    """Hard-delete the use case ``id_`` from disk (REQ-001/004/005/006).

    Same resolve/lock/safety semantics as :func:`_delete_req`.
    """
    base_dir = uc_base_dir()
    with uc_lock(id_):  # REQ-004
        path, _existing = load_uc_by_id(base_dir, id_)  # resolves + UcNotFoundError
        assert_within(base_dir, path)  # REQ-003 defense-in-depth
        try:
            path.unlink()  # REQ-006
        except OSError as ex:
            raise DeleteError(f"failed to delete {path}: {ex}") from ex  # REQ-005
    return str(path)  # REQ-001


def _delete_tsk(id_: str) -> str:
    """Hard-delete the task list ``id_`` from disk (REQ-001/004/005/006).

    Same resolve/lock/safety semantics as :func:`_delete_req`.
    """
    base_dir = tsk_base_dir()
    with tsk_lock(id_):  # REQ-004
        path, _existing = load_tsk_by_id(base_dir, id_)  # resolves + TskNotFoundError
        assert_within(base_dir, path)  # REQ-003 defense-in-depth
        try:
            path.unlink()  # REQ-006
        except OSError as ex:
            raise DeleteError(f"failed to delete {path}: {ex}") from ex  # REQ-005
    return str(path)  # REQ-001


def _delete_qa(id_: str) -> str:
    """Hard-delete the QA document ``id_`` from disk (REQ-001/004/005/006).

    Same resolve/lock/safety semantics as :func:`_delete_req`.
    """
    base_dir = qa_base_dir()
    with qa_lock(id_):  # REQ-004
        path, _existing = load_qa_by_id(base_dir, id_)  # resolves + QaNotFoundError
        assert_within(base_dir, path)  # REQ-003 defense-in-depth
        try:
            path.unlink()  # REQ-006
        except OSError as ex:
            raise DeleteError(f"failed to delete {path}: {ex}") from ex  # REQ-005
    return str(path)  # REQ-001


def _delete_prb(id_: str) -> str:
    """Hard-delete the problem statement ``id_`` from disk (REQ-001/004/005/006).

    Same resolve/lock/safety semantics as :func:`_delete_req`.
    """
    base_dir = prb_base_dir()
    with prb_lock(id_):  # REQ-004
        path, _existing = load_prb_by_id(base_dir, id_)  # resolves + PrbNotFoundError
        assert_within(base_dir, path)  # REQ-003 defense-in-depth
        try:
            path.unlink()  # REQ-006
        except OSError as ex:
            raise DeleteError(f"failed to delete {path}: {ex}") from ex  # REQ-005
    return str(path)  # REQ-001


def _delete_gol(id_: str) -> str:
    """Hard-delete the goal ``id_`` from disk (REQ-001/004/005/006).

    Same resolve/lock/safety semantics as :func:`_delete_req`.
    """
    base_dir = gol_base_dir()
    with gol_lock(id_):  # REQ-004
        path, _existing = load_gol_by_id(base_dir, id_)  # resolves + GolNotFoundError
        assert_within(base_dir, path)  # REQ-003 defense-in-depth
        try:
            path.unlink()  # REQ-006
        except OSError as ex:
            raise DeleteError(f"failed to delete {path}: {ex}") from ex  # REQ-005
    return str(path)  # REQ-001


def _delete_rsk(id_: str) -> str:
    """Hard-delete the risk ``id_`` from disk (REQ-001/004/005/006).

    Same resolve/lock/safety semantics as :func:`_delete_req`.
    """
    base_dir = rsk_base_dir()
    with rsk_lock(id_):  # REQ-004
        path, _existing = load_rsk_by_id(base_dir, id_)  # resolves + RskNotFoundError
        assert_within(base_dir, path)  # REQ-003 defense-in-depth
        try:
            path.unlink()  # REQ-006
        except OSError as ex:
            raise DeleteError(f"failed to delete {path}: {ex}") from ex  # REQ-005
    return str(path)  # REQ-001


def _delete_dec(id_: str) -> str:
    """Hard-delete the decision ``id_`` from disk (REQ-001/004/005/006).

    Same resolve/lock/safety semantics as :func:`_delete_req`.
    """
    base_dir = dec_base_dir()
    with dec_lock(id_):  # REQ-004
        path, _existing = load_dec_by_id(base_dir, id_)  # resolves + DecNotFoundError
        assert_within(base_dir, path)  # REQ-003 defense-in-depth
        try:
            path.unlink()  # REQ-006
        except OSError as ex:
            raise DeleteError(f"failed to delete {path}: {ex}") from ex  # REQ-005
    return str(path)  # REQ-001


def _delete_sop(id_: str) -> str:
    """Hard-delete the SOP ``id_`` from disk (REQ-001/004/005/006) -- see :func:`_delete_req` for the full semantics."""
    base_dir = sop_base_dir()
    with sop_lock(id_):  # REQ-004
        path, _existing = load_sop_by_id(base_dir, id_)  # resolves + SopNotFoundError
        assert_within(base_dir, path)  # REQ-003 defense-in-depth
        try:
            path.unlink()  # REQ-006
        except OSError as ex:
            raise DeleteError(f"failed to delete {path}: {ex}") from ex  # REQ-005
    return str(path)  # REQ-001


def _delete_feat(id_: str) -> str:
    """Hard-delete the feature ``id_`` from disk (REQ-001/004/005/006).

    ``feat`` is folder-per-document (ADR 8cf940c5), so the deletion target
    is the entire containing ``<base>/<id_>/`` folder (removed via
    ``shutil.rmtree`` -- deleting ``README.md``, any ``history.md``, and
    any session transcripts in that folder), not the ``README.md`` file,
    and the folder path is what is returned -- see :func:`_delete_req` for
    the shared resolve/lock/safety semantics.
    """
    base_dir = feat_base_dir()
    with feat_lock(id_):  # REQ-004
        path, _existing = load_feat_by_id(base_dir, id_)  # resolves + FeatNotFoundError (<base>/<id>/README.md)
        folder = path.parent
        assert_within(base_dir, folder)  # REQ-003 defense-in-depth
        try:
            shutil.rmtree(folder)  # REQ-006: whole folder
        except OSError as ex:
            raise DeleteError(f"failed to delete {folder}: {ex}") from ex  # REQ-005
    return str(folder)  # REQ-001


def _delete_vcr(id_: str) -> str:
    """Hard-delete the verification case record ``id_`` from disk (REQ-001/004/005/006).

    Same resolve/lock/safety semantics as :func:`_delete_req`.
    """
    base_dir = vcr_base_dir()
    with vcr_lock(id_):  # REQ-004
        path, _existing = load_vcr_by_id(base_dir, id_)  # resolves + VcrNotFoundError
        assert_within(base_dir, path)  # REQ-003 defense-in-depth
        try:
            path.unlink()  # REQ-006
        except OSError as ex:
            raise DeleteError(f"failed to delete {path}: {ex}") from ex  # REQ-005
    return str(path)  # REQ-001


#: Dispatch table mapping the ``type`` value to its private adapter.
_ADAPTERS: dict[str, Callable[[str], str]] = {
    "req": _delete_req,
    "uc": _delete_uc,
    "tsk": _delete_tsk,
    "qa": _delete_qa,
    "prb": _delete_prb,
    "gol": _delete_gol,
    "rsk": _delete_rsk,
    "dec": _delete_dec,
    "sop": _delete_sop,
    "feat": _delete_feat,
    "vcr": _delete_vcr,
}


@mcp.tool(
    name="delete",
    title="Delete document",
    description=(
        "Permanently delete an existing document from disk across the eleven whole-body "
        "domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr; "
        "`adr` is not supported). Resolves the document by `id`, takes the domain lock, "
        "and removes it: the single `*.md` file for the ten flat domains, or the entire "
        "`<base>/<id>/` folder for `feat`. Returns the deleted path as a string. "
        "An invalid `id` (path-injection attempt or wrong format) is a `ValueError` "
        "raised before any file access; a missing document is the domain's own "
        "`XNotFoundError`; an I/O failure is a `DeleteError`. This is the sole "
        "delete entry point -- the former per-domain `delete_<d>` tools are removed."
    ),
)
def delete(
    id: str,
    type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "feat", "vcr"],
) -> str:
    """Permanently delete an existing document from disk, across the eleven whole-body domains.

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
    attempt (``/``, ``\\``, or ``..``) or a wrong-format id (not a canonical
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
    """
    # REQ-003: validate before any filesystem access (injection prevention).
    validate_id(type, id)
    result = _ADAPTERS[type](id)
    return result
