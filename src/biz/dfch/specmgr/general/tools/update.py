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
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Literal

from ...dec.models.v1 import DecDocument, DecFrontmatter, Decision
from ...dec.tools._io import load_by_id as load_dec_by_id
from ...dec.tools._lock import dec_lock
from ...dec.tools._paths import dec_base_dir
from ...dec.tools._write import write_dec_file
from ...feat.models.v1 import FeatDocument, FeatFrontmatter, Feature
from ...feat.tools._io import load_by_id as load_feat_by_id
from ...feat.tools._lock import feat_lock
from ...feat.tools._paths import feat_base_dir
from ...feat.tools._write import write_feat_file
from ...gol.models.v1 import GolDocument, GolFrontmatter, Goal
from ...gol.tools._io import load_by_id as load_gol_by_id
from ...gol.tools._lock import gol_lock
from ...gol.tools._paths import gol_base_dir
from ...gol.tools._write import write_gol_file
from ...models.md._errors import BODY_CHANNEL, wrap_tool_errors
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
from ...sop.models.v1 import Sop, SopDocument, SopFrontmatter
from ...sop.tools._io import load_by_id as load_sop_by_id
from ...sop.tools._lock import sop_lock
from ...sop.tools._paths import sop_base_dir
from ...sop.tools._write import write_sop_file
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
from ...vcr.models.v1 import Vcr, VcrDocument, VcrFrontmatter
from ...vcr.tools._io import load_by_id as load_vcr_by_id
from ...vcr.tools._lock import vcr_lock
from ...vcr.tools._paths import vcr_base_dir
from ...vcr.tools._write import write_vcr_file
from ._splice import body_text, splice_body

__all__ = ["update"]

#: The generic tool's 11-way return union -- annotation-only (see module docstring).
_UpdateDocument = (
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
)


def _update_req(id_: str, content: str, offset: int | None, limit: int | None) -> ReqDocument:
    """Replace the body of the requirement identified by ``id_`` (whole-body or line-range mode).

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
    """
    if offset is not None:
        assert limit is None or offset is not None, "the public `update` guard enforces offset with limit"

        base_dir = req_base_dir()
        with req_lock(id_):
            path, existing = load_req_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), offset, limit, content)
            with wrap_tool_errors(domain="req", tool="update", channel=BODY_CHANNEL):
                body = Requirement.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = ReqFrontmatter(**fm_data)
            new_doc = ReqDocument(frontmatter=new_frontmatter, body=body)
            write_req_file(path, new_frontmatter, spliced)
        return new_doc

    with wrap_tool_errors(domain="req", tool="update", channel=BODY_CHANNEL):
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


def _update_uc(id_: str, content: str, offset: int | None, limit: int | None) -> UcDocument:
    """Replace the body of the use case identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain use-case update tool's function
    body (same ``uc_lock``, ``load_by_id``, frontmatter carry-over with only
    ``updated`` bumped, ``write_uc_file``, ``UcNotFoundError``; that
    per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
    branch (see :func:`_update_req`).
    """
    if offset is not None:
        assert limit is None or offset is not None, "the public `update` guard enforces offset with limit"

        base_dir = uc_base_dir()
        with uc_lock(id_):
            path, existing = load_uc_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), offset, limit, content)
            with wrap_tool_errors(domain="uc", tool="update", channel=BODY_CHANNEL):
                body = UseCase.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = UcFrontmatter(**fm_data)
            new_doc = UcDocument(frontmatter=new_frontmatter, body=body)
            write_uc_file(path, new_frontmatter, spliced)
        return new_doc

    with wrap_tool_errors(domain="uc", tool="update", channel=BODY_CHANNEL):
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


def _update_tsk(id_: str, content: str, offset: int | None, limit: int | None) -> TskDocument:
    """Replace the body of the task list identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain task list update tool's
    function body (same ``tsk_lock``, ``load_by_id``, frontmatter carry-over
    with only ``updated`` bumped, ``write_tsk_file``, ``TskNotFoundError``;
    that per-domain tool was retired in feat-22 Phase 3), plus the REQ-002
    range branch (see :func:`_update_req`).
    """
    if offset is not None:
        assert limit is None or offset is not None, "the public `update` guard enforces offset with limit"

        base_dir = tsk_base_dir()
        with tsk_lock(id_):
            path, existing = load_tsk_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), offset, limit, content)
            with wrap_tool_errors(domain="tsk", tool="update", channel=BODY_CHANNEL):
                body = Task.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = TskFrontmatter(**fm_data)
            new_doc = TskDocument(frontmatter=new_frontmatter, body=body)
            write_tsk_file(path, new_frontmatter, spliced)
        return new_doc

    with wrap_tool_errors(domain="tsk", tool="update", channel=BODY_CHANNEL):
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


