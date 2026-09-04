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

"""MCP tool wrappers for Standard Operating Procedures (mirrors ``dec/tools/``'s own shape).

``parse_sop`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_sop_example`` returns a complete, valid
sample SOP document as raw markdown; ``get_sop_template`` returns a
document with every field present but populated with short placeholder
("blind text") content instead -- both read a packaged, build-guaranteed
data file rather than anything on the caller's filesystem (Task 2.2; the
real packaged data files arrive in Phase 3 Task 3.1/3.2).
``get_sop`` reads, parses, and returns a full SOP document by id -- the
sole id-based read path for SOP (there is no ``specmgr://sop/{id}`` resource,
ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). ``list_sop`` returns one page of
id/title/status/ref summaries of every SOP, shipped as a paged tool
from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). ``create_sop``
assigns a fresh id, builds the frontmatter itself, and writes a new document
(body markdown only, no frontmatter) under the SOP base directory
(``sop.tools._paths``/``_io``). Disk-free, id-free dry-run content
validation goes through the generic ``validate`` tool in ``general.tools``
(``type="sop"``) -- the former ``validate_sop`` tool was removed in favor
of it (feat-81-83-validation Phase 2). Import this package to register all
SOP tools at once::

    from biz.dfch.specmgr.sop import tools  # noqa: F401 (side-effects only)

``sop`` is the first domain built with **no** per-domain
``update_sop``/``set_status_sop`` tools at all (ADR 36905d5b): whole-body
and line-range updates of an existing document go through the generic
``update`` tool in ``general.tools`` (``type="sop"``), preserving every
frontmatter field except ``updated``; status changes go through the generic
``set_status`` tool in ``general.tools`` (``type="sop"``), also bumping
``updated``, leaving the body untouched; deletion goes through the generic
``delete`` tool in ``general.tools`` (``type="sop"``).
"""

from .create_sop import create_sop
from .get_sop import get_sop
from .get_sop_example import get_sop_example
from .get_sop_template import get_sop_template
from .list_sop import list_sop
from .parse_sop import parse_sop

__all__ = [
    "create_sop",
    "get_sop",
    "get_sop_example",
    "get_sop_template",
    "list_sop",
    "parse_sop",
]
