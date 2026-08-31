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

"""MCP tool wrappers for verification case records (mirrors ``dec/tools/``'s own shape).

``parse_vcr`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_vcr_example`` returns a complete, valid
sample verification case record document as raw markdown; ``get_vcr_template``
returns a document with every field present but populated with short
placeholder ("blind text") content instead -- both read a packaged,
build-guaranteed data file rather than anything on the caller's filesystem
(Task 2.1). ``get_vcr`` reads, parses, and returns a full verification case
record document by id -- the sole id-based read path for VCR (there is no
``specmgr://vcr/{id}`` resource, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
``list_vcr`` returns one page of id/title/status/ref summaries of every
verification case record, shipped as a paged tool from day one (ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13). ``create_vcr`` assigns a fresh id,
builds the frontmatter itself, and writes a new document (body markdown
only, no frontmatter) under the verification case record base directory
(``vcr.tools._paths``/``_io``). Whole-body and line-range updates of an
existing document go through the generic ``update`` tool in
``general.tools`` (``type="vcr"``), preserving every frontmatter field
except ``updated``. Status changes of an existing document go through the
generic ``set_status`` tool in ``general.tools`` (``type="vcr"``), also
bumping ``updated``, leaving the body untouched.
``delete_vcr`` is a registered stub -- always raises
``NotImplementedError``, reserving the name for a future real
implementation. ``validate_vcr`` is a disk-free, id-free dry run against a
submitted ``content`` string, independent of the other tools. Import this
package to register all verification case record tools at once::

    from biz.dfch.specmgr.vcr import tools  # noqa: F401 (side-effects only)
"""

from .create_vcr import create_vcr
from .delete_vcr import delete_vcr
from .get_vcr import get_vcr
from .get_vcr_example import get_vcr_example
from .get_vcr_template import get_vcr_template
from .list_vcr import list_vcr
from .parse_vcr import parse_vcr
from .validate_vcr import validate_vcr

__all__ = [
    "create_vcr",
    "delete_vcr",
    "get_vcr",
    "get_vcr_example",
    "get_vcr_template",
    "list_vcr",
    "parse_vcr",
    "validate_vcr",
]
