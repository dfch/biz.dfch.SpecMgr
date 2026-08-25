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

"""Thin file read helpers over ``parse_rsk`` (Task 3.1).

Read-only, unlike ``adr.tools._io``'s ``read_adr``/``write_adr`` pair: there
is no ``write_rsk``/``render_rsk`` counterpart here, since ``create_rsk``/
``update_rsk`` persist the caller's already-validated body markdown
byte-for-byte rather than rendering it back out from a parsed model -- no
renderer is needed for that shape, so none is added speculatively here.
Mirrors ``tsk.tools._io`` file-for-file.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.
"""

from __future__ import annotations

from pathlib import Path

from ..models.v1 import RskDocument, parse_rsk
from ._paths import find_rsk_path

__all__ = ["load_by_id", "read_rsk"]


def read_rsk(path: Path) -> RskDocument:
    """Read and parse the risk at ``path``.

    Parameters
    ----------
    path:
        The filesystem path to the risk ``.md`` file.

    Returns
    -------
    RskDocument
        The parsed, validated document.
    """
    assert isinstance(path, Path), type(path)

    result = parse_rsk(path.read_text(encoding="utf-8"))
    return result


def load_by_id(base_dir: Path, id_: str) -> tuple[Path, RskDocument]:
    """Resolve ``id_`` under ``base_dir`` and read the matching risk.

    Parameters
    ----------
    base_dir:
        The directory to scan for ``*.md`` files.
    id_:
        The id to look up.

    Returns
    -------
    tuple[Path, RskDocument]
        The resolved file path and the parsed document -- callers that
        mutate the document need the path to write it back afterward.

    Raises
    ------
    RskNotFoundError
        If no file matches (propagated from :func:`._paths.find_rsk_path`).
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(id_, str), type(id_)
    assert id_.strip()

    path = find_rsk_path(base_dir, id_)
    result = (path, read_rsk(path))
    return result
