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

"""Free-Form Text (TXT) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``vcr/models/v1`` layout: a free-function ``parse_txt`` entry
point, document-level ``TxtDocument(frontmatter, body)`` wrapper,
frontmatter and body subclasses under this same package, and the
``TxtSummary`` listing model for the (Phase 110) ``list_txt`` tool. Body
classes map directly to the structure of a free-form text markdown file --
an opaque free-form ``body`` plus a mandatory newest-first ``## Updates``
log -- see ``body.py`` for the full hierarchy.
"""

from ._util import SCHEMA_COMMENT_VERSION
from .body import Txt, TxtBody, UpdateEntry, Updates
from .document import TxtDocument
from .frontmatter import TxtFrontmatter
from .parser import parse_txt
from .summary import TxtSummary

__all__ = [
    "SCHEMA_COMMENT_VERSION",
    "Txt",
    "TxtBody",
    "TxtDocument",
    "TxtFrontmatter",
    "TxtSummary",
    "UpdateEntry",
    "Updates",
    "parse_txt",
]
