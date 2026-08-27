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

"""MCP tool wrappers for problem statements (mirrors ``tsk/tools/``'s own shape).

``parse_prb`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_prb_example`` returns a complete, valid
sample problem statement document as raw markdown; ``get_prb_template``
returns a document with every field present but populated with short
placeholder ("blind text") content instead -- both read a packaged,
build-guaranteed data file rather than anything on the caller's filesystem.
``get_prb`` reads, parses, and returns a full problem statement document by
id -- the sole id-based read path for PRB (there is no
``specmgr://prb/{id}`` resource). ``list_prb`` returns one page of
id/title/status/ref summaries of every problem statement, shipped as a
paged tool from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
``create_prb`` assigns a fresh id, builds the frontmatter itself, and
writes a new document (body markdown only, no frontmatter) under the
problem statement base directory (``prb.tools._paths``/``_io``).
Whole-body and line-range updates of an existing document go through the
generic ``update`` tool in ``general.tools`` (``type="prb"``), preserving
every frontmatter field except ``updated``. Status changes of an existing
document go through the generic ``set_status`` tool in ``general.tools``
(``type="prb"``), also bumping ``updated``, leaving the body untouched.
``delete_prb`` is a registered stub -- always raises
``NotImplementedError``, reserving the name for a future real
implementation. ``validate_prb`` is a disk-free, id-free dry run against a
submitted ``content`` string, independent of the other tools. Import this
package to register all problem statement tools at once::

    from biz.dfch.specmgr.prb import tools  # noqa: F401 (side-effects only)
"""

from .create_prb import create_prb
from .delete_prb import delete_prb
from .get_prb import get_prb
from .get_prb_example import get_prb_example
from .get_prb_template import get_prb_template
from .list_prb import list_prb
from .parse_prb import parse_prb
from .validate_prb import validate_prb

__all__ = [
    "create_prb",
    "delete_prb",
    "get_prb",
    "get_prb_example",
    "get_prb_template",
    "list_prb",
    "parse_prb",
    "validate_prb",
]
