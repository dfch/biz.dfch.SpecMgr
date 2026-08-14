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

"""Requirement (REQ) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``uc/models/v2`` layout: a free-function ``parse_req`` entry point,
document-level ``ReqDocument(frontmatter, body)`` wrapper, frontmatter and body
subclasses under this same package. Body classes map directly to heading sections
in a requirement markdown file -- see ``body.py`` for the full hierarchy.
"""

from ._util import SCHEMA_COMMENT_VERSION
from .body import (
    AcceptanceCriteria,
    Characteristics,
    Decisions,
    Description,
    Goals,
    Level,
    MoreInformation,
    Notes,
    Priority,
    RelatedArtifacts,
    Requirement,
    Requirements,
    Source,
    Tags,
)
from .document import ReqDocument
from .frontmatter import ReqFrontmatter
from .parser import parse_req

__all__ = [
    "SCHEMA_COMMENT_VERSION",
    "AcceptanceCriteria",
    "Characteristics",
    "Decisions",
    "Description",
    "Goals",
    "Level",
    "MoreInformation",
    "Notes",
    "Priority",
    "RelatedArtifacts",
    "ReqDocument",
    "Requirement",
    "ReqFrontmatter",
    "Requirements",
    "Source",
    "Tags",
    "parse_req",
]