def _update_qa(id_: str, content: str, offset: int | None, limit: int | None) -> QaDocument:
    """Replace the body of the QA document identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain QA document update tool's
    function body (same ``qa_lock``, ``load_by_id``, frontmatter carry-over
    with only ``updated`` bumped, ``write_qa_file``, ``QaNotFoundError``;
    that per-domain tool was retired in feat-22 Phase 3), plus the REQ-002
    range branch (see :func:`_update_req`).
    """
    if offset is not None:
        assert limit is None or offset is not None, "the public `update` guard enforces offset with limit"

        base_dir = qa_base_dir()
        with qa_lock(id_):
            path, existing = load_qa_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), offset, limit, content)
            with wrap_tool_errors(domain="qa", tool="update", channel=BODY_CHANNEL):
                body = Qa.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = QaFrontmatter(**fm_data)
            new_doc = QaDocument(frontmatter=new_frontmatter, body=body)
            write_qa_file(path, new_frontmatter, spliced)
        return new_doc

    with wrap_tool_errors(domain="qa", tool="update", channel=BODY_CHANNEL):
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


def _update_prb(id_: str, content: str, offset: int | None, limit: int | None) -> PrbDocument:
    """Replace the body of the problem statement identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain problem statement update
    tool's function body (same ``prb_lock``, ``load_by_id``, frontmatter
    carry-over with only ``updated`` bumped, ``write_prb_file``,
    ``PrbNotFoundError``; that per-domain tool was retired in feat-22
    Phase 3), plus the REQ-002 range branch (see :func:`_update_req`).
    """
    if offset is not None:
        assert limit is None or offset is not None, "the public `update` guard enforces offset with limit"

        base_dir = prb_base_dir()
        with prb_lock(id_):
            path, existing = load_prb_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), offset, limit, content)
            with wrap_tool_errors(domain="prb", tool="update", channel=BODY_CHANNEL):
                body = Prb.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = PrbFrontmatter(**fm_data)
            new_doc = PrbDocument(frontmatter=new_frontmatter, body=body)
            write_prb_file(path, new_frontmatter, spliced)
        return new_doc

    with wrap_tool_errors(domain="prb", tool="update", channel=BODY_CHANNEL):
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


def _update_gol(id_: str, content: str, offset: int | None, limit: int | None) -> GolDocument:
    """Replace the body of the goal identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain goal update tool's function
    body (same ``gol_lock``, ``load_by_id``, frontmatter carry-over with
    only ``updated`` bumped, ``write_gol_file``, ``GolNotFoundError``; that
    per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
    branch (see :func:`_update_req`).
    """
    if offset is not None:
        assert limit is None or offset is not None, "the public `update` guard enforces offset with limit"

        base_dir = gol_base_dir()
        with gol_lock(id_):
            path, existing = load_gol_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), offset, limit, content)
            with wrap_tool_errors(domain="gol", tool="update", channel=BODY_CHANNEL):
                body = Goal.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = GolFrontmatter(**fm_data)
            new_doc = GolDocument(frontmatter=new_frontmatter, body=body)
            write_gol_file(path, new_frontmatter, spliced)
        return new_doc

    with wrap_tool_errors(domain="gol", tool="update", channel=BODY_CHANNEL):
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


def _update_rsk(id_: str, content: str, offset: int | None, limit: int | None) -> RskDocument:
    """Replace the body of the risk identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain risk update tool's function
    body (same ``rsk_lock``, ``load_by_id``, frontmatter carry-over with
    only ``updated`` bumped, ``write_rsk_file``, ``RskNotFoundError``; that
    per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
    branch (see :func:`_update_req`).
    """
    if offset is not None:
        assert limit is None or offset is not None, "the public `update` guard enforces offset with limit"

        base_dir = rsk_base_dir()
        with rsk_lock(id_):
            path, existing = load_rsk_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), offset, limit, content)
            with wrap_tool_errors(domain="rsk", tool="update", channel=BODY_CHANNEL):
                body = Risk.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = RskFrontmatter(**fm_data)
            new_doc = RskDocument(frontmatter=new_frontmatter, body=body)
            write_rsk_file(path, new_frontmatter, spliced)
        return new_doc

    with wrap_tool_errors(domain="rsk", tool="update", channel=BODY_CHANNEL):
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


