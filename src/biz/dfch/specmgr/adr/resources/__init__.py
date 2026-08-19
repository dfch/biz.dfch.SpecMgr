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

"""MCP resource registrations for Architecture Decision Records (plan §8, §9a).

``adr_get`` registers the by-id template resource (``specmgr://adr/{id}``).
The former ADR listing resource (``adr_list``, ``specmgr://adr/list``) was
replaced by the ``list_adr`` ``@mcp.tool()`` (``adr.tools.list_adr``), so
that paging parameters (``max_results``/``offset``) could be accepted --
see ``.specmgr/feat/feat-13-list-paging/README.md``. Import this package to
register the remaining ADR resource::

    from biz.dfch.specmgr.adr import resources  # noqa: F401 (side-effects only)
"""

from . import adr_get  # noqa: F401

__all__ = [
    "adr_get",
]
