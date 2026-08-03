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

"""ADR schema version 1 (``SCHEMA_MAJOR_VERSION == 1``).

Holds every model class for this schema major version. See
``doc/adr-tool-plan.md`` §6 for the versioning strategy: a new major schema
version gets its own sibling package (``models/adr/v2/``, ...) containing
*only* the classes that actually changed for that version -- unchanged
classes are imported from the previous version's package rather than
duplicated -- plus a ``migrate_v1_to_v2()``-style adapter function. This
package is never itself duplicated wholesale; it is the frozen v1 baseline
that later versions diff against.
"""

from .adr import CURRENT_SCHEMA_VERSION, SCHEMA_MAJOR_VERSION, Adr
from .body import AdrBody
from .frontmatter import AdrFrontmatter
from .option import AdrOption
from .parser import AdrParseError, parse_adr

__all__ = [
    "CURRENT_SCHEMA_VERSION",
    "SCHEMA_MAJOR_VERSION",
    "Adr",
    "AdrBody",
    "AdrFrontmatter",
    "AdrOption",
    "AdrParseError",
    "parse_adr",
]
