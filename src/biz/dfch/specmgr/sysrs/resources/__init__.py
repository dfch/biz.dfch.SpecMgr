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

"""MCP resource registrations for System Requirements Specification (SYSRS) documents (Task 4.5).

``sysrs_schema`` registers the persisted-JSON-Schema resource
(``specmgr://sysrs/schema``). ``sysrs_example`` registers the packaged sample
SYSRS document resource (``specmgr://sysrs/example``). ``sysrs_template``
registers the packaged SYSRS template resource (``specmgr://sysrs/template``)
-- every section present, populated with short placeholder ("blind text")
content that still round-trips through ``parse_sysrs`` (the SOP/VCR
precedent). Import this package to register all SYSRS resources against the
shared ``mcp`` application instance::

    from biz.dfch.specmgr.sysrs import resources  # noqa: F401 (side-effects only)

Like SOP/DEC/VCR, SYSRS has exactly three resources and no by-id single-document
*resource* -- id-based reads go through the ``get_sysrs`` tool only
(``sysrs.tools.get_sysrs``), and no ``specmgr://sysrs/list`` resource either --
listing goes through the ``list_sysrs`` ``@mcp.tool()``
(``sysrs.tools.list_sysrs``) from the start, per ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13, so that paging parameters
(``max_results``/``offset``) could be accepted.

Unlike SOP (gained ``specmgr://rasci``) and VCR (gained ``specmgr://dtais``),
SYSRS introduces **no** new cross-cutting ``general`` resource of its own:
the nine canonical ISO/IEC 25010:2023 characteristic names its
``create_sysrs`` prompt needs come from the existing
``specmgr://iso25010`` resource (``general.resources.iso25010``).
"""

from . import sysrs_example, sysrs_schema, sysrs_template  # noqa: F401

__all__ = [
    "sysrs_example",
    "sysrs_schema",
    "sysrs_template",
]
