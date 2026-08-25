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

"""MCP prompt wrappers for Risks (Task 3.13).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``rsk/tools/``/``rsk/resources/`` surface in the right order --
one module per prompt, mirroring ``req/prompts/``'s own one-module-per-
prompt split. Named ``create_risk``/``update_risk`` (the issue's literal
wording), not the ``rsk``-prefixed convention the tools/resources use --
see each prompt's own docstring. Import this package to register all risk
prompts at once::

    from biz.dfch.specmgr.rsk import prompts  # noqa: F401 (side-effects only)
"""

from .create_risk import create_risk
from .update_risk import update_risk

__all__ = [
    "create_risk",
    "update_risk",
]
