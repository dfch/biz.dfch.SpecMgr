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

"""``@mcp.tool()`` wrapper: update (feat-22-consolidate-mutation-tools, Phase 2).

The generic, cross-domain whole-body *and* line-range replace tool for the
seven whole-body document types (``req``/``uc``/``tsk``/``qa``/``prb``/
``gol``/``rsk``). It dispatches on the explicit ``type`` parameter to a
private per-domain adapter (``_update_<d>``), each a **verbatim port** of
the corresponding per-domain ``update_<d>`` tool's function body (same
domain lock, same ``load_by_id``, same frontmatter carry-over with only
``updated`` bumped, same verbatim persistence via the domain's own
``write_<d>_file``, same domain ``XNotFoundError``) plus the REQ-002 range
branch: with ``begin``/``end`` given, the on-disk body is re-read via
:func:`._splice.body_text`, spliced via :func:`._splice.splice_body`, and
the *spliced result* is validated as a whole document and persisted
verbatim instead of the raw fragment.

The parameter is intentionally named ``type`` (it matches the frontmatter
field vocabulary the client already knows); no enabled ruff rule objects to
the builtin shadow. The 7-way union return type is annotation-only -- the
MCP input schema is built from the parameters, and the SDK serializes
whichever concrete document is returned.

ADR is deliberately *not* a ``type`` here: its section-level MADR mutation
contract (``update_frontmatter``/``update_section``/``option_*``) has no
whole-body replace by design.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Literal

from ...gol.models.v1 import GolDocument, GolFrontmatter, Goal
from ...gol.tools._io import load_by_id as load_gol_by_id
from ...gol.tools._lock import gol_lock
from ...gol.tools._paths import gol_base_dir
from ...gol.tools._write import write_gol_file
from ...models.md._markdown import format_text
from ...prb.models.v1 import Prb, PrbDocument, PrbFrontmatter
from ...prb.tools._io import load_by_id as load_prb_by_id
from ...prb.tools._lock import prb_lock
from ...prb.tools._paths import prb_base_dir
from ...prb.tools._write import write_prb_file
from ...qa.models.v2 import Qa, QaDocument, QaFrontmatter
from ...qa.tools._io import load_by_id as load_qa_by_id
from ...qa.tools._lock import qa_lock
from ...qa.tools._paths import qa_base_dir
from ...qa.tools._write import write_qa_file
from ...req.models.v1 import ReqDocument, ReqFrontmatter, Requirement
from ...req.tools._io import load_by_id as load_req_by_id
from ...req.tools._lock import req_lock
from ...req.tools._paths import req_base_dir
from ...req.tools._write import write_req_file
from ...rsk.models.v1 import Risk, RskDocument, RskFrontmatter
from ...rsk.tools._io import load_by_id as load_rsk_by_id
from ...rsk.tools._lock import rsk_lock
from ...rsk.tools._paths import rsk_base_dir
from ...rsk.tools._write import write_rsk_file
from ...server import mcp
from ...tsk.models.v1 import Task, TskDocument, TskFrontmatter
from ...tsk.tools._io import load_by_id as load_tsk_by_id
from ...tsk.tools._lock import tsk_lock
from ...tsk.tools._paths import tsk_base_dir
from ...tsk.tools._write import write_tsk_file
from ...uc.models.v2 import UcDocument, UcFrontmatter, UseCase
from ...uc.tools._io import load_by_id as load_uc_by_id
from ...uc.tools._lock import uc_lock
from ...uc.tools._paths import uc_base_dir
from ...uc.tools._write import write_uc_file
from ._splice import body_text, splice_body

__all__ = ["update"]

#: The generic tool's 7-way return union -- annotation-only (see module docstring).
_UpdateDocument = ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument


def _update_req(id_: str, content: str, begin: int | None, end: int | None) -> ReqDocument:
    """Replace the body of the requirement identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain requirement update tool's
    function body (same ``req_lock``, ``load_by_id``, frontmatter carry-over
    with only ``updated`` bumped, ``write_req_file``, ``ReqNotFoundError``;
    that per-domain tool was retired in feat-22 Phase 3), plus the REQ-002
    range branch: with ``begin``/``end`` given (both-or-neither is
    enforced by the public :func:`update` before dispatch), the on-disk
    body is re-read via :func:`body_text`, spliced via
    :func:`splice_body`, and the *spliced result* is validated and
    persisted verbatim instead of the raw fragment.
    """
    if begin is not None or end is not None:
        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"

        base_dir = req_base_dir()
        with req_lock(id_):
            path, existing = load_req_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), begin, end, content)
            body = Requirement.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = ReqFrontmatter(**fm_data)
            new_doc = ReqDocument(frontmatter=new_frontmatter, body=body)
            write_req_file(path, new_frontmatter, spliced)
        return new_doc

    body = Requirement.from_text(format_text(content))

    base_dir = req_base_dir()
    with req_lock(id_):
        path, existing = load_req_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = ReqFrontmatter(**fm_data)
        new_doc = ReqDocument(frontmatter=new_frontmatter, body=body)
        write_req_file(path, new_frontmatter, content)
    return new_doc


def _update_uc(id_: str, content: str, begin: int | None, end: int | None) -> UcDocument:
    """Replace the body of the use case identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain use-case update tool's function
    body (same ``uc_lock``, ``load_by_id``, frontmatter carry-over with only
    ``updated`` bumped, ``write_uc_file``, ``UcNotFoundError``; that
    per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
    branch (see :func:`_update_req`).
    """
    if begin is not None or end is not None:
        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"

        base_dir = uc_base_dir()
        with uc_lock(id_):
            path, existing = load_uc_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), begin, end, content)
            body = UseCase.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = UcFrontmatter(**fm_data)
            new_doc = UcDocument(frontmatter=new_frontmatter, body=body)
            write_uc_file(path, new_frontmatter, spliced)
        return new_doc

    body = UseCase.from_text(format_text(content))

    base_dir = uc_base_dir()
    with uc_lock(id_):
        path, existing = load_uc_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = UcFrontmatter(**fm_data)
        new_doc = UcDocument(frontmatter=new_frontmatter, body=body)
        write_uc_file(path, new_frontmatter, content)
    return new_doc


def _update_tsk(id_: str, content: str, begin: int | None, end: int | None) -> TskDocument:
    """Replace the body of the task list identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain task list update tool's
    function body (same ``tsk_lock``, ``load_by_id``, frontmatter carry-over
    with only ``updated`` bumped, ``write_tsk_file``, ``TskNotFoundError``;
    that per-domain tool was retired in feat-22 Phase 3), plus the REQ-002
    range branch (see :func:`_update_req`).
    """
    if begin is not None or end is not None:
        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"

        base_dir = tsk_base_dir()
        with tsk_lock(id_):
            path, existing = load_tsk_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), begin, end, content)
            body = Task.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = TskFrontmatter(**fm_data)
            new_doc = TskDocument(frontmatter=new_frontmatter, body=body)
            write_tsk_file(path, new_frontmatter, spliced)
        return new_doc

    body = Task.from_text(format_text(content))

    base_dir = tsk_base_dir()
    with tsk_lock(id_):
        path, existing = load_tsk_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = TskFrontmatter(**fm_data)
        new_doc = TskDocument(frontmatter=new_frontmatter, body=body)
        write_tsk_file(path, new_frontmatter, content)
    return new_doc


def _update_qa(id_: str, content: str, begin: int | None, end: int | None) -> QaDocument:
    """Replace the body of the QA document identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain QA document update tool's
    function body (same ``qa_lock``, ``load_by_id``, frontmatter carry-over
    with only ``updated`` bumped, ``write_qa_file``, ``QaNotFoundError``;
    that per-domain tool was retired in feat-22 Phase 3), plus the REQ-002
    range branch (see :func:`_update_req`).
    """
    if begin is not None or end is not None:
        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"

        base_dir = qa_base_dir()
        with qa_lock(id_):
            path, existing = load_qa_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), begin, end, content)
            body = Qa.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = QaFrontmatter(**fm_data)
            new_doc = QaDocument(frontmatter=new_frontmatter, body=body)
            write_qa_file(path, new_frontmatter, spliced)
        return new_doc

    body = Qa.from_text(format_text(content))

    base_dir = qa_base_dir()
    with qa_lock(id_):
        path, existing = load_qa_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = QaFrontmatter(**fm_data)
        new_doc = QaDocument(frontmatter=new_frontmatter, body=body)
        write_qa_file(path, new_frontmatter, content)
    return new_doc


def _update_prb(id_: str, content: str, begin: int | None, end: int | None) -> PrbDocument:
    """Replace the body of the problem statement identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain problem statement update
    tool's function body (same ``prb_lock``, ``load_by_id``, frontmatter
    carry-over with only ``updated`` bumped, ``write_prb_file``,
    ``PrbNotFoundError``; that per-domain tool was retired in feat-22
    Phase 3), plus the REQ-002 range branch (see :func:`_update_req`).
    """
    if begin is not None or end is not None:
        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"

        base_dir = prb_base_dir()
        with prb_lock(id_):
            path, existing = load_prb_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), begin, end, content)
            body = Prb.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = PrbFrontmatter(**fm_data)
            new_doc = PrbDocument(frontmatter=new_frontmatter, body=body)
            write_prb_file(path, new_frontmatter, spliced)
        return new_doc

    body = Prb.from_text(format_text(content))

    base_dir = prb_base_dir()
    with prb_lock(id_):
        path, existing = load_prb_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = PrbFrontmatter(**fm_data)
        new_doc = PrbDocument(frontmatter=new_frontmatter, body=body)
        write_prb_file(path, new_frontmatter, content)
    return new_doc


def _update_gol(id_: str, content: str, begin: int | None, end: int | None) -> GolDocument:
    """Replace the body of the goal identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain goal update tool's function
    body (same ``gol_lock``, ``load_by_id``, frontmatter carry-over with
    only ``updated`` bumped, ``write_gol_file``, ``GolNotFoundError``; that
    per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
    branch (see :func:`_update_req`).
    """
    if begin is not None or end is not None:
        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"

        base_dir = gol_base_dir()
        with gol_lock(id_):
            path, existing = load_gol_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), begin, end, content)
            body = Goal.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = GolFrontmatter(**fm_data)
            new_doc = GolDocument(frontmatter=new_frontmatter, body=body)
            write_gol_file(path, new_frontmatter, spliced)
        return new_doc

    body = Goal.from_text(format_text(content))

    base_dir = gol_base_dir()
    with gol_lock(id_):
        path, existing = load_gol_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = GolFrontmatter(**fm_data)
        new_doc = GolDocument(frontmatter=new_frontmatter, body=body)
        write_gol_file(path, new_frontmatter, content)
    return new_doc


def _update_rsk(id_: str, content: str, begin: int | None, end: int | None) -> RskDocument:
    """Replace the body of the risk identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain risk update tool's function
    body (same ``rsk_lock``, ``load_by_id``, frontmatter carry-over with
    only ``updated`` bumped, ``write_rsk_file``, ``RskNotFoundError``; that
    per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
    branch (see :func:`_update_req`).
    """
    if begin is not None or end is not None:
        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"

        base_dir = rsk_base_dir()
        with rsk_lock(id_):
            path, existing = load_rsk_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), begin, end, content)
            body = Risk.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = RskFrontmatter(**fm_data)
            new_doc = RskDocument(frontmatter=new_frontmatter, body=body)
            write_rsk_file(path, new_frontmatter, spliced)
        return new_doc

    body = Risk.from_text(format_text(content))

    base_dir = rsk_base_dir()
    with rsk_lock(id_):
        path, existing = load_rsk_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = RskFrontmatter(**fm_data)
        new_doc = RskDocument(frontmatter=new_frontmatter, body=body)
        write_rsk_file(path, new_frontmatter, content)
    return new_doc


#: Dispatch table mapping the ``type`` value to its private adapter.
_ADAPTERS: dict[str, Callable[[str, str, int | None, int | None], _UpdateDocument]] = {
    "req": _update_req,
    "uc": _update_uc,
    "tsk": _update_tsk,
    "qa": _update_qa,
    "prb": _update_prb,
    "gol": _update_gol,
    "rsk": _update_rsk,
}


@mcp.tool(
    name="update",
    title="Update document",
    description=(
        "Whole-body or line-range replace of an existing document's content across the seven "
        "whole-body domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk), preserving its "
        "id/type/status/created/version; only `updated` changes. With no `begin`/`end`, `content` "
        "is the full replacement body (body markdown only, no frontmatter block). With both, "
        "`content` replaces the 1-based inclusive body-line range `begin`..`end` of the current "
        "on-disk body (`N+1` = end-of-body sentinel: append after the last line, or replace "
        "through end of body); the spliced result is validated as a whole document before "
        "anything is written. `status` is never settable -- use the `set_status_*` tools."
    ),
)
def update(
    id: str,
    type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk"],
    content: str,
    begin: int | None = None,
    end: int | None = None,
) -> _UpdateDocument:
    """Replace the body of an existing document, in whole-body or line-range mode.

    Cross-domain generic for the seven whole-body document types
    (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``); dispatches on
    ``type`` to the domain's own ported adapter (same lock, same id
    resolution, same frontmatter carry-over, same verbatim persistence,
    same domain not-found error).

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
    through this tool -- the per-domain ``set_status_<d>`` tools are the
    only status-change path.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    type:
        The document type / domain: one of ``req``, ``uc``, ``tsk``,
        ``qa``, ``prb``, ``gol``, ``rsk``.
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
    ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument
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
    PrbNotFoundError / GolNotFoundError / RskNotFoundError
        No document of the dispatched ``type`` has this id -- the
        domain's own not-found error, unchanged from the per-domain tools.
    """
    if (begin is None) != (end is None):
        raise ValueError(f"begin and end must be given together (both or neither), got begin={begin!r}, end={end!r}")

    adapter = _ADAPTERS[type]
    result = adapter(id, content, begin, end)
    return result
