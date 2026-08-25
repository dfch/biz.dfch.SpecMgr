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

"""Pydantic model for a full goal document (frontmatter + body).

Mirrors `req.models.v1.document.ReqDocument`/`prb.models.v1.document.PrbDocument`'s
own frontmatter+body pairing. ``GolDocument`` holds no file/id/path information
itself -- that lives on ``frontmatter.id``, same convention as
``GolFrontmatter.id``.

Frontmatter *stripping* is deliberately not this module's responsibility:
a caller splits a raw ``.md`` file's ``---...---`` block from its body via
``python-frontmatter`` (``frontmatter.loads(text)``), validates ``.metadata`` as
``GolFrontmatter`` and ``.content`` as ``Goal.from_text(...)`` separately, then
constructs a ``GolDocument`` from the two already-parsed pieces -- see
``gol/models/v1/parser.py::parse_gol`` for that glue.
"""

from __future__ import annotations

from pydantic import BaseModel

from .body import Goal
from .frontmatter import GolFrontmatter

__all__ = ["GolDocument"]


class GolDocument(BaseModel):
    """A full goal document: YAML frontmatter and body.

    Attributes
    ----------
    frontmatter:
        The YAML frontmatter block. See :class:`GolFrontmatter`.
    body:
        The parsed goal sections. See :class:`Goal`.
    """

    frontmatter: GolFrontmatter
    body: Goal
