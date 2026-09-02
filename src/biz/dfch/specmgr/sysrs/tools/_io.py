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

"""Thin file read helpers over ``parse_sysrs`` (Task 3.1).

Read-only, unlike ``adr.tools._io``'s ``read_adr``/``write_adr`` pair: there
is no ``write_sysrs``/``render_sysrs`` counterpart here, since ``create_sysrs``
and the generic ``update`` tool in ``general.tools`` persist the caller's
own already-validated body markdown byte-for-byte rather than rendering it
back out from a parsed model -- no
renderer is needed for that shape, so none is added speculatively here.
Mirrors ``vcr.tools._io``/``dec.tools._io`` file-for-file.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.
"""

from __future__ import annotations

from pathlib import Path

from ..models.v1 import SysrsDocument, parse_sysrs
from ._paths import find_sysrs_path

__all__ = ["load_by_id", "read_sysrs"]


def read_sysrs(path: Path) -> SysrsDocument:
    """Read and parse the System Requirements Specification at ``path``.

    Parameters
    ----------
    path:
        The filesystem path to the System Requirements Specification ``.md`` file.

    Returns
    -------
    SysrsDocument
        The parsed, validated document.
    """
    assert isinstance(path, Path), type(path)

    result = parse_sysrs(path.read_text(encoding="utf-8"))
    return result


def load_by_id(base_dir: Path, id_: str) -> tuple[Path, SysrsDocument]:
    """Resolve ``id_`` under ``base_dir`` and read the matching System Requirements Specification.

    Parameters
    ----------
    base_dir:
        The directory to scan for ``*.md`` files.
    id_:
        The id to look up.

    Returns
    -------
    tuple[Path, SysrsDocument]
        The resolved file path and the parsed document -- callers that
        mutate the document need the path to write it back afterward.

    Raises
    ------
    SysrsNotFoundError
        If no file matches (propagated from :func:`._paths.find_sysrs_path`).
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(id_, str), type(id_)
    assert id_.strip()

    path = find_sysrs_path(base_dir, id_)
    result = (path, read_sysrs(path))
    return result
