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

"""Thin file read helpers over ``parse_feat`` (Task 2.2).

Read-only, mirroring ``dec.tools._io``'s own shape and rationale: there is
no ``write_feat``/``render_feat`` counterpart here, since ``create_feat``
and the generic ``update`` tool in ``general.tools`` (``type="feat"``)
persist the caller's own already-validated body markdown byte-for-byte
rather than rendering it back out from a parsed model -- see
``feat.tools._write.write_feat_file``.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any ``@mcp.tool()``-decorated function so they stay
independently testable.
"""

from __future__ import annotations

from pathlib import Path

from ..models.v1 import FeatDocument, parse_feat
from ._paths import find_feat_path_by_id

__all__ = ["load_by_id", "read_feat"]


def read_feat(path: Path) -> FeatDocument:
    """Read and parse the feature document at ``path``.

    Parameters
    ----------
    path:
        The filesystem path to the feature's ``README.md`` file.

    Returns
    -------
    FeatDocument
        The parsed, validated document.
    """
    assert isinstance(path, Path), type(path)

    result = parse_feat(path.read_text(encoding="utf-8"))
    return result


def load_by_id(base_dir: Path, id_: str) -> tuple[Path, FeatDocument]:
    """Resolve ``id_`` under ``base_dir`` and read the matching feature document.

    Parameters
    ----------
    base_dir:
        The feature base directory (typically :func:`._paths.feat_base_dir`'s
        return value).
    id_:
        The id to look up.

    Returns
    -------
    tuple[Path, FeatDocument]
        The resolved ``README.md`` path and the parsed document -- callers
        that mutate the document need the path to write it back afterward.

    Raises
    ------
    FeatNotFoundError
        If no folder matches (propagated from :func:`._paths.find_feat_path_by_id`).
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(id_, str), type(id_)
    assert id_.strip()

    path = find_feat_path_by_id(base_dir, id_)
    result = (path, read_feat(path))
    return result
