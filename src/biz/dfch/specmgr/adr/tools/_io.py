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

"""Thin file read/write helpers over ``parse_adr``/``render_adr`` (plan §7, §9a).

No ``mcp`` dependency here either -- these are plain file-I/O adapters,
kept separate from the ``@mcp.tool()``-decorated functions in ``tools.py``
so they stay independently testable.
"""

from __future__ import annotations

from pathlib import Path

from ...models.adr import Adr, parse_adr, render_adr
from ._paths import find_adr_path

__all__ = ["load_by_id", "read_adr", "write_adr"]


def read_adr(path: Path) -> Adr:
    """Read and parse the ADR at ``path`` (plan §7's "re-read, re-parse")."""
    return parse_adr(path.read_text(encoding="utf-8"))


def write_adr(path: Path, adr: Adr) -> None:
    """Render ``adr`` and write it to ``path`` (plan §7's "re-render, re-write")."""
    path.write_text(render_adr(adr), encoding="utf-8")


def load_by_id(base_dir: Path, id_: str) -> tuple[Path, Adr]:
    """Resolve ``id_`` under ``base_dir`` and read the matching ADR.

    Raises :class:`._paths.AdrNotFoundError` if no file matches.

    Returns
    -------
    tuple[Path, Adr]
        The resolved file path and the parsed document -- callers that
        mutate the document need the path to write it back afterward.
    """
    path = find_adr_path(base_dir, id_)
    return path, read_adr(path)
