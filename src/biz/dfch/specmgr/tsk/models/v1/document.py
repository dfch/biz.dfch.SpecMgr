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

"""Pydantic model for a full TaskList document (frontmatter + body).

Mirrors `req.models.v1.document.ReqDocument`'s own frontmatter+body pairing.
``TskDocument`` holds no file/id/path information itself -- that lives on
``frontmatter.id``, same convention as ``ReqFrontmatter.id``.

Frontmatter *stripping* is deliberately not this module's responsibility:
a caller splits a raw ``.md`` file's ``---...---`` block from its body via
``python-frontmatter`` (``frontmatter.loads(text)``), validates ``.metadata`` as
``TskFrontmatter`` and ``.content`` as ``Task.from_text(...)`` separately, then
constructs a ``TskDocument`` from the two already-parsed pieces -- there is no
``TskDocument.from_text``/parser function here.
"""

from __future__ import annotations

from pydantic import BaseModel

from .body import Task
from .frontmatter import TskFrontmatter

__all__ = ["TskDocument"]


class TskDocument(BaseModel):
    """A full TaskList document: YAML frontmatter and body.

    Attributes
    ----------
    frontmatter:
        The YAML frontmatter block. See :class:`TskFrontmatter`.
    body:
        The parsed task list sections. See :class:`Task`.
    """

    frontmatter: TskFrontmatter
    body: Task
