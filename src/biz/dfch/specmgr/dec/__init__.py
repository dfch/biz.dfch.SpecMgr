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

"""Decision (DEC) domain -- decisions in general (not architecture-only).

This is a domain-first package, mirroring ``gol``'s layout (per ADR
ece4554b-725c-4f76-bc04-5d2b760363d2), containing models, tools, prompts,
and resources for managing ``dec`` documents. A DEC keeps the ADR's general
structure (MADR-style headings, ``Options`` collection) but is built on the
generic ``models/md`` parser with the simple surface used by GOL/RSK/QA --
no fine-grained mutation tools, no by-id resource.

Import this package to register all decision tools/prompts/
resources against the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import dec  # noqa: F401 (side-effects only)

``tools`` (``create_dec``, ``parse_dec``,
``list_dec``, ``get_dec``, ``get_dec_example``, ``get_dec_template``,
``validate_dec``), ``resources`` (``specmgr://dec/schema``,
``specmgr://dec/example``, ``specmgr://dec/template``), and ``prompts``
(``create_dec``, ``update_dec``) all exist; whole-body and line-range
updates of an existing document go through the generic ``update`` tool in
``general.tools`` (``type="dec"``), and status changes go through the
generic ``set_status`` tool in ``general.tools`` (``type="dec"``). Like
GOL, DEC has no
``specmgr://dec/{id}`` resource -- id-based reads go through the ``get_dec``
tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). Likewise, there is no
``specmgr://dec/list`` resource -- ``list_dec`` ships as a paged
``@mcp.tool()`` from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
"""

from . import prompts, resources, tools  # noqa: F401

__all__ = [
    "prompts",
    "resources",
    "tools",
]
