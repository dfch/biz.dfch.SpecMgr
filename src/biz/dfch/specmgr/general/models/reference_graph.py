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

"""The frozen reference-graph model + the deterministic PlantUML renderer (feat-207-reference-graph,
Phase 110, REQ-001/REQ-003).

Pure and **stdlib-only** (the import-free bar of the ``plantuml/`` package, ADR
7a626b12): no ``mcp``, no ``general.tools`` imports, no third-party dependency.
It holds the three frozen fact dataclasses the graph builders
(``general.tools._reference_graph``) and the hand-built test graphs share,
plus the one pure function that turns a :class:`ReferenceGraph` into the
frozen PlantUML component-diagram source of the reference-graph rulebook
(``specmgr://reference_graph`` / ``general/data/general_reference_graph.md`` §2):

- :class:`GraphNode` -- one artifact: its lowercase domain ``type``, its
  verbatim ``id`` (canonical lowercase-hex uuid for the 12 UUID domains, the
  full ``feat-NNN-slug`` or the bare ``feat-NNN`` for ``feat``), and its
  resolved title (the document's H1 as the builders derive it) or ``None``
  for a reference that could not be resolved on disk (the unresolved node
  of rulebook §2.6).
- :class:`GraphEdge` -- one unique reference: the (source, target) pair of
  ``(type, id)`` keys (the referenced item carries the incoming arrow).
- :class:`ReferenceGraph` -- the diagram's title (the scoped source's H1 or
  the registry-wide ``Reference Graph`` default, or a caller override) plus
  the node and edge collections.
- :func:`render_reference_graph` -- the frozen layout (rulebook §2.1–§2.8):
  the ``@startuml {title}`` line (sanitised, **never truncated**, §2.2/§5),
  the full 14-entry skinparam colour block (always, in block order, §2.5),
  the ``left to right direction`` line, the top-level unresolved node lines
  (sorted by alias, §2.6), one ``package "TYPE"`` … ``end package`` per
  non-empty domain (in the 13-domain order, nodes sorted by id, §2.7), and
  the deduped + sorted edge lines (uniform ``: refers to`` label, the red
   ``-[#red]->`` form on cycle edges only, §2.8/§4). The content sections
   (the ``@startuml`` line, the skinparam block, the direction line, the
   top-level unresolved node lines, each non-empty package, and the edge
   section) are separated by exactly one blank line, an empty section is
   omitted entirely, ``@enduml`` follows the last non-empty section
   directly, and the source ends with exactly one trailing newline (§2.1,
   corrected 2026-10-11).

Cycle detection (REQ-003, rulebook §4): an edge lies on a cycle iff it is a
self-loop or both endpoints belong to the same strongly connected component
of size ≥ 2. Computed here by an **iterative** Tarjan (stdlib, deterministic
node order) -- the model stays pure facts, and the recursion-free walk keeps
large registry graphs off Python's recursion limit.

Label rules (rulebook §2.4/§5): a resolved node's label is its title,
sanitised (embedded ``"`` → ``#quot;``, a literal newline → the two-character
sequence ``\\n`` — the UC rulebook §2.4 conventions, reused as-is) and
truncated to ``max_label`` (if ``len(label) > N``: ``candidate = label[:
N-1]``, cut at the candidate's last space if any (else a hard cut), append
``…`` — the result is ≤ N characters; exactly-N labels are untouched). An
unresolved node's label is its verbatim id, never truncated (and never
sanitised -- the extractor's own shape guards keep ids free of quotes and
newlines). The diagram title is sanitised but never truncated, and the
renderer takes ``max_label`` as a plain parameter -- it never reads the
``SPECMGR_DIAGRAM_MAX_TITLE`` env var itself (the shared
``general.tools._diagram_config`` helper does that for the tool/CLI layer,
keeping this module pure).
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

__all__ = [
    "DEFAULT_MAX_LABEL",
    "GraphEdge",
    "GraphNode",
    "ReferenceGraph",
    "render_reference_graph",
]

#: The default label limit (rulebook §5.2's default; the env var's own
#: default, which the ``general.tools._diagram_config`` helper shares as its
#: single source of truth). The renderer never reads the env var itself.
DEFAULT_MAX_LABEL = 40

#: The one non-UUID domain (rulebook §2.3): its alias is the verbatim
#: ``feat-NNN-slug``/``feat-NNN`` id (already type-prefixed and
#: registry-unique); every other domain takes the ``[TYPE-{id}]`` form.
_FEAT = "feat"

#: The frozen 13-domain package order (rulebook §2.7 -- ``ALL_DOMAINS``):
#: the one constant this pure module may not import from
#: ``general.tools._domains`` (the import-free bar); the drift is pinned by
#: ``tests/general/models/test_reference_graph.py``.
_DOMAIN_ORDER: tuple[str, ...] = (
    "adr",
    "req",
    "uc",
    "tsk",
    "qa",
    "prb",
    "gol",
    "rsk",
    "dec",
    "sop",
    "feat",
    "vcr",
    "sysrs",
)

#: The frozen 14-entry palette (rulebook §2.5), in the skinparam block's own
#: order (the 13 domain stereotypes, then ``UNRESOLVED``).
_PALETTE: tuple[tuple[str, str], ...] = (
    ("ADR", "LightYellow"),
    ("REQ", "LightBlue"),
    ("UC", "Pink"),
    ("TSK", "Honeydew"),
    ("QA", "LemonChiffon"),
    ("PRB", "LightCoral"),
    ("GOL", "Lavender"),
    ("RSK", "Orange"),
    ("DEC", "LightGreen"),
    ("SOP", "PowderBlue"),
    ("FEAT", "PaleTurquoise"),
    ("VCR", "Khaki"),
    ("SYSRS", "Thistle"),
    ("UNRESOLVED", "DarkRed"),
)

#: The frozen direction line (rulebook §2.1).
_DIRECTION = "left to right direction"

#: The two frozen arrow forms (rulebook §2.8/§4.3): the plain form for
#: off-cycle edges, the red form for on-cycle edges (the Phase 100
#: real-parser gate's retained candidate).
_PLAIN_ARROW = "-->"
_RED_ARROW = "-[#red]->"

#: The frozen uniform edge label (rulebook §2.8 -- per-type edge labels are
#: out of scope).
_EDGE_LABEL = ": refers to"

#: The frozen stereotype of an unresolved node (rulebook §2.6).
_UNRESOLVED_STEREOTYPE = "UNRESOLVED"

#: The frozen truncation marker (rulebook §5.2).
_ELLIPSIS = "…"


@dataclass(frozen=True)
class GraphNode:
    """One artifact of the reference graph (a pure fact, rulebook §1).

    Parameters
    ----------
    type:
        The artifact's lowercase domain name (one of the 13
        ``general.tools._domains.ALL_DOMAINS`` names for builder-produced
        graphs; the renderer accepts any string, placing a node whose type
        is outside the 13-domain order top-level, like unresolved nodes).
    id:
        The artifact's verbatim id: the canonical lowercase-hex uuid for the
        12 UUID domains, the full ``feat-NNN-slug`` id or the bare
        ``feat-NNN`` number for ``feat`` (the two spellings of one feature
        are two distinct nodes -- rulebook §3.7's inherited caveat).
    title:
        The artifact's resolved title (its H1, as the builders derive it --
        the feature's H1 with the ``Feature: `` prefix stripped for
        ``feat``), or ``None`` for a reference that could not be resolved on
        disk (the unresolved node of rulebook §2.6: top-level, verbatim-id
        label, ``<<UNRESOLVED>>`` stereotype).
    """

    type: str
    id: str
    title: str | None = None


@dataclass(frozen=True)
class GraphEdge:
    """One unique reference of the reference graph (a pure fact, rulebook §2.8).

    The referenced item carries the incoming arrow: ``source`` is the
    referring document, ``target`` the referenced one.

    Parameters
    ----------
    source_type:
        The referring document's lowercase domain name.
    source_id:
        The referring document's verbatim id.
    target_type:
        The referenced document's lowercase domain name.
    target_id:
        The referenced document's verbatim id, as it appeared in the source
        body (a dangling reference keeps its verbatim id -- the target
        resolves to the unresolved node's label).
    """

    source_type: str
    source_id: str
    target_type: str
    target_id: str


@dataclass(frozen=True)
class ReferenceGraph:
    """The full reference graph a renderer call emits (rulebook §1).

    Parameters
    ----------
    title:
        The diagram title: the caller's override, else the scoped source's
        H1 (``build_source_graph``) or ``Reference Graph``
        (``build_registry_graph``) -- sanitised but never truncated
        (rulebook §2.2) on the way to the ``@startuml`` line.
    nodes:
        The node facts, one per (type, id) key (the builders guarantee
        uniqueness; the renderer dedupes defensively, first occurrence
        wins, and auto-adds a ``title=None`` node for an edge endpoint the
        collection omits, so the emitted source is always checker-clean).
    edges:
        The edge facts (deduped + sorted by
        (source_type, source_id, target_type, target_id) at render time).
    """

    title: str
    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...]


def _sanitize(text: str) -> str:
    """Quote sanitisation (rulebook §5.1, the UC rulebook §2.4 convention): an embedded ``"`` becomes ``#quot;``.

    The structural double quotes PlantUML requires around a label are added
    *after* sanitisation and remain real ``"``.
    """
    assert isinstance(text, str), type(text)

    result = text.replace('"', "#quot;")
    return result


def _single_line(text: str) -> str:
    """Quote sanitisation + single-line escaping (rulebook §5.1, the UC rulebook §2.4 conventions).

    An embedded ``"`` becomes ``#quot;`` and a literal newline becomes the
    two-character sequence ``\\n`` (PlantUML's in-message line break), so
    the text emits on exactly one line (the ``@startuml`` title line and
    every component label).
    """
    assert isinstance(text, str), type(text)

    result = _sanitize(text).replace("\n", "\\n")
    return result


def _truncate(label: str, max_label: int) -> str:
    """Label truncation (rulebook §5.2, N = ``max_label``, label already sanitised).

    If ``len(label) > N``: ``candidate = label[:N-1]``; if ``candidate``
    contains a space, cut at its LAST space (dropping from that space on);
    else hard cut at ``candidate``; append ``…``. The result is ≤ N
    characters. Labels of exactly N characters (and shorter ones) are
    returned untouched.
    """
    assert isinstance(label, str), type(label)
    assert isinstance(max_label, int), type(max_label)
    assert max_label >= 1, max_label

    if len(label) <= max_label:
        result = label
        return result
    candidate = label[: max_label - 1]
    last_space = candidate.rfind(" ")
    if last_space != -1:
        candidate = candidate[:last_space]
    result = candidate + _ELLIPSIS
    return result


def _alias(type_: str, id_: str) -> str:
    """The bracketed alias's text (rulebook §2.3): ``TYPE-{id}`` for the UUID domains, the verbatim id for ``feat``.

    The alias is unique per (type, id) key (collision-free by construction);
    edge operands carry it bracketed verbatim.
    """
    assert isinstance(type_, str), type(type_)
    assert isinstance(id_, str), type(id_)

    if type_ == _FEAT:
        result = id_
    else:
        result = f"{type_.upper()}-{id_}"
    return result


def _node_line(node: GraphNode, max_label: int) -> str:
    """One node's frozen ``component`` declaration line (rulebook §2.4/§2.6).

    A resolved node: its title, sanitised + truncated to ``max_label``, as
    the label, its ``<<TYPE>>`` stereotype. An unresolved node (``title``
    ``None``): the verbatim id as the label (never truncated, never
    sanitised), the ``<<UNRESOLVED>>`` stereotype. The label is always
    emitted in double quotes (added after sanitisation).
    """
    assert isinstance(node, GraphNode), type(node)

    alias = _alias(node.type, node.id)
    if node.title is None:
        label = node.id
        stereotype = _UNRESOLVED_STEREOTYPE
    else:
        label = _truncate(_single_line(node.title), max_label)
        stereotype = node.type.upper()
    result = f'component "{label}" as [{alias}] <<{stereotype}>>'
    return result


def _skinparam_block() -> str:
    """The frozen 14-entry skinparam colour block (rulebook §2.5) -- always emitted in full, in block order."""
    lines = ["skinparam component {"]
    lines.extend(f"  backgroundColor<<{stereotype}>> {colour}" for stereotype, colour in _PALETTE)
    lines.append("}")
    result = "\n".join(lines)
    return result


def _tarjan_scc_sizes(
    node_keys: list[tuple[str, str]], successors: dict[tuple[str, str], list[tuple[str, str]]]
) -> dict[tuple[str, str], tuple[int, int]]:
    """Iterative Tarjan strongly connected components over the graph's node keys (rulebook §4.2).

    Stdlib, recursion-free (deep registry graphs never hit Python's
    recursion limit), deterministic (nodes visited in the given ``node_keys``
    order, successors in their stored order). Returns ``key -> (scc index,
    scc size)`` -- the index is unique per component (in discovery order)
    and the size the component's member count; an isolated node is its own
    size-1 component.
    """
    assert isinstance(node_keys, list), type(node_keys)

    index: dict[tuple[str, str], int] = {}
    lowlink: dict[tuple[str, str], int] = {}
    on_stack: set[tuple[str, str]] = set()
    stack: list[tuple[str, str]] = []
    scc_of: dict[tuple[str, str], int] = {}
    counter = 0
    next_component = 0

    for root in node_keys:
        if root in index:
            continue
        counter += 1
        index[root] = counter
        lowlink[root] = counter
        stack.append(root)
        on_stack.add(root)
        # The explicit work stack: (node, its own successor iterator) -- the
        # iterator's state persists across descents, resuming exactly where
        # the recursive call would have returned.
        work: list[tuple[tuple[str, str], Iterator[tuple[str, str]]]] = [(root, iter(successors.get(root, ())))]
        while work:
            node, node_iter = work[-1]
            descended = False
            for successor in node_iter:
                if successor not in index:
                    counter += 1
                    index[successor] = counter
                    lowlink[successor] = counter
                    stack.append(successor)
                    on_stack.add(successor)
                    work.append((successor, iter(successors.get(successor, ()))))
                    descended = True
                    break
                if successor in on_stack:
                    lowlink[node] = min(lowlink[node], index[successor])
            if descended:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                lowlink[parent] = min(lowlink[parent], lowlink[node])
            if lowlink[node] == index[node]:
                component = next_component
                next_component += 1
                while True:
                    member = stack.pop()
                    on_stack.discard(member)
                    scc_of[member] = component
                    if member == node:
                        break

    sizes: dict[int, int] = {}
    for scc_id in scc_of.values():
        sizes[scc_id] = sizes.get(scc_id, 0) + 1
    result = {key: (scc_id, sizes[scc_id]) for key, scc_id in scc_of.items()}
    return result


def _on_cycle_edges(
    node_keys: list[tuple[str, str]], edges: set[tuple[str, str, str, str]]
) -> set[tuple[str, str, str, str]]:
    """The on-cycle subset of ``edges`` (rulebook §4.1's exact characterization).

    An edge lies on a cycle iff it is a self-loop (source == target) or both
    endpoints belong to the same strongly connected component of size ≥ 2 --
    within an SCC every pair of nodes is mutually reachable, so any internal
    edge (u→v) plus a v→…→u path forms a cycle containing it; conversely,
    every node on a cycle is mutually reachable with the rest of it, so a
    cycle's nodes form (a subset of) one SCC. Computed over the iterative
    Tarjan SCCs of :func:`_tarjan_scc_sizes` (deterministic node order).
    """
    assert isinstance(node_keys, list), type(node_keys)
    assert isinstance(edges, set), type(edges)

    successors: dict[tuple[str, str], list[tuple[str, str]]] = {key: [] for key in node_keys}
    for source_type, source_id, target_type, target_id in edges:
        source = (source_type, source_id)
        target = (target_type, target_id)
        if source == target:
            continue  # a self-loop forms no SCC membership question (on-cycle by definition)
        if source in successors and target in successors:
            successors[source].append(target)

    scc = _tarjan_scc_sizes(node_keys, successors)
    result: set[tuple[str, str, str, str]] = set()
    for edge in edges:
        source = (edge[0], edge[1])
        target = (edge[2], edge[3])
        if source == target:
            result.add(edge)
            continue
        source_scc, source_size = scc[source]
        if scc[target][0] == source_scc and source_size >= 2:
            result.add(edge)
    return result


def render_reference_graph(graph: ReferenceGraph, *, max_label: int = DEFAULT_MAX_LABEL) -> str:
    """Render ``graph`` to the frozen PlantUML component-diagram source (rulebook §2).

    The deterministic, byte-stable mapping the rulebook freezes: the
    ``@startuml {title}`` line (sanitised, never truncated), the full
    14-entry skinparam block, the ``left to right direction`` line, the
    top-level unresolved node lines (sorted by alias, before the first
    package), one ``package "TYPE"`` … ``end package`` per non-empty domain
    (in the 13-domain order, nodes sorted by id), and the deduped + sorted
    edge lines (uniform ``: refers to`` label; the red ``-[#red]->`` form
    exactly for the on-cycle edges of :func:`_on_cycle_edges`, plain
    ``-->`` otherwise). The content sections -- the ``@startuml`` line, the
    skinparam block, the direction line, the top-level unresolved node
    lines, each non-empty package, and the edge section -- are separated by
    exactly one blank line; an empty section is omitted entirely (no
    residual blank line); ``@enduml`` follows the last non-empty section
    directly; the source ends with exactly one trailing newline (rulebook
    §2.1, corrected 2026-10-11).

    The input is treated as pure facts: duplicate (type, id) nodes dedupe
    (first occurrence's title wins), edges dedupe, and an edge endpoint
    missing from the node collection auto-adds a ``title=None`` (unresolved)
    node -- the emitted source is checker-clean for any input, never raising
    for content (the renderer is pure).

    Parameters
    ----------
    graph:
        The reference graph to render (the builders' output or a hand-built
        fact collection).
    max_label:
        The resolved-node label limit (rulebook §5.2, default 40 -- the
        env var's own default; this module never reads the env var itself,
        keeping it pure). The diagram title and unresolved ids are never
        truncated by it.

    Returns
    -------
    str
        The PlantUML source (``@startuml …`` through ``@enduml``, one
        trailing newline).

    Raises
    ------
    AssertionError
        ``graph`` is not a :class:`ReferenceGraph`, or ``max_label`` is not
        an int ≥ 1 -- program-invariant failures only, never content-driven
        (the renderer never fails for graph content).
    """
    assert isinstance(graph, ReferenceGraph), type(graph)
    assert isinstance(max_label, int), type(max_label)
    assert max_label >= 1, max_label

    # The node facts, keyed by (type, id): duplicates dedupe (first
    # occurrence wins), and every edge endpoint gets a node -- a missing
    # one auto-adds as unresolved (title None), so the emission is total.
    nodes: dict[tuple[str, str], GraphNode] = {}
    for node in graph.nodes:
        key = (node.type, node.id)
        if key not in nodes:
            nodes[key] = node
    for edge in graph.edges:
        for key in ((edge.source_type, edge.source_id), (edge.target_type, edge.target_id)):
            if key not in nodes:
                nodes[key] = GraphNode(type=key[0], id=key[1], title=None)

    # The edge facts, deduped (one edge per (source, target) pair).
    edges = {(edge.source_type, edge.source_id, edge.target_type, edge.target_id) for edge in graph.edges}

    # The on-cycle subset (iterative Tarjan, deterministic node order).
    on_cycle = _on_cycle_edges(sorted(nodes), edges)

    sections: list[str] = [f"@startuml {_single_line(graph.title)}", _skinparam_block(), _DIRECTION]

    # The top-level section: unresolved nodes (sorted by alias) plus any
    # resolved node whose type sits outside the 13-domain order (the
    # builder never produces one -- its reference vocabulary is a subset of
    # the 13 domains -- so this placement is a hand-built-input totality
    # rule, not a frozen layout case).
    top_level = [node for node in nodes.values() if node.title is None or node.type not in _DOMAIN_ORDER]
    if top_level:
        top_level.sort(key=lambda node: _alias(node.type, node.id))
        sections.append("\n".join(_node_line(node, max_label) for node in top_level))

    # One package per non-empty domain, in the frozen 13-domain order
    # (nodes sorted by id inside); the close is the NAMED ``end package``
    # form (a bare ``end`` on a package fragment is a hard checker error in
    # both modes -- rulebook §2.7/§7.1).
    for domain in _DOMAIN_ORDER:
        domain_nodes = sorted(
            (node for node in nodes.values() if node.type == domain and node.title is not None),
            key=lambda node: node.id,
        )
        if not domain_nodes:
            continue
        package_lines = [f'package "{domain.upper()}"']
        package_lines.extend(_node_line(node, max_label) for node in domain_nodes)
        package_lines.append("end package")
        sections.append("\n".join(package_lines))

    # The edge section: deduped + sorted by
    # (source_type, source_id, target_type, target_id); the red form
    # exactly for the on-cycle edges.
    if edges:
        edge_lines: list[str] = []
        for source_type, source_id, target_type, target_id in sorted(edges):
            arrow = _RED_ARROW if (source_type, source_id, target_type, target_id) in on_cycle else _PLAIN_ARROW
            edge_lines.append(
                f"[{_alias(source_type, source_id)}] {arrow} [{_alias(target_type, target_id)}] {_EDGE_LABEL}"
            )
        sections.append("\n".join(edge_lines))

    # The content sections, separated by exactly one blank line; the
    # skinparam block and the direction line are never empty, so the body
    # is never empty; @enduml follows the last section directly.
    result = "\n\n".join(sections) + "\n@enduml\n"
    return result
