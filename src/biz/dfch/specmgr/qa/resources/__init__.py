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

"""MCP resource registrations for Question and Answer (QA) documents (Phase 4, Task 4.2).

``qa_schema`` registers the persisted-JSON-Schema resource
(``specmgr://qa/schema``). ``qa_example`` registers the packaged sample QA
document resource (``specmgr://qa/example``). ``qa_template`` registers the
packaged QA template resource (``specmgr://qa/template``) -- every field
present, populated with short placeholder ("blind text") content rather
than a valid document instance. Import this package to register all QA
resources against the shared ``mcp`` application instance::

    from biz.dfch.specmgr.qa import resources  # noqa: F401 (side-effects only)

Like REQ, QA has no by-id single-document *resource* -- id-based reads go
through the ``get_qa`` tool only; see ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614 ("Expose id-based REQ document reads as
a tool (get_req), not a resource"). The former listing resource (``qa_list``,
``specmgr://qa/list``) was replaced the same way by the ``list_qa``
``@mcp.tool()`` (``qa.tools.list_qa``), so that paging parameters
(``max_results``/``offset``) could be accepted -- see
``.specmgr/feat/feat-13-list-paging/README.md``.
"""

from . import qa_example, qa_schema, qa_template  # noqa: F401

__all__ = [
    "qa_example",
    "qa_schema",
    "qa_template",
]
