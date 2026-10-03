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

"""The generic ``update`` tool's own success return shape (feat-153-off-by-n Phase 2,
REQ-002/REQ-003, ADR 19ff316b-cd11-41a7-a616-ffd84917da51, "Revise the generic
update tool's success return to frontmatter plus an optional before/after snippet").

Revises feature feat-69-update-context's "frontmatter-only" return precedent
for ``update`` alone: every successful ``update`` call across every whole-body
domain now returns this wrapper -- the same per-domain frontmatter object
feat-69 returned, plus a bounded before/after ``snippet`` of the touched
range in range mode (``None`` in whole-body mode and for the
whole-body-equivalent ``offset=1`` + omitted-``limit`` range).
``create_<d>``/``set_status``/``set_classification`` keep feat-69's bare-
frontmatter return, and ``delete``/``edit``/the ADR tools are unchanged --
the revision is scoped to ``update`` specifically (ADR 19ff316b's
Decision Outcome item 5).

Like :class:`~biz.dfch.specmgr.general.models.parse_failure_result.
ParseFailureResult`, this model is a distinct, purpose-built structured
tool result (not a reuse of any domain's own ``*Frontmatter`` class): the
``frontmatter`` field is typed with the whole-body domains' frontmatter
union -- re-exported as :data:`UpdateFrontmatter` so the generic ``update``
tool's own dispatch module annotates its internal adapter outcome against
this single source instead of keeping a second, drifting copy of the union.

Import caveat (why ``general.models.__init__`` exports this module's names
lazily via PEP 562): this module imports every whole-body domain's own models
package, so importing it eagerly from that ``__init__`` would re-enter
partially-initialized domain ``__init__`` files (e.g. ``feat.models.v1.body``
imports ``tsk``'s models, whose package ``__init__`` pulls in the server's
full domain-import list).
"""

from __future__ import annotations

from pydantic import BaseModel

from ...dec.models.v1 import DecFrontmatter
from ...feat.models.v1 import FeatFrontmatter
from ...gol.models.v1 import GolFrontmatter
from ...prb.models.v1 import PrbFrontmatter
from ...qa.models.v2 import QaFrontmatter
from ...req.models.v1 import ReqFrontmatter
from ...rsk.models.v1 import RskFrontmatter
from ...sop.models.v1 import SopFrontmatter
from ...sysrs.models.v1 import SysrsFrontmatter
from ...tsk.models.v1 import TskFrontmatter
from ...uc.models.v2 import UcFrontmatter
from ...vcr.models.v1 import VcrFrontmatter

__all__ = ["UpdateFrontmatter", "UpdateResult"]

#: The whole-body domains' frontmatter types (req/uc/tsk/qa/prb/gol/rsk/dec/
#: sop/feat/vcr/sysrs), unioned: the type of :class:`UpdateResult`'s
#: ``frontmatter`` field (single source -- the generic ``update`` tool's
#: dispatch module imports this alias instead of re-listing the frontmatter
#: classes; add a new domain's frontmatter here and in the tool's dispatch
#: table together).
UpdateFrontmatter = (
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


class UpdateResult(BaseModel):
    """The generic ``update`` tool's success return: the updated frontmatter plus an optional snippet.

    ``frontmatter`` is the same per-domain frontmatter object feature
    feat-69-update-context's "frontmatter-only" precedent returned -- the
    document's carried-over frontmatter with only ``updated`` bumped -- so a
    caller that previously read frontmatter fields directly off the result now
    reads them off ``result.frontmatter`` (the ADR's documented breaking
    change). ``snippet`` is the before/after window of the touched range, in
    range mode only: up to 2 unchanged context lines immediately above the
    touched range, the dropped lines (labeled with their **pre-splice** 1-based
    body-line numbers), the inserted lines (labeled with their **post-splice**
    numbers), and up to 2 unchanged context lines immediately below, each line
    formatted ``<marker> <n>: <line text>`` (marker ``-``/``+``/single space;
    plain decimal number; the ``": "`` separator; verbatim line text -- an
    empty body line renders with a trailing space after the separator); the
    snippet text is its lines joined with ``"\\n"`` plus a single trailing
    ``"\\n"``, or ``""`` when it contains no lines at all. ``snippet`` is
    ``None`` in exactly two cases: whole-body mode (no ``offset``) and the
    whole-body-equivalent range (``offset=1`` with omitted ``limit``) -- never
    in any other range-mode call. The dropped/inserted numbering sequences are
    independent and need not be contiguous when the replacement changes the
    line count (the expected pre-splice/post-splice split, not a defect); the
    snippet is bounded by the touched range, not the document size (no hard
    cap).

    Parameters
    ----------
    frontmatter:
        The updated document's frontmatter only (no body) of the dispatched
        domain type.
    snippet:
        The before/after window of the touched range (see the class docstring),
        or ``None`` in whole-body mode and for the whole-body-equivalent
        ``offset=1`` + omitted-``limit`` range.
    """

    frontmatter: UpdateFrontmatter
    snippet: str | None
