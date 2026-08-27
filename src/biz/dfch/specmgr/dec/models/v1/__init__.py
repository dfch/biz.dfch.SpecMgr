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

"""Decision (DEC) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``gol/models/v1`` layout: a free-function ``parse_dec`` entry
point, document-level ``DecDocument(frontmatter, body)`` wrapper,
frontmatter and body subclasses under this same package, and the
``DecSummary`` listing model for the (Phase-2) ``list_dec`` tool. Body
classes map directly to heading sections in a decision markdown file --
see ``body.py`` for the full hierarchy.
"""

from ._util import SCHEMA_COMMENT_VERSION
from .body import (
    AcceptanceCriteria,
    Confirmation,
    Consequences,
    ConsideredOptions,
    Context,
    Decision,
    DecisionDrivers,
    DecisionOutcome,
    Decisions,
    Goals,
    MoreInformation,
    Option,
    ProsAndCons,
    RelatedArtifacts,
    Requirements,
    UpdateEntry,
    Updates,
)
from .document import DecDocument
from .frontmatter import DecFrontmatter
from .parser import parse_dec
from .summary import DecSummary

__all__ = [
    "SCHEMA_COMMENT_VERSION",
    "AcceptanceCriteria",
    "Confirmation",
    "Consequences",
    "ConsideredOptions",
    "Context",
    "DecDocument",
    "DecFrontmatter",
    "DecSummary",
    "Decision",
    "DecisionDrivers",
    "DecisionOutcome",
    "Decisions",
    "Goals",
    "MoreInformation",
    "Option",
    "ProsAndCons",
    "RelatedArtifacts",
    "Requirements",
    "UpdateEntry",
    "Updates",
    "parse_dec",
]
