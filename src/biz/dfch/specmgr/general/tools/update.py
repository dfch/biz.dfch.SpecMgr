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

"""``@mcp.tool()`` wrapper: update (feat-22-consolidate-mutation-tools, Phase 2).

The generic, cross-domain whole-body *and* line-range replace tool for the
whole-body document types (``req``/``uc``/``tsk``/``qa``/``prb``/
``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/``sysrs``). It dispatches on the
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
the builtin shadow. The union return type is annotation-only -- the
MCP input schema is built from the parameters, and the SDK serializes
whichever concrete document is returned.

Return shape (feat-153-off-by-n Phase 2, REQ-002/REQ-003, ADR
19ff316b-cd11-41a7-a616-ffd84917da51, revising feature feat-69-
update-context's "frontmatter-only" precedent for ``update`` alone): every
successful call returns the shared
:class:`~biz.dfch.specmgr.general.models.UpdateResult` wrapper -- its
``frontmatter`` is the same per-domain frontmatter object feat-69 returned
(carry-over with only ``updated`` bumped), and its ``snippet`` is, in range
mode, the before/after window of the touched range (the dropped lines
numbered pre-splice, the inserted lines numbered post-splice, up to 2
unchanged context lines per side, each line ``<marker> <n>: <line text>``)
computed once in the shared public dispatcher via
:func:`._splice.splice_snippet`; ``snippet`` is ``None`` in whole-body mode
(no ``offset``) and for the whole-body-equivalent range (``offset=1`` +
omitted ``limit``). The adapters themselves return an internal
:class:`_UpdateOutcome` (the new frontmatter plus, in range mode, the
pre-splice body, the post-splice body, and the ``offset``/``limit``
coordinates they used) so the dispatcher -- not any of the 12 adapters --
assembles the ``UpdateResult``.

``feat`` is the one domain whose adapter (``_update_feat``) diverges from
every other domain's identical shape in how it resolves ``id``: via
``feat.tools._paths``'s bespoke folder-per-document shortcut, not a
flat-file directory scan (see
``.specmgr/feat/feat-31-feature/README.md`` Design Notes, "Addressing").
It bumps ``updated`` to the same shared date+time timestamp (via
``general.tools._timestamps.now_timestamp()``) as every other domain --
an earlier, deliberate divergence (a plain ``YYYY-MM-DD`` date) was
reversed for cross-domain consistency; see that feature's Decisions
Made.

ADR is deliberately *not* a ``type`` here: its section-level MADR mutation
contract (``update_frontmatter``/``update_section``/``option_*``) has no
whole-body replace by design.

**Non-raising failure channels (feat-170-update-edit-parse-failure, GitHub
issue #170, ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f -- case 4 of the ADR
519d1206-4d2a-4500-9046-6db635209996 non-raising, structured-result
workaround chain).** Two failures now return a structured result instead of
raising, with nothing written in either case. (1) On a target ``id`` whose
only matching on-disk file fails to parse, every adapter returns the
non-raising :class:`~biz.dfch.specmgr.general.models.ParseFailureResult`
(``error``/``path``/``id``) instead of raising the domain's own
``XNotFoundError``: the adapter catches the ``load_by_id`` failure (inside
the domain lock, before any write), probes the domain's existing
parse-failure lookup (:func:`._doc_paths.find_parse_failure` for the 11
flat-file domains, called with the domain's own cache-backed ``read_<d>``
as ``read_fn``;
:func:`feat.tools._paths.find_feat_parse_failure` for ``feat``), and
returns the result when the probe finds a name-matching broken file (the
probed path passes the same ``_path_safety.assert_within`` guard the
primary load path applies, mirroring every ``get_<d>``'s own branch). The
``error`` text is byte-identical to the domain's ``list_<d>`` failed row's
``error`` for the same file (identical field path and cause, including the
trailing pydantic documentation line -- feat-162-doc-cache-exception-footer,
GitHub issue #162, fixed ``DocCache``'s exception reconstruction to preserve
that footer on a warm re-raise). A truly-absent ``id`` (no file on
disk matches at all) still raises the domain's own not-found error
unchanged. (2) A content-validation failure on the submitted new content
(whole-body mode: the pre-lock validation; range mode: the in-lock
post-splice validation) returns the non-raising
:class:`~biz.dfch.specmgr.general.models.ValidateResult`
(``valid=False``, ``errors=[...]``) instead of raising
``AssertionError``/``pydantic.ValidationError`` -- the single
``errors[].message`` is the enriched exception text capped exactly as the
generic ``validate`` tool caps it (300 chars via
:func:`models.md._markdown.snippet`, feat-110), mirroring ``validate``
exactly (the shared ``_CAUGHT_EXCEPTIONS`` tuple defined in
:mod:`~biz.dfch.specmgr.general.models.validate_result` and re-exported by
``general.tools.validate``). The mode-dependent precedence when both failures hold at once is
intentional (whole-body mode validates before loading, so
``ValidateResult`` wins; range mode loads first, so
``ParseFailureResult`` wins -- REQ-010). Every caller-usage ``ValueError``
(invalid ``id`` shape, ``limit`` given without ``offset``, misused range
coordinates) still raises exactly as before, and a plain ``KeyError``
still marks ``type="adr"`` (inherited from the dispatch-table lookup).

Safety (REQ-009, feat-38-39-41-43-44 Phase 4): the public :func:`update`
validates ``id`` via ``_path_safety.validate_id`` before dispatch (a
``ValueError`` before any filesystem access -- mirroring the generic
``delete`` tool's own REQ-003), and every adapter confines the resolved
path to the domain's own base directory with ``_path_safety.assert_within``
after ``load_by_id``, inside the domain lock.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ...dec.models.v1 import DecFrontmatter, Decision
from ...dec.tools._io import load_by_id as load_dec_by_id
from ...dec.tools._io import read_dec
from ...dec.tools._lock import dec_lock
from ...dec.tools._paths import DecNotFoundError, dec_base_dir
from ...dec.tools._write import write_dec_file
from ...feat.models.v1 import FeatFrontmatter, Feature
from ...feat.tools._cache import read_feat, read_feat_dirty
from ...feat.tools._io import load_by_id as load_feat_by_id
from ...feat.tools._lock import feat_lock
from ...feat.tools._paths import FeatNotFoundError, feat_base_dir, find_feat_parse_failure
from ...feat.tools._write import write_feat_file
from ...gol.models.v1 import GolFrontmatter, Goal
from ...gol.tools._io import load_by_id as load_gol_by_id
from ...gol.tools._io import read_gol
from ...gol.tools._lock import gol_lock
from ...gol.tools._paths import GolNotFoundError, gol_base_dir
from ...gol.tools._write import write_gol_file
from ...models.md._errors import BODY_CHANNEL, wrap_tool_errors
from ...models.md._markdown import format_text, snippet

# PEP 562 lazy export: pylint cannot see the __getattr__-provided names (see update_result.py's module docstring).
from ..models import (  # pylint: disable=no-name-in-module
    ParseFailureResult,
    UpdateFrontmatter,
    UpdateResult,
    ValidateResult,
    ValidationErrorEntry,
)
from ...prb.models.v1 import Prb, PrbFrontmatter
from ...prb.tools._io import load_by_id as load_prb_by_id
from ...prb.tools._io import read_prb
from ...prb.tools._lock import prb_lock
from ...prb.tools._paths import PrbNotFoundError, prb_base_dir
from ...prb.tools._write import write_prb_file
from ...qa.models.v2 import Qa, QaFrontmatter
from ...qa.tools._io import load_by_id as load_qa_by_id
from ...qa.tools._io import read_qa
from ...qa.tools._lock import qa_lock
from ...qa.tools._paths import QaNotFoundError, qa_base_dir
from ...qa.tools._write import write_qa_file
from ...req.models.v1 import ReqFrontmatter, Requirement
from ...req.tools._io import load_by_id as load_req_by_id
from ...req.tools._io import read_req
from ...req.tools._lock import req_lock
from ...req.tools._paths import ReqNotFoundError, req_base_dir
from ...req.tools._write import write_req_file
from ...rsk.models.v1 import Risk, RskFrontmatter
from ...rsk.tools._io import load_by_id as load_rsk_by_id
from ...rsk.tools._io import read_rsk
from ...rsk.tools._lock import rsk_lock
from ...rsk.tools._paths import RskNotFoundError, rsk_base_dir
from ...rsk.tools._write import write_rsk_file
from ...server import mcp
from ...sop.models.v1 import Sop, SopFrontmatter
from ...sop.tools._io import load_by_id as load_sop_by_id
from ...sop.tools._io import read_sop
from ...sop.tools._lock import sop_lock
from ...sop.tools._paths import SopNotFoundError, sop_base_dir
from ...sop.tools._write import write_sop_file
from ...sysrs.models.v1 import Sysrs, SysrsFrontmatter
from ...sysrs.tools._io import load_by_id as load_sysrs_by_id
from ...sysrs.tools._io import read_sysrs
from ...sysrs.tools._lock import sysrs_lock
from ...sysrs.tools._paths import SysrsNotFoundError, sysrs_base_dir
from ...sysrs.tools._write import write_sysrs_file
from ...tsk.models.v1 import Task, TskFrontmatter
from ...tsk.tools._io import load_by_id as load_tsk_by_id
from ...tsk.tools._io import read_tsk
from ...tsk.tools._lock import tsk_lock
from ...tsk.tools._paths import TskNotFoundError, tsk_base_dir
from ...tsk.tools._write import write_tsk_file
from ...uc.models.v2 import UcFrontmatter, UseCase
from ...uc.tools._io import load_by_id as load_uc_by_id
from ...uc.tools._io import read_uc
from ...uc.tools._lock import uc_lock
from ...uc.tools._paths import UcNotFoundError, uc_base_dir
from ...uc.tools._write import write_uc_file
from ...vcr.models.v1 import Vcr, VcrFrontmatter
from ...vcr.tools._io import load_by_id as load_vcr_by_id
from ...vcr.tools._io import read_vcr
from ...vcr.tools._lock import vcr_lock
from ...vcr.tools._paths import VcrNotFoundError, vcr_base_dir
from ...vcr.tools._write import write_vcr_file
from ._doc_paths import find_parse_failure
from ._domains import WHOLE_BODY_DOMAINS, WholeBodyType
from ._path_safety import assert_within, validate_id
from ._splice import body_text, splice_body, splice_snippet
from ._timestamps import now_timestamp
from .validate import _CAUGHT_EXCEPTIONS, _MAX_VALIDATE_ERROR_CHARS

__all__ = ["update"]

#: The 1-based first body line -- combined with an omitted ``limit``, the
#: offset of the whole-body-equivalent range (``splice_body`` documents the
#: equivalence; the existing ``test_offset_one_equals_whole_body_mode`` test
#: pins it): that range returns ``snippet=None`` exactly like whole-body mode
#: (feat-153-off-by-n Phase 2, REQ-003).
_WHOLE_BODY_OFFSET = 1


@dataclass(frozen=True)
class _UpdateOutcome:
    """The generic ``update`` tool's internal per-domain adapter return (feat-153-off-by-n Phase 2, REQ-002/REQ-003).

    Carries everything the shared public dispatcher needs to assemble the
    public :class:`~biz.dfch.specmgr.general.models.UpdateResult`: the
    updated frontmatter, and -- in range mode only -- the pre-splice body,
    the post-splice body, and the ``offset``/``limit`` coordinates the
    adapter used (the same values it handed to
    :func:`~biz.dfch.specmgr.general.tools._splice.splice_body`). In
    whole-body mode the four range fields are all ``None`` and the dispatcher
    sets ``snippet=None``; so does it for the whole-body-equivalent range
    (``offset=1`` + omitted ``limit``), which the dispatcher detects from the
    coordinates. Never returned from the public tool itself -- the
    dispatcher converts every outcome to ``UpdateResult``.

    Parameters
    ----------
    frontmatter:
        The updated document's frontmatter only (no body) of the dispatched
        domain type (feat-69-update-context's own return object, unchanged).
    pre_body:
        Range mode only: the frontmatter-stripped body text as it existed
        before the splice (``body_text`` of the on-disk file under the
        domain lock).
    post_body:
        Range mode only: the spliced body text -- the result of splicing
        ``pre_body`` at the coordinates below via ``splice_body`` (the text
        validated as a whole document and persisted).
    offset:
        Range mode only: the 1-based first body line of the spliced range.
    limit:
        Range mode only: the number of body lines the spliced range spans
        (``0`` = pure insert; ``None`` = omitted, through the last body
        line).
    """

    frontmatter: UpdateFrontmatter
    pre_body: str | None = None
    post_body: str | None = None
    offset: int | None = None
    limit: int | None = None


def _update_req(
    id_: str, content: str, offset: int | None, limit: int | None
) -> _UpdateOutcome | ParseFailureResult | ValidateResult:
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
    verbatim instead of the raw fragment. Failure returns (see the module
    docstring): a target ``id`` whose only matching on-disk file fails to
    parse yields the non-raising ``ParseFailureResult`` instead of
    ``ReqNotFoundError`` (a truly-absent id still raises), and a
    content-validation failure on the submitted/spliced content yields the
    non-raising ``ValidateResult(valid=False, ...)`` instead of
    ``AssertionError``/``pydantic.ValidationError``. As of feat-153-off-by-n
    Phase 2 (REQ-002/REQ-003) the adapter returns the dispatcher's internal
    :class:`_UpdateOutcome` -- the new frontmatter plus, in range mode, the
    pre-splice body, the post-splice body, and the ``offset``/``limit``
    coordinates it used -- so the shared public dispatcher assembles the
    public :class:`~biz.dfch.specmgr.general.models.UpdateResult` (computing
    the ``snippet`` once via :func:`_splice.splice_snippet`) instead of
    returning the bare frontmatter; the write behavior itself is unchanged.
    """
    if offset is not None:
        assert limit is None or offset is not None, "the public `update` guard enforces offset with limit"

        base_dir = req_base_dir()
        with req_lock(id_):
            try:
                path, existing = load_req_by_id(base_dir, id_)
            except ReqNotFoundError:
                parse_failure = find_parse_failure(base_dir, id_, read_req)
                if parse_failure is None:
                    raise
                failure_path, failure_error = parse_failure
                assert_within(base_dir, failure_path)
                return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
            assert_within(base_dir, path)
            pre = body_text(path)
            spliced = splice_body(pre, offset, limit, content)
            try:
                with wrap_tool_errors(domain="req", tool="update", channel=BODY_CHANNEL):
                    Requirement.from_text(format_text(spliced))
            except _CAUGHT_EXCEPTIONS as ex:
                message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
                return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])
            now = now_timestamp()
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = ReqFrontmatter(**fm_data)
            write_req_file(path, new_frontmatter, spliced)
            read_req(path)  # warm the cache (feat-107-doc-cache Phase 3, REQ-003)
        return _UpdateOutcome(frontmatter=new_frontmatter, pre_body=pre, post_body=spliced, offset=offset, limit=limit)

    try:
        with wrap_tool_errors(domain="req", tool="update", channel=BODY_CHANNEL):
            Requirement.from_text(format_text(content))
    except _CAUGHT_EXCEPTIONS as ex:
        message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
        return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])

    base_dir = req_base_dir()
    with req_lock(id_):
        try:
            path, existing = load_req_by_id(base_dir, id_)
        except ReqNotFoundError:
            parse_failure = find_parse_failure(base_dir, id_, read_req)
            if parse_failure is None:
                raise
            failure_path, failure_error = parse_failure
            assert_within(base_dir, failure_path)
            return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
        assert_within(base_dir, path)
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = ReqFrontmatter(**fm_data)
        write_req_file(path, new_frontmatter, content)
        read_req(path)  # warm the cache (feat-107-doc-cache Phase 3, REQ-003)
    return _UpdateOutcome(frontmatter=new_frontmatter)


