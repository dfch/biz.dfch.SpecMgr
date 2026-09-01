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

"""MCP tool wrappers for goals (mirrors ``prb/tools/``'s own shape).

``parse_gol`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_gol_example`` returns a complete, valid
sample goal document as raw markdown; ``get_gol_template`` returns a document
with every field present but populated with short placeholder ("blind text")
content instead -- both read a packaged, build-guaranteed data file rather
than anything on the caller's filesystem (Task 3.10). ``get_gol`` (Task 3.8)
reads, parses, and returns a full goal document by id -- the sole id-based
read path for GOL (there is no ``specmgr://gol/{id}`` resource, ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614). ``list_gol`` (Task 3.9) returns one
page of id/title/status/ref summaries of every goal, shipped as a paged tool
from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). ``create_gol``
(Task 3.3) assigns a fresh id, builds the frontmatter itself, and writes a
new document (body markdown only, no frontmatter) under the goal base
directory (``gol.tools._paths``/``_io``). Whole-body and line-range updates
of an existing document go through the generic ``update`` tool in
``general.tools`` (``type="gol"``), preserving every frontmatter field
except ``updated``. Status changes of an existing document go through the
generic ``set_status`` tool in ``general.tools`` (``type="gol"``), also
bumping ``updated``, leaving the body untouched. Deletion of ``gol``
documents goes through the generic ``delete`` tool in ``general.tools``
(``type="gol"``). ``validate_gol`` (Task 3.7) is a disk-free, id-free dry
run against a submitted ``content`` string, independent of the other tools.
Import this package to register all goal tools at once::

    from biz.dfch.specmgr.gol import tools  # noqa: F401 (side-effects only)
"""

from .create_gol import create_gol
from .get_gol import get_gol
from .get_gol_example import get_gol_example
from .get_gol_template import get_gol_template
from .list_gol import list_gol
from .parse_gol import parse_gol
from .validate_gol import validate_gol

__all__ = [
    "create_gol",
    "get_gol",
    "get_gol_example",
    "get_gol_template",
    "list_gol",
    "parse_gol",
    "validate_gol",
]
