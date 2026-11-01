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
the variable's own name constant, its import-time registration in the
central env-var registry, plus the int parse with fallback + validity
flag. The read goes through ``biz.dfch.specmgr._envregistry`` -- the
import-free top-level registry (the import-chain constraint is why the
registry is top-level, not under ``general/tools/``; see the registry's
own module docstring) -- and the Phase 120 MCP tools and the Phase 130
CLI both call :func:`diagram_max_title`; the pure renderer
(``general.models.reference_graph.render_reference_graph``) takes the
limit as a plain ``max_label`` parameter and never reads the env var
itself.

:func:`diagram_max_title` resolves the value through the registry's
``get_with_default`` accessor (an unset value falls back to the record's
registered default, "40"), then applies the int parse with fallback +
validity flag: set-but-invalid values (empty, non-int, or < 1) fall back
to the default 40 with a validity flag ``False`` -- the flag is surfaced
by the ``specmgr://config`` ``diagram`` section (Phase 120). The
``server.json`` manifest entry for the variable must travel with this
first read site (``tests/test_server_json.py``'s drift test enforces
manifest coverage of every ``SPECMGR_*`` read in ``src/``, and
``tests/test_envregistry_coverage.py`` pins the manifest's ``default``/
``format`` against the registry record).

Plain Python, no ``mcp`` import (like ``plantuml/chain.py``) --
independently testable by pinning the process environment.
"""

from __future__ import annotations

from ... import _envregistry
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

# The registry record for :data:`ENV_VAR_DIAGRAM_MAX_TITLE` (the feat-208
# dev sync; the read site below migrated to the registry accessor in the
# same step): the central env-var registry is the single authority for the
# variable's default and its ``server.json`` manifest ``format`` (the
# description tracks the manifest verbatim, like every other ``SPECMGR_*``
# record). ``empty_falls_back_to_default`` is False: a set-but-empty value
# is one of the set-but-invalid cases (handled by :func:`diagram_max_title`'s
# own parse-fallback with the validity flag), not an empty-fallback-to-
# default read.
_envregistry.register(
    ENV_VAR_DIAGRAM_MAX_TITLE,
    default="40",
    description=(
        "Maximum length (in characters) of a resolved node's title label in the reference-graph diagrams "
        "(the get_reference_diagram / get_reference_diagram_all MCP tools and the specmgr diagram refs CLI): "
        "labels longer than the limit are cut at the last word boundary within the limit (a hard cut when "
        "there is none) with an ellipsis appended; the diagram title itself and unresolved node ids are "
        "never truncated. An integer; the default 40 applies when the variable is unset or set to an "
        "invalid value (empty, non-integer, or less than 1)."
    ),
    owner="general",
    format="number",
)

#: The default label limit (rulebook §5.2 -- shared with the pure renderer
#: as its own ``DEFAULT_MAX_LABEL`` constant, the single source of truth for
#: the value; set-but-invalid env values fall back to it).
DEFAULT_MAX_TITLE = DEFAULT_MAX_LABEL

#: The minimum valid label limit (rulebook §5.2: a set-but-invalid value is
#: empty, non-int, or < 1).
_MIN_VALID_LIMIT = 1


def diagram_max_title() -> tuple[int, bool]:
    """Read ``SPECMGR_DIAGRAM_MAX_TITLE`` into the effective label limit + a validity flag (rulebook §5.2).

    The value read goes through the central env-var registry's
    ``get_with_default`` accessor (the registry record's own default is
    "40", so an unset value resolves to the default before the parse
    below; a set-but-empty value stays set, since the record's
    ``empty_falls_back_to_default`` flag is False -- the empty string is
    one of the set-but-invalid cases, not an empty-fallback). Unset ⇒
    ``(40, True)`` (the default, valid). Set-but-invalid (empty string,
    non-int, or < 1) ⇒ ``(40, False)`` (the fallback with the invalidity
    flag -- surfaced by the ``specmgr://config`` ``diagram`` section,
    Phase 120). A valid int N ⇒ ``(N, True)``.

    Returns
    -------
    tuple[int, bool]
        ``(effective limit, valid)`` -- the int the renderer's
        ``max_label`` parameter must be called with, plus whether the
        environment value (when set) actually determined it.
    """
    value = _envregistry.get_with_default(ENV_VAR_DIAGRAM_MAX_TITLE)
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
