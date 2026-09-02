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

"""MCP tool wrappers for System Requirements Specification (SYSRS) documents (mirrors ``vcr/tools/``'s own shape).

``parse_sysrs`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_sysrs_example`` returns a complete, valid
sample System Requirements Specification document as raw markdown;
``get_sysrs_template`` returns a document with every field present but
populated with short placeholder ("blind text") content instead -- both
read a packaged, build-guaranteed data file rather than anything on the
caller's filesystem (Task 3.2; the real packaged data files themselves
arrive in Phase 4, so both tools raise ``FileNotFoundError`` until then).
``get_sysrs`` reads, parses, and returns a full System Requirements
Specification document by id -- the sole id-based read path for SYSRS
(there is no ``specmgr://sysrs/{id}`` resource, ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614). ``list_sysrs`` returns one page of
id/title/status/ref summaries of every System Requirements Specification,
shipped as a paged tool from day one (ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13). ``create_sysrs`` assigns a fresh id,
builds the frontmatter itself, and writes a new document (body markdown
only, no frontmatter) under the System Requirements Specification base
directory (``sysrs.tools._paths``/``_io``). Whole-body and line-range
updates of an existing document go through the generic ``update`` tool in
``general.tools`` (``type="sysrs"``), preserving every frontmatter field
except ``updated``. Status changes of an existing document go through the
generic ``set_status`` tool in ``general.tools`` (``type="sysrs"``), also
bumping ``updated``, leaving the body untouched. Classification changes go
through the generic ``set_classification`` tool in ``general.tools``
(``type="sysrs"``). Deletion of ``sysrs`` documents goes through the
generic ``delete`` tool in ``general.tools`` (``type="sysrs"``).
``validate_sysrs`` is a disk-free, id-free dry run against a submitted
``content`` string, independent of the other tools. There is **no**
per-domain ``update_sysrs``/``set_status_sysrs``/``delete_sysrs`` tool --
dispatch-only from day one, ADR 36905d5b-8057-4294-8665-c7eed5534db0.
Import this package to register all System Requirements Specification
tools at once::

    from biz.dfch.specmgr.sysrs import tools  # noqa: F401 (side-effects only)
"""

from .create_sysrs import create_sysrs
from .get_sysrs import get_sysrs
from .get_sysrs_example import get_sysrs_example
from .get_sysrs_template import get_sysrs_template
from .list_sysrs import list_sysrs
from .parse_sysrs import parse_sysrs
from .validate_sysrs import validate_sysrs

__all__ = [
    "create_sysrs",
    "get_sysrs",
    "get_sysrs_example",
    "get_sysrs_template",
    "list_sysrs",
    "parse_sysrs",
    "validate_sysrs",
]
