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

"""Thin file read helpers over ``parse_uc`` (Task 3.1.5).

Read-only, mirroring ``req.tools._io`` exactly: there is no
``write_uc``/``render_uc`` counterpart here, since ``create_uc`` and the
generic ``update`` tool in ``general.tools`` persist the caller's
already-validated body markdown byte-for-byte rather than rendering it back
out from a parsed model -- no renderer is needed for that shape, so none is
added speculatively here.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.
"""

from __future__ import annotations

from pathlib import Path

from ..models.v2 import UcDocument, parse_uc
from ._paths import find_uc_path

__all__ = ["load_by_id", "read_uc"]


def read_uc(path: Path) -> UcDocument:
    """Read and parse the use case at ``path``.

    Parameters
    ----------
    path:
        The filesystem path to the use-case ``.md`` file.

    Returns
    -------
    UcDocument
        The parsed, validated document.
    """
    assert isinstance(path, Path), type(path)

    result = parse_uc(path.read_text(encoding="utf-8"))
    return result


def load_by_id(base_dir: Path, id_: str) -> tuple[Path, UcDocument]:
    """Resolve ``id_`` under ``base_dir`` and read the matching use case.

    Parameters
    ----------
    base_dir:
        The directory to scan for ``*.md`` files.
    id_:
        The id to look up.

    Returns
    -------
    tuple[Path, UcDocument]
        The resolved file path and the parsed document -- callers that
        mutate the document need the path to write it back afterward.

    Raises
    ------
    UcNotFoundError
        If no file matches (propagated from :func:`._paths.find_uc_path`).
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(id_, str), type(id_)
    assert id_.strip()

    path = find_uc_path(base_dir, id_)
    result = (path, read_uc(path))
    return result
