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

"""MCP tool wrappers for requirements (mirrors ``uc/tools/``'s own shape).

``parse_req`` reads a raw filepath, parses, and validates it into a structured
document model. ``get_req_example`` returns a complete, valid sample requirement
document as raw markdown (Task 3.6); ``get_req_template`` returns a document
with every field present but populated with short placeholder ("blind text")
content instead (Task 3.7) -- both read a packaged, build-guaranteed data file
rather than anything on the caller's filesystem. ``get_req`` (feat-7-various-
improvements Task 0.9) reads, parses, and returns a full requirement document
by id -- the sole id-based read path for REQ, replacing the former
``specmgr://req/{id}`` resource (see ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
``list_req`` (feat-13-list-paging Task 2.2) returns one page of id/title/
status/ref summaries of every requirement, replacing the former
``specmgr://req/list`` resource so that ``max_results``/``offset`` paging
parameters could be accepted (see
``.specmgr/feat/feat-13-list-paging/README.md``). ``create_req`` (Task 3.12)
assigns a fresh id, builds the frontmatter itself, and writes a new document
(body markdown only, no frontmatter) under the requirement base directory
(``req.tools._paths``/``_io``). ``update_req`` (Task 3.13) replaces an
existing document's body the same way, preserving every frontmatter field
except ``updated``. ``set_status_req`` (Task 3.14) is the only path that
changes ``status``, also bumping ``updated``, leaving the body untouched.
``delete_req`` (Task 3.15) is a registered stub -- always raises
``NotImplementedError``, reserving the name for a future real
implementation. ``validate_req`` (Task 3.16) is a disk-free, id-free dry
run against a submitted ``content`` string, independent of the other
tools. Import this package to register all requirement tools at once::

    from biz.dfch.specmgr.req import tools  # noqa: F401 (side-effects only)
"""

from .create_req import create_req
from .delete_req import delete_req
from .get_req import get_req
from .get_req_example import get_req_example
from .get_req_template import get_req_template
from .list_req import list_req
from .parse_req import parse_req
from .set_status_req import set_status_req
from .update_req import update_req
from .validate_req import validate_req

__all__ = [
    "create_req",
    "delete_req",
    "get_req",
    "get_req_example",
    "get_req_template",
    "list_req",
    "parse_req",
    "set_status_req",
    "update_req",
    "validate_req",
]
