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

"""MCP prompt wrappers for set (set) documents (feat-173-req-iso29148-level-set Phase 180).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``set/tools/``/``set/resources/`` surface in the right order --
one module per prompt, mirroring ``vcr/prompts/``'s own one-module-per-
prompt split. Import this package to register all set
prompts at once::

    from biz.dfch.specmgr.set import prompts  # noqa: F401 (side-effects only)
"""

from .create_set import create_set
from .update_set import update_set

__all__ = [
    "create_set",
    "update_set",
]
