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

"""Risk (RSK) models -- Pydantic schema and (in a later phase) parser powered by the generic ``models/md`` engine.

Mirrors the ``tsk/models/v1`` layout: body classes map directly to heading
sections in an ``rsk`` markdown file -- see ``body.py``/``assessment.py`` for
the full hierarchy -- and ``frontmatter.py`` narrows the generic
``MarkdownFrontmatter`` for the ``rsk`` document type.

Per `.specmgr/feat/feat-15-add-artifact-type-risk/README.md` Phase 1
("Specification"), only the frontmatter and body models exist so far. There is
no ``RskDocument``/``parse_rsk``/``RskSummary`` yet -- those are Phase 2 -- so,
unlike ``tsk.models.v1``, this package does not yet export them.
"""

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
from .frontmatter import RskFrontmatter

__all__ = [
    "LEVEL_HIGH",
    "LEVEL_LOW",
    "LEVEL_MEDIUM",
    "LEVEL_VERY_HIGH",
    "Assessment",
    "Cause",
    "Consequence",
    "Impact",
    "InitialAssessment",
    "Mitigation",
    "MoreInformation",
    "Owner",
    "Probability",
    "ResidualAssessment",
    "Risk",
    "RskFrontmatter",
    "Scope",
    "Strategy",
    "Tags",
    "Trigger",
    "level_from_product",
]
