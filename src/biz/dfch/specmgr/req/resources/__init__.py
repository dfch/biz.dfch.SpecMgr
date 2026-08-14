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

"""MCP resource registrations for Requirement (REQ) documents (Tasks 3.5-3.7, 3.17-3.18).

``req_schema`` registers the persisted-JSON-Schema resource
(``specmgr://req/schema``). ``req_example`` registers the packaged sample
requirement document resource (``specmgr://req/example``). ``req_template``
registers the packaged requirement template resource (``specmgr://req/template``)
-- every field present, populated with short placeholder ("blind text")
content rather than a valid document instance. This sub-package also holds
the ``data/`` directory of packaged, build-guaranteed example/template
markdown files (declared package data, not Python modules). ``req_get``
registers the by-id single-document resource (``specmgr://req/{id}``, Task
3.17) and ``req_list`` registers the listing resource (``specmgr://req/list``,
Task 3.18), both mirroring ``adr.resources.adr_get``/``adr_list``. Import
this package to register all requirement resources against the shared
``mcp`` application instance::

    from biz.dfch.specmgr.req import resources  # noqa: F401 (side-effects only)
"""

from . import req_example, req_get, req_list, req_schema, req_template  # noqa: F401

__all__ = [
    "req_example",
    "req_get",
    "req_list",
    "req_schema",
    "req_template",
]
