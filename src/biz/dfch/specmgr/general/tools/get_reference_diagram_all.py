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

# pylint: disable=duplicate-code  # the title-override + label-limit + render tail mirrors get_reference_diagram
# (one module per tool; update.py's thirteen near-identical per-domain adapters are the house precedent)

"""``@mcp.tool()`` wrapper: get_reference_diagram_all (feat-207-reference-graph, Phase 120, REQ-005).

Read-only, registry-wide diagram tool: the deterministic PlantUML component
diagram of the whole reference registry (rulebook
``specmgr://reference-graph`` / ``general/data/general_reference_graph.md``
§2–§5, the registry-wide construction of §3.3): one node per parseable
document across all 14 domains (broken documents are skipped -- the render
never fails for content, the ``get_use_case_package_diagram`` precedent),
one label-free edge per unique extracted reference (``{src} --> {dst}`` --
the referenced item carries the incoming arrow), every edge lying on a
cycle (SCC-based) drawn with the red label-free ``-[#red]->`` arrow (the
2026-10-15 correction -- the edges carry no label), and every reference
whose target cannot be resolved on disk drawn as a top-level
``<<UNRESOLVED>>`` node. Labels (the node H1s) are truncated to the
``SPECMGR_DIAGRAM_MAX_TITLE`` env var's effective value (the shared
``_diagram_config.diagram_max_title`` helper; default 40) -- the diagram
title is sanitized but never truncated.

Thin over the Phase 110 library (``_reference_graph.
build_registry_graph`` + ``reference_graph.render_reference_graph``): this
module adds only the ``title`` override (replaces the graph's title before
rendering; the frozen default is ``Reference Graph``) and the ``max_label``
read. There are no id guards (there is no id), and the tool never raises
for content -- a broken document anywhere in the registry is simply absent
from the diagram, and so is a document that vanishes mid-build between the
scan's parse leg and the builder's own extraction legs (the ``body_text``
re-reads; the builders' own ``FileNotFoundError`` skips -- the
``_reference_graph`` module docstring's vanished-mid-build rule).
"""

from __future__ import annotations

from dataclasses import replace

from ...general.models.reference_graph import ReferenceGraph, render_reference_graph
from ...general.tools._diagram_config import diagram_max_title
from ...general.tools._reference_graph import build_registry_graph
from ...server import mcp

__all__ = ["get_reference_diagram_all"]


@mcp.tool(
    name="get_reference_diagram_all",
    title="Get the registry-wide reference diagram",
    description=(
        "Render and return the deterministic PlantUML component diagram of the whole reference "
        "registry (the frozen rulebook specmgr://reference-graph §2–§5, the registry-wide "
        "construction of §3.3): one node per parseable document across all 14 domains (broken "
        "documents are skipped -- the render never fails for content), one label-free edge per "
        "unique reference (`{src} --> {dst}`, the referenced item carries the incoming arrow), "
        "every edge lying on a cycle (SCC-based) drawn with the red label-free `-[#red]->` "
        "arrow, and every reference whose target cannot be resolved on disk drawn as a "
        "top-level `<<UNRESOLVED>>` node. Node labels are truncated to SPECMGR_DIAGRAM_MAX_TITLE "
        "(default 40). `include_feat=False` drops every FEAT node (then every edge touching a "
        "dropped "
        "node); `title` overrides the diagram title (default: `Reference Graph`; sanitized but "
        "never truncated). Returns PlantUML source (not a specmgr document) -- run it through "
        "`specmgr plantuml-check` (CLI) or the `validate_plantuml` tool for a validation verdict."
    ),
)
def get_reference_diagram_all(include_feat: bool = True, title: str | None = None) -> str:
    """Render and return the PlantUML reference diagram of the whole registry.

    The registry-wide construction (rulebook §3.3): the same full 14-domain
    scan the scoped tool's ``reverse`` pass uses -- every successfully
    parsed document is a node (its H1 as the label), every extracted
    reference an edge, and a target not present as a scanned document gets
    its title via the shared target resolution (dangling ⇒ the unresolved
    node). Broken documents are skipped (never a node, never an edge
    source; the render never fails for content), and documents vanishing
    mid-build on the builder's extraction legs (the ``body_text`` re-reads)
    are skipped the same way (the ``_reference_graph`` module docstring's
    vanished-mid-build rule). There are no id guards (there is no id): the
    only inputs are the ``include_feat`` switch and the optional ``title``
    override, so this tool never raises for content -- it always returns
    the diagram.

    The FEAT exclusion (``include_feat=False``, rulebook §3.5) is applied
    last: drop every FEAT node, then every edge touching a dropped node.
    The diagram title is the ``title`` override when given (sanitized but
    never truncated by the renderer), else the frozen ``Reference Graph``
    default. The resolved-node label limit is the ``SPECMGR_DIAGRAM_MAX_TITLE``
    env var via the shared ``_diagram_config.diagram_max_title`` helper
    (default 40; a set-but-invalid value falls back to 40 -- the
    ``specmgr://config`` ``diagram`` section reports its set/valid/default/
    resolved status).

    Parameters
    ----------
    include_feat:
        When ``False``, apply the FEAT exclusion (rulebook §3.5) last: drop
        every FEAT node, then every edge touching a dropped node.
    title:
        An optional diagram-title override (sanitized but never truncated);
        when ``None``, the frozen ``Reference Graph`` default.

    Returns
    -------
    str
        The byte-stable PlantUML source (``@startuml …`` through
        ``@enduml``, one trailing newline).
    """
    graph: ReferenceGraph = build_registry_graph(include_feat=include_feat)
    if title is not None:
        graph = replace(graph, title=title)
    max_label, _valid = diagram_max_title()
    result: str = render_reference_graph(graph, max_label=max_label)
    return result