def _update_uc(
    id_: str, content: str, offset: int | None, limit: int | None
) -> _UpdateOutcome | ParseFailureResult | ValidateResult:
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
            try:
                path, existing = load_uc_by_id(base_dir, id_)
            except UcNotFoundError:
                parse_failure = find_parse_failure(base_dir, id_, read_uc)
                if parse_failure is None:
                    raise
                failure_path, failure_error = parse_failure
                assert_within(base_dir, failure_path)
                return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
            assert_within(base_dir, path)
            pre = body_text(path)
            spliced = splice_body(pre, offset, limit, content)
            try:
                with wrap_tool_errors(domain="uc", tool="update", channel=BODY_CHANNEL):
                    UseCase.from_text(format_text(spliced))
            except _CAUGHT_EXCEPTIONS as ex:
                message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
                return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])
            now = now_timestamp()
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = UcFrontmatter(**fm_data)
            write_uc_file(path, new_frontmatter, spliced)
            read_uc(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
        return _UpdateOutcome(frontmatter=new_frontmatter, pre_body=pre, post_body=spliced, offset=offset, limit=limit)

    try:
        with wrap_tool_errors(domain="uc", tool="update", channel=BODY_CHANNEL):
            UseCase.from_text(format_text(content))
    except _CAUGHT_EXCEPTIONS as ex:
        message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
        return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])

    base_dir = uc_base_dir()
    with uc_lock(id_):
        try:
            path, existing = load_uc_by_id(base_dir, id_)
        except UcNotFoundError:
            parse_failure = find_parse_failure(base_dir, id_, read_uc)
            if parse_failure is None:
                raise
            failure_path, failure_error = parse_failure
            assert_within(base_dir, failure_path)
            return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
        assert_within(base_dir, path)
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = UcFrontmatter(**fm_data)
        write_uc_file(path, new_frontmatter, content)
        read_uc(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
    return _UpdateOutcome(frontmatter=new_frontmatter)


def _update_tsk(
    id_: str, content: str, offset: int | None, limit: int | None
) -> _UpdateOutcome | ParseFailureResult | ValidateResult:
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
            try:
                path, existing = load_tsk_by_id(base_dir, id_)
            except TskNotFoundError:
                parse_failure = find_parse_failure(base_dir, id_, read_tsk)
                if parse_failure is None:
                    raise
                failure_path, failure_error = parse_failure
                assert_within(base_dir, failure_path)
                return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
            assert_within(base_dir, path)
            pre = body_text(path)
            spliced = splice_body(pre, offset, limit, content)
            try:
                with wrap_tool_errors(domain="tsk", tool="update", channel=BODY_CHANNEL):
                    Task.from_text(format_text(spliced))
            except _CAUGHT_EXCEPTIONS as ex:
                message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
                return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])
            now = now_timestamp()
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = TskFrontmatter(**fm_data)
            write_tsk_file(path, new_frontmatter, spliced)
            read_tsk(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
        return _UpdateOutcome(frontmatter=new_frontmatter, pre_body=pre, post_body=spliced, offset=offset, limit=limit)

    try:
        with wrap_tool_errors(domain="tsk", tool="update", channel=BODY_CHANNEL):
            Task.from_text(format_text(content))
    except _CAUGHT_EXCEPTIONS as ex:
        message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
        return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])

    base_dir = tsk_base_dir()
    with tsk_lock(id_):
        try:
            path, existing = load_tsk_by_id(base_dir, id_)
        except TskNotFoundError:
            parse_failure = find_parse_failure(base_dir, id_, read_tsk)
            if parse_failure is None:
                raise
            failure_path, failure_error = parse_failure
            assert_within(base_dir, failure_path)
            return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
        assert_within(base_dir, path)
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = TskFrontmatter(**fm_data)
        write_tsk_file(path, new_frontmatter, content)
        read_tsk(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
    return _UpdateOutcome(frontmatter=new_frontmatter)


def _update_qa(
    id_: str, content: str, offset: int | None, limit: int | None
) -> _UpdateOutcome | ParseFailureResult | ValidateResult:
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
            try:
                path, existing = load_qa_by_id(base_dir, id_)
            except QaNotFoundError:
                parse_failure = find_parse_failure(base_dir, id_, read_qa)
                if parse_failure is None:
                    raise
                failure_path, failure_error = parse_failure
                assert_within(base_dir, failure_path)
                return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
            assert_within(base_dir, path)
            pre = body_text(path)
            spliced = splice_body(pre, offset, limit, content)
            try:
                with wrap_tool_errors(domain="qa", tool="update", channel=BODY_CHANNEL):
                    Qa.from_text(format_text(spliced))
            except _CAUGHT_EXCEPTIONS as ex:
                message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
                return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])
            now = now_timestamp()
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = QaFrontmatter(**fm_data)
            write_qa_file(path, new_frontmatter, spliced)
            read_qa(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
        return _UpdateOutcome(frontmatter=new_frontmatter, pre_body=pre, post_body=spliced, offset=offset, limit=limit)

    try:
        with wrap_tool_errors(domain="qa", tool="update", channel=BODY_CHANNEL):
            Qa.from_text(format_text(content))
    except _CAUGHT_EXCEPTIONS as ex:
        message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
        return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])

    base_dir = qa_base_dir()
    with qa_lock(id_):
        try:
            path, existing = load_qa_by_id(base_dir, id_)
        except QaNotFoundError:
            parse_failure = find_parse_failure(base_dir, id_, read_qa)
            if parse_failure is None:
                raise
            failure_path, failure_error = parse_failure
            assert_within(base_dir, failure_path)
            return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
        assert_within(base_dir, path)
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = QaFrontmatter(**fm_data)
        write_qa_file(path, new_frontmatter, content)
        read_qa(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
    return _UpdateOutcome(frontmatter=new_frontmatter)


def _update_prb(
    id_: str, content: str, offset: int | None, limit: int | None
) -> _UpdateOutcome | ParseFailureResult | ValidateResult:
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
            try:
                path, existing = load_prb_by_id(base_dir, id_)
            except PrbNotFoundError:
                parse_failure = find_parse_failure(base_dir, id_, read_prb)
                if parse_failure is None:
                    raise
                failure_path, failure_error = parse_failure
                assert_within(base_dir, failure_path)
                return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
            assert_within(base_dir, path)
            pre = body_text(path)
            spliced = splice_body(pre, offset, limit, content)
            try:
                with wrap_tool_errors(domain="prb", tool="update", channel=BODY_CHANNEL):
                    Prb.from_text(format_text(spliced))
            except _CAUGHT_EXCEPTIONS as ex:
                message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
                return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])
            now = now_timestamp()
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = PrbFrontmatter(**fm_data)
            write_prb_file(path, new_frontmatter, spliced)
            read_prb(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
        return _UpdateOutcome(frontmatter=new_frontmatter, pre_body=pre, post_body=spliced, offset=offset, limit=limit)

    try:
        with wrap_tool_errors(domain="prb", tool="update", channel=BODY_CHANNEL):
            Prb.from_text(format_text(content))
    except _CAUGHT_EXCEPTIONS as ex:
        message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
        return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])

    base_dir = prb_base_dir()
    with prb_lock(id_):
        try:
            path, existing = load_prb_by_id(base_dir, id_)
        except PrbNotFoundError:
            parse_failure = find_parse_failure(base_dir, id_, read_prb)
            if parse_failure is None:
                raise
            failure_path, failure_error = parse_failure
            assert_within(base_dir, failure_path)
            return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
        assert_within(base_dir, path)
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = PrbFrontmatter(**fm_data)
        write_prb_file(path, new_frontmatter, content)
        read_prb(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
    return _UpdateOutcome(frontmatter=new_frontmatter)


def _update_gol(
    id_: str, content: str, offset: int | None, limit: int | None
) -> _UpdateOutcome | ParseFailureResult | ValidateResult:
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
            try:
                path, existing = load_gol_by_id(base_dir, id_)
            except GolNotFoundError:
                parse_failure = find_parse_failure(base_dir, id_, read_gol)
                if parse_failure is None:
                    raise
                failure_path, failure_error = parse_failure
                assert_within(base_dir, failure_path)
                return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
            assert_within(base_dir, path)
            pre = body_text(path)
            spliced = splice_body(pre, offset, limit, content)
            try:
                with wrap_tool_errors(domain="gol", tool="update", channel=BODY_CHANNEL):
                    Goal.from_text(format_text(spliced))
            except _CAUGHT_EXCEPTIONS as ex:
                message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
                return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])
            now = now_timestamp()
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = GolFrontmatter(**fm_data)
            write_gol_file(path, new_frontmatter, spliced)
            read_gol(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
        return _UpdateOutcome(frontmatter=new_frontmatter, pre_body=pre, post_body=spliced, offset=offset, limit=limit)

    try:
        with wrap_tool_errors(domain="gol", tool="update", channel=BODY_CHANNEL):
            Goal.from_text(format_text(content))
    except _CAUGHT_EXCEPTIONS as ex:
        message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
        return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])

    base_dir = gol_base_dir()
    with gol_lock(id_):
        try:
            path, existing = load_gol_by_id(base_dir, id_)
        except GolNotFoundError:
            parse_failure = find_parse_failure(base_dir, id_, read_gol)
            if parse_failure is None:
                raise
            failure_path, failure_error = parse_failure
            assert_within(base_dir, failure_path)
            return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
        assert_within(base_dir, path)
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = GolFrontmatter(**fm_data)
        write_gol_file(path, new_frontmatter, content)
        read_gol(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
    return _UpdateOutcome(frontmatter=new_frontmatter)


def _update_rsk(
    id_: str, content: str, offset: int | None, limit: int | None
) -> _UpdateOutcome | ParseFailureResult | ValidateResult:
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
            try:
                path, existing = load_rsk_by_id(base_dir, id_)
            except RskNotFoundError:
                parse_failure = find_parse_failure(base_dir, id_, read_rsk)
                if parse_failure is None:
                    raise
                failure_path, failure_error = parse_failure
                assert_within(base_dir, failure_path)
                return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
            assert_within(base_dir, path)
            pre = body_text(path)
            spliced = splice_body(pre, offset, limit, content)
            try:
                with wrap_tool_errors(domain="rsk", tool="update", channel=BODY_CHANNEL):
                    Risk.from_text(format_text(spliced))
            except _CAUGHT_EXCEPTIONS as ex:
                message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
                return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])
            now = now_timestamp()
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = RskFrontmatter(**fm_data)
            write_rsk_file(path, new_frontmatter, spliced)
            read_rsk(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
        return _UpdateOutcome(frontmatter=new_frontmatter, pre_body=pre, post_body=spliced, offset=offset, limit=limit)

    try:
        with wrap_tool_errors(domain="rsk", tool="update", channel=BODY_CHANNEL):
            Risk.from_text(format_text(content))
    except _CAUGHT_EXCEPTIONS as ex:
        message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
        return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])

    base_dir = rsk_base_dir()
    with rsk_lock(id_):
        try:
            path, existing = load_rsk_by_id(base_dir, id_)
        except RskNotFoundError:
            parse_failure = find_parse_failure(base_dir, id_, read_rsk)
            if parse_failure is None:
                raise
            failure_path, failure_error = parse_failure
            assert_within(base_dir, failure_path)
            return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
        assert_within(base_dir, path)
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = RskFrontmatter(**fm_data)
        write_rsk_file(path, new_frontmatter, content)
        read_rsk(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
    return _UpdateOutcome(frontmatter=new_frontmatter)


def _update_dec(
    id_: str, content: str, offset: int | None, limit: int | None
) -> _UpdateOutcome | ParseFailureResult | ValidateResult:
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
            try:
                path, existing = load_dec_by_id(base_dir, id_)
            except DecNotFoundError:
                parse_failure = find_parse_failure(base_dir, id_, read_dec)
                if parse_failure is None:
                    raise
                failure_path, failure_error = parse_failure
                assert_within(base_dir, failure_path)
                return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
            assert_within(base_dir, path)
            pre = body_text(path)
            spliced = splice_body(pre, offset, limit, content)
            try:
                with wrap_tool_errors(domain="dec", tool="update", channel=BODY_CHANNEL):
                    Decision.from_text(format_text(spliced))
            except _CAUGHT_EXCEPTIONS as ex:
                message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
                return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])
            now = now_timestamp()
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = DecFrontmatter(**fm_data)
            write_dec_file(path, new_frontmatter, spliced)
            read_dec(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
        return _UpdateOutcome(frontmatter=new_frontmatter, pre_body=pre, post_body=spliced, offset=offset, limit=limit)

    try:
        with wrap_tool_errors(domain="dec", tool="update", channel=BODY_CHANNEL):
            Decision.from_text(format_text(content))
    except _CAUGHT_EXCEPTIONS as ex:
        message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
        return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])

    base_dir = dec_base_dir()
    with dec_lock(id_):
        try:
            path, existing = load_dec_by_id(base_dir, id_)
        except DecNotFoundError:
            parse_failure = find_parse_failure(base_dir, id_, read_dec)
            if parse_failure is None:
                raise
            failure_path, failure_error = parse_failure
            assert_within(base_dir, failure_path)
            return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
        assert_within(base_dir, path)
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = DecFrontmatter(**fm_data)
        write_dec_file(path, new_frontmatter, content)
        read_dec(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
    return _UpdateOutcome(frontmatter=new_frontmatter)


def _update_feat(
    id_: str, content: str, offset: int | None, limit: int | None
) -> _UpdateOutcome | ParseFailureResult | ValidateResult:
    """Replace the body of the feature identified by ``id_`` (whole-body or line-range mode).

    Mirrors :func:`_update_dec`'s shape (same ``feat_lock``, ``load_by_id``,
    ``write_feat_file``, ``FeatNotFoundError``) with one feat-only
    divergence (see the module docstring): ``id_`` resolves via
    ``feat.tools._paths``'s bespoke folder-per-document shortcut (through
    ``load_by_id``/``feat_base_dir``), not a flat-file directory scan.
    ``updated`` is bumped to the same shared date+time timestamp as every
    other domain.
    """
    if offset is not None:
        assert limit is None or offset is not None, "the public `update` guard enforces offset with limit"

        base_dir = feat_base_dir()
        with feat_lock(id_):
            try:
                path, existing = load_feat_by_id(base_dir, id_)
            except FeatNotFoundError:
                parse_failure = find_feat_parse_failure(base_dir, id_)
                if parse_failure is None:
                    raise
                failure_path, failure_error = parse_failure
                assert_within(base_dir, failure_path)
                return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
            assert_within(base_dir, path)
            pre = body_text(path)
            spliced = splice_body(pre, offset, limit, content)
            try:
                with wrap_tool_errors(domain="feat", tool="update", channel=BODY_CHANNEL):
                    Feature.from_text(format_text(spliced))
            except _CAUGHT_EXCEPTIONS as ex:
                message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
                return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])
            now = now_timestamp()
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = FeatFrontmatter(**fm_data)
            write_feat_file(path, new_frontmatter, spliced)
            read_feat(path)  # warm the clean cache (feat-107-doc-cache Phase 4, REQ-003)
            read_feat_dirty(path)  # warm the dirty cache too (feat-187-list-feat-timeout, Task 110.130)
        return _UpdateOutcome(frontmatter=new_frontmatter, pre_body=pre, post_body=spliced, offset=offset, limit=limit)

    try:
        with wrap_tool_errors(domain="feat", tool="update", channel=BODY_CHANNEL):
            Feature.from_text(format_text(content))
    except _CAUGHT_EXCEPTIONS as ex:
        message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
        return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])

    base_dir = feat_base_dir()
    with feat_lock(id_):
        try:
            path, existing = load_feat_by_id(base_dir, id_)
        except FeatNotFoundError:
            parse_failure = find_feat_parse_failure(base_dir, id_)
            if parse_failure is None:
                raise
            failure_path, failure_error = parse_failure
            assert_within(base_dir, failure_path)
            return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
        assert_within(base_dir, path)
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = FeatFrontmatter(**fm_data)
        write_feat_file(path, new_frontmatter, content)
        read_feat(path)  # warm the clean cache (feat-107-doc-cache Phase 4, REQ-003)
        read_feat_dirty(path)  # warm the dirty cache too (feat-187-list-feat-timeout, Task 110.130)
    return _UpdateOutcome(frontmatter=new_frontmatter)


