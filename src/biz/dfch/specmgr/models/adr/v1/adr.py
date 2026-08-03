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

"""Pydantic model for a full ADR document (frontmatter + body).

Deliberately holds no file/id/path information -- the file/directory
naming and id-assignment scheme is still an open backlog item (plan §9)
and is out of scope for this schema.
"""

from __future__ import annotations

from pydantic import BaseModel

from ._util import CURRENT_SCHEMA_VERSION, SCHEMA_MAJOR_VERSION
from .body import AdrBody
from .frontmatter import AdrFrontmatter

__all__ = ["CURRENT_SCHEMA_VERSION", "SCHEMA_MAJOR_VERSION", "Adr"]


class Adr(BaseModel):
    """A full ADR document: YAML frontmatter and body.

    This is the structured object the future parser produces from an
    on-disk ``.md`` file and the renderer consumes to produce one, and the
    shape ``get_adr``/``create_adr`` (plan §8) are expected to exchange
    with the LLM instead of raw markdown text.

    The specmgr schema version lives on ``frontmatter.version`` (plan §3),
    not here -- it must round-trip through the on-disk file's YAML block,
    which only ``frontmatter``/``body`` do (plan §7); a top-level field on
    this wrapper class would never be persisted.

    Parameters
    ----------
    frontmatter:
        The YAML frontmatter block, including the schema version. See
        :class:`AdrFrontmatter`.
    body:
        The parsed body sections and options. See :class:`AdrBody`.
    """

    frontmatter: AdrFrontmatter
    body: AdrBody
