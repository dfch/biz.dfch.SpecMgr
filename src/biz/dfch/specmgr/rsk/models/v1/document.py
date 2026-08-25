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

"""Pydantic model for a full Risk document (frontmatter + body).

Mirrors `req.models.v1.document.ReqDocument`'s own frontmatter+body pairing
(and `tsk.models.v1.document.TskDocument`). ``RskDocument`` holds no
file/id/path information itself -- that lives on ``frontmatter.id``, same
convention as ``ReqFrontmatter.id``.

Frontmatter *stripping* is deliberately not this module's responsibility:
a caller splits a raw ``.md`` file's ``---...---`` block from its body via
``python-frontmatter`` (``frontmatter.loads(text)``), validates ``.metadata`` as
``RskFrontmatter`` and ``.content`` as ``Risk.from_text(...)`` separately, then
constructs a ``RskDocument`` from the two already-parsed pieces -- there is no
``RskDocument.from_text``/parser function here.
"""

from __future__ import annotations

from pydantic import BaseModel

from .body import Risk
from .frontmatter import RskFrontmatter

__all__ = ["RskDocument"]


class RskDocument(BaseModel):
    """A full Risk document: YAML frontmatter and body.

    Attributes
    ----------
    frontmatter:
        The YAML frontmatter block. See :class:`RskFrontmatter`.
    body:
        The parsed risk sections. See :class:`Risk`.
    """

    frontmatter: RskFrontmatter
    body: Risk
