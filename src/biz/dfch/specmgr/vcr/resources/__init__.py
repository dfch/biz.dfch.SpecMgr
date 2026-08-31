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

"""MCP resource registrations for Verification Case Record (VCR) documents (Task 3.1).

``vcr_schema`` registers the persisted-JSON-Schema resource
(``specmgr://vcr/schema``). ``vcr_example`` registers the packaged sample
verification case record document resource (``specmgr://vcr/example``).
``vcr_template`` registers the packaged verification case record template
resource (``specmgr://vcr/template``) -- every section present, populated
with short placeholder ("blind text") content that still round-trips
through ``parse_vcr`` (the DEC/RSK precedent). Import this package to
register all verification case record resources against the shared ``mcp``
application instance::

    from biz.dfch.specmgr.vcr import resources  # noqa: F401 (side-effects only)

Like DEC/GOL, VCR has no by-id single-document *resource* -- id-based reads
go through the ``get_vcr`` tool only (``vcr.tools.get_vcr``), and no
``specmgr://vcr/list`` resource either -- listing goes through the
``list_vcr`` ``@mcp.tool()`` (``vcr.tools.list_vcr``) from the start, per
ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, so that paging parameters
(``max_results``/``offset``) could be accepted.
"""

from . import vcr_example, vcr_schema, vcr_template  # noqa: F401

__all__ = [
    "vcr_example",
    "vcr_schema",
    "vcr_template",
]
