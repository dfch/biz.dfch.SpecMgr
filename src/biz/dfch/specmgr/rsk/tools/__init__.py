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

"""MCP tool wrappers for risks (mirrors ``tsk/tools/``'s own shape).

``parse_rsk`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_rsk_example`` returns a complete, valid
sample risk document as raw markdown; ``get_rsk_template`` returns a
document with every field present but populated with short placeholder
("blind text") content instead -- both read a packaged, build-guaranteed
data file rather than anything on the caller's filesystem. ``get_rsk``
reads, parses, and returns a full risk document by id -- the sole id-based
read path for RSK (there never was a ``specmgr://rsk/{id}`` resource to
begin with). ``list_rsk`` (Task 3.14) returns one page of
id/title/status/ref summaries of every risk, plus the initial/residual 5x5
zone levels, the TARA strategy word, the first ``## Scope`` entry, and the
residual-risk coordinates (``RskSummary``), so that ``max_results``/
``offset`` paging parameters can be accepted (feat-13-list-paging, ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13). ``create_rsk`` assigns a fresh id,
builds the frontmatter itself, and writes a new document (body markdown
only, no frontmatter) under the risk base directory (``rsk.tools._paths``/
``_io``). Whole-body and line-range updates of an existing document go
through the generic ``update`` tool in ``general.tools`` (``type="rsk"``),
preserving every frontmatter field except ``updated``. Status changes of an
existing document go through the generic ``set_status`` tool in
``general.tools`` (``type="rsk"``), also bumping ``updated``, leaving the
body untouched. Deletion of ``rsk`` documents goes through the generic
``delete`` tool in ``general.tools`` (``type="rsk"``). ``validate_rsk`` is
a disk-free, id-free dry run against a submitted ``content`` string,
independent of the other tools. Import this package to register all risk
tools at once::

    from biz.dfch.specmgr.rsk import tools  # noqa: F401 (side-effects only)
"""

from .create_rsk import create_rsk
from .get_rsk import get_rsk
from .get_rsk_example import get_rsk_example
from .get_rsk_template import get_rsk_template
from .list_rsk import list_rsk
from .parse_rsk import parse_rsk
from .validate_rsk import validate_rsk

__all__ = [
    "create_rsk",
    "get_rsk",
    "get_rsk_example",
    "get_rsk_template",
    "list_rsk",
    "parse_rsk",
    "validate_rsk",
]
