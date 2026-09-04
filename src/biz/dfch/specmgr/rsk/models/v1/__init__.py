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

"""Risk (RSK) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``tsk/models/v1`` layout: a free-function ``parse_rsk`` entry
point, document-level ``RskDocument(frontmatter, body)`` wrapper, and a
one-line ``RskSummary`` for the paged ``list_rsk`` tool, with frontmatter and
body subclasses under this same package. Body classes map directly to heading
sections in an ``rsk`` markdown file -- see ``body.py``/``assessment.py`` for
the full hierarchy.

Also backs feat-92-resources's cross-cutting reference-resource
model-backed drift-guard convention (ADR
356d8781-e446-4c26-917a-eda85648ce9d, REQ-003):

- :func:`parse_tara`/:class:`Tara` -- parses the TARA risk-response-
  strategy guidance document (``rsk/data/rsk_tara.md``) backing
  ``specmgr://rsk/tara``, purely to fail fast on structural drift (the
  parsed result is discarded by the resource itself).
"""

from ._util import SCHEMA_COMMENT_VERSION
from .assessment import (
    LEVEL_HIGH,
    LEVEL_LOW,
    LEVEL_MEDIUM,
    LEVEL_VERY_HIGH,
    Assessment,
    Impact,
    InitialAssessment,
    Probability,
    ResidualAssessment,
    level_from_product,
)
from .body import (
    Cause,
    Consequence,
    Mitigation,
    MoreInformation,
    Owner,
    Risk,
    Scope,
    Strategy,
    Tags,
    Trigger,
)
from .document import RskDocument
from .frontmatter import RskFrontmatter
from .parser import parse_rsk
from .summary import RskSummary
from .tara import (
    MitigationInteraction,
    MitigationItem,
    QuadrantItem,
    StatusInteraction,
    StatusItem,
    StrategyItem,
    Tara,
    WhenToApply,
    parse_tara,
)

__all__ = [
    "LEVEL_HIGH",
    "LEVEL_LOW",
    "LEVEL_MEDIUM",
    "LEVEL_VERY_HIGH",
    "SCHEMA_COMMENT_VERSION",
    "Assessment",
    "Cause",
    "Consequence",
    "Impact",
    "InitialAssessment",
    "Mitigation",
    "MitigationInteraction",
    "MitigationItem",
    "MoreInformation",
    "Owner",
    "Probability",
    "QuadrantItem",
    "ResidualAssessment",
    "Risk",
    "RskDocument",
    "RskFrontmatter",
    "RskSummary",
    "Scope",
    "StatusInteraction",
    "StatusItem",
    "Strategy",
    "StrategyItem",
    "Tags",
    "Tara",
    "Trigger",
    "WhenToApply",
    "level_from_product",
    "parse_rsk",
    "parse_tara",
]
