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

"""MCP resource registrations for Requirement (REQ) documents (Task 3.5).

``req_schema`` registers the persisted-JSON-Schema resource
(``specmgr://req/schema``). Import this package to register it against
the shared ``mcp`` application instance::

    from biz.dfch.specmgr.req import resources  # noqa: F401 (side-effects only)
"""

from . import req_schema  # noqa: F401

__all__ = [
    "req_schema",
]
