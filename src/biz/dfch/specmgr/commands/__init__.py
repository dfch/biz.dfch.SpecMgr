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

"""commands module.

Each CLI command lives in its own module, exposing a plain function that
``cli.py`` registers on the Typer ``app`` via ``app.command()(fn)``.
"""

from .adr_toc import adr_toc
from .coverage_badge import coverage_badge
from .docs import docs
from .mcp import mcp
from .mcp_docs import mcp_docs
from .req_parse import req_parse
from .schema import schema
from .unused_code import unused_code
from .version import version

__all__ = [
    "adr_toc",
    "coverage_badge",
    "docs",
    "mcp",
    "mcp_docs",
    "req_parse",
    "schema",
    "unused_code",
    "version",
]
