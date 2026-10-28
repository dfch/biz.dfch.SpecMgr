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

"""MCP resource registrations for free-form text (TXT) documents (feat-229-txt Phase 120).

``txt_example`` registers the packaged sample
free-form text document resource (``specmgr://txt/example``).
``txt_template`` registers the packaged free-form text template
resource (``specmgr://txt/template``) -- every field present, populated
with short placeholder ("blind text") content that still round-trips
through ``parse_txt`` (the DEC/RSK precedent). Import this package to
register all free-form text resources against the shared ``mcp``
application instance::

    from biz.dfch.specmgr.txt import resources  # noqa: F401 (side-effects only)

Like VCR/SYSRS, TXT has no by-id single-document *resource* -- id-based
reads go through the ``get_txt`` tool only (``txt.tools.get_txt``), and
no ``specmgr://txt/list`` resource either -- listing goes through the
``list_txt`` ``@mcp.tool()`` (``txt.tools.list_txt``) from the start, per
ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, so that paging parameters
(``max_results``/``offset``) could be accepted.
TXT ships the generated JSON Schema as the ``get_txt_schema`` ``@mcp.tool()``
(``txt.tools.get_txt_schema``) from day one, per ADR
112b6498-078b-4a59-88b8-8ffb7a5041b3 (feat-189 Phase 105) -- there is no
``specmgr://txt/schema`` resource in its history.
"""

from . import txt_example, txt_template  # noqa: F401

__all__ = [
    "txt_example",
    "txt_template",
]
