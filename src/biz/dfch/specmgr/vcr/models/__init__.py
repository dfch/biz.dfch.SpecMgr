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

"""Verification Case Record (VCR) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors ``dec/models``'s layout: a versioned sub-package (``v1``, ...)
holding the frontmatter/body classes, the document wrapper and parser for
``vcr`` documents, and the one-line ``VcrSummary`` for the paged
``list_vcr`` tool.
"""

from .v1 import (
    SCHEMA_COMMENT_VERSION,
    AcceptanceCriteria,
    AcceptanceCriterion,
    Coverage,
    MoreInformation,
    TestSteps,
    UpdateEntry,
    Updates,
    Vcr,
    VcrDocument,
    VcrFrontmatter,
    VcrSummary,
    Verifies,
    parse_vcr,
)

__all__ = [
    "SCHEMA_COMMENT_VERSION",
    "AcceptanceCriteria",
    "AcceptanceCriterion",
    "Coverage",
    "MoreInformation",
    "TestSteps",
    "UpdateEntry",
    "Updates",
    "Vcr",
    "VcrDocument",
    "VcrFrontmatter",
    "VcrSummary",
    "Verifies",
    "parse_vcr",
]