def _update_sop(
    id_: str, content: str, offset: int | None, limit: int | None
) -> _UpdateOutcome | ParseFailureResult | ValidateResult:
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
            try:
                path, existing = load_sop_by_id(base_dir, id_)
            except SopNotFoundError:
                parse_failure = find_parse_failure(base_dir, id_, read_sop)
                if parse_failure is None:
                    raise
                failure_path, failure_error = parse_failure
                assert_within(base_dir, failure_path)
                return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
            assert_within(base_dir, path)
            pre = body_text(path)
            spliced = splice_body(pre, offset, limit, content)
            try:
                with wrap_tool_errors(domain="sop", tool="update", channel=BODY_CHANNEL):
                    Sop.from_text(format_text(spliced))
            except _CAUGHT_EXCEPTIONS as ex:
                message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
                return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])
            now = now_timestamp()
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = SopFrontmatter(**fm_data)
            write_sop_file(path, new_frontmatter, spliced)
            read_sop(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
        return _UpdateOutcome(frontmatter=new_frontmatter, pre_body=pre, post_body=spliced, offset=offset, limit=limit)

    try:
        with wrap_tool_errors(domain="sop", tool="update", channel=BODY_CHANNEL):
            Sop.from_text(format_text(content))
    except _CAUGHT_EXCEPTIONS as ex:
        message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
        return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])

    base_dir = sop_base_dir()
    with sop_lock(id_):
        try:
            path, existing = load_sop_by_id(base_dir, id_)
        except SopNotFoundError:
            parse_failure = find_parse_failure(base_dir, id_, read_sop)
            if parse_failure is None:
                raise
            failure_path, failure_error = parse_failure
            assert_within(base_dir, failure_path)
            return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
        assert_within(base_dir, path)
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = SopFrontmatter(**fm_data)
        write_sop_file(path, new_frontmatter, content)
        read_sop(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
    return _UpdateOutcome(frontmatter=new_frontmatter)


def _update_vcr(
    id_: str, content: str, offset: int | None, limit: int | None
) -> _UpdateOutcome | ParseFailureResult | ValidateResult:
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
            try:
                path, existing = load_vcr_by_id(base_dir, id_)
            except VcrNotFoundError:
                parse_failure = find_parse_failure(base_dir, id_, read_vcr)
                if parse_failure is None:
                    raise
                failure_path, failure_error = parse_failure
                assert_within(base_dir, failure_path)
                return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
            assert_within(base_dir, path)
            pre = body_text(path)
            spliced = splice_body(pre, offset, limit, content)
            try:
                with wrap_tool_errors(domain="vcr", tool="update", channel=BODY_CHANNEL):
                    Vcr.from_text(format_text(spliced))
            except _CAUGHT_EXCEPTIONS as ex:
                message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
                return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])
            now = now_timestamp()
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = VcrFrontmatter(**fm_data)
            write_vcr_file(path, new_frontmatter, spliced)
            read_vcr(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
        return _UpdateOutcome(frontmatter=new_frontmatter, pre_body=pre, post_body=spliced, offset=offset, limit=limit)

    try:
        with wrap_tool_errors(domain="vcr", tool="update", channel=BODY_CHANNEL):
            Vcr.from_text(format_text(content))
    except _CAUGHT_EXCEPTIONS as ex:
        message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
        return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])

    base_dir = vcr_base_dir()
    with vcr_lock(id_):
        try:
            path, existing = load_vcr_by_id(base_dir, id_)
        except VcrNotFoundError:
            parse_failure = find_parse_failure(base_dir, id_, read_vcr)
            if parse_failure is None:
                raise
            failure_path, failure_error = parse_failure
            assert_within(base_dir, failure_path)
            return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
        assert_within(base_dir, path)
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = VcrFrontmatter(**fm_data)
        write_vcr_file(path, new_frontmatter, content)
        read_vcr(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
    return _UpdateOutcome(frontmatter=new_frontmatter)


def _update_sysrs(
    id_: str, content: str, offset: int | None, limit: int | None
) -> _UpdateOutcome | ParseFailureResult | ValidateResult:
    """Replace the body of the System Requirements Specification identified by ``id_`` (whole-body or line-range mode).

    Verbatim-shape port of :func:`_update_sop` (same ``sysrs_lock``,
    ``load_by_id``, frontmatter carry-over with only ``updated`` bumped,
    ``write_sysrs_file``, ``SysrsNotFoundError``; ``sysrs`` is dispatch-only
    from day one per ADR 36905d5b, so there was never a per-domain
    ``update_sysrs`` tool to port -- this adapter was written directly in
    this shape), plus the REQ-002 range branch (see :func:`_update_req`).
    """
    if offset is not None:
        assert limit is None or offset is not None, "the public `update` guard enforces offset with limit"

        base_dir = sysrs_base_dir()
        with sysrs_lock(id_):
            try:
                path, existing = load_sysrs_by_id(base_dir, id_)
            except SysrsNotFoundError:
                parse_failure = find_parse_failure(base_dir, id_, read_sysrs)
                if parse_failure is None:
                    raise
                failure_path, failure_error = parse_failure
                assert_within(base_dir, failure_path)
                return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
            assert_within(base_dir, path)
            pre = body_text(path)
            spliced = splice_body(pre, offset, limit, content)
            try:
                with wrap_tool_errors(domain="sysrs", tool="update", channel=BODY_CHANNEL):
                    Sysrs.from_text(format_text(spliced))
            except _CAUGHT_EXCEPTIONS as ex:
                message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
                return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])
            now = now_timestamp()
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = SysrsFrontmatter(**fm_data)
            write_sysrs_file(path, new_frontmatter, spliced)
            read_sysrs(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
        return _UpdateOutcome(frontmatter=new_frontmatter, pre_body=pre, post_body=spliced, offset=offset, limit=limit)

    try:
        with wrap_tool_errors(domain="sysrs", tool="update", channel=BODY_CHANNEL):
            Sysrs.from_text(format_text(content))
    except _CAUGHT_EXCEPTIONS as ex:
        message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
        return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])

    base_dir = sysrs_base_dir()
    with sysrs_lock(id_):
        try:
            path, existing = load_sysrs_by_id(base_dir, id_)
        except SysrsNotFoundError:
            parse_failure = find_parse_failure(base_dir, id_, read_sysrs)
            if parse_failure is None:
                raise
            failure_path, failure_error = parse_failure
            assert_within(base_dir, failure_path)
            return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
        assert_within(base_dir, path)
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = SysrsFrontmatter(**fm_data)
        write_sysrs_file(path, new_frontmatter, content)
        read_sysrs(path)  # warm the cache (feat-107-doc-cache Phase 4, REQ-003)
    return _UpdateOutcome(frontmatter=new_frontmatter)


