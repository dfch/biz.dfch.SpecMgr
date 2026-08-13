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

Currently just ``parse_req`` -- a single, narrowly-scoped tool added ahead of
the full Phase 3/4 tool specification/sequencing. Unlike ``adr/tools/``, there
is no id-based file storage layer for requirements yet (no
``req_base_dir``/``_paths.py``/``_io.py`` equivalent), so this tool takes a raw
filepath, reads it, and parses it into a structured document model. Import
this package to register all requirement tools at once::

    from biz.dfch.specmgr.req import tools  # noqa: F401 (side-effects only)
"""

from .parse_req import parse_req

__all__ = [
    "parse_req",
]
