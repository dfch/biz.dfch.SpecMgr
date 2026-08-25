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

"""MCP resource registrations for Risk (RSK) documents (Tasks 3.10-3.11, 3.15).

``rsk_schema`` registers the persisted-JSON-Schema resource
(``specmgr://rsk/schema``). ``rsk_example`` registers the packaged sample
risk document resource (``specmgr://rsk/example``). ``rsk_template``
registers the packaged risk template resource (``specmgr://rsk/template``)
-- every field present, populated with short placeholder ("blind text")
content. ``rsk_tara`` registers the static TARA domain-knowledge resource
(``specmgr://rsk/tara``) and ``rsk_risk_matrix`` the static 5x5 risk-matrix
domain-knowledge resource (``specmgr://rsk/risk-matrix``) -- both raw
packaged markdown, the audience being an LLM agent reading guidance rather
than code consuming data. Import this package to register all risk
resources against the shared ``mcp`` application instance::

    from biz.dfch.specmgr.rsk import resources  # noqa: F401 (side-effects only)

Like REQ/TSK, RSK has no by-id single-document *resource* -- id-based reads
go through the ``get_rsk`` tool only (``rsk.tools.get_rsk``); there never
was a ``specmgr://rsk/{id}`` resource to remove in the first place (same
rationale as ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). There is no
``specmgr://rsk/list`` resource either -- listing is the paged ``list_rsk``
tool (``rsk.tools.list_rsk``), so that paging parameters
(``max_results``/``offset``) can be accepted (feat-13-list-paging, ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13).
"""

from . import rsk_example, rsk_schema, rsk_template, risk_matrix, tara  # noqa: F401

__all__ = [
    "rsk_example",
    "risk_matrix",
    "rsk_schema",
    "rsk_template",
    "tara",
]
