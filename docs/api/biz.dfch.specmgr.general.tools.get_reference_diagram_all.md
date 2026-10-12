# `biz.dfch.specmgr.general.tools.get_reference_diagram_all`

``@mcp.tool()`` wrapper: get_reference_diagram_all (feat-207-reference-graph, Phase 120, REQ-005).

Read-only, registry-wide diagram tool: the deterministic PlantUML component
diagram of the whole reference registry (rulebook
``specmgr://reference-graph`` / ``general/data/general_reference_graph.md``
§2–§5, the registry-wide construction of §3.3): one node per parseable
document across all 13 domains (broken documents are skipped -- the render
never fails for content, the ``get_use_case_package_diagram`` precedent),
one edge per unique extracted reference (``{src} --> {dst} : refers to`` --
the referenced item carries the incoming arrow), every edge lying on a
cycle (SCC-based) drawn with the red ``-[#red]->`` arrow, and every
reference whose target cannot be resolved on disk drawn as a top-level
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

## Functions

### `get_reference_diagram_all(include_feat: 'bool' = True, title: 'str | None' = None) -> 'str'`

Render and return the PlantUML reference diagram of the whole registry.

The registry-wide construction (rulebook §3.3): the same full 13-domain
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

