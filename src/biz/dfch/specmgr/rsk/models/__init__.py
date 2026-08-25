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

Mirrors ``tsk/models``'s layout: a versioned sub-package (``v1``, ...) holding
the frontmatter/body classes, the document wrapper and parser for ``rsk``
documents, and the one-line ``RskSummary`` for the paged ``list_rsk`` tool.
"""

from .v1 import (
    LEVEL_HIGH,
    LEVEL_LOW,
    LEVEL_MEDIUM,
    LEVEL_VERY_HIGH,
    SCHEMA_COMMENT_VERSION,
    Assessment,
    Cause,
    Consequence,
    Impact,
    InitialAssessment,
    Mitigation,
    MoreInformation,
    Owner,
    Probability,
    ResidualAssessment,
    Risk,
    RskDocument,
    RskFrontmatter,
    RskSummary,
    Scope,
    Strategy,
    Tags,
    Trigger,
    level_from_product,
    parse_rsk,
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
    "MoreInformation",
    "Owner",
    "Probability",
    "ResidualAssessment",
    "Risk",
    "RskDocument",
    "RskFrontmatter",
    "RskSummary",
    "Scope",
    "Strategy",
    "Tags",
    "Trigger",
    "level_from_product",
    "parse_rsk",
]
