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

"""Standard Operating Procedure (SOP) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``dec/models/v1`` layout: a free-function ``parse_sop`` entry
point, document-level ``SopDocument(frontmatter, body)`` wrapper,
frontmatter and body subclasses under this same package, and the
``SopSummary`` listing model for the (Phase-2) ``list_sop`` tool. Body
classes map directly to heading sections in an SOP markdown file --
see ``body.py`` for the full hierarchy.
"""

from ._util import SCHEMA_COMMENT_VERSION
from .body import (
    AcceptanceCriteria,
    Accountable,
    Consulted,
    Decisions,
    Definitions,
    Goals,
    Informed,
    MoreInformation,
    Procedure,
    Purpose,
    RelatedArtifacts,
    Requirements,
    Responsible,
    RolesAndResponsibilities,
    SafetyAndPrecautions,
    Sop,
    Sops,
    Step,
    Support,
    UpdateEntry,
    Updates,
)
from .document import SopDocument
from .frontmatter import SopFrontmatter
from .parser import parse_sop
from .summary import SopSummary

__all__ = [
    "SCHEMA_COMMENT_VERSION",
    "AcceptanceCriteria",
    "Accountable",
    "Consulted",
    "Decisions",
    "Definitions",
    "Goals",
    "Informed",
    "MoreInformation",
    "Procedure",
    "Purpose",
    "RelatedArtifacts",
    "Requirements",
    "Responsible",
    "RolesAndResponsibilities",
    "SafetyAndPrecautions",
    "Sop",
    "SopDocument",
    "SopFrontmatter",
    "SopSummary",
    "Sops",
    "Step",
    "Support",
    "UpdateEntry",
    "Updates",
    "parse_sop",
]
