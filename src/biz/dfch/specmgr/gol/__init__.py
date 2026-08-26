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

"""Goal (GOL) domain -- high-level business goal specifications.

This is a domain-first package, mirroring ``prb``/``req``'s layout (per ADR
ece4554b-725c-4f76-bc04-5d2b760363d2), containing models, tools, prompts,
and resources for managing ``gol`` documents.

Import this package to register all goal tools/prompts/
resources against the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import gol  # noqa: F401 (side-effects only)

``tools`` (``parse_gol``, ``get_gol``, ``list_gol``, ``get_gol_example``,
``get_gol_template``, ``create_gol``, ``update_gol``, ``set_status_gol``,
``delete_gol``, ``validate_gol``), ``resources`` (``specmgr://gol/schema``,
``specmgr://gol/example``, ``specmgr://gol/template``), and ``prompts``
(``create_gol``, ``update_gol``) all exist. Like REQ/PRB/TSK/QA, GOL has no
``specmgr://gol/{id}`` resource -- id-based reads go through the ``get_gol``
tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). Likewise, there is no
``specmgr://gol/list`` resource -- ``list_gol`` ships as a paged
``@mcp.tool()`` from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13),
unlike REQ/UC/TSK/QA/PRB's own resource-then-converted history.
"""

from . import prompts, resources, tools  # noqa: F401

__all__ = [
    "prompts",
    "resources",
    "tools",
]
