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
the generic, cross-domain whole-body or line-range replace for the seven
whole-body document types (``type`` is one of req/uc/tsk/qa/prb/gol/rsk;
optional 1-based inclusive body-line ``begin``/``end`` range with the
``N+1`` end-of-body sentinel). ``set_status`` -- the generic, cross-domain
status change for all eight document types (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/adr; ``superseded_by`` is ``adr``-only, composing
the status as ``"superseded by {superseded_by}"``). ``webfetch`` -- a
bearer-authenticated HTTP GET fetch restricted to a configured base URL.
Import this package to register all general tools at once::

    from biz.dfch.specmgr.general import tools  # noqa: F401 (side-effects only)
"""

from .mdformat import mdformat
from .set_status import set_status
from .update import update
from .webfetch import webfetch

__all__ = [
    "mdformat",
    "set_status",
    "update",
    "webfetch",
]