#: Dispatch table mapping the ``type`` value to its private adapter.
_ADAPTERS: dict[
    str,
    Callable[[str, str, int | None, int | None], _UpdateOutcome | ParseFailureResult | ValidateResult],
] = {
    "req": _update_req,
    "uc": _update_uc,
    "tsk": _update_tsk,
    "qa": _update_qa,
    "prb": _update_prb,
    "gol": _update_gol,
    "rsk": _update_rsk,
    "dec": _update_dec,
    "sop": _update_sop,
    "feat": _update_feat,
    "vcr": _update_vcr,
    "sysrs": _update_sysrs,
}

assert set(_ADAPTERS) == set(WHOLE_BODY_DOMAINS), (
    "_ADAPTERS keys drifted from the shared general.tools._domains.WHOLE_BODY_DOMAINS source -- add or "
    "remove the domain in both places (feat-125-domain-lists, REQ-006)"
)


def _assemble_result(outcome: _UpdateOutcome) -> UpdateResult:
    """Assemble the public ``UpdateResult`` from one adapter's internal :class:`_UpdateOutcome`.

    The shared dispatcher's single point where the before/after ``snippet``
    is computed -- once per successful call, never inside a per-domain
    adapter (feat-153-off-by-n Phase 2, REQ-002/REQ-003, ADR
    19ff316b-cd11-41a7-a616-ffd84917da51). ``snippet`` is ``None`` in exactly
    two cases: whole-body mode (no ``offset``) and the whole-body-equivalent
    range (``offset=1`` + omitted ``limit`` -- the range :func:`_splice.
    splice_body` documents as equivalent to the no-range mode); every other
    range-mode call renders the touched range via :func:`_splice.splice_
    snippet` from the outcome's pre/post bodies and coordinates.
    """
    assert outcome.offset is None or outcome.pre_body is not None and outcome.post_body is not None
    if outcome.offset is None or (outcome.offset == _WHOLE_BODY_OFFSET and outcome.limit is None):
        result_snippet = None
    else:
        pre_body = outcome.pre_body
        post_body = outcome.post_body
        offset = outcome.offset
        assert pre_body is not None and post_body is not None and offset is not None
        result_snippet = splice_snippet(pre_body, post_body, offset, outcome.limit)
    result = UpdateResult(frontmatter=outcome.frontmatter, snippet=result_snippet)
    return result


