# `biz.dfch.specmgr.general.models.reference_graph`

The frozen reference-graph model + the deterministic PlantUML renderer (feat-207-reference-graph,
Phase 110, REQ-001/REQ-003).

Pure and **stdlib-only** (the import-free bar of the ``plantuml/`` package, ADR
7a626b12): no ``mcp``, no ``general.tools`` imports, no third-party dependency.
It holds the three frozen fact dataclasses the graph builders
(``general.tools._reference_graph``) and the hand-built test graphs share,
plus the one pure function that turns a :class:`ReferenceGraph` into the
frozen PlantUML component-diagram source of the reference-graph rulebook
(``specmgr://reference_graph`` / ``general/data/general_reference_graph.md`` §2):

- :class:`GraphNode` -- one artifact: its lowercase domain ``type``, its
  verbatim ``id`` (canonical lowercase-hex uuid for the 13 UUID domains, the
  full ``feat-NNN-slug`` or the bare ``feat-NNN`` for ``feat``), and its
  resolved title (the document's H1 as the builders derive it) or ``None``
  for a reference that could not be resolved on disk (the unresolved node
  of rulebook §2.6).
- :class:`GraphEdge` -- one unique reference: the (source, target) pair of
  ``(type, id)`` keys (the referenced item carries the incoming arrow).
- :class:`ReferenceGraph` -- the diagram's title (the scoped source's H1 or
  the registry-wide ``Reference Graph`` default, or a caller override) plus
  the node and edge collections.
- :func:`render_reference_graph` -- the frozen layout (rulebook §2.1–§2.8,
  corrected 2026-10-15): the ``@startuml {title}`` line (sanitised, **never
  truncated**, §2.2/§5), the full 15-entry skinparam colour block (always,
  in block order, §2.5), the ``left to right direction`` line, the
  top-level unresolved node lines (sorted by alias, §2.6), one curly
  domain group ``component "TYPE" { … }`` per non-empty domain (in the
  14-domain order, nodes sorted by id, §2.7), and the deduped + sorted
  label-free edge lines (the red ``-[#red]->`` form on cycle edges only,
  §2.8/§4). The content sections (the ``@startuml`` line, the skinparam
  block, the direction line, the top-level unresolved node lines, each
  non-empty domain group, and the edge section) are separated by exactly
  one blank line, an empty section is omitted entirely, ``@enduml`` follows
  the last non-empty section directly, and the source ends with exactly one
  trailing newline (§2.1, corrected 2026-10-11 and 2026-10-15).

Cycle detection (REQ-003, rulebook §4): an edge lies on a cycle iff it is a
self-loop or both endpoints belong to the same strongly connected component
of size ≥ 2. Computed here by an **iterative** Tarjan (stdlib, deterministic
node order) -- the model stays pure facts, and the recursion-free walk keeps
large registry graphs off Python's recursion limit.

Label rules (rulebook §2.4/§5): a resolved node's label is its title,
sanitised (embedded ``"`` → ``#quot;``, a literal newline → the two-character
sequence ``\n`` — the UC rulebook §2.4 conventions, reused as-is) and
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

## Classes

### `GraphEdge`

One unique reference of the reference graph (a pure fact, rulebook §2.8).

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


### `GraphNode`

One artifact of the reference graph (a pure fact, rulebook §1).

Parameters
----------
type:
    The artifact's lowercase domain name (one of the 14
    ``general.tools._domains.ALL_DOMAINS`` names for builder-produced
    graphs; the renderer accepts any string, placing a node whose type
    is outside the 14-domain order top-level, like unresolved nodes).
id:
    The artifact's verbatim id: the canonical lowercase-hex uuid for the
    13 UUID domains, the full ``feat-NNN-slug`` id or the bare
    ``feat-NNN`` number for ``feat`` (the two spellings of one feature
    are two distinct nodes -- rulebook §3.7's inherited caveat).
title:
    The artifact's resolved title (its H1, as the builders derive it --
    the feature's H1 with the ``Feature: `` prefix stripped for
    ``feat``), or ``None`` for a reference that could not be resolved on
    disk (the unresolved node of rulebook §2.6: top-level, verbatim-id
    label, ``<<UNRESOLVED>>`` stereotype).


### `ReferenceGraph`

The full reference graph a renderer call emits (rulebook §1).

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


## Functions

### `_alias(type_: 'str', id_: 'str') -> 'str'`

The bracketed alias's text (rulebook §2.3): ``TYPE-{id}`` for the UUID domains, the verbatim id for ``feat``.

The alias is unique per (type, id) key (collision-free by construction);
edge operands carry it bracketed verbatim.


### `_node_line(node: 'GraphNode', max_label: 'int') -> 'str'`

One node's frozen ``component`` declaration line (rulebook §2.4/§2.6).

A resolved node: its title, sanitised + truncated to ``max_label``, as
the label, its ``<<TYPE>>`` stereotype. An unresolved node (``title``
``None``): the verbatim id as the label (never truncated, never
sanitised), the ``<<UNRESOLVED>>`` stereotype. The label is always
emitted in double quotes (added after sanitisation).


### `_on_cycle_edges(node_keys: 'list[tuple[str, str]]', edges: 'set[tuple[str, str, str, str]]') -> 'set[tuple[str, str, str, str]]'`

The on-cycle subset of ``edges`` (rulebook §4.1's exact characterization).

An edge lies on a cycle iff it is a self-loop (source == target) or both
endpoints belong to the same strongly connected component of size ≥ 2 --
within an SCC every pair of nodes is mutually reachable, so any internal
edge (u→v) plus a v→…→u path forms a cycle containing it; conversely,
every node on a cycle is mutually reachable with the rest of it, so a
cycle's nodes form (a subset of) one SCC. Computed over the iterative
Tarjan SCCs of :func:`_tarjan_scc_sizes` (deterministic node order).


### `_sanitize(text: 'str') -> 'str'`

Quote sanitisation (rulebook §5.1, the UC rulebook §2.4 convention): an embedded ``"`` becomes ``#quot;``.

The structural double quotes PlantUML requires around a label are added
*after* sanitisation and remain real ``"``.


### `_single_line(text: 'str') -> 'str'`

Quote sanitisation + single-line escaping (rulebook §5.1, the UC rulebook §2.4 conventions).

An embedded ``"`` becomes ``#quot;`` and a literal newline becomes the
two-character sequence ``\n`` (PlantUML's in-message line break), so
the text emits on exactly one line (the ``@startuml`` title line and
every component label).


### `_skinparam_block() -> 'str'`

The frozen 15-entry skinparam colour block (rulebook §2.5) -- always emitted in full, in block order.


### `_tarjan_scc_sizes(node_keys: 'list[tuple[str, str]]', successors: 'dict[tuple[str, str], list[tuple[str, str]]]') -> 'dict[tuple[str, str], tuple[int, int]]'`

Iterative Tarjan strongly connected components over the graph's node keys (rulebook §4.2).

Stdlib, recursion-free (deep registry graphs never hit Python's
recursion limit), deterministic (nodes visited in the given ``node_keys``
order, successors in their stored order). Returns ``key -> (scc index,
scc size)`` -- the index is unique per component (in discovery order)
and the size the component's member count; an isolated node is its own
size-1 component.


### `_truncate(label: 'str', max_label: 'int') -> 'str'`

Label truncation (rulebook §5.2, N = ``max_label``, label already sanitised).

If ``len(label) > N``: ``candidate = label[:N-1]``; if ``candidate``
contains a space, cut at its LAST space (dropping from that space on);
else hard cut at ``candidate``; append ``…``. The result is ≤ N
characters. Labels of exactly N characters (and shorter ones) are
returned untouched.


### `render_reference_graph(graph: 'ReferenceGraph', *, max_label: 'int' = 40) -> 'str'`

Render ``graph`` to the frozen PlantUML component-diagram source (rulebook §2).

The deterministic, byte-stable mapping the rulebook freezes (corrected
2026-10-15): the ``@startuml {title}`` line (sanitised, never
truncated), the full 15-entry skinparam block, the ``left to right
direction`` line, the top-level unresolved node lines (sorted by alias,
before the first domain group), one curly domain group ``component
"TYPE" { … }`` per non-empty domain (in the 14-domain order, nodes
sorted by id), and the deduped + sorted label-free edge lines (the red
``-[#red]->`` form exactly for the on-cycle edges of
:func:`_on_cycle_edges`, plain ``-->`` otherwise). The content sections
-- the ``@startuml`` line, the skinparam block, the direction line, the
top-level unresolved node lines, each non-empty domain group, and the
edge section -- are separated by exactly one blank line; an empty
section is omitted entirely (no residual blank line); ``@enduml``
follows the last non-empty section directly; the source ends with
exactly one trailing newline (rulebook §2.1, corrected 2026-10-11 and
2026-10-15).

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

