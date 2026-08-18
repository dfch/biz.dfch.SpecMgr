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

"""Question and Answer (QA) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``tsk/models/v1`` layout: a free-function ``parse_qa`` entry point,
document-level ``QaDocument(frontmatter, body)`` wrapper, frontmatter and body
subclasses under this same package. Body classes map directly to heading sections
in a ``qa`` markdown file -- see ``body.py`` for the full hierarchy.
"""

from ._util import SCHEMA_COMMENT_VERSION
from .body import (
    Compatibility,
    FunctionalSuitability,
    Flexibility,
    General,
    InteractionCapability,
    Introduction,
    Maintainability,
    MoreInformation,
    PerformanceEfficiency,
    Qa,
    QaAnswer,
    QaSection,
    RawRequirements,
    Reliability,
    Requirement,
    Safety,
    Security,
)
from .document import QaDocument
from .frontmatter import QaFrontmatter
from .parser import parse_qa
from .summary import QaSummary

__all__ = [
    "SCHEMA_COMMENT_VERSION",
    "Compatibility",
    "Flexibility",
    "FunctionalSuitability",
    "General",
    "InteractionCapability",
    "Introduction",
    "Maintainability",
    "MoreInformation",
    "PerformanceEfficiency",
    "Qa",
    "QaAnswer",
    "QaDocument",
    "QaFrontmatter",
    "QaSection",
    "QaSummary",
    "RawRequirements",
    "Reliability",
    "Requirement",
    "Safety",
    "Security",
    "parse_qa",
]
