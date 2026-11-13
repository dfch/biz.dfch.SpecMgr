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

"""MCP resource registrations for set (set) documents (feat-173-req-iso29148-level-set Phase 180).

``set_example`` registers the packaged sample
set document resource (``specmgr://set/example``).
``set_template`` registers the packaged set template
resource (``specmgr://set/template``) -- every field present, populated
with short placeholder ("blind text") content that still round-trips
through ``parse_set`` (the DEC/RSK precedent). Import this package to
register all set resources against the shared ``mcp``
application instance::

    from biz.dfch.specmgr.set import resources  # noqa: F401 (side-effects only)

Like VCR/SYSRS, SET has no by-id single-document *resource* -- id-based
reads go through the ``get_set`` tool only (``set.tools.get_set``), and
no ``specmgr://set/list`` resource either -- listing goes through the
``list_set`` ``@mcp.tool()`` (``set.tools.list_set``) from the start, per
DEC ec9f5262-9912-49d0-903f-fcfb54f28c13, so that paging parameters
(``max_results``/``offset``) could be accepted.
set ships the generated JSON Schema as the ``get_set_schema`` ``@mcp.tool()``
(``set.tools.get_set_schema``) from day one, per DEC
112b6498-078b-4a59-88b8-8ffb7a5041b3 (feat-189 Phase 105) -- there is no
``specmgr://set/schema`` resource in its history.
"""

from . import set_example, set_template  # noqa: F401

__all__ = [
    "set_example",
    "set_template",
]
