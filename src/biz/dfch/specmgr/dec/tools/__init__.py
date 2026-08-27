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

"""MCP tool wrappers for decisions (mirrors ``gol/tools/``'s own shape).

``parse_dec`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_dec_example`` returns a complete, valid
sample decision document as raw markdown; ``get_dec_template`` returns a
document with every field present but populated with short placeholder
("blind text") content instead -- both read a packaged, build-guaranteed
data file rather than anything on the caller's filesystem (Task 2.2).
``get_dec`` reads, parses, and returns a full decision document by id -- the
sole id-based read path for DEC (there is no ``specmgr://dec/{id}`` resource,
ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). ``list_dec`` returns one page of
id/title/status/ref summaries of every decision, shipped as a paged tool
from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). ``create_dec``
assigns a fresh id, builds the frontmatter itself, and writes a new document
(body markdown only, no frontmatter) under the decision base directory
(``dec.tools._paths``/``_io``). Whole-body and line-range updates of an
existing document go through the generic ``update`` tool in
``general.tools`` (``type="dec"``), preserving every frontmatter field
except ``updated``. Status changes of an existing document go through the
generic ``set_status`` tool in ``general.tools`` (``type="dec"``), also
bumping ``updated``, leaving the body untouched.
``delete_dec`` is a registered stub -- always raises
``NotImplementedError``, reserving the name for a future real
implementation. ``validate_dec`` is a disk-free, id-free dry run against a
submitted ``content`` string, independent of the other tools. Import this
package to register all decision tools at once::

    from biz.dfch.specmgr.dec import tools  # noqa: F401 (side-effects only)
"""

from .create_dec import create_dec
from .delete_dec import delete_dec
from .get_dec import get_dec
from .get_dec_example import get_dec_example
from .get_dec_template import get_dec_template
from .list_dec import list_dec
from .parse_dec import parse_dec
from .validate_dec import validate_dec

__all__ = [
    "create_dec",
    "delete_dec",
    "get_dec",
    "get_dec_example",
    "get_dec_template",
    "list_dec",
    "parse_dec",
    "validate_dec",
]
