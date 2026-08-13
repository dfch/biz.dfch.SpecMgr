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

"""MCP tool wrappers for use cases (mirrors ``adr/tools/``'s own shape).

Currently just ``parse_uc`` -- a single, narrowly-scoped tool added ahead of
the full Phase 3 (``.specmgr/feat/feat-4-use-cases/README.md``) tool
specification/sequencing, at the repo owner's explicit request. Unlike
``adr/tools/``, there is no id-based file storage layer for use cases yet
(no ``uc_base_dir``/``_paths.py``/``_io.py`` equivalent), so this tool takes
raw markdown text directly rather than resolving an id to an on-disk file.
Import this package to register all use-case tools at once::

    from biz.dfch.specmgr.uc import tools  # noqa: F401 (side-effects only)
"""

from .parse_uc import parse_uc

__all__ = [
    "parse_uc",
]
