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

"""Goal (GOL) models -- Pydantic schema powered by the generic ``models/md`` engine.

Mirrors the ``req/models/v1`` layout: frontmatter and body classes under this
same package; the document-level ``GolDocument`` wrapper, the free-function
``parse_gol`` entry point, and the ``GolSummary`` listing model join in a
later phase (see the feature README's Task List, Phase 2). Body classes map
directly to heading sections in a goal markdown file -- see ``body.py`` for
the full hierarchy.
"""

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
from .frontmatter import GolFrontmatter

__all__ = [
    "AcceptanceCriteria",
    "Decisions",
    "Description",
    "Goal",
    "Goals",
    "GolFrontmatter",
    "MoreInformation",
    "Notes",
    "Priority",
    "RelatedArtifacts",
    "Requirements",
    "Source",
    "Tags",
]
