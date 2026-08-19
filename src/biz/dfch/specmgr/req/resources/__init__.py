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

"""MCP resource registrations for Requirement (REQ) documents (Tasks 3.5-3.7, 3.18).

``req_schema`` registers the persisted-JSON-Schema resource
(``specmgr://req/schema``). ``req_example`` registers the packaged sample
requirement document resource (``specmgr://req/example``). ``req_template``
registers the packaged requirement template resource (``specmgr://req/template``)
-- every field present, populated with short placeholder ("blind text")
content rather than a valid document instance. Import this package to
register all requirement resources against the shared ``mcp`` application
instance::

    from biz.dfch.specmgr.req import resources  # noqa: F401 (side-effects only)

Unlike ADR, REQ has no by-id single-document *resource* --
``specmgr://req/{id}`` (``req_get``, Task 3.17) was removed in favor of the
``get_req`` tool (``req.tools.get_req``); see ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614 ("Expose id-based REQ document reads as
a tool (get_req), not a resource"). The former listing resource
(``req_list``, ``specmgr://req/list``, Task 3.18) was replaced the same way
by the ``list_req`` ``@mcp.tool()`` (``req.tools.list_req``), so that paging
parameters (``max_results``/``offset``) could be accepted -- see
``.specmgr/feat/feat-13-list-paging/README.md``.
"""

from . import req_example, req_schema, req_template  # noqa: F401

__all__ = [
    "req_example",
    "req_schema",
    "req_template",
]
