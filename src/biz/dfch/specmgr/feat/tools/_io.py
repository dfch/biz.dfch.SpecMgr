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

``read_feat`` itself now lives in ``._cache`` (feat-107-doc-cache Phase 4,
Task 4.1a) -- it is re-exported here unchanged (same name, same signature)
so every existing external caller (e.g. ``feat.tools.list_feat``'s
``from ._io import read_feat``) keeps working with zero changes to its own
import line. See ``._cache``'s module docstring for why ``read_feat`` had
to move out of this module in the first place (avoiding a circular import
between ``_io.py`` and ``_paths.py``) and for the module-level cache
singleton it now reads through.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from ..models.v1 import FeatDocument
from ._cache import read_feat
from ._paths import FeatNotFoundError, find_feat_path_by_id

__all__ = ["load_by_id", "read_feat"]


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
        If no folder matches (propagated from :func:`._paths.find_feat_path_by_id`),
        or if ``path`` -- already resolved successfully by
        :func:`._paths.find_feat_path_by_id` an instant earlier -- vanishes
        out from under this function's own subsequent :func:`._cache.read_feat`
        call, racing a concurrent ``set_feat_id`` rename in the same narrow
        window :func:`._paths.find_feat_path_by_id`'s own docstring describes
        (feat-107-doc-cache Phase 6, REQ-012): this second, independent read
        has exactly the same ``FileNotFoundError`` exposure as the first one
        does, and is translated into the same :class:`._paths.FeatNotFoundError`
        here rather than left to propagate uncaught.
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(id_, str), type(id_)
    assert id_.strip()

    path = find_feat_path_by_id(base_dir, id_)
    try:
        doc = read_feat(path)
    except (AssertionError, ValidationError, FileNotFoundError) as ex:
        raise FeatNotFoundError(
            f"feature folder {id_!r} exists at {path}, but its content could not be read as a valid "
            f"feature document on this second read ({type(ex).__name__}: {ex})."
        ) from ex
    result = (path, doc)
    return result
