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

"""MCP tool wrappers for free-form text documents (mirrors ``vcr/tools/``'s own shape).

``parse_txt`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_txt_example`` returns a complete, valid
sample free-form text document as raw markdown; ``get_txt_template``
returns a document with every field present but populated with short
placeholder ("blind text") content instead -- both read a packaged,
build-guaranteed data file rather than anything on the caller's filesystem
(feat-229-txt Phase 110).
``get_txt_schema`` returns the domain's generated JSON Schema (2020-12
dialect) as raw text, reading the same packaged, build-guaranteed data
file (TXT ships the schema as a tool from day one, the feat-189 Phase 105
/ ADR 112b6498-078b-4a59-88b8-8ffb7a5041b3 precedent).
``get_txt`` reads, parses, and returns a full free-form text document by
id -- the sole id-based read path for TXT (there is no
``specmgr://txt/{id}`` resource, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
``list_txt`` returns one page of id/title/status/ref summaries of every
free-form text document, shipped as a paged tool from day one (ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13). ``create_txt`` assigns a fresh id,
builds the frontmatter itself, and writes a new document (body markdown
only, no frontmatter) under the free-form text base directory
(``txt.tools._paths``/``_io``). Whole-body and line-range updates of an
existing document go through the generic ``update`` tool in
``general.tools`` (``type="txt"``), preserving every frontmatter field
except ``updated``. Status changes of an existing document go through the
generic ``set_status`` tool in ``general.tools`` (``type="txt"``), also
bumping ``updated``, leaving the body untouched. Deletion of ``txt``
documents goes through the generic ``delete`` tool in ``general.tools``
(``type="txt"``). Disk-free, id-free dry-run content validation goes
through the generic ``validate`` tool in ``general.tools`` (``type="txt"``)
-- the generic-tool registration of those dispatches lands with this
feature's Phase 130; there is no per-domain mutation tool of this domain's
own (dispatch-only from day one, ADR 36905d5b-8057-4294-8665-c7eed5534db0).
Import this package to register all free-form text tools at once::

    from biz.dfch.specmgr.txt import tools  # noqa: F401 (side-effects only)
"""

from .create_txt import create_txt
from .get_txt import get_txt
from .get_txt_example import get_txt_example
from .get_txt_schema import get_txt_schema
from .get_txt_template import get_txt_template
from .list_txt import list_txt
from .parse_txt import parse_txt

__all__ = [
    "create_txt",
    "get_txt",
    "get_txt_example",
    "get_txt_schema",
    "get_txt_template",
    "list_txt",
    "parse_txt",
]
