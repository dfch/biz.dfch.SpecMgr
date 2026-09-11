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

"""Thin file read helpers over ``parse_gol`` (feat-107-doc-cache Phase 4).

Read-only, mirroring ``req.tools._io`` exactly: there is no
``write_gol``/``render_gol`` counterpart here, since ``create_gol`` and the
generic ``update`` tool in ``general.tools`` persist the caller's
already-validated body markdown byte-for-byte rather than rendering it back
out from a parsed model -- no renderer is needed for that shape, so none is
added speculatively here.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.

``read_gol`` itself now lives in ``._cache`` (feat-107-doc-cache Phase 4) --
it is re-exported here unchanged (same name, same signature) so every
existing external caller (e.g. ``gol.tools.list_gol``'s
``from ._io import read_gol``) keeps working with zero changes to its own
import line. See ``._cache``'s module docstring for why ``read_gol`` had to
move out of this module in the first place (avoiding a circular import
between ``_io.py`` and ``_paths.py``) and for the module-level cache
singleton it now reads through.

**The second, independent ``read_gol`` call is also guarded against a
vanished file (feat-107-doc-cache Phase 8, REQ-015).** :func:`load_by_id`
calls ``read_gol(path)`` again immediately after ``find_gol_path`` already
resolved and read the same ``path`` once during its own scan. The generic
``delete`` tool in ``general.tools`` only holds the *target* document's own
per-id lock, never a whole-domain lock, while ``get_gol``/``list_gol``
intentionally take no lock at all (ADR
33c5ab08-ff58-4c73-8c32-23abaf3838e3) -- so a concurrent ``delete`` of this
same document can remove ``path`` in the narrow window between
``find_gol_path``'s own read and this one, raising ``FileNotFoundError``.
This mirrors ``feat.tools._io.load_by_id``'s already-shipped shape exactly
(the identical race, closed there in Phase 6 for REQ-012's narrower,
rename-only claim): ``AssertionError``/``pydantic.ValidationError``/
``yaml.YAMLError``/``FileNotFoundError`` around this second read are all
translated into :class:`._paths.GolNotFoundError` here, rather than left to
propagate uncaught.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from ..models.v1 import GolDocument
from ._cache import read_gol
from ._paths import GolNotFoundError, find_gol_path

__all__ = ["load_by_id", "read_gol"]


def load_by_id(base_dir: Path, id_: str) -> tuple[Path, GolDocument]:
    """Resolve ``id_`` under ``base_dir`` and read the matching goal.

    Parameters
    ----------
    base_dir:
        The directory to scan for ``*.md`` files.
    id_:
        The id to look up.

    Returns
    -------
    tuple[Path, GolDocument]
        The resolved file path and the parsed document -- callers that
        mutate the document need the path to write it back afterward.

    Raises
    ------
    GolNotFoundError
        If no file matches (propagated from :func:`._paths.find_gol_path`),
        or if ``path`` -- already resolved successfully by
        :func:`._paths.find_gol_path` an instant earlier -- fails this
        function's own second, independent :func:`._cache.read_gol` call
        (``AssertionError``/``pydantic.ValidationError``/``yaml.YAMLError``/
        ``FileNotFoundError``, feat-107-doc-cache Phase 8, REQ-015 -- e.g. a
        concurrent ``delete`` tool call racing this lock-free read, the
        same race class ``feat.tools._io.load_by_id`` already guards
        against).
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(id_, str), type(id_)
    assert id_.strip()

    path = find_gol_path(base_dir, id_)
    try:
        doc = read_gol(path)
    except (AssertionError, ValidationError, yaml.YAMLError, FileNotFoundError) as ex:
        raise GolNotFoundError(
            f"goal {id_!r} exists at {path}, but its content could not be read as a valid "
            f"goal document on this second read ({type(ex).__name__}: {ex})."
        ) from ex
    result = (path, doc)
    return result
