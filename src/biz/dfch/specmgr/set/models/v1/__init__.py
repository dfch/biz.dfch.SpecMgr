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

"""Set (SET) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``txt/models/v1`` layout: a free-function ``parse_set`` entry
point, document-level ``SetDocument(frontmatter, body)`` wrapper,
frontmatter and body subclasses under this same package, and the
``SetSummary`` listing model for the paged ``list_set`` tool. Body classes
map directly to the structure of a set markdown file -- a mandatory opaque
``## Description`` plus a mandatory mixed-tag ``## Items`` list -- see
``body.py`` for the full hierarchy.
"""

from ._util import SCHEMA_COMMENT_VERSION
from .body import Description, Items, Set
from .document import SetDocument
from .frontmatter import SetFrontmatter
from .parser import parse_set, parse_set_body
from .summary import SetSummary

__all__ = [
    "SCHEMA_COMMENT_VERSION",
    "Description",
    "Items",
    "Set",
    "SetDocument",
    "SetFrontmatter",
    "SetSummary",
    "parse_set",
    "parse_set_body",
]
