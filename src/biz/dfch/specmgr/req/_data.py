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

"""Private, dependency-free access to REQ's packaged example markdown (Task 3.6).

Unlike ``docs/req_schema.json`` (read via ``biz.dfch.specmgr._paths.DOCS_DIR``,
which only resolves correctly from an editable/source checkout), the file this
module reads is shipped as real *package data* -- declared under
``[tool.setuptools.package-data]`` for ``biz.dfch.specmgr.req.resources`` and
loaded via :mod:`importlib.resources` -- so its presence is a genuine
build-time guarantee that survives a real, non-editable ``pip install`` too,
not just a dev checkout.

Kept in a neutral module directly under ``req/`` (not under ``req/tools/`` or
``req/resources/``) so neither of those two sub-packages has to import from
the other just to share this one file read -- both ``req.tools.get_req_example``
and ``req.resources.req_example`` import this module directly, mirroring the
top-level ``_paths.py``'s own "shared, dependency-free" role.

Only imports the standard library (``importlib.resources``), so importing this
module never pulls in the ``cli``/``mcp`` extras.
"""

from __future__ import annotations

from importlib import resources
from importlib.resources.abc import Traversable

#: Anchor package for the packaged example data -- ``req/resources/data/``
#: is real package data (declared in ``pyproject.toml``'s
#: ``[tool.setuptools.package-data]``), not a Python sub-package.
_DATA_PACKAGE = "biz.dfch.specmgr.req.resources"

#: The packaged, build-guaranteed REQ example markdown file. A plain
#: module-level constant (like ``req.resources.req_schema``'s
#: ``_REQ_SCHEMA_PATH``) so tests can patch it directly with
#: ``mock.patch.object`` to point at a temporary file.
_EXAMPLE_PATH: Traversable = resources.files(_DATA_PACKAGE) / "data" / "req_example.md"


def read_req_example_text() -> str:
    """Return the packaged REQ example's full markdown text, verbatim.

    Reads the file fresh on every call (no in-memory cache, consistent with
    every other resource/tool in this codebase). The file's presence is a
    build-time guarantee (declared package data, not user-authored content
    living elsewhere), so a missing or corrupted file is a hard, uncaught
    failure -- there is no defensive handling here.

    Returns
    -------
    str
        The example document's raw markdown source, including its YAML
        frontmatter block, exactly as committed on disk.

    Raises
    ------
    FileNotFoundError
        If the packaged example file is missing (should never happen outside
        a broken installation).
    """
    result: str = _EXAMPLE_PATH.read_text(encoding="utf-8")
    return result
