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

"""``@mcp.tool()`` wrapper: set_classification (feat-56-classification, Phase 2).

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
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

import frontmatter

from ...dec.models.v1 import DecFrontmatter
from ...dec.tools._io import load_by_id as load_dec_by_id
from ...dec.tools._lock import dec_lock
from ...dec.tools._paths import dec_base_dir
from ...dec.tools._write import write_dec_file
from ...feat.models.v1 import FeatFrontmatter
from ...feat.tools._io import load_by_id as load_feat_by_id
from ...feat.tools._lock import feat_lock
from ...feat.tools._paths import feat_base_dir
from ...feat.tools._write import write_feat_file
from ...gol.models.v1 import GolFrontmatter
from ...gol.tools._io import load_by_id as load_gol_by_id
from ...gol.tools._lock import gol_lock
from ...gol.tools._paths import gol_base_dir
from ...gol.tools._write import write_gol_file
from ...models.md._errors import FRONTMATTER_CHANNEL, wrap_tool_errors
from ...prb.models.v1 import PrbFrontmatter
from ...prb.tools._io import load_by_id as load_prb_by_id
from ...prb.tools._lock import prb_lock
from ...prb.tools._paths import prb_base_dir
from ...prb.tools._write import write_prb_file
from ...qa.models.v2 import QaFrontmatter
from ...qa.tools._io import load_by_id as load_qa_by_id
from ...qa.tools._lock import qa_lock
from ...qa.tools._paths import qa_base_dir
from ...qa.tools._write import write_qa_file
from ...req.models.v1 import ReqFrontmatter
from ...req.tools._io import load_by_id as load_req_by_id
from ...req.tools._lock import req_lock
from ...req.tools._paths import req_base_dir
from ...req.tools._write import write_req_file
from ...rsk.models.v1 import RskFrontmatter
from ...rsk.tools._io import load_by_id as load_rsk_by_id
from ...rsk.tools._lock import rsk_lock
from ...rsk.tools._paths import rsk_base_dir
from ...rsk.tools._write import write_rsk_file
from ...server import mcp
from ...sop.models.v1 import SopFrontmatter
from ...sop.tools._io import load_by_id as load_sop_by_id
from ...sop.tools._lock import sop_lock
from ...sop.tools._paths import sop_base_dir
from ...sop.tools._write import write_sop_file
from ...sysrs.models.v1 import SysrsFrontmatter
from ...sysrs.tools._io import load_by_id as load_sysrs_by_id
from ...sysrs.tools._lock import sysrs_lock
from ...sysrs.tools._paths import sysrs_base_dir
from ...sysrs.tools._write import write_sysrs_file
from ...tsk.models.v1 import TskFrontmatter
from ...tsk.tools._io import load_by_id as load_tsk_by_id
from ...tsk.tools._lock import tsk_lock
from ...tsk.tools._paths import tsk_base_dir
from ...tsk.tools._write import write_tsk_file
from ...uc.models.v2 import UcFrontmatter
from ...uc.tools._io import load_by_id as load_uc_by_id
from ...uc.tools._lock import uc_lock
from ...uc.tools._paths import uc_base_dir
from ...uc.tools._write import write_uc_file
from ...vcr.models.v1 import VcrFrontmatter
from ...vcr.tools._io import load_by_id as load_vcr_by_id
from ...vcr.tools._lock import vcr_lock
from ...vcr.tools._paths import vcr_base_dir
from ...vcr.tools._write import write_vcr_file
from ._path_safety import assert_within, validate_id
from ._timestamps import now_timestamp

__all__ = ["set_classification"]

#: The generic tool's 12-way return union -- annotation-only (see module docstring).
_SetClassificationFrontmatter = (
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


def _set_classification_req(id_: str, classification: str) -> ReqFrontmatter:
    """Replace the classification of the requirement identified by ``id_``.

    Shaped exactly like :func:`~.set_status._set_status_req` (same
    ``req_lock``, ``load_by_id``, raw-body re-read via the established
    ``frontmatter.loads(...).content`` mechanism and verbatim
    re-persistence, frontmatter reconstructed through :class:`ReqFrontmatter`'s
    own constructor, ``write_req_file``, ``ReqNotFoundError``), replacing
    ``classification`` instead of ``status``.
    """
    base_dir = req_base_dir()
    with req_lock(id_):
        path, existing = load_req_by_id(base_dir, id_)
        assert_within(base_dir, path)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["classification"] = classification
        fm_data["updated"] = now
        with wrap_tool_errors(domain="req", tool="set_classification", channel=FRONTMATTER_CHANNEL):
            new_frontmatter = ReqFrontmatter(**fm_data)
        write_req_file(path, new_frontmatter, raw_body)
    return new_frontmatter


def _set_classification_uc(id_: str, classification: str) -> UcFrontmatter:
    """Replace the classification of the use case identified by ``id_``.

    See :func:`_set_classification_req` for the full semantics (same
    ``uc_lock``, ``load_by_id``, ``write_uc_file``, ``UcNotFoundError``).
    """
    base_dir = uc_base_dir()
    with uc_lock(id_):
        path, existing = load_uc_by_id(base_dir, id_)
        assert_within(base_dir, path)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["classification"] = classification
        fm_data["updated"] = now
        with wrap_tool_errors(domain="uc", tool="set_classification", channel=FRONTMATTER_CHANNEL):
            new_frontmatter = UcFrontmatter(**fm_data)
        write_uc_file(path, new_frontmatter, raw_body)
    return new_frontmatter


def _set_classification_tsk(id_: str, classification: str) -> TskFrontmatter:
    """Replace the classification of the task list identified by ``id_``.

    See :func:`_set_classification_req` for the full semantics (same
    ``tsk_lock``, ``load_by_id``, ``write_tsk_file``, ``TskNotFoundError``).
    """
    base_dir = tsk_base_dir()
    with tsk_lock(id_):
        path, existing = load_tsk_by_id(base_dir, id_)
        assert_within(base_dir, path)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["classification"] = classification
        fm_data["updated"] = now
        with wrap_tool_errors(domain="tsk", tool="set_classification", channel=FRONTMATTER_CHANNEL):
            new_frontmatter = TskFrontmatter(**fm_data)
        write_tsk_file(path, new_frontmatter, raw_body)
    return new_frontmatter


def _set_classification_qa(id_: str, classification: str) -> QaFrontmatter:
    """Replace the classification of the QA document identified by ``id_``.

    See :func:`_set_classification_req` for the full semantics (same
    ``qa_lock``, ``load_by_id``, ``write_qa_file``, ``QaNotFoundError``).
    """
    base_dir = qa_base_dir()
    with qa_lock(id_):
        path, existing = load_qa_by_id(base_dir, id_)
        assert_within(base_dir, path)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["classification"] = classification
        fm_data["updated"] = now
        with wrap_tool_errors(domain="qa", tool="set_classification", channel=FRONTMATTER_CHANNEL):
            new_frontmatter = QaFrontmatter(**fm_data)
        write_qa_file(path, new_frontmatter, raw_body)
    return new_frontmatter


def _set_classification_prb(id_: str, classification: str) -> PrbFrontmatter:
    """Replace the classification of the problem statement identified by ``id_``.

    See :func:`_set_classification_req` for the full semantics (same
    ``prb_lock``, ``load_by_id``, ``write_prb_file``, ``PrbNotFoundError``).
    """
    base_dir = prb_base_dir()
    with prb_lock(id_):
        path, existing = load_prb_by_id(base_dir, id_)
        assert_within(base_dir, path)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["classification"] = classification
        fm_data["updated"] = now
        with wrap_tool_errors(domain="prb", tool="set_classification", channel=FRONTMATTER_CHANNEL):
            new_frontmatter = PrbFrontmatter(**fm_data)
        write_prb_file(path, new_frontmatter, raw_body)
    return new_frontmatter


def _set_classification_gol(id_: str, classification: str) -> GolFrontmatter:
    """Replace the classification of the goal identified by ``id_``.

    See :func:`_set_classification_req` for the full semantics (same
    ``gol_lock``, ``load_by_id``, ``write_gol_file``, ``GolNotFoundError``).
    """
    base_dir = gol_base_dir()
    with gol_lock(id_):
        path, existing = load_gol_by_id(base_dir, id_)
        assert_within(base_dir, path)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["classification"] = classification
        fm_data["updated"] = now
        with wrap_tool_errors(domain="gol", tool="set_classification", channel=FRONTMATTER_CHANNEL):
            new_frontmatter = GolFrontmatter(**fm_data)
        write_gol_file(path, new_frontmatter, raw_body)
    return new_frontmatter


def _set_classification_rsk(id_: str, classification: str) -> RskFrontmatter:
    """Replace the classification of the risk identified by ``id_``.

    See :func:`_set_classification_req` for the full semantics (same
    ``rsk_lock``, ``load_by_id``, ``write_rsk_file``, ``RskNotFoundError``).
    """
    base_dir = rsk_base_dir()
    with rsk_lock(id_):
        path, existing = load_rsk_by_id(base_dir, id_)
        assert_within(base_dir, path)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["classification"] = classification
        fm_data["updated"] = now
        with wrap_tool_errors(domain="rsk", tool="set_classification", channel=FRONTMATTER_CHANNEL):
            new_frontmatter = RskFrontmatter(**fm_data)
        write_rsk_file(path, new_frontmatter, raw_body)
    return new_frontmatter


def _set_classification_dec(id_: str, classification: str) -> DecFrontmatter:
    """Replace the classification of the decision identified by ``id_``.

    See :func:`_set_classification_req` for the full semantics (same
    ``dec_lock``, ``load_by_id``, ``write_dec_file``, ``DecNotFoundError``).
    """
    base_dir = dec_base_dir()
    with dec_lock(id_):
        path, existing = load_dec_by_id(base_dir, id_)
        assert_within(base_dir, path)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["classification"] = classification
        fm_data["updated"] = now
        with wrap_tool_errors(domain="dec", tool="set_classification", channel=FRONTMATTER_CHANNEL):
            new_frontmatter = DecFrontmatter(**fm_data)
        write_dec_file(path, new_frontmatter, raw_body)
    return new_frontmatter


def _set_classification_feat(id_: str, classification: str) -> FeatFrontmatter:
    """Replace the classification of the feature identified by ``id_``.

    Mirrors :func:`_set_classification_dec`'s shape (same ``feat_lock``,
    ``load_by_id``, ``write_feat_file``, ``FeatNotFoundError``) -- see
    :func:`_set_classification_req` for the full semantics -- with the same
    feat-only divergence ``_update_feat``/``_set_status_feat`` document:
    ``id_`` resolves via ``feat.tools._paths``'s bespoke folder-per-document
    shortcut, not a flat-file directory scan. ``updated`` is bumped to the
    same shared date+time timestamp as every other domain.
    """
    base_dir = feat_base_dir()
    with feat_lock(id_):
        path, existing = load_feat_by_id(base_dir, id_)
        assert_within(base_dir, path)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["classification"] = classification
        fm_data["updated"] = now
        with wrap_tool_errors(domain="feat", tool="set_classification", channel=FRONTMATTER_CHANNEL):
            new_frontmatter = FeatFrontmatter(**fm_data)
        write_feat_file(path, new_frontmatter, raw_body)
    return new_frontmatter


def _set_classification_sop(id_: str, classification: str) -> SopFrontmatter:
    """Replace the classification of the SOP identified by ``id_``.

    Verbatim-shape port of :func:`_set_classification_dec` (same
    ``sop_lock``, ``load_by_id``, ``write_sop_file``, ``SopNotFoundError``;
    ``sop`` is the first domain built dispatch-only from day one per ADR
    36905d5b, so this adapter was written directly in this shape) -- see
    :func:`_set_classification_req` for the full semantics.
    """
    base_dir = sop_base_dir()
    with sop_lock(id_):
        path, existing = load_sop_by_id(base_dir, id_)
        assert_within(base_dir, path)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["classification"] = classification
        fm_data["updated"] = now
        with wrap_tool_errors(domain="sop", tool="set_classification", channel=FRONTMATTER_CHANNEL):
            new_frontmatter = SopFrontmatter(**fm_data)
        write_sop_file(path, new_frontmatter, raw_body)
    return new_frontmatter


def _set_classification_vcr(id_: str, classification: str) -> VcrFrontmatter:
    """Replace the classification of the verification case record identified by ``id_``.

    Mirrors :func:`_set_classification_dec`'s shape (same ``vcr_lock``,
    ``load_by_id``, ``write_vcr_file``, ``VcrNotFoundError``) -- see
    :func:`_set_classification_req` for the full semantics.
    """
    base_dir = vcr_base_dir()
    with vcr_lock(id_):
        path, existing = load_vcr_by_id(base_dir, id_)
        assert_within(base_dir, path)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["classification"] = classification
        fm_data["updated"] = now
        with wrap_tool_errors(domain="vcr", tool="set_classification", channel=FRONTMATTER_CHANNEL):
            new_frontmatter = VcrFrontmatter(**fm_data)
        write_vcr_file(path, new_frontmatter, raw_body)
    return new_frontmatter


def _set_classification_sysrs(id_: str, classification: str) -> SysrsFrontmatter:
    """Replace the classification of the System Requirements Specification identified by ``id_``.

    Mirrors :func:`_set_classification_sop`'s shape (same ``sysrs_lock``,
    ``load_by_id``, ``write_sysrs_file``, ``SysrsNotFoundError``; ``sysrs``
    is dispatch-only from day one per ADR 36905d5b, so this adapter was
    written directly in this shape) -- see :func:`_set_classification_req`
    for the full semantics.
    """
    base_dir = sysrs_base_dir()
    with sysrs_lock(id_):
        path, existing = load_sysrs_by_id(base_dir, id_)
        assert_within(base_dir, path)
        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

        now = now_timestamp()
        fm_data = existing.frontmatter.model_dump()
        fm_data["classification"] = classification
        fm_data["updated"] = now
        with wrap_tool_errors(domain="sysrs", tool="set_classification", channel=FRONTMATTER_CHANNEL):
            new_frontmatter = SysrsFrontmatter(**fm_data)
        write_sysrs_file(path, new_frontmatter, raw_body)
    return new_frontmatter


#: Dispatch table mapping the ``type`` value to its private adapter.
_ADAPTERS: dict[str, Callable[[str, str], _SetClassificationFrontmatter]] = {
    "req": _set_classification_req,
    "uc": _set_classification_uc,
    "tsk": _set_classification_tsk,
    "qa": _set_classification_qa,
    "prb": _set_classification_prb,
    "gol": _set_classification_gol,
    "rsk": _set_classification_rsk,
    "dec": _set_classification_dec,
    "feat": _set_classification_feat,
    "sop": _set_classification_sop,
    "vcr": _set_classification_vcr,
    "sysrs": _set_classification_sysrs,
}


@mcp.tool(
    name="set_classification",
    title="Set document classification",
    description=(
        "Replace the free-text `classification` frontmatter field of an existing document across "
        "the twelve whole-body domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, sop, "
        "feat, vcr; `adr` is not supported), also bumping `updated` and leaving the body and every "
        "other frontmatter field untouched. `classification` is fully free-text -- no closed "
        "vocabulary; a blank or whitespace-only value clears it back to `None`/absent. No `create_*` "
        "tool accepts a `classification` argument at all -- this is the sole classification-change "
        "entry point. An invalid `id` (path-injection attempt or wrong format for `type`) or an "
        "unsupported `type` is a `ValueError` raised before any file access. Returns the updated "
        "frontmatter only (no body); use the corresponding `get_<d>` tool to fetch the full "
        "document afterward."
    ),
)
def set_classification(
    id: str,
    type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "feat", "vcr", "sysrs"],
    classification: str,
) -> _SetClassificationFrontmatter:
    """Replace the ``classification`` frontmatter field of an existing document.

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
    (no ``/``, no ``\\``, no ``..``, plus the dispatched domain's own
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
    """
    # Mirrors set_status's/update's own REQ-009 guard: validate before any filesystem access
    # (injection prevention); an unsupported `type` also raises ValueError here, before dispatch.
    validate_id(type, id)

    adapter = _ADAPTERS[type]
    result = adapter(id, classification)
    return result
