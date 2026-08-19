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

"""MCP resource registrations for Task List (TSK) documents (Tasks 3.10-3.11).

``tsk_schema`` registers the persisted-JSON-Schema resource
(``specmgr://tsk/schema``). ``tsk_example`` registers the packaged sample
task list document resource (``specmgr://tsk/example``). ``tsk_template``
registers the packaged task list template resource (``specmgr://tsk/template``)
-- every field present, populated with short placeholder ("blind text")
content rather than a valid document instance. Import this package to
register all task list resources against the shared ``mcp`` application
instance::

    from biz.dfch.specmgr.tsk import resources  # noqa: F401 (side-effects only)

Like REQ, TSK has no by-id single-document *resource* -- id-based reads go
through the ``get_tsk`` tool only (``tsk.tools.get_tsk``); there never was a
``specmgr://tsk/{id}`` resource to remove in the first place. The former
listing resource (``tsk_list``, ``specmgr://tsk/list``) was replaced the
same way by the ``list_tsk`` ``@mcp.tool()`` (``tsk.tools.list_tsk``), so
that paging parameters (``max_results``/``offset``) could be accepted --
see ``.specmgr/feat/feat-13-list-paging/README.md``.
"""

from . import tsk_example, tsk_schema, tsk_template  # noqa: F401

__all__ = [
    "tsk_example",
    "tsk_schema",
    "tsk_template",
]
