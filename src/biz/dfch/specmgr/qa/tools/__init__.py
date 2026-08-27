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

"""MCP tool wrappers for Question and Answer (QA) documents (mirrors ``req/tools/``'s own shape).

``parse_qa`` reads a raw filepath, parses, and validates it into a structured
document model. ``get_qa_example`` returns a complete, valid sample QA
document as raw markdown; ``get_qa_template`` returns a document with every
field present but populated with short placeholder ("blind text") content
instead -- both read a packaged, build-guaranteed data file rather than
anything on the caller's filesystem. ``get_qa`` reads, parses, and returns a
full QA document by id -- the sole id-based read path for QA, mirroring
REQ's own choice (see ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). ``list_qa``
(feat-13-list-paging Task 2.5) returns one page of id/title/status/ref
summaries of every QA document, replacing the former ``specmgr://qa/list``
resource so that ``max_results``/``offset`` paging parameters could be
accepted (see ``.specmgr/feat/feat-13-list-paging/README.md``). ``create_qa``
assigns a fresh id, builds the frontmatter itself, and writes a new document
(body markdown only, no frontmatter) under the QA base directory
(``qa.tools._paths``/``_io``). Whole-body and line-range updates of an
existing document go through the generic ``update`` tool in ``general.tools``
(``type="qa"``), preserving every frontmatter field except ``updated``.
Status changes of an existing document go through the generic
``set_status`` tool in ``general.tools`` (``type="qa"``), also bumping
``updated``, leaving the body untouched. ``delete_qa`` is a registered stub
-- always raises ``NotImplementedError``, reserving the name for a future
real implementation. ``validate_qa`` is a disk-free, id-free dry run against
a submitted ``content`` string, independent of the other tools. Import this
package to register all QA tools at once::

    from biz.dfch.specmgr.qa import tools  # noqa: F401 (side-effects only)
"""

from .create_qa import create_qa
from .delete_qa import delete_qa
from .get_qa import get_qa
from .get_qa_example import get_qa_example
from .get_qa_template import get_qa_template
from .list_qa import list_qa
from .parse_qa import parse_qa
from .validate_qa import validate_qa

__all__ = [
    "create_qa",
    "delete_qa",
    "get_qa",
    "get_qa_example",
    "get_qa_template",
    "list_qa",
    "parse_qa",
    "validate_qa",
]
