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

"""Thin file read helpers over ``parse_req`` (Task 3.11).

Read-only, unlike ``adr.tools._io``'s ``read_adr``/``write_adr`` pair: there
is no ``write_req``/``render_req`` counterpart here, since Task 3.9's design
settled on ``create_req``/``update_req`` (Tasks 3.12/3.13) persisting the
caller's already-validated body markdown byte-for-byte rather than rendering
it back out from a parsed model -- no renderer is needed for that shape, so
none is added speculatively here.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.
"""

from __future__ import annotations

from pathlib import Path

from ..models.v1 import ReqDocument, parse_req
from ._paths import find_req_path

__all__ = ["load_by_id", "read_req"]


def read_req(path: Path) -> ReqDocument:
    """Read and parse the requirement at ``path``.

    Parameters
    ----------
    path:
        The filesystem path to the requirement ``.md`` file.

    Returns
    -------
    ReqDocument
        The parsed, validated document.
    """
    assert isinstance(path, Path), type(path)

    result = parse_req(path.read_text(encoding="utf-8"))
    return result


def load_by_id(base_dir: Path, id_: str) -> tuple[Path, ReqDocument]:
    """Resolve ``id_`` under ``base_dir`` and read the matching requirement.

    Parameters
    ----------
    base_dir:
        The directory to scan for ``*.md`` files.
    id_:
        The id to look up.

    Returns
    -------
    tuple[Path, ReqDocument]
        The resolved file path and the parsed document -- callers that
        mutate the document need the path to write it back afterward.

    Raises
    ------
    ReqNotFoundError
        If no file matches (propagated from :func:`._paths.find_req_path`).
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(id_, str), type(id_)
    assert id_.strip()

    path = find_req_path(base_dir, id_)
    result = (path, read_req(path))
    return result
