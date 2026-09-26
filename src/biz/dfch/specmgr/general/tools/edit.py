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

"""``@mcp.tool()`` wrapper: edit (feat-159-edit, GitHub issue #159).

The generic, cross-domain, surgical exact-match string-replacement tool for
the frontmatter-stripped body of the whole-body document types
(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/
``feat``/``vcr``/``sysrs``). It dispatches on the explicit ``type``
parameter to a private per-domain adapter (``_edit_<d>``), each mirroring
the generic ``update`` tool's own adapter shape (same domain lock, same
``load_by_id``, same frontmatter carry-over with only ``updated`` bumped,
same verbatim persistence via the domain's own ``write_<d>_file``, same
domain ``XNotFoundError``, same doc-cache warm) with a different in-lock
sequence: the domain lock is held **across the entire read -> match ->
validate -> write**, because the match runs against *on-disk* content
(unlike ``update``'s whole-body mode, which validates client-supplied
content before taking the lock) -- reading the body outside the lock would
be a TOCTOU race.

The signature and the stage-1 runtime error strings mirror the OpenCode
``edit`` tool (parity pinned to opencode dev commit
``236cfcbbc31530fde6a9e65318703f40adad8455``,
``packages/opencode/src/tool/edit.ts`` ``replace()``; see the feature
README's Design Notes): the exact-match semantics, the optional
``replace_all`` flag, and the four verbatim stage-1 messages (the
identical-input guard, the empty-``old_str`` guard -- OC's ``write``
reference adapted to specmgr's ``update`` --, the not-found message, and
the multiple-matches message). OC's 9-stage fuzzy matcher chain -- and its
``isDisproportionateMatch`` refusal guard, which exists only to police
those fuzzy stages -- is deliberately not replicated: this tool is
exact-match only.

**2-fold contract (REQ-003).** The edited document is written to disk only
if both stages pass: stage 1 (match) counts exact ``old_str`` occurrences
in the on-disk body -- zero -> the OC not-found ``ValueError``, more than
one without ``replace_all`` -> the OC multiple-matches ``ValueError`` --
then stage 2 validates the *edited* body as a whole document via
``<Domain>.from_text(format_text(edited))`` under ``wrap_tool_errors``.
The disk write via ``write_<d>_file`` happens strictly after stage 2
succeeds; on any failure (either stage) nothing is written and the file is
byte-unchanged.

**Stage-1 errors are plain ``ValueError``s (REQ-002/REQ-008, D3).** The
four stage-1 failures (identical input, empty ``old_str``, not found,
multiple matches) each raise a plain ``ValueError`` carrying the OC message
verbatim with **no** ``domain tool (channel)`` wrap prefix -- they are
client-controlled-input guards (the ``update`` tool's coordinate-guard
precedent), not document-structure failures; ``wrap_tool_errors`` applies
to stage 2 only, exactly as in ``update``. The two match-stage strings,
quoted verbatim from the pinned commit (parity targets the *runtime*
strings -- OC's own tool description text promises different messages that
its runtime never throws)::

    Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.
    Found multiple matches for oldString. Provide more surrounding context to make the match unique.

**Byte-exact matching (REQ-009, D2).** Matching is pure byte-exact over
the frontmatter-stripped body text the shared ``body_text`` helper returns
(the same text ``get_<d>(id, raw=True)`` returns): no line-ending
normalization (OC's file-dominant-EOL conversion is deliberately not
replicated -- an ``old_str`` containing a ``\\n`` will not match a CRLF
body), no BOM handling (UTF-8, like every other tool), no fuzzy/regex
fallback. ``replace_all`` rewrites every exact occurrence; an empty
``new_str`` (a pure deletion, REQ-001, D1) is legal iff stage 2 validates
the result.

**Explicit type check (REQ-004, D4).** Unlike ``update``/``delete``/
``set_classification`` -- whose dispatch-table lookup inherits a
``KeyError`` for ``type="adr"`` -- the public :func:`edit` raises an
explicit ``ValueError`` for an unknown or ``adr`` ``type`` before
dispatch, following the generic ``validate`` tool's own precedent (ADR
078bf395-0a5f-4afd-84f6-b7a2191a00e6). ADR is deliberately *not* a
``type`` here: its section-level MADR mutation contract
(``update_frontmatter``/``update_section``/``option_*``) has no whole-body
replace by design, and an exact-match body edit is outside it.

**Persistence (REQ-006).** On success the existing frontmatter is carried
over with only ``updated`` bumped (via ``now_timestamp()``), the edited
body is persisted verbatim via the domain's own ``write_<d>_file`` (no
mdformat reformat on write -- ``format_text`` is applied during validation
only, exactly like ``update``; "verbatim" is additionally modulo the
python-frontmatter ``YAMLHandler``'s trailing-whitespace strip on
serialization, the inherited ``_write.py`` caveat identical to
``update``), the domain doc cache is warmed via the domain's own
``read_<d>`` (the feat-107-doc-cache precedent), and the updated
frontmatter only is returned (no body).

**Safety (REQ-005).** The public :func:`edit` validates ``id`` via
``_path_safety.validate_id`` before any filesystem access (a
``ValueError`` before any file access -- mirroring the generic ``update``
tool's own guard), and every adapter confines the resolved path to the
domain's own base directory with ``_path_safety.assert_within`` after
``load_by_id``, inside the domain lock.

OC's read-before-edit enforcement is a *client* session-state convention
in OC; no server-side counterpart is replicated (nothing is enforced
here), and the tool description instead documents the convention to read
the current body via ``get_<d>(id, raw=True)`` before editing.

The parameter is intentionally named ``type`` (it matches the frontmatter
field vocabulary the client already knows); no enabled ruff rule objects
to the builtin shadow. The union return type is annotation-only -- the
MCP input schema is built from the parameters, and the SDK serializes
whichever concrete frontmatter model is returned.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from ...dec.models.v1 import DecFrontmatter, Decision
from ...dec.tools._io import load_by_id as load_dec_by_id
from ...dec.tools._io import read_dec
from ...dec.tools._lock import dec_lock
from ...dec.tools._paths import dec_base_dir
from ...dec.tools._write import write_dec_file
from ...feat.models.v1 import FeatFrontmatter, Feature
from ...feat.tools._cache import read_feat
from ...feat.tools._io import load_by_id as load_feat_by_id
from ...feat.tools._lock import feat_lock
from ...feat.tools._paths import feat_base_dir
from ...feat.tools._write import write_feat_file
from ...gol.models.v1 import GolFrontmatter, Goal
from ...gol.tools._io import load_by_id as load_gol_by_id
from ...gol.tools._io import read_gol
from ...gol.tools._lock import gol_lock
from ...gol.tools._paths import gol_base_dir
from ...gol.tools._write import write_gol_file
from ...models.md._errors import BODY_CHANNEL, wrap_tool_errors
from ...models.md._markdown import format_text
from ...prb.models.v1 import Prb, PrbFrontmatter
from ...prb.tools._io import load_by_id as load_prb_by_id
from ...prb.tools._io import read_prb
from ...prb.tools._lock import prb_lock
from ...prb.tools._paths import prb_base_dir
from ...prb.tools._write import write_prb_file
from ...qa.models.v2 import Qa, QaFrontmatter
from ...qa.tools._io import load_by_id as load_qa_by_id
from ...qa.tools._io import read_qa
from ...qa.tools._lock import qa_lock
from ...qa.tools._paths import qa_base_dir
from ...qa.tools._write import write_qa_file
from ...req.models.v1 import ReqFrontmatter, Requirement
from ...req.tools._io import load_by_id as load_req_by_id
from ...req.tools._io import read_req
from ...req.tools._lock import req_lock
from ...req.tools._paths import req_base_dir
from ...req.tools._write import write_req_file
from ...rsk.models.v1 import Risk, RskFrontmatter
from ...rsk.tools._io import load_by_id as load_rsk_by_id
from ...rsk.tools._io import read_rsk
from ...rsk.tools._lock import rsk_lock
from ...rsk.tools._paths import rsk_base_dir
from ...rsk.tools._write import write_rsk_file
from ...server import mcp
from ...sop.models.v1 import Sop, SopFrontmatter
from ...sop.tools._io import load_by_id as load_sop_by_id
from ...sop.tools._io import read_sop
from ...sop.tools._lock import sop_lock
from ...sop.tools._paths import sop_base_dir
from ...sop.tools._write import write_sop_file
from ...sysrs.models.v1 import Sysrs, SysrsFrontmatter
from ...sysrs.tools._io import load_by_id as load_sysrs_by_id
from ...sysrs.tools._io import read_sysrs
from ...sysrs.tools._lock import sysrs_lock
from ...sysrs.tools._paths import sysrs_base_dir
from ...sysrs.tools._write import write_sysrs_file
from ...tsk.models.v1 import Task, TskFrontmatter
from ...tsk.tools._io import load_by_id as load_tsk_by_id
from ...tsk.tools._io import read_tsk
from ...tsk.tools._lock import tsk_lock
from ...tsk.tools._paths import tsk_base_dir
from ...tsk.tools._write import write_tsk_file
from ...uc.models.v2 import UcFrontmatter, UseCase
from ...uc.tools._io import load_by_id as load_uc_by_id
from ...uc.tools._io import read_uc
from ...uc.tools._lock import uc_lock
from ...uc.tools._paths import uc_base_dir
from ...uc.tools._write import write_uc_file
from ...vcr.models.v1 import Vcr, VcrFrontmatter
from ...vcr.tools._io import load_by_id as load_vcr_by_id
from ...vcr.tools._io import read_vcr
from ...vcr.tools._lock import vcr_lock
from ...vcr.tools._paths import vcr_base_dir
from ...vcr.tools._write import write_vcr_file
from ._domains import WHOLE_BODY_DOMAINS
from ._path_safety import assert_within, validate_id
from ._splice import body_text
from ._timestamps import now_timestamp

__all__ = ["edit"]

#: The generic tool's return union -- annotation-only (see module docstring).
_EditFrontmatter = (
    ReqFrontmatter
    | UcFrontmatter
    | TskFrontmatter
    | QaFrontmatter
    | PrbFrontmatter
    | GolFrontmatter
    | RskFrontmatter
    | DecFrontmatter
    | FeatFrontmatter
    | SopFrontmatter
    | VcrFrontmatter
    | SysrsFrontmatter
)


def _match_and_replace(body: str, old_str: str, new_str: str, replace_all: bool) -> str:
    """Stage 1 of the 2-fold edit contract: byte-exact match and replace (REQ-009, D2).

    Domain-agnostic: the per-domain ``_edit_<d>`` adapters call this on the
    on-disk body text (:func:`body_text`'s result -- the same text
    ``get_<d>(id, raw=True)`` returns) and stage-2-validate, persist, and
    cache-warm the returned edited body themselves.

    Counts exact ``old_str`` occurrences in ``body``: zero occurrences
    raises the OC not-found ``ValueError`` verbatim (REQ-002, the pinned
    string quoted in the module docstring); more than one occurrence
    without ``replace_all`` raises the OC multiple-matches ``ValueError``
    verbatim. Matching is pure byte-exact -- no line-ending normalization
    (an ``old_str`` containing a ``\\n`` will not match a CRLF body), no
    BOM handling, no fuzzy/regex fallback. A successful match is applied
    via ``str.replace`` (``count=1`` for the single rewrite, no ``count``
    for ``replace_all``); an empty ``new_str`` (a pure deletion, REQ-001)
    is legal here -- its validity is stage 2's job. The raised
    ``ValueError``s are plain, with no ``domain tool (channel)`` wrap
    prefix (D3).

    Parameters
    ----------
    body:
        The current frontmatter-stripped on-disk body text.
    old_str:
        The exact text to find (byte-exact; never empty -- the public
        :func:`edit` guard rejects an empty ``old_str`` before dispatch).
    new_str:
        The replacement text; the empty string deletes the match(es).
    replace_all:
        ``True``: rewrite every exact occurrence. ``False``: the match must
        be unique (exactly one occurrence), else the multiple-matches
        error.

    Returns
    -------
    str
        The edited body text (one replacement applied, or all of them when
        ``replace_all``).

    Raises
    ------
    ValueError
        ``old_str`` is not found at all, or is found more than once while
        ``replace_all`` is ``False`` -- the OC message verbatim, plain (no
        wrap prefix), nothing written.
    """
    assert isinstance(body, str), type(body)
    assert isinstance(old_str, str), type(old_str)
    assert isinstance(new_str, str), type(new_str)
    assert isinstance(replace_all, bool), type(replace_all)

    count = body.count(old_str)
    if count == 0:
        raise ValueError(
            "Could not find oldString in the file. It must match exactly, including whitespace, "
            "indentation, and line endings."
        )
    if count > 1 and not replace_all:
        raise ValueError(
            "Found multiple matches for oldString. Provide more surrounding context to make the match unique."
        )
    result = body.replace(old_str, new_str) if replace_all else body.replace(old_str, new_str, 1)
    return result


def _edit_req(id_: str, old_str: str, new_str: str, replace_all: bool) -> ReqFrontmatter:
    """Surgically replace exact occurrences of ``old_str`` in the requirement identified by ``id_``.

    Mirror of the generic ``update`` tool's own ``_update_req`` adapter
    shape (same ``req_lock``, ``load_by_id``, frontmatter carry-over with
    only ``updated`` bumped, ``write_req_file``, ``ReqNotFoundError``) with
    the edit-specific in-lock sequence (see the module docstring): the
    domain lock is held across the entire read -> match -> validate ->
    write, stage 1 is the domain-agnostic :func:`_match_and_replace` over
    :func:`body_text(path)`, and stage 2 validates the *edited* body as a
    whole document before the verbatim persist and the cache warm.
    """
    base_dir = req_base_dir()
    with req_lock(id_):
        path, existing = load_req_by_id(base_dir, id_)
        assert_within(base_dir, path)
        edited = _match_and_replace(body_text(path), old_str, new_str, replace_all)
        with wrap_tool_errors(domain="req", tool="edit", channel=BODY_CHANNEL):
            Requirement.from_text(format_text(edited))
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = ReqFrontmatter(**fm_data)
        write_req_file(path, new_frontmatter, edited)
        read_req(path)  # warm the cache (feat-107-doc-cache, REQ-006)
    return new_frontmatter


def _edit_uc(id_: str, old_str: str, new_str: str, replace_all: bool) -> UcFrontmatter:
    """Surgically replace exact occurrences of ``old_str`` in the use case identified by ``id_``.

    Mirror of :func:`_edit_req`'s shape (same ``uc_lock``, ``load_by_id``,
    frontmatter carry-over with only ``updated`` bumped, ``write_uc_file``,
    ``UcNotFoundError``).
    """
    base_dir = uc_base_dir()
    with uc_lock(id_):
        path, existing = load_uc_by_id(base_dir, id_)
        assert_within(base_dir, path)
        edited = _match_and_replace(body_text(path), old_str, new_str, replace_all)
        with wrap_tool_errors(domain="uc", tool="edit", channel=BODY_CHANNEL):
            UseCase.from_text(format_text(edited))
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = UcFrontmatter(**fm_data)
        write_uc_file(path, new_frontmatter, edited)
        read_uc(path)  # warm the cache (feat-107-doc-cache, REQ-006)
    return new_frontmatter


def _edit_tsk(id_: str, old_str: str, new_str: str, replace_all: bool) -> TskFrontmatter:
    """Surgically replace exact occurrences of ``old_str`` in the task list identified by ``id_``.

    Mirror of :func:`_edit_req`'s shape (same ``tsk_lock``, ``load_by_id``,
    frontmatter carry-over with only ``updated`` bumped, ``write_tsk_file``,
    ``TskNotFoundError``).
    """
    base_dir = tsk_base_dir()
    with tsk_lock(id_):
        path, existing = load_tsk_by_id(base_dir, id_)
        assert_within(base_dir, path)
        edited = _match_and_replace(body_text(path), old_str, new_str, replace_all)
        with wrap_tool_errors(domain="tsk", tool="edit", channel=BODY_CHANNEL):
            Task.from_text(format_text(edited))
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = TskFrontmatter(**fm_data)
        write_tsk_file(path, new_frontmatter, edited)
        read_tsk(path)  # warm the cache (feat-107-doc-cache, REQ-006)
    return new_frontmatter


def _edit_qa(id_: str, old_str: str, new_str: str, replace_all: bool) -> QaFrontmatter:
    """Surgically replace exact occurrences of ``old_str`` in the QA document identified by ``id_``.

    Mirror of :func:`_edit_req`'s shape (same ``qa_lock``, ``load_by_id``,
    frontmatter carry-over with only ``updated`` bumped, ``write_qa_file``,
    ``QaNotFoundError``).
    """
    base_dir = qa_base_dir()
    with qa_lock(id_):
        path, existing = load_qa_by_id(base_dir, id_)
        assert_within(base_dir, path)
        edited = _match_and_replace(body_text(path), old_str, new_str, replace_all)
        with wrap_tool_errors(domain="qa", tool="edit", channel=BODY_CHANNEL):
            Qa.from_text(format_text(edited))
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = QaFrontmatter(**fm_data)
        write_qa_file(path, new_frontmatter, edited)
        read_qa(path)  # warm the cache (feat-107-doc-cache, REQ-006)
    return new_frontmatter


def _edit_prb(id_: str, old_str: str, new_str: str, replace_all: bool) -> PrbFrontmatter:
    """Surgically replace exact occurrences of ``old_str`` in the problem statement identified by ``id_``.

    Mirror of :func:`_edit_req`'s shape (same ``prb_lock``, ``load_by_id``,
    frontmatter carry-over with only ``updated`` bumped, ``write_prb_file``,
    ``PrbNotFoundError``).
    """
    base_dir = prb_base_dir()
    with prb_lock(id_):
        path, existing = load_prb_by_id(base_dir, id_)
        assert_within(base_dir, path)
        edited = _match_and_replace(body_text(path), old_str, new_str, replace_all)
        with wrap_tool_errors(domain="prb", tool="edit", channel=BODY_CHANNEL):
            Prb.from_text(format_text(edited))
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = PrbFrontmatter(**fm_data)
        write_prb_file(path, new_frontmatter, edited)
        read_prb(path)  # warm the cache (feat-107-doc-cache, REQ-006)
    return new_frontmatter


def _edit_gol(id_: str, old_str: str, new_str: str, replace_all: bool) -> GolFrontmatter:
    """Surgically replace exact occurrences of ``old_str`` in the goal identified by ``id_``.

    Mirror of :func:`_edit_req`'s shape (same ``gol_lock``, ``load_by_id``,
    frontmatter carry-over with only ``updated`` bumped, ``write_gol_file``,
    ``GolNotFoundError``).
    """
    base_dir = gol_base_dir()
    with gol_lock(id_):
        path, existing = load_gol_by_id(base_dir, id_)
        assert_within(base_dir, path)
        edited = _match_and_replace(body_text(path), old_str, new_str, replace_all)
        with wrap_tool_errors(domain="gol", tool="edit", channel=BODY_CHANNEL):
            Goal.from_text(format_text(edited))
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = GolFrontmatter(**fm_data)
        write_gol_file(path, new_frontmatter, edited)
        read_gol(path)  # warm the cache (feat-107-doc-cache, REQ-006)
    return new_frontmatter


def _edit_rsk(id_: str, old_str: str, new_str: str, replace_all: bool) -> RskFrontmatter:
    """Surgically replace exact occurrences of ``old_str`` in the risk identified by ``id_``.

    Mirror of :func:`_edit_req`'s shape (same ``rsk_lock``, ``load_by_id``,
    frontmatter carry-over with only ``updated`` bumped, ``write_rsk_file``,
    ``RskNotFoundError``).
    """
    base_dir = rsk_base_dir()
    with rsk_lock(id_):
        path, existing = load_rsk_by_id(base_dir, id_)
        assert_within(base_dir, path)
        edited = _match_and_replace(body_text(path), old_str, new_str, replace_all)
        with wrap_tool_errors(domain="rsk", tool="edit", channel=BODY_CHANNEL):
            Risk.from_text(format_text(edited))
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = RskFrontmatter(**fm_data)
        write_rsk_file(path, new_frontmatter, edited)
        read_rsk(path)  # warm the cache (feat-107-doc-cache, REQ-006)
    return new_frontmatter


def _edit_dec(id_: str, old_str: str, new_str: str, replace_all: bool) -> DecFrontmatter:
    """Surgically replace exact occurrences of ``old_str`` in the decision identified by ``id_``.

    Mirror of :func:`_edit_req`'s shape (same ``dec_lock``, ``load_by_id``,
    frontmatter carry-over with only ``updated`` bumped, ``write_dec_file``,
    ``DecNotFoundError``).
    """
    base_dir = dec_base_dir()
    with dec_lock(id_):
        path, existing = load_dec_by_id(base_dir, id_)
        assert_within(base_dir, path)
        edited = _match_and_replace(body_text(path), old_str, new_str, replace_all)
        with wrap_tool_errors(domain="dec", tool="edit", channel=BODY_CHANNEL):
            Decision.from_text(format_text(edited))
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = DecFrontmatter(**fm_data)
        write_dec_file(path, new_frontmatter, edited)
        read_dec(path)  # warm the cache (feat-107-doc-cache, REQ-006)
    return new_frontmatter


def _edit_feat(id_: str, old_str: str, new_str: str, replace_all: bool) -> FeatFrontmatter:
    """Surgically replace exact occurrences of ``old_str`` in the feature identified by ``id_``.

    Mirror of :func:`_edit_dec`'s shape (same ``feat_lock``, ``load_by_id``,
    ``write_feat_file``, ``FeatNotFoundError``) with one feat-only
    divergence (see the module docstring): ``id_`` resolves via
    ``feat.tools._paths``'s bespoke folder-per-document shortcut (through
    ``load_by_id``/``feat_base_dir``), not a flat-file directory scan.
    """
    base_dir = feat_base_dir()
    with feat_lock(id_):
        path, existing = load_feat_by_id(base_dir, id_)
        assert_within(base_dir, path)
        edited = _match_and_replace(body_text(path), old_str, new_str, replace_all)
        with wrap_tool_errors(domain="feat", tool="edit", channel=BODY_CHANNEL):
            Feature.from_text(format_text(edited))
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = FeatFrontmatter(**fm_data)
        write_feat_file(path, new_frontmatter, edited)
        read_feat(path)  # warm the cache (feat-107-doc-cache, REQ-006)
    return new_frontmatter


def _edit_sop(id_: str, old_str: str, new_str: str, replace_all: bool) -> SopFrontmatter:
    """Surgically replace exact occurrences of ``old_str`` in the SOP identified by ``id_``.

    Mirror of :func:`_edit_req`'s shape (same ``sop_lock``, ``load_by_id``,
    frontmatter carry-over with only ``updated`` bumped, ``write_sop_file``,
    ``SopNotFoundError``).
    """
    base_dir = sop_base_dir()
    with sop_lock(id_):
        path, existing = load_sop_by_id(base_dir, id_)
        assert_within(base_dir, path)
        edited = _match_and_replace(body_text(path), old_str, new_str, replace_all)
        with wrap_tool_errors(domain="sop", tool="edit", channel=BODY_CHANNEL):
            Sop.from_text(format_text(edited))
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = SopFrontmatter(**fm_data)
        write_sop_file(path, new_frontmatter, edited)
        read_sop(path)  # warm the cache (feat-107-doc-cache, REQ-006)
    return new_frontmatter


def _edit_vcr(id_: str, old_str: str, new_str: str, replace_all: bool) -> VcrFrontmatter:
    """Surgically replace exact occurrences of ``old_str`` in the verification case record identified by ``id_``.

    Mirror of :func:`_edit_req`'s shape (same ``vcr_lock``, ``load_by_id``,
    frontmatter carry-over with only ``updated`` bumped, ``write_vcr_file``,
    ``VcrNotFoundError``).
    """
    base_dir = vcr_base_dir()
    with vcr_lock(id_):
        path, existing = load_vcr_by_id(base_dir, id_)
        assert_within(base_dir, path)
        edited = _match_and_replace(body_text(path), old_str, new_str, replace_all)
        with wrap_tool_errors(domain="vcr", tool="edit", channel=BODY_CHANNEL):
            Vcr.from_text(format_text(edited))
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = VcrFrontmatter(**fm_data)
        write_vcr_file(path, new_frontmatter, edited)
        read_vcr(path)  # warm the cache (feat-107-doc-cache, REQ-006)
    return new_frontmatter


def _edit_sysrs(id_: str, old_str: str, new_str: str, replace_all: bool) -> SysrsFrontmatter:
    """Surgically replace exact occurrences of ``old_str`` in the System Requirements Specification for ``id_``.

    Mirror of :func:`_edit_req`'s shape (same ``sysrs_lock``, ``load_by_id``,
    frontmatter carry-over with only ``updated`` bumped,
    ``write_sysrs_file``, ``SysrsNotFoundError``).
    """
    base_dir = sysrs_base_dir()
    with sysrs_lock(id_):
        path, existing = load_sysrs_by_id(base_dir, id_)
        assert_within(base_dir, path)
        edited = _match_and_replace(body_text(path), old_str, new_str, replace_all)
        with wrap_tool_errors(domain="sysrs", tool="edit", channel=BODY_CHANNEL):
            Sysrs.from_text(format_text(edited))
        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = SysrsFrontmatter(**fm_data)
        write_sysrs_file(path, new_frontmatter, edited)
        read_sysrs(path)  # warm the cache (feat-107-doc-cache, REQ-006)
    return new_frontmatter


#: Dispatch table mapping the ``type`` value to its private adapter.
_ADAPTERS: dict[str, Callable[[str, str, str, bool], _EditFrontmatter]] = {
    "req": _edit_req,
    "uc": _edit_uc,
    "tsk": _edit_tsk,
    "qa": _edit_qa,
    "prb": _edit_prb,
    "gol": _edit_gol,
    "rsk": _edit_rsk,
    "dec": _edit_dec,
    "sop": _edit_sop,
    "feat": _edit_feat,
    "vcr": _edit_vcr,
    "sysrs": _edit_sysrs,
}

assert set(_ADAPTERS) == set(WHOLE_BODY_DOMAINS), (
    "_ADAPTERS keys drifted from the shared general.tools._domains.WHOLE_BODY_DOMAINS source -- add or "
    "remove the domain in both places (feat-159-edit, GitHub issue #159)"
)


@mcp.tool(
    name="edit",
    title="Edit document",
    description=(
        "Surgical, exact-match string replacement of an existing document's frontmatter-stripped body "
        f"across the whole-body domains (`type` is one of {', '.join(WHOLE_BODY_DOMAINS)}; `adr` is not "
        "supported -- an explicit pre-dispatch `ValueError`, unlike `update`'s inherited `KeyError`). "
        "Read the current body via the corresponding `get_<d>(id, raw=True)` first -- the read-before-edit "
        "step is a client convention, not server-enforced. Use `edit` for a surgical string replacement "
        "within an existing body; use the generic `update` tool for a whole-body or line-range replacement "
        "instead. The YAML frontmatter is never addressable (body only). The edit is 2-fold: stage 1 "
        "requires `old_str` to match the on-disk body byte-exactly -- uniquely, unless `replace_all` is "
        "`true`, in which case every exact occurrence is rewritten -- and stage 2 validates the *edited* "
        "body as a whole document; the document is written to disk only if both stages pass, and nothing "
        "is written on any failure (the file stays byte-unchanged). An empty `new_str` is a pure deletion "
        "(legal iff stage 2 validates). Matching is pure byte-exact with no line-ending normalization (an "
        "`old_str` containing `\\n` will not match a CRLF body), no BOM handling, and no fuzzy/regex "
        "fallback. An invalid `id` (path-injection attempt or wrong format for `type`) is a `ValueError` "
        "raised before any file access. Returns the updated frontmatter only (no body; `updated` bumped); "
        "use the corresponding `get_<d>` tool to fetch the full document afterward."
    ),
)
def edit(
    id: str,
    type: Literal[*WHOLE_BODY_DOMAINS],
    old_str: str,
    new_str: str,
    replace_all: bool = False,
) -> _EditFrontmatter:
    """Surgically replace a byte-exact occurrence of ``old_str`` in an existing document's body.

    Cross-domain generic for the whole-body document types
    (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/
    ``feat``/``vcr``/``sysrs``); dispatches on ``type`` to the domain's own
    private adapter (same lock, same id resolution, same frontmatter
    carry-over, same verbatim persistence, same domain not-found error).
    The signature and the stage-1 runtime error strings mirror the
    OpenCode ``edit`` tool (parity pinned in the module docstring).

    **Stage 1 (match).** ``old_str`` is counted byte-exactly in the
    current frontmatter-stripped on-disk body (the text
    ``get_<d>(id, raw=True)`` returns): no line-ending normalization, no
    BOM handling, no fuzzy/regex fallback. Zero occurrences raise the OC
    not-found ``ValueError`` verbatim; more than one occurrence raises the
    OC multiple-matches ``ValueError`` verbatim unless ``replace_all`` is
    ``True``, in which case every exact occurrence is rewritten. An empty
    ``new_str`` (a pure deletion, REQ-001) is legal iff stage 2 validates
    the result.

    **Stage 2 (validate).** The *edited* body is validated as a whole
    document via the domain body model's ``from_text(format_text(edited))``
    under ``wrap_tool_errors`` -- letting ``AssertionError`` (structural
    failure) or ``pydantic.ValidationError`` (field/cross-field failure)
    propagate uncaught, with nothing written in either case.

    **2-fold write (REQ-003).** The disk write happens strictly after both
    stages pass: the domain lock is held across the entire read -> match ->
    validate -> write sequence (the match is against on-disk content, so
    reading it outside the lock would be a TOCTOU race -- unlike
    ``update``'s whole-body mode, which validates client-supplied content
    before taking the lock), the existing frontmatter is carried over with
    every field preserved except ``updated`` (bumped to the current
    date+time timestamp, via ``general.tools._timestamps.now_timestamp()``),
    the edited body is persisted verbatim (no mdformat reformat on write --
    ``format_text`` is applied during validation only, exactly like
    ``update``), the domain doc cache is warmed via the domain's own
    ``read_<d>`` (the feat-107-doc-cache precedent), and the updated
    frontmatter only is returned (no body). On any failure (either stage)
    nothing is written and the file is byte-unchanged.

    Safety (REQ-005): ``id`` is validated via ``_path_safety.validate_id``
    **before** any filesystem access, so a path-injection attempt or a
    wrong-format id is a ``ValueError`` raised before dispatch; an unknown
    or ``adr`` ``type`` is likewise an explicit ``ValueError`` before
    dispatch (REQ-004, D4 -- the generic ``validate`` tool's precedent, a
    deliberate divergence from ``update``'s inherited ``KeyError``); the
    identical-input and empty-``old_str`` guards (the OC messages verbatim,
    plain ``ValueError``s with no wrap prefix, REQ-008) fire after them and
    still before any filesystem access. Each adapter additionally confines
    the resolved path to the domain's own base directory with
    ``_path_safety.assert_within`` inside the lock -- defense-in-depth
    against any future gap in the id validation.

    OC's read-before-edit enforcement is a client session-state convention
    (no server-side counterpart is replicated): read the current body via
    the corresponding ``get_<d>(id, raw=True)`` before calling this tool.
    The YAML frontmatter is never addressable (body only); use the generic
    ``update`` tool for a whole-body or line-range replacement instead.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    type:
        The document type / domain: one of ``req``, ``uc``, ``tsk``,
        ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``, ``feat``,
        ``vcr``, ``sysrs``.
    old_str:
        The exact text to find in the current frontmatter-stripped on-disk
        body (byte-exact, including whitespace, indentation, and line
        endings); never empty (the empty-``old_str`` guard) and never
        identical to ``new_str`` (the identical-input guard).
    new_str:
        The replacement text; the empty string is a pure deletion (legal
        iff the edited body still validates as a whole document).
    replace_all:
        ``False`` (default): ``old_str`` must match exactly once (multiple
        matches are an error). ``True``: every exact occurrence is
        rewritten.

    Returns
    -------
    ReqFrontmatter | UcFrontmatter | TskFrontmatter | QaFrontmatter | PrbFrontmatter |
    GolFrontmatter | RskFrontmatter | DecFrontmatter | FeatFrontmatter | SopFrontmatter |
    VcrFrontmatter | SysrsFrontmatter
        The updated document's frontmatter only (no body) of the dispatched domain type
        (``updated`` bumped); use the corresponding ``get_<d>`` tool to fetch the full
        document afterward.

    Raises
    ------
    ValueError
        ``id`` is a path-injection attempt or not in the dispatched
        domain's own format (raised before any filesystem access);
        ``type`` is not one of the supported domains, including
        ``"adr"`` (raised before dispatch, REQ-004); ``old_str`` is
        identical to ``new_str`` or empty (raised before any filesystem
        access); or the stage-1 match fails -- ``old_str`` not found, or
        multiple matches without ``replace_all`` (raised under the domain
        lock after the on-disk body is read). All four guard/stage-1
        ``ValueError``s carry the OC message verbatim with no
        ``domain tool (channel)`` wrap prefix (REQ-002/REQ-008). Nothing
        is written in any of these cases.
    AssertionError
        The edited body is structurally invalid (stage 2) -- e.g. deleting
        the H1. The message is prefixed with domain/tool/channel context
        (e.g. ``"req edit (body): ..."``) by the shared tool-boundary
        wrapper (:func:`~biz.dfch.specmgr.models.md._errors.
        wrap_tool_errors`), layered on top of the engine's own
        field-path/line/snippet enrichment (feat-27-validation Phases
        1/2). Nothing is written.
    pydantic.ValidationError
        A field/cross-field validation failure in the edited body (stage
        2, e.g. an edit producing an out-of-vocabulary value) -- similarly
        prefixed. Nothing is written.
    ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError /
    PrbNotFoundError / GolNotFoundError / RskNotFoundError / DecNotFoundError /
    FeatNotFoundError / SopNotFoundError / VcrNotFoundError / SysrsNotFoundError
        No document of the dispatched ``type`` has this id -- the
        domain's own not-found error, unchanged from the per-domain tools.
    """
    # REQ-005: validate before any filesystem access (injection prevention).
    validate_id(type, id)
    # REQ-004: explicit type check before dispatch (the `validate` tool's precedent; a deliberate
    # divergence from `update`'s inherited `KeyError` for `type="adr"`, D4).
    if type not in _ADAPTERS:
        raise ValueError(
            f"unknown document type {type!r}; expected one of {', '.join(WHOLE_BODY_DOMAINS)} ('adr' is not supported)"
        )
    # REQ-008: the identical-input and empty-`old_str` guards fire before any filesystem access.
    if old_str == new_str:
        raise ValueError("No changes to apply: oldString and newString are identical.")
    if old_str == "":
        raise ValueError(
            "oldString cannot be empty when editing an existing file. "
            "Provide the exact text to replace, "
            "or use update for an intentional full-file replacement."
        )

    adapter = _ADAPTERS[type]
    result = adapter(id, old_str, new_str, replace_all)
    return result
