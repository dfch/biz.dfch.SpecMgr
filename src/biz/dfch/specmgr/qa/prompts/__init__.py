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

"""MCP prompt registrations for Question and Answer (QA) documents (Phase 4, Task 4.3).

``create_qa`` guides drafting a brand-new QA document. ``update_qa`` guides
revising an existing one by id. Both return instructional text, not tool
calls themselves -- mirroring ``req.prompts``'s own shape. Import this
package to register all QA prompts against the shared ``mcp`` application
instance::

    from biz.dfch.specmgr.qa import prompts  # noqa: F401 (side-effects only)
"""

from .create_qa import create_qa
from .update_qa import update_qa

__all__ = [
    "create_qa",
    "update_qa",
]
