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

"""Pydantic model for a full feature document (frontmatter + body).

Mirrors `dec.models.v1.document.DecDocument`'s own frontmatter+body pairing.
``FeatDocument`` holds no file/id/path information itself -- that lives on
``frontmatter.id``, same convention as ``FeatFrontmatter.id`` (though, unlike
every other domain, `feat`'s own `id` is also -- by REQ-004's addressing
convention -- the name of the containing folder, an invariant enforced at
the *tool* layer in Phase 2, not here).

Frontmatter *stripping* is deliberately not this module's responsibility:
a caller splits a raw ``.md`` file's ``---...---`` block from its body via
``python-frontmatter`` (``frontmatter.loads(text)``), validates ``.metadata`` as
``FeatFrontmatter`` and ``.content`` as ``Feature.from_text(...)`` separately,
then constructs a ``FeatDocument`` from the two already-parsed pieces -- see
``feat/models/v1/parser.py::parse_feat`` for that glue.
"""

from __future__ import annotations

from pydantic import BaseModel

from .body import Feature
from .frontmatter import FeatFrontmatter

__all__ = ["FeatDocument"]


class FeatDocument(BaseModel):
    """A full feature document: YAML frontmatter and body.

    Attributes
    ----------
    frontmatter:
        The YAML frontmatter block. See :class:`FeatFrontmatter`.
    body:
        The parsed feature sections. See :class:`Feature`.
    """

    frontmatter: FeatFrontmatter
    body: Feature
