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

"""Pydantic model for a full requirement document (frontmatter + body).

Mirrors `models.adr.v1.Adr`'s own frontmatter+body pairing. ``ReqDocument`` holds
no file/id/path information itself -- that lives on ``frontmatter.id``, same
convention as ``AdrFrontmatter.id``.

Frontmatter *stripping* is deliberately not this module's responsibility:
a caller splits a raw ``.md`` file's ``---...---`` block from its body via
``python-frontmatter`` (``frontmatter.loads(text)``), validates ``.metadata`` as
``ReqFrontmatter`` and ``.content`` as ``Requirement.from_text(...)`` separately, then
constructs a ``ReqDocument`` from the two already-parsed pieces -- there is no
``ReqDocument.from_text``/parser function here.
"""

from __future__ import annotations

from pydantic import BaseModel

from .body import Requirement
from .frontmatter import ReqFrontmatter

__all__ = ["ReqDocument"]


class ReqDocument(BaseModel):
    """A full requirement document: YAML frontmatter and body.

    Attributes
    ----------
    frontmatter:
        The YAML frontmatter block. See :class:`ReqFrontmatter`.
    body:
        The parsed requirement sections. See :class:`Requirement`.
    """

    frontmatter: ReqFrontmatter
    body: Requirement
