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

"""Feature (FEAT) v1 schema -- frontmatter, body, document, parser, summary.

Mirrors the ``dec/models/v1`` layout: a free-function ``parse_feat`` entry
point, document-level ``FeatDocument(frontmatter, body)`` wrapper,
frontmatter and body subclasses under this same package, and the
``FeatSummary`` listing model for the (Phase-2) ``list_feat`` tool. Body
classes map directly to heading sections in a feature markdown file -- see
``body.py`` for the full hierarchy.
"""

from ._util import SCHEMA_COMMENT_VERSION
from .body import (
    AcceptanceCriteria,
    AcceptanceCriterionItem,
    Blockers,
    Blocks,
    CurrentStatus,
    DecisionEntry,
    DecisionsMade,
    Dependencies,
    DependsOn,
    DesignNotes,
    ExplicitlyOutOfScope,
    Feature,
    Included,
    MoreInformation,
    Overview,
    Phase,
    Plan,
    Progress,
    RelatedDecisions,
    RelatedPrsCommits,
    RequirementItem,
    Requirements,
    Scope,
    TaskList,
    UpdateEntry,
    Updates,
)
from .document import FeatDocument
from .frontmatter import FeatFrontmatter
from .parser import parse_feat
from .summary import FeatSummary

__all__ = [
    "SCHEMA_COMMENT_VERSION",
    "AcceptanceCriteria",
    "AcceptanceCriterionItem",
    "Blockers",
    "Blocks",
    "CurrentStatus",
    "DecisionEntry",
    "DecisionsMade",
    "Dependencies",
    "DependsOn",
    "DesignNotes",
    "ExplicitlyOutOfScope",
    "FeatDocument",
    "FeatFrontmatter",
    "FeatSummary",
    "Feature",
    "Included",
    "MoreInformation",
    "Overview",
    "Phase",
    "Plan",
    "Progress",
    "RelatedDecisions",
    "RelatedPrsCommits",
    "RequirementItem",
    "Requirements",
    "Scope",
    "TaskList",
    "UpdateEntry",
    "Updates",
    "parse_feat",
]
