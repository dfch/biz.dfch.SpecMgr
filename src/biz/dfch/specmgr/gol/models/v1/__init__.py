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

"""Goal (GOL) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``req/models/v1`` layout: a free-function ``parse_gol`` entry point,
document-level ``GolDocument(frontmatter, body)`` wrapper, frontmatter and body
subclasses under this same package, and the ``GolSummary`` listing model for
the (Phase-3) ``list_gol`` tool. Body classes map directly to heading sections
in a goal markdown file -- see ``body.py`` for the full hierarchy.
"""

from ._util import SCHEMA_COMMENT_VERSION
from .body import (
    AcceptanceCriteria,
    Decisions,
    Description,
    Goal,
    Goals,
    MoreInformation,
    Notes,
    Priority,
    RelatedArtifacts,
    Requirements,
    Source,
    Tags,
)
from .document import GolDocument
from .frontmatter import GolFrontmatter
from .parser import parse_gol
from .summary import GolSummary

__all__ = [
    "SCHEMA_COMMENT_VERSION",
    "AcceptanceCriteria",
    "Decisions",
    "Description",
    "Goal",
    "Goals",
    "GolDocument",
    "GolFrontmatter",
    "GolSummary",
    "MoreInformation",
    "Notes",
    "Priority",
    "RelatedArtifacts",
    "Requirements",
    "Source",
    "Tags",
    "parse_gol",
]
