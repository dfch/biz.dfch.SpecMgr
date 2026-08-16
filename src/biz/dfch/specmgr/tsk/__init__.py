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

"""TaskList (TSK) domain -- lightweight task/todo-list specifications.

This is a domain-first package, mirroring ``req``'s layout (per ADR
ece4554b-725c-4f76-bc04-5d2b760363d2), that will eventually contain models,
tools, prompts, and resources for managing ``tsk`` documents.

As of `.specmgr/feat/feat-10-add-artifact-type-tasklist/README.md` Phase 1
("Specification"), only ``models`` exists (``tsk.models.v1``). There are no
``tools``/``prompts``/``resources`` sub-packages yet -- those are Phase 3 --
so, unlike ``req``/``uc``/``adr``/``general``, this package deliberately does
not yet import/re-export them here.
"""

__all__: list[str] = []
