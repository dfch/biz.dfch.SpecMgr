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

"""MCP prompt wrappers for Architecture Decision Records (doc/adr-tool-plan.md §11).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``tools/adr/`` tool surface in the right order -- one module per
prompt, mirroring ``tools/adr/``'s own one-tool-per-module split. Import
this package to register all ADR prompts at once::

    from biz.dfch.specmgr.prompts import adr  # noqa: F401 (side-effects only)
"""

from .create_adr import create_adr
from .create_adr_test import create_adr_test
from .update_adr import update_adr
from .update_adr_test import update_adr_test

__all__ = [
    "create_adr",
    "create_adr_test",
    "update_adr",
    "update_adr_test",
]
