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

"""One ranked hit row of the two similarity tools (feat-134, Phase 3, ACC-001/ACC-002).

The return shape both ``find_related`` and ``find_similar_text`` (Phase 3,
Task 3.1/3.2, ``general.tools``) build: a ``list`` of one
:class:`SimilarityHit` per ranked candidate, sorted by ``score`` descending.
The six fields are the plan's own hit shape ``(type, id, title, status,
path, score)`` (ACC-001/ACC-002; the 2026-09-18 plan refinement dropped the
earlier draft's redundant ``ref`` field and added ``status``).

A candidate document that fails to parse still produces a hit row
(REQ-009, ADR 750842b2-aca4-4649-ba0c-855ec8e1f505's **embedding input**
sub-decision): its ``id`` is ``None`` (the marker rows are not
addressable) and its ``title``/``status`` are the fixed
``"<failed to parse>"`` marker (``general.tools._listing.
FAILED_TO_PARSE_MARKER``, reused, not redefined) -- broken artifacts stay
discoverable instead of vanishing from similarity results. Its ``path`` is
still the real on-disk file, so a caller can open it to see what broke.

Standalone (no ``DocSummary`` base): the hit shape carries ``type`` (the
row is cross-domain, unlike a domain's own ``list_<d>`` summary) and
``score`` (the ranking result), and deliberately drops ``DocSummary``'s
``ref``/``error`` fields (the plan refinement's own hit shape) -- so this
is a sibling of :class:`~biz.dfch.specmgr.general.models.summary.DocSummary`
rather than a subclass.
"""

from __future__ import annotations

from pydantic import BaseModel

__all__ = ["SimilarityHit"]


class SimilarityHit(BaseModel):
    """One ranked similarity hit: a candidate document plus its score (ACC-001/ACC-002).

    Parameters
    ----------
    type:
        The hit's domain name: one of the whole-body domains
        (``req``, ``uc``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``,
        ``dec``, ``sop``, ``feat``, ``vcr``, ``sysrs``) -- ``adr`` is
        structurally excluded from the candidate set (issue #46, ADR
        750842b2's **corpus and registry** sub-decision).
    id:
        The hit document's specmgr-assigned id (the validated frontmatter
        value, the domain's own defaults applied for a blank key --
        exactly what ``list_<domain>`` surfaces), or ``None`` when the
        candidate file failed to parse (REQ-009: the marker rows are not
        addressable).
    title:
        The hit document's first H1 title, or the fixed marker
        ``"<failed to parse>"`` for an unparseable candidate.
    status:
        The hit document's validated ``frontmatter.status`` value, or the
        fixed marker ``"<failed to parse>"`` for an unparseable candidate.
    path:
        The real, absolute (``.resolve()``d) filesystem path to the hit
        document's on-disk file, for a caller that wants to read it
        directly instead of going through the matching ``get_<domain>``
        tool (which it cannot do for an unparseable candidate -- its
        ``id`` is ``None``).
    score:
        The cosine similarity of the hit document's embedding against the
        query (dot product on L2-normalized vectors, in [-1, 1]); the
        result list is sorted by ``score`` descending, ties in the
        candidate enumeration's own deterministic order.
    """

    type: str
    id: str | None
    title: str
    status: str
    path: str
    score: float