def _update_dec(id_: str, content: str, offset: int | None, limit: int | None) -> DecDocument:
    """Replace the body of the decision identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain decision update tool's
    function body (same ``dec_lock``, ``load_by_id``, frontmatter carry-over
    with only ``updated`` bumped, ``write_dec_file``, ``DecNotFoundError``;
    that per-domain tool was retired in feat-22 Phase 8, when the DEC
    domain -- merged from dev while still on the old per-domain mechanism
    -- was converted to the generic tools), plus the REQ-002 range branch
    (see :func:`_update_req`).
    """
    if offset is not None:
        assert limit is None or offset is not None, "the public `update` guard enforces offset with limit"

        base_dir = dec_base_dir()
        with dec_lock(id_):
            path, existing = load_dec_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), offset, limit, content)
            with wrap_tool_errors(domain="dec", tool="update", channel=BODY_CHANNEL):
                body = Decision.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = DecFrontmatter(**fm_data)
            new_doc = DecDocument(frontmatter=new_frontmatter, body=body)
            write_dec_file(path, new_frontmatter, spliced)
        return new_doc

    with wrap_tool_errors(domain="dec", tool="update", channel=BODY_CHANNEL):
        body = Decision.from_text(format_text(content))

    base_dir = dec_base_dir()
    with dec_lock(id_):
        path, existing = load_dec_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = DecFrontmatter(**fm_data)
        new_doc = DecDocument(frontmatter=new_frontmatter, body=body)
        write_dec_file(path, new_frontmatter, content)
    return new_doc


def _update_feat(id_: str, content: str, offset: int | None, limit: int | None) -> FeatDocument:
    """Replace the body of the feature identified by ``id_`` (whole-body or line-range mode).

    Mirrors :func:`_update_dec`'s shape (same ``feat_lock``, ``load_by_id``,
    ``write_feat_file``, ``FeatNotFoundError``) with one feat-only
    divergence (see the module docstring): ``id_`` resolves via
    ``feat.tools._paths``'s bespoke folder-per-document shortcut (through
    ``load_by_id``/``feat_base_dir``), not a flat-file directory scan.
    ``updated`` is bumped to the same microsecond timestamp as every other
    domain.
    """
    if offset is not None:
        assert limit is None or offset is not None, "the public `update` guard enforces offset with limit"

        base_dir = feat_base_dir()
        with feat_lock(id_):
            path, existing = load_feat_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), offset, limit, content)
            with wrap_tool_errors(domain="feat", tool="update", channel=BODY_CHANNEL):
                body = Feature.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = FeatFrontmatter(**fm_data)
            new_doc = FeatDocument(frontmatter=new_frontmatter, body=body)
            write_feat_file(path, new_frontmatter, spliced)
        return new_doc

    with wrap_tool_errors(domain="feat", tool="update", channel=BODY_CHANNEL):
        body = Feature.from_text(format_text(content))

    base_dir = feat_base_dir()
    with feat_lock(id_):
        path, existing = load_feat_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = FeatFrontmatter(**fm_data)
        new_doc = FeatDocument(frontmatter=new_frontmatter, body=body)
        write_feat_file(path, new_frontmatter, content)
    return new_doc


def _update_sop(id_: str, content: str, offset: int | None, limit: int | None) -> SopDocument:
    """Replace the body of the SOP identified by ``id_`` (whole-body or line-range mode).

    Verbatim-shape port of :func:`_update_dec` (same ``sop_lock``,
    ``load_by_id``, frontmatter carry-over with only ``updated`` bumped,
    ``write_sop_file``, ``SopNotFoundError``; ``sop`` is the first domain
    built dispatch-only from day one per ADR 36905d5b, so there was never a
    per-domain ``update_sop`` tool to port -- this adapter was written
    directly in this shape), plus the REQ-002 range branch
    (see :func:`_update_req`).
    """
    if offset is not None:
        assert limit is None or offset is not None, "the public `update` guard enforces offset with limit"

        base_dir = sop_base_dir()
        with sop_lock(id_):
            path, existing = load_sop_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), offset, limit, content)
            with wrap_tool_errors(domain="sop", tool="update", channel=BODY_CHANNEL):
                body = Sop.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = SopFrontmatter(**fm_data)
            new_doc = SopDocument(frontmatter=new_frontmatter, body=body)
            write_sop_file(path, new_frontmatter, spliced)
        return new_doc

    with wrap_tool_errors(domain="sop", tool="update", channel=BODY_CHANNEL):
        body = Sop.from_text(format_text(content))

    base_dir = sop_base_dir()
    with sop_lock(id_):
        path, existing = load_sop_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = SopFrontmatter(**fm_data)
        new_doc = SopDocument(frontmatter=new_frontmatter, body=body)
        write_sop_file(path, new_frontmatter, content)
    return new_doc


