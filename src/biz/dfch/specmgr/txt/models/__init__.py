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

Mirrors ``vcr/models``'s layout: a versioned sub-package (``v1``, ...)
holding the frontmatter/body classes, the document wrapper and parser for
``txt`` documents, and the one-line ``TxtSummary`` for the paged
``list_txt`` tool.
"""

from .v1 import (
    SCHEMA_COMMENT_VERSION,
    Txt,
    TxtBody,
    TxtDocument,
    TxtFrontmatter,
    TxtSummary,
    UpdateEntry,
    Updates,
    parse_txt,
)

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
