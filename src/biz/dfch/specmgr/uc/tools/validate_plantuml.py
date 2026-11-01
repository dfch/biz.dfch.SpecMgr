# Copyright (C) 2026 Ronald Rink, http://d-fens.ch
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

"""``@mcp.tool()`` wrapper: validate_plantuml (feat-185-uc-diagrams, Phase 120).

Direct, thin wrapper over ``plantuml.chain.validate_plantuml`` (Phase 110)
-- the strict first-set-wins validation chain (rulebook
``specmgr://uc/plantuml`` §3: structure pre-flight always, then the single
configured source -- ``SPECMGR_PLANTUML_JAR`` → ``SPECMGR_PLANTUML_BIN`` →
``SPECMGR_PLANTUML_URL``, no fall-through; the all-unset state is the
structure-only floor). The returned ``PlantumlValidationResult`` is the
frozen §3.6 non-raising result model (the ADR 519d1206 chain precedent) --
a dataclass the MCP SDK serializes directly; this wrapper adds no state of
its own. Content-based: the caller passes the diagram text (the Phase 130
CLI reads the file and passes its text).
"""

from __future__ import annotations

from ... import _envregistry
from ...plantuml import chain
from ...plantuml.chain import ENV_VAR_BIN, ENV_VAR_JAR, ENV_VAR_URL, PlantumlValidationResult
from ...server import mcp

# The PlantUML validation-source trio, registered by this uc-domain
# consumer (feat-208, Phase 110): the import-free ``plantuml/`` package
# itself (ADR 7a626b12) cannot register them, so its uc-domain consumer
# that imports ``plantuml.chain`` does -- the names come from
# ``chain.py``'s own ``ENV_VAR_*`` constants (never a second hardcoded
# copy), and the trio's read sites in ``plantuml/chain.py`` keep their
# direct ``os.environ`` reads (the import-free carve-out; the registry is
# the single source of truth for the documentation-tracking tests, not for
# the reads). Presence-based, no defaults, no empty-fallback: the
# first-set-wins selection semantics (rulebook §3.2) are unchanged.
_envregistry.register(
    ENV_VAR_JAR,
    description=(
        "Path to a plantuml.jar, one of exactly three PlantUML validation-source selectors (the first "
        "one set, in JAR then BIN then URL order, is the only source used; no fall-through, no PATH "
        "discovery, no public default; all three unset is the offline structure-only floor). Unset by "
        "default. The selected source is reported by the plantuml section of the specmgr://config "
        "resource."
    ),
    owner="plantuml/uc",
)
_envregistry.register(
    ENV_VAR_BIN,
    description=(
        "Path to an executable speaking the PlantUML CLI contract, one of exactly three PlantUML "
        "validation-source selectors (the first one set, in JAR then BIN then URL order, is the only "
        "source used; no fall-through, no PATH discovery, no public default; all three unset is the "
        "offline structure-only floor). Unset by default. The selected source is reported by the "
        "plantuml section of the specmgr://config resource."
    ),
    owner="plantuml/uc",
)
_envregistry.register(
    ENV_VAR_URL,
    description=(
        "PlantUML server base URL, one of exactly three PlantUML validation-source selectors (the "
        "first one set, in JAR then BIN then URL order, is the only source used; no fall-through, no "
        "PATH discovery, no public default; all three unset is the offline structure-only floor). "
        "Diagram content is only sent to a PlantUML server if this variable is set. Unset by default. "
        "The selected source is reported by the plantuml section of the specmgr://config resource."
    ),
    owner="plantuml/uc",
)


@mcp.tool(
    name="validate_plantuml",
    title="Validate PlantUML diagram text",
    description=(
        "Validate PlantUML diagram text through the strict validation chain (the frozen rulebook "
        "specmgr://uc/plantuml §3): the structure check always runs first (on a structure red the "
        "parser is never called -- no subprocess, no network), then the single configured source "
        "(the first set of SPECMGR_PLANTUML_JAR/SPECMGR_PLANTUML_BIN/SPECMGR_PLANTUML_URL; no "
        "fall-through -- a set-but-unavailable source is a hard failure with reason + fix hint), "
        "and the all-unset state degrades to the structure-only floor. A PlantUML server crash "
        "page (200 + the embedded Java-exception trace -- the recognised 1.2026.8 crash line of "
        "the rulebook §5.2 matrix, the known self-message/note-left shape bug) is a recognised "
        "INVALID row: valid=false with the line-0 crash finding carrying the exception class and "
        "a fix hint pointing at the rulebook §2.9 anchored notes. Content-based: pass the diagram "
        "text (a CLI reads the file and passes its text). Never raises for validation content -- "
        "returns the non-raising §3.6 result model: structure_ok, valid/rendered (None = not run, "
        "never run-and-failed), checked_by (jar/bin/url/structure), errors and warnings (1-based "
        "line + message + fix hint), source_state (ok/misconfigured/unavailable/inconclusive/"
        "none), available, reason, fix_hint."
    ),
)
def validate_plantuml(text: str) -> PlantumlValidationResult:
    """Validate one PlantUML diagram's text through the strict chain.

    Parameters
    ----------
    text:
        The full diagram source (``@startuml ...`` through ``@enduml``).
        Content-based by design -- a CLI reads the file and passes its text.

    Returns
    -------
    PlantumlValidationResult
        The frozen §3.6 result model (non-raising): ``structure_ok`` plus
        ``valid``/``rendered`` (``None`` = "not run"), ``checked_by``,
        ``errors``/``warnings`` (1-based line + message + fix hint),
        ``source_state``, ``available``, ``reason``, ``fix_hint``. On a
        structure-red short-circuit (§3.7) the parser is never called
        (no subprocess, no network); on the all-unset floor (§3.4) only
        the structure checker runs; with a configured source, a
        set-but-unavailable one is a hard failure (no fall-through,
        rulebook §3.3).
    """
    result = chain.validate_plantuml(text)
    return result
