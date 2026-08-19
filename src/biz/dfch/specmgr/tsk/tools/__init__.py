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

"""MCP tool wrappers for task lists (mirrors ``req/tools/``'s own shape).

``parse_tsk`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_tsk_example`` returns a complete, valid
sample task list document as raw markdown; ``get_tsk_template`` returns a
document with every field present but populated with short placeholder
("blind text") content instead -- both read a packaged, build-guaranteed
data file rather than anything on the caller's filesystem. ``get_tsk``
reads, parses, and returns a full task list document by id -- the sole
id-based read path for TSK (there never was a
``specmgr://tsk/{id}`` resource to begin with). ``list_tsk``
(feat-13-list-paging Task 2.4) returns one page of id/title/status/ref
summaries of every task list, replacing the former ``specmgr://tsk/list``
resource so that ``max_results``/``offset`` paging parameters could be
accepted (see ``.specmgr/feat/feat-13-list-paging/README.md``).
``create_tsk`` assigns a fresh id, builds the frontmatter itself, and
writes a new document (body markdown only, no frontmatter) under the task
list base directory (``tsk.tools._paths``/``_io``). ``update_tsk`` replaces
an existing document's body the same way, preserving every frontmatter
field except ``updated``. ``set_status_tsk`` is the only path that changes
``status``, also bumping ``updated``, leaving the body untouched.
``delete_tsk`` is a registered stub -- always raises ``NotImplementedError``,
reserving the name for a future real implementation. ``validate_tsk`` is a
disk-free, id-free dry run against a submitted ``content`` string,
independent of the other tools. Import this package to register all task
list tools at once::

    from biz.dfch.specmgr.tsk import tools  # noqa: F401 (side-effects only)
"""

from .create_tsk import create_tsk
from .delete_tsk import delete_tsk
from .get_tsk import get_tsk
from .get_tsk_example import get_tsk_example
from .get_tsk_template import get_tsk_template
from .list_tsk import list_tsk
from .parse_tsk import parse_tsk
from .set_status_tsk import set_status_tsk
from .update_tsk import update_tsk
from .validate_tsk import validate_tsk

__all__ = [
    "create_tsk",
    "delete_tsk",
    "get_tsk",
    "get_tsk_example",
    "get_tsk_template",
    "list_tsk",
    "parse_tsk",
    "set_status_tsk",
    "update_tsk",
    "validate_tsk",
]
