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

"""Feature (FEAT) domain -- formalizes the ``.specmgr/feat/<id>/README.md`` convention.

Per ADR e369ee2e-3353-4f92-991c-6367d76d832e ("Organize development
artifacts in ``.specmgr`` with feature-driven work units") and
``.specmgr/feat/feat-31-feature/README.md``, this domain-first package
(ADR ece4554b-725c-4f76-bc04-5d2b760363d2) formalizes a convention already
used by hand 17+ times before this package existed. ``feat`` is deliberately
special among domains: ``id`` is ``feat-NNN-slug`` (the containing folder's
own name), not a server-generated UUID, and documents live one-per-folder
as ``<base>/<id>/README.md`` (a fixed filename), not flat files directly
under the base directory -- see ``feat/tools/_paths.py`` (added in Phase 2)
for the bespoke addressing this requires, in contrast to every other
domain's shared ``general/tools/_doc_paths.py``.

**Current status: Phase 2 (tools) complete.** ``models/v1/`` (Phase 1) and
``tools/`` (Phase 2) are fully implemented; ``resources`` and ``prompts``
remain empty sub-packages, built out in Phases 3-4 of the linked feature
plan. ``feat`` already follows the ``sop``-style generic-dispatch MCP
surface (ADR 36905d5b-8057-4294-8665-c7eed5534db0): ``create_feat``,
``parse_feat``, ``list_feat``, ``get_feat``, ``get_feat_example``,
``get_feat_template``, ``delete_feat`` (stub), ``validate_feat``, plus
``type="feat"`` entries in the generic ``update``/``set_status`` tools --
no ``update_feat``/``set_status_feat`` of its own.

Import this package to register every feature tool/prompt/resource against
the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import feat  # noqa: F401 (side-effects only)
"""

from . import prompts, resources, tools  # noqa: F401

__all__ = [
    "prompts",
    "resources",
    "tools",
]
