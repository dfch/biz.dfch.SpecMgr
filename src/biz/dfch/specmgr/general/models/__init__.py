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

"""Shared, cross-domain Pydantic models with no document-type-specific content.

Backs feat-13's ``<domain>_list`` -> ``list_<domain>`` pagination rollout
(``.specmgr/feat/feat-13-list-paging/README.md`` Task 1.1/Task 1.3):

- :class:`PagedResult` -- a generic ``{total, offset, max_results, truncated,
  results}`` page wrapper, shared by every domain's ``list_<domain>`` tool.
- :class:`DocSummary` -- the common ``id``/``title``/``status``/``ref`` field
  set that every domain's own ``*Summary`` model (``ReqSummary``,
  ``UcSummary``, ``TskSummary``, ``QaSummary``) subclasses.

Also backs feat-92-resources's cross-cutting reference-resource
model-backed drift-guard convention (ADR
356d8781-e446-4c26-917a-eda85648ce9d, REQ-002):

- :func:`parse_dtais`/:class:`Dtais` -- parses the DTAIS verification-
  methods guidance document (``general/data/general_dtais.md``) backing
  ``specmgr://dtais``, purely to fail fast on structural drift (the parsed
  result is discarded by the resource itself).

Import this package to use either model directly::

    from biz.dfch.specmgr.general.models import DocSummary, PagedResult
"""

from .dtais import (
    CoverageItem,
    CoverageRelationship,
    Dtais,
    MethodItem,
    WhenToApply,
    WhenToApplyItem,
    parse_dtais,
)
from .paged_result import PagedResult
from .summary import DocSummary

__all__ = [
    "CoverageItem",
    "CoverageRelationship",
    "Dtais",
    "DocSummary",
    "MethodItem",
    "PagedResult",
    "WhenToApply",
    "WhenToApplyItem",
    "parse_dtais",
]
