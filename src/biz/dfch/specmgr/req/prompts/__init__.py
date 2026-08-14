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

"""MCP prompt wrappers for Requirements (Task 3.19).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``req/tools/``/``req/resources/`` surface in the right order --
one module per prompt, mirroring ``adr/prompts/``'s own one-module-per-
prompt split. Import this package to register all REQ prompts at once::

    from biz.dfch.specmgr.req import prompts  # noqa: F401 (side-effects only)
"""

from .create_req import create_req
from .update_req import update_req

__all__ = [
    "create_req",
    "update_req",
]
