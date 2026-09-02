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

"""MCP prompt registrations that are not specific to any single document
domain (Various improvements, Task 0.21; ``confluence_update``/
``confluence_fetch`` added feat-50-confluence Phase 8).

``compact_history`` guides rotating older ``### Recent Updates`` entries out
of any `.specmgr` feature folder's ``README.md`` into an optional sibling
``history.md``. ``confluence_update``/``confluence_fetch`` are thin,
single-tool-call prompts sharing their respective tools' exact names
(``general/tools/confluence_update.py``/``confluence_fetch.py``) --
instructional text only, telling the LLM to call the matching tool with
the given parameters. Domain-specific prompts (e.g. ``create_adr``/
``refine``) live under their own domain package instead. Import this
package to register all general prompts against the shared ``mcp``
application instance::

    from biz.dfch.specmgr.general import prompts  # noqa: F401 (side-effects only)
"""

from .compact_history import compact_history
from .confluence_fetch import confluence_fetch
from .confluence_update import confluence_update

__all__ = [
    "compact_history",
    "confluence_fetch",
    "confluence_update",
]
