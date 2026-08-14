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

"""Private, dependency-free repo-root-relative path constants.

This module imports nothing beyond the standard library (``pathlib``), so
both the ``cli`` extra (``commands/schema.py``, ``commands/docs.py``, ...)
and the ``mcp`` extra (e.g. ``req/resources/req_schema.py``) can share it
without either extra's optional dependencies (``typer``, ``mcp``) leaking
into the other's import graph -- unlike importing ``commands.schema``
directly (pulls in ``typer``) or the ``general`` package (whose
``__init__.py`` side-effect-imports ``mcp``-dependent tools).

``REPO_ROOT``/``DOCS_DIR`` only resolve correctly when this package is used
from an editable/source checkout (the layout ``uv run`` and CI use) -- a
built, non-editable installation (e.g. a plain ``pip install`` from PyPI)
does not ship ``docs/`` as package data, so climbing from ``__file__``
would land somewhere inside ``site-packages`` with no ``docs/`` directory
at all. This is an accepted, currently-out-of-scope limitation (see
`.specmgr/feat/feat-6-requirement-artifact/README.md`'s Decisions Made) --
every current caller of ``DOCS_DIR`` is either a dev/CI-only CLI command or
a resource whose backing file is guaranteed present at build time.
"""

from __future__ import annotations

from pathlib import Path

# __file__ = src/biz/dfch/specmgr/_paths.py
_SPECMGR_ROOT = Path(__file__).resolve().parent  # src/biz/dfch/specmgr

#: The repository root, four directories above this package
#: (``specmgr`` -> ``dfch`` -> ``biz`` -> ``src`` -> repo root).
REPO_ROOT = _SPECMGR_ROOT.parent.parent.parent.parent

#: The repo's ``docs/`` directory, holding generated artifacts
#: (``docs/api/``, ``docs/adr/README.md``, ``docs/req_schema.json``, ...).
DOCS_DIR = REPO_ROOT / "docs"

__all__ = ["DOCS_DIR", "REPO_ROOT"]
