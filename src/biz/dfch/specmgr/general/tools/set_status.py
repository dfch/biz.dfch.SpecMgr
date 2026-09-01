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

"""``@mcp.tool()`` wrapper: set_status (feat-22-consolidate-mutation-tools, Phase 4).

The generic, cross-domain status-change tool for all twelve document types
(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/``adr``).
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
to the builtin shadow. The 12-way union return type is annotation-only --
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
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

import frontmatter

from ...adr.tools._io import load_by_id as load_adr_by_id
from ...adr.tools._io import write_adr
from ...adr.tools._lock import adr_lock
from ...adr.tools._paths import adr_base_dir
from ...dec.models.v1 import DecDocument, DecFrontmatter
from ...dec.tools._io import load_by_id as load_dec_by_id
from ...dec.tools._lock import dec_lock
from ...dec.tools._paths import dec_base_dir
from ...dec.tools._write import write_dec_file
from ...feat.models.v1 import FeatDocument, FeatFrontmatter
from ...feat.tools._io import load_by_id as load_feat_by_id
from ...feat.tools._lock import feat_lock
from ...feat.tools._paths import feat_base_dir
from ...feat.tools._write import write_feat_file
from ...gol.models.v1 import GolDocument, GolFrontmatter
from ...gol.tools._io import load_by_id as load_gol_by_id
from ...gol.tools._lock import gol_lock
from ...gol.tools._paths import gol_base_dir
from ...gol.tools._write import write_gol_file
from ...models.adr import Adr
from ...models.adr.v1 import mutations
from ...prb.models.v1 import PrbDocument, PrbFrontmatter
from ...prb.tools._io import load_by_id as load_prb_by_id
from ...prb.tools._lock import prb_lock
from ...prb.tools._paths import prb_base_dir
from ...prb.tools._write import write_prb_file
from ...qa.models.v2 import QaDocument, QaFrontmatter
from ...qa.tools._io import load_by_id as load_qa_by_id
from ...qa.tools._lock import qa_lock
from ...qa.tools._paths import qa_base_dir
from ...qa.tools._write import write_qa_file
from ...req.models.v1 import ReqDocument, ReqFrontmatter
from ...req.tools._io import load_by_id as load_req_by_id
from ...req.tools._lock import req_lock
from ...req.tools._paths import req_base_dir
from ...req.tools._write import write_req_file
from ...rsk.models.v1 import RskDocument, RskFrontmatter
from ...rsk.tools._io import load_by_id as load_rsk_by_id
from ...rsk.tools._lock import rsk_lock
from ...rsk.tools._paths import rsk_base_dir
from ...rsk.tools._write import write_rsk_file
from ...server import mcp
from ...sop.models.v1 import SopDocument, SopFrontmatter
from ...sop.tools._io import load_by_id as load_sop_by_id
from ...sop.tools._lock import sop_lock
from ...sop.tools._paths import sop_base_dir
from ...sop.tools._write import write_sop_file
from ...tsk.models.v1 import TskDocument, TskFrontmatter
from ...tsk.tools._io import load_by_id as load_tsk_by_id
from ...tsk.tools._lock import tsk_lock
from ...tsk.tools._paths import tsk_base_dir
from ...tsk.tools._write import write_tsk_file
from ...uc.models.v2 import UcDocument, UcFrontmatter
from ...uc.tools._io import load_by_id as load_uc_by_id
from ...uc.tools._lock import uc_lock
from ...uc.tools._paths import uc_base_dir
from ...uc.tools._write import write_uc_file
from ...vcr.models.v1 import VcrDocument, VcrFrontmatter
from ...vcr.tools._io import load_by_id as load_vcr_by_id
from ...vcr.tools._lock import vcr_lock
from ...vcr.tools._paths import vcr_base_dir
from ...vcr.tools._write import write_vcr_file
from ._timestamps import now_timestamp

__all__ = ["set_status"]

#: The only ``type`` whose status can be composed via ``superseded_by``
#: (the ``"superseded by X"`` pattern is ADR-specific).
_TYPE_ADR = "adr"

#: The generic tool's 12-way return union -- annotation-only (see module docstring).
_SetStatusDocument = (
    ReqDocument
    | UcDocument
    | TskDocument
    | QaDocument
    | PrbDocument
    | GolDocument
    | RskDocument
    | DecDocument
    | FeatDocument
    | SopDocument
    | VcrDocument
    | Adr
)


def _set_status_req(id_: str, status: str, superseded_by: str | None) -> ReqDocument:
    """Replace the status of the requirement identified by ``id_``.

    Verbatim port of the previous per-domain requirement status tool's
    function body (same ``req_lock``, ``load_by_id``, raw-body re-read via
    the established ``frontmatter.loads(...).content`` mechanism and
    verbatim re-persistence, frontmatter reconstructed through
    :class:`ReqFrontmatter`'s own constructor so the closed status
    vocabulary validates, ``write_req_file``, ``ReqNotFoundError``; that
    per-domain tool was retired in feat-22 Phase 4). ``superseded_by`` is
    never used here -- the public :func:`set_status` guard rejects it for
    every non-``adr`` type before dispatch.
    """
    assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"

    base_dir = req_base_dir()
    with req_lock(id_):
        path, existing = load_req_by_id(base_dir, id_)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["status"] = status
        fm_data["updated"] = now
        new_frontmatter = ReqFrontmatter(**fm_data)
        new_doc = ReqDocument(frontmatter=new_frontmatter, body=existing.body)
        write_req_file(path, new_frontmatter, raw_body)
    return new_doc


def _set_status_uc(id_: str, status: str, superseded_by: str | None) -> UcDocument:
    """Replace the status of the use case identified by ``id_``.

    Verbatim port of the previous per-domain use-case status tool's
    function body (same ``uc_lock``, ``load_by_id``, ``write_uc_file``,
    ``UcNotFoundError``; that per-domain tool was retired in feat-22
    Phase 4) -- see :func:`_set_status_req` for the full semantics.
    """
    assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"

    base_dir = uc_base_dir()
    with uc_lock(id_):
        path, existing = load_uc_by_id(base_dir, id_)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["status"] = status
        fm_data["updated"] = now
        new_frontmatter = UcFrontmatter(**fm_data)
        new_doc = UcDocument(frontmatter=new_frontmatter, body=existing.body)
        write_uc_file(path, new_frontmatter, raw_body)
    return new_doc


def _set_status_tsk(id_: str, status: str, superseded_by: str | None) -> TskDocument:
    """Replace the status of the task list identified by ``id_``.

    Verbatim port of the previous per-domain task list status tool's
    function body (same ``tsk_lock``, ``load_by_id``, ``write_tsk_file``,
    ``TskNotFoundError``; that per-domain tool was retired in feat-22
    Phase 4) -- see :func:`_set_status_req` for the full semantics.
    """
    assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"

    base_dir = tsk_base_dir()
    with tsk_lock(id_):
        path, existing = load_tsk_by_id(base_dir, id_)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["status"] = status
        fm_data["updated"] = now
        new_frontmatter = TskFrontmatter(**fm_data)
        new_doc = TskDocument(frontmatter=new_frontmatter, body=existing.body)
        write_tsk_file(path, new_frontmatter, raw_body)
    return new_doc


def _set_status_qa(id_: str, status: str, superseded_by: str | None) -> QaDocument:
    """Replace the status of the QA document identified by ``id_``.

    Verbatim port of the previous per-domain QA document status tool's
    function body (same ``qa_lock``, ``load_by_id``, ``write_qa_file``,
    ``QaNotFoundError``; that per-domain tool was retired in feat-22
    Phase 4) -- see :func:`_set_status_req` for the full semantics.
    """
    assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"

    base_dir = qa_base_dir()
    with qa_lock(id_):
        path, existing = load_qa_by_id(base_dir, id_)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["status"] = status
        fm_data["updated"] = now
        new_frontmatter = QaFrontmatter(**fm_data)
        new_doc = QaDocument(frontmatter=new_frontmatter, body=existing.body)
        write_qa_file(path, new_frontmatter, raw_body)
    return new_doc


def _set_status_prb(id_: str, status: str, superseded_by: str | None) -> PrbDocument:
    """Replace the status of the problem statement identified by ``id_``.

    Verbatim port of the previous per-domain problem statement status
    tool's function body (same ``prb_lock``, ``load_by_id``,
    ``write_prb_file``, ``PrbNotFoundError``; that per-domain tool was
    retired in feat-22 Phase 4) -- see :func:`_set_status_req` for the
    full semantics.
    """
    assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"

    base_dir = prb_base_dir()
    with prb_lock(id_):
        path, existing = load_prb_by_id(base_dir, id_)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["status"] = status
        fm_data["updated"] = now
        new_frontmatter = PrbFrontmatter(**fm_data)
        new_doc = PrbDocument(frontmatter=new_frontmatter, body=existing.body)
        write_prb_file(path, new_frontmatter, raw_body)
    return new_doc


def _set_status_gol(id_: str, status: str, superseded_by: str | None) -> GolDocument:
    """Replace the status of the goal identified by ``id_``.

    Verbatim port of the previous per-domain goal status tool's function
    body (same ``gol_lock``, ``load_by_id``, ``write_gol_file``,
    ``GolNotFoundError``; that per-domain tool was retired in feat-22
    Phase 4) -- see :func:`_set_status_req` for the full semantics.
    """
    assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"

    base_dir = gol_base_dir()
    with gol_lock(id_):
        path, existing = load_gol_by_id(base_dir, id_)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["status"] = status
        fm_data["updated"] = now
        new_frontmatter = GolFrontmatter(**fm_data)
        new_doc = GolDocument(frontmatter=new_frontmatter, body=existing.body)
        write_gol_file(path, new_frontmatter, raw_body)
    return new_doc


def _set_status_rsk(id_: str, status: str, superseded_by: str | None) -> RskDocument:
    """Replace the status of the risk identified by ``id_``.

    Verbatim port of the previous per-domain risk status tool's function
    body (same ``rsk_lock``, ``load_by_id``, ``write_rsk_file``,
    ``RskNotFoundError``; that per-domain tool was retired in feat-22
    Phase 4) -- see :func:`_set_status_req` for the full semantics.
    """
    assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"

    base_dir = rsk_base_dir()
    with rsk_lock(id_):
        path, existing = load_rsk_by_id(base_dir, id_)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["status"] = status
        fm_data["updated"] = now
        new_frontmatter = RskFrontmatter(**fm_data)
        new_doc = RskDocument(frontmatter=new_frontmatter, body=existing.body)
        write_rsk_file(path, new_frontmatter, raw_body)
    return new_doc


def _set_status_dec(id_: str, status: str, superseded_by: str | None) -> DecDocument:
    """Replace the status of the decision identified by ``id_``.

    Verbatim port of the previous per-domain decision status tool's
    function body (same ``dec_lock``, ``load_by_id``, ``write_dec_file``,
    ``DecNotFoundError``; that per-domain tool was retired in feat-22
    Phase 8, when the DEC domain -- merged from dev while still on the
    old per-domain mechanism -- was converted to the generic tools) --
    see :func:`_set_status_req` for the full semantics.
    """
    assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"

    base_dir = dec_base_dir()
    with dec_lock(id_):
        path, existing = load_dec_by_id(base_dir, id_)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["status"] = status
        fm_data["updated"] = now
        new_frontmatter = DecFrontmatter(**fm_data)
        new_doc = DecDocument(frontmatter=new_frontmatter, body=existing.body)
        write_dec_file(path, new_frontmatter, raw_body)
    return new_doc


def _set_status_feat(id_: str, status: str, superseded_by: str | None) -> FeatDocument:
    """Replace the status of the feature identified by ``id_``.

    Mirrors :func:`_set_status_dec`'s shape (same ``feat_lock``,
    ``load_by_id``, ``write_feat_file``, ``FeatNotFoundError``) -- see
    :func:`_set_status_req` for the full semantics -- with the same
    feat-only divergence ``_update_feat`` (in ``update.py``) documents:
    ``id_`` resolves via ``feat.tools._paths``'s bespoke folder-per-document
    shortcut, not a flat-file directory scan. ``updated`` is bumped to the
    same shared date+time timestamp as every other domain.
    """
    assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"

    base_dir = feat_base_dir()
    with feat_lock(id_):
        path, existing = load_feat_by_id(base_dir, id_)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["status"] = status
        fm_data["updated"] = now
        new_frontmatter = FeatFrontmatter(**fm_data)
        new_doc = FeatDocument(frontmatter=new_frontmatter, body=existing.body)
        write_feat_file(path, new_frontmatter, raw_body)
    return new_doc


def _set_status_sop(id_: str, status: str, superseded_by: str | None) -> SopDocument:
    """Replace the status of the SOP identified by ``id_``.

    Verbatim-shape port of :func:`_set_status_dec` (same ``sop_lock``,
    ``load_by_id``, ``write_sop_file``, ``SopNotFoundError``; ``sop`` is the
    first domain built dispatch-only from day one per ADR 36905d5b, so there
    was never a per-domain ``set_status_sop`` tool to port -- this adapter
    was written directly in this shape) -- see :func:`_set_status_req` for
    the full semantics.
    """
    assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"

    base_dir = sop_base_dir()
    with sop_lock(id_):
        path, existing = load_sop_by_id(base_dir, id_)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["status"] = status
        fm_data["updated"] = now
        new_frontmatter = SopFrontmatter(**fm_data)
        new_doc = SopDocument(frontmatter=new_frontmatter, body=existing.body)
        write_sop_file(path, new_frontmatter, raw_body)
    return new_doc


def _set_status_vcr(id_: str, status: str, superseded_by: str | None) -> VcrDocument:
    """Replace the status of the verification case record identified by ``id_``.

    Mirrors :func:`_set_status_dec`'s shape (same ``vcr_lock``,
    ``load_by_id``, ``write_vcr_file``, ``VcrNotFoundError``) -- see
    :func:`_set_status_req` for the full semantics. ``vcr`` is not
    ``adr``, so ``superseded_by`` must never be given.
    """
    assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"

    base_dir = vcr_base_dir()
    with vcr_lock(id_):
        path, existing = load_vcr_by_id(base_dir, id_)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["status"] = status
        fm_data["updated"] = now
        new_frontmatter = VcrFrontmatter(**fm_data)
        new_doc = VcrDocument(frontmatter=new_frontmatter, body=existing.body)
        write_vcr_file(path, new_frontmatter, raw_body)
    return new_doc


def _set_status_adr(id_: str, status: str, superseded_by: str | None) -> Adr:
    """Replace the status of the ADR identified by ``id_``.

    Port of the previous per-domain ADR status tool's function body
    (same ``adr_lock``, ``load_by_id``, delegation to
    ``models.adr.v1.mutations.set_status`` -- which composes ``status`` as
    ``"superseded by {superseded_by}"`` when ``superseded_by`` is given --
    and the ``write_adr`` render round-trip, ``AdrNotFoundError``; that
    per-domain tool was retired in feat-22 Phase 4).
    """
    base_dir = adr_base_dir()
    with adr_lock(id_):
        path, adr = load_adr_by_id(base_dir, id_)
        new_adr = mutations.set_status(adr, status, superseded_by)
        write_adr(path, new_adr)
    return new_adr


#: Dispatch table mapping the ``type`` value to its private adapter.
_ADAPTERS: dict[str, Callable[[str, str, str | None], _SetStatusDocument]] = {
    "req": _set_status_req,
    "uc": _set_status_uc,
    "tsk": _set_status_tsk,
    "qa": _set_status_qa,
    "prb": _set_status_prb,
    "gol": _set_status_gol,
    "rsk": _set_status_rsk,
    "dec": _set_status_dec,
    "feat": _set_status_feat,
    "sop": _set_status_sop,
    "vcr": _set_status_vcr,
    _TYPE_ADR: _set_status_adr,
}


@mcp.tool(
    name="set_status",
    title="Set document status",
    description=(
        "Replace the status of an existing document across all twelve domains (`type` is one of "
        "req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, adr), also bumping `updated` (the eleven "
        "whole-body domains) and leaving the body untouched. The new `status` must be one of the "
        "domain's own closed vocabulary values (see the domain's `XFrontmatter.status` field); "
        "anything else raises `pydantic.ValidationError` and writes nothing. `superseded_by` is "
        'accepted only for `type="adr"` -- it composes the status as "superseded by '
        '{superseded_by}"; with any other `type` it is a `ValueError`. Neither `create_*` nor '
        "the generic `update` tool accepts a `status` argument at all -- this is the sole "
        "status-change entry point."
    ),
)
def set_status(
    id: str,
    type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "feat", "vcr", "adr"],
    status: str,
    superseded_by: str | None = None,
) -> _SetStatusDocument:
    """Replace the status of an existing document, across all twelve domains.

    Cross-domain generic for every document type
    (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/``adr``);
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
    ``XFrontmatter.status`` field (the eleven whole-body domains'
    ``models/<v>/frontmatter.py`` and ``models/adr/v1/frontmatter.py``)
    rather than any list in this docstring.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    type:
        The document type / domain: one of ``req``, ``uc``, ``tsk``,
        ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``, ``feat``,
        ``vcr``, ``adr``.
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
    ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument |
    GolDocument | RskDocument | DecDocument | FeatDocument | SopDocument |
    VcrDocument | Adr
        The updated document of the dispatched domain type.

    Raises
    ------
    ValueError
        ``superseded_by`` given with a ``type`` other than ``"adr"``
        (raised before any file access). Nothing is written.
    pydantic.ValidationError
        ``status`` is not in the dispatched domain's closed vocabulary
        (for ``adr``: not one of its six values and not a
        ``"superseded by ..."`` string). Nothing is written.
    ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError /
    PrbNotFoundError / GolNotFoundError / RskNotFoundError / DecNotFoundError /
    FeatNotFoundError / SopNotFoundError / VcrNotFoundError / AdrNotFoundError
        No document of the dispatched ``type`` has this id -- the
        domain's own not-found error, unchanged from the per-domain tools.
    """
    if superseded_by is not None and type != _TYPE_ADR:
        raise ValueError(
            f'superseded_by is only accepted for type={_TYPE_ADR!r} (the "superseded by X" '
            f"pattern is ADR-specific), got type={type!r} with superseded_by={superseded_by!r}"
        )

    adapter = _ADAPTERS[type]
    result = adapter(id, status, superseded_by)
    return result
