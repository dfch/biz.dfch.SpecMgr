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

"""Problem Statement (PRB) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``tsk/models/v1``/``qa/models/v2`` layout: a free-function
``parse_prb`` entry point, document-level ``PrbDocument(frontmatter, body)``
wrapper, frontmatter and body classes all live directly in this package.
Body classes map directly to heading sections in a ``prb`` markdown file --
see ``body.py`` for the full hierarchy.
"""

from ._util import SCHEMA_COMMENT_VERSION
from .body import (
    CurrentState,
    FutureState,
    Gap,
    Impact,
    MoreInformation,
    Prb,
    Question1,
    Question2,
    Question3,
    Question4,
    Question5,
    Question6,
    Question7,
    References,
    Summary,
)
from .document import PrbDocument
from .frontmatter import PrbFrontmatter
from .parser import parse_prb
from .summary import PrbSummary

__all__ = [
    "SCHEMA_COMMENT_VERSION",
    "CurrentState",
    "FutureState",
    "Gap",
    "Impact",
    "MoreInformation",
    "Prb",
    "PrbDocument",
    "PrbFrontmatter",
    "PrbSummary",
    "Question1",
    "Question2",
    "Question3",
    "Question4",
    "Question5",
    "Question6",
    "Question7",
    "References",
    "Summary",
    "parse_prb",
]
