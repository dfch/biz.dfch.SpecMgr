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

"""TaskList (TSK) models -- Pydantic schema and (in a later phase) parser powered by ``models/md``.

Mirrors the ``req/models/v1`` layout: body classes map directly to heading
sections in a ``tsk`` markdown file -- see ``body.py``/``task_item.py`` for
the full hierarchy -- and ``frontmatter.py`` narrows the generic
``MarkdownFrontmatter`` for the ``tsk`` document type.

Per `.specmgr/feat/feat-10-add-artifact-type-tasklist/README.md` Phase 1
("Specification"), only the frontmatter and body models exist so far. There is
no ``TskDocument``/``parse_tsk``/``TskSummary`` yet -- those are Phase 2 -- so,
unlike ``req.models.v1``, this package does not yet export them.
"""

from .body import RecentUpdates, Task, UpdateEntry
from .frontmatter import TskFrontmatter
from .task_item import TaskItem

__all__ = [
    "RecentUpdates",
    "Task",
    "TaskItem",
    "TskFrontmatter",
    "UpdateEntry",
]