def _update_vcr(id_: str, content: str, offset: int | None, limit: int | None) -> VcrDocument:
    """Replace the body of the verification case record identified by ``id_`` (whole-body or line-range mode).

    Mirrors :func:`_update_dec`'s shape (same ``vcr_lock``, ``load_by_id``,
    frontmatter carry-over with only ``updated`` bumped, ``write_vcr_file``,
    ``VcrNotFoundError``), plus the REQ-002 range branch (see
    :func:`_update_req`).
    """
    if offset is not None:
        assert limit is None or offset is not None, "the public `update` guard enforces offset with limit"

        base_dir = vcr_base_dir()
        with vcr_lock(id_):
            path, existing = load_vcr_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), offset, limit, content)
            with wrap_tool_errors(domain="vcr", tool="update", channel=BODY_CHANNEL):
                body = Vcr.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = VcrFrontmatter(**fm_data)
            new_doc = VcrDocument(frontmatter=new_frontmatter, body=body)
            write_vcr_file(path, new_frontmatter, spliced)
        return new_doc

    with wrap_tool_errors(domain="vcr", tool="update", channel=BODY_CHANNEL):
        body = Vcr.from_text(format_text(content))

    base_dir = vcr_base_dir()
    with vcr_lock(id_):
        path, existing = load_vcr_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = VcrFrontmatter(**fm_data)
        new_doc = VcrDocument(frontmatter=new_frontmatter, body=body)
        write_vcr_file(path, new_frontmatter, content)
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
    "dec": _update_dec,
    "feat": _update_feat,
    "sop": _update_sop,
    "vcr": _update_vcr,
}


@mcp.tool(
    name="update",
    title="Update document",
    description=(
        "Whole-body or line-range replace of an existing document's content across the eleven "
        "whole-body domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr), "
        "preserving its id/type/status/created/version; only `updated` changes. With no `offset`/`limit`, "
        "`content` is the full replacement body (body markdown only, no frontmatter block). With "
        "`offset`, `content` replaces the body line(s) starting at 1-based line `offset` of the current "
        "on-disk body: `limit` is the number of lines to replace (`offset`..`offset+limit-1`; `limit` "
        "omitted = through the last body line, `limit=0` = pure insert), and `offset=N+1` (one past "
        "the last body line) appends after it; the spliced result is validated as a whole document "
        "before anything is written. `status` is never settable -- use the generic `set_status` tool."
    ),
)
def update(
    id: str,
    type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "feat", "vcr"],
    content: str,
    offset: int | None = None,
    limit: int | None = None,
) -> _UpdateDocument:
    """Replace the body of an existing document, in whole-body or line-range mode.

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
        deletes the H1). The message is prefixed with domain/tool/channel
        context (e.g. ``"tsk update (body): ..."``) by the shared
        tool-boundary wrapper (:func:`~biz.dfch.specmgr.models.md._errors.
        wrap_tool_errors`), layered on top of the engine's own
        field-path/line/snippet enrichment (feat-27-validation Phases
        1/2). Nothing is written.
    pydantic.ValidationError
        A field/cross-field validation failure in the (spliced) body (e.g.
        a range producing an out-of-vocabulary value) -- similarly
        prefixed. Nothing is written.
    ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError /
    PrbNotFoundError / GolNotFoundError / RskNotFoundError / DecNotFoundError /
    FeatNotFoundError / SopNotFoundError / VcrNotFoundError
        No document of the dispatched ``type`` has this id -- the
        domain's own not-found error, unchanged from the per-domain tools.
    """
    if offset is None and limit is not None:
        raise ValueError(f"limit must be given together with offset, got offset={offset!r}, limit={limit!r}")

    adapter = _ADAPTERS[type]
    result = adapter(id, content, offset, limit)
    return result
