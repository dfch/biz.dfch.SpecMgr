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

"""MCP tool wrappers for Architecture Decision Records (plan §6, §8, §10 item 4).

Thin file-I/O/id-lookup adapters over ``models/adr/v1/mutations.py`` plus
``parse_adr``/``render_adr``, exposed as ``@mcp.tool()``-decorated functions
against the shared ``mcp`` application instance -- one module per tool.
Import this package to register all ADR tools at once::

    from biz.dfch.specmgr.adr import tools  # noqa: F401 (side-effects only)
"""

from .create_adr import create_adr
from .get_adr import get_adr
from .list_adr import list_adr
from .option_create import option_create
from .option_delete import option_delete
from .option_list import option_list
from .option_read import option_read
from .option_update import option_update
from .set_status import set_status
from .update_frontmatter import update_frontmatter
from .update_section import update_section
from .validate_adr import validate_adr

__all__ = [
    "create_adr",
    "get_adr",
    "list_adr",
    "option_create",
    "option_delete",
    "option_list",
    "option_read",
    "option_update",
    "set_status",
    "update_frontmatter",
    "update_section",
    "validate_adr",
]