@mcp.tool(
    name="update",
    title="Update document",
    description=(
        "Whole-body or line-range replace of an existing document's content across the "
        f"whole-body domains (`type` is one of {', '.join(WHOLE_BODY_DOMAINS)}), preserving its "
        "id/type/status/created/version; only `updated` changes. With no `offset`/`limit`, "
        "`content` is the full replacement body (body markdown only, no frontmatter block). With "
        "`offset`, `content` replaces the body line(s) starting at 1-based line `offset` of the current "
        "on-disk body: `limit` is the number of lines to replace (`offset`..`offset+limit-1`; `limit` "
        "omitted = through the last body line, `limit=0` = pure insert), and `offset=N+1` (one past "
        "the last body line) appends after it; the spliced result is validated as a whole document "
        "before anything is written. `offset`/`limit` address the frontmatter-stripped body, never "
        "the raw on-disk `.md` file: the YAML frontmatter block is variable-length, so a raw file "
        "read's line numbers are never the same as body-line coordinates -- the only safe source of "
        "coordinates is a `get_<d>(id, raw=True)` read, never a raw file read minus an assumed "
        "constant. A `get_<d>(raw=True, numbered=True)` read's numbered output must never be fed "
        'back verbatim into `content` -- strip the `"<n>: "` prefix from each line first (it is '
        "likewise never a valid `edit` `old_str`). `status` is never settable -- use the generic "
        "`set_status` tool. A document that exists but fails to parse returns a `ParseFailureResult` "
        "(`error`/`path`/`id`) instead of raising the domain's not-found error -- its `error` text "
        "is byte-identical to the domain's `list_<d>` failed row's `error` for the same file "
        "(identical field path and cause, including the trailing pydantic documentation line; "
        "ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c) -- and a truly-absent id still raises the domain's "
        "not-found error. A content-validation failure on the submitted new content (or, in range "
        "mode, on the spliced result) returns a non-raising `ValidateResult` (`valid=False`, "
        "`errors=[{message}]`) with the message capped at 300 chars as the generic `validate` tool "
        "caps it, instead of raising `AssertionError`/`pydantic.ValidationError` (ADR "
        "b8c9bfea-6dcf-4158-bfc5-4ec17abb842f, GitHub issue #170 -- case 4 of the ADR 519d1206 "
        "non-raising-structured-result workaround chain). An invalid `id` (path-injection attempt or "
        "wrong format for `type`) or misused range coordinates (`limit` without `offset`) is a "
        "`ValueError` raised before any file access. Returns an `UpdateResult`: `frontmatter`, the "
        "updated frontmatter (no body) of the dispatched domain, plus `snippet` -- in range mode, "
        "the before/after window of the touched range (dropped lines numbered pre-splice, inserted "
        "lines numbered post-splice, up to 2 unchanged context lines per side, each line "
        "`<marker> <n>: <line text>`); `snippet` is `None` in whole-body mode and for the "
        "whole-body-equivalent range (`offset=1` with `limit` omitted). Use the corresponding "
        "`get_<d>` tool to fetch the full document afterward."
    ),
)
def update(
    id: str,
    type: WholeBodyType,
    content: str,
    offset: int | None = None,
    limit: int | None = None,
) -> UpdateResult | ParseFailureResult | ValidateResult:
    """Replace the body of an existing document, in whole-body or line-range mode.

    Cross-domain generic for the whole-body document types
    (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/``sysrs``);
    dispatches on ``type`` to the domain's own ported adapter (same lock,
    same id resolution, same frontmatter carry-over, same verbatim
    persistence, same domain not-found error).

    **Whole-body mode** (no ``offset``/``limit``): ``content`` is body
    markdown only, with no YAML frontmatter block -- the same shape the
    per-domain ``update_<d>`` tools accept. Validated the same way: the
    domain body model's ``from_text(format_text(content))`` -- a
    structural (``AssertionError``) or field/cross-field
    (``pydantic.ValidationError``) failure returns the non-raising
    ``ValidateResult(valid=False, ...)`` (the single ``errors[].message``
    capped at 300 chars exactly as the generic ``validate`` tool caps it,
    feat-110 -- feat-170-update-edit-parse-failure, GitHub issue #170, ADR
    b8c9bfea-6dcf-4158-bfc5-4ec17abb842f, case 4 of the ADR 519d1206 chain)
    with nothing written.

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
    date+time timestamp, via ``general.tools._timestamps.now_timestamp()``);
    ``status`` in particular is never settable through this tool -- the
    generic ``set_status`` tool in ``general.tools`` is the only
    status-change path.

    Safety (REQ-009, feat-38-39-41-43-44 Phase 4, mirroring ``delete``'s
    own REQ-003): ``id`` is validated via ``_path_safety.validate_id`` (no
    ``/``, no ``\\``, no ``..``, plus the dispatched domain's own format --
    canonical lowercase-hex UUID for every domain other than ``feat``,
    ``feat-NNN-slug`` for ``feat``) **before** any filesystem access, so a path-injection
    attempt or a wrong-format id is a ``ValueError`` raised before dispatch.
    Each adapter additionally confines the resolved path to the domain's
    own base directory with ``_path_safety.assert_within`` inside the
    lock -- defense-in-depth against any future gap in the id validation.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    type:
        The document type / domain: one of ``req``, ``uc``, ``tsk``,
        ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``, ``feat``,
        ``vcr``, ``sysrs``.
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
    UpdateResult | ParseFailureResult | ValidateResult
        On success, the updated document's
        :class:`~biz.dfch.specmgr.general.models.UpdateResult` wrapper
        (feat-153-off-by-n Phase 2, ADR 19ff316b-cd11-41a7-a616-ffd84917da51):
        its ``frontmatter`` is the updated frontmatter only (no body) of
        the dispatched domain type -- the same object feature
        feat-69-update-context's "frontmatter-only" precedent returned --
        and its ``snippet`` is, in range mode, the before/after window of
        the touched range: up to 2 unchanged context lines above, the
        dropped lines (numbered with their pre-splice 1-based body-line
        numbers), the inserted lines (numbered with their post-splice
        numbers), and up to 2 unchanged context lines below, each line
        formatted ``<marker> <n>: <line text>`` (marker ``-``/``+``/
        single space); the two numbering sequences are independent and
        need not be contiguous when the replacement changes the line
        count. ``snippet`` is ``None`` in exactly two cases: whole-body
        mode (no ``offset``) and the whole-body-equivalent range
        (``offset=1`` with omitted ``limit``). The ``offset``/``limit``
        coordinates address lines of the frontmatter-stripped body --
        never lines of the raw on-disk ``.md`` file (whose YAML
        frontmatter block is variable-length, so a raw file read's line
        numbers are never the same as body-line coordinates) -- the only
        safe source of coordinates is a ``get_<d>(id, raw=True)`` read
        (optionally ``numbered=True``), never a raw file read minus an
        assumed constant, and a numbered read's output must never be fed
        back verbatim into ``content`` (strip the ``"<n>: "`` prefix
        first; it is likewise never a valid ``edit`` ``old_str``). Use
        the corresponding ``get_<d>`` tool to fetch the full document
        afterward. On a target ``id`` whose only matching on-disk file
        fails to parse, a non-raising
        :class:`~biz.dfch.specmgr.general.models.ParseFailureResult`
        (``error``/``path``/``id``) instead of the domain's not-found
        error -- ``error`` is byte-identical to the domain's ``list_<d>``
        failed row's ``error`` for the same file (identical field path and
        cause, including the trailing pydantic documentation line; ADR
        9080b37c-82b3-4f63-81f1-79641d0bf14c). On a content-validation
        failure of the submitted new content (or, in range mode, of the
        spliced result), a non-raising
        :class:`~biz.dfch.specmgr.general.models.ValidateResult`
        (``valid=False``, ``errors=[{message}]``) with the single
        ``errors[].message`` capped at 300 chars exactly as the generic
        ``validate`` tool caps it (feat-110), instead of
        ``AssertionError``/``pydantic.ValidationError``. Nothing is written
        in either failure case (feat-170-update-edit-parse-failure, GitHub
        issue #170, ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f -- case 4 of
        the ADR 519d1206-4d2a-4500-9046-6db635209996 non-raising,
        structured-result workaround chain).

    Raises
    ------
    ValueError
        ``id`` is a path-injection attempt or not in the dispatched
        domain's own format (raised before any filesystem access; nothing
        is written). Also raised for misused range coordinates: ``limit``
        given without ``offset`` (raised before any file access), or
        ``offset < 1``, ``offset > N + 1``, ``limit < 0``, or
        ``offset + limit - 1 > N`` (raised after the on-disk body is read;
        the message names the offending value(s) and the allowed range).
        Nothing is written in any of these cases.
    KeyError
        A plain ``KeyError`` still marks ``type="adr"`` (inherited from
        the dispatch-table lookup): ``adr`` is in ``_path_safety``'s
        UUID-shaped domain set, so ``type="adr"`` with a well-formed
        UUID ``id`` passes ``validate_id`` and reaches the lookup, which
        has no ``adr`` entry. Nothing is written. Unreachable through the
        MCP server, whose ``type`` enum carries the 12 whole-body domains
        only; a direct-Python-caller outcome.
    ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError /
    PrbNotFoundError / GolNotFoundError / RskNotFoundError / DecNotFoundError /
    FeatNotFoundError / SopNotFoundError / VcrNotFoundError / SysrsNotFoundError
        The target id is truly absent (no file on disk matches it at all)
        -- the domain's own not-found error, unchanged from the per-domain
        tools. An existing-but-broken document returns the non-raising
        ``ParseFailureResult`` instead, and a content-validation failure of
        the submitted/spliced content returns the non-raising
        ``ValidateResult`` instead (both see Returns).
    """
    # REQ-009: validate before any filesystem access (injection prevention).
    validate_id(type, id)
    if offset is None and limit is not None:
        raise ValueError(f"limit must be given together with offset, got offset={offset!r}, limit={limit!r}")

    adapter = _ADAPTERS[type]
    result = adapter(id, content, offset, limit)
    if isinstance(result, (ParseFailureResult, ValidateResult)):
        return result
    return _assemble_result(result)
