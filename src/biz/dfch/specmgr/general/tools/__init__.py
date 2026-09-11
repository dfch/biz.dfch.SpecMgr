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

"""MCP tool wrappers for general-purpose utilities (mirrors ``adr/tools/``'s shape).

``mdformat`` -- a markdown document formatter that preserves YAML frontmatter
blocks (for ADR/UC files) and formats only the body markdown. ``update`` --
the generic, cross-domain whole-body or line-range replace for the eleven
whole-body document types (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr; optional read-style body-line
``offset``/``limit`` coordinates -- ``offset`` = 1-based first line,
``limit`` = number of lines, omitted = through end of body, ``0`` = pure
insert, ``offset = N+1`` = the virtual end-of-body append position -- strict
validation, splice-then-validate-whole). ``set_status`` -- the generic,
cross-domain status change for all twelve document types (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/adr; ``superseded_by`` is
``adr``-only, composing the status as ``"superseded by {superseded_by}"``).
``set_classification`` -- the generic, cross-domain change of the free-text
``classification`` frontmatter field for the eleven whole-body document
types (``type`` is one of req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr;
``adr`` is not supported), bumping ``updated`` and leaving the body and
every other frontmatter field untouched; a blank/whitespace-only value
clears ``classification`` back to ``None``/absent.
``delete`` -- the
generic, cross-domain hard-delete for the eleven whole-body document types
(``type`` is one of req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr; ``adr`` is
not supported), resolving the document by ``id``, taking the domain's own
per-id lock, and removing it from disk (the single ``*.md`` file for the
ten flat domains, the entire ``<base>/<id>/`` folder for ``feat``),
returning the deleted path as a string. ``validate`` -- the generic,
cross-domain, disk-free/id-free dry-run content validator for the twelve
whole-body document types (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs; ``adr`` is not supported,
``validate_adr`` remains its own standalone tool); unlike every other
generic tool here, it never raises for a content-validation failure --
it always returns ``{valid: bool, errors: list[{message: str}]}``, only
raising ``ValueError`` for a ``full``/content-shape mismatch or an
unsupported ``type`` (feat-81-83-validation, ADR
078bf395-0a5f-4afd-84f6-b7a2191a00e6).
Import this package to register all general tools at once::

    from biz.dfch.specmgr.general import tools  # noqa: F401 (side-effects only)
"""

from .delete import delete
from .mdformat import mdformat
from .set_classification import set_classification
from .set_status import set_status
from .update import update
from .validate import validate

__all__ = [
    "delete",
    "mdformat",
    "set_classification",
    "set_status",
    "update",
    "validate",
]
