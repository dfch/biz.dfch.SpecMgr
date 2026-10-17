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

"""MCP resource registrations for Standard Operating Procedure (SOP) documents (feat-30 Task 3.7).

``sop_example`` registers the packaged sample
SOP document resource (``specmgr://sop/example``). ``sop_template``
registers the packaged SOP template resource (``specmgr://sop/template``)
-- every section present, populated with short placeholder ("blind text")
content that still round-trips through ``parse_sop`` (the RSK/DEC
precedent). Import this package to register all SOP resources against the
shared ``mcp`` application instance::

    from biz.dfch.specmgr.sop import resources  # noqa: F401 (side-effects only)

Like DEC/GOL, SOP has exactly two resources and no by-id single-document
*resource* -- id-based reads go through the ``get_sop`` tool only
(``sop.tools.get_sop``), and no ``specmgr://sop/list`` resource either --
listing goes through the ``list_sop`` ``@mcp.tool()``
(``sop.tools.list_sop``) from the start, per ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13, so that paging parameters
(``max_results``/``offset``) could be accepted.
The former schema resource (``sop_schema``, ``specmgr://sop/schema``) was
converted the same way into the ``get_sop_schema`` ``@mcp.tool()``
(``sop.tools.get_sop_schema``), so that the generated JSON Schema is
discoverable from the always-in-context tool surface instead of the
resource layer -- see ADR 112b6498-078b-4a59-88b8-8ffb7a5041b3
(feat-189 Phase 105).

The generic RASCI role-definitions guidance is **not** a third ``sop``
resource: ``specmgr://rasci`` lives under ``general/resources/`` instead,
since RASCI is a well-known external framework not coupled to any one
domain's schema (REQ-011). ``sop`` reaches it via cross-references in the
six RASCI-family class docstrings, the ``create_sop``/``update_sop``
packaged instructions, ``sop/__init__.py``'s module docstring, and
``server.py``'s module docstring -- see ``general.resources.rasci``.
"""

from . import sop_example, sop_template  # noqa: F401

__all__ = [
    "sop_example",
    "sop_template",
]
