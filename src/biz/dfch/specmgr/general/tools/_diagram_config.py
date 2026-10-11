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

"""The ``SPECMGR_DIAGRAM_MAX_TITLE`` env-var helper (feat-207-reference-graph, Phase 110, REQ-008).

The shared read site for the reference-graph label limit (rulebook §5.2):
the ``plantuml/chain.py`` ``ENV_VAR_*`` + ``os.environ.get`` idiom, plus the
new int parse with fallback + validity flag. The Phase 120 MCP tools and
the Phase 130 CLI both call :func:`diagram_max_title` -- the pure renderer
(``general.models.reference_graph.render_reference_graph``) takes the limit
as a plain ``max_label`` parameter and never reads the env var itself.

Set-but-invalid values (empty, non-int, or < 1) fall back to the default
40 with a validity flag ``False`` -- the flag is surfaced by the
``specmgr://config`` ``diagram`` section (Phase 120). The ``server.json``
manifest entry for the variable must travel with this first read site
(``tests/test_server_json.py``'s drift test enforces manifest coverage of
every ``SPECMGR_*`` read in ``src/``).

Plain Python, no ``mcp`` import (like ``plantuml/chain.py``) --
independently testable by pinning the process environment.
"""

from __future__ import annotations

import os

from ..models.reference_graph import DEFAULT_MAX_LABEL

__all__ = [
    "DEFAULT_MAX_TITLE",
    "ENV_VAR_DIAGRAM_MAX_TITLE",
    "diagram_max_title",
]

#: The ``SPECMGR_DIAGRAM_MAX_TITLE`` environment variable name (rulebook
#: §5.2). The single read site this module's constant feeds
#: (:func:`diagram_max_title`); the ``server.json`` manifest entry must
#: cover it (the feat-126 drift test).
ENV_VAR_DIAGRAM_MAX_TITLE = "SPECMGR_DIAGRAM_MAX_TITLE"

#: The default label limit (rulebook §5.2 -- shared with the pure renderer
#: as its own ``DEFAULT_MAX_LABEL`` constant, the single source of truth for
#: the value; set-but-invalid env values fall back to it).
DEFAULT_MAX_TITLE = DEFAULT_MAX_LABEL

#: The minimum valid label limit (rulebook §5.2: a set-but-invalid value is
#: empty, non-int, or < 1).
_MIN_VALID_LIMIT = 1


def diagram_max_title() -> tuple[int, bool]:
    """Read ``SPECMGR_DIAGRAM_MAX_TITLE`` into the effective label limit + a validity flag (rulebook §5.2).

    Unset ⇒ ``(40, True)`` (the default, valid). Set-but-invalid (empty
    string, non-int, or < 1) ⇒ ``(40, False)`` (the fallback with the
    invalidity flag -- surfaced by the ``specmgr://config`` ``diagram``
    section, Phase 120). A valid int N ⇒ ``(N, True)``.

    Returns
    -------
    tuple[int, bool]
        ``(effective limit, valid)`` -- the int the renderer's
        ``max_label`` parameter must be called with, plus whether the
        environment value (when set) actually determined it.
    """
    value = os.environ.get(ENV_VAR_DIAGRAM_MAX_TITLE)
    if value is None:
        result: tuple[int, bool] = (DEFAULT_MAX_TITLE, True)
        return result
    try:
        parsed = int(value)
    except ValueError:
        result = (DEFAULT_MAX_TITLE, False)
        return result
    if parsed < _MIN_VALID_LIMIT:
        result = (DEFAULT_MAX_TITLE, False)
        return result
    result = (parsed, True)
    return result
